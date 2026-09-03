Arquitectura de un Middleware de Reconciliación de Estados para Trading Algorítmico

La automatización de estrategias cuantitativas mediante el envío de alertas webhooks desde plataformas de análisis gráfico como TradingView hacia interfaces de programación de aplicaciones (APIs) de brókers institucionales presenta desafíos operacionales complejos^1^. Mientras que el entorno de simulación virtual de TradingView (su *Strategy Tester* y el motor de ejecución Pine Script) opera bajo supuestos ideales de liquidez infinita, ejecución inmediata sin latencia y llenados perfectos a precios de cierre, las cuentas reales en brókers institucionales se enfrentan a la microestructura del mercado^1^. En la negociación real, factores como el deslizamiento de precios (*slippage*), las limitaciones de tamaño de lote basadas en los tamaños mínimos de tics lógicos de los activos, los rechazos de órdenes por parte del servidor y la ejecución asíncrona de órdenes de protección internas desalinean de forma constante el estado real de la cuenta respecto al teórico^3^.

El diseño de un middleware de reconciliación basado en una máquina de estados finita (FSM) implementada en Python permite subsanar esta divergencia, actuando como un supervisor determinista de la ejecución^2^. Este documento detalla la arquitectura de software requerida para consolidar el estado virtual y el estado físico de una cuenta institucional de negociación algorítmica^2^.

El Problema de las Posiciones Fantasma (Ghost Positions)

El fenómeno de las "posiciones fantasma" es una de las fallas más críticas en los sistemas de trading algorítmico que dependen de webhooks de dirección única^5^. Ocurre cuando el estado simulado en TradingView diverge de la realidad operativa del bróker, lo que lleva a un ciclo de retroalimentación erróneo que amplifica las pérdidas y genera operaciones involuntarias en el mercado de manera descontrolada^10^.

Dinámica del Escenario de Desincronización

La raíz del problema radica en la naturaleza asíncrona de TradingView, que no mantiene una comunicación bidireccional en tiempo real con el bróker a nivel de protocolo de red nativo^2^. TradingView simplemente emite un evento de alerta HTTP POST en un sentido^2^. El flujo temporal de la falla estructural se desarrolla a través de las siguientes fases consecutivas:

- **Apertura de la Posición ():** La estrategia en Pine Script genera una señal de compra. TradingView registra internamente una posición larga virtual (LONG) y emite un webhook de apertura^2^. El middleware procesa la alerta y envía una orden de compra de mercado al bróker institucional, la cual se ejecuta con éxito^9^. En este instante, tanto el estado virtual como la posición física en el bróker se encuentran alineados en un volumen idéntico de contratos^2^.
- **Ejecución del Stop Loss Local ():** El precio del activo experimenta una caída abrupta y volátil en el mercado real^2^. Debido a la velocidad del movimiento, el bróker ejecuta la orden de parada de pérdidas (*Stop Loss*) configurada de forma local en sus propios servidores de ejecución para proteger la integridad del capital del cliente^2^. El bróker pasa inmediatamente a un estado plano o sin posición (FLAT)^5^. Sin embargo, la estrategia de TradingView aún no ha cerrado la barra actual en su gráfico histórico o su alimentación de datos en la nube experimenta una latencia de varios cientos de milisegundos, por lo que su Stop Loss virtual no se ha activado aún^3^.
- **Emisión del Webhook de Cierre de Posición ():** TradingView finalmente procesa la caída del precio en su siguiente ciclo de cálculo y determina que su Stop Loss virtual ha sido alcanzado^5^. Al asumir que todavía mantiene una posición abierta (LONG), la plataforma emite un comando de cierre de posición (Close Position) mediante el envío de un nuevo webhook que contiene una orden de venta de mercado para liquidar el lote original^10^.
- **Apertura Involuntaria de Posición Inversa ():** El middleware recibe la orden de venta y la reenvía al bróker institucional sin realizar verificaciones previas de estado^9^. Debido a que el bróker ya se encontraba en un estado plano (FLAT) desde el momento , la recepción de una nueva orden de venta de mercado no actúa como un cierre de posición, sino como la apertura de una nueva posición de sentido inverso^10^. El sistema ha entrado de manera accidental en una posición corta (SHORT) no planificada ni controlada por el algoritmo original de TradingView, exponiéndose a pérdidas sustanciales en un mercado altamente volátil^10^.

El siguiente cuadro detalla el comportamiento del sistema bajo el flujo convencional frente al flujo anómalo que da origen a la desincronización destructiva:

| **Atributo Temporal** | **Estado Virtual (TradingView)** | **Estado Real (Bróker)** | **Acción Lógica / Ejecución Física** | **Impacto en Cuenta** |
| --- | --- | --- | --- | --- |
| **Alineación Inicial ()** | LONG (10 Contratos) | LONG (10 Contratos) | Entrada síncrona aprobada por middleware^2^. | Consistencia operativa del 100%^2^. |
| **Evento de Parada ()** | LONG (10 Contratos) | FLAT (0 Contratos) | Bróker ejecuta Stop Loss local de forma autónoma^2^. | Desincronización silenciosa activa^5^. |
| **Acción Tardía ()** | FLAT (0 Contratos) | FLAT (0 Contratos) | TradingView alcanza nivel de salida y emite webhook SELL^10^. | Transmisión de señal redundante por red^5^. |
| **Falla de Reconciliación ()** | FLAT (0 Contratos) | SHORT (-10 Contratos) | Bróker procesa orden SELL entrante como nueva apertura^10^. | Creación de la **Posición Fantasma**^10^. |

Diseño de la Máquina de Estados Finita (FSM)

Para neutralizar de forma determinista el desalineamiento entre el entorno simulado y el entorno real, el middleware debe estructurarse en torno a una Máquina de Estados Finita (FSM) que actúe como un validador estricto de transiciones de estado de ejecución^2^. El objetivo fundamental de esta máquina es aislar el procesamiento de señales lógicas de la infraestructura de mensajería del bróker, garantizando que ninguna orden se enrute al mercado real si viola las reglas de transición del sistema financiero^18^.

Especificación de los Estados Propuestos

La arquitectura de la FSM se compone de cinco estados bien definidos y mutuamente excluyentes, que encapsulan el ciclo de vida de la ejecución y la reconciliación en tiempo real^7^:

- **TV_WAITING**: Es el estado de reposo operativo estándar^2^. Representa una situación de perfecta sincronía donde no existen ejecuciones en curso ni discrepancias pendientes^2^. El sistema está listo para recibir y validar una nueva señal de inicio de operación proveniente de TradingView^2^.
- **BROKER_EXECUTING**: Este estado se activa inmediatamente después de recibir un webhook válido de apertura o cierre desde TradingView^9^. Durante esta fase, el middleware bloquea temporalmente la aceptación de cualquier webhook entrante adicional para el mismo símbolo y cuenta con el propósito de prevenir colisiones por ejecución concurrente o ráfagas de señales duplicadas debido a ruidos temporales en la red^21^. El sistema permanece en este estado transitorio hasta recibir una respuesta de confirmación definitiva (lleno total, rechazo o cancelación) de la API institucional del bróker^4^.
- **PARTIAL_FILL**: Se alcanza este estado cuando el bróker confirma que una orden ha sido ejecutada parcialmente pero no se ha completado en su totalidad debido a restricciones de liquidez del mercado^4^. En esta condición, el sistema evalúa de forma dinámica si es viable cancelar el remanente o si se debe esperar un tiempo de corte estricto (*timeout*) para forzar la compleción a mercado abierto, manteniendo la máquina en una fase segura y evitando que se asuma un estado plano o completamente lleno de forma errónea^11^.
- **SL_HIT_LOCAL**: Este estado se activa de forma asíncrona cuando el middleware detecta, mediante el bucle de retroalimentación inverso, que la posición física en el bróker ha vuelto a cero debido a la activación de un Stop Loss o Take Profit local sin intervención de una señal de TradingView^2^. Al entrar en esta fase de contingencia, el middleware inhabilita el flujo normal de operaciones y marca la estrategia como "desalineada", preparándose para mitigar las señales obsoletas que TradingView emitirá posteriormente^5^.
- **ORPHAN_SIGNAL**: Estado de excepción de seguridad absoluta^20^. Se activa cuando llega una alerta de salida o de reducción de posición desde TradingView, pero las consultas en tiempo real indican que no existe una posición abierta coincidente en los servidores del bróker, o que la dirección de la señal contradice la posición física actual^11^. El middleware retiene la orden, rechaza su ejecución en el mercado real y genera un evento de alerta crítica para la intervención manual o la auto-reconciliación destructiva de la cuenta^10^.

El comportamiento de la máquina de estados frente a cada evento e instrucción se formaliza en la siguiente matriz de transiciones lógicas:

| **Estado Origen** | **Evento de Entrada / Condición lógica** | **Acción de Reconciliación Asociada** | **Estado Destino** |
| --- | --- | --- | --- |
| **TV_WAITING** | TV_WEBHOOK_RECEIVED (Señal de entrada válida) | Enrutamiento de orden a mercado e inicio de temporizador^9^. | **BROKER_EXECUTING** |
| **BROKER_EXECUTING** | BROKER_FILL_CONFIRMED (Llenado completo de orden) | Confirmación de alineación de inventario con TradingView^2^. | **TV_WAITING** |
| **BROKER_EXECUTING** | BROKER_PARTIAL_FILL_RECEIVED (Ejecución incompleta) | Registro de lote ejecutado y ajuste de orden remanente^4^. | **PARTIAL_FILL** |
| **PARTIAL_FILL** | REMANENTE_RESOLVED (Cancelación o compleción) | Limpieza de órdenes pendientes en el libro del bróker^10^. | **TV_WAITING** |
| **TV_WAITING** | BROKER_LOCAL_EXIT (Ejecución de Stop Loss del bróker) | Activación de bandera de desalineación en caché Redis^2^. | **SL_HIT_LOCAL** |
| **SL_HIT_LOCAL** | TV_DELAYED_WEBHOOK (Señal de salida tardía recibida) | Descarte inmediato de la señal para evitar posición inversa^5^. | **SL_HIT_LOCAL** |
| **SL_HIT_LOCAL** | SYNC_FORCE_FLATTEN (Comando manual o auto-reconciliación) | Actualización del estado lógico interno de TradingView a plano^10^. | **TV_WAITING** |
| **TV_WAITING** | TV_INCONGRUENT_SIGNAL (Orden de cierre sin posición real) | Bloqueo físico de la orden y registro en auditoría^11^. | **ORPHAN_SIGNAL** |
| **ORPHAN_SIGNAL** | MANUAL_OVERRIDE / AUTO_ALIGN_FLAT | Sincronización forzada de ambos entornos a cero absoluto^5^. | **TV_WAITING** |

Feedback Loop Inverso (Bucle de Retroalimentación Inverso)

Para impedir que las discrepancias descritas en la máquina de estados se traduzcan en operaciones reales erróneas, es imperativo establecer un bucle de retroalimentación inverso y robusto de baja latencia entre el Gateway basado en FastAPI y la API del bróker institucional^2^. El Gateway no puede actuar como un simple enrutador ciego; debe validar activamente el estado físico de la cuenta antes de otorgar viabilidad a cualquier webhook entrante^9^.

┌────────────────────────────────────────────────────────┐

│                   Gateway FastAPI                      │

│                                                        │

│  1. Recepción Webhook (Symbol, Target Qty)  │

│  2. Consulta ultra-rápida a Redis Cache [cite: 22, 24] │

└──────────────────────────┬─────────────────────────────┘

                           │

             ¿Existe discrepancia de estado?

             (Q_actual != Q_esperada_TV)

                           │

             ┌─────────────┴─────────────┐

             SÍ                          NO

             │                           │

  Aplicar Política out_of_sync     Permitir Orden

  (wait / flatten / resync)              │

                      ▼

                           Enviar a Execution Queue

                           (Asynchronous Worker)

Mecanismo de Monitoreo de Baja Latencia y Recuperación de Estado

El Gateway FastAPI implementa un patrón híbrido de monitoreo en tiempo real basado en dos canales de comunicación concurrentes con la infraestructura del bróker^24^:

- **Canal Principal de Transmisión de Eventos (WebSockets / FIX Drop Copy):** El middleware mantiene un canal de suscripción persistente bidireccional que escucha los eventos del sistema de gestión de órdenes (OMS) del bróker^24^. Cada evento de ejecución de Stop Loss, Take Profit, cancelación manual o llenado parcial se transmite de manera instantánea al middleware, el cual actualiza inmediatamente la posición de inventario real en una base de datos en caché de estructura clave-valor (Redis) en un plazo inferior a diez milisegundos^8^.
- **Canal Secundario de Respaldo (REST Polling Activo):** En mercados volátiles, las conexiones de transmisión de datos basadas en hilos lógicos pueden sufrir micro-cortes de red o saturación^24^. Para resolver esto, el middleware ejecuta un proceso secundario persistente asíncronizado mediante asyncio que realiza consultas rápidas y parametrizadas al puerto REST de posiciones reales del bróker bajo las siguientes condiciones^18^:

- Inmediatamente después de detectar una reconexión exitosa en el socket^24^.
- Al expirar un temporizador de seguridad periódico de treinta segundos (latido de estado)^21^.
- Inmediatamente al recibir un webhook de TradingView, antes de calcular la lógica de la máquina de estados, para validar que la memoria caché local está perfectamente sincronizada con el estado real del bróker^5^.

Control Inteligente de Alineación y Políticas de Desincronización

Cuando un webhook de TradingView llega al Gateway, este extrae el tamaño de la posición esperado tras la ejecución de la señal, denominado cantidad objetivo () y proporcionado de forma dinámica por las variables de estado de TradingView^11^:

En paralelo, el Gateway recupera de Redis la cantidad neta real de contratos que mantiene abiertos en el bróker ()^11^. El middleware evalúa la discrepancia física calculando el delta operativo^11^:

Si el resultado del delta operativo arroja un valor nulo (), el webhook se reconoce como redundante u obsoleto, procediendo a su rechazo seguro^5^. Si se detecta un desalineamiento (), el middleware aplica una de las siguientes tres políticas de seguridad configurables para contener el riesgo en la cuenta^10^:

- **wait (Espera y Bloqueo Seguro):** Se rechaza la ejecución de la orden asociada al webhook^10^. El middleware congela temporalmente la recepción de operaciones para el activo en conflicto y genera un reporte de excepción inmediato en el panel de control del operador algorítmico^10^. No se realizan cambios en la cartera del bróker hasta que exista una intervención humana que resuelva manualmente la desincronización^10^.
- **flatten (Liquidación Autocurativa):** El middleware descarta de inmediato el webhook de TradingView^10^. En paralelo, emite de forma automática órdenes de cancelación para cualquier instrucción pendiente y una orden de mercado para cerrar y liquidar cualquier posición residual abierta en el bróker, llevando el inventario real a cero absoluto (FLAT)^10^. Esta acción de restauración garantiza que la estrategia pueda reanudar sus operaciones limpiamente en la siguiente señal de entrada generada desde un estado de reposo absoluto^10^.
- **resync (Ajuste Quirúrgico de Delta):** El middleware no bloquea ni descarta la operación de forma destructiva^11^. En su lugar, el Gateway de FastAPI intercepta la orden de mercado original enviada por TradingView y calcula dinámicamente una orden correctora de mercado equivalente a ^11^. Esta orden es enrutada de inmediato al bróker para alinear de forma quirúrgica la posición real con la cantidad esperada por la estrategia simulada, subsanando de forma automática problemas de llenados parciales previos u operaciones no sincronizadas sin interrumpir la continuidad del algoritmo^11^.

Desacoplamiento Asíncrono de Procesamiento

Para garantizar una operación segura y estable, la arquitectura del middleware exige desacoplar el ciclo de recepción del webhook de la ejecución real de las órdenes en el bróker^22^. TradingView requiere que el servidor que recibe el webhook retorne una respuesta HTTP exitosa (código de estado 200 OK) en un plazo de tiempo extremadamente estricto, típicamente inferior a tres segundos; de lo contrario, asume una falla de red e inicia reintentos automáticos que pueden duplicar las operaciones en el mercado real^13^.

El Gateway FastAPI satisface este límite crítico ejecutando un procesamiento asíncrono en segundo plano^22^:

- El Gateway recibe el webhook de TradingView, extrae los parámetros esenciales, realiza las comprobaciones iniciales de idempotencia y confirma la autenticidad de la firma^9^.
- Inmediatamente, escribe el mensaje en una cola de mensajería asíncrona de alto rendimiento, como Redis Streams o una cola de Celery^22^.
- El Gateway retorna de forma inmediata la respuesta HTTP 200 OK a TradingView, completando la solicitud en pocos milisegundos y evitando que la plataforma de análisis asuma un fallo o inicie reintentos duplicados^13^.
- Un grupo de procesos de ejecución (*workers*) independientes en segundo plano consume los mensajes de la cola asíncrona, procesa la lógica de la máquina de estados, realiza la consulta de posición en tiempo real al bróker, decide sobre la viabilidad del delta de reconciliación y ejecuta las órdenes físicas correspondientes en el mercado real de forma secuencial y controlada^22^.

Idempotencia y Secuenciadores

El middleware institucional debe implementar mecanismos avanzados de control de mensajes para proteger el sistema contra la recepción de webhooks duplicados resultantes de reintentos de red y evitar la alteración cronológica en la llegada de las órdenes debido al enrutamiento asíncrono de paquetes a través de Internet^5^.

Mecanismo de Idempotencia Atómica con Redis

Para asegurar el procesamiento de "exactamente una vez" de cada señal generada por TradingView, el middleware requiere el uso de claves de idempotencia persistentes y de validación obligatoria en cada solicitud HTTP POST^34^. TradingView debe configurarse para generar e incluir un identificador único en formato UUID v7 dentro de las cabeceras HTTP (Idempotency-Key) o directamente en el cuerpo del mensaje JSON de alerta^21^. La elección de UUID v7 es óptima debido a que su estructura está ordenada cronológicamente por diseño, incorporando una marca de tiempo en sus primeros 48 bits, lo cual mejora significativamente la eficiencia de la indexación en las bases de datos de reconciliación frente a los UUID v4 tradicionales basados puramente en aleatoriedad^21^.

Al recibir una petición, el Gateway de FastAPI extrae este UUID v7 y ejecuta un comando de escritura atómico no bloqueante en Redis^22^:

Fragmento de código

SET idempotency:request_uuid "PROCESSING" NX EX 86400

El parámetro NX asegura que la clave se escriba únicamente si no existe previamente en la base de datos de Redis^22^. El parámetro EX 86400 establece un tiempo de vida (TTL) automático de 24 horas para evitar la acumulación infinita de datos en memoria, lo cual cubre ampliamente cualquier ventana razonable de reintentos de red de TradingView^22^.

La ejecución de este comando atómico retorna dos posibles resultados de flujo lógico^21^:

- **Éxito (OK):** La clave no existía. El middleware reconoce la transacción como un evento de ejecución nuevo, cambia el estado a BROKER_EXECUTING y permite que el sistema continúe con la validación de la lógica financiera y el enrutamiento de la orden al mercado institucional^21^. Una vez que el bróker confirma la orden y se completa el flujo de ejecución, el middleware actualiza atómicamente el valor de la clave en Redis a COMPLETED y almacena de forma estructurada la respuesta de éxito generada por el bróker junto con su código de transacción^35^.
- **Fallo (Retorno Nil):** La clave ya existe en Redis^34^. El middleware detiene inmediatamente el procesamiento y evalúa el valor actual asociado a la clave^21^. Si el estado es PROCESSING, significa que una ejecución idéntica está siendo procesada de forma concurrente, por lo que retorna una respuesta HTTP 409 Conflict indicando que la solicitud está en curso^21^. Si el estado es COMPLETED, el middleware extrae de inmediato el resultado histórico almacenado en caché y lo devuelve al emisor, evitando duplicar operaciones en el mercado institucional y asegurando que las retransmisiones fallidas no impacten la cartera física del cliente^33^.

Para blindar el sistema contra manipulaciones de carga útil maliciosas o errores de software donde un mismo ID se asocie de forma errónea a una orden distinta, el middleware implementa una validación complementaria basada en firmas digitales de contenido^32^. El sistema genera un hash criptográfico SHA-256 utilizando una combinación normalizada y ordenada de los campos más sensibles del cuerpo del mensaje (como el activo, la dirección, la cantidad esperada y el timestamp)^21^. Este hash de validación se almacena en el mismo registro de Redis junto con el identificador único^35^. Si llega una solicitud de reintento que coincide con un ID existente pero presenta diferencias en la estructura del hash generado de su carga útil, el middleware la detecta como una violación de contrato y responde con un código de error HTTP 422 Unprocessable Entity, bloqueando de forma absoluta cualquier ejecución errónea^21^.

Secuenciación Temporal y Validación Cronológica

Debido al enrutamiento dinámico de los paquetes de red sobre la arquitectura TCP/IP estándar de Internet, no se puede garantizar que el orden físico de llegada de las solicitudes HTTP al servidor del middleware coincida exactamente con el orden cronológico en el que TradingView generó las señales en su plataforma de gráficos^5^. Para evitar el escenario catastrófico donde un webhook de cierre de posición retrasado llegue después de una nueva señal de reapertura, alterando el sentido real de la estrategia, se requiere el uso de marcas de tiempo de alta precisión y validaciones lógicas secuenciales en el middleware^5^.

Cada payload de webhook generado por TradingView debe incluir de forma obligatoria el marcador de posición dinámico correspondiente a la marca de tiempo exacta de la vela que originó el disparo de la alerta^1^:

JSON

{

  *"timestamp_origen"*: *"{{time}}"*

}

Este marcador es inyectado por TradingView en el instante preciso de la generación del evento en sus servidores de gráficos, ofreciendo una marca de tiempo en milisegundos UTC que es inmune a las variaciones de latencia de transporte por la red^1^.

El middleware mantiene un registro persistente en la memoria de alta velocidad de Redis que actúa como un control de secuencia lógico para cada cuenta y activo financiero bajo la estructura de clave last_timestamp:<symbol>:<account_id>^22^. El Gateway de FastAPI realiza la siguiente validación matemática estricta antes de procesar el webhook entrante en el motor de la máquina de estados:

- Extrae el valor del parámetro timestamp_origen del cuerpo JSON del mensaje entrante ().
- Obtiene de Redis el último timestamp que fue procesado exitosamente para ese activo y cuenta específicos ().
- Aplica el criterio de descarte cronológico:

Si la marca de tiempo de la solicitud entrante es menor o igual al último registro almacenado en caché, el middleware detecta de inmediato que el paquete de datos corresponde a una transmisión desordenada o tardía que ha quedado obsoleta frente al estado actual de la cuenta^5^. El middleware interrumpe el procesamiento del webhook, retorna una respuesta HTTP 200 OK (para satisfacer el protocolo de TradingView de forma pacífica) pero bloquea el envío de cualquier orden al mercado real, resguardando la cuenta contra cambios de estado anacrónicos y manteniendo la integridad del inventario de trading^5^.

Esquema de Base de Datos para Reconciliación

Para cumplir con los estándares normativos de auditoría institucional, facilitar análisis posteriores del deslizamiento de precios (*slippage*) y permitir la resincronización automatizada de posiciones caídas ante reinicios críticos del sistema, el middleware requiere una base de datos relacional robusta^29^. PostgreSQL se postula como la opción óptima para este propósito debido a su excelente soporte para transacciones ACID, su potente motor de consultas con restricciones de integridad referencial y su capacidad nativa para indexar datos estructurados complejos a través de tipos de datos JSONB^23^.

La base de datos se estructura bajo el principio de reconciliación transaccional de doble entrada^29^. El objetivo principal es forzar y documentar una relación determinista de uno a uno entre el identificador lógico de la orden simulada en TradingView (el identificador virtual del sistema de pruebas) y el número de confirmación físico devuelto por la API del bróker (el número de ticket de ejecución real)^29^.

El siguiente diagrama lógico detalla las entidades de base de datos diseñadas y sus relaciones lógicas:

┌──────────────────────────────┐          ┌──────────────────────────────┐

│     tradingview_signals      │          │        broker_orders         │

├──────────────────────────────┤          ├──────────────────────────────┤

│ PK  signal_id                │          │ PK  order_id                 │

│ UK  idempotency_key          │          │ UK  broker_ticket_number     │

│     virtual_trade_id         │          │     symbol                     │

│     symbol                   │          │     direction                │

│     action                   │          │     executed_qty             │

│     target_quantity          │          │     executed_price           │

│     pine_timestamp           │          │     executed_at              │

└──────────────┬───────────────┘          └──────────────┬───────────────┘

               │                                         │

               │ 1                                       │ 1

               │                                         │

               │   ┌──────────────────────────────┐      │

               └──>│     reconciliation_ledger    │<─────┘

                   ├──────────────────────────────┤

                   │ PK  reconciliation_id        │

                   │ FK  signal_id (Unique)       │

                   │ FK  broker_order_id (Unique) │

                   │     virtual_trade_id         │

                   │     reconciliation_status    │

                   │     discrepancy_qty          │

                   │     discrepancy_price        │

                   └──────────────────────────────┘

El siguiente script en SQL de estándar de producción define las tablas, restricciones de clave foránea e índices de optimización para búsquedas concurrentes en alta velocidad^21^:

SQL

*-- Habilitar extensión criptográfica estándar para generación de identificadores únicos UUIDv4*

*CREATE* EXTENSION IF *NOT* *EXISTS* "uuid-ossp";

*-- Tabla de Señales de Origen (TradingView)*

*-- Almacena el historial exhaustivo de alertas de entrada enviadas por TradingView*

*CREATE* *TABLE* tradingview_signals (

    signal_id UUID *PRIMARY* KEY *DEFAULT* uuid_generate_v4(),

    idempotency_key *VARCHAR*(*255*) *UNIQUE* *NOT* *NULL*, *-- UUIDv7 enviado en cabecera HTTP [cite: 35, 37]*

    virtual_trade_id *VARCHAR*(*100*) *NOT* *NULL*, *-- Identificador de la estrategia de TV (ID de trade del Strategy Tester)*

    symbol *VARCHAR*(*50*) *NOT* *NULL*,

    action *VARCHAR*(*20*) *NOT* *NULL*, *-- BUY, SELL, FLATTEN [cite: 9, 42]*

    requested_qty *NUMERIC*(*18*, *8*) *NOT* *NULL*,

    expected_prev_position *VARCHAR*(*20*) *NOT* *NULL*, *-- LONG, SHORT, FLAT*

    expected_next_position *VARCHAR*(*20*) *NOT* *NULL*, *-- LONG, SHORT, FLAT*

    target_quantity *NUMERIC*(*18*, *8*) *NOT* *NULL*, *-- strategy.position_size esperada tras el trade*

    pine_timestamp *TIMESTAMP* *WITH* *TIME* ZONE *NOT* *NULL*, *-- Marca de tiempo de origen de la vela ({{time}})*

    raw_payload JSONB *NOT* *NULL*, *-- Payload crudo para depuración y almacenamiento flexible de variables*

    received_at *TIMESTAMP* *WITH* *TIME* ZONE *DEFAULT* *CURRENT_TIMESTAMP* *NOT* *NULL*

);

*-- Tabla de Órdenes Reales (Bróker)*

*-- Registra las operaciones ejecutadas físicamente en el bróker tras la confirmación de la API institucional*

*CREATE* *TABLE* broker_orders (

    order_id UUID *PRIMARY* KEY *DEFAULT* uuid_generate_v4(),

    broker_ticket_number *VARCHAR*(*100*) *UNIQUE* *NOT* *NULL*, *-- Identificador de confirmación único devuelto por la API del bróker*

    symbol *VARCHAR*(*50*) *NOT* *NULL*,

    direction *VARCHAR*(*20*) *NOT* *NULL*, *-- BUY, SELL*

    executed_qty *NUMERIC*(*18*, *8*) *NOT* *NULL*,

    executed_price *NUMERIC*(*18*, *8*) *NOT* *NULL*,

    order_type *VARCHAR*(*50*) *NOT* *NULL*, *-- MARKET, LIMIT, STOP [cite: 26, 42]*

    order_status *VARCHAR*(*50*) *NOT* *NULL*, *-- FILLED, PARTIAL, CANCELLED, REJECTED [cite: 4]*

    commission_fees *NUMERIC*(*12*, *4*) *DEFAULT* *0.0000* *NOT* *NULL*, *-- Cálculo de coste de fricción real para auditorías [cite: 6, 40]*

    raw_response JSONB *NOT* *NULL*, *-- Respuesta JSON nativa e íntegra del bróker institucional para fines de soporte [cite: 9, 29]*

    executed_at *TIMESTAMP* *WITH* *TIME* ZONE *NOT* *NULL*

);

*-- Libro Mayor de Reconciliación (Ledger)*

*-- Tabla pivote que mapea la correspondencia de doble entrada entre TradingView y el Bróker*

*CREATE* *TABLE* reconciliation_ledger (

    reconciliation_id UUID *PRIMARY* KEY *DEFAULT* uuid_generate_v4(),

    signal_id UUID *UNIQUE*, *-- Relación 1:1 estricta con la señal. Puede ser NULL si la orden física se originó sin señal (SL local) [cite: 2, 35]*

    broker_order_id UUID *UNIQUE*, *-- Relación 1:1 estricta con la orden. Puede ser NULL si la señal de TV fue bloqueada antes del envío [cite: 11, 35]*

    virtual_trade_id *VARCHAR*(*100*) *NOT* *NULL*, *-- Duplicado denormalizado para búsquedas rápidas agregadas de operaciones lógicas*

    reconciliation_status *VARCHAR*(*50*) *NOT* *NULL*, *-- MATCHED, SL_HIT_DETECTED, ORPHAN_TV_REJECTED, PARTIAL_BREAK, PRICE_SLIPPAGE_ALERT [cite: 5, 40]*

    discrepancy_qty *NUMERIC*(*18*, *8*) *DEFAULT* *0.0000* *NOT* *NULL*, *-- Cantidad TV menos Cantidad Ejecutada*

    discrepancy_price *NUMERIC*(*18*, *8*) *DEFAULT* *0.0000* *NOT* *NULL*, *-- Diferencia entre precio esperado de TV y el real obtenido (Slippage)*

    reconciled_at *TIMESTAMP* *WITH* *TIME* ZONE *DEFAULT* *CURRENT_TIMESTAMP* *NOT* *NULL*,

    audit_notes TEXT, *-- Campo libre para documentar intervenciones manuales de resolución o llamadas del sistema*

    *CONSTRAINT* fk_signal_ledger *FOREIGN* KEY (signal_id) *REFERENCES* tradingview_signals(signal_id) *ON* *DELETE* RESTRICT,

    *CONSTRAINT* fk_broker_order_ledger *FOREIGN* KEY (broker_order_id) *REFERENCES* broker_orders(order_id) *ON* *DELETE* RESTRICT

);

*-- Índices de Rendimiento Críticos para Operaciones en Tiempo Real*

*-- Optimiza la velocidad de las consultas de reconciliación y previene bloqueos de base de datos bajo alta concurrencia*

*CREATE* INDEX idx_tv_signals_virtual_trade_id *ON* tradingview_signals(virtual_trade_id);

*CREATE* INDEX idx_tv_signals_pine_timestamp *ON* tradingview_signals(pine_timestamp *DESC*);

*CREATE* INDEX idx_broker_orders_ticket *ON* broker_orders(broker_ticket_number);

*CREATE* INDEX idx_broker_orders_executed_at *ON* broker_orders(executed_at *DESC*);

*CREATE* INDEX idx_reconciliation_ledger_status *ON* reconciliation_ledger(reconciliation_status);

*CREATE* INDEX idx_reconciliation_ledger_virtual_trade_id *ON* reconciliation_ledger(virtual_trade_id);

Gestión de Relaciones de Reconciliación en el Modelo de Datos

El diseño físico de la base de datos PostgreSQL, específicamente en la tabla pivote de reconciliación (reconciliation_ledger), implementa restricciones de unicidad explícitas (UNIQUE) en los campos que enlazan con las señales de origen (signal_id) y las confirmaciones físicas de la API del bróker (broker_order_id)^35^. Esta decisión de diseño garantiza de forma estricta una correspondencia uno a uno (1:1) de nivel transaccional para operaciones que siguen el flujo estándar del sistema, mitigando la posibilidad de que una misma señal de TradingView se vincule o valide múltiples órdenes físicas en el mercado, o que múltiples boletas de confirmación del bróker pretendan respaldar una única señal virtual^29^.

Sin embargo, para dar cabida a los eventos de desincronización que la máquina de estados está diseñada para mitigar, la base de datos permite que estas claves foráneas admitan valores nulos de forma controlada^40^:

- **Orden de Ejecución Huérfana del Bróker (ORPHAN_BROKER):** Si el Stop Loss local del bróker se activa en su servidor sin la participación directa de TradingView, el middleware registra la orden del bróker de manera asíncrona creando un registro en reconciliation_ledger donde el campo signal_id se asigna como nulo (NULL) y el estado de la fila se marca como SL_HIT_DETECTED^2^. Esto documenta que existió una salida de mercado física válida e independiente que no provino de un webhook de origen, asegurando la trazabilidad de la operación para la contabilidad regulatoria^29^.
- **Señal Huérfana de TradingView (ORPHAN_TV):** Si TradingView emite una señal de cierre tardía que el middleware intercepta y decide rechazar bajo la política de seguridad wait o flatten, la señal virtual se registra en la base de datos para mantener un historial de auditoría de rendimiento de red^10^. El registro correspondiente en la tabla pivot reconciliation_ledger se almacena con el campo broker_order_id asignado como nulo (NULL), definiendo el estado de la fila como ORPHAN_TV_REJECTED^11^. Esto indica que la señal existió pero que no generó ninguna transacción física en el mercado al ser identificada como un riesgo de posición fantasma redundante^10^.

Con esta estructura de base de datos relacional y el control lógico del ledger de reconciliación, el middleware proporciona una trazabilidad operativa completa^29^. Permite realizar auditorías forenses diarias para cuantificar con precisión las desviaciones financieras debidas a latencias de red y deslizamientos de ejecución (*slippage*), consolidando la infraestructura algorítmica sobre un entorno transparente, resiliente y de bajo riesgo^3^.

Fuentes citadas

- TradingView Automated Trading - QuantVPS, https://www.quantvps.com/blog/tradingview-automated-trading
- Pine Script to Trading Bot - Nadcab Labs, https://www.nadcab.com/blog/pine-script-trading-bot-tradingview-webhook-live-execution
- stop using webhooks for live execution if you care about your money : r/TradingView, https://www.reddit.com/r/TradingView/comments/1tk71me/stop_using_webhooks_for_live_execution_if_you/
- How do you adapt a strategy when moving from backtesting to live trading? - Reddit, https://www.reddit.com/r/Daytrading/comments/1rtby56/how_do_you_adapt_a_strategy_when_moving_from/
- Automating TradingView Strategies - CrossTrade, https://crosstrade.io/docs/getting-started/complete-guides/automating-tradingview-strategies
- Production Trading Bots: 15 Failure Patterns Nobody Warns You About - Medium, https://medium.com/@florinelchis/production-trading-bots-15-failure-patterns-nobody-warns-you-about-af917d263c35
- python-statemachine 3.2.0, https://python-statemachine.readthedocs.io/
- TradingView Broker Integration - TraderEvolution, https://traderevolution.com/tradingview/
- How to Automate TradingView Alerts to Any Broker - BotJockie, https://botjockie.com/blog/tradingview-to-broker-automation.html
- How Strategy Sync Keeps TradingView and NinjaTrader in Lockstep - CrossTrade, https://crosstrade.io/blog/synchronize-tradingview-strategies
- Strategy Synchronization - CrossTrade, https://crosstrade.io/docs/webhooks/advanced-options/strategy-synchronization
- Best TradingView Auto Traders 2026: Webhook Bots, Setup Guide & Top Picks for Futures & Prop Firms - Lune Trading, https://lunefi.com/blog/best-tradingview-auto-traders-2026-webhook-bots-setup-guide
- Automating TradingView Alerts with Nubra API Using Webhooks, https://nubra.io/products/api/blogs/tradingview-to-nubra-webhook-guide
- TradingView Alerts Setup: Free Plan Limits (2026), https://www.tv-hub.org/guide/tradingview-alerts-setup
- Handle pinescript webhooks to exit a strategy : r/TradingView - Reddit, https://www.reddit.com/r/TradingView/comments/1e5f9gk/handle_pinescript_webhooks_to_exit_a_strategy/
- June 2025 Recap: CrossTrade v1.9.0 released with Strategy Sync and Continuous Contracts, https://crosstrade.io/blog/june-2025-recap
- CrossTrade Q2 2025 Recap: Strategy Sync, Continuous Contracts, and Trade Copier Preview, https://crosstrade.io/blog/crosstrade-q2-2025-recap
- Concurrent Scalping Algo Using Async Python - Alpaca, https://alpaca.markets/learn/concurrent-scalping-algo-async-python
- State Machine in Python: Run Code in Transition or State? - Stack Overflow, https://stackoverflow.com/questions/30492494/state-machine-in-python-run-code-in-transition-or-state
- StateFlow: Enhancing LLM Task-Solving through State-Driven Workflows - arXiv, https://arxiv.org/html/2403.11322v1
- An Uncomfortably Deep Dive into the Idempotency Key | by Sameer Ahmed - Medium, https://sameerahmed56.medium.com/an-uncomfortably-deep-dive-into-the-idempotency-key-67626c8d3f3d
- Handling Webhook Idempotency with Fastio API, https://fast.io/resources/fastio-webhook-idempotency-guide/
- Best practices for implementing Idempotent Requests with FastAPI #3555 - GitHub, https://github.com/fastapi/fastapi/discussions/3555
- How often do your trading bots break because of exchange API issues? - Reddit, https://www.reddit.com/r/algotrading/comments/1sfmpvn/how_often_do_your_trading_bots_break_because_of/
- How to Auto-Correct Mismatched NinjaTrader Positions with your TradingView Strategy, https://crosstrade.io/blog/auto-correct-mismatched-ninjatrader-positions-tradingview-strategy
- Place Order | CrossTrade, https://crosstrade.io/docs/webhooks/commands/place-order
- Automate TradingView Alerts with Python: Fast API Execution - Contra, https://contra.com/community/959rCAbV-automate-trading-view-alerts-with-python-fast
- Connection Loss - General Discussions - NinjaTrader Community Forum, https://discourse.ninjatrader.com/t/connection-loss/6253
- What Is Post-Trade Processing? Settlement & Reconciliation - Quod Financial, https://www.quodfinancial.com/post-trade-processing-settlement-reconciliation-and-the-back-office-lifecycle-of-a-trade/
- How to Automate TradingView Strategies with CrossTrade, https://crosstrade.io/blog/how-to-automate-tradingview-strategies-with-crosstrade
- FastAPI + Redis Streams for Sagas: Exactly-Once Orchestration Without a Message Broker, https://medium.com/@2nick2patel2/fastapi-redis-streams-for-sagas-exactly-once-orchestration-without-a-message-broker-7ce84db6bcba
- pypy-riley/idemptx: Idempotency decorator for FastAPI. Redis-based locking and replay support. - GitHub, https://github.com/pypy-riley/idemptx
- Requests at Scale — Idempotency. Double-charged users? Duplicate orders… | by Tito Adeoye | Medium, https://medium.com/@titoadeoye/requests-at-scale-idempotency-91505ccff0e0
- What is idempotency in Redis? Cost-saving patterns for LLM apps, https://redis.io/blog/what-is-idempotency-in-redis/
- Idempotency Keys, How to Prevent Duplicate Request and API Chaos | by Wahyu Bagus Sulaksono | Jul, 2026 | Medium, https://medium.com/@wahyubagus1910/idempotency-keys-how-to-prevent-duplicate-request-and-api-chaos-3ad6b1cdfe30
- How to Implement Idempotency Keys with Redis - OneUptime, https://oneuptime.com/blog/post/2026-01-21-redis-idempotency-keys/view
- Idempotency - Worldpay Developer Hub, https://docs.worldpay.com/apis/wpg/idempotency
- A Simple Way to Handle Idempotency in FastAPI using idemptx | by Riley Chen | Medium, https://medium.com/@riley.dev/a-simple-way-to-handle-idempotency-in-fastapi-using-idemptx-08d57f0faf88
- Resolving Timezone Sync Issues for Accurate Timekeeping on Your Trading Platform, https://chartvps.com/helpdesk/resolving-timezone-sync-issues-for-accurate-timekeeping-on-your-trading-platform/
- Trade Reconciliation: Process, Challenges & Best Practices (2026 Guide) - Osfin, https://www.osfin.ai/blog/trade-reconciliation
- Reconciliation Testing Aspects of Trading Systems Software Failures - Exactpro, https://exactpro.com/sites/default/files/attachments/SYRCOSE-2014_ReconciliationTestingAspects_of_TradingSystemsSoftwareFailures.pdf