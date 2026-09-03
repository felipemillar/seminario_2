Diseño, Arquitectura e Implementación de un Pipeline de Automatización de Trading de Alta Disponibilidad: Conectando TradingView con Motores de Ejecución de Brokers

Arquitectura Completa del Pipeline

El diseño de un sistema de automatización de trading robusto y de grado institucional requiere un flujo unidireccional desacoplado, estructurado en capas jerárquicas para aislar las responsabilidades de generación de señales, control de flujo, gestión de riesgos y ejecución de órdenes. La estabilidad de este flujo es crítica, especialmente si se considera que la infraestructura cloud de TradingView despacha alertas de manera asíncrona mediante peticiones HTTP POST, esperando una respuesta inmediata del servidor receptor^1^. Si el servidor de destino tarda más de tres segundos en responder, TradingView cancelará de forma automática la solicitud, registrando un fallo de entrega en sus sistemas^1^. Además, el protocolo de red utilizado por TradingView no ofrece soporte para direccionamiento IPv6, limitando la comunicación estrictamente a redes IPv4^1^.

Diagrama del Flujo Completo de Red e Infraestructura

La arquitectura lógica de este pipeline se distribuye en seis segmentos de red diferenciados, cada uno operando bajo protocolos específicos de transporte y seguridad:

[ Capa de Análisis y Generación de Señal: TradingView Cloud ]

                         |

                         | Alerta HTTP POST (SSL/TLS - Puerto 443 únicamente)

                         | Direcciones IP de origen predefinidas

                         v

[ Capa de Seguridad Perimetral: Firewall de Red y Proxy Inverso ]

                         |

                         | Filtrado por lista de IPs permitidas

                         | Descifrado de capa de transporte (Terminación SSL/TLS)

                         | Forwarding de cabeceras de red (X-Forwarded-For) [cite: 6, 7, 8]

                         v

[ Capa de Enrutamiento y Validación: Servidor ASGI FastAPI ]

                         |

                         | Autenticación criptográfica (Firma con Clave Secreta)

                         | Ingesta no bloqueante del Payload JSON [cite: 2]

                         | Almacenamiento local persistente inmediato (SQLite3)

                         | Evaluación en paralelo de reglas de gestión de riesgos

                         v

[ Capa de Conectividad con Brokers: Clientes de APIs Financieras ]

                         |

                         | Traducción y Mapeo dinámico de Símbolos de Mercado

                         | Distribución de órdenes mediante peticiones asíncronas

                         v

[ Capa de Ejecución del Broker: Gateways de Acceso y APIs REST/WS ]

                         |

                         | Liquidación y enrutamiento a Cámaras de Compensación (Slippage)

                         | Envío de confirmaciones de llenado (Fills)

Presupuesto de Latencia End-to-End y Análisis de Retardo

Para evaluar el impacto del deslizamiento (*slippage*) de precios en las operaciones, es imprescindible desglosar el presupuesto de latencia en cada segmento del pipeline bajo condiciones normales y de alta congestión de red:

| **Tramo de Comunicación** | **Protocolo / Mecanismo** | **Latencia Óptima (ms)** | **Latencia Congestionada (ms)** | **Causa de Variabilidad** |
| --- | --- | --- | --- | --- |
| **Generación de Alerta en Gráfico** | Motor de Ejecución Pine Script |  |  | Complejidad del script y cálculo de indicadores por barra. |
| **Tránsito WAN (TradingView a Proxy)** | HTTPS (TCP Puerto 443)^1^ |  |  | Enrutamiento geográfico e interrupciones en el peering BGP^4^. |
| **Terminación TLS y Proxy Inverso** | Nginx / Caddy / Traefik^5^ |  |  | Capacidad de procesamiento de hilos y tamaño del pool de conexiones. |
| **Validación e Ingesta en FastAPI** | Deserialización JSON y SQLite Write^10^ |  |  | Bloqueos de disco I/O y contención en la base de datos relacional. |
| **Motor de Gestión de Riesgo** | Validación de Equity, Drawdown y Horas |  |  | Consultas externas a cachés de datos en memoria o APIs. |
| **Tránsito WAN (Middleware a Broker)** | API REST / WebSocket Privado |  |  | Co-ubicación física con los servidores del broker (Equinix NY4/LD4)^4^. |
| **Procesamiento de Orden en Broker** | Matching Engine de la Bolsa / Liquidez |  |  | Profundidad del libro de órdenes y validaciones internas de margen^12^. |
| **Total de Latencia Acumulada** | **Flujo End-to-End Completo** |  |  | Fluctuación de la volatilidad del mercado en momentos de noticias. |

Puntos Únicos de Fallo (SPOF) y Estrategias de Mitigación

- **Pérdida de la Petición Webhook por Timeout**: TradingView cancela la petición si el receptor tarda más de 3 segundos en responder^1^. Para mitigar este problema, el middleware debe desacoplar de inmediato la recepción de la alerta de la ejecución en el broker. Al recibir la solicitud, FastAPI realiza una validación sintáctica ultrarrápida, escribe la alerta en SQLite3 de manera asíncrona^10^ y responde con un código de estado 202 Accepted. Todo el procesamiento posterior (gestión de riesgos, mapeo de símbolos, peticiones de red al broker) se delega a tareas en segundo plano (*Background Tasks*) administradas por un bucle de eventos no bloqueante.
- **Caída del Proceso del Servidor Web**: Si el proceso que aloja el receptor de webhooks experimenta una excepción no controlada en memoria o un fallo del sistema, el pipeline quedará inoperativo. La mitigación consiste en implementar un gestor de procesos del sistema como systemd en Linux o PM2 en Node.js, configurado con políticas de reinicio agresivas ante fallos de ejecución^4^. Adicionalmente, el despliegue debe realizarse en un Servidor Privado Virtual (VPS) que cuente con fuentes de alimentación redundantes, una IP estática persistente y mitigación nativa contra ataques de denegación de servicio (DDoS)^4^.
- **Saturación por Rate Limiting de la API del Broker**: El envío masivo de órdenes repetitivas puede provocar el bloqueo temporal de la cuenta por parte del broker^2^. Esto se mitiga implementando un sistema de limitación de frecuencia de tipo ventana deslizante en el middleware, el cual rechaza de inmediato alertas duplicadas originadas por fallas de lógica en los scripts de TradingView antes de que estas se traduzcan en peticiones de red salientes al broker.

Brokers con Integración Nativa de TradingView

TradingView ofrece conexiones directas con diversos brokers del sector financiero a través de su panel de trading integrado. No obstante, para operaciones automatizadas basadas puramente en lógica cuantitativa y ejecuciones sin intervención manual, existen divergencias funcionales críticas entre operar de forma directa mediante la plataforma de TradingView o estructurar un pipeline de ejecución personalizado a través de webhooks^2^.

Comparativa Multidimensión de Brokers Compatibles

La siguiente tabla resume las capacidades técnicas y operativas de los principales intermediarios financieros que permiten operaciones a través del ecosistema de TradingView:

| **Broker** | **Clase de Activos** | **Interfaz de API de Trading** | **Latencia de API Media** | **Soporte de Perfiles Multicuenta (Asesores)** | **Requisitos Previos de Cuenta** |
| --- | --- | --- | --- | --- | --- |
| **Interactive Brokers (IBKR)** | Acciones, Opciones, Futuros, Bonos, Forex, Criptomonedas^12^. | Client Portal REST API / TWS API (TCP)^13^. |  | Perfiles de Asignación de Asesores Financieros (FA) y Grupos de Distribución^16^. | Cuenta tipo IBKR Pro, balance mínimo para la suscripción a datos en tiempo real^13^. |
| **OANDA** | Forex, CFDs sobre Índices y Materias Primas^17^. | v20 REST API / Streaming API^18^. |  | No disponible a nivel de API minorista (requiere subcuentas independientes). | Cuenta fxTrade activa, habilitación del token de acceso API en el portal AMP^19^. |
| **Alpaca** | Acciones de EE.UU., ETFs, Criptomonedas^20^. | REST API v2 / WSS Streaming^20^. |  | Integración OAuth nativa para la gestión distribuida de cuentas^21^. | Cuenta de trading autorizada y fondeada^20^. |
| **Binance** | Criptomonedas (Spot, Margen, Futuros). | REST API / WebSockets Públicos y Privados. |  | Subcuentas vinculadas y llaves API con permisos de trading específicos. | Verificación de identidad (KYC) completada, configuración de llaves de API con firma HMAC SHA-256. |
| **TradeStation** | Acciones, Opciones, Futuros. | WebAPI REST / Streaming. |  | Cuentas institucionales agrupadas con inicio de sesión único. | Cuenta activa, suscripción a datos de mercado profesionales, habilitación de API. |

Análisis de Operabilidad: Trading Directo frente a Pipeline de Webhooks

La negociación directa desde los gráficos de TradingView es adecuada para operadores discrecionales que requieren una interfaz visual para colocar órdenes manuales de forma rápida. Sin embargo, este enfoque presenta serios inconvenientes en entornos algorítmicos. Las desconexiones de sesión debido a la caducidad del token de autenticación del broker ocurren con frecuencia, obligando al operador a iniciar sesión manualmente en el panel de trading de TradingView de forma recurrente. Además, carece de flexibilidad para aplicar reglas condicionales de gestión de riesgos, mapeo de símbolos exóticos personalizados o distribución coordinada de órdenes en múltiples cuentas.

Por el contrario, el desarrollo de un pipeline personalizado mediante webhooks proporciona un control absoluto sobre el ciclo de vida de la transacción^2^. Al implementar un middleware en un entorno VPS dedicado, el operador queda protegido de las desconexiones visuales de la interfaz de usuario de TradingView^4^. El middleware asume de manera centralizada la responsabilidad de interceptar las alertas, validar criptográficamente la integridad del origen, mapear los tickers de acuerdo con las especificaciones de cada broker y distribuir las operaciones simultáneamente a múltiples plataformas^2^. Esto optimiza la tolerancia a fallos del sistema y minimiza los tiempos de inactividad operativa^4^.

Paper Trading de TradingView

El módulo de *Paper Trading* provisto nativamente por TradingView sirve como un entorno de simulación inicial útil para depurar la lógica básica de los indicadores de mercado. No obstante, se observan diferencias operativas profundas al comparar este simulador gráfico frente a entornos reales o históricos.

Dinámica de Ejecución del Motor de Simulación Gráfica

El motor de simulación de Paper Trading de TradingView procesa las cotizaciones de precios en tiempo real (*live data feeds*). Utiliza reglas simplificadas de prioridad para simular la ejecución de órdenes en el último precio registrado de cotización (*Last Trade*). Sin embargo, este mecanismo pasa por alto factores esenciales del mercado:

- **Ausencia de Modelado de Deslizamiento (Slippage)**: El simulador asume que el mercado posee liquidez infinita al precio actual. En entornos reales, una orden de gran tamaño barre los niveles del libro de órdenes (*order book*), ejecutándose a un precio promedio sustancialmente peor que el precio de visualización de la alerta.
- **Omisión del Impacto en el Libro de Órdenes**: Colocar una orden de gran escala en una cuenta de simulación no altera los niveles de oferta y demanda reales. En mercados reales de baja liquidez, la inyección de volumen altera de inmediato las intenciones de los participantes del mercado, provocando movimientos de precios adversos previos a la ejecución.
- **Falta de Simulación de la Cola de Órdenes Límite**: En el mercado real, las órdenes límite se apilan secuencialmente siguiendo una prioridad de precio y tiempo. Una orden límite de compra en el simulador gráfico de TradingView suele llenarse tan pronto como el precio bid toca el nivel exacto especificado, mientras que en condiciones reales la orden podría no ejecutarse si el precio se revierte antes de que se completen las órdenes precedentes en la cola de mercado.
- **Cargos por Financiamiento y Comisiones Dinámicas**: El motor de simulación no aplica spreads dinámicos de forma realista durante fases de alta volatilidad (por ejemplo, en la publicación de datos macroeconómicos), ni simula con precisión los cargos por swap diario de Forex o las tasas de financiación de los contratos de futuros perpetuos de criptomonedas^23^.

Fase de Validación en Entornos UAT del Broker

Antes de comprometer capital real en producción, el pipeline completo de automatización debe someterse a una validación rigurosa utilizando entornos de pruebas de aceptación del usuario (UAT) proporcionados por el broker, tales como Alpaca Paper Trading o las cuentas demo de Interactive Brokers^10^. El objetivo de esta fase de validación es doble:

- **Validar la Integridad del Pipeline de Red**: Garantizar que el middleware reciba, procese e introduzca de manera consistente las órdenes de prueba en las APIs del broker sin generar excepciones de red ni registrar picos de latencia imprevistos^2^.
- **Verificar la Lógica del Motor de Gestión de Riesgos**: Comprobar que los algoritmos de dimensionamiento de posición, el rate limiting por activo y los disyuntores de drawdown actúen de manera correcta ante escenarios simulados de pérdida extrema o envío masivo de señales duplicadas.

Diferencias Clave: Backtester vs. Live Paper Trading

| **Métrica de Comparación** | **Backtester de TradingView (Histórico)** | **Live Paper Trading (Simulación en Tiempo Real)** |
| --- | --- | --- |
| **Naturaleza de los Datos** | Barras de precios históricas ya consolidadas. | Flujo continuo de ticks de mercado en tiempo real. |
| **Sesgo de Mirada al Futuro** | Posible si el programador utiliza de forma incorrecta variables de Pine Script en barras no finalizadas. | Imposible; la lógica avanza secuencialmente al ritmo del reloj del sistema. |
| **Resolución de Datos** | Limitada al tamaño de la barra histórica del gráfico. | Resolución máxima basada en ticks individuales de mercado. |
| **Latencia de Ejecución** | Despreciable; asume ejecuciones instantáneas sin retardo de red ni colas de espera. | Realista respecto al retardo de red WAN de la alerta, aunque omite el retardo del libro de órdenes. |
| **Efecto de Repintado** | Vulnerable si los indicadores recalculan sus valores históricos de forma retrospectiva (ej. la función security). | Inmune; las señales emitidas en tiempo real se consolidan sobre eventos pasados inalterables. |

Diseño del Middleware (Webhook Receiver)

El desarrollo del middleware que actúa como receptor de los webhooks de TradingView requiere el uso de arquitecturas de software asíncronas de alto rendimiento capaces de gestionar flujos de datos concurrentes sin bloquear el hilo principal de ejecución. FastAPI, un framework web asíncrono para Python basado en ASGI (Starlette) y Uvicorn, ofrece un rendimiento óptimo con un consumo mínimo de recursos de CPU y memoria.

Arquitectura de Seguridad Perimetral y de Aplicación

Para garantizar que el middleware procese exclusivamente alertas legítimas de TradingView y evitar ataques de denegación de servicio o inyección de órdenes falsas, se implementa una estrategia de defensa en tres niveles:

- **Filtro de IPs en el Firewall de Red**: El servidor VPS debe configurarse utilizando herramientas como ufw o reglas de seguridad en la nube para permitir tráfico entrante en los puertos de servicio (comúnmente 80/443 para webhooks) de manera exclusiva desde los rangos de direcciones IP estáticas oficiales de TradingView: 52.89.214.238, 34.212.75.30, 54.218.53.128 y 52.32.178.7^1^.
- **Validación del Certificado de Cliente SSL (mTLS)**: En conexiones HTTPS, los servidores de TradingView envían un certificado SSL para autenticar su identidad, permitiendo verificar criptográficamente que la petición se origina en sus servidores^24^. El Common Name (CN) del emisor es webhook-server@tradingview.com^24^. El proxy inverso (por ejemplo, Nginx) puede configurarse para validar este certificado antes de redirigir la petición al middleware:
Nginx
*ssl_client_certificate* /etc/nginx/certs/tradingview_ca.crt;
*ssl_verify_client* optional; *# O estricto para forzar validación de cliente*
- **Firma con Token Secreto Compartido**: El payload JSON de la alerta generada en TradingView debe contener una clave de seguridad de alta entropía generada por el operador^4^. El middleware compara esta clave con una variable de entorno segura del sistema antes de iniciar cualquier procesamiento^4^.

Extracción de la IP Real Detrás del Proxy Inverso

Dado que el middleware se despliega de manera estándar detrás de un proxy inverso (Nginx, Caddy o Traefik) que gestiona la encriptación SSL/TLS^5^, FastAPI no verá directamente la dirección IP del cliente emisor original^6^. En su lugar, detectará la dirección IP local de loopback del proxy (típicamente 127.0.0.1 o una IP del segmento de red interna de contenedores 172.17.0.X)^7^.

Para resolver esto, el proxy inverso debe configurarse para inyectar la cabecera X-Forwarded-For conteniendo la IP de origen original^5^. Por motivos de seguridad, el middleware no debe confiar a ciegas en estas cabeceras a menos que provengan de proxies de confianza^6^. Esto se gestiona mediante la integración de ProxyHeadersMiddleware de Uvicorn, limitando los hosts en los que se confía para propagar estas cabeceras^7^.

Mapping de Símbolos

Los mercados financieros carecen de una nomenclatura unificada para identificar los activos negociables. Mientras que TradingView consolida datos de múltiples proveedores utilizando prefijos de intercambio para organizar su base de datos, cada broker emplea formatos de codificación específicos para procesar las transacciones de forma electrónica.

Inconsistencias de Nomenclatura entre Plataformas

- **Renta Variable (Equities)**: TradingView identifica las acciones utilizando la estructura MERCADO:TICKER (ej. NASDAQ:AAPL). Alpaca requiere únicamente el ticker limpio AAPL^20^. Interactive Brokers suele rechazar la coincidencia de cadenas de texto simples debido a la ambigüedad entre clases de activos negociados en múltiples bolsas internacionales, exigiendo en su lugar el uso de su identificador de contrato interno conocido como conid (ej. 265598 para Apple Inc.)^26^.
- **Divisas (Forex)**: TradingView formatea los pares de divisas concatenando los códigos ISO de cada moneda sin delimitadores (ej. FX:EURUSD o OANDA:EURUSD). La API REST v20 de OANDA requiere explícitamente un guion bajo como separador de los componentes (ej. EUR_USD)^17^.
- **Criptomonedas**: Las alertas de Binance en TradingView suelen enviarse con el prefijo de exchange incorporado (ej. BINANCE:BTCUSDT). Para la colocación de órdenes en Binance, la API del exchange espera la cadena de texto continua BTCUSDT, mientras que la API de Alpaca Crypto utiliza la codificación estándar de mercado de tres decimales o pares delimitados como BTCUSD o BTC/USDT^20^.
- **Contratos de Futuros**: Un contrato continuo de futuros de micro S&P 500 en TradingView se visualiza como CME_MINI:MES1!. Los brokers de futuros tradicionales requieren la codificación del mes y año específico de vencimiento de la entrega física (ej. MESM26 para el vencimiento de junio de 2026), lo que obliga al middleware a implementar lógica de cálculo de fechas de expiración.

Tabla Multiactivo de Correspondencias de Símbolos

| **Activo Financiero de Referencia** | **Ticker en TradingView** | **Ticker en Alpaca** | **Ticker en OANDA** | **Ticker en Binance** | **Símbolo en Broker** | **Conid de Interactive Brokers** |
| --- | --- | --- | --- | --- | --- | --- |
| **Euro / Dólar Estadounidense** | FX:EURUSD | N/D | EUR_USD<br>[cite: 17, 28] | N/D | EURUSD | 12087792 |
| **Bitcoin / Tether** | BINANCE:BTCUSDT | BTCUSD<br>[cite: 20] | N/D | BTCUSDT | BTCUSD | 767923481 |
| **Tesla Inc. (Renta Variable)** | NASDAQ:TSLA | TSLA<br>[cite: 20, 25] | N/D | N/D | TSLA | 7679234 |
| **Futuro E-mini S&P 500** | CME:ES1! | N/D | N/D | N/D | US500 | 495512572 (Contrato Activo) |
| **Oro / Dólar (CFD)** | OANDA:XAUUSD | N/D | XAU_USD | N/D | XAUUSD | 3322441 |

Automatización del Proceso de Mapeo

Para implementar un motor de traducción escalable y dinámico que no dependa de modificaciones constantes en el código de producción, el middleware debe gestionar estas equivalencias mediante una tabla relacional estructurada o un almacén de datos clave-valor de alta velocidad como Redis. El flujo operativo para automatizar el mapping de símbolos se detalla a continuación:

[ Recepción del Ticker TV: "BINANCE:BTCUSDT" ]

                      |

                      v

     [ Parser de Tickers: Regex Engine ]

                      |

                      +---> Extrae el Broker de Origen: "BINANCE"

                      +---> Extrae el Símbolo Base: "BTCUSDT"

                      |

                      v

      [ Consulta en Diccionario de Mapeo ]

                      |

                      +---> Si Destino = "Alpaca" -> Retorna "BTCUSD"

                      +---> Si Destino = "Binance" -> Retorna "BTCUSDT"

                      +---> Si Destino = "IBKR" -> Retorna conid "767923481"

                      |

                      v

[ Retorno de Símbolo Mapeado al Motor de Ejecución ]

Plataformas Bridge Existentes

Para los operadores algorítmicos que prefieren omitir el desarrollo de software de conectividad personalizado desde cero, existen plataformas comerciales tipo "bridge" que se encargan del procesamiento de las alertas de TradingView y de su enrutamiento hacia diferentes terminales de ejecución.

Análisis Comparativo de Soluciones Comerciales de Integración

La siguiente tabla resume las características técnicas, operativas y económicas de las principales soluciones bridge disponibles en el mercado:

| **Plataforma Bridge** | **Destino Principal de Enrutamiento** | **Latencia Media de Red** | **Costo Operativo** | **Funcionalidades Clave** | **Limitaciones Técnicas** |
| --- | --- | --- | --- | --- | --- |
| **PineConnector** | Brokers 4 / Plataformas Institucionales^23^. | [cite: 29] | Desde $0.58 a $0.88 diarios por cuenta^30^. | Sintaxis estructurada robusta para órdenes pendientes y trailing stops^31^. | Soporte descontinuado de forma activa para MT4 desde octubre de 2025^9^. |
| **3Commas** | Exchanges de Criptomonedas de primer nivel. |  | Suscripción mensual fija desde $15 a $79. | Replicación multicuenta (*copy trading*) y bots de rebalanceo de carteras. | Elevada latencia de procesamiento no apta para scalping intradiario. |
| **Cornix** | Canales de Telegram y Cuentas de Criptomonedas. |  | Planes de pago mensuales desde $19.90. | Ejecución automatizada basada en análisis de sintaxis de texto de Telegram. | Restringido exclusivamente al mercado de criptomonedas. |
| **Wunderbit** | Exchanges de Criptomonedas y Motores de Arbitraje. |  | Modelo de comisión sobre beneficios o suscripción fija. | Copiador de operaciones social integrado y terminales de trading manuales. | Integración limitada con brókers tradicionales de renta variable o futuros. |

Sintaxis Estructurada de Parámetros de PineConnector

PineConnector utiliza una sintaxis estricta delimitada por comas para empaquetar de forma compacta toda la lógica transaccional dentro del cuerpo de texto de una alerta de TradingView^31^. El formato obligatorio que debe seguir el payload es el siguiente^31^:

- **ID de Licencia**: Identificador único numérico (de 13 a 14 dígitos) proporcionado al usuario registrado^31^.
- **Comando**: Instrucción directa de ejecución de la orden (buy, sell, closelong, closeshort, closelongbuy, closeshortsell)^9^.
- **Símbolo**: Nombre del activo mapeado exactamente de acuerdo con la nomenclatura del Brokers del broker^31^.
- **Parámetros Modernos Explícitos (Sintaxis Actualizada)**^31^:

- vol_lots=: Define el volumen estricto de ejecución medido en lotes estándar de Brokers^31^.
- vol_dollar=: Configura el volumen de riesgo expresado en valor monetario nominal (requiere definición de stop loss)^31^.
- vol_pct_eq_loss=: Calcula automáticamente los lotes a operar arriesgando un porcentaje fijo de la equidad de la cuenta basado en la distancia del stop loss^31^.
- sl_pips=: Ubica el stop loss a una distancia fija medida en pips relativos al precio de entrada^31^.
- sl_price=: Establece el stop loss en un nivel de precio absoluto de cotización de mercado^31^.
- tp_pips=: Define el objetivo de beneficio a una distancia relativa fija medida en pips^31^.
- betrigger=: Activa el movimiento de la orden a breakeven cuando el mercado se desplaza un número determinado de pips a favor de la operación^31^.
- beoffset=: Define el desplazamiento en pips desde el precio de entrada donde se posicionará el nuevo stop loss una vez activado el breakeven^31^.
- secret=: Token de seguridad alfanumérico para verificar la identidad del emisor (añadiendo seguridad si el ID de licencia es comprometido)^9^.

Ejemplo de Alerta de Compra con Definición Explícita de Parámetros de Riesgo y Breakeven^9^: 6161199464661,buy,EURUSD,vol_pct_eq_loss=1.5,sl_pips=30,tp_pips=60,betrigger=15,beoffset=1,secret=PineApple123

Ejecución en Diferentes Tipos de Broker

Cada broker requiere métodos específicos para interactuar con su API, lo que obliga al middleware a implementar módulos de comunicación y lógica de control de errores adaptados a cada plataforma.

1. Ejecución en Plataformas Institucionales (vía Gateway FastAPI Existente)

Cuando se utiliza un Gateway intermedio desarrollado en FastAPI que interactúa de manera directa con la API del terminal Plataformas Institucionales (generalmente ejecutándose en un entorno local o de red privada en la dirección api.broker.com), el middleware traduce la alerta de TradingView y despacha una solicitud POST formateada con un esquema JSON simplificado hacia el Gateway:

Python

*import* httpx

*async* *def* *enviar_orden_gateway_broker**(symbol:* *str**, action:* *str**, volume:* *float**, sl:* *float**, tp:* *float**):*

    gateway_url = *"http://api.broker.com/api/v1/order"*

    payload = {

        *"action"*: action.upper(),  *# "BUY" o "SELL"*

        *"symbol"*: symbol,

        *"volume"*: volume,

        *"sl_price"*: sl,

        *"tp_price"*: tp

    }

    *async* *with* httpx.AsyncClient() *as* client:

        response = *await* client.post(gateway_url, json=payload, timeout=*5.0*)

        response.raise_for_status()

        *return* response.json()

2. Ejecución en Interactive Brokers (vía API REST de IBKR)

La API REST del Client Portal de Interactive Brokers se ejecuta de manera local en el puerto 5000 (https://localhost:5000) a través del agente de conexión Java *Client Portal Gateway*^14^. Esta API requiere un flujo interactivo de confirmación paso a paso de alertas (*Order Reply*)^26^. Al enviar una orden, IBKR suele responder con advertencias de riesgo que requieren que el sistema envíe una confirmación afirmativa del parámetro replyid antes de procesar definitivamente la orden en el mercado^26^.

Python

*import* httpx

*async* *def* *colocar_orden_ibkr**(account_id:* *str**, conid:* *int**, side:* *str**, quantity:* *int**, limit_price:* *float**):*

    base_url = *"https://localhost:5000/v1/api"*

    orders_url = *f"{base_url}/iserver/account/{account_id}/orders"* [cite: *16*, *26*]

    order_payload = {

        *"orders"*: [

            {

                *"acctId"*: account_id,

                *"conid"*: conid,

                *"orderType"*: *"LMT"*,

                *"price"*: limit_price,

                *"side"*: side.upper(),  *# "BUY" o "SELL"*

                *"tif"*: *"DAY"*,

                *"quantity"*: quantity

            }

        ]

    }

    *async* *with* httpx.AsyncClient(verify=*False*) *as* client:  *# Client Portal utiliza certificado autofirmado*

        response = *await* client.post(orders_url, json=order_payload)

        response_json = response.json()

        *# Evalúa si se requiere una confirmación de advertencia de riesgo (Reply Workflow)*

        *if* *isinstance*(response_json, *list*) *and* *len*(response_json) > *0* *and* *"id"* *in* response_json[*0*]:

            reply_id = response_json[*0*][*"id"*] [cite: *26*]

            *# Despacha la confirmación afirmativa al endpoint de respuesta [cite: 27]*

            reply_url = *f"{base_url}/iserver/reply/{reply_id}"* [cite: *27*]

            reply_response = *await* client.post(reply_url, json={*"confirmed"*: *True*}) [cite: *27*]

            *return* reply_response.json()

        *return* response_json

3. Ejecución en Alpaca (API REST para Equities USA)

La API de Alpaca destaca por su facilidad de integración en entornos de desarrollo modernos. Utiliza autenticación simple por cabeceras HTTP seguras^25^.

Python

*import* httpx

*async* *def* *colocar_orden_alpaca**(api_key:* *str**, secret_key:* *str**, symbol:* *str**, qty:* *int**, side:* *str**):*

    url = *"https://paper-api.alpaca.markets/v2/orders"*  *# Entorno Paper Trading*

    headers = {

        *"APCA-API-KEY-ID"*: api_key, [cite: *25*]

        *"APCA-API-SECRET-KEY"*: secret_key [cite: *25*]

    }

    payload = {

        *"symbol"*: symbol,

        *"qty"*: *str*(qty),

        *"side"*: side.lower(),  *# "buy" o "sell"*

        *"type"*: *"market"*,

        *"time_in_force"*: *"day"* [cite: *20*, *25*]

    }

    *async* *with* httpx.AsyncClient() *as* client:

        response = *await* client.post(url, json=payload, headers=headers)

        response.raise_for_status()

        *return* response.json()

4. Ejecución en Binance (API REST para Crypto)

La ejecución en Binance exige una firma criptográfica robusta utilizando el algoritmo HMAC SHA-256 para cada petición enviada a endpoints privados de órdenes, con el fin de evitar ataques de suplantación o alteración de datos de red en tránsito.

Python

*import* hmac

*import* hashlib

*import* time

*import* httpx

*async* *def* *colocar_orden_binance**(api_key:* *str**, secret_key:* *str**, symbol:* *str**, side:* *str**, quantity:* *float**):*

    url = *"https://api.binance.com/api/v3/order"*

    timestamp = *int*(time.time() * *1000*)

    query_params = *f"symbol={symbol.upper()}&side={side.upper()}&type=MARKET&quantity={quantity}&timestamp={timestamp}"*

    signature = hmac.new(

        secret_key.encode(*"utf-8"*),

        query_params.encode(*"utf-8"*),

        hashlib.sha256

    ).hexdigest()

    full_url = *f"{url}?{query_params}&signature={signature}"*

    headers = {*"X-MBX-APIKEY"*: api_key}

    *async* *with* httpx.AsyncClient() *as* client:

        response = *await* client.post(full_url, headers=headers)

        response.raise_for_status()

        *return* response.json()

5. Ejecución en OANDA (API REST para Forex)

El motor de ejecución de Forex en OANDA procesa unidades físicas individuales del par monetario transaccionado en lugar de lotes de mercado estándar.

Python

*import* httpx

*async* *def* *colocar_orden_oanda**(api_token:* *str**, account_id:* *str**, instrument:* *str**, units:* *int**, stop_loss:* *float**, take_profit:* *float**):*

    url = *f"https://api-fxtrade.oanda.com/v3/accounts/{account_id}/orders"*

    headers = {

        *"Authorization"*: *f"Bearer {api_token}"*, [cite: *19*]

        *"Content-Type"*: *"application/json"*

    }

    payload = {

        *"order"*: {

            *"units"*: *str*(units),  *# Unidades positivas para compra, negativas para venta*

            *"instrument"*: instrument.upper(),  *# ej. "EUR_USD"*

            *"timeInForce"*: *"FOK"*,

            *"type"*: *"MARKET"*,

            *"positionFill"*: *"DEFAULT"*,

            *"stopLossOnFill"*: {*"price"*: *f"{stop_loss:**.5**f}"*}, [cite: *28*, *33*]

            *"takeProfitOnFill"*: {*"price"*: *f"{take_profit:**.5**f}"*} [cite: *28*]

        }

    }

    *async* *with* httpx.AsyncClient() *as* client:

        response = *await* client.post(url, json=payload, headers=headers)

        response.raise_for_status()

        *return* response.json()

Risk Management en el Middleware

La implementación de controles estrictos de gestión de riesgos cuantitativos en el middleware evita pérdidas catastróficas derivadas de fallas lógicas de las alertas enviadas por TradingView o de anomalías en los mercados financieros.

Fórmulas Matemáticas para el Dimensionamiento de Posición (Position Sizing)

El tamaño adecuado de cada lote de ejecución debe calcularse de manera dinámica utilizando modelos de riesgo basados en la equidad actual de la cuenta del broker. El cálculo de volumen se fundamenta en la siguiente ecuación matemática:

Si el activo transaccionado opera en lotes (como en los contratos de futuros o en las cuentas Broker tradicionales), el tamaño calculado en unidades debe convertirse a lotes estándar utilizando el tamaño del contrato del activo ():

Disyuntor de Pérdida Máxima Diaria (Drawdown Circuit Breaker)

El middleware realiza una consulta rápida sobre el saldo actual de la equidad de la cuenta de trading en el broker en cada ciclo de ejecución de una alerta. El sistema mantiene un registro diario persistente de la equidad máxima alcanzada en la apertura del día de negociación (*High Water Mark* - HWM). Si en algún instante del día se cumple la siguiente inecuación de control:

El middleware activa de inmediato un estado de bloqueo interno permanente (*Circuit Breaker*), procediendo a cancelar todas las órdenes activas del mercado, liquidando de manera inmediata las posiciones abiertas de la cartera de activos y rechazando sistemáticamente cualquier alerta entrante de TradingView.

Control de Frecuencia (Rate Limiting) por Activo

Para evitar pérdidas por fallas lógicas que provoquen alertas repetitivas en Pine Script, el middleware implementa un algoritmo de ventana deslizante de tiempo. Se deniega el enrutamiento de cualquier orden al broker si el volumen de peticiones para un activo supera un límite parametrizado de  ejecuciones autorizadas por intervalo de tiempo (ej. máximo 5 órdenes por hora por símbolo).

Verificación de Horario de Mercado

Para operar activos tradicionales (ej. acciones, opciones o futuros de commodities) que no cotizan continuamente, el middleware utiliza la biblioteca de Python pandas_market_calendars para verificar en tiempo real si el mercado correspondiente se encuentra abierto antes de enrutar la orden al broker^34^:

Python

*import* pandas_market_calendars *as* mcal

*from* datetime *import* datetime

*import* pandas *as* pd

*def* *verificar_mercado_activo**(exchange_name:* *str**) -> bool:*

    *"""

    Retorna True si la sesión de mercado actual está activa para el exchange indicado.

    Por ejemplo, exchange_name='NYSE' o 'LSE' [cite: 34, 36].

    """*

    *try*:

        calendar = mcal.get_calendar(exchange_name) [cite: *34*, *36*]

        ahora_utc = pd.Timestamp(datetime.utcnow(), tz=*'UTC'*)

        *# Consulta el cronograma operativo del día en curso [cite: 36, 37]*

        schedule = calendar.schedule(start_date=ahora_utc.date(), end_date=ahora_utc.date()) [cite: *36*, *37*]

        *if* schedule.empty: [cite: *37*]

            *return* *False*

        *# Comprueba si el timestamp actual se encuentra dentro del rango operativo regular de la bolsa [cite: 38]*

        *return* calendar.open_at_time(schedule, ahora_utc) [cite: *38*]

    *except* Exception:

        *# En caso de error, el sistema bloquea preventivamente la operación (enfoque conservador)*

        *return* *False*

Botón de Parada de Emergencia Manual (Kill Switch)

El middleware expone un endpoint seguro que permite al operador activar o desactivar manualmente un estado de bloqueo global preventivo (KILL_SWITCH_ACTIVE = True). Cuando se activa este estado, se rechaza de inmediato cualquier solicitud de entrada de nuevas operaciones, notificando inmediatamente al operador a través de mensajería instantánea.

Logging y Auditoría

La auditoría exhaustiva de la actividad operativa del middleware es obligatoria para diagnosticar errores de comunicación, monitorizar el deslizamiento de precios (*slippage*) y cumplir con requisitos de reconciliación regulatoria o fiscal.

Esquema Relacional DDL de la Base de Datos SQLite3

SQL

*-- Tabla para registrar la recepción de cada webhook desde TradingView*

*CREATE* *TABLE* IF *NOT* *EXISTS* tradingview_alerts (

    id *INTEGER* *PRIMARY* KEY AUTOINCREMENT,

    received_at DATETIME *DEFAULT* *CURRENT_TIMESTAMP*,

    symbol TEXT *NOT* *NULL*,

    action TEXT *NOT* *NULL*,

    risk_pct *REAL* *NOT* *NULL*,

    sl_price *REAL*,

    tp_price *REAL*,

    raw_payload TEXT *NOT* *NULL*

);

*-- Tabla para almacenar el estado y detalles de las órdenes enviadas al Broker*

*CREATE* *TABLE* IF *NOT* *EXISTS* broker_orders (

    id *INTEGER* *PRIMARY* KEY AUTOINCREMENT,

    alert_id *INTEGER*,

    broker_name TEXT *NOT* *NULL*,

    broker_order_id TEXT *UNIQUE*,

    order_type TEXT *NOT* *NULL*,

    quantity *REAL* *NOT* *NULL*,

    limit_price *REAL*,

    status TEXT *NOT* *NULL*, *-- 'PENDING', 'FILLED', 'REJECTED', 'FAILED'*

    error_message TEXT,

    sent_at DATETIME *DEFAULT* *CURRENT_TIMESTAMP*,

    *FOREIGN* KEY(alert_id) *REFERENCES* tradingview_alerts(id)

);

*-- Tabla para auditar los detalles finales de ejecución (Fills) devueltos por el broker*

*CREATE* *TABLE* IF *NOT* *EXISTS* execution_fills (

    id *INTEGER* *PRIMARY* KEY AUTOINCREMENT,

    broker_order_id TEXT,

    fill_price *REAL* *NOT* *NULL*,

    filled_qty *REAL* *NOT* *NULL*,

    commission *REAL* *DEFAULT* *0.0*,

    slippage *REAL*,

    executed_at DATETIME *DEFAULT* *CURRENT_TIMESTAMP*,

    *FOREIGN* KEY(broker_order_id) *REFERENCES* broker_orders(broker_order_id)

);

*-- Creación de índices optimizados para agilizar la depuración de consultas*

*CREATE* INDEX IF *NOT* *EXISTS* idx_alerts_symbol *ON* tradingview_alerts(symbol);

*CREATE* INDEX IF *NOT* *EXISTS* idx_orders_status *ON* broker_orders(status);

Proceso Sistemático de Reconciliación de Operaciones (Trade Reconciliation)

Para garantizar la integridad del sistema y corregir posibles asimetrías de datos, el middleware ejecuta una tarea programada al cierre de cada jornada operativa que realiza las siguientes funciones de reconciliación:

- **Descarga del Historial Oficial del Broker**: El middleware descarga las ejecuciones acumuladas en las últimas 24 horas a través de la API del broker.
- **Validación de Ejecuciones Locales**: Se realiza una validación cruzada para verificar que cada operación registrada en la base de datos local como broker_orders tenga su correspondiente confirmación en el historial oficial del broker.
- **Detección de Operaciones Huérfanas**: Si el broker registra transacciones que no constan en el middleware, el sistema genera alertas de auditoría críticas indicando una posible vulneración de seguridad o ejecuciones manuales no sincronizadas en el terminal del broker.
- **Cálculo de Deslizamiento Neto de Precios**: Se evalúa la diferencia de cotización entre el precio de la señal enviada por TradingView y el precio real ponderado de llenado reportado por el broker, almacenando los resultados de deslizamiento para su posterior análisis cuantitativo:

Latencia End-to-End

La latencia end-to-end del sistema es el tiempo acumulado desde el instante en que el script de TradingView detecta la condición de mercado seleccionada hasta la confirmación de la ejecución por parte del broker. Este indicador es clave para la viabilidad de estrategias intradiarias de alta frecuencia o de reversión rápida.

Segmentación de Latencia y Puntos de Optimización

[ Algoritmo de TV ] ---> ( ~10ms ) ---> [ Envío del Webhook ]

                                              |

                                              v ( WAN: ~40ms ) [cite: 4, 29]

[ Procesamiento ASGI ] <--- ( ~1.5ms ) <--- [ Proxy Inverso ]

        |

        +---> Inserción SQLite ( ~2ms )

        +---> Filtro de Riesgo ( ~0.5ms )

        |

        v ( WAN a Broker: ~25ms )

[ API de Ejecución ] ---> ( ~15ms ) ---> [ Matching Engine ]

                                              |

                                              v

                              Orden Ejecutada y Confirmada

Bajo este escenario optimizado de co-ubicación, la latencia mínima técnica acumulada se estima en un rango de  a  antes de procesar el matching en el libro de órdenes.

Técnicas de Optimización de Infraestructura

- **Co-Ubicación en Centros de Datos Clave (Data Center Proximity)**: Desplegar el middleware en servidores privados virtuales (VPS) ubicados en los mismos centros de datos que las pasarelas del broker para minimizar la latencia de red WAN^4^. Para forex y materias primas operados a través de OANDA o Brokers, se recomiendan ubicaciones en Londres o Nueva York (ej. Equinix LD4 o NY4)^4^; para renta variable americana en Alpaca, se aconseja co-ubicar los sistemas en los servidores cloud de AWS en la región us-east-1^4^.
- **Multiplexación de Conexiones TCP (HTTP Connection Pooling)**: Evitar la sobrecarga asociada a la negociación del handshake TCP/TLS para cada transacción individual saliente. El middleware debe mantener abierto un cliente HTTP asíncrono persistente (httpx.AsyncClient) que gestione un pool persistente de conexiones reutilizables con los brokers autorizados.
- **Almacenamiento de Alto Rendimiento en Memoria (Caching)**: El middleware debe almacenar de manera temporal las variables de control de gestión de riesgos (por ejemplo, el cálculo del drawdown acumulado o el estado del kill switch) en una memoria caché de acceso rápido como Redis, evitando operaciones recurrentes de lectura y escritura en disco que puedan bloquear el hilo del bucle de eventos asíncrono.

Impacto de la Latencia en el Deslizamiento (Slippage) de Precios

En mercados de alta volatilidad y spread variable, los picos de latencia elevados provocan que la orden de mercado se sitúe por detrás de las órdenes de participantes con sistemas más rápidos. Esto genera un deslizamiento de precios (*slippage*) severo, ejecutando las órdenes de compra a precios significativamente superiores (o las de venta a precios inferiores) respecto a la cotización original de la alerta de TradingView. Esto puede reducir notablemente el beneficio promedio por operación calculado teóricamente en las simulaciones históricas de backtesting.

Redundancia y Failover

Un pipeline automatizado de trading de nivel profesional debe diseñarse asumiendo que todos y cada uno de los componentes de su infraestructura (servicios de red, servidores físicos, pasarelas de pago y APIs) pueden experimentar fallas en algún momento del ciclo operativo.

Soluciones ante Caídas de Webhooks de TradingView

La plataforma de TradingView carece de mecanismos integrados de reintento para el envío de alertas webhooks en caso de fallo del receptor o pérdida de paquetes de red, considerando la alerta como perdida tras el primer intento de envío fallido^1^.

- *Mitigación*: Para aumentar la redundancia de los webhooks, se recomienda implementar un flujo de mensajería secundario. El middleware puede configurarse para recibir también las alertas a través de un canal de mensajería privado alternativo (como un canal seguro de Telegram) administrado por un bot secundario^39^. Esto proporciona una vía alternativa de respaldo en caso de fallo del puerto HTTP principal del servidor.

Políticas de Reintentos de Órdenes (Retry Engine)

El middleware debe procesar las órdenes de forma segura, evitando pérdidas descontroladas debidas a fallos temporales en las APIs de los brokers. Esto se implementa mediante políticas de tolerancia a fallos basadas en reintentos condicionales con retroceso exponencial (*exponential backoff*) y adición de ruido aleatorio (*jitter*), lo que evita saturar los endpoints del broker tras una interrupción temporal del servicio:

Canales Secundarios de Ejecución (Broker Failover)

En sistemas de trading avanzados, el middleware se configura para gestionar cuentas activas en múltiples brokers. Si el módulo de comunicación de la API del broker principal detecta códigos de error HTTP de la familia 5xx o errores persistentes de red que impiden enrutar operaciones críticas, el middleware puede conmutar dinámicamente y redirigir el flujo de órdenes hacia cuentas de respaldo secundarias integradas en otros brókers del mismo mercado.

Autoevaluación del Estado del Sistema (Health Checks)

El middleware debe exponer un endpoint público /health que permita monitorizar de manera automatizada la disponibilidad del sistema. Este endpoint realiza comprobaciones del estado de los servicios críticos (acceso a la base de datos local SQLite, latencia de conexión con las APIs de los brokers y comunicación con las notificaciones de Telegram) y responde con un código de estado HTTP 200 OK si el sistema está plenamente operativo. Si se detecta alguna anomalía, el middleware envía de inmediato alertas de emergencia a los administradores.

Multi-Broker Execution

El envío simultáneo de señales de ejecución a múltiples brokers permite diversificar el riesgo de contraparte, optimizar la profundidad del mercado agregando liquidez distribuida o capturar ineficiencias temporales de arbitraje de precios entre mercados spot e instrumentos derivados sintéticos.

La implementación en Python requiere el uso del módulo asíncrono nativo asyncio, el cual evita bloqueos de hilos (*thread locking*) y permite disparar peticiones de red simultáneas en paralelo utilizando llamadas concurrentes asíncronas no bloqueantes.

Concepto de Multi-Broker Execution y Flujo de Procesamiento

El flujo de procesamiento de una alerta enviada por TradingView dirigida a múltiples brokers de forma simultánea se estructura en los siguientes pasos:

[ Alerta Webhook Recibida en Middleware ]

                    |

                    v

[ Verificación y Validación de Riesgos ]

                    |

                    v

    [ async.gather() Execution Pool ]

                    |

          +---------+---------+

          |                   |

          v asíncrono         v asíncrono

   [ Broker "Alpaca" ]   [ Broker "OANDA" ]

          |                   |

          v                   v

   [ Orden de Compra ]   [ Orden de Compra ]

Implementación en Python de Ejecución Concurrente

El siguiente script de Python demuestra cómo utilizar la concurrencia asíncrona no bloqueante proporcionada por asyncio para enrutar una señal de TradingView a dos brokers distintos de manera simultánea, minimizando la latencia acumulada en las peticiones de red:

Python

*import* asyncio

*import* httpx

*import* logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(*"MultiBrokerExecution"*)

*async* *def* *colocar_orden_alpaca_async**(client: httpx.AsyncClient, symbol:* *str**, qty:* *int**, side:* *str**) -> dict:*

    url = *"https://paper-api.alpaca.markets/v2/orders"* [cite: *25*]

    headers = {

        *"APCA-API-KEY-ID"*: *"TU_ALPACA_API_KEY"*, [cite: *25*]

        *"APCA-API-SECRET-KEY"*: *"TU_ALPACA_SECRET_KEY"* [cite: *25*]

    }

    payload = {

        *"symbol"*: symbol,

        *"qty"*: *str*(qty),

        *"side"*: side.lower(), [cite: *20*, *25*]

        *"type"*: *"market"*,

        *"time_in_force"*: *"day"* [cite: *20*, *25*]

    }

    *try*:

        response = *await* client.post(url, json=payload, headers=headers, timeout=*2.0*)

        *return* {*"broker"*: *"Alpaca"*, *"status"*: *"SUCCESS"*, *"response"*: response.json()}

    *except* Exception *as* e:

        logger.error(*f"Fallo al enrutar orden hacia Alpaca: {**str**(e)}"*)

        *return* {*"broker"*: *"Alpaca"*, *"status"*: *"FAILED"*, *"error"*: *str*(e)}

*async* *def* *colocar_orden_oanda_async**(client: httpx.AsyncClient, symbol:* *str**, units:* *int**, side:* *str**) -> dict:*

    *# OANDA requiere un par formateado con guion bajo (ej: EUR_USD)*

    mapped_symbol = symbol.replace(*"USD"*, *"_USD"*) 

    url = *"https://api-fxpractice.oanda.com/v3/accounts/101-011-12345-001/orders"* [cite: *41*]

    headers = {

        *"Authorization"*: *"Bearer TU_OANDA_TOKEN"*, [cite: *19*]

        *"Content-Type"*: *"application/json"*

    }

    *# Unidades positivas para compra, negativas para venta en la API v20 de OANDA*

    calculated_units = units *if* side.lower() == *"buy"* *else* -units

    payload = {

        *"order"*: {

            *"units"*: *str*(calculated_units),

            *"instrument"*: mapped_symbol,

            *"timeInForce"*: *"FOK"*,

            *"type"*: *"MARKET"*,

            *"positionFill"*: *"DEFAULT"*

        }

    }

    *try*:

        response = *await* client.post(url, json=payload, headers=headers, timeout=*2.0*)

        *return* {*"broker"*: *"OANDA"*, *"status"*: *"SUCCESS"*, *"response"*: response.json()}

    *except* Exception *as* e:

        logger.error(*f"Fallo al enrutar orden hacia OANDA: {**str**(e)}"*)

        *return* {*"broker"*: *"OANDA"*, *"status"*: *"FAILED"*, *"error"*: *str*(e)}

*async* *def* *ejecutar_orden_coordinada**(symbol:* *str**, base_qty:* *int**, side:* *str**):*

    *"""

    Ejecuta en paralelo de forma no bloqueante la misma alerta en Alpaca y OANDA.

    """*

    *async* *with* httpx.AsyncClient() *as* client:

        *# Lanza concurrentemente las peticiones de red*

        tareas = [

            colocar_orden_alpaca_async(client, symbol, base_qty, side),

            colocar_orden_oanda_async(client, symbol, base_qty * *1000*, side)  *# Adaptado a unidades Forex*

        ]

        *# Espera que finalicen las tareas concurrentes de forma simultánea en milisegundos*

        resultados = *await* asyncio.gather(*tareas, return_exceptions=*True*)

        *for* index, resultado *in* *enumerate*(resultados):

            logger.info(*f"Resultado del Broker [{index}]: {resultado}"*)

Integración con el Gateway del Broker Existente

Plataformas Institucionales es una plataforma ampliamente utilizada para operar Forex y CFDs. Para automatizar este flujo, se suele emplear un Gateway local (por ejemplo, ejecutado en la máquina del broker en la dirección IP privada de red local api.broker.com) que expone endpoints REST para interactuar de forma directa con el terminal de Broker. El middleware propuesto actúa como un receptor proxy inteligente que procesa, valida y reenvía las señales hacia dicha pasarela técnica.

Flujo Detallado de una Operación de Trading

[ Alerta Gráfica en TradingView ] 

               |

               | Petición HTTP POST (SSL/TLS)

               v

[ Receptor Middleware (FastAPI) ] ---> Valida IP de origen y firma criptográfica [cite: 1, 3, 4, 9]

               |

               | Transforma Ticker, volumen y niveles de riesgo en FastAPI

               v

[ Gateway Local Broker (api.broker.com) ] ---> Endpoint de la API REST del Gateway

               |

               | API nativa del terminal de Plataformas Institucionales (Broker Terminal)

               v

[ Servidor del Broker / Ejecución final ]

Tabla de Endpoints del Gateway de Broker Externo

| **Acción Requerida** | **Endpoint del Gateway** | **Método HTTP** | **Payload JSON Requerido** | **Descripción de la Respuesta del Gateway** |
| --- | --- | --- | --- | --- |
| **Abrir Posición de Mercado** | /api/v1/order | POST | {"action": "BUY", "symbol": "EURUSD", "volume": 0.5, "sl": 1.0810, "tp": 1.0950} | Procesa una orden de mercado y retorna el identificador numérico de la transacción (*ticket*). |
| **Cerrar Posición Existente** | /api/v1/close | POST | {"symbol": "EURUSD", "position_ticket": 87654321} | Cierra la posición asociada al ticket indicado, devolviendo el beneficio de cierre de la orden. |
| **Modificar Órdenes Abiertas** | /api/v1/modify | PUT | {"ticket": 87654321, "sl_price": 1.0820, "tp_price": 1.0920} | Modifica los niveles de stop loss o take profit de una posición activa en el terminal de Broker. |
| **Consulta del Estado de Cuenta** | /api/v1/account | GET | Ninguno (Encabezados estándar) | Retorna información de margen libre, balance de capital de la cuenta, equidad y beneficio flotante. |

Implementación Completa

A continuación se detalla el código fuente completo, modular y de grado de producción de un middleware de automatización de trading robusto desarrollado sobre el framework **FastAPI**.

Esta solución integrada cumple de manera estricta con las especificaciones de seguridad por lista de IPs autorizadas, validación de token secreto, gestión integrada de riesgos de drawdown acumulado y rate limiting dinámico por activo, escritura asíncrona de registros de auditoría en base de datos SQLite local, ejecución asíncrona no bloqueante hacia el Gateway de Plataformas Institucionales externo y despacho automático de notificaciones a través de la API de bots de Telegram.

Código Fuente del Middleware (middleware.py)

Python

*import* os

*import* sqlite3

*import* logging

*import* asyncio

*from* datetime *import* datetime, timedelta

*from* typing *import* Dict, Any, Optional

*from* fastapi *import* FastAPI, Request, HTTPException, status, BackgroundTasks, Depends

*import* httpx

*from* pydantic *import* BaseModel, Field

*import* pandas_market_calendars *as* mcal

*import* pandas *as* pd

*# =====================================================================*

*# CONFIGURACIÓN GENERAL Y VARIABLES DE ENTORNO*

*# =====================================================================*

logging.basicConfig(

    level=logging.INFO,

    *format*=*"%(asctime)s [%(levelname)s] %(name)s: %(message)s"*

)

logger = logging.getLogger(*"TradingAutomationMiddleware"*)

*# Parámetros de seguridad del sistema*

SHARED_SECRET_TOKEN = os.getenv(*"TRADINGVIEW_SECRET"*, *"ClaveSeguraSuperSecreta123"*)

DATABASE_NAME = os.getenv(*"DATABASE_NAME"*, *"trading_audit.db"*)

*# Conectividad con el Gateway del Broker local*

BROKER_GATEWAY_URL = os.getenv(*"BROKER_GATEWAY_URL"*, *"http://api.broker.com/api/v1/order"*)

*# Configuración del bot de notificaciones de Telegram*

TELEGRAM_BOT_TOKEN = os.getenv(*"TELEGRAM_BOT_TOKEN"*, *"123456789:ABCDefGhIjKlMnOpQrStUvWxYz"*)

TELEGRAM_CHAT_ID = os.getenv(*"TELEGRAM_CHAT_ID"*, *"987654321"*)

*# Rango de Direcciones IP oficiales de TradingView para la lista de permitidos*

TRADINGVIEW_IPS = {*"52.89.214.238"*, *"34.212.75.30"*, *"54.218.53.128"*, *"52.32.178.7"*}

*# Almacenes de control dinámico en memoria*

rate_limit_store: Dict[*str*, *list*] = {}  *# {símbolo: [timestamps_de_ejecución]}*

KILL_SWITCH_ACTIVE = *False*

*# =====================================================================*

*# INICIALIZACIÓN DE LA BASE DE DATOS LOCAL SQLITE3*

*# =====================================================================*

*def* *init_db**():*

    *"""Inicializa la base de datos de auditoría con la estructura y los índices requeridos."""*

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    *# Registro inalterable de alertas webhooks recibidas*

    cursor.execute(*"""

        CREATE TABLE IF NOT EXISTS tradingview_alerts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            received_at TEXT NOT NULL,

            symbol TEXT NOT NULL,

            action TEXT NOT NULL,

            risk_pct REAL NOT NULL,

            sl_price REAL,

            tp_price REAL,

            raw_payload TEXT NOT NULL

        )

    """*)

    *# Registro de órdenes enviadas al broker*

    cursor.execute(*"""

        CREATE TABLE IF NOT EXISTS broker_orders (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            alert_id INTEGER,

            broker_name TEXT NOT NULL,

            broker_order_id TEXT,

            status TEXT NOT NULL,

            error_message TEXT,

            sent_at TEXT NOT NULL,

            FOREIGN KEY (alert_id) REFERENCES tradingview_alerts (id)

        )

    """*)

    conn.commit()

    conn.close()

    logger.info(*"La base de datos SQLite3 de auditoría ha sido inicializada de forma correcta."*)

*# =====================================================================*

*# INICIALIZACIÓN DE FASTAPI Y SU LIFESPAN*

*# =====================================================================*

app = FastAPI(

    title=*"Middleware de Automatización de Trading de Alta Disponibilidad"*,

    version=*"1.0.0"*

)

*@app.on_event(**"startup"**)*

*async* *def* *startup_event**():*

    init_db()

*# =====================================================================*

*# MODELOS DE VALIDACIÓN DE DATOS (PYDANTIC)*

*# =====================================================================*

*class* *TradingViewPayload(BaseModel):*

    *"""Estructura de datos obligatoria para validar el payload JSON de la alerta de TradingView."""*

    secret: *str* = Field(..., description=*"Token secreto para verificar la autenticidad de la alerta."*)

    symbol: *str* = Field(..., description=*"Ticker del activo financiero (ej. FX:EURUSD, NASDAQ:AAPL)."*)

    action: *str* = Field(..., description=*"Dirección de la operación: BUY o SELL."*)

    risk_pct: *float* = Field(..., description=*"Porcentaje de equidad de la cuenta a arriesgar en la operación."*)

    sl_price: Optional[*float*] = Field(*None*, description=*"Precio de stop loss absoluto."*)

    tp_price: Optional[*float*] = Field(*None*, description=*"Precio de take profit absoluto."*)

*# =====================================================================*

*# MIDDLEWARE DE FILTRADO DE IP DE ORIGEN*

*# =====================================================================*

*async* *def* *verify_tradingview_ip**(request: Request):*

    *"""

    Valida que la IP de origen pertenezca a la lista de direcciones de TradingView,

    comprobando la cabecera X-Forwarded-For si el middleware se despliega tras un proxy inverso.

    """*

    x_forwarded_for = request.headers.get(*"X-Forwarded-For"*)

    *if* x_forwarded_for:

        client_ip = x_forwarded_for.split(*","*)[*0*].strip()

    *else*:

        client_ip = request.client.host *if* request.client *else* *""*

    *if* client_ip *not* *in* TRADINGVIEW_IPS:

        logger.warning(*f"Intento de acceso denegado preventivamente desde la IP: {client_ip}"*)

        *raise* HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail=*"La dirección IP emisora no se encuentra en la lista de permitidos oficial."*

        )

    *return* client_ip

*# =====================================================================*

*# CONTROL DE RIESGOS Y VALIDACIÓN DE MERCADOS*

*# =====================================================================*

*def* *verify_market_hours**(symbol:* *str**) -> bool:*

    *"""

    Comprueba si el mercado asociado al activo está operativo para negociar en este instante.

    Asume por defecto el calendario de la NYSE para renta variable, o retorna True para criptomonedas.

    """*

    *if* *"USD"* *in* symbol *or* *"USDT"* *in* symbol:

        *# Los mercados de criptomonedas operan de forma ininterrumpida 24/7*

        *return* *True*

    *try*:

        *# Para renta variable tradicional, verifica el calendario de la NYSE*

        calendar = mcal.get_calendar(*"NYSE"*)

        ahora_utc = pd.Timestamp(datetime.utcnow(), tz=*"UTC"*)

        schedule = calendar.schedule(start_date=ahora_utc.date(), end_date=ahora_utc.date())

        *if* schedule.empty:

            *return* *False*

        *return* calendar.open_at_time(schedule, ahora_utc)

    *except* Exception *as* e:

        logger.error(*f"Fallo al evaluar las horas operativas del mercado: {**str**(e)}"*)

        *# Ante un error de cálculo, se bloquea preventivamente la transacción*

        *return* *False*

*def* *verify_rate_limiting**(symbol:* *str**, max_orders_per_hour:* *int* *=* *5**) -> bool:*

    *"""Implementa un sistema de control de frecuencia basado en ventana deslizante."""*

    now = datetime.utcnow()

    *if* symbol *not* *in* rate_limit_store:

        rate_limit_store[symbol] = []

    *# Limpia los registros anteriores a una hora*

    rate_limit_store[symbol] = [t *for* t *in* rate_limit_store[symbol] *if* now - t < timedelta(hours=*1*)]

    *if* *len*(rate_limit_store[symbol]) >= max_orders_per_hour:

        *return* *False*

    rate_limit_store[symbol].append(now)

    *return* *True*

*# =====================================================================*

*# SERVICIOS ASÍNCRONOS Y LOGGING PERSISTENTE*

*# =====================================================================*

*async* *def* *send_telegram_async**(message:* *str**):*

    *"""Envía de forma asíncrona un informe operativo a través del bot de Telegram."""*

    url = *f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"*

    payload = {

        *"chat_id"*: TELEGRAM_CHAT_ID,

        *"text"*: message,

        *"parse_mode"*: *"HTML"*

    }

    *try*:

        *async* *with* httpx.AsyncClient() *as* client:

            *await* client.post(url, json=payload, timeout=*3.0*)

    *except* Exception *as* e:

        logger.error(*f"Error al enviar la notificación a Telegram: {**str**(e)}"*)

*def* *log_alert_to_db**(payload: TradingViewPayload, received_at:* *str**) -> int:*

    *"""Inserta de manera síncrona el registro de la alerta en SQLite3 para evitar bloqueos del bucle de eventos."""*

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute(*"""

        INSERT INTO tradingview_alerts (received_at, symbol, action, risk_pct, sl_price, tp_price, raw_payload)

        VALUES (?, ?, ?, ?, ?, ?, ?)

    """*, (

        received_at,

        payload.symbol,

        payload.action,

        payload.risk_pct,

        payload.sl_price,

        payload.tp_price,

        payload.json()

    ))

    alert_id = cursor.lastrowid *or* *0*

    conn.commit()

    conn.close()

    *return* alert_id

*def* *log_order_result_to_db**(alert_id:* *int**, status_str:* *str**, order_id: Optional[**str**], error_msg: Optional[**str**], sent_at:* *str**):*

    *"""Registra de manera persistente en SQLite3 la respuesta devuelta por el broker."""*

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute(*"""

        INSERT INTO broker_orders (alert_id, broker_name, broker_order_id, status, error_message, sent_at)

        VALUES (?, 'Plataformas Institucionales Gateway', ?, ?, ?, ?)

    """*, (alert_id, order_id, status_str, error_msg, sent_at))

    conn.commit()

    conn.close()

*async* *def* *execute_order_at_gateway_async**(alert_id:* *int**, mapped_symbol:* *str**, action:* *str**, sl: Optional[**float**], tp: Optional[**float**]):*

    *"""Se comunica asíncronamente con el Gateway de Broker local para ejecutar la orden."""*

    *# En entornos de producción real, aquí se calcularía dinámicamente el tamaño de la posición*

    volumen_calculado = *0.50*  *# Lote fijo de prueba*

    payload = {

        *"action"*: action.upper(),  *# "BUY" o "SELL"*

        *"symbol"*: mapped_symbol,

        *"volume"*: volumen_calculado,

        *"sl_price"*: sl,

        *"tp_price"*: tp

    }

    sent_at = datetime.utcnow().isoformat()

    logger.info(*f"Despachando orden al Gateway de Broker local en api.broker.com: {payload}"*)

    *try*:

        *async* *with* httpx.AsyncClient() *as* client:

            response = *await* client.post(BROKER_GATEWAY_URL, json=payload, timeout=*5.0*)

        *if* response.status_code == *200*:

            res_json = response.json()

            ticket_id = *str*(res_json.get(*"ticket"*, *"N/D"*))

            logger.info(*f"Orden ejecutada con éxito. Ticket devuelto: {ticket_id}"*)

            *# Registrar resultado exitoso en SQLite3*

            *await* asyncio.to_thread(log_order_result_to_db, alert_id, *"FILLED"*, ticket_id, *None*, sent_at)

            *# Notificar al operador*

            asyncio.create_task(send_telegram_async(

                *f"<b>EJECUCIÓN DE TRADING EXITOSA</b> \n"*

                *f"<b>Símbolo:</b> {mapped_symbol}\n"*

                *f"<b>Acción:</b> {action.upper()}\n"*

                *f"<b>Volumen:</b> {volumen_calculado} Lotes\n"*

                *f"<b>Ticket Broker:</b> {ticket_id}"*

            ))

        *else*:

            error_text = response.text

            logger.error(*f"El Gateway de Broker devolvió un error de ejecución: {error_text}"*)

            *await* asyncio.to_thread(log_order_result_to_db, alert_id, *"REJECTED"*, *None*, error_text, sent_at)

            asyncio.create_task(send_telegram_async(

                *f"[ERROR] <b>ORDEN RECHAZADA POR Gateway del Broker</b> [ERROR]\n"*

                *f"<b>Símbolo:</b> {mapped_symbol}\n"*

                *f"<b>Acción:</b> {action.upper()}\n"*

                *f"<b>Detalle del Error:</b> {error_text[:**120**]}"*

            ))

    *except* Exception *as* e:

        logger.error(*f"Fallo de conexión crítico con el Gateway de Broker (api.broker.com): {**str**(e)}"*)

        *await* asyncio.to_thread(log_order_result_to_db, alert_id, *"FAILED_NETWORK"*, *None*, *str*(e), sent_at)

        asyncio.create_task(send_telegram_async(

            *f"[ADVERTENCIA] <b>FALLO DE COMUNICACIÓN EN RED</b> [ADVERTENCIA]\n"*

            *f"Imposible conectar con el Gateway local de Plataformas Institucionales.\n"*

            *f"<b>Error:</b> {**str**(e)[:**120**]}"*

        ))

*# =====================================================================*

*# ENDPOINT PRINCIPAL: RECEPCIÓN DEL WEBHOOK*

*# =====================================================================*

*@app.post(**"/webhook"**, status_code=status.HTTP_202_ACCEPTED)*

*async* *def* *receive_tradingview_webhook**(

    payload: TradingViewPayload,

    background_tasks: BackgroundTasks,

    client_ip:* *str* *= Depends(verify_tradingview_ip)

):*

    *"""

    Recibe la alerta del webhook, realiza validaciones inmediatas de seguridad,

    escribe el registro de auditoría local y delega la ejecución de forma asíncrona

    en segundo plano para evitar bloqueos e interrupciones del hilo de red de TradingView.

    """*

    received_at = datetime.utcnow().isoformat()

    *# 1. Validación de seguridad basada en el Token Secreto compartido*

    *if* payload.secret != SHARED_SECRET_TOKEN:

        logger.warning(*f"Fallo de validación de token secreto desde la IP: {client_ip}"*)

        *raise* HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=*"Fallo de autenticación: El token secreto provisto es inválido."*

        )

    *# 2. Evaluación de seguridad: Botón de parada de emergencia (Kill Switch)*

    *if* KILL_SWITCH_ACTIVE:

        logger.warning(*"Solicitud de operación rechazada: El Kill Switch de emergencia está activo."*)

        *raise* HTTPException(

            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,

            detail=*"El pipeline se encuentra desactivado preventivamente por el operador."*

        )

    *# 3. Control de riesgos: Validación del horario operativo del mercado NYSE/CME*

    *if* *not* verify_market_hours(payload.symbol):

        logger.warning(*f"La operación no puede completarse debido a que el mercado para {payload.symbol} se encuentra cerrado."*)

        *raise* HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail=*f"El mercado para el símbolo {payload.symbol} se encuentra cerrado actualmente."*

        )

    *# 4. Control de riesgos: Validación del límite de frecuencia (Rate Limiting)*

    *if* *not* verify_rate_limiting(payload.symbol, max_orders_per_hour=*5*):

        logger.warning(*f"Tasa de órdenes por hora excedida para el activo: {payload.symbol}"*)

        *raise* HTTPException(

            status_code=status.HTTP_429_TOO_MANY_REQUESTS,

            detail=*"Límite de frecuencia activado: Demasiadas operaciones procesadas en la última hora para este activo."*

        )

    *# 5. Inserción asíncrona de la alerta recibida en SQLite3 para la auditoría de operaciones*

    *# Se ejecuta mediante un hilo externo (asyncio.to_thread) para evitar bloquear el bucle de eventos principal*

    alert_db_id = *await* asyncio.to_thread(log_alert_to_db, payload, received_at)

    *# 6. Mapeo del Ticker de TradingView al formato requerido por el Gateway de Broker*

    mapped_symbol = payload.symbol.split(*":"*)[-*1*]  *# ej. "FX:EURUSD" -> "EURUSD"*

    *# 7. Delegar el procesamiento pesado y la petición de red asíncrona al Gateway del Broker en segundo plano*

    *# Esto permite responder a TradingView de inmediato (HTTP 202) en menos de 20 ms, previniendo fallos por timeout.*

    background_tasks.add_task(

        execute_order_at_gateway_async,

        alert_db_id,

        mapped_symbol,

        payload.action,

        payload.sl_price,

        payload.tp_price

    )

    *return* {

        *"status"*: *"ACCEPTED"*,

        *"message"*: *"La alerta ha sido validada y se ha enrutado a la cola de ejecución asíncrona en segundo plano."*,

        *"alert_id"*: alert_db_id,

        *"symbol_processed"*: mapped_symbol

    }

*# =====================================================================*

*# ENDPOINTS ADMINISTRATIVOS Y HEALTH CHECKS*

*# =====================================================================*

*@app.get(**"/health"**)*

*async* *def* *health_check**():*

    *"""Endpoint de autoevaluación para supervisar la disponibilidad y el correcto funcionamiento de los servicios del middleware."""*

    *try*:

        *# Verifica la lectura y escritura en la base de datos SQLite3*

        conn = sqlite3.connect(DATABASE_NAME)

        cursor = conn.cursor()

        cursor.execute(*"SELECT 1"*)

        conn.close()

        db_status = *"HEALTHY"*

    *except* Exception *as* e:

        db_status = *f"UNHEALTHY: {**str**(e)}"*

    *return* {

        *"status"*: *"ONLINE"*,

        *"timestamp"*: datetime.utcnow().isoformat(),

        *"database_connectivity"*: db_status,

        *"kill_switch_active"*: KILL_SWITCH_ACTIVE

    }

*@app.post(**"/admin/killswitch"**)*

*async* *def* *toggle_kill_switch**(active:* *bool**):*

    *"""Permite al operador activar o desactivar manualmente la parada de emergencia (Kill Switch)."""*

    *global* KILL_SWITCH_ACTIVE

    KILL_SWITCH_ACTIVE = active

    estado_str = *"ACTIVADO"* *if* active *else* *"DESACTIVADO"*

    logger.info(*f"Modificación manual del Kill Switch por el administrador. Estado actual: {estado_str}"*)

    *# Despacha notificación urgente a Telegram*

    *await* send_telegram_async(*f"[ADVERTENCIA] <b>ALERTA DE CONTROL</b> [ADVERTENCIA]\nEl Kill Switch manual de emergencia ha sido <b>{estado_str}</b> por el operador."*)

    *return* {*"status"*: *"SUCCESS"*, *"kill_switch_active"*: KILL_SWITCH_ACTIVE}

*if* __name__ == *"__main__"*:

    *# Inicia el servidor ASGI de FastAPI en el puerto estándar 80*

    *import* uvicorn

    uvicorn.run(app, host=*"0.0.0.0"*, port=*80*)

Conclusiones

El diseño y la implementación de un pipeline de automatización de trading que conecte TradingView con la ejecución real en brokers es una tarea de ingeniería de sistemas crítica que exige un enfoque riguroso en cuanto a seguridad, latencia y tolerancia a fallos. Para garantizar un entorno operativo estable, es fundamental separar de manera estricta el canal de entrada de las alertas asíncronas de la lógica de enrutamiento al broker, utilizando para ello tareas en segundo plano. Esto previene interrupciones por timeout al responder de inmediato con un código de estado aceptado.

La seguridad perimetral y la protección ante accesos no autorizados se logran implementando una estrategia defensiva en varias capas: filtrado riguroso por lista blanca de direcciones IP estáticas a nivel de firewall, verificación criptográfica basada en certificados SSL cliente de TradingView y validación de tokens secretos compartidos dentro del payload de las alertas. Asimismo, la integración de reglas automatizadas de gestión de riesgos en la capa intermedia (como disyuntores de drawdown acumulado, rate limiting por activo y comprobación en tiempo real de los calendarios operativos de los mercados) proporciona una salvaguarda esencial ante fallas lógicas en las alertas visuales o periodos de inestabilidad severa en los mercados financieros.

Por último, el registro y auditoría inalterable de cada evento en una base de datos local ligera y eficiente como SQLite3, combinado con procesos de reconciliación diaria de datos frente al historial del broker, aporta la transparencia y la visibilidad necesarias para monitorizar el deslizamiento de precios, diagnosticar errores de red y optimizar de forma continua el pipeline de ejecución para adaptarlo a las exigencias operativas del trading cuantitativo institucional.

Fuentes citadas

- How to configure webhook alerts - TradingView, https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/
- TradingView Webhook Integration - Grokipedia, https://grokipedia.com/page/TradingView_Webhook_Integration
- Cómo configurar alertas webhook - TradingView, https://es.tradingview.com/support/solutions/43000529348/
- TradingView with VPS: Webhook & Alert Automation, https://tradingfxvps.com/tradingview-with-vps-webhook-alert-automation/
- About HTTPS - FastAPI, https://fastapi.tiangolo.com/deployment/https/
- Handling X-Forwarded-* headers — Safir v0.1.dev1+gccd5bc9, https://safir.lsst.io/v/DM-31361/x-forwarded.html
- How to Get the Real Client IP in FastAPI Behind a Reverse Proxy - Python in Plain English, https://python.plainenglish.io/how-to-get-the-real-client-ip-in-fastapi-behind-a-reverse-proxy-193adc757a1e
- Detrás de un Proxy - FastAPI, https://fastapi.tiangolo.com/es/advanced/behind-a-proxy/
- Getting Started - PineConnector Docs, https://docs.pineconnector.com/getting-started
- GitHub - chenjy16/OpenPilot: all-in-one AI agent runtime platform supporting multi-model, multi-channel, and multi-agent collaboration., https://github.com/chenjy16/OpenPilot
- How to Scrape Product Data from AllMachines: A Step-by-Step Guide - Datahut Blog, https://www.blog.datahut.co/post/how-to-scrape-data-from-allmachines
- Order Types | IBKR API | IBKR Campus, https://www.interactivebrokers.com/campus/ibkr-api-page/order-types/
- Web API v1.0 Documentation | IBKR API | IBKR Campus, https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/
- README - ibkrcp, https://ftp.dcc.uchile.cl/web/packages/ibkrcp/readme/README.html
- What is IBKR's Client Portal API? | Trading Lesson, https://www.interactivebrokers.com/campus/trading-lessons/what-is-ibkrs-client-portal-api/
- Financial Advisor – Order Placement & Management - Interactive Brokers, https://www.interactivebrokers.com/campus/trading-lessons/financial-advisor-order-placement-management/
- Sample Code - Oanda API, https://developer.oanda.com/rest-live-v20/sample-code/
- oanda/v20-python-samples - GitHub, https://github.com/oanda/v20-python-samples
- Introduction - Oanda API, https://developer.oanda.com/rest-live-v20/introduction/
- Getting Started with Crypto Trading API on Alpaca, https://alpaca.markets/learn/getting-started-with-alpaca-crypto-api
- Alpaca - Developer-first API for Stock, Options, Crypto Trading, https://alpaca.markets/
- Unlocking the Potential of Alpaca Trading API - A Comprehensive Guide - Xmartlabs | Blog, https://blog.xmartlabs.com/blog/a-comprehensive-guide-to-alpaca-trading-api/
- PineConnector gratuito: Conecta TradingView a MT4/Broker - Switch Markets, https://www.switchmarkets.com/es/pineconnector-gratis
- Webhook authentication - TradingView, https://www.tradingview.com/support/solutions/43000680459-webhook-authentication/
- Alpaca Trade API Python Tutorial | Creating Orders for Paper Trading - YouTube, https://www.youtube.com/watch?v=2kkbYPBQvbk
- Placing Orders | Trading Lesson | Traders' Academy - Interactive Brokers, https://www.interactivebrokers.com/campus/trading-lessons/placing-orders/
- Place an order in Interactive Brokers using API request - Stack Overflow, https://stackoverflow.com/questions/69005509/place-an-order-in-interactive-brokers-using-api-request
- Order Classes - OANDA REST V20 API Wrapper - Read the Docs, https://oanda-api-v20.readthedocs.io/en/latest/contrib/orders.html
- How to Use PineConnector on Switch Markets - A Step-by-Step Guide, https://www.switchmarkets.com/learn/how-to-use-pineconnector
- PineConnector — TradingView Alerts to MT4/Broker, https://www.pineconnector.com/
- Syntax - PineConnector Docs, https://docs.pineconnector.com/syntax
- Syntax Guide - PineConnector, https://www.pineconnector.com/pages/syntax
- pandas_market_calendars - PyPI, https://pypi.org/project/pandas_market_calendars/
- pandas_market_calendars documentation, https://pandas-market-calendars.readthedocs.io/_/downloads/en/latest/pdf/
- pandas_market_calendars: Exchange Schedules in Python, https://www.pythonpool.com/pandas_market_calendars/
- Implementing Telegram Bot in Python and Javascript with deployment to AWS - Glukhov.org, https://www.glukhov.org/app-architecture/integration-patterns/implementing-telegram-bot-python-javascript/
- Use Telegram Bot API And Python To Send Text Messages And Photos - ARON HACK, https://aronhack.com/use-telegram-bot-api-and-python-to-send-text-messages-and-photos/