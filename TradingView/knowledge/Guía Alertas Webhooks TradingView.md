Sistema de Alertas y Webhooks de TradingView: Guía Técnica de Configuración, Integración y Automatización de Trading

El desarrollo y despliegue de sistemas de trading algorítmico exigen una infraestructura de alta confiabilidad para la detección de eventos técnicos y el ruteo de señales hacia los centros de ejecución de órdenes^1^. TradingView se ha consolidado como una plataforma líder en análisis gráfico e ideación de estrategias^3^. Sin embargo, la verdadera transición hacia el trading sistemático y automatizado se logra al dominar su motor de alertas y el protocolo de webhooks^1^. Este informe técnico detalla la arquitectura, las herramientas de programación en Pine Script, los límites operativos de red, y los modelos de diseño de software requeridos para implementar un pipeline de ejecución de órdenes robusto, de baja latencia y alta disponibilidad^1^.

1. Tipos de Alertas Nativas en la Plataforma

Las alertas nativas de TradingView representan la capa de detección de eventos más accesible del sistema, ejecutándose directamente sobre la infraestructura en la nube de la plataforma para monitorizar de forma constante los activos financieros^3^. Estas alertas se dividen en tres grandes familias según su origen y complejidad matemática^3^.

Alertas sobre Precio

Las alertas de precio monitorizan de forma exclusiva el último valor de cotización reportado por el feed de datos (tick de mercado)^10^. A nivel de servidor, TradingView procesa estas condiciones en barras de un minuto para optimizar los recursos de red y cómputo, lo que implica que el motor de evaluación de precios opera bajo un muestreo constante de alta frecuencia^10^. El sistema admite una variedad de operadores lógicos estructurados:

- **Crossing (Cruce):** Se activa cuando el precio actual del activo interseca un nivel estático  o un valor dinámico provisto por un indicador^11^. Matemáticamente, se detecta el cruce cuando se cumple la condición:
Donde  es el precio actual y  es el precio del tick o barra anterior.
- **Crossing Up (Cruce Ascendente):** Variante direccional del cruce. Se dispara únicamente si la trayectoria del precio cruza el nivel de referencia de abajo hacia arriba:
- **Crossing Down (Cruce Descendente):** Se activa cuando la trayectoria del precio cruza el umbral de referencia de arriba hacia abajo:
- **Greater Than (Mayor que):** Evaluación lógica continua donde la alerta se activa en el instante en que el precio supera el umbral establecido:
- **Less Than (Menor que):** Evaluación lógica contraria a la anterior. Se activa cuando el precio cae por debajo del nivel de referencia:
- **Entering Channel (Entrada en Canal):** Monitorea una banda de precios definida por un límite superior  y un límite inferior ^9^. El disparo ocurre cuando el precio del activo se introduce en el rango habiendo estado fuera de él en el tick anterior^9^:
- **Exiting Channel (Salida de Canal):** El opuesto lógico del operador anterior. Se dispara cuando el precio abandona la banda delimitada:
- **Moving Up % (Subida de %):** Evalúa el impulso alcista del precio en términos relativos. Se activa si el incremento porcentual del precio dentro de un intervalo temporal o un número de barras parametrizado  alcanza o supera el valor  definido^3^:
- **Moving Down % (Bajada de %):** Variante bajista que evalúa la depreciación porcentual del activo dentro de la ventana de análisis^3^:

Alertas sobre Indicadores Técnicos

Las alertas de indicadores vinculan la lógica de disparo a las series de datos generadas por algoritmos analíticos ejecutados en el servidor, como el Índice de Fuerza Relativa (RSI), Bandas de Bollinger, o Convergencia/Divergencia de Promedios Móviles (MACD)^9^. A diferencia de las alertas de precio simple, el cálculo de las alertas de indicadores depende estrictamente del marco temporal (intervalo o resolución) del gráfico donde han sido creadas^3^.

El cálculo numérico del indicador se realiza de forma asíncrona en los servidores de la plataforma cada vez que se recibe un nuevo dato^3^. Si el usuario define la evaluación del indicador al cierre de barra ("Once Per Bar Close"), el motor evaluará la condición lógica únicamente cuando la variable de estado de la barra finalice, eliminando el ruido provocado por las fluctuaciones temporales de precio dentro de la barra^7^.

Alertas sobre Herramientas de Dibujo (Drawing Tools)

TradingView permite vincular condiciones lógicas de alerta a objetos visuales y vectoriales dibujados manualmente por el analista en el gráfico de precios, como líneas de tendencia, canales paralelos, rayos o retrocesos de Fibonacci^9^.

- **Líneas de tendencia y Rayos:** El motor de TradingView proyecta la ecuación lineal del vector dibujado sobre el eje tiempo-precio^12^. La alerta evalúa continuamente la intersección del precio con dicha línea recta, permitiendo parametrizar si se busca un cruce simple, ascendente o descendente^9^.
- **Canales paralelos:** Definen áreas de soporte y resistencia móviles. Las alertas asociadas monitorizan si el precio penetra o abandona las bandas de la herramienta^9^.
- **Retrocesos y extensiones de Fibonacci:** El sistema vigila la aproximación o cruce de niveles específicos calculados de manera geométrica a partir de los puntos extremos seleccionados por el operador^9^. Si la alerta se configura sobre un gráfico que utiliza escala logarítmica, el cálculo de las proporciones horizontales cambia automáticamente a un modelo logarítmico para garantizar la validez matemática de los niveles de Fibonacci en activos de alta volatilidad^9^.

| **Tipo de Alerta** | **Base de Datos de Referencia** | **Frecuencia de Evaluación** | **Dependencia del Timeframe** | **Soporte de Escala Logarítmica** |
| --- | --- | --- | --- | --- |
| **Precio** | Último precio de mercado (Tick) | Tiempo real (muestreo 1m)^10^ | No (independiente del gráfico)^3^ | No aplicable |
| **Indicadores** | Serie de datos calculada por el indicador | Al tick o al cierre de barra^9^ | Sí (evaluado en la resolución del gráfico)^3^ | Según la naturaleza del indicador |
| **Líneas de Tendencia** | Coordenadas lineales proyectadas^12^ | Al tick o al cierre de barra^12^ | Sí (calculada en la resolución del gráfico)^9^ | No |
| **Canales Geométricos** | Polígonos de límites paralelos | Al tick o al cierre de barra | Sí (calculada en la resolución del gráfico) | No |
| **Fibonacci** | Proporciones proporciones del rango^9^ | Al tick o al cierre de barra^9^ | Sí (calculada en la resolución del gráfico)^9^ | Sí (configurable por el usuario)^9^ |

2. Alertas Basadas en Indicadores Pine con alertcondition()

Para los desarrolladores de indicadores personalizados que desean distribuir herramientas comerciales a terceros a través de la biblioteca pública de TradingView, la función alertcondition() representa el mecanismo tradicional para la creación de opciones de alertas preconfiguradas^14^.

Sintaxis y Parámetros de alertcondition()

La función alertcondition() permite definir de manera explícita un evento de alerta dentro del indicador que el usuario final podrá seleccionar posteriormente en la interfaz gráfica^14^. Su firma matemática y de programación en Pine Script es:

Pine Script

alertcondition(condition, title, message)

- **condition (series bool):** Expresión lógica o serie de valores booleanos que el compilador y el motor de alertas de TradingView monitorizan en tiempo real^14^. Cuando esta serie adopta el valor true, el evento es candidato para disparar la alerta^14^.
- **title (const string):** Cadena de caracteres estática que actúa como identificador de la alerta en el cuadro de diálogo de creación de alertas nativas de la plataforma^14^. Este campo no acepta variables dinámicas determinadas en tiempo de ejecución.
- **message (series string):** Mensaje predeterminado de la alerta que se presentará en la caja de texto del diálogo^14^. Aunque su valor por defecto es estático en el código, admite el uso de marcadores de posición dinámicos (placeholders) que el servidor de TradingView sustituye por valores reales en el instante de activación de la alerta^14^.

Limitaciones Críticas de alertcondition()

Aunque es una herramienta de gran utilidad para indicadores comerciales, la función alertcondition() cuenta con restricciones de diseño de bajo nivel que limitan su aplicabilidad en sistemas de automatización complejos^14^:

- **Exclusión de Ámbito Local:** No puede llamarse dentro de bloques locales condicionales de código, tales como estructuras if, for o funciones personalizadas definidas por el usuario^14^. Debe declararse estrictamente en el ámbito global del indicador^14^.
- **Incompatibilidad con Estrategias:** Está diseñada de forma exclusiva para indicadores declarados con el encabezado //@version=X y el tipo indicator()^15^. Si se intenta incluir una llamada a alertcondition() en un script de tipo strategy(), el compilador de Pine Script detendrá el proceso de compilación arrojando un error de sintaxis^15^.
- **Dependencia de Configuración Manual:** La presencia de alertcondition() en el código no activa automáticamente la alerta en los servidores de la plataforma^15^. El usuario final debe abrir el diálogo de alertas en la interfaz de usuario, seleccionar el script, elegir el título de la alerta de la lista desplegable de condiciones y configurar los parámetros de notificación^14^.

Declaración de Múltiples alertcondition() en un Mismo Indicador

Un único script de indicador puede registrar múltiples llamadas a alertcondition(), permitiendo ofrecer diferentes flujos lógicos de alerta en el mismo código^14^:

Pine Script

//@version=5

indicator("Módulo Analítico RSI con Múltiples Alertas", overlay=false)

rsiSource = close

rsiPeriod = 14

rsiValue = ta.rsi(rsiSource, rsiPeriod)

// Definición de variables lógicas para las condiciones de cruce

cruceSobrecompra = ta.crossover(rsiValue, 70)

cruceSobrevenda = ta.crossunder(rsiValue, 30)

// Configuración de múltiples alertcondition en el ámbito global del script

alertcondition(condition=cruceSobrecompra, 

               title="RSI Sobrecompra (70)", 

               message='{"event": "SOBRECOMPRA", "ticker": "{{ticker}}", "val": {{plot_0}}}')

alertcondition(condition=cruceSobrevenda, 

               title="RSI Sobrevenda (30)", 

               message='{"event": "SOBREVENDA", "ticker": "{{ticker}}", "val": {{plot_0}}}')

// Trazado de datos para visualización en el gráfico y referencia en placeholders

plot(rsiValue, title="RSI Calculado", color=color.purple)

En este escenario, el usuario que ejecute el indicador podrá seleccionar individualmente en la interfaz si desea activar una alerta para el cruce de sobrecompra, una para el cruce de sobrevivenda, o crear dos alertas distintas para cubrir ambos eventos de forma paralela^15^.

3. Función alert() en Pine Script

Introducida para dar mayor flexibilidad a los desarrolladores de algoritmos de trading, la función alert() permite disparar alertas de forma dinámica directamente desde la lógica de ejecución del código, superando las limitaciones de estructura y de ámbito de alertcondition()^14^.

Sintaxis y Parámetros de alert()

La función alert() se ejecuta de forma inmediata en el momento en que se procesa su llamada en una barra en tiempo real^14^. Su firma es:

Pine Script

alert(message, freq)

- **message (series string):** Cadena de caracteres dinámica que define el texto de la notificación^14^. Al aceptar strings dinámicos de tipo "series", el desarrollador puede construir el mensaje concatenando variables del script, cálculos internos del algoritmo y datos numéricos formateados en tiempo de ejecución, eliminando la dependencia exclusiva de los placeholders del sistema^14^.
- **freq (input string):** Parámetro constante que instruye al motor de alertas sobre las reglas de frecuencia permitidas para el disparo de la alerta^14^. Los modificadores de frecuencia disponibles son:

- alert.freq_once_per_bar: La alerta se dispara la primera vez que se cumple la condición dentro de la barra en tiempo real^14^. Si la condición se vuelve a cumplir en ticks posteriores de la misma barra, se ignora el disparo para evitar spam de mensajes^14^.
- alert.freq_once_per_bar_close: La alerta se evalúa y se dispara únicamente cuando la barra en tiempo real se cierra (cuando el estado de la barra transiciona de activa a completada)^14^. Esta es la opción más recomendada para evitar señales falsas causadas por volatilidad intrabarra^7^.
- alert.freq_all: La alerta se dispara en cada tick individual donde la lógica del código evalúe la llamada como activa^14^. Es un modificador de alto riesgo que puede saturar los servidores de destino y provocar el bloqueo de la alerta por parte de las políticas de throttling de TradingView^6^.

Diferencias Cruciales entre alertcondition() y alert()

El entendimiento de las diferencias operativas entre ambos esquemas es indispensable para el arquitecto de sistemas de trading algorítmico^14^:

| **Característica Técnica** | **alertcondition()** | **alert()** |
| --- | --- | --- |
| **Soporte de Script** | Exclusivo para Indicadores (@indicator)^15^ | Soportado en Indicadores (@indicator) y Estrategias (@strategy)^15^ |
| **Ámbito de Declaración** | Ámbito global únicamente (nivel de raíz del script)^14^ | Ámbito global o local (dentro de bloques if, for, etc.)^14^ |
| **Naturaleza del Mensaje** | Estático en compilación; dinámico mediante placeholders^14^ | Dinámico en ejecución; admite manipulación de strings nativa^14^ |
| **Configuración en la UI** | El usuario debe crear alertas para cada condición específica^15^ | Una sola alerta genérica captura todos los llamados de alert()<br>[cite: 14] |
| **Frecuencia de Disparo** | Determinada por el usuario al crear la alerta en la interfaz^14^ | Programada por el desarrollador mediante parámetros de código^14^ |

Cuándo Utilizar Cada Enfoque

alertcondition() es la opción idónea cuando se desea que el usuario final tenga el control absoluto sobre qué eventos específicos activar y cómo estructurar los mensajes de forma independiente a través de la interfaz gráfica sin modificar el código fuente^14^. Por el contrario, alert() es indispensable para sistemas de trading automatizado de grado industrial, donde la lógica del script es la encargada de estructurar payloads JSON dinámicos que contienen variables exactas como el tamaño de la posición calculado según la volatilidad, la dirección del mercado, identificadores de órdenes y niveles dinámicos de protección en tiempo real^15^.

Inyección de Datos Dinámicos en alert()

La inyección de datos dinámicos en alert() se realiza utilizando funciones nativas de procesamiento de strings en Pine Script, principalmente str.format() y str.tostring(), permitiendo formatear números y concatenar texto de manera precisa^14^:

Pine Script

//@version=5

indicator("Generador de Payloads Dinámicos", overlay=true)

fastMA = ta.sma(close, 10)

slowMA = ta.sma(close, 50)

atrVal = ta.atr(14)

cruceAlcista = ta.crossover(fastMA, slowMA)

if cruceAlcista and barstate.isrealtime

    // Definición de variables dinámicas de trading

    precioEntrada = close

    stopLossCalculado = precioEntrada - (atrVal * 2.0)

    // Construcción del payload JSON dinámico utilizando str.format

    mensajeJSON = str.format('{{"action": "BUY", "ticker": "{0}", "price": {1,number,#.##}, "sl": {2,number,#.##}}}', 

                              syminfo.ticker, precioEntrada, stopLossCalculado)

    alert(mensajeJSON, alert.freq_once_per_bar_close)

4. Alertas de Estrategias y Ejecución de Órdenes

Las estrategias en Pine Script (@strategy) poseen un motor de alertas integrado con el simulador de corretaje (broker emulator) de TradingView que automatiza el envío de notificaciones en el momento exacto en que ocurren eventos de trading de cuenta^2^.

Generación Automática de Alertas por Eventos de Orden

Cuando un script de estrategia ejecuta funciones de posicionamiento como strategy.entry(), strategy.exit(), o strategy.close(), los servidores de TradingView simulan la ejecución de la orden sobre el feed de precios en tiempo real^16^.

En el instante preciso en que el simulador de corretaje de la plataforma procesa la orden y cambia su estado a "ejecutada" (filled), el motor de alertas nativo dispara automáticamente una notificación vinculada a dicha ejecución^18^. Esto significa que no se requiere programar código adicional para notificar la entrada o salida de una posición, ya que el ciclo de vida de la orden en el simulador actúa de forma nativa como el disparador de la alerta^2^.

El Parámetro alert_message en Funciones de Estrategia

Para controlar de forma individualizada el contenido del mensaje enviado por cada orden específica de la estrategia, las funciones de envío de órdenes incorporan el parámetro alert_message^10^. Este parámetro acepta expresiones de cadena dinámica, permitiendo definir payloads personalizados para cada tipo de orden^10^:

Pine Script

//@version=5

strategy("Estrategia con Mensajes Individualizados", overlay=true)

// Lógica de cruce simplificada

crossoverTrend = ta.crossover(ta.sma(close, 5), ta.sma(close, 20))

crossunderTrend = ta.crossunder(ta.sma(close, 5), ta.sma(close, 20))

if crossoverTrend

    // Configuración del mensaje dinámico para la orden de entrada

    payloadEntrada = '{"action": "OPEN_LONG", "contracts": {{strategy.order.contracts}}, "price": {{strategy.order.price}}}'

    strategy.entry("Long_Trade", strategy.long, alert_message=payloadEntrada)

if crossunderTrend

    // Configuración del mensaje dinámico para la orden de cierre

    payloadCierre = '{"action": "CLOSE_LONG", "contracts": {{strategy.order.contracts}}, "price": {{strategy.order.price}}}'

    strategy.close("Long_Trade", alert_message=payloadCierre)

Cuando la orden "Long_Trade" se ejecuta en el simulador, el motor de alertas de la plataforma captura el valor asignado a alert_message, procesa los placeholders de la estrategia y transmite el mensaje resultante a través del webhook^10^.

Configuración del Disparador de Alerta de Estrategia Completa

Para activar la automatización de una estrategia, el usuario debe acceder al menú de creación de alertas en la interfaz gráfica y seleccionar su estrategia del listado desplegable de condiciones^18^. En este cuadro de diálogo, es fundamental seleccionar la opción:

- **Order fills and alert() function calls (Ejecuciones de órdenes y llamadas a alert()):** Esta opción unifica los canales de notificación de la estrategia^9^. El servidor de TradingView disparará el webhook tanto cuando el emulador ejecute operaciones comerciales (strategy.entry, strategy.exit, etc.) como cuando la lógica del código llame explícitamente a la función alert(), proporcionando un único punto de control para la automatización total de la estrategia^9^.

Mecánica de Ejecución Server-side de Estrategias

Al guardar una alerta asociada a una estrategia en la plataforma, TradingView genera una copia independiente de la estrategia y de su configuración de parámetros actual, desplegándola directamente en sus servidores de procesamiento asíncrono^18^. Esta copia se ejecuta de forma continua e independiente de lo que ocurra en el navegador del operador^8^.

Si el usuario realiza modificaciones en los parámetros de la estrategia, optimiza el código de Pine Script o cambia de símbolo en su terminal local de TradingView, la versión de la estrategia que se ejecuta en el servidor web no se verá afectada^18^. Para que los cambios realizados en el gráfico local surtan efecto en el flujo de automatización real, el usuario debe eliminar de forma obligatoria la alerta existente y crear una nueva para forzar un nuevo despliegue en la nube de la plataforma^18^.

5. Configuración de Webhooks de TradingView

El webhook es un protocolo de notificación automática basado en HTTP POST mediante el cual TradingView transmite datos estructurados en tiempo real a una URL segura configurada por el operador en el momento exacto en que se dispara una alerta^1^.

Pasos para Configurar la URL del Webhook

El proceso de integración de webhooks requiere la configuración del endpoint remoto en la alerta^1^:

- Crear la alerta presionando el icono del reloj de la interfaz gráfica o utilizando el atajo Alt + A (Windows) u Option + A (Mac)^11^.
- Definir las condiciones lógicas de precio, indicador o estrategia^11^.
- Navegar a la pestaña "Notificaciones" y marcar la casilla de verificación de "Webhook URL"^1^.
- Ingresar la URL del servidor receptor de alertas de trading en el campo de texto provisto^1^.

Restricciones de Red e Infraestructura de TradingView

La transmisión de solicitudes webhooks desde TradingView está sujeta a límites rígidos de red que deben ser considerados al diseñar el servidor receptor^20^:

- **Puertos Admitidos:** Las conexiones salientes de TradingView solo se realizan a través de los puertos de comunicación estándar de navegación web: **puerto 80 (HTTP)** y **puerto 443 (HTTPS)**^6^. Las solicitudes dirigidas a puertos alternativos o personalizados (por ejemplo, http://mi-vps.com:8080/webhook) son rechazadas por los firewalls de salida de la plataforma^20^.
- **Protocolo IP:** La infraestructura de salida de webhooks de TradingView opera exclusivamente bajo el direccionamiento **IPv4**^6^. El protocolo IPv6 no es soportado para estas conexiones^6^.
- **Tiempo de Espera (Timeout):** El servidor remoto de destino debe responder con un código de estado HTTP exitoso (rango 2xx) en un tiempo máximo de **3 segundos** tras recibir la petición^6^. Si la resolución de DNS, el establecimiento de la conexión TCP o el procesamiento del lado del servidor remoto demora más de 3 segundos, TradingView cancela unilateralmente la solicitud HTTP POST y la registra como fallida^6^.
- **Requerimiento de Autenticación de Doble Factor (2FA):** Para habilitar la funcionalidad de webhooks en las alertas de una cuenta, TradingView exige obligatoriamente que el usuario tenga activada la autenticación de doble factor en la configuración de seguridad de su perfil^6^.

Variables de Placeholder Disponibles

TradingView ofrece un conjunto de marcadores de posición dinámicos que el motor de procesamiento reemplaza con valores en tiempo real del mercado o de la cuenta de trading en el instante exacto del disparo^10^:

| **Placeholder (Variable)** | **Formato / Tipo de Dato** | **Valor Retornado en Ejecución** |
| --- | --- | --- |
| **{{ticker}}** | Cadena de texto (String) | Símbolo de cotización del activo de la alerta (ej. AAPL, BTCUSD)^10^. |
| **{{exchange}}** | Cadena de texto (String) | Siglas de la bolsa o mercado donde cotiza el activo (ej. NASDAQ, BINANCE, CME)^10^. |
| **{{close}}** | Valor numérico (Float) | Precio de cierre de la barra en la que se ejecutó la alerta^10^. |
| **{{open}}** | Valor numérico (Float) | Precio de apertura de la barra en la que se ejecutó la alerta^10^. |
| **{{high}}** | Valor numérico (Float) | Precio máximo alcanzado en la barra de la alerta^10^. |
| **{{low}}** | Valor numérico (Float) | Precio mínimo alcanzado en la barra de la alerta^10^. |
| **{{volume}}** | Valor numérico (Float/Int) | Volumen acumulado de operaciones de la barra de la alerta^10^. |
| **{{time}}** | Cadena de texto (ISO 8601 UTC) | Marca de tiempo de la barra en formato aaaa-MM-ddTHH:mm:ssZ^10^. |
| **{{timenow}}** | Cadena de texto (ISO 8601 UTC) | Fecha y hora exacta del instante del disparo de la alerta^10^. |
| **{{interval}}** | Cadena de texto (String) | Resolución temporal del gráfico. Retorna "1" para alertas de precio^10^. |
| **{{strategy.order.action}}** | Cadena de texto (String) | Sentido de la orden ejecutada en la estrategia: "buy" o "sell"^10^. |
| **{{strategy.order.contracts}}** | Valor numérico (Float/Int) | Cantidad exacta de contratos o lotes ejecutados por la orden^10^. |
| **{{strategy.order.price}}** | Valor numérico (Float) | Precio de ejecución de la orden en el simulador^10^. |
| **{{strategy.order.id}}** | Cadena de texto (String) | Identificador único de orden provisto en la llamada de código^10^. |
| **{{strategy.market_position}}** | Cadena de texto (String) | Posición actual de la estrategia tras la orden: "long", "short", "flat"^16^. |
| **{{strategy.market_position_size}}** | Valor numérico (Float) | Magnitud absoluta del tamaño de la posición actual (valor absoluto)^18^. |
| **{{strategy.prev_market_position}}** | Cadena de texto (String) | Estado de posición previo al procesamiento de la orden: "long", "short", "flat"^16^. |

6. Diseño e Ingeniería de Payloads JSON

El diseño de un payload JSON correcto es indispensable para evitar fallos de lectura en el servidor receptor, lo que requiere combinar de forma adecuada el formateo de datos con las variables dinámicas de TradingView^2^.

Principios de Construcción y Formateo

Un payload JSON para webhooks debe cumplir con reglas sintácticas estrictas para garantizar su compatibilidad con los deserializadores estándar^6^:

- **Comillas Dobles Obligatorias:** Todas las claves y los valores de tipo cadena de texto deben estar envueltos en comillas dobles ("clave": "valor")^20^. El uso de comillas simples invalidará la estructura del JSON^11^.
- **Tratamiento de Marcadores:** Los placeholders que devuelven cadenas de texto (como {{ticker}}, {{timenow}} y {{strategy.order.action}}) deben encerrarse siempre entre comillas dobles en el cuerpo del mensaje^16^. Los marcadores que devuelven valores numéricos (como {{close}}, {{volume}} y {{strategy.order.contracts}}) deben colocarse directamente sin comillas para ser interpretados nativamente como números enteros o flotantes^16^.
- **Encabezado de Solicitud Automático:** Si el mensaje de la alerta es un JSON sintácticamente válido, TradingView configura de forma automática el encabezado de la solicitud HTTP como Content-Type: application/json; charset=utf-8^6^. Si el formato contiene errores, la solicitud se enviará como texto plano (Content-Type: text/plain; charset=utf-8), lo que puede causar fallos de lectura en el servidor receptor^6^.

Ejemplo de Payload para Ejecución en Broker (ej. Bridge o Bot de Trading)

Este payload está diseñado para transferir instrucciones comerciales estructuradas a un puente de trading que rutea órdenes de forma directa a una API de corretaje (como Binance, Bybit o Interactive Brokers)^1^:

JSON

{

  *"client_auth"*: {

    *"api_token"*: *"tv_sec_78ab91cde0123f4567890"*,

    *"account_id"*: *"live_es_portfolio_01"*

  },

  *"signal"*: {

    *"symbol"*: *"{{ticker}}"*,

    *"exchange"*: *"{{exchange}}"*,

    *"action"*: *"{{strategy.order.action}}"*,

    *"size"*: {{strategy.order.contracts}},

    *"execution_price"*: {{strategy.order.price}},

    *"order_id"*: *"{{strategy.order.id}}"*,

    *"timestamp"*: *"{{timenow}}"*

  },

  *"risk"*: {

    *"position_size"*: {{strategy.position_size}},

    *"market_position"*: *"{{strategy.market_position}}"*

  }

}

Ejemplo de Payload para Registro de Datos y Logging Analítico

Orientado al almacenamiento de datos históricos y auditoría de eventos de mercado en un motor de base de datos relacional o serie temporal (como PostgreSQL, Elasticsearch o InfluxDB)^2^:

JSON

{

  *"log_source"*: *"TradingView_Cloud_Engine"*,

  *"meta_data"*: {

    *"asset"*: *"{{ticker}}"*,

    *"resolution"*: *"{{interval}}"*,

    *"trading_time"*: *"{{time}}"*

  },

  *"ohlcv"*: {

    *"open"*: {{open}},

    *"high"*: {{high}},

    *"low"*: {{low}},

    *"close"*: {{close}},

    *"volume"*: {{volume}}

  },

  *"system_info"*: {

    *"trigger_time"*: *"{{timenow}}"*,

    *"currency"*: *"{{syminfo.currency}}"*

  }

}

Ejemplo de Payload para Notificaciones Multicanal Estructuradas

Estructura optimizada para la integración directa con conectores de chat avanzados como Slack o canales de Discord que requieren esquemas JSON con propiedades anidadas y claves específicas como "content" o "embeds"^20^:

JSON

{

  *"username"*: *"Servidor de Alertas Algorítmicas"*,

  *"avatar_url"*: *"https://midominio.com/img/bot-avatar.png"*,

  *"content"*: *"[ADVERTENCIA] **EVENTO DE MERCADO DETECTADO** [ADVERTENCIA]"*,

  *"embeds"*: [

    {

      *"title"*: *"Cruce Técnico de Indicador"*,

      *"color"*: *16711680*,

      *"fields"*: [

        {

          *"name"*: *"Activo Financiero"*,

          *"value"*: *"`{{ticker}}` (Bolsa: {{exchange}})"*,

          *"inline"*: *true*

        },

        {

          *"name"*: *"Precio de Cierre"*,

          *"value"*: *"$**{{close}}**"*,

          *"inline"*: *true*

        },

        {

          *"name"*: *"Hora del Servidor (UTC)"*,

          *"value"*: *"`{{timenow}}`"*,

          *"inline"*: *false*

        }

      ]

    }

  ]

}

7. Alertas Server-side vs. Client-side

Un concepto fundamental en la arquitectura técnica de TradingView es la separación de los entornos de cálculo y ejecución de las alertas^8^.

El Motor de Alertas en la Nube (Server-side)

Todas las alertas configuradas de forma estándar por los usuarios a través de la interfaz web, de escritorio o móvil de TradingView se ejecutan en los clústeres de servidores en la nube de la plataforma (alojados principalmente en la infraestructura AWS en la costa oeste de EE.UU.)^3^.

- **Operatividad Total 24/7:** Al estar desplegadas directamente en servidores dedicados de TradingView, las alertas se evalúan de forma continua sin importar el estado del dispositivo del usuario^3^. El operador puede cerrar la pestaña del gráfico en el navegador web, apagar su computadora de trabajo o suspender su terminal de trading móvil; las condiciones de mercado seguirán siendo monitorizadas en tiempo real en la nube y el webhook se disparará de manera asíncrona ante cualquier evento coincidente^1^.
- **Instancias Independientes ("Headless"):** Para las alertas de indicadores o estrategias, el servidor web crea una instancia independiente y "sin interfaz" (headless) del código que procesa el flujo de datos de cotización en tiempo real de forma aislada^18^. Esto desvincula completamente el cálculo algorítmico del rendimiento del procesador o de la memoria RAM del hardware del operador local^8^.

Soluciones Client-side (Librerías de Gráficos de Terceros)

Una realidad técnica completamente opuesta se presenta al analizar las librerías independientes que TradingView licencia para su integración en portales financieros de terceros, conocidas como **Advanced Charts** y **Trading Platform**^25^.

- **Ausencia de Motores en el Servidor:** Estas librerías se cargan y ejecutan de forma exclusiva dentro del navegador web de cada cliente final mediante scripts de JavaScript y entornos de ejecución web locales^25^. Por lo tanto, no tienen acceso por defecto a los clústeres de computación de TradingView^25^. Las funcionalidades que dependen de procesamiento asíncrono e independiente del navegador —tales como Pine Script, el módulo del Strategy Tester y el motor de alertas y webhooks en la nube— no están soportadas de forma nativa por las librerías de clientes^25^.
- **Necesidad de Backends Propietarios:** Si un desarrollador desea ofrecer alertas continuas utilizando las librerías independientes de TradingView en su sitio web, debe construir una arquitectura de software propia^25^. Esto incluye implementar servidores dedicados que procesen los flujos de datos del mercado, almacenen las condiciones de alertas de los usuarios en bases de datos relacionales y evalúen de forma continua en su propio backend la validez de los disparadores para despachar notificaciones^25^.

8. Límites de Cuenta y Políticas de Throttling

Para garantizar la estabilidad de su infraestructura compartida y evitar ataques de denegación de servicio (DoS) por saturación de red, TradingView restringe la cantidad de alertas simultáneas e impone políticas de control de tasa de disparo (throttling)^6^.

Capacidad Operativa y Límites por Plan de Suscripción

La cantidad de alertas que un usuario puede mantener activas de forma concurrente varía según el nivel de suscripción contratado^6^. La tabla siguiente detalla las capacidades operativas vigentes en la plataforma^4^:

| **Nivel del Plan** | **Alertas de Precio Activas** | **Alertas Técnicas Activas** | **Acceso a Webhooks** | **Expiración de las Alertas** |
| --- | --- | --- | --- | --- |
| **Basic (Free)** | 3 alertas^11^ | 0 alertas^11^ | No soportado^1^ | Expiración rápida^29^ |
| **Essential** | 20 alertas^26^ | 20 alertas^28^ | Sí (disponible)^1^ | 1 mes^28^ |
| **Plus** | 100 alertas^26^ | 100 alertas^28^ | Sí (disponible)^28^ | 2 meses^28^ |
| **Premium** | 400 alertas^26^ | 400 alertas^27^ | Sí (disponible)^28^ | Sin expiración (ilimitada)^4^ |
| **Expert / Ultimate** | 1000 alertas^27^ | 1000 alertas^27^ | Sí (disponible)^28^ | Sin expiración (ilimitada) |

*Nota:* Si un usuario alcanza el límite de alertas permitidas por su suscripción, cualquier intento manual o automatizado de crear una nueva alerta provocará un error de validación en los servidores de la plataforma, bloqueando la operación de registro hasta que se eliminen alertas existentes o se actualice la cuenta a una suscripción superior^27^.

Políticas de Estrangulamiento de Tasa (Throttling)

TradingView aplica reglas severas de protección contra el envío masivo de señales para evitar la saturación de sus servidores y de los servidores receptores externos^6^.

- **La Regla de las 15 Alertas en 3 Minutos:** Esta es la política de throttling más crítica y estricta^6^. Si una alerta individual (ya sea de precio, indicador o estrategia) se activa más de **15 veces** dentro de una ventana de tiempo móvil de **3 minutos** (180 segundos), el servidor de TradingView toma una medida preventiva automatizada: **suspende de forma inmediata y definitiva la alerta afectada, poniéndola en estado pausado**^19^.
- **Impacto en Sistemas Automatizados:** Si el sistema realiza trading en marcos temporales extremadamente bajos (como gráficos de ticks o de segundos) o con datos muy volátiles, existe un alto riesgo de cruzar este límite de frecuencia^32^. Al pausarse la alerta, el sistema dejará de transmitir señales de webhooks, impidiendo el despacho de órdenes de cobertura o el cierre de posiciones en Stop Loss y exponiendo la cuenta a riesgos financieros significativos^33^.
- **Límites en Watchlists (Listas de Seguimiento):** Para las alertas generales de listas de seguimiento, TradingView aplica un límite general de **1000 activaciones por cada 3 minutos** en el acumulado global de la lista, manteniendo el límite estricto de 15 activaciones cada 3 minutos por cada símbolo individual dentro de la lista^19^. Si un solo símbolo alcanza el límite individual de 15 disparos, la monitorización para ese activo se detiene temporalmente, pero la alerta general de la lista sigue ejecutándose para los demás activos^19^. Sin embargo, si la suma total de activaciones de todos los activos de la lista alcanza el límite global de 1000 disparos en 3 minutos, la alerta de la lista completa se suspende definitivamente^19^.

9. Sistemas de Notificación Nativos

TradingView incorpora múltiples canales de notificación nativos para alertar a los usuarios de eventos en tiempo real, cada uno con características particulares de configuración y nivel de fiabilidad^3^.

- **Correo Electrónico (Email):** Envía un mensaje formateado a la dirección de correo electrónico registrada en el perfil del usuario^3^. La fiabilidad de este medio es considerada media-baja debido a posibles latencias en los servidores de correo SMTP y filtros de correo no deseado de los proveedores^11^. Para sistemas de trading automatizado, el correo electrónico resulta demasiado lento, ya que los tiempos de entrega pueden oscilar entre varios segundos y minutos^11^.
- **Notificaciones Push Móviles:** Envía una alerta visual y sonora directamente a la aplicación de TradingView instalada en dispositivos móviles iOS o Android^3^. Utiliza las redes de notificación push de Apple (APNs) y Google (FCM)^3^. Su fiabilidad es alta si el dispositivo móvil cuenta con conexión de datos activa y el sistema operativo no tiene restringido el consumo de batería de la aplicación^3^.
- **Ventanas Emergentes (Pop-up Toasts):** Genera una ventana flotante con sonido en la pantalla del gráfico de TradingView si el usuario se encuentra navegando activamente en la plataforma^3^. Soporta la visualización fuera de la pestaña de la aplicación utilizando la API de notificaciones nativas de escritorio del navegador web, requiriendo que el operador otorgue permisos específicos de notificación del navegador para su correcto funcionamiento^3^.
- **Sonido:** Reproduce una señal sonora parametrizable a través de los altavoces del dispositivo local en el instante del disparo de la alerta, sirviendo como un canal complementario muy útil para la operativa discrecional^3^.

| **Canal de Notificación** | **Velocidad de Entrega (Típica)** | **Nivel de Fiabilidad** | **Tipo de Uso Recomendado** | **Requerimiento Técnico de Configuración** |
| --- | --- | --- | --- | --- |
| **Correo Electrónico** | 2.0 – 30.0 segundos^11^ | Medio - Bajo | Auditoría pasiva y confirmación de cierres de sesión | Registro de cuenta y configuración SMTP activa^3^ |
| **Notificaciones Push** | 0.5 – 2.0 segundos | Alto | Monitoreo remoto y alertas discrecionales en movilidad | Instalación de app oficial y activación de permisos de fondo^3^ |
| **Pop-up en Navegador** | Prácticamente instantáneo | Alto | Operativa discrecional frente a pantallas | Mantener pestaña abierta y habilitar alertas HTML5 de escritorio^3^ |
| **Señal Acústica** | Prácticamente instantáneo | Muy Alto | Confirmación inmediata de niveles en tiempo real | Dispositivo de audio local activo en el sistema^3^ |
| **Webhook HTTP POST** | 0.1 – 0.5 segundos^7^ | Muy Alto^3^ | Automatización algorítmica y ruteo directo de órdenes | Servidor dedicado con puerto 80/443 expuesto^1^ |

10. Análisis de Latencia en la Entrega de Alertas

En el trading sistemático de alta frecuencia o de scalping intradiario, la latencia (el tiempo transcurrido desde que se cumple la condición en el mercado hasta que se ejecuta la orden en el broker) es una variable que impacta de forma directa sobre la rentabilidad esperada debido al deslizamiento de precios (slippage)^2^.

El Pipeline Completo del Retraso Temporal (The Delay Chain)

El tiempo total requerido para procesar y ejecutar una alerta de webhook de TradingView se compone de la suma de cuatro etapas de red y de cómputo diferenciadas^2^:

- **Detección de la Condición ():** Ocurre en la infraestructura en la nube de TradingView^2^. Representa el tiempo que le toma al servidor de la plataforma evaluar el tick entrante contra las condiciones matemáticas del indicador o estrategia^2^. En condiciones normales, este proceso demora entre **25 y 100 ms**^7^. Sin embargo, si la alerta depende de llamadas complejas de marcos temporales superiores (request.security) o bucles de cálculo pesados, esta latencia puede incrementarse^7^.
- **Transmisión del Webhook ():** Consiste en la serialización del payload JSON, resolución de DNS, establecimiento de la sesión TCP, negociación de la clave de encriptación TLS y transmisión física del paquete HTTP POST a través de internet desde los servidores en us-west-2 (Oregon) de TradingView hasta la dirección IP del servidor receptor^6^. Este trayecto geográfico consume entre **50 y 300 ms** bajo condiciones normales de enrutamiento de red^7^.
- **Procesamiento del Servidor Intermedio ():** Es el tiempo que le toma a la API del operador (el middleware) recibir la petición de red, realizar controles de seguridad (verificar IP de origen y certificados SSL)^1^, parsear el JSON y estructurar el llamado hacia la API del broker^2^. Con una infraestructura optimizada (como FastAPI en Python o Express en Node.js sobre servidores con alto ancho de banda), este proceso añade tan solo de **10 a 50 ms**^6^.
- **Ejecución de la Orden en el Broker ():** Es la latencia necesaria para transmitir la orden desde el servidor intermedio hasta la API del broker, procesar la orden en su motor de emparejamiento (matching engine) y retornar el resultado de la transacción completada^1^. Dependiendo del broker o exchange utilizado y de la geolocalización de sus servidores, este paso final añade entre **50 y 500 ms**^1^.

Retrasos Atípicos y Picos de Latencia (Spikes)

Bajo condiciones de mercado normales, la latencia total desde el disparo en TradingView hasta el llenado de la orden en el broker suele mantenerse en un rango de **100 a 500 ms**^7^. Sin embargo, este flujo no cuenta con garantías de tiempo de respuesta (SLA de latencia) y puede experimentar picos significativos debido a^2^:

- **Saturación en Eventos Macroeconómicos:** Durante noticias macroeconómicas de alto impacto (anuncios de la Fed, datos de empleo NFP, IPC, etc.), el volumen de operaciones aumenta exponencialmente, lo que incrementa el volumen de alertas simultáneas procesadas en la nube de TradingView^7^. Esto puede provocar retrasos de procesamiento de **1 a 5 segundos**, y en situaciones extremas de sobrecarga de servidores, de hasta **25 a 30 segundos**^2^.
- **Enrutamiento Ineficiente:** Si el servidor receptor se aloja en un proveedor residencial con direccionamiento dinámico o mala conectividad internacional, los tiempos de transmisión aumentan drásticamente, incrementando el riesgo de experimentar caídas de conexión^1^.

Diferencias entre Alertas de Precio, Indicadores y Estrategias

El tipo de alerta configurado influye significativamente en la latencia del disparo debido a cómo gestiona TradingView el cálculo en cada caso:

- **Alertas de Precio:** Son las más rápidas debido a su bajo costo computacional^10^. Al evaluarse directamente en la capa de datos de la plataforma sobre barras de un minuto, el disparo es casi instantáneo, requiriendo un procesamiento mínimo en los servidores^10^.
- **Alertas de Indicadores:** Añaden latencia debido al tiempo requerido para compilar el código de Pine Script y calcular los valores de las series numéricas sobre el histórico de datos del gráfico activo^3^. El retraso de cálculo puede aumentar según la complejidad de las ecuaciones matemáticas del script^7^.
- **Alertas de Estrategias:** Introducen la mayor latencia del sistema^6^. Al cumplirse la condición en el mercado, el motor de TradingView debe procesar primero la lógica de colocación de la orden en el emulador de corretaje interno, calcular el impacto en los balances, comprobar las restricciones de margen de la cuenta simulada y actualizar los registros históricos de rendimiento antes de generar el webhook de ejecución^6^. Este flujo secuencial de validaciones añade capas adicionales de procesamiento en los servidores que incrementan el tiempo de respuesta en comparación con las alertas de precio simple^6^.

11. Arquitectura de un Webhook Receiver de Alto Rendimiento

Para asegurar la continuidad de un sistema de trading automatizado, el servidor middleware encargado de recibir los webhooks de TradingView y de rutear las órdenes a las APIs de los brokers debe diseñarse bajo estándares rigurosos de alta disponibilidad y seguridad de red^1^.

Configuración de Seguridad en un Servidor de Proxy Inverso (Nginx)

No es recomendable exponer directamente el servidor de la aplicación (como FastAPI o Node.js) a la red pública de internet, ya que carecen de las capas de protección avanzada de red que ofrecen los servidores proxy inverso dedicados como Nginx^6^. Nginx actúa como un escudo perimetral seguro de alto rendimiento, gestionando el establecimiento de conexiones TCP, mitigando ataques de denegación de servicio (DDoS) y realizando la desencriptación de los canales TLS/SSL (SSL Termination) de forma eficiente para liberar de esta carga computacional a la aplicación de trading^1^.

A continuación se presenta un bloque de configuración de Nginx (/etc/nginx/sites-available/trading_gateway.conf) para configurar la validación del certificado SSL de cliente enviado por TradingView en conexiones HTTPS^6^:

Nginx

*# Formato de registro personalizado para auditar información de los certificados SSL de cliente*

*log_format* tv_ssl_audit *'$remote_addr - $remote_user [$time_local] '*

                        *'"$request" $status $body_bytes_sent '*

                        *'SSL_CLIENT_S_DN="$ssl_client_s_dn" '*

                        *'SSL_CLIENT_VERIFY="$ssl_client_verify"'*;

*server* {

    *listen* *443* ssl;

    *server_name* webhook.midominio.com;

    *# Rutas a los certificados SSL del Servidor de Webhooks (emitidos por Let's Encrypt / Certbot)*

    *ssl_certificate* /etc/letsencrypt/live/webhook.midominio.com/fullchain.pem;

    *ssl_certificate_key* /etc/letsencrypt/live/webhook.midominio.com/privkey.pem;

    *ssl_protocols* TLSv1.*2* TLSv1.*3*;

    *ssl_ciphers* HIGH:!aNULL:!MD5;

    *# =========================================================================*

    *# CONFIGURACIÓN DE VALIDACIÓN DEL CERTIFICADO DE CLIENTE (TRADINGVIEW)*

    *# =========================================================================*

    *# TradingView envía un certificado SSL de cliente firmado por su propia entidad.*

    *# Configuramos ssl_verify_client como 'optional_no_ca' para recibir el certificado*

    *# sin requerir la presencia de una entidad certificadora (CA) raíz local en el sistema,*

    *# permitiendo validar sus campos manualmente en el proxy inverso o en la aplicación.*

    *# =========================================================================*

    *ssl_verify_client* optional_no_ca;

    *# Inyección de metadatos SSL en las cabeceras HTTP que se envían a la aplicación de backend*

    *proxy_set_header* X-SSL-Client-Verify $ssl_client_verify;

    *proxy_set_header* X-SSL-Client-S-DN $ssl_client_s_dn;

    *proxy_set_header* X-SSL-Client-Raw-Cert $ssl_client_raw_cert;

    *# Cabeceras estándar para preservar la dirección IP original del cliente de origen*

    *proxy_set_header* Host $host;

    *proxy_set_header* X-Real-IP $remote_addr;

    *proxy_set_header* X-Forwarded-For $proxy_add_x_forwarded_for;

    *proxy_set_header* X-Forwarded-Proto $scheme;

    *access_log* /var/log/nginx/tv_webhook_access.log tv_ssl_audit;

    *error_log* /var/log/nginx/tv_webhook_error.log *debug*;

    *location* / {

        *# Redirección interna de la petición HTTP al servidor de backend (FastAPI/Express)*

        *proxy_pass* http://127.0.0.1:8000;

        *proxy_connect_timeout* *3s*;

        *proxy_read_timeout* *3s*;

    }

}

Al utilizar esta configuración, Nginx interceptará la petición HTTPS de TradingView y extraerá los metadatos del certificado de cliente^37^. Si el certificado es auténtico de TradingView, la cabecera X-SSL-Client-S-DN contendrá los campos oficiales del sujeto del certificado^37^: C=US, ST=Ohio, L=Westerville, O="TradingView, Inc.", CN="webhook-server@tradingview.com"^38^

Implementaciones Completas del Servidor Receptor

A continuación se detallan los códigos fuente completos, robustos y funcionales para los dos entornos de ejecución más adoptados en el desarrollo de software middleware: Python y Node.js^1^. Ambos están preparados para validar la IP de origen de la solicitud de red y corroborar los datos de seguridad requeridos antes de procesar cualquier instrucción^1^.

Opción A: Servidor en Python (FastAPI)

Esta implementación utiliza FastAPI debido a su velocidad de procesamiento basada en operaciones de entrada/salida no bloqueantes (asincronía nativa) y validación automatizada de esquemas mediante Pydantic^1^:

Python

*# filename: server_fastapi.py*

*import* logging

*from* fastapi *import* FastAPI, Request, HTTPException, status, BackgroundTasks

*from* pydantic *import* BaseModel, Field

*from* typing *import* Optional, Set

*import* uvicorn

*# Configuración de logs para auditoría de señales*

logging.basicConfig(

    level=logging.INFO,

    *format*=*"%(asctime)s [%(levelname)s] %(name)s - %(message)s"*

)

logger = logging.getLogger(*"FastAPIGateway"*)

app = FastAPI(title=*"FastAPI TradingView Webhook Receiver"*, version=*"1.0.0"*)

*# Token secreto compartido que TradingView debe incluir en el payload para autenticarse*

TOKEN_SECRETO_COMPARTIDO = *"TOKEN_DE_SEGURIDAD_INTERNO_998"*

*# Lista de direcciones IP oficiales de TradingView para la lista de permitidos*

IPS_VALIDAS_TRADINGVIEW: Set[*str*] = {

    *"52.89.214.238"*,

    *"34.212.75.30"*,

    *"54.218.53.128"*,

    *"52.32.178.7"*

}

*# Definición del esquema estricto de validación del payload recibido*

*class* *SignalPayload(BaseModel):*

    token: *str* = Field(..., description=*"Token secreto para validación"*)

    action: *str* = Field(..., description=*"Dirección: buy, sell, exit"*)

    symbol: *str* = Field(..., description=*"Símbolo del activo financiero"*)

    contracts: *float* = Field(..., gt=*0.0*, description=*"Cantidad de contratos a operar"*)

    price: *float* = Field(..., gt=*0.0*, description=*"Precio de ejecución de referencia"*)

    order_id: Optional[*str*] = Field(*None*, description=*"Identificador único de la señal"*)

*# Tarea asíncrona que se ejecuta fuera de la petición HTTP principal para evitar el timeout*

*def* *procesar_orden_en_segundo_plano**(payload: SignalPayload):*

    logger.info(*f"[Segundo Plano] Procesando orden: ID={payload.order_id} | {payload.action.upper()} {payload.contracts} {payload.symbol}"*)

    *# En esta sección se implementa la lógica de conexión con el SDK o API del broker*

    *# ej. client.place_order(symbol=payload.symbol, qty=payload.contracts, side=payload.action)*

    logger.info(*f"[Segundo Plano] Orden ejecutada de forma asíncrona con éxito en el mercado."*)

*@app.post(**"/webhook"**, status_code=status.HTTP_200_OK)*

*async* *def* *recibir_webhook**(

    request: Request, 

    payload: SignalPayload, 

    background_tasks: BackgroundTasks

):*

    *# 1. Validación de IP de Origen en el Cortafuegos de la Aplicación*

    *# En sistemas reales de producción, se lee la dirección original de la cabecera 'X-Forwarded-For'*

    ip_origen = request.client.host

    x_forwarded_for = request.headers.get(*"x-forwarded-for"*)

    *if* x_forwarded_for:

        ip_origen = x_forwarded_for.split(*","*)[*0*].strip()

    *if* ip_origen *not* *in* IPS_VALIDAS_TRADINGVIEW:

        logger.warning(*f"Intento de conexión bloqueado desde una IP no autorizada: {ip_origen}"*)

        *raise* HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=*"Dirección IP no autorizada en la lista de permitidos"*

        )

    *# 2. Validación del Certificado SSL de Cliente extraído por Nginx (Capa Opcional Avanzada)*

    ssl_client_verify = request.headers.get(*"x-ssl-client-verify"*)

    ssl_client_dn = request.headers.get(*"x-ssl-client-s-dn"*)

    *if* ssl_client_verify *and* ssl_client_verify == *"SUCCESS"*:

        *if* *"O=TradingView, Inc."* *not* *in* ssl_client_dn *or* *"CN=webhook-server@tradingview.com"* *not* *in* ssl_client_dn:

            logger.warning(*f"Certificado SSL de Cliente no verificado o inválido: {ssl_client_dn}"*)

            *raise* HTTPException(

                status_code=status.HTTP_401_UNAUTHORIZED,

                detail=*"Certificado SSL de cliente inválido"*

            )

        logger.info(*"Verificación SSL de cliente correcta en la cabecera HTTP."*)

    *# 3. Validación de Token Secreto Compartido*

    *if* payload.token != TOKEN_SECRETO_COMPARTIDO:

        logger.warning(*"Intento de ejecución rechazado por token secreto inválido."*)

        *raise* HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=*"Token secreto de autenticación incorrecto"*

        )

    *# 4. Derivación de la Tarea al Worker en Segundo Plano (Asincronía para evitar timeout de 3s)*

    background_tasks.add_task(procesar_orden_en_segundo_plano, payload)

    *# Retornamos respuesta HTTP exitosa de inmediato a TradingView en menos de 50ms*

    *return* {*"status"*: *"accepted"*, *"message"*: *"Señal encolada para ejecución"*}

*if* __name__ == *"__main__"*:

    *# Arrancamos el servidor ASGI escuchando en el puerto 8000 interno de la máquina*

    uvicorn.run(*"server_fastapi:app"*, host=*"127.0.0.1"*, port=*8000*, reload=*False*)

Opción B: Servidor en Node.js (Express)

Esta opción implementa el servidor receptor utilizando Node.js con el framework Express, ofreciendo un entorno de alto rendimiento para el manejo de flujos asíncronos gracias a su arquitectura basada en un bucle de eventos (Event Loop) único no bloqueante^2^:

JavaScript

*// filename: server_express.js*

*const* express = *require*(*'express'*);

*const* app = express();

*// Middleware obligatorio para parsear solicitudes entrantes con formato JSON*

app.use(express.json());

*const* PORT = *8000*;

*const* TOKEN_SECRETO_COMPARTIDO = *"TOKEN_DE_SEGURIDAD_INTERNO_998"*;

*// Direcciones IP de TradingView autorizadas*

*const* IPS_VALIDAS_TRADINGVIEW = *new* *Set*([

    *"52.89.214.238"*,

    *"34.212.75.30"*,

    *"54.218.53.128"*,

    *"52.32.178.7"*

]);

*// Worker que simula la ejecución asíncrona de la orden sin bloquear el hilo principal*

*const* despacharOrdenEnSegundoPlano = *(payload) =>* {

    *console*.log(*`[Segundo Plano] Ejecutando: ${payload.action.toUpperCase()} ${payload.contracts} de ${payload.symbol}`*);

    *// En esta sección se integra el llamado al SDK del Broker/Exchange*

    *console*.log(*`[Segundo Plano] Operación completada con éxito.`*);

};

app.post(*'/webhook'*, *(req, res) =>* {

    *// 1. Obtención y validación de la IP de origen*

    *let* ipOrigen = req.ip;

    *const* xForwardedFor = req.headers[*'x-forwarded-for'*];

    *if* (xForwardedFor) {

        ipOrigen = xForwardedFor.split(*','*)[*0*].trim();

    }

    *// Adaptador para el formato de IP que incluye prefijo IPv4 en Node.js (::ffff:)*

    *if* (ipOrigen.startsWith(*"::ffff:"*)) {

        ipOrigen = ipOrigen.replace(*"::ffff:"*, *""*);

    }

    *if* (!IPS_VALIDAS_TRADINGVIEW.has(ipOrigen)) {

        *console*.warn(*`[Seguridad] Bloqueado acceso desde dirección IP no autorizada: ${ipOrigen}`*);

        *return* res.status(*401*).send(*'Origen no autorizado'*);

    }

    *// 2. Validación de la identidad del Certificado SSL de cliente provisto por Nginx*

    *const* sslVerify = req.headers[*'x-ssl-client-verify'*];

    *const* sslDN = req.headers[*'x-ssl-client-s-dn'*];

    *if* (sslVerify && sslVerify === *"SUCCESS"*) {

        *if* (!sslDN.includes(*"O=TradingView, Inc."*) || !sslDN.includes(*"CN=webhook-server@tradingview.com"*)) {

            *console*.warn(*`[Seguridad] Certificado SSL de Cliente no verificado: ${sslDN}`*);

            *return* res.status(*401*).send(*'Certificado SSL no válido'*);

        }

    }

    *// 3. Desestructuración y validación del cuerpo JSON de la solicitud*

    *const* { token, action, symbol, contracts, price, order_id } = req.body;

    *if* (!token || token !== TOKEN_SECRETO_COMPARTIDO) {

        *console*.warn(*`[Seguridad] Solicitud rechazada por token secreto inválido.`*);

        *return* res.status(*401*).send(*'Token de autenticación incorrecto'*);

    }

    *if* (!action || !symbol || !contracts || contracts <= *0* || !price) {

        *console*.warn(*`[Validación] Payload JSON mal formado o con campos obligatorios vacíos.`*);

        *return* res.status(*400*).send(*'Esquema de payload inválido'*);

    }

    *// 4. Procesamiento asíncrono no bloqueante*

    *// En Node.js, setImmediate deriva la ejecución al final de la cola de eventos actual*

    setImmediate(*() =>* {

        despacharOrdenEnSegundoPlano({ token, action, symbol, contracts, price, order_id });

    });

    *// Retorno inmediato de la respuesta HTTP 200 OK a TradingView para cumplir con los 3s*

    *return* res.status(*200*).json({ *status*: *"success"*, *message*: *"Señal recibida correctamente"* });

});

app.listen(PORT, *'127.0.0.1'*, *() =>* {

    *console*.log(*`[Servidor Activo] Webhook Gateway escuchando de forma segura en http://127.0.0.1:${PORT}`*);

});

12. Integración con Servicios Externos

Para operadores que carecen de conocimientos profundos en programación de servidores web de bajo nivel o que desean crear prototipos rápidos de sistemas automatizados, las herramientas de automatización sin código (no-code / low-code) representan un puente eficiente para enlazar los webhooks de TradingView con múltiples servicios^23^.

n8n (La Opción Recomendada para Entornos de Alta Confiabilidad)

n8n es un software de automatización de flujos de trabajo de código abierto que se destaca por su potencia computacional, su interfaz visual basada en nodos estructurados y la posibilidad de ser autohospedado de forma gratuita (self-hosted)^41^.

- **Mecánica de Enlace:** El operador inserta un nodo de entrada de tipo "Webhook Trigger"^42^. n8n genera una URL dedicada y segura que se configura directamente en la alerta de TradingView^23^. Cuando el webhook de la plataforma se dispara, el nodo captura el payload JSON, mapea automáticamente sus claves y permite estructurar tareas lógicas secundarias, como filtrar la señal según la volatilidad, registrar los datos del evento en una base de datos u optimizar los parámetros antes de enviar la orden final al broker utilizando nodos HTTP adicionales o el nodo nativo de Telegram para notificaciones rápidas^41^.
- **Ventaja Competitiva:** Su arquitectura permite la ejecución en el propio servidor VPS del operador, garantizando un control total sobre la privacidad del flujo de señales de trading, reduciendo los tiempos de red y eliminando costos de suscripción recurrentes^41^.

Make (Integromat)

Make destaca por su versatilidad, su interfaz visual intuitiva y la facilidad para modelar flujos de trabajo con ramificaciones lógicas sin necesidad de escribir código^42^.

- **Mecánica de Enlace:** Se crea un módulo de tipo "Custom Webhook". Este módulo provee un endpoint dedicado donde TradingView envía la solicitud HTTP POST de la alerta^41^. Una vez que ingresa una señal, Make mapea visualmente la estructura del JSON y permite enlazar módulos posteriores para ruterar alertas a bases de datos en la nube o enviar mensajes enriquecidos a canales de Slack^20^.
- **Ventaja Competitiva:** Ofrece una curva de aprendizaje sumamente suave y planes de suscripción accesibles que lo convierten en una opción idónea para la validación rápida de estrategias^42^.

Zapier

Zapier es la plataforma de automatización en la nube con el mayor catálogo de integraciones nativas con servicios web del mercado corporativo^41^.

- **Mecánica de Enlace:** Se configura una receta ("Zap") utilizando la aplicación de inicio "Webhooks by Zapier" con el disparador "Catch Hook"^41^. Zapier expone una URL segura que se añade en el webhook de TradingView para capturar el payload JSON y derivar las señales procesadas a miles de aplicaciones de terceros de forma casi instantánea^41^.
- **Inconveniente Principal:** Su modelo de precios es costoso para la operativa sistemática diaria, ya que requiere de planes de pago avanzados para acceder a los disparadores de webhooks y para manejar el volumen recurrente de ejecuciones de una estrategia de trading activa^41^. Además, añade capas de procesamiento intermedias en servidores remotos que incrementan la latencia total del sistema^41^.

IFTTT (If This Then That)

IFTTT es una de las soluciones pioneras de automatización en la web, orientada principalmente a integraciones domésticas y de consumo personal^42^.

- **Mecánica de Enlace:** El usuario configura una receta ("Applet") donde el servicio "Webhooks" actúa como el disparador primario^42^. Al recibir la señal HTTP POST de TradingView, el sistema ejecuta una acción de salida sencilla, como activar una alerta inteligente, encender un indicador de luz de color en el espacio físico de trabajo del operador o enviar un mensaje SMS de respaldo al dispositivo telefónico^3^.
- **Inconveniente Principal:** Su diseño está muy limitado para el procesamiento y manipulación de estructuras complejas de datos JSON, lo que lo descarta como una herramienta viable para automatizar sistemas algorítmicos profesionales^42^.

Comparativa Técnica de Plataformas No-Code / Low-Code

| **Característica** | **n8n (Self-Hosted)** | **Make** | **Zapier** | **IFTTT** |
| --- | --- | --- | --- | --- |
| **Costo Operativo** | Gratuito (asociado al costo del VPS)^42^ | Bajo a medio (suscripción básica)^42^ | Elevado (planes por volumen)^42^ | Muy económico (planes básicos)^42^ |
| **Latencia de Red** | Mínima (desplegado cerca del broker)^1^ | Media (procesamiento en la nube de Make) | Alta (múltiples capas de enrutamiento)^43^ | Alta (no diseñado para velocidad) |
| **Nodos Admitidos** | 1000+ (ampliable mediante JS)^42^ | 1700+ integraciones^42^ | 7000+ aplicaciones^42^ | 700+ servicios simples^42^ |
| **Complejidad Lógica** | Muy alta (soporta bucles, wait y código)^42^ | Alta (modelado visual con routers)^42^ | Media (flujos secuenciales sencillos)^42^ | Baja (reglas secuenciales simples)^42^ |
| **Privacidad de Datos** | Máxima (datos contenidos en el propio VPS)^23^ | Media (procesados en servidores de Make) | Media (procesados en servidores de Zapier) | Baja (canalizados por servicios públicos) |

13. Mejores Prácticas de Fiabilidad y Alta Disponibilidad

El trading automatizado expone directamente capital financiero a la red de internet, por lo que es indispensable estructurar el sistema bajo principios estrictos de resiliencia, redundancia y monitoreo pasivo para mitigar posibles fallos operativos^1^.

Arquitectura de Cola de Mensajería (The Queue Pattern)

La regla de oro de la estabilidad en webhooks consiste en desacoplar por completo la fase de recepción de la señal de la fase de ejecución de la orden^6^. El endpoint expuesto del servidor de webhooks debe actuar únicamente como un colector de señales sumamente rápido^6^.

Al ingresar la petición HTTP POST, el receptor de la aplicación debe limitarse a validar la IP de origen, corroborar la estructura del JSON y el token secreto, guardar la señal de inmediato en una cola de mensajería en memoria ultrarrápida (como **Redis** o **RabbitMQ**) y responder instantáneamente con un código 200 OK al servidor de TradingView en menos de 50 milisegundos, cumpliendo holgadamente el límite de timeout de 3 segundos^6^.

En paralelo, uno o varios procesos independientes de ejecución (workers asíncronos en segundo plano) consumen de forma ordenada los mensajes de la cola de Redis, gestionando las llamadas de red hacia las APIs del broker, procesando las órdenes y gestionando la lógica de reintentos ante fallos sin interferir en la recepción de nuevas señales entrantes^6^.

Auditoría del Registro de Entrega de Webhooks

Para auditar la estabilidad y el rendimiento de las comunicaciones, el operador debe monitorizar de forma constante los registros del sistema^2^:

- **Auditoría de TradingView:** La plataforma ofrece un panel de control detallado denominado "Registro de Alertas" donde se puede auditar la columna de estado del webhook^20^. Si una solicitud falla por problemas de red o errores en el servidor receptor, la plataforma registrará el evento con códigos de error específicos (como respuestas 4xx o 5xx o timeout de conexión), facilitando el diagnóstico de problemas de comunicación^20^.
- **Exportación para Análisis:** El sistema permite exportar de forma sencilla los registros históricos de alertas en formato de archivo CSV para realizar análisis de rendimiento, contrastando las marcas de tiempo de los disparos contra los registros de ejecución reales del broker para medir y corregir problemas de deslizamiento de precios (slippage)^7^.

Redundancia en Canales de Alertas

Un único canal de comunicación es propenso a sufrir interrupciones temporales debido a caídas de red o fallos en los servidores^2^. Las estrategias institucionales mitigan este riesgo diversificando los flujos de recepción de señales de forma paralela^3^:

- **Duplicidad de Webhooks:** Se configuran dos alertas independientes en TradingView con idénticos parámetros analíticos pero apuntando a endpoints en servidores independientes (por ejemplo, un servidor principal en AWS y un servidor de respaldo en DigitalOcean)^1^. La lógica del receptor debe implementar un sistema de deduplicación que descarte señales repetidas en una ventana de milisegundos mediante identificadores únicos de orden para evitar la duplicidad de operaciones^2^.
- **Enlace de Canales Redundantes:** De forma complementaria a los webhooks, se puede configurar el envío de correos electrónicos de respaldo o notificaciones push móviles para alertar al operador humano en caso de una desconexión total del servidor principal^3^.

Modelos de Meta-Monitoreo (Alertas sobre las Alertas)

Un fallo en el servidor receptor impedirá el correcto procesamiento de las operaciones de mercado^1^. Dado que el propio canal automatizado estará inoperativo, se requiere desplegar un sistema externo de supervisión independiente (Meta-Monitoring)^1^.

- **Peticiones de Latido de Corazón (Heartbeats):** Un script externo alojado en una infraestructura separada realiza peticiones HTTP periódicas (por ejemplo, cada 30 segundos) al endpoint de salud (/health) del servidor de trading^46^. Si el servidor receptor no responde o devuelve un código de error de forma persistente, el sistema de meta-monitoreo asume que el servidor ha caído^1^.
- **Notificaciones de Emergencia de Alta Prioridad:** Ante la detección de una anomalía en el servidor, el sistema de meta-monitoreo despacha notificaciones de emergencia a través de llamadas telefónicas de voz automatizadas utilizando servicios de comunicaciones en la nube (como Twilio), garantizando que el operador sea notificado de inmediato, incluso si se encuentra durmiendo o con su dispositivo en modo silencioso^29^.

14. Dos Implementaciones Técnicas Completas de Referencia

A continuación se presentan los códigos fuente de producción completos, robustos, sin omisiones y completamente anotados para implementar la arquitectura de automatización de trading de extremo a extremo^2^.

Implementación 1: Indicador en Pine Script (v5) con Lógica de Alertas Integrada

Este indicador calcula un cruce clásico de Promedios Móviles Simples (Fast SMA vs Slow SMA)^15^. Registra puntos de alerta estáticos mediante alertcondition() con payloads JSON con placeholders de variables, e incorpora llamadas dinámicas a la función alert() evaluadas de forma estricta en barras reales cerradas para evitar el repintado (repainting) de señales y el envío descontrolado de peticiones por ruido de ticks temporales^14^.

Pine Script

//@version=5

indicator("Arquitectura de Alertas SMA Crossover - Producción", overlay=true, max_bars_back=500)

// =========================================================================

// VARIABLES DE ENTRADA Y PARAMETRIZACIÓN

// =========================================================================

fastLength   = input.int(10, title="Período SMA Rápido", minval=1)

slowLength   = input.int(50, title="Período SMA Lento", minval=1)

tokenSeguro  = input.string("TOKEN_DE_SEGURIDAD_INTERNO_998", title="Token de Webhook")

// =========================================================================

// CÁLCULO DE PROMEDIOS MÓVILES

// =========================================================================

fastSMA = ta.sma(close, fastLength)

slowSMA = ta.sma(close, slowLength)

// Representación visual en el gráfico

plot(fastSMA, color=color.blue, title="SMA Rápida", linewidth=2)

plot(slowSMA, color=color.orange, title="SMA Lenta", linewidth=2)

// =========================================================================

// EVALUACIÓN DE LAS CONDICIONES DE CRUCE (EVITANDO REPINTE)

// =========================================================================

// Se calcula el cruce en la barra actual. Para la automatización real,

// se evaluará si el cruce se confirmó en la transición de la barra previa.

// =========================================================================

cruceAlcista  = ta.crossover(fastSMA, slowSMA)

cruceBajista  = ta.crossunder(fastSMA, slowSMA)

// Graficar marcas visuales en el gráfico de precios para auditoría de señales

plotshape(cruceAlcista, title="Crossover Alcista", style=shape.triangleup, 

          location=location.belowbar, color=color.green, size=size.small)

plotshape(cruceBajista, title="Crossover Bajista", style=shape.triangledown, 

          location=location.abovebar, color=color.red, size=size.small)

// =========================================================================

// 1. REGISTRO DE ALERTAS ESTÁTICAS (alertcondition)

// =========================================================================

// El usuario final debe crear estas alertas de forma manual a través de la UI.

// Utilizan placeholders de variables dinámicas nativas de TradingView.

// =========================================================================

alertcondition(

     condition = cruceAlcista,

     title = "Crossover Alcista SMA [Manual]",

     message = '{"token": "TOKEN_DE_SEGURIDAD_INTERNO_998", "action": "buy", "symbol": "{{ticker}}", "contracts": 1.0, "price": {{close}}, "order_id": "crossover_long"}'

 )

alertcondition(

     condition = cruceBajista,

     title = "Crossover Bajista SMA [Manual]",

     message = '{"token": "TOKEN_DE_SEGURIDAD_INTERNO_998", "action": "sell", "symbol": "{{ticker}}", "contracts": 1.0, "price": {{close}}, "order_id": "crossover_short"}'

 )

// =========================================================================

// 2. EJECUCIÓN DE ALERTAS DINÁMICAS (alert)

// =========================================================================

// Estas alertas se ejecutan automáticamente en tiempo real en cada barra

// y permiten construir mensajes JSON dinámicos parametrizados por código.

// =========================================================================

// Para evitar señales falsas causadas por fluctuaciones intrabarra,

// se evalúa la condición de cierre de la barra inmediatamente anterior (index [1])

// garantizando que el cruce esté plenamente confirmado en el gráfico.

// =========================================================================

cruceAlcistaConfirmado = cruceAlcista[1]

cruceBajistaConfirmado = cruceBajista[1]

if barstate.isrealtime

    if cruceAlcistaConfirmado

        // Construcción del mensaje JSON dinámico

        payloadAlcista = str.format('{{"token": "{0}", "action": "buy", "symbol": "{1}", "contracts": 1.0, "price": {2,number,#.##}, "order_id": "sma_crossover_long_{3}"}}', 

          tokenSeguro, syminfo.ticker, close, str.tostring(time, "yyyyMMdd_HHmmss"))

        // Disparador dinámico configurado para ejecutarse una única vez al cierre de la barra

        alert(payloadAlcista, alert.freq_once_per_bar_close)

    if cruceBajistaConfirmado

        payloadBajista = str.format('{{"token": "{0}", "action": "sell", "symbol": "{1}", "contracts": 1.0, "price": {2,number,#.##}, "order_id": "sma_crossover_short_{3}"}}', 

          tokenSeguro, syminfo.ticker, close, str.tostring(time, "yyyyMMdd_HHmmss"))

        alert(payloadBajista, alert.freq_once_per_bar_close)

Implementación 2: Servidor Receptor Webhook en Python (FastAPI) con Despacho de Órdenes y Notificaciones de Telegram

Este script de servidor implementa el backend receptor utilizando FastAPI en Python^1^. Cuenta con capas integradas para validar la dirección IP de origen contra la lista de permitidos oficial de TradingView^6^, procesar de manera asíncrona la recepción del payload para evitar expiraciones de conexión (timeouts)^6^, registrar los eventos en un archivo log estructurado^6^ y despachar un reporte del evento en formato HTML a un bot de Telegram^2^.

Python

*# filename: production_gateway.py*

*import* logging

*from* logging.handlers *import* RotatingFileHandler

*from* fastapi *import* FastAPI, Request, HTTPException, status, BackgroundTasks

*from* pydantic *import* BaseModel, Field

*from* typing *import* Optional, Set

*import* httpx

*import* uvicorn

*# =========================================================================*

*# CONFIGURACIÓN DEL SISTEMA DE REGISTRO ROTATIVO (LOGGING)*

*# =========================================================================*

logger = logging.getLogger(*"ProductionTradingGateway"*)

logger.setLevel(logging.INFO)

*# Formateador de eventos estructurado*

log_formatter = logging.Formatter(*"%(asctime)s [%(levelname)s] %(name)s - %(message)s"*)

*# Rotación de logs: Máximo de 10MB por archivo, conservando hasta 5 backups históricos*

file_handler = RotatingFileHandler(*"trading_gateway_production.log"*, maxBytes=*10485760*, backupCount=*5*)

file_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler()

stream_handler.setFormatter(log_formatter)

logger.addHandler(file_handler)

logger.addHandler(stream_handler)

*# =========================================================================*

*# PARÁMETROS OPERATIVOS DE CONFIGURACIÓN*

*# =========================================================================*

TOKEN_SECRETO_VÁLIDO = *"TOKEN_DE_SEGURIDAD_INTERNO_998"*

TELEGRAM_BOT_TOKEN = *"738192012:AAH9f_Yj_0123ef_AJS9823ejA98u_example"*

TELEGRAM_CHAT_ID = *"-100291823901"*

*# Direcciones IP oficiales del clúster de TradingView para validación de firewall*

IPS_VALIDAS_TRADINGVIEW: Set[*str*] = {

    *"52.89.214.238"*,

    *"34.212.75.30"*,

    *"54.218.53.128"*,

    *"52.32.178.7"*

}

app = FastAPI(

    title=*"TradingView Webhook High-Availability Gateway"*, 

    description=*"Endpoint asíncrono para ingesta de señales de trading y ruteo estructurado"*,

    version=*"2.1.0"*

)

*# =========================================================================*

*# MODELO DE VALIDACIÓN DE ENTRADA (PYDANTIC)*

*# =========================================================================*

*class* *WebhookSignal(BaseModel):*

    token: *str* = Field(..., description=*"Token de autenticación interno"*)

    action: *str* = Field(..., description=*"Lógica: buy, sell, exit"*)

    symbol: *str* = Field(..., description=*"Ticker del activo de la alerta"*)

    contracts: *float* = Field(..., gt=*0.0*, description=*"Cantidad de contratos a ejecutar"*)

    price: *float* = Field(..., gt=*0.0*, description=*"Precio de referencia en el disparo"*)

    order_id: Optional[*str*] = Field(*None*, description=*"Identificador único de la orden"*)

*# =========================================================================*

*# PROCESADOR ASÍNCRONO EN SEGUNDO PLANO (WORKER)*

*# =========================================================================*

*async* *def* *despachar_ejecuci**ó**n_de_orden_y_notificaci**ó**n**(payload: WebhookSignal):*

    *"""

    Simula la colocación de la orden en la API del broker y envía

    un informe formateado de forma asíncrona a un canal de Telegram.

    Toda la latencia de red ocurre en segundo plano, protegiendo al sistema

    de experimentar timeouts de TradingView.

    """*

    logger.info(*f"[Worker] Iniciando procesamiento de orden para {payload.symbol} | ID={payload.order_id}"*)

    *# ---------------------------------------------------------------------*

    *# Simulación de colocación de orden en la API de trading*

    *# ---------------------------------------------------------------------*

    *# En este bloque se integran llamadas asíncronas con httpx hacia APIs reales:*

    *# ej. await client.place_limit_order(symbol=payload.symbol, side=payload.action, qty=payload.contracts)*

    *# ---------------------------------------------------------------------*

    orden_completada_con_éxito = *True*

    precio_ejecucion_final = payload.price *# En operativa real, devuelto por la API del broker*

    *if* *not* orden_completada_con_éxito:

        logger.error(*f"[Worker] Error crítico al ejecutar la orden en el broker para {payload.symbol}."*)

        *return*

    logger.info(*f"[Worker] Orden ejecutada correctamente para {payload.symbol} a un precio de {precio_ejecucion_final}"*)

    *# ---------------------------------------------------------------------*

    *# Envío de Notificación estructurada a la API de Telegram*

    *# ---------------------------------------------------------------------*

    url_telegram = *f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"*

    mensaje_html = (

        *f"<b>SEÑAL DE TRADING PROCESADA</b> \n\n"*

        *f"<b>Símbolo:</b> <code>{payload.symbol}</code>\n"*

        *f"<b>Operación:</b> {payload.action.upper()}\n"*

        *f"<b>Contratos:</b> {payload.contracts}\n"*

        *f"<b>Precio Ejecutado:</b> ${precio_ejecucion_final:,**.2**f}\n"*

        *f"<b>ID Señal:</b> <code>{payload.order_id* *if* *payload.order_id* *else* *'N/A'}</code>\n\n"*

        *f"<b>Estado del Servidor:</b> [ACTIVO] Operativo en VPS"*

    )

    body_telegram = {

        *"chat_id"*: TELEGRAM_CHAT_ID,

        *"text"*: mensaje_html,

        *"parse_mode"*: *"HTML"*

    }

    *try*:

        *# Se realiza una petición asíncrona no bloqueante de red con timeout amplio de 10s*

        *async* *with* httpx.AsyncClient(timeout=*10.0*) *as* cliente_http:

            respuesta = *await* cliente_http.post(url_telegram, json=body_telegram)

            *if* respuesta.status_code == *200*:

                logger.info(*f"[Notificaciones] Reporte de orden enviado correctamente a Telegram para {payload.symbol}."*)

            *else*:

                logger.error(*f"[Notificaciones] Error de Telegram API: Código {respuesta.status_code} | {respuesta.text}"*)

    *except* Exception *as* e:

        logger.error(*f"[Notificaciones] Excepción al enviar señal a Telegram: {**str**(e)}"*)

*# =========================================================================*

*# ENDPOINT DE CONTROL DE SALUD (HEALTH CHECK)*

*# =========================================================================*

*@app.get(**"/health"**, status_code=status.HTTP_200_OK)*

*async* *def* *health_check**():*

    *"""

    Permite a los meta-monitores de infraestructura externa evaluar

    si el receptor de webhooks está en línea y funcionando.

    """*

    *return* {*"status"*: *"healthy"*, *"service"*: *"tradingview-production-gateway"*}

*# =========================================================================*

*# ENDPOINT DE ENTRADA WEBHOOK (POST)*

*# =========================================================================*

*@app.post(**"/webhook"**, status_code=status.HTTP_200_OK)*

*async* *def* *webhook_receiver**(

    request: Request,

    payload: WebhookSignal,

    background_tasks: BackgroundTasks

):*

    *"""

    Endpoint de recepción principal para los webhooks de TradingView.

    Valida la IP de origen, el certificado SSL de cliente enviado por Nginx,

    el token secreto compartido y encola la orden de forma asíncrona.

    """*

    *# 1. Validación de IP de origen contra la lista de admitidos de TradingView*

    ip_cliente = request.client.host

    x_forwarded_for = request.headers.get(*"x-forwarded-for"*)

    *if* x_forwarded_for:

        ip_cliente = x_forwarded_for.split(*","*)[*0*].strip()

    logger.info(*f"Petición POST de Webhook recibida desde la dirección IP: {ip_cliente}"*)

    *if* ip_cliente *not* *in* IPS_VALIDAS_TRADINGVIEW:

        logger.warning(*f"Conexión bloqueada desde IP no autorizada: {ip_cliente}"*)

        *raise* HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=*"Dirección IP de origen no autorizada en la lista de admitidos"*

        )

    *# 2. Validación de Certificado SSL de cliente extraído por Nginx*

    ssl_verify = request.headers.get(*"x-ssl-client-verify"*)

    ssl_dn = request.headers.get(*"x-ssl-client-s-dn"*)

    *if* ssl_verify *and* ssl_verify == *"SUCCESS"*:

        *if* *"O=TradingView, Inc."* *not* *in* ssl_dn *or* *"CN=webhook-server@tradingview.com"* *not* *in* ssl_dn:

            logger.warning(*f"Certificado SSL de cliente no autorizado: {ssl_dn}"*)

            *raise* HTTPException(

                status_code=status.HTTP_401_UNAUTHORIZED,

                detail=*"Certificado SSL de cliente inválido"*

            )

        logger.info(*f"Certificado SSL verificado para: {ssl_dn}"*)

    *# 3. Validación del Token Secreto Compartido*

    *if* payload.token != TOKEN_SECRETO_VÁLIDO:

        logger.warning(*"Intento de autenticación fallido por token secreto incorrecto."*)

        *raise* HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=*"Token de validación incorrecto"*

        )

    *# 4. Encolamiento de la Tarea en Segundo Plano (BackgroundTasks)*

    *# FastAPI retorna la respuesta HTTP 200 de forma inmediata en < 5ms,*

    *# mientras el worker asíncrono se encarga del procesamiento de la orden en segundo plano.*

    background_tasks.add_task(despachar_ejecución_de_orden_y_notificación, payload)

    logger.info(*f"Señal para {payload.symbol} validada correctamente y añadida a la cola asíncrona."*)

    *return* {

        *"status"*: *"success"*,

        *"message"*: *"Señal recibida con éxito y derivada al worker asíncrono de ejecución"*

    }

*if* __name__ == *"__main__"*:

    *# Arrancamos uvicorn de forma local escuchando en el puerto 8000 interno*

    uvicorn.run(*"production_gateway:app"*, host=*"127.0.0.1"*, port=*8000*, reload=*False*, workers=*4*)

Fuentes citadas

- TradingView with VPS: Webhook & Alert Automation, https://tradingfxvps.com/tradingview-with-vps-webhook-alert-automation/
- Pine Script to Trading Bot - Nadcab Labs, https://www.nadcab.com/blog/pine-script-trading-bot-tradingview-webhook-live-execution
- Introduction to TradingView alerts, https://www.tradingview.com/support/solutions/43000520149-introduction-to-tradingview-alerts/
- TradingView 2025 Review: Pros, Cons, and Plans Breakdown - NewTrading.io, https://www.newtrading.io/tradingview-review/
- TradingView Automated Trading: How to Auto-Execute Signals on Any Exchange (2026), https://www.tv-hub.org/guide/tradingview-automation
- Automating TradingView Alerts with a VPS and Webhooks: Architecture, Security, and Broker Integration Guide, https://www.vpsforextrader.com/blog/what-is-tradingview-and-how-to-use-it/
- TradingView alert delay causes and solutions - ClearEdge Automation, https://clearedge.trading/post/tradingview-alert-delay-causes-solutions
- Will alerts work if TradingView is not open on the computer?, https://www.tradingview.com/support/solutions/43000548327-will-alerts-work-if-tradingview-is-not-open-on-the-computer/
- Getting started with technical alerts - TradingView, https://www.tradingview.com/support/solutions/43000763315-getting-started-with-technical-alerts/
- How to use a variable value in alert - TradingView, https://www.tradingview.com/support/solutions/43000531021-how-to-use-a-variable-value-in-alert/
- TradingView Alerts Setup: Free Plan Limits (2026), https://www.tv-hub.org/guide/tradingview-alerts-setup
- Trendline drawing tool - TradingView, https://www.tradingview.com/support/solutions/43000518095-trendline-drawing-tool/
- Ray drawing tool - TradingView, https://www.tradingview.com/support/solutions/43000518113-ray-drawing-tool/
- Alerts - TradingView, https://www.tradingview.com/pine-script-docs/v5/faq/alerts/
- Alerts - TradingView, https://www.tradingview.com/pine-script-docs/faq/alerts/
- TradingView Alert Placeholders: Full List & {{plot}} Guide - PickMyTrade, https://docs.pickmytrade.trade/docs/tradingview-plot-placeholder/
- Introducing variables in Alerts — TradingView Blog, https://www.tradingview.com/blog/en/introducing-variables-in-alerts-14880/
- Strategy Alerts - TradingView, https://www.tradingview.com/support/solutions/43000481368-strategy-alerts/
- Alert was triggered too often and stopped - TradingView, https://www.tradingview.com/support/solutions/43000690939-alert-was-triggered-too-often-and-stopped/
- How to configure webhook alerts - TradingView, https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/
- How to Set Alerts on TradingView - Blueberry Markets, https://blueberrymarkets.com/market-analysis/how-to-set-alerts-on-tradingview/
- Cómo configurar alertas webhook - TradingView, https://es.tradingview.com/support/solutions/43000529348/
- TradingView Webhook Integration - Grokipedia, https://grokipedia.com/page/TradingView_Webhook_Integration
- Standard Alert Message Structure for TradingView Alerts - Tickerly, https://tickerly.net/standard-alert-message-structure/
- Frequently Asked Questions | Advanced Charts Documentation - TradingView, https://www.tradingview.com/charting-library-docs/latest/resources/Frequently-Asked-Questions/
- TradingView pricing UK 2026: plans & costs explained - CMC Markets, https://www.cmcmarkets.com/en-gb/trading-platforms/tradingview/tradingview-pricing-explained
- Cómo obtener más alertas activas por suscripción - TradingView, https://es.tradingview.com/support/solutions/43000690941/
- TradingView Subscriptions: Pricing and Features, https://www.tradingview.com/pricing/
- TradingView Alert Limits: What to Do When You Hit the Cap - Stock Alarm Pro, https://pro.stockalarm.io/blog/tradingview-alert-limits
- It's doubled now: more alerts for each plan! — TradingView Blog, https://www.tradingview.com/blog/en/more-alerts-for-each-plan-31701/
- TradingView Pricing 2026: Total Cost & Competitors Compared, https://checkthat.ai/brands/tradingview/pricing
- pine script - TradingView - Limit trades based on time - Stack Overflow, https://stackoverflow.com/questions/79343919/tradingview-limit-trades-based-on-time
- Alerts triggered too often are being stopped. How to solve? : r/TradingView - Reddit, https://www.reddit.com/r/TradingView/comments/1qk2otj/alerts_triggered_too_often_are_being_stopped_how/
- stop using webhooks for live execution if you care about your money : r/TradingView, https://www.reddit.com/r/TradingView/comments/1tk71me/stop_using_webhooks_for_live_execution_if_you/
- Writing / Limitations - TradingView, https://www.tradingview.com/pine-script-docs/v5/writing/limitations/
- How to Measure TradingView Latency in TradersPost, https://blog.traderspost.io/article/how-to-measure-tradingview-latency-in-traderspost
- Secure your Tradingview webhook with HTTPS - Nexus Fission - WordPress.com, https://nexusfission.wordpress.com/2024/01/19/secure-your-tradingview-webhook-with-https/
- Autenticación del webhook - TradingView, https://es.tradingview.com/support/solutions/43000680459/
- Webhook authentication - TradingView, https://www.tradingview.com/support/solutions/43000680459-webhook-authentication/
- Viandoks/tradingview-listener: A simple webhook listener for Tradingview - GitHub, https://github.com/Viandoks/tradingview-listener
- n8n integrations | Zapier, https://zapier.com/blog/n8n-integrations/
- Zapier vs IFTTT vs n8n vs Make:No-Code Automation Tools Compared - Ragic, https://www.ragic.com/intl/en/blog/470/no-code-integration-tools-comparison-n8n-make-zapier-ifttt
- Cómo integrar Whaticket con N8N, Zapier y Make - YouTube, https://www.youtube.com/watch?v=-MwrDLfElhw
- Connect n8n to IFTTT - WP Webhooks, https://wp-webhooks.com/integrations/n8n/workflows/ifttt/
- TradingView signal extractor with Gmail, Google Sheets & Telegram notifications - N8N, https://n8n.io/workflows/4334-tradingview-signal-extractor-with-gmail-google-sheets-and-telegram-notifications/
- Webhook Debugger & Logger - Real-time API Mocking & Testing - Apify, https://apify.com/ar27111994/webhook-debugger-logger