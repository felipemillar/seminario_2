Análisis Técnico de Ingeniería Inversa del Protocolo WebSocket No Oficial de TradingView para la Ingesta de Datos en Tiempo Real

El acceso eficiente a los datos de mercado en tiempo real es una necesidad crítica para el desarrollo de infraestructuras de trading algorítmico de alto rendimiento. Para evitar la sobrecarga computacional y la inestabilidad de soluciones basadas en la automatización de navegadores (como Selenium) o de dependencias de terceros propensas a quedar obsoletas, se plantea la interacción directa con el canal seguro de WebSockets (WSS) utilizado por el cliente web oficial de TradingView^1^. El presente informe expone un desglose técnico exhaustivo del protocolo propietario de comunicación de la plataforma, detallando su infraestructura de red, la sintaxis de sus mensajes, el flujo de suscripción para gráficos y cotizaciones, el parseo de respuestas de mercado y la gestión avanzada del ciclo de vida de la conexión.

1. Arquitectura de Conexión y Negociación WSS

El canal bidireccional que soporta el flujo continuo de cotizaciones e históricos en TradingView se implementa sobre una variante optimizada y no documentada del protocolo de red Socket.io^2^. La pasarela principal de comunicación expone el siguiente endpoint seguro de WebSockets:

wss://data.tradingview.com/socket.io/websocket

El establecimiento de la conexión (handshake) se gestiona de forma directa mediante la promoción de una petición HTTP estándar al protocolo de WebSocket (Upgrade request)^4^. Sin embargo, la infraestructura perimetral del servidor valida rigurosamente los encabezados HTTP para mitigar el acceso no autorizado y prevenir abusos de API. La omisión de estos encabezados resulta sistemáticamente en un código de respuesta HTTP 403 Forbidden^3^.

| **Encabezado HTTP** | **Valor Técnico Requerido** | **Función dentro del Protocolo** |
| --- | --- | --- |
| Origin | https://www.tradingview.com | Requerido para superar las directivas CORS del balanceador de carga del servidor^4^. |
| User-Agent | Mozilla/5.0 (Windows NT 10.0; Win64; x64)... | Simula la firma de un agente de usuario legítimo (navegador moderno)^4^. |
| Cookie | sessionid=<token>; sessionid_sign=<firma> | (Opcional) Requerido únicamente para asociar la conexión a cuentas de pago y acceder a datos en tiempo real sin retardo^6^. |

Una vez promovida la conexión, a diferencia del estándar de Socket.io clásico que exige una negociación previa por HTTP POST para la asignación de un identificador de sesión (sid), el servidor de TradingView permite la transmisión inmediata de comandos a través del flujo una vez detectado el estado abierto del socket, lo que simplifica sustancialmente la arquitectura de red requerida en lenguajes como Python^3^.

2. Sintaxis de los Mensajes Propietarios y Framer Envelope

Una de las principales particularidades del canal de comunicación reside en su sistema de empaquetado y enmarcado de mensajes, denominado *Framer Envelope*^8^. TradingView no transmite objetos JSON en formato plano; en su lugar, utiliza un esquema de delimitación de longitud para empaquetar una o más tramas de datos dentro de un único paquete de red físico^4^.

La sintaxis del enmarcado se define formalmente mediante la siguiente estructura de cadena de caracteres:

En esta especificación,  representa el cuerpo del mensaje serializado en formato JSON compacto (sin espacios en blanco internos), mientras que  corresponde a la longitud exacta en caracteres del objeto ^3^. La constante de control ~m~ actúa como delimitador de la longitud^3^.

Este enmarcado requiere que cualquier cliente de lectura analice el búfer TCP segmentando los datos entrantes a partir de las anclas lógicas definidas por el patrón ~m~[longitud]~m~^4^. Si un mensaje supera el tamaño estándar de la trama o si el servidor decide enviar múltiples payloads lógicos concatenados en una sola transmisión de red, el analizador del cliente debe procesar de forma iterativa cada segmento basándose en la longitud declarada^4^.

Ejemplo de Mensaje Enmarcado

Si se requiere transmitir el método de autorización anónima, el JSON compacto resultante es:

JSON

{*"m"*:*"set_auth_token"*,*"p"*:[*"unauthorized_user_token"*]}

Este string posee una longitud de 54 caracteres^4^. Al aplicar el Framer Envelope, la carga de datos enviada al WebSocket debe ser exactamente la siguiente:

~m~54~m~{"m":"set_auth_token","p":["unauthorized_user_token"]}

Estructura del JSON de Llamada a Procedimientos (RPC)

El objeto JSON interno sigue un patrón estructurado de llamada a métodos (RPC) compuesto por dos claves raíz obligatorias^4^:

- **m (Método):** Cadena de caracteres que define el nombre de la función expuesta por el backend de TradingView que se desea ejecutar (por ejemplo, chart_create_session)^4^.
- **p (Parámetros):** Arreglo posicional que contiene los argumentos requeridos por la firma del método invocado^4^. La validación en el servidor es estricta, por lo que la omisión o alteración de los tipos de datos en este arreglo genera excepciones críticas^4^.

3. Flujo Completo de Suscripción a un Gráfico

El ciclo de suscripción para recibir datos históricos y flujos continuos en tiempo real consta de una secuencia lógica obligatoria de inicialización de sesiones^4^. El cliente debe orquestar los mensajes en orden cronológico inverso para registrar las sesiones antes de solicitar datos^4^.

Cliente                                                              Servidor WSS

     │                                                                      │

     ├───────────► 1. set_auth_token ("unauthorized_user_token") ──────────►│

     ├───────────► 2. set_locale ("en", "US") ─────────────────────────────►│

     ├───────────► 3. chart_create_session ("cs_...") ──────────────────────►│

     ├───────────► 4. quote_create_session ("qs_...") ──────────────────────►│

     ├───────────► 5. quote_set_fields ("qs_...", ["lp", ...]) ────────────►│

     ├───────────► 6. quote_add_symbols ("qs_...", "={\"symbol\":...}") ────►│

     ├───────────► 7. resolve_symbol ("cs_...", "sds_sym_1", "={\"...\") ───►│

     └───────────► 8. create_series ("cs_...", "sds_1", "s1", ...) ────────►│

Paso 1: Generación de Identificadores de Sesión del Cliente

La aplicación debe instanciar y rastrear localmente dos identificadores únicos de sesión de red independientes, los cuales se generan de forma dinámica para evitar colisiones de canales de datos en la infraestructura del servidor^4^:

- **Sesión de Gráfico (chart_session):** Cadena con el prefijo cs_ seguido de un identificador aleatorio de 12 caracteres alfanuméricos en minúscula^4^. Ejemplo: cs_abfghjklpqrs^4^.
- **Sesión de Cotización (quote_session):** Cadena con el prefijo qs_ seguido de un identificador aleatorio de 12 caracteres alfanuméricos en minúscula^4^. Ejemplo: qs_xyzfghjklpqr^5^.

Paso 2: Mensajes de Inicialización en Orden Cronológico

Para realizar una suscripción completa al par BINANCE:BTCUSDT en un intervalo de un minuto, se deben enviar de manera secuencial los siguientes comandos enmarcados^4^:

1. Establecimiento del Contexto de Autorización

Configura los privilegios de la conexión actual. En este caso, se utiliza un perfil no autenticado^4^. ~m~54~m~{"m":"set_auth_token","p":["unauthorized_user_token"]}

2. Definición del Contexto de Localización

Establece las directivas de idioma y región del servidor para las respuestas numéricas y descriptivas^4^. ~m~34~m~{"m":"set_locale","p":["en","US"]}

3. Creación de la Sesión del Gráfico

Instancia la sesión del gráfico en el servidor vinculada al identificador aleatorio generado por el cliente^3^. ~m~43~m~{"m":"chart_create_session","p":["cs_abfghjklpqrs",""]}

4. Creación de la Sesión de Cotización

Registra la sesión paralela que gestionará la watchlist y el flujo rápido de precios^3^. ~m~40~m~{"m":"quote_create_session","p":["qs_xyzfghjklpqr"]}

5. Configuración de Filtros de Datos para Cotizaciones

Informa al motor de cotizaciones cuáles son las propiedades numéricas y estadísticas exactas que se desea recibir en cada actualización de precio^3^. ~m~142~m~{"m":"quote_set_fields","p":["qs_xyzfghjklpqr","lp","volume","bid","ask","ch","chp","high_price","low_price","open_price","prev_close_price"]}

6. Adición de Símbolo a la Sesión de Cotización

VIncula de forma activa el activo para el seguimiento continuo de cotizaciones rápidas^4^. Nótese el uso del carácter = para encapsular la cadena JSON con los datos del símbolo y las especificaciones de ajuste de mercado^4^. ~m~102~m~{"m":"quote_add_symbols","p":["qs_xyzfghjklpqr","={"symbol":"BINANCE:BTCUSDT","adjustment":"splits"}"]}

7. Resolución del Símbolo en la Sesión de Gráfico

Inicia el motor de resolución de símbolos de gráficos asociados al identificador interno sds_sym_1 bajo la sesión de gráfico declarada^4^. ~m~120~m~{"m":"resolve_symbol","p":["cs_abfghjklpqrs","sds_sym_1","={"symbol":"BINANCE:BTCUSDT","adjustment":"splits"}"]}

8. Creación formal de la Serie Temporal (Suscripción OHLCV)

Instancia el flujo de datos históricos y en tiempo real con una resolución específica^4^. ~m~100~m~{"m":"create_series","p":["cs_abfghjklpqrs","sds_1","s1","sds_sym_1","1",300,""]}

Los parámetros requeridos en el método create_series se estructuran secuencialmente de la siguiente manera:

| **Parámetro Ordinal** | **Nombre Técnico** | **Tipo de Dato** | **Descripción y Reglas del Protocolo** |
| --- | --- | --- | --- |
| p[0] | session_id | String | Identificador de la sesión del gráfico (cs_...)^4^. |
| p[1] | series_id | String | Identificador interno de la serie de datos en este canal (habitualmente sds_1)^4^. |
| p[2] | turnaround | String | Versión de la petición o modificador de serie (por ejemplo, s1)^4^. |
| p[3] | resolve_id | String | Referencia al alias del símbolo resuelto previamente mediante resolve_symbol^4^. |
| p[4] | resolution | String | Marco temporal del gráfico. Ejemplos: "1" (1 minuto), "60" (1 hora), "1D" (diario)^4^. |
| p[5] | bars | Integer | Cantidad de velas históricas iniciales que se desean recibir en el primer volcado de datos^4^. |
| p[6] | options | String | Modificadores vacíos obligatorios para completar la firma del método^4^. |

4. Parseo de la Respuesta (Velas, Ticks y Cotizaciones)

Tras procesar la conexión, el servidor envía un flujo asíncrono y masivo de mensajes. El analizador del cliente debe decodificar las tramas del Framer Envelope y extraer las propiedades del campo de método m para clasificar las respuestas en tres categorías fundamentales de procesamiento^4^.

4.1. Carga Histórica (timescale_update)

Es el primer paquete de alta densidad que recibe el cliente tras enviar el comando create_series^4^. Contiene el conjunto completo de datos históricos solicitados para construir las barras del gráfico^4^.

JSON

{

  *"m"*: *"timescale_update"*,

  *"p"*: [

    *"cs_abfghjklpqrs"*,

    {

      *"sds_1"*: {

        *"s"*: [

          {*"i"*: *0*, *"v"*: [*1699912800.0*, *36520.1*, *36580.4*, *36490.2*, *36550.0*, *412.51*]},

          {*"i"*: *1*, *"v"*: [*1699912860.0*, *36550.0*, *36600.0*, *36510.5*, *36590.2*, *295.12*]}

        ]

      }

    }

  ]

}

Para extraer la serie, el cliente debe recuperar el objeto asociado a la clave correspondiente a la serie suscrita (por ejemplo, sds_1)^4^. El arreglo de claves s contiene diccionarios con un índice secuencial i y un arreglo puramente posicional de valores de mercado identificado como v^4^. El mapeo de la matriz posicional v se define de la siguiente manera:

| **Posición en el Arreglo (v)** | **Propiedad** | **Tipo de Dato** | **Significado y Normalización Técnica** |
| --- | --- | --- | --- |
| v[0] | Timestamp | Float / Integer | Época de tiempo Unix representada en segundos^18^. |
| v[1] | Open | Float | Precio de apertura registrado para el intervalo de tiempo^4^. |
| v[2] | High | Float | Precio máximo alcanzado durante el intervalo de tiempo^4^. |
| v[3] | Low | Float | Precio mínimo alcanzado durante el intervalo de tiempo^4^. |
| v[4] | Close | Float | Precio de cierre de la barra o cotización actual^4^. |
| v[5] | Volume | Float | Volumen total transaccionado del activo durante el intervalo^4^. |

4.2. Actualizaciones en Tiempo Real (du)

Una vez cargada la serie de tiempo histórica, el servidor propaga actualizaciones incrementales con el identificador "m": "du" cada vez que se genera actividad en el mercado^4^. Estas actualizaciones envían exclusivamente la barra actual en desarrollo^8^.

JSON

{

  *"m"*: *"du"*,

  *"p"*: [

    *"cs_abfghjklpqrs"*,

    {

      *"sds_1"*: {

        *"s"*: [

          {*"i"*: *300*, *"v"*: [*1699912920.0*, *36590.2*, *36650.0*, *36585.0*, *36610.1*, *51.24*]}

        ]

      }

    }

  ]

}

La lógica de integración local del cliente debe operar de la siguiente forma:

- **Comparación de Índices:** Se extrae el índice numérico i de la actualización^4^.
- **Actualización Incremental:** Si el índice i es idéntico al último índice de la base de datos o arreglo local del cliente, se sobrescribe en su totalidad el último registro con los nuevos valores del vector v^19^. Esto refleja los cambios continuos del tick actual (máximo, mínimo, volumen y precio de cierre dinámico)^19^.
- **Apertura de Barra Nueva:** Si el índice i es mayor que el último índice almacenado localmente, se interpreta como la consolidación de la barra previa y la apertura de una nueva barra en el gráfico, por lo que el objeto v se agrega como un nuevo registro en la base de datos o memoria^19^.

4.3. Actualizaciones de Watchlist (qsd)

Para aplicaciones que requieren paneles rápidos de precios o sistemas de monitoreo multiticker que no demandan históricos, las actualizaciones se procesan a través de la sesión de cotización mediante el evento "m": "qsd"^8^.

El objeto contiene la clave v con atributos específicos de cambio dinámico^13^:

- lp (Last Price): Último precio de cotización del mercado^16^.
- volume (Volume): Volumen diario total acumulado^16^.
- ch (Change): Variación de precio neta diaria^16^.
- chp (Change Percent): Porcentaje diario de variación de precio^16^.
- lp_time (Last Price Time): Timestamp de la última actualización del precio^21^.

5. Manejo de Autenticación, Cookies de Sesión y Keep-Alives

Establecer una suscripción sin autenticar restringe la velocidad y el volumen de datos disponibles. Por ejemplo, los clientes no autenticados (unauthorized_user_token) reciben actualizaciones del feed con un retardo sistemático de entre 10 y 15 minutos en determinados mercados y no pueden acceder a resoluciones inferiores a una hora de forma consistente^6^. Para desbloquear el flujo en tiempo real puro se requiere un flujo de autenticación basado en la identidad de sesión activa de una cuenta verificada^6^.

5.1. Extracción de Token de Autorización (auth_token)

TradingView gestiona las identidades mediante cookies de dominio firmadas. Para capturar el token del WebSocket se realiza el siguiente procedimiento^7^:

- **Captura de cookies de sesión:** Se extraen los valores de las cookies sessionid y sessionid_sign directamente del almacenamiento del navegador donde se inició sesión de forma válida en TradingView^6^.
- **Consulta de Handshake HTTP:** Se realiza una petición HTTP GET simulando un cliente web convencional a la dirección principal del módulo gráfico (por ejemplo, https://www.tradingview.com/chart/), inyectando en la cabecera Cookie los valores recuperados^7^.
- **Parseo de la Interfaz:** En el documento HTML de respuesta se localiza un bloque de inicialización de JavaScript global que asigna el objeto de inicialización de la sesión del usuario. Mediante expresiones regulares se extrae la clave del token correspondiente, habitualmente declarada dentro del payload de configuración como^7^: "auth_token":"<hash_jwt>"
- **Uso de Credenciales en el WebSocket:** El token JWT recuperado se envía como argumento en el primer mensaje de la sesión de WebSocket, eliminando el estado anónimo y heredando de forma inmediata los privilegios del perfil^7^: sendMessage(ws, "set_auth_token", [auth_token])^14^.

5.2. Protocolo de Keep-Alive (Heartbeats)

Para mantener estable el canal de comunicación del WebSocket, el cliente debe cumplir con el ciclo de Keep-Alive establecido por el servidor de TradingView para detectar conexiones muertas (zombies)^24^.

A intervalos regulares de aproximadamente 30 segundos, el servidor envía una trama de control simplificada^5^:

~m~4~m~~h~1

La cadena ~h~1 (donde el número entero final puede variar incrementalmente) actúa como un ping de nivel de aplicación^5^. El cliente debe capturar esta trama y responder de forma inmediata transmitiendo el paquete de retorno con el contenido exacto de la trama recibida^8^.

La falta de respuesta (pong) dentro de una ventana de tiempo de 10 segundos provoca la terminación abrupta e inmediata del canal por parte de la infraestructura de red de TradingView, requiriendo el inicio de un nuevo flujo de handshake y negociación de sesión de gráfico^24^.

6. Implementación Práctica e Integración en Python

El siguiente desarrollo en Python implementa las reglas técnicas detalladas para la ingeniería inversa del protocolo WebSocket de TradingView. Se utiliza la biblioteca nativa websocket-client para gestionar de forma asíncrona la recepción del flujo, el análisis del Framer Envelope, la resolución del keep-alive y el mapeo de las respuestas OHLCV^8^:

Python

*import* time

*import* json

*import* random

*import* string

*import* re

*import* threading

*from* websocket *import* create_connection

*class* *TradingViewWSSClient:*

    *def* *__init__**(self, symbol:* *str**, timeframe:* *str**, auth_token:* *str* *=* *"unauthorized_user_token"**):*

        self.symbol = symbol

        self.timeframe = timeframe

        self.auth_token = auth_token

        self.ws_endpoint = *"wss://data.tradingview.com/socket.io/websocket"*

        self.ws = *None*

        self.is_connected = *False*

        *# Generación de identificadores únicos locales para las sesiones*

        self.chart_session = self.generate_session_id(*"cs"*)

        self.quote_session = self.generate_session_id(*"qs"*)

    *def* *generate_session_id**(self, prefix:* *str**) -> str:*

        random_chars = *''*.join(random.choices(string.ascii_lowercase, k=*12*))

        *return* *f"{prefix}_{random_chars}"*

    *def* *pack_message**(self, json_data:* *dict**) -> str:*

        *# Codificación compacta y enmarcado bajo el protocolo ~m~*

        compact_str = json.dumps(json_data, separators=(*','*, *':'*))

        length = *len*(compact_str)

        *return* *f"~m~{length}~m~{compact_str}"*

    *def* *send_rpc**(self, method:* *str**, params:* *list**):*

        payload = {*"m"*: method, *"p"*: params}

        framed_data = self.pack_message(payload)

        self.ws.send(framed_data)

    *def* *init_handshake**(self):*

        *# 1. Establecimiento de credenciales de acceso y localización regional*

        self.send_rpc(*"set_auth_token"*, [self.auth_token])

        self.send_rpc(*"set_locale"*, [*"en"*, *"US"*])

        *# 2. Orquestación y registro de las sesiones de procesamiento*

        self.send_rpc(*"chart_create_session"*, [self.chart_session, *""*])

        self.send_rpc(*"quote_create_session"*, [self.quote_session])

        *# 3. Propiedades para monitorización paralela de cotizaciones*

        fields = [*"lp"*, *"volume"*, *"bid"*, *"ask"*, *"ch"*, *"chp"*, *"high_price"*, *"low_price"*, *"open_price"*]

        self.send_rpc(*"quote_set_fields"*, [self.quote_session] + fields)

        *# 4. Enlace del símbolo objetivo a las respectivas colas*

        symbol_query = {*"symbol"*: self.symbol, *"adjustment"*: *"splits"*}

        symbol_payload = *f"={json.dumps(symbol_query, separators=(',', ':'))}"*

        self.send_rpc(*"quote_add_symbols"*, [self.quote_session, symbol_payload])

        self.send_rpc(*"resolve_symbol"*, [self.chart_session, *"sds_sym_1"*, symbol_payload])

        *# 5. Inicialización de la serie temporal (Carga de 300 barras previas e inicio de streaming)*

        self.send_rpc(*"create_series"*, [self.chart_session, *"sds_1"*, *"s1"*, *"sds_sym_1"*, self.timeframe, *300*, *""*])

    *def* *connect**(self):*

        headers = {

            *"Origin"*: *"https://www.tradingview.com"*,

            *"User-Agent"*: *"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"*

        }

        self.ws = create_connection(self.ws_endpoint, headers=headers)

        self.is_connected = *True*

        *# Inicia las peticiones de suscripción en el canal recién abierto*

        self.init_handshake()

        *# Lanza la monitorización y lectura del socket en un hilo secundario independiente*

        threading.Thread(target=self._recv_handler, daemon=*True*).start()

    *def* *_recv_handler**(self):*

        framer_regex = re.*compile*(*r"~m~\d+~m~"*)

        *while* self.is_connected:

            *try*:

                raw_payload = self.ws.recv()

                *# Respuesta inmediata a los Keep-Alives (Heartbeats) para evitar desconexiones*

                *if* *"~h~"* *in* raw_payload:

                    self.ws.send(raw_payload)

                    *continue*

                *# Segmentación de tramas mediante el delimitador del Framer Envelope*

                messages = framer_regex.split(raw_payload)

                *for* message_str *in* messages:

                    *if* *not* message_str:

                        *continue*

                    *try*:

                        message_json = json.loads(message_str)

                        self._process_message(message_json)

                    *except* json.JSONDecodeError:

                        *continue*

            *except* Exception:

                self.is_connected = *False*

                *break*

    *def* *_process_message**(self, data:* *dict**):*

        method = data.get(*"m"*)

        params = data.get(*"p"*, [])

        *if* method == *"timescale_update"*:

            series_data = params[*1*].get(*"sds_1"*, {}).get(*"s"*, [])

            *for* bar *in* series_data:

                v = bar.get(*"v"*, [])

                print(*f"[HISTÓRICO] Vela indexada - Timestamp: {v[**0**]}, O: {v[**1**]}, H: {v[**2**]}, L: {v[**3**]}, C: {v[**4**]}, Vol: {v[**5**]}"*)

        *elif* method == *"du"*:

            series_data = params[*1*].get(*"sds_1"*, {}).get(*"s"*, [])

            *for* bar *in* series_data:

                v = bar.get(*"v"*, [])

                print(*f"[STREAMING] Modificación Tick - Timestamp: {v[**0**]}, Cierre actual: {v[**4**]}, Volumen acumulado: {v[**5**]}"*)

        *elif* method == *"qsd"*:

            quote_v = params[*1*].get(*"v"*, {})

            symbol_id = params[*1*].get(*"n"*)

            *if* *"lp"* *in* quote_v:

                print(*f"[COTIZACIÓN] Tick Rápido - Símbolo: {symbol_id}, Precio: {quote_v['lp']}, Volumen diario: {quote_v.get('volume')}"*)

*if* __name__ == *"__main__"*:

    *# Suscripción de prueba al par de Binance BTCUSDT en intervalo de 5 minutos*

    client = TradingViewWSSClient(symbol=*"BINANCE:BTCUSDT"*, timeframe=*"5"*)

    client.connect()

    *# Bucle para mantener la ejecución del hilo principal*

    *try*:

        *while* *True*:

            time.sleep(*1*)

    *except* KeyboardInterrupt:

        client.is_connected = *False*

7. Conclusiones y Consideraciones de Estabilidad

El desarrollo de clientes nativos basados en la ingeniería inversa de los WebSockets de TradingView proporciona una ventaja sustancial en cuanto a latencia y consumo de recursos^1^. Sin embargo, el diseño del sistema debe contemplar mecanismos específicos de resiliencia ante los siguientes factores identificados:

- **Pipelining de Mensajes:** La infraestructura de TradingView acostumbra a concatenar decenas de actualizaciones en un único paquete físico durante periodos de alta volatilidad^4^. El uso de expresiones de coincidencia en el búfer de red (como el patrón de expresiones regulares para identificar ~m~) es indispensable para evitar fallas de decodificación en los deserializadores JSON^4^.
- **Gestión de Desconexiones Zombies:** El sistema debe integrar temporizadores de inactividad que vigilen el flujo de pings procedentes del servidor^24^. Si transcurren más de 45 segundos sin recibir tramas del tipo ~h~, se debe asumir un estado de conexión zombie, forzando la reinicialización de las llamadas asíncronas para garantizar la continuidad del flujo de datos de mercado^24^.

Fuentes citadas

- Reverse engineered connection to the TradingView ticker in Python - GitHub, https://github.com/Hattorius/Tradingview-ticker
- Load stock data from TradingView. Introduction | by Prem Chotepanit - Medium, https://medium.com/@premchotepanit/load-stock-data-from-tradingview-3659950e21c8
- protocol error when connecting to websocket in NodeJS - Stack Overflow, https://stackoverflow.com/questions/65741117/protocol-error-when-connecting-to-websocket-in-nodejs
- tradingView-websocket-api/TView_api.py at main - GitHub, https://github.com/vlad-yeghiazaryan/tradingView-websocket-api/blob/main/TView_api.py
- Web scraping an interactive chart - javascript - Stack Overflow, https://stackoverflow.com/questions/63624043/web-scraping-an-interactive-chart
- Credentials error: Wrong or expired sessionid · Issue #187 · Mathieu2301/TradingView-API, https://github.com/Mathieu2301/TradingView-API/issues/187
- Which parameters should we pass for authenticated user session? · Issue #10 · imxeno/tradingview-scraper - GitHub, https://github.com/imxeno/tradingview-scraper/issues/10
- tradingview-scraper/CLAUDE.md at main - GitHub, https://github.com/mnwato/tradingview-scraper/blob/main/CLAUDE.md
- proto.js - GitHub Gist, https://gist.github.com/inesusvet/6f860def3d74768b0682acf376f53926
- Invalid Symbol #103 - tradingview/charting-library-tutorial - GitHub, https://github.com/tradingview/charting-library-tutorial/issues/103
- How to receive data through websockets in python - Stack Overflow, https://stackoverflow.com/questions/56330154/how-to-receive-data-through-websockets-in-python
- Retrieve chart pattern studies example missing · Issue #220 ... - GitHub, https://github.com/Mathieu2301/TradingView-API/issues/220
- Integrating Websockets for TradingView Chart Data - Reddit, https://www.reddit.com/r/TradingView/comments/17vfh2o/integrating_websockets_for_tradingview_chart_data/
- accessing private websocket data from tradingview in python - Stack Overflow, https://stackoverflow.com/questions/65731895/accessing-private-websocket-data-from-tradingview-in-python
- tradingView-API/tradingView.py at main · mohamadkhalaj/tradingView-API - GitHub, https://github.com/mohamadkhalaj/tradingView-API/blob/main/tradingView.py
- tvsocket package - github.com/ivo100/tvsocket - Go Packages, https://pkg.go.dev/github.com/ivo100/tvsocket
- GitHub - obafemisolo/tvdatafeedclient-js: A lighweight websocket client for accessing tradingView candlestick data via Node.js. Inspired by `tvdatafeed` for python - But made for JavaScript Devs, crypto traders and bot builders. This is just what could be., https://github.com/obafemisolo/tvdatafeedclient-js
- batprem/trading-view-scraper: Scrape trading view with ... - GitHub, https://github.com/batprem/trading-view-scraper
- Implement streaming | Advanced Charts Documentation - TradingView, https://www.tradingview.com/charting-library-docs/latest/tutorials/implement_datafeed_tutorial/Streaming-Implementation/
- Troodi/BinaryOptionsCMS - GitHub, https://github.com/Troodi/BinaryOptionsCMS
- tradingview-scraper - PyPI, https://pypi.org/project/tradingview-scraper/
- Ilia-Abolhasani/tradingview-ws: Get data realtime from websocket tradingview - GitHub, https://github.com/Ilia-Abolhasani/tradingview-ws
- How to get Session Id from Trading view - Combiz Services, https://copytrading.combiz.org/document/How-to-get-Session-Id-from-Trading-view
- WebSocket Heartbeat: Ping/Pong, Keep-Alive & Zombie Detection, https://websocket.org/guides/heartbeat/
- Keepalive and latency - websockets 15.0.1 documentation, https://websockets.readthedocs.io/en/15.0.1/topics/keepalive.html
- Keeping WebSocket connections alive - RingCentral Developers, https://developers.ringcentral.com/guide/notifications/websockets/heart-beats
- tradingview-websocket - piwheels, https://www.piwheels.org/project/tradingview-websocket/