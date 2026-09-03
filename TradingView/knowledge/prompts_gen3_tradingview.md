# [SIGNAL] Prompts para Gemini Deep Research — TradingView (Generación 3)

> **Instrucciones de uso**: Copia y pega cada prompt en una sesión nueva de Gemini Deep Research.
> **Fecha de creación**: 2026-07-11
> **Enfoque**: Ingeniería de Software Extrema en Pine Script, Hacking de Protocolos y Sinergia MT5.
> **Nota crítica**: Cada prompt incluye una sección "Ya documentado — NO cubrir" para evitar duplicación masiva con las Gen 1 y Gen 2 (los primeros 20 documentos).

---

## Prompt 21: Librerías, Versionamiento y Arquitectura Modular en Pine Script

```
Genera un manual exhaustivo de ingeniería de software sobre el diseño, publicación y mantenimiento de librerías en Pine Script v6.

CONTEXTO: Ya tenemos documentada la sintaxis completa de Pine, sus estructuras de datos avanzadas (arrays, matrices, maps, UDTs) y patrones de diseño básicos. Este informe debe enfocarse estrictamente en la ARQUITECTURA MODULAR a nivel institucional.

El informe debe cubrir en profundidad, con código de ejemplo:

1. **Diseño de Librerías (export)**: Reglas para exportar funciones, tipos definidos por usuario (UDTs) e instanciación. Prácticas recomendadas de inmutabilidad en librerías.
2. **Namespaces y Conflictos**: Gestión de colisiones de nombres al importar múltiples librerías. Uso de alias en el `import`.
3. **Mantenimiento y Versionamiento Semántico**: Cómo funciona el versionado en TradingView (`import usuario/libreria/1`). Ciclo de vida de una librería pública vs privada. Manejo de breaking changes para los usuarios de la librería.
4. **Documentación Automática**: Formato estándar de docstrings para librerías (`@description`, `@param`, `@returns`). Cómo TradingView extrae esto para el auto-completado del editor.
5. **Arquitectura Modular de Referencia**: Cómo estructurar un sistema complejo dividiendo el código en: Librería de Tipos (UDTs), Librería Core (Cálculos), Script de Interfaz (Visualización) y Script de Ejecución (Estrategia).

NO cubrir en este documento (ya documentado):
- Cómo declarar variables o UDTs (sólo cómo exportarlos).
- Cómo funcionan los Arrays, Maps o Matrices internamente.
- Cómo publicar un indicador en el mercado.
```

---

## Prompt 22: Profiling, Garbage Collection y Optimización Extrema de Memoria

```
Genera un informe altamente técnico sobre los límites de compilación, ejecución y memoria del motor de Pine Script, y cómo realizar "Profiling" y optimización extrema.

CONTEXTO: Ya documentamos cómo programar en Pine, pero no tenemos documentación de qué hacer cuando el script lanza un error de "Calculation takes too long" o se queda sin memoria al procesar matrices o datos muy pesados.

El informe debe cubrir en profundidad, con código de ejemplo:

1. **Límites de Ejecución y Memoria del Servidor**: Explicación técnica de los límites de tiempo de compilación, tiempo de ejecución por barra, límite total de memoria y variables permitidas en el runtime de TradingView.
2. **Manejo del Garbage Collector (GC)**: Cuándo Pine Script libera memoria de Arrays y Matrices. Cómo forzar limpiezas explícitas (`array.clear()`) versus la recolección automática. Estrategias para evitar fugas de memoria en `var` y `varip`.
3. **Optimización de Bucles `for` y Cálculos Pesados**: Por qué los bucles son lentos en Pine. Técnicas de "Loop Unrolling", pre-cálculo de constantes, y vectorización manual.
4. **Estado Persistente Intra-Tick (`varip`) avanzado**: Trampas y peligros de `varip` durante el repainting de la última barra. Casos donde la pérdida de sincronización corrompe la matriz de datos.
5. **Profiling Empírico**: Cómo medir los milisegundos de ejecución usando `timenow` dentro del código para crear tu propio profiler de funciones en Pine Script. Identificación de cuellos de botella.

NO cubrir en este documento:
- Limitaciones de objetos gráficos (`max_lines_count`, etc.) ya está documentado.
- Explicación teórica de qué es un bucle `for` o un `array`.
```

---

## Prompt 23: Algoritmos de Order Flow y Footprint en Pine Script

```
Genera una guía de implementación algorítmica para reconstruir gráficos de Footprint, Order Flow y Volume Profile de alta granularidad usando Pine Script.

CONTEXTO: TradingView tiene herramientas nativas de Volume Profile, pero queremos CONSTRUIR nuestros propios analizadores de flujo de órdenes a nivel código.

El informe debe cubrir en profundidad, con código de ejemplo:

1. **Reconstrucción del Tick Intra-Barra**: Uso avanzado de `request.security_lower_tf()` para extraer el volumen bid/ask (o su aproximación) usando el timeframe de 1 segundo (1S) o ticks donde esté disponible, e inyectarlo en la barra de un timeframe superior (ej. 5M).
2. **Matriz de Order Flow (Footprint)**: Lógica algorítmica para mapear volumen por nivel de precio (Price Level Volume) usando `map` o `matrix` en Pine Script.
3. **Detección de Desequilibrios (Imbalances)**: Código matemático para detectar imbalances diagonales (bid vs ask) y *stacked imbalances* (3 o más niveles consecutivos).
4. **Point of Control (POC) y Value Area Dinámicos**: Algoritmos eficientes para recalcular el dPOC y las bandas VAH/VAL (Value Area High/Low al 70%) de manera eficiente en cada tick sin crashear el servidor.
5. **Delta Acumulativo (CVD)**: Implementación robusta de Cumulative Volume Delta desde cero.

NO cubrir en este documento:
- Herramientas nativas de la UI de TradingView.
- Uso básico de `request.security()`.
- Dibujo básico de tablas o cajas.
```

---

## Prompt 24: Ingeniería Inversa del Protocolo WebSocket de TradingView

```
Genera un análisis técnico exhaustivo (Ingeniería Inversa) del protocolo WebSocket no oficial (WSS) utilizado por el cliente web de TradingView para recibir datos de mercado en tiempo real.

CONTEXTO: Queremos conectar nuestros scripts Python directamente al flujo de datos en tiempo real de TradingView sin depender de librerías tipo Selenium (scrapers) o paquetes obsoletos de terceros.

El informe debe cubrir en profundidad:

1. **Arquitectura del WebSocket WSS**: Endpoints principales (ej. `wss://data.tradingview.com/socket.io/websocket`). Formato de los mensajes de inicialización (handshake, tokens de sesión).
2. **Sintaxis de los Mensajes Propietarios**: Análisis del protocolo JSON estructurado con el prefijo `~m~[longitud]~m~`. Cómo se empacan las llamadas a métodos (`quote_create_session`, `resolve_symbol`, `create_series`).
3. **Flujo Completo de Subscripción a un Gráfico**: Mensajes exactos (en orden cronológico) para autenticarse, crear una sesión de quote, crear una sesión de chart, resolver el símbolo (ej. `BINANCE:BTCUSDT`) y suscribirse a las actualizaciones de la serie.
4. **Parseo de la Respuesta (Ticks)**: Formato de la respuesta del servidor (`du` message, updates de las barras OHLCV, índices de volumen).
5. **Manejo de Autenticación y Tokens**: Extracción y renovación del token `session_id` desde las cookies de una cuenta validada. Manejo de desconexiones (ping/pong keep-alives).

NO cubrir en este documento:
- El uso de la librería Python `tvdatafeed`.
- Cómo usar Webhooks.
- Documentación de Pine Script.
```

---

## Prompt 25: Data Engineering Alternativo (Pine Seed y Data Import)

```
Genera un informe técnico sobre los métodos (oficiales y *hacks*) para importar datos externos alternativos a TradingView que no pertenecen a su flujo de mercado estándar.

CONTEXTO: Queremos cruzar nuestros propios datos alternativos (ej. datos on-chain procesados en nuestro servidor, clima, sentimiento de redes sociales) y graficarlos junto al precio en TradingView.

El informe debe cubrir:

1. **Pine Seed API**: Uso de Pine Seed (la función `seed()` o sus alternativas recientes) para subir series de tiempo personalizadas alojadas en repositorios públicos de GitHub. Formato requerido (CSV/JSON), límites de actualización y caché temporal.
2. **Inyección vía Webhooks a Charting Library**: Cómo usar nuestra propia instancia de la Charting Library (B2B) para cruzar los datos de nuestro Gateway MT5 usando la `Datafeed API` customizada.
3. **Uso de Request.Financial para Hacks**: Exploración de *workarounds* donde desarrolladores han usado campos financieros oscuros o económicos globales para inyectar o cruzar métricas externas.
4. **Pine Script y Codificación de Datos (Data Encoding)**: Técnicas de esteganografía donde los traders empaquetan información en cadenas numéricas grandes o strings.
5. **Limitaciones Arquitectónicas Actuales**: Cuáles son las fronteras absolutas dictaminadas por TradingView respecto a llamadas HTTP hacia el exterior (inexistentes en Pine por seguridad) y el roadmap prometido para el soporte nativo de "Custom Data".

NO cubrir en este documento:
- La exportación de Webhooks (ya sabemos cómo sacar datos de TV, aquí queremos meter datos a TV).
```

---

## Prompt 26: Middleware de Reconciliación Asíncrona (TV ↔ Broker Externo)

```
Genera el diseño de arquitectura de software para un Middleware de Reconciliación (State Machine) en Python que maneje las divergencias de estado entre TradingView (fuente de señales asíncrona) y un API Broker Institucional (ejecución síncrona local).

CONTEXTO: TradingView asume en su "Paper Trading" o *Strategy Tester* que las órdenes se llenan perfectamente, pero los brokers lidian con slippage real, rechazos del servidor, y Stop Losses locales. Necesitamos una máquina de estados para reconciliar esto.

El informe debe cubrir en profundidad:

1. **El Problema de "Ghost Positions"**: Escenario detallado de desincronización (Ej: TV lanza orden Buy, el Broker la ejecuta. El precio baja abruptamente, el Broker ejecuta el Stop Loss en su servidor. TV no lo sabe porque su SL en Pine aún no se ha tocado. TV luego lanza un comando de "Close Position", pero en el Broker ya no existe. Resultado: Error lógico o posición inversa accidental).
2. **Diseño de la Máquina de Estados (FSM)**: Estados propuestos (`TV_WAITING`, `BROKER_EXECUTING`, `PARTIAL_FILL`, `SL_HIT_LOCAL`, `ORPHAN_SIGNAL`). Diagrama lógico de transiciones.
3. **Feedback Loop Inverso**: Estrategia técnica para que el Gateway FastAPI lea el historial de órdenes real del Broker y rechace/cancele de forma inteligente los webhooks tardíos o contradictorios provenientes de TradingView.
4. **Idempotencia y Secuenciadores**: Uso de un UUID (`order_id` o tag del Webhook) para evitar la duplicación de órdenes ante reintentos de red de TradingView.
5. **Esquema de Base de Datos para Reconciliación**: Diseño de las tablas (SQL) o colecciones (NoSQL) que mapean la relación 1-a-1 entre el *Virtual Trade ID* de TradingView y el *Ticket Number* del Broker.

NO cubrir en este documento:
- Cómo enviar un webhook básico desde Pine Script.
- Código Python básico de Flask/FastAPI.
```

---

## Prompt 27: Arbitraje Estadístico y Pairs Trading (TV ↔ API Broker)

```
Genera un manual técnico sobre cómo implementar estrategias complejas multi-pierna (Arbitraje Estadístico y Pairs Trading) usando TradingView como cerebro analítico y una API Broker Institucional como motor de ejecución.

CONTEXTO: Queremos aprovechar la superioridad de Pine Script para matemáticas y correlaciones (ej. Matrices, Eigenvalues) para calcular cointegración, y enviar instrucciones complejas a nuestro Gateway Python local.

El informe debe cubrir en profundidad:

1. **Cálculo de Cointegración y Z-Score en Pine Script**: Algoritmo en Pine v6 para calcular el *spread* de dos activos (Ej: AAPL vs MSFT), aplicando regresión lineal con Matrices y derivando el Z-Score de la reversión a la media.
2. **Payload Estructurado del Webhook Multi-Pierna**: Diseño del JSON para enviar instrucciones compuestas de ejecución atómica ("Comprar 1 lote de Activo A y Vender simultáneamente 1.5 lotes del Activo B") en un solo webhook.
3. **Motor de Ejecución Atómica en el Gateway Python**: Cómo debe el script de Python (FastAPI → Broker API) recibir la instrucción y asegurar una ejecución concurrente de ambas patas usando `asyncio` o *multithreading* para minimizar el riesgo de *leg risk* (deslizamiento de precio entre las dos órdenes).
4. **Manejo de Slippage en Pairs Trading**: Lógica de *fill-or-kill* aproximada o abandono de la posición si una de las patas del spread es rechazada por el servidor del Broker.
5. **Reversión y Cierre Sincronizado**: Cómo TradingView debe gestionar el cruce del Z-Score por el eje 0 (Mean Reversion) y emitir el comando exacto para deshacer el spread de forma limpia en el broker.

NO cubrir en este documento:
- Teoría financiera básica de qué es un spread.
- Cómo usar conectores básicos de Python.
```
