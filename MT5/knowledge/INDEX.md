# Índice Maestro — Base de Conocimiento MT5

> **Última actualización**: 2026-06-28
> **Documentos indexados**: 20
> **Tamaño total**: ~1.83 MB
> **Generaciones**: v1 (10 docs originales) + v2 (10 docs reformulados)

---

## I. Catálogo de Documentos

### Generación 1 — Investigaciones Originales

#### 01. Informe Técnico MT5 y MQL5.md
- **Tamaño**: 68 KB | 420 líneas
- **Tags**: `#arquitectura` `#mql5-lenguaje` `#tipos-datos` `#memoria` `#eventos` `#threads` `#compilador` `#profiler` `#series-temporales` `#DOM` `#ticks` `#cluster-servidores` `#sandbox`
- **Secciones**: Arquitectura de clúster (5 tipos de servidores) · Sincronización de ticks/históricos · Event-driven model · Sistema de tipos y alineación en memoria · Descriptores de objetos · Diferencias con C++ · Tipos de programas MQL5 · Compilación y profiling · Concurrencia · Series temporales y DOM
- **Resumen**: Documento fundacional. Cubre arquitectura cliente-servidor de MT5, MQL5 en profundidad (tipos, OOP, memoria, gotchas vs C++), modelo de eventos con cola de 1024 elementos, y acceso a datos de mercado.

---

#### 02. Informe Técnico Python para MetaTrader 5.md
- **Tamaño**: 51 KB | 533 líneas
- **Tags**: `#python-api` `#metatrader5-package` `#inicialización` `#copy-rates` `#copy-ticks` `#timeframes` `#order-send` `#MqlTradeRequest` `#fill-policies` `#retcodes` `#DOM-python` `#macOS-limitaciones` `#asyncio` `#wrapper` `#ZeroMQ` `#PyMT5` `#pandas`
- **Secciones**: Setup y conexión multiterminal · Extracción de datos (Rates/Ticks) · Timeframes · Zonas horarias · DOM/Level 2 · Órdenes y posiciones · Limitaciones macOS/Linux · Patrones avanzados (pandas, asyncio, wrapper) · Ecosistema terceros
- **Resumen**: Referencia del paquete Python `MetaTrader5`. Código funcional para wrapper con auto-reconexión y asyncio.

---

#### 03. MT5: Flujos de Datos en Tiempo Real.md
- **Tamaño**: 84 KB | 472 líneas
- **Tags**: `#real-time` `#OnTick` `#OnBookEvent` `#OnTimer` `#ticks-vs-OHLCV` `#microestructura` `#DOM` `#streaming` `#named-pipes` `#ZeroMQ` `#IPC` `#baja-latencia` `#ring-buffer` `#heartbeat` `#reconexión` `#benchmarks` `#latencia`
- **Secciones**: Modelo de eventos RT · Saturación de cola · Tick vs OHLCV · DOM · Arquitecturas streaming IPC · Named Pipes Duplex (código completo) · Ring buffers · Tolerancia a fallos · Benchmarks de latencia
- **Resumen**: Ingeniería de datos en tiempo real. Implementación completa de Named Pipes MT5↔Python. Benchmarks de latencia reales por entorno.

---

#### 04. Backtesting Estrategias Trading: MT5 y Python.md
- **Tamaño**: 128 KB | 788+ líneas
- **Tags**: `#strategy-tester` `#backtesting` `#modos-modelado` `#every-tick` `#real-ticks` `#optimización` `#algoritmo-genético` `#métricas` `#profit-factor` `#sharpe-ratio` `#drawdown` `#overfitting` `#look-ahead-bias` `#data-snooping` `#deflated-sharpe` `#backtrader` `#vectorbt` `#WFA` `#walk-forward` `#monte-carlo` `#pipeline-validación` `#go-no-go`
- **Secciones**: Strategy Tester (4 modos) · Métricas de rendimiento · Sesgos (DSR) · Frameworks Python · WFA · Monte Carlo · Pipeline de validación 6 fases Go/No-Go
- **Resumen**: El documento más extenso. Strategy Tester exhaustivo, sesgos con mitigación matemática, comparativa frameworks Python, pipeline de validación completo.

---

#### 05. Gestión de Órdenes y Riesgo MT5.md
- **Tamaño**: 104 KB | 778 líneas
- **Tags**: `#órdenes` `#deals` `#posiciones` `#order-types` `#fill-policies` `#ejecución` `#stop-loss` `#take-profit` `#trailing-stop` `#ATR` `#break-even` `#position-sizing` `#kelly-criterion` `#risk-parity` `#portfolio-risk` `#correlación` `#drawdown` `#circuit-breaker` `#error-handling` `#retcodes` `#retry-logic` `#hedging` `#netting` `#FIFO` `#margen` `#código-MQL5` `#código-Python`
- **Secciones**: Modelo Order→Deal→Position · Tipos de órdenes · Fill/ejecución · Trailing stops · Position sizing · Riesgo portfolio · Error handling · Clase risk MQL5 · Módulo risk Python · Hedging/Netting · FIFO · Margen dinámico
- **Resumen**: Documento dual: mecánica del motor de trading MT5 + risk management. Implementaciones completas en MQL5 y Python con circuit breakers y kill switch.

---

#### 06. Desarrollo Profesional de EAs con IA.md
- **Tamaño**: 67 KB | 942 líneas
- **Tags**: `#expert-advisors` `#arquitectura-modular` `#state-machine` `#señales` `#ejecución` `#logging` `#telemetría` `#multi-timeframe` `#multi-symbol` `#magic-number` `#new-bar-detection` `#robustez` `#weekend-gaps` `#splits` `#spread-noticias` `#prompts-IA` `#workflow-IA` `#VPS` `#hot-swap` `#deployment` `#heartbeat`
- **Secciones**: Anatomía modular de EA · Patrones de diseño · State machine 5 estados · Multi-TF · Multi-symbol · Edge cases · Workflow con IA · Logging/telemetría · Deployment y hot-swap
- **Resumen**: Manual de ingeniería de software para EAs. State machine completa, motor de nueva barra, sistema de telemetría con heartbeat. Ciclo completo hasta hot-swap en producción.

---

#### 07. Creación Indicadores MQL5 Avanzados y ML.md
- **Tamaño**: 114 KB | 915 líneas
- **Tags**: `#indicadores` `#OnCalculate` `#buffers` `#draw-styles` `#DRAW_FILLING` `#DRAW_CANDLES` `#COLOR_INDEX` `#iCustom` `#CopyBuffer` `#handles` `#VWAP` `#orderflow` `#footprint` `#market-profile` `#volume-profile` `#renko` `#heikin-ashi` `#supertrend` `#ichimoku` `#feature-engineering` `#z-score` `#min-max` `#divergencias` `#régimen-mercado` `#FFT` `#wavelets` `#profiler` `#señales` `#confluencia`
- **Secciones**: OnCalculate() y buffers · Estilos de dibujo · Multi-buffer y colores · iCustom vs handles · Indicadores avanzados (VWAP, Footprint, Profile, Renko, HA, Supertrend, Ichimoku) · Feature engineering ML · Rendimiento · **3 indicadores completos implementados**
- **Resumen**: El más técnico. 3 implementaciones completas (VWAP, Heikin Ashi Smoothed, ML Feature Engine). Único que conecta indicadores con feature engineering para ML.

---

#### 08. Data Engineering para Trading Algorítmico MT5.md
- **Tamaño**: 121 KB | 709 líneas
- **Tags**: `#data-engineering` `#extracción-masiva` `#paginación` `#tick-data` `#OHLCV` `#datos-alternativos` `#COT` `#calidad-datos` `#anomalías` `#limpieza` `#rollover` `#Parquet` `#HDF5` `#TimescaleDB` `#QuestDB` `#feature-engineering` `#VPIN` `#bid-ask` `#dollar-bars` `#triple-barrier` `#purging` `#embargo` `#ETL` `#Airflow` `#Prefect` `#DVC` `#Delta-Lake` `#asof-join`
- **Secciones**: Extracción masiva · Calidad de datos · Formatos almacenamiento · Feature engineering · Datasets ML (Triple Barrier, purging) · Pipelines ETL · Fuentes complementarias · **Pipeline completo EURUSD**
- **Resumen**: Pipeline completo de datos MT5→ML. Triple Barrier Method, VPIN, dollar bars. Implementación funcional completa en Python.

---

#### 09. Informe Técnico: MT5, Python y Cloud.md
- **Tamaño**: 102 KB | 792 líneas
- **Tags**: `#arquitectura-cloud` `#monolítica` `#híbrida` `#enterprise` `#VPS` `#Wine` `#Docker` `#ZeroMQ` `#bridges` `#Named-Pipes` `#shared-files` `#TimescaleDB` `#schemas` `#ML-pipeline` `#Feast` `#feature-store` `#drift-detection` `#dashboards` `#Grafana` `#Streamlit` `#Telegram-bot` `#alertas` `#escalación` `#WebRequest` `#circuit-breaker` `#failover` `#disaster-recovery`
- **Secciones**: 3 arquitecturas (Simple/Intermedia/Enterprise) · Bridges comparativa · ZeroMQ Bridge código · Almacenamiento · ML Pipeline · Dashboards · Alertas Telegram · Seguridad · Circuit breaker · Disaster recovery
- **Resumen**: Documento de arquitectura de sistemas. 3 niveles con costos/latencias. ZeroMQ bridge, Telegram bot, circuit breaker, disaster recovery completo.

---

#### 10. IA para Trading Algorítmico MT5.md
- **Tamaño**: 50 KB | 397 líneas
- **Tags**: `#agentes-IA` `#Antigravity` `#Gemini` `#Claude` `#prompt-engineering` `#workflow-IA` `#pseudocódigo` `#code-review` `#tests` `#debugging` `#knowledge-management` `#GEMINI.md` `#SKILL.md` `#Skills` `#auditoría-código` `#checklist` `#documentación-automática` `#ética` `#riesgos-IA`
- **Secciones**: Capacidades/limitaciones IA para MQL5 · Prompt engineering · Workflow 7 fases · Knowledge management (GEMINI.md, SKILL.md) · Auditoría código · Documentación automática · Ética y riesgos
- **Resumen**: Guía para usar agentes de código en desarrollo de trading algorítmico. Workflow de 7 fases y configuración de Knowledge Management con Skills.

---

### Generación 2 — Investigaciones Reformuladas (MT5-focused)

#### 11. Informe Técnico Arquitectura MetaTrader 5.md
- **Tamaño**: 55 KB | 418 líneas
- **Tags**: `#arquitectura` `#cliente-servidor` `#autenticación` `#canales-comunicación` `#servidor-trading` `#servidor-históricos` `#pérdida-conexión` `#event-loop` `#eventos` `#coalescencia` `#OnTradeTransaction` `#threads` `#hilos-ejecución` `#memoria-compartida` `#concurrencia` `#main-thread-símbolo` `#DLL-sincronización` `#ticks-almacenamiento` `#hcc` `#tkc` `#RAM-límites` `#directorio-datos` `#sandbox` `#archivos` `#DLL-permisos` `#multi-terminal` `#portable-mode` `#VPS-límites` `#MetaTester` `#protocolo-agentes` `#MQL5-Cloud` `#LiveUpdate` `#breaking-changes` `#versionamiento`
- **Secciones**: Cliente-servidor y red · Canales de comunicación · Servidor trading vs históricos · Pérdida de conexión · Event-driven model (bucle, prioridades, coalescencia, OnTradeTransaction) · Threads y concurrencia · Main thread de símbolo · DLL sincronización · Datos internos (.hcc, .tkc, RAM) · Directorio de datos · Sandbox · Multi-terminal portable · MetaTester protocolo · MQL5 Cloud · LiveUpdate y breaking changes
- **Resumen**: **Versión v2 de arquitectura** — más profundo que el doc 01. Cubre pérdida de conexión, coalescencia de eventos, main thread de símbolo, estructura de directorios para automatización, portable mode con límites de hardware, protocolo MetaTester, y estrategias contra breaking changes.

---

#### 12. Informe Técnico MQL5 para Desarrolladores.md
- **Tamaño**: 70 KB | 634+ líneas
- **Tags**: `#mql5-lenguaje` `#sistema-tipos` `#char` `#short` `#int` `#long` `#float` `#double` `#datetime` `#color` `#enum` `#struct` `#class` `#union` `#MqlRates` `#MqlTick` `#MqlTradeRequest` `#casting` `#OOP` `#herencia` `#interfaces` `#polimorfismo` `#virtual` `#operator-overloading` `#templates` `#memoria` `#heap` `#punteros` `#ArrayResize` `#memory-leaks` `#preprocesador` `#define` `#include` `#property` `#import` `#ifdef` `#compilación` `#errores` `#GetLastError` `#ResetLastError` `#strings` `#archivos` `#FileOpen` `#sandbox` `#Print` `#PrintFormat` `#math` `#arrays` `#ArrayCopy` `#ArraySort` `#matrix` `#vector` `#gotchas-cpp` `#AS_SERIES`
- **Secciones**: Sistema de tipos completo (primitivos, compuestos, predefinidos) · Casting y trampas de precisión · OOP (herencia, interfaces, polimorfismo, operator overloading, templates) · Memoria y heap (punteros inteligentes, ArrayResize, memory leaks, límites) · Preprocesador y compilación · Control de errores (LastError, patrón post-llamada) · Strings, archivos y telemetría · Biblioteca matemática y arrays · Matrices y vectores nativos · **Gotchas exhaustivos vs C++ (sección dedicada)**
- **Resumen**: **Versión v2 de referencia MQL5** — trata MQL5 como lenguaje formal. Más profundo que el doc 01 en templates, operator overloading, matrices/vectores nativos, y tiene sección dedicada a gotchas vs C++ que el doc 01 solo rozaba.

---

#### 13. MQL5: Capacidades Avanzadas y Extensión.md
- **Tamaño**: 94 KB | 882+ líneas
- **Tags**: `#OpenCL` `#GPU` `#kernels` `#CLContextCreate` `#CLBufferCreate` `#DLL` `#import` `#marshaling` `#alineación-memoria` `#crashes-DLL` `#WebRequest` `#HTTP` `#HTTPS` `#REST-API` `#whitelist-URLs` `#sockets` `#SocketCreate` `#SocketConnect` `#TCP` `#TLS` `#SQLite` `#DatabaseCreate` `#DatabaseExecute` `#transacciones` `#schemas` `#Services` `#OnStart` `#background` `#Standard-Library` `#CTrade` `#CPositionInfo` `#CAppDialog` `#CExpert` `#Custom-Symbols` `#CustomSymbolCreate` `#CustomRatesUpdate` `#instrumentos-sintéticos` `#matrix` `#vector` `#numpy-comparativa`
- **Secciones**: OpenCL (API completa, kernels, benchmarks, código funcional) · DLL imports (marshaling, alineación, crashes, sandbox) · WebRequest HTTP/HTTPS (código funcional REST) · Sockets TCP/TLS · SQLite embebido (schema trading, transacciones, código funcional) · Services (ciclo de vida, diferencias vs EA, código funcional) · Standard Library (CTrade, CExpert, CAppDialog — evaluación crítica) · Custom Symbols (creación, datos, código funcional) · Matrices/vectores vs NumPy
- **Resumen**: **NUEVO — cubría gap [INACTIVO]**. El documento que faltaba completamente. Cubre todas las capacidades de extensión de MQL5 con código funcional para cada una: OpenCL, DLLs, REST API, SQLite, Services, Custom Symbols.

---

#### 14. Desarrollo Profesional de Expert Advisors en MQL5.md
- **Tamaño**: 73 KB | 911 líneas
- **Tags**: `#expert-advisors` `#ciclo-vida` `#OnInit` `#OnDeinit` `#OnTick` `#OnTimer` `#OnTrade` `#OnTradeTransaction` `#OnChartEvent` `#OnTester` `#INIT_SUCCEEDED` `#REASON_CODES` `#arquitectura-modular` `#directorios-proyecto` `#mqh` `#guardas-inclusión` `#state-machine` `#FSM` `#persistencia-estado` `#GlobalVariables` `#multi-timeframe` `#barra-0-repintado` `#sincronización-historial` `#multi-symbol` `#OnTimer-polling` `#thread-blocking` `#edge-cases` `#desconexión` `#auto-recovery` `#splits` `#dividendos` `#logging-JSON` `#rotación-logs` `#sinput` `#parameter-groups` `#Magic-Number` `#bucle-descendente` `#código-completo`
- **Secciones**: Ciclo de vida completo (todos los callbacks con códigos de retorno/razón) · OnTradeTransaction en detalle · Arquitectura modular (directorios, guardas) · State machine con persistencia · Multi-TF (barra 0, sincronización) · Multi-symbol (OnTimer, thread blocking) · Edge cases (desconexión, auto-recovery, splits) · Logging JSON con rotación · sinput y parameter groups · Magic Numbers (bucle descendente) · **Código fuente unificado completo**
- **Resumen**: **Versión v2 de EAs** — más riguroso que doc 06. Añade: todos los reason codes de OnDeinit, OnTradeTransaction detallado, estructura de directorios de proyecto, persistencia de estado, logging JSON con rotación, parameter groups, y bucle descendente de posiciones.

---

#### 15. Informe Técnico: Indicadores y Gráficos MT5.md
- **Tamaño**: 94 KB | 967 líneas
- **Tags**: `#indicadores` `#OnCalculate` `#firma-completa` `#firma-reducida` `#prev_calculated` `#cálculo-incremental` `#buffers` `#INDICATOR_DATA` `#INDICATOR_COLOR_INDEX` `#INDICATOR_CALCULATIONS` `#EMPTY_VALUE` `#PlotIndexSet` `#draw-styles` `#DRAW_COLOR_CANDLES` `#DRAW_COLOR_LINE` `#DRAW_FILLING` `#DRAW_ZIGZAG` `#multi-ventana` `#overlay` `#indicator_level` `#escala` `#iCustom` `#IndicatorCreate` `#CopyBuffer` `#caché-handles` `#conteo-referencias` `#objetos-gráficos` `#OBJ_TREND` `#OBJ_HLINE` `#OBJ_RECTANGLE_LABEL` `#OBJ_BUTTON` `#OBJ_BITMAP` `#coordenadas-pixel` `#coordenadas-precio` `#anclaje` `#paneles-interactivos` `#CHARTEVENT_OBJECT_CLICK` `#CHARTEVENT_MOUSE_MOVE` `#CAppDialog` `#CPanel` `#CButton` `#rendimiento` `#ArraySetAsSeries` `#profiling` `#tester-indicadores`
- **Secciones**: OnCalculate() 2 firmas · prev_calculated e incremental · Buffers (modos, EMPTY_VALUE, PlotIndexSet) · **Catálogo exhaustivo de 18 estilos de dibujo** · Multi-ventana vs overlay · Escala y niveles · iCustom/IndicatorCreate/CopyBuffer con caché de handles · **Objetos gráficos completos** (coordenadas pixel/precio, anclaje) · **Paneles interactivos** (CHARTEVENT_*, CAppDialog) · Rendimiento y ArraySetAsSeries · Indicadores en Strategy Tester · **3 implementaciones**: Velas por volatilidad, Panel interactivo con Standard Library, iCustom Proxy
- **Resumen**: **Versión v2 de indicadores — cubría gap [PENDIENTE]**. Añade lo que faltaba: objetos gráficos completos, paneles interactivos con CAppDialog, catálogo de 18 estilos de dibujo, y 3 nuevos indicadores (incluido un panel interactivo funcional).

---

#### 16. MT5: Órdenes, Trades y Posiciones.md
- **Tamaño**: 84 KB | 888 líneas
- **Tags**: `#órdenes` `#deals` `#posiciones` `#Order-Deal-Position` `#POSITION_IDENTIFIER` `#market-orders` `#pending-orders` `#stop-limit` `#ORDER_TYPE_CLOSE_BY` `#ejecución-request` `#ejecución-instant` `#ejecución-market` `#ejecución-exchange` `#matriz-campos` `#fill-FOK` `#fill-IOC` `#fill-Return` `#MqlTradeRequest` `#TRADE_ACTION_DEAL` `#TRADE_ACTION_PENDING` `#TRADE_ACTION_SLTP` `#TRADE_ACTION_MODIFY` `#TRADE_ACTION_REMOVE` `#TRADE_ACTION_CLOSE_BY` `#MqlTradeResult` `#request_id` `#async` `#retcodes` `#hedging` `#netting` `#margen-matemático` `#OnTradeTransaction` `#MqlTradeTransaction` `#cola-transacciones` `#OrderCheck` `#NormalizeDouble` `#SYMBOL_VOLUME_MIN` `#HistorySelect` `#HistorySelectByPosition` `#close-by-limitación` `#código-despachador` `#código-tracker` `#código-reconstructor`
- **Secciones**: Modelo Order→Deal→Position (con POSITION_IDENTIFIER) · Tipología exhaustiva de órdenes (8 tipos + close by) · 4 modos de ejecución con matrices de campos · Fill policies con compatibilidad · MqlTradeRequest (17 campos detallados) · MqlTradeResult y request_id async · Hedging vs Netting (modelado matemático de margen) · OnTradeTransaction (cola, reglas de llenado por tipo) · OrderCheck y validación · Historial (limitación close-by documentada) · **3 implementaciones**: Despachador completo, Tracker OnTradeTransaction, Reconstructor por Magic Number
- **Resumen**: **Versión v2 dedicada al motor de trading** — separado del risk management (doc 05). Más exhaustivo: matrices de campos por modo de ejecución, modelado matemático de margen, limitación documentada de HistorySelectByPosition, y 3 implementaciones de código de producción.

---

#### 17. Strategy Tester MT5: Guía Exhaustiva.md
- **Tamaño**: 80 KB | 613 líneas
- **Tags**: `#strategy-tester` `#modos-modelado` `#every-tick` `#real-ticks` `#OHLC-1min` `#open-prices` `#modo-visual` `#depuración-visual` `#profiling` `#optimización` `#grid-search` `#algoritmo-genético` `#población` `#crossover` `#mutación` `#convergencia` `#multi-símbolo` `#forward-testing` `#overfitting` `#agentes-locales` `#agentes-remotos` `#MQL5-Cloud-Network` `#criterios-optimización` `#OnTester` `#custom-criterio` `#Frames-API` `#OnTesterInit` `#OnTesterDeinit` `#OnTesterPass` `#FrameFirst` `#FrameNext` `#TesterStatistics` `#STAT_PROFIT` `#STAT_SHARPE_RATIO` `#equity-curve` `#limitaciones-tester` `#Sleep-tester` `#WebRequest-tester` `#reportes-HTML` `#línea-comandos` `#automatización`
- **Secciones**: 4 modos de modelado detallados · Modo visual (control, objetos, profiling) · Motor de optimización (genético en detalle: población, crossover, mutación) · Forward testing automático · Agentes (locales, remotos, Cloud) · Criterios de optimización + OnTester custom · **Frames API completa** (OnTesterInit/Deinit/Pass, FrameFirst/Next) · TesterStatistics (todas las STAT_*) · Limitaciones (Sleep, WebRequest en tester) · Reportes HTML/PDF · **Automatización por línea de comandos** · **3 guías paso a paso**: Backtest real ticks, optimización genética+forward, EA con OnTester custom
- **Resumen**: **Versión v2 de Strategy Tester** — más profundo que doc 04 en la mecánica de MT5. Agrega: internals del algoritmo genético, Frames API completa, automatización por línea de comandos, y modo visual para debugging. Doc 04 es superior en metodología estadística (WFA, Monte Carlo, DSR).

---

#### 18. Informe Técnico MetaTrader5 Python API.md
- **Tamaño**: 103 KB | 984 líneas
- **Tags**: `#python-api` `#metatrader5-package` `#initialize` `#login` `#terminal_info` `#account_info` `#symbols_get` `#symbol_info` `#trade_mode` `#volume_min` `#trade_stops_level` `#copy_rates_from` `#copy_rates_from_pos` `#copy_rates_range` `#TIMEFRAME` `#numpy-structured-array` `#pandas-DataFrame` `#UTC` `#copy_ticks_from` `#copy_ticks_range` `#COPY_TICKS_ALL` `#COPY_TICKS_INFO` `#COPY_TICKS_TRADE` `#TICK_FLAG` `#market_book_add` `#market_book_get` `#BookInfo` `#order_check` `#order_send` `#TradeRequest` `#OrderSendResult` `#positions_get` `#orders_get` `#history_orders_get` `#history_deals_get` `#last_error` `#RES_S_OK` `#rate-limiting` `#benchmarks-velocidad` `#scheduling` `#VPS-gateway` `#macOS-bridge` `#gRPC` `#código-pasarela`
- **Secciones**: Inicialización (parámetros, fallos, recuperación) · Inspección de sesión · Símbolos (filtrado avanzado, todos los campos) · Datos OHLCV (3 métodos, 21 timeframes, numpy→pandas) · Ticks (3 flags, TICK_FLAG_*, límites memoria) · DOM (suscripción, BookInfo, brokers forex) · Órdenes (order_check, TradeRequest completo, patrones de configuración) · Posiciones e historial · Errores (códigos runtime, API vs servidor) · Rendimiento (benchmarks, concurrencia) · Integración Python (pandas, matplotlib, scheduling) · **Código completo de Pasarela VPS (Gateway)**
- **Resumen**: **Versión v2 de API Python** — el doble de extenso que doc 02. Agrega: todos los campos de symbol_info, TICK_FLAG_* detallados, benchmarks de velocidad, diferenciación errores API/servidor, y un **código completo de pasarela VPS** para macOS.

---

#### 19. Integración de MetaTrader 5 con Sistemas Externos.md
- **Tamaño**: 84 KB | ~800 líneas
- **Tags**: `#WebRequest` `#HTTP` `#HTTPS` `#GET` `#POST` `#PUT` `#DELETE` `#JSON-parsing` `#whitelist-URLs` `#sockets` `#SocketCreate` `#SocketConnect` `#SocketSend` `#SocketRead` `#TCP` `#TLS` `#framing` `#heartbeat` `#ZeroMQ` `#DWX` `#REQ-REP` `#PUB-SUB` `#Named-Pipes` `#shared-memory` `#archivos-compartidos` `#watchdog` `#python-MT5-inverso` `#GlobalVariables` `#GlobalVariableSet` `#GlobalVariableGet` `#persistencia` `#EA-servidor-REST` `#HTTP-server-EA` `#SendNotification` `#SendMail` `#Alert` `#push` `#comparativa-métodos`
- **Secciones**: WebRequest completo (GET/POST/PUT/DELETE, JSON, whitelist) · Sockets TCP/TLS (framing, reconnection) · ZeroMQ/DWX (REQ/REP, PUB/SUB, extensión) · Named Pipes y shared memory · Archivos compartidos (file locking, watchdog) · Python→MT5 vía API oficial · GlobalVariables (comunicación inter-EA, persistencia) · **EA como servidor REST** (endpoints, parsing HTTP) · Notificaciones (push, email, Alert) · **Tabla comparativa de todos los métodos**
- **Resumen**: **NUEVO — cubría gap [PENDIENTE]**. Documento dedicado a integración que estaba distribuido entre docs 03 y 09. Agrega: WebRequest detallado con JSON parsing, EA como servidor REST completo, GlobalVariables para inter-EA, y tabla comparativa de 9 métodos evaluados en 6 dimensiones.

---

#### 20. MT5 macOS Trading Algorítmico: Guía Técnica.md
- **Tamaño**: 108 KB | ~900 líneas
- **Tags**: `#macOS` `#Apple-Silicon` `#M1` `#M2` `#M3` `#M4` `#CrossOver` `#Wine` `#DLL-limitaciones` `#Parallels` `#VMware-Fusion` `#UTM` `#Windows-ARM` `#VPS` `#ForexVPS` `#BeeksFX` `#Contabo` `#Vultr` `#AWS-Lightsail` `#Google-Cloud` `#Azure` `#Pepperstone-latencia` `#configuración-VPS` `#Task-Scheduler` `#Windows-Defender` `#auto-trading` `#macOS-desarrollo` `#VSCode-MQL5` `#rsync` `#SCP` `#compilación-remota` `#RDP` `#Parsec` `#SSH-tunneling` `#Telegram-heartbeat` `#Healthchecks.io` `#push-iOS` `#watchdog-PowerShell` `#auto-restart` `#SQLite-estado` `#backup` `#disaster-recovery` `#TCO` `#costos` `#matriz-decisión` `#latencia-slippage`
- **Secciones**: MT5 nativo macOS (CrossOver, limitaciones DLL/OpenCL) · Virtualización Apple Silicon (Parallels, VMware, UTM) · VPS Windows (7 proveedores, latencia a Pepperstone) · Configuración óptima VPS (Task Scheduler, Defender, power plan) · **Workflow macOS→VPS** (VSCode MQL5, rsync, compilación remota, Strategy Tester) · Acceso remoto (RDP, Parsec, SSH) · **Telemetría y alertas** (Telegram heartbeat MQL5 clase completa, Healthchecks.io, push iOS) · **Auto-recovery** (watchdog PowerShell, reinicio VPS por API, estado SQLite) · Backup y disaster recovery · **Análisis TCO y matriz de decisión** · Modelo de impacto latencia→slippage
- **Resumen**: **NUEVO — cubría gap [INACTIVO]**. El documento que faltaba completamente. Cubre TODA la problemática de operar MT5 desde macOS. Incluye: clase MQL5 para Telegram heartbeat, watchdog PowerShell, workflow de desarrollo macOS→VPS, análisis de costos de 7 proveedores, y modelo de impacto latencia→slippage financiero.

---

## II. Tabla de Tags Cruzados

| Tag | Documentos donde aparece |
|---|---|
| `#arquitectura` | 01, 09, **11** |
| `#mql5-lenguaje` | 01, 06, **12** |
| `#python-api` | 02, 03, 08, **18** |
| `#órdenes` / `#order-send` | 02, 05, 06, **16**, **18** |
| `#ticks` / `#tick-data` | 01, 02, 03, 08, **11**, **18** |
| `#DOM` | 01, 02, 03, **18** |
| `#real-time` / `#streaming` | 03, 09 |
| `#strategy-tester` / `#backtesting` | 04, 07, **17** |
| `#optimización` / `#algoritmo-genético` | 04, 07, **17** |
| `#risk-management` | 05, 06 |
| `#expert-advisors` | 06, **14** |
| `#indicadores` | 07, **15** |
| `#feature-engineering` | 03, 07, 08 |
| `#ML` / `#machine-learning` | 07, 08, 09 |
| `#ZeroMQ` / `#bridges` | 02, 03, 09, **19** |
| `#VPS` / `#deployment` | 06, 09, **20** |
| `#alertas` / `#Telegram` | 06, 09, **20** |
| `#circuit-breaker` | 05, 09 |
| `#agentes-IA` / `#workflow-IA` | 06, 10 |
| `#macOS` / `#Apple-Silicon` | 02, 09, **18**, **20** |
| `#trailing-stop` / `#ATR` | 05, 07 |
| `#hedging` / `#netting` | 05, **16** |
| `#Parquet` / `#TimescaleDB` | 08, 09 |
| `#WFA` / `#walk-forward` | 04 |
| `#monte-carlo` | 04 |
| `#state-machine` | 06, **14** |
| `#OpenCL` / `#GPU` | **13** |
| `#DLL` / `#import` | **13**, **19** |
| `#SQLite` / `#DatabaseCreate` | **13**, **20** |
| `#Services` / `#OnStart` | **13** |
| `#Standard-Library` / `#CExpert` | **13**, **15** |
| `#Custom-Symbols` | **13** |
| `#WebRequest` / `#REST-API` | **13**, **19** |
| `#sockets` / `#TCP` | **13**, **19** |
| `#objetos-gráficos` / `#paneles` | **15** |
| `#GlobalVariables` | **19** |
| `#watchdog` / `#auto-recovery` | **20** |
| `#backup` / `#disaster-recovery` | 09, **20** |
| `#Frames-API` / `#OnTesterPass` | **17** |
| `#línea-comandos` / `#automatización` | **17** |
| `#OnTradeTransaction` | **11**, **14**, **16** |
| `#logging-JSON` / `#rotación` | **14** |

---

## III. Cobertura vs. Prompts Reformulados (MT5-only)

| Prompt | Doc Gen1 | Doc Gen2 | Cobertura |
|---|---|---|:---:|
| P1: Arquitectura interna MT5 | 01 | **11** | [ACTIVO][ACTIVO] Doble cobertura |
| P2: MQL5 referencia del lenguaje | 01 (parcial) | **12** | [ACTIVO] Cubierto (v2 completa gaps) |
| P3: MQL5 avanzado (OpenCL, DLL, SQLite) | [ERROR] | **13** | [ACTIVO] **Cubierto** [OK] |
| P4: Expert Advisors profesionales | 06 | **14** | [ACTIVO][ACTIVO] Doble cobertura |
| P5: Indicadores y objetos gráficos | 07 (parcial) | **15** | [ACTIVO] **Cubierto** [OK] |
| P6: Sistema de órdenes y ejecución | 05 (mezclado) | **16** | [ACTIVO] **Cubierto** [OK] |
| P7: Strategy Tester y optimización | 04 | **17** | [ACTIVO][ACTIVO] Doble cobertura |
| P8: API Python completa | 02 | **18** | [ACTIVO][ACTIVO] Doble cobertura |
| P9: Comunicación e integración | 03+09 (parcial) | **19** | [ACTIVO] **Cubierto** [OK] |
| P10: MT5 en macOS e infraestructura | [ERROR] | **20** | [ACTIVO] **Cubierto** [OK] |

> **[OK] COBERTURA COMPLETA**: Los 10 pilares de conocimiento MT5 están cubiertos. Los 2 gaps rojos y 3 amarillos de la v1 han sido resueltos con la Generación 2.

---

## IV. Relación entre Generaciones (Gen1 vs Gen2)

| Tema | Gen1 | Gen2 | Relación |
|---|---|---|---|
| Arquitectura | 01 | 11 | Gen2 más profundo en eventos, threading, directorios, LiveUpdate |
| MQL5 Lenguaje | 01 (parcial) | 12 | Gen2 cubre templates, operator overloading, matrices, gotchas dedicados |
| MQL5 Avanzado | [ERROR] | 13 | **Solo Gen2** — OpenCL, DLL, SQLite, Services, Custom Symbols |
| Expert Advisors | 06 | 14 | Gen2 más riguroso en callbacks, estado, logging JSON, parameter groups |
| Indicadores | 07 | 15 | Gen1 más fuerte en indicadores avanzados; Gen2 añade objetos gráficos/paneles |
| Órdenes/Trading | 05 | 16 | Gen1 incluye risk; Gen2 puro motor de trading con más detalle |
| Strategy Tester | 04 | 17 | Gen1 mejor en metodología (WFA, MC); Gen2 mejor en mecánica MT5 |
| Python API | 02 | 18 | Gen2 el doble de extenso, con pasarela VPS y benchmarks |
| Integración | 03+09 | 19 | Gen2 consolida todo en un doc con tabla comparativa |
| macOS/Infra | [ERROR] | 20 | **Solo Gen2** — workflow macOS, VPS, monitoring, disaster recovery |
| Data Engineering | 08 | [ERROR] | **Solo Gen1** |
| Cloud Architectures | 09 | [ERROR] | **Solo Gen1** (Gen2 P19 cubre integración, no cloud) |
| IA/Workflows | 10 | [ERROR] | **Solo Gen1** |

---

## V. Protocolo de Actualización

### Cuándo actualizar
- Al agregar un nuevo documento a `knowledge/`
- Al modificar significativamente un documento existente

### Cómo actualizar
Pedir a Antigravity:
```
Actualiza el INDEX.md con los documentos nuevos en knowledge/
```

### Qué actualizar
1. Agregar nueva entrada en la sección I (Catálogo)
2. Actualizar la tabla de tags cruzados (sección II)
3. Actualizar la tabla de cobertura (sección III)
4. Actualizar metadatos (fecha, conteo de documentos, tamaño total)
