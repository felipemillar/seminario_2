# Líneas de Investigación — TradingView: Dominio al 100%

> **Objetivo**: Diseñar los prompts de Deep Research para construir una base de conocimiento de TradingView equivalente a lo que tenemos con Broker (20 documentos, ~1.8 MB de conocimiento destilado).
> **Fecha**: 2026-07-11
> **Método**: Cada línea de investigación = 1 prompt para Gemini Deep Research

---

---

## Las 20 Líneas de Investigación

### BLOQUE A: Fundamentos de Plataforma (3 líneas)

---

#### Línea 01: Arquitectura Interna de TradingView

**Razonamiento**: En Broker empezamos por la arquitectura cliente-servidor (clusters, Access Server, Trade Server). En TradingView necesitamos entender la arquitectura cloud, cómo se procesan los scripts, cómo llegan los datos de mercado, y cómo funciona el renderizado del chart.

**Debe cubrir**:
- Arquitectura cloud de TradingView: cómo se ejecutan los scripts Pine en sus servidores
- Motor de renderizado de gráficos (HTML5 Canvas vs WebGL vs WebAssembly)
- Pipeline de datos de mercado: exchanges → TradingView servers → usuario
- Modelo de subscripción y límites por plan (Free, Pro, Pro+, Premium, Expert)
- Infraestructura de feeds de datos: qué exchanges cubren, latencia, data vendors
- Sistema de caché y persistencia de layouts, drawings, watchlists
- Diferencias entre la app web, desktop (Electron) y mobile
- Rate limits, throttling, y limitaciones de la plataforma
- Modelo de seguridad: cómo protegen el código Pine de los usuarios
- Comparativa arquitectónica directa con Broker

**Tags esperados**: `#arquitectura` `#cloud` `#rendering` `#data-feed` `#planes` `#límites` `#canvas` `#exchanges`

---

#### Línea 02: Ecosistema y Modelo de Negocio de TradingView

**Razonamiento**: TradingView no es solo una plataforma técnica — es un **ecosistema social y comercial**. Entender esto es crucial para saber qué APIs están disponibles, qué se puede monetizar, y cómo funciona la comunidad. Broker no tiene este componente.

**Debe cubrir**:
- Modelo de negocio: planes de suscripción, TradingView Market (indicadores de pago), publicidad
- TradingView Brokerage Integration: cómo los brokers se integran para trading real
- Social Network: Ideas, publicaciones, sistema de reputación, scripts públicos
- TradingView Market (Pine marketplace): cómo publicar y vender indicadores/estrategias
- Regulaciones y compliance: qué datos son gratuitos vs de pago, EOD vs realtime
- Programa de afiliados y partnerships
- TradingView para empresas: Charting Library (licencia empresarial)
- Diferencias regionales (qué exchanges están disponibles por país)
- Historial de versiones y roadmap público
- Competidores directos (TrendSpider, Finviz, StockCharts) y posicionamiento

**Tags esperados**: `#ecosistema` `#modelo-negocio` `#social` `#marketplace` `#brokerage` `#licensing`

---

#### Línea 03: Interfaz de Usuario y Funcionalidades Nativas de TradingView

**Razonamiento**: Antes de programar, necesitamos dominar lo que TradingView ya ofrece sin código. En Broker esto era más limitado; TradingView tiene un arsenal enorme de herramientas de dibujo, tipos de gráfico, y análisis built-in.

**Debe cubrir**:
- Todos los tipos de gráficos nativos (Candlestick, Heikin Ashi, Renko, Kagi, Point & Figure, Line Break, Range, etc.)
- Herramientas de dibujo: Fibonacci, Gann, Pitchfork, ondas de Elliott, patrones armónicos
- Panel de indicadores incorporados (200+): categorías, parámetros, overlay vs separado
- Watchlists, screeners, y heatmaps
- Multi-chart layouts y sincronización entre paneles
- Sistema de alertas nativo: tipos, condiciones, notificaciones (email, push, webhook)
- Replay mode (simulación de mercado pasado bar a bar)
- Hotkeys, shortcuts, y personalización del workspace
- Paper Trading nativo: cómo funciona, limitaciones, realismo
- DOM/Order Book donde esté disponible
- Calendario económico, earnings calendar, y datos fundamentales integrados
- Pine Editor: IDE integrado, autocompletado, debugging

**Tags esperados**: `#UI` `#gráficos` `#herramientas-dibujo` `#alertas` `#screeners` `#replay` `#paper-trading`

---

### BLOQUE B: Pine Script — El Lenguaje (5 líneas)

---

#### Línea 04: Pine Script v6 — Referencia Completa del Lenguaje

**Razonamiento**: Esto es el equivalente exacto de nuestro documento "MQL5 Referencia del Lenguaje". Pine Script es un lenguaje completamente distinto a MQL5 — es funcional-declarativo, ejecutado en la nube, con un modelo de series temporales implícito. Necesitamos dominar cada constructo.

**Debe cubrir**:
- Evolución del lenguaje: v1 → v2 → v3 → v4 → v5 → v6 (cambios breaking entre versiones)
- Sistema de tipos: int, float, bool, string, color, na, arrays, matrices, maps, UDT (User Defined Types)
- Modelo de ejecución: cómo Pine ejecuta barra por barra (left to right, historical vs realtime)
- Variables y constantes: `var`, `varip`, diferencia entre persistencia histórica y runtime
- Operadores, expresiones condicionales, operador ternario
- Funciones built-in: categorías completas (math, ta, str, array, matrix, map, request, etc.)
- Funciones definidas por el usuario: parámetros, valores por defecto, overloading
- Scope y visibilidad de variables
- Loops: `for`, `for...in`, `while` — y sus limitaciones en Pine
- `switch`, `if/else`, control de flujo
- Enums y tipos definidos por el usuario (UDT/type)
- Manejo de `na` (null handling) — uno de los aspectos más complejos y únicos de Pine
- Anotaciones de tipo: `series`, `simple`, `input`, `const` — el sistema de qualifiers
- Limitaciones del lenguaje: qué NO se puede hacer en Pine vs lenguajes generales
- Gotchas y trampas comunes para desarrolladores que vienen de Python/C++/MQL5

**Tags esperados**: `#pine-script` `#v6` `#tipos` `#ejecución` `#var` `#varip` `#na` `#qualifiers` `#UDT` `#funciones`

---

#### Línea 05: Pine Script — Indicadores Personalizados

**Razonamiento**: Equivalente a nuestro documento de "Indicadores MQL5 Avanzados". Pine Script es extremadamente potente para visualización, con un modelo de plots y colores más expresivo que MQL5.

**Debe cubrir**:
- `indicator()` declaration: title, overlay, format, precision, scale, max_bars_back
- Sistema de plots: `plot()`, `plotshape()`, `plotchar()`, `plotarrow()`, `plotcandle()`, `plotbar()`
- `hline()`, `fill()` entre plots y hlines
- Colores dinámicos: `color.new()`, transparencia, gradientes condicionales
- Labels y lines: `label.new()`, `line.new()` — objetos de dibujo programáticos
- Boxes, tables, y polylines (Pine v5+/v6)
- Inputs: `input.int()`, `input.float()`, `input.string()`, `input.color()`, `input.source()`, `input.timeframe()`
- Input groups y tooltips
- Multi-timeframe en indicadores: `request.security()` — uso, limitaciones, trampas de repintado
- Indicadores multi-símbolo
- Librerías Pine (libraries): cómo crear, importar, y publicar código reutilizable
- Rendimiento: `max_bars_back`, `max_lines_count`, `max_labels_count`, optimización
- Built-in variables: `bar_index`, `close`, `open`, `high`, `low`, `volume`, `time`, `timenow`, `syminfo.*`, `timeframe.*`
- Debugging: `log.info()`, `str.tostring()`, tablas de debug

**Tags esperados**: `#indicadores` `#plot` `#labels` `#lines` `#boxes` `#tables` `#request.security` `#multi-timeframe` `#libraries` `#inputs`

---

#### Línea 06: Pine Script — Estrategias y Backtesting

**Razonamiento**: Equivalente directo a nuestro documento de "Strategy Tester". En TradingView las estrategias se definen en Pine con `strategy()` y el backtesting corre en la nube. El modelo es COMPLETAMENTE distinto al de Broker (no hay Strategy Tester local con agentes).

**Debe cubrir**:
- `strategy()` declaration: todos los parámetros (initial_capital, commission, slippage, margin_long, margin_short, currency, pyramiding, etc.)
- Funciones de entrada: `strategy.entry()`, `strategy.order()`, `strategy.close()`, `strategy.close_all()`, `strategy.cancel()`, `strategy.cancel_all()`
- Funciones de protección: `strategy.exit()` con stop-loss, take-profit, trailing stop
- Modelo de ejecución de órdenes: `calc_on_order_fills`, `calc_on_every_tick`, `process_orders_on_close`
- Hedging vs Netting en Pine strategies
- Variables de estado: `strategy.position_size`, `strategy.position_avg_price`, `strategy.equity`, `strategy.openprofit`, `strategy.closedtrades.*`
- Strategy Tester de TradingView: Overview, Performance Summary, List of Trades, Equity Curve
- Métricas de rendimiento disponibles: Net Profit, Gross Profit, Max Drawdown, Sharpe Ratio, Sortino, Profit Factor, etc.
- Optimización de parámetros: ¿existe equivalente al algoritmo genético de Broker? Deep Backtesting
- Limitaciones del backtester: resolución de barras, look-ahead bias, re-painting risks
- Comparativa directa con el Strategy Tester de Broker (fortalezas y debilidades)
- `strategy.closedtrades.*` y `strategy.opentrades.*` — acceso programático al historial

**Tags esperados**: `#strategy` `#backtesting` `#entry` `#exit` `#stop-loss` `#trailing` `#equity` `#performance` `#deep-backtesting` `#métricas`

---

#### Línea 07: Pine Script — Funciones Avanzadas y Patrones de Diseño

**Razonamiento**: Una vez dominado el lenguaje base y los indicadores/estrategias, necesitamos profundizar en las capacidades avanzadas que permiten construir herramientas profesionales.

**Debe cubrir**:
- Arrays en profundidad: `array.new<type>()`, operaciones, sorting, slicing
- Matrices: `matrix.new<type>()`, operaciones matriciales, álgebra lineal
- Maps: `map.new<type, type>()`, key-value storage dinámico
- User Defined Types (UDT): `type`, constructors, métodos
- Methods: métodos en UDTs, encadenamiento
- `request.security()` avanzado: gaps, lookahead, barmerge, ticker.new(), expresiones de seguridad
- `request.security_lower_tf()`: acceso a timeframes inferiores (Pine v5+)
- `request.financial()`: datos fundamentales (EPS, revenue, etc.)
- `request.economic()`: datos económicos (GDP, CPI, interest rates)
- `request.dividends()`, `request.earnings()`, `request.splits()`
- `request.seed()`: datos de usuarios/proveedores externos
- `ticker.new()`, `ticker.modify()`, `ticker.heikinashi()`, `ticker.renko()`, etc.
- Manejo de errores y edge cases: qué pasa cuando `request.security()` retorna `na`
- Patrones de diseño: encapsulación con UDTs, state machines en Pine, factory patterns

**Tags esperados**: `#arrays` `#matrices` `#maps` `#UDT` `#methods` `#request.security` `#request.financial` `#datos-fundamentales` `#ticker` `#patrones-diseño`

---

#### Línea 08: Pine Script — Tables, Drawings y Visualización Avanzada

**Razonamiento**: TradingView tiene capacidades de visualización MUY superiores a Broker. Las tables, polylines y el sistema de coloring son herramientas que permiten crear dashboards completos dentro del gráfico. Es un eje de conocimiento propio.

**Debe cubrir**:
- `table.new()`: creación, posicionamiento, estilizado completo
- Celdas: `table.cell()`, merge, colores, fuentes, alineación
- Dashboard patterns: cómo construir paneles informativos dentro del chart
- `line.new()` avanzado: estilos, extensiones, coordenadas de tiempo vs barras
- `linefill.new()`: relleno entre líneas
- `box.new()`: rectangulos, zonas de soporte/resistencia dinámicas
- `polyline.new()`: dibujo de formas complejas (Pine v5+/v6)
- `label.new()` avanzado: tooltips, estilos, posicionamiento dinámico
- Color schemes: paletas profesionales, gradientes dinámicos basados en datos
- `color.rgb()`, `color.from_gradient()`: coloring programático avanzado
- Limitaciones de objetos: max_lines_count, max_labels_count, max_boxes_count — y estrategias para manejarlos
- Charts estéticos profesionales: mejores prácticas de diseño visual en Pine
- Ejemplos de dashboards complejos: screeners dentro del chart, tablas de correlación, heat maps

**Tags esperados**: `#tables` `#lines` `#boxes` `#polylines` `#labels` `#color` `#gradientes` `#dashboard` `#visualización`

---

### BLOQUE C: Datos y Análisis (3 líneas)

---

#### Línea 09: Data Engineering en TradingView — Feeds, Resoluciones y Fuentes

**Razonamiento**: Equivalente a nuestro "Data Engineering para Trading Algorítmico". TradingView tiene un modelo de datos completamente distinto al de Broker. No extraes datos localmente — los datos viven en la nube. Necesitamos entender qué hay disponible, con qué granularidad, y cómo accederlos.

**Debe cubrir**:
- Data providers de TradingView: CBOE, BATS, IEX, ICE, exchanges directos
- Resoluciones disponibles: segundos, minutos, horas, días, semanas, meses — y cuáles requieren plan premium
- Datos históricos: profundidad por tipo de activo (equities, forex, crypto, commodities, indices)
- Datos en tiempo real vs delayed: qué exchanges son real-time gratis vs de pago
- Extended hours data (pre-market, after-hours): disponibilidad y configuración
- Tipos de fuentes en Pine: `close`, `open`, `high`, `low`, `volume`, `hl2`, `hlc3`, `ohlc4`, `hlcc4`
- Datos fundamentales disponibles: `request.financial()` — qué métricas, qué exchanges
- Datos económicos: `request.economic()` — cobertura por país
- Spreads y pares sintéticos: cómo construir instrumentos personalizados (ej: `AAPL/MSFT`, `BTCUSD-ETHUSD`)
- Custom data feeds: `request.seed()` para datos propietarios
- Pine Data Groups: el concepto de "data windows" y cómo se agrupan los datos
- Exportación de datos: capacidades y limitaciones (¿se puede extraer data de TradingView para análisis offline?)
- Comparativa directa con el modelo de datos de Broker (broker-fed vs exchange-fed)

**Tags esperados**: `#data-feeds` `#resoluciones` `#exchanges` `#fundamentales` `#económicos` `#spreads` `#exportación` `#real-time`

---

#### Línea 10: Análisis Técnico Built-in y Funciones `ta.*` de Pine

**Razonamiento**: TradingView tiene la biblioteca de indicadores técnicos más completa del mercado. La namespace `ta.*` de Pine Script es ENORME. Necesitamos un catálogo exhaustivo porque esto alimentará la construcción de estrategias.

**Debe cubrir**:
- Catálogo completo de funciones `ta.*`: cada función con firma, parámetros, y uso
- Medias móviles: `ta.sma()`, `ta.ema()`, `ta.wma()`, `ta.vwma()`, `ta.rma()`, `ta.swma()`, `ta.alma()`, `ta.hma()`
- Osciladores: `ta.rsi()`, `ta.stoch()`, `ta.mfi()`, `ta.cci()`, `ta.cmo()`, `ta.cog()`
- Tendencia: `ta.macd()`, `ta.supertrend()`, `ta.dmi()`, `ta.adx()`, `ta.sar()`
- Volatilidad: `ta.atr()`, `ta.bb()`, `ta.kc()`, `ta.tr()`, `ta.stdev()`
- Volumen: `ta.obv()`, `ta.accdist()`, `ta.pvt()`, `ta.vwap()`, `ta.mfi()`
- Patrones: `ta.pivothigh()`, `ta.pivotlow()`, `ta.crossover()`, `ta.crossunder()`, `ta.rising()`, `ta.falling()`
- Estadísticas: `ta.correlation()`, `ta.linreg()`, `ta.percentile_linear_interpolation()`, `ta.percentile_nearest_rank()`, `ta.median()`
- Rangos: `ta.highest()`, `ta.lowest()`, `ta.highestbars()`, `ta.lowestbars()`, `ta.barssince()`, `ta.valuewhen()`
- Cómo Pine maneja internamente el cálculo de indicadores (warm-up period, `na` en las primeras barras)
- Implementación manual vs función built-in: cuándo conviene escribir tu propio cálculo
- Combinación de indicadores: patrones de confluencia técnica en Pine

**Tags esperados**: `#ta` `#indicadores-técnicos` `#medias-móviles` `#osciladores` `#volatilidad` `#volumen` `#estadísticas` `#patrones`

---

#### Línea 11: Screeners, Heatmaps y Análisis Multi-Activo en TradingView

**Razonamiento**: TradingView tiene herramientas de screening y análisis cross-market que Broker simplemente NO tiene. Esto incluye Stock Screener, Crypto Screener, Forex Screener, heatmaps de mercado, y análisis de sectores. Este es un diferenciador clave.

**Debe cubrir**:
- Stock Screener: filtros disponibles, campos técnicos vs fundamentales, exportación
- Crypto Screener, Forex Screener: diferencias y particularidades
- Heatmap de mercado: personalización, métrica de tamaño, métricas de color
- Relative Rotation Graphs (si están disponibles)
- Pine Screener: cómo crear screeners personalizados con Pine Script
- Análisis multi-símbolo en Pine: iterar sobre watchlists, crear rankings
- Análisis sectorial y comparativas de rendimiento
- Watchlists avanzadas: columnas personalizadas, coloring condicional
- Alertas multi-activo: cómo monitorear portfolios completos
- Análisis de correlación entre activos
- Datos de opciones: cadenas de opciones, volatilidad implícita (si disponible)
- Bonds, yields, y macroeconomía en TradingView

**Tags esperados**: `#screener` `#heatmap` `#multi-activo` `#sectores` `#watchlists` `#correlación` `#opciones` `#macro`

---

### BLOQUE D: Integración y Automatización (4 líneas)

---

#### Línea 12: Sistema de Alertas y Webhooks de TradingView

**Razonamiento**: Este es el mecanismo central de automatización de TradingView. A diferencia de Broker donde tienes un EA corriendo 24/7, en TradingView dependes de alertas que disparan webhooks. Es un paradigma completamente distinto y es LA forma de conectar TradingView con ejecución externa.

**Debe cubrir**:
- Sistema de alertas: tipos (crossing, moving up/down, greater/less than, entering/exiting channel)
- Alertas basadas en indicadores: condiciones simples y compuestas
- Alertas basadas en estrategias: `strategy.entry()` y `strategy.exit()` como trigger
- `alert()` function en Pine: alertas programáticas desde código
- `alertcondition()`: alertas predefinidas para usuarios de tu indicador
- `alert.freq_once_per_bar`, `alert.freq_once_per_bar_close`, `alert.freq_all`
- Webhook configuration: URL, método, payload personalizado con `{{variables}}`
- Variables de placeholder en alertas: `{{ticker}}`, `{{exchange}}`, `{{close}}`, `{{time}}`, `{{strategy.order.action}}`, etc.
- Payloads JSON personalizados para webhooks
- Limitaciones: cuántas alertas por plan, cuántos webhooks, rate limits
- Integración con servicios externos: IFTTT, Make (Integromat), Zapier
- Arquitectura de servidor para recibir webhooks: Node.js, Python Flask/FastAPI
- Latencia de alertas: cuánto tarda desde la detección hasta el webhook
- Mejores prácticas de fiabilidad: redundancia, retry logic, logging
- Alertas server-side vs client-side: diferencia crucial

**Tags esperados**: `#alertas` `#webhooks` `#automatización` `#payload` `#variables` `#latencia` `#server-side` `#integración`

---

#### Línea 13: TradingView REST API y Charting Library

**Razonamiento**: TradingView ofrece una API REST y una Charting Library embebible para empresas. Esto es el equivalente empresarial del ecosistema — permite construir plataformas propias con gráficos de TradingView.

**Debe cubrir**:
- TradingView Charting Library: qué es, licenciamiento, arquitectura
- Widget de gráfico embebible: configuración, personalización, eventos
- Advanced Charts vs Lightweight Charts (librería open-source)
- Lightweight Charts API: instalación, configuración, series de datos, plugins
- TradingView Data API: endpoints, autenticación, rate limits
- Datafeed API: cómo conectar fuentes de datos propias a la Charting Library
- Broker API: interfaz para integrar brokers propios
- WebSocket streaming para datos en tiempo real en la Charting Library
- Personalización de UI: temas, idiomas, toolbars, overlays
- Eventos y callbacks: onChartReady, subscribeBarsEvents, etc.
- Trading Terminal widget (para brokers): funcionalidades de trading integradas
- Comparativa: Charting Library vs competidores (HighCharts Stock, ApexCharts, Plotly)
- Ejemplos de implementación: dashboard propio con Charting Library + backend Python
- Costos y modelo de licencia para empresas

**Tags esperados**: `#charting-library` `#lightweight-charts` `#widgets` `#datafeed-api` `#broker-api` `#websocket` `#embedding`

---

#### Línea 14: Automatización de Trading — TradingView → Broker Execution

**Razonamiento**: Este es el puente crítico. TradingView no ejecuta órdenes directamente como Broker — necesitas un pipeline: TradingView Alert → Webhook → Tu Servidor → Broker API. Necesitamos documentar cada componente de este pipeline.

**Debe cubrir**:
- Arquitectura completa del pipeline: TV Alert → Webhook → Middleware → Broker
- Brokers con integración nativa de TradingView: lista completa, capacidades
- Trading desde TradingView: Paper Trading, cuenta demo de broker, cuenta real
- Webhook receivers: diseño de un servidor que recibe y procesa alertas
- Payload parsing: extraer símbolo, dirección, volumen, SL/TP del JSON
- Mapping de símbolos: cómo traducir tickers de TradingView a tickers del broker (ej: `BINANCE:BTCUSDT` → `BTCUSDT`)
- Plataformas intermedias: PineConnector, TradingView-to-Broker bridges, 3Commas, Cornix
- Construcción de un bot propio: Python + FastAPI/Flask para recibir webhooks y ejecutar en Broker/broker
- Risk management en el middleware: validación de órdenes, position sizing, circuit breakers
- Logging, auditoría, y reconciliación de trades
- Latencia end-to-end: desde señal en Pine hasta fill en broker
- Redundancia y failover: qué pasa si el webhook falla, si el broker está caído
- Multi-broker execution: enviar la misma señal a varios brokers simultáneamente
- Compliance y regulaciones: restricciones de automatización por jurisdicción

**Tags esperados**: `#ejecución` `#webhook-receiver` `#broker-bridge` `#pipeline` `#risk-management` `#latencia` `#PineConnector` `#bot`

---

#### Línea 15: Integración TradingView ↔ Python y Ecosistema Externo

**Razonamiento**: Equivalente a nuestro documento de "Integración Broker con Sistemas Externos". Cómo conectar TradingView con Python, bases de datos, modelos de ML, y APIs externas.

**Debe cubrir**:
- Librerías Python para TradingView: `tvdatafeed`, `tradingview-ta`, `lightweight-charts-python`
- Scraping vs API oficial: pros, contras, riesgos legales
- `tradingview-ta`: obtener análisis técnico (señales buy/sell) desde Python
- `tvdatafeed`: extracción de datos históricos programáticamente
- Lightweight Charts en Python: visualización local con datos propios
- Integración con Jupyter Notebooks: charts interactivos para análisis
- Pipeline ML: datos de TradingView → feature engineering → modelo → señales de vuelta a TradingView
- Publicación de señales externas en TradingView: `request.seed()` y custom data
- Telegram/Discord bots que consumen alertas de TradingView
- Integración con bases de datos: almacenar señales, trades, rendimiento
- CI/CD para scripts Pine: versionamiento, testing, deployment
- Herramientas de desarrollo: Pine Editor alternativo (VSCode extensions), linters
- APIs de brokers comunes para el execution layer: IBKR, Alpaca, Binance, Kraken
- Cloud deployment: AWS Lambda, Google Cloud Functions para webhook receivers

**Tags esperados**: `#python` `#tvdatafeed` `#tradingview-ta` `#lightweight-charts` `#ML` `#telegram` `#cloud` `#deployment`

---

### BLOQUE E: Estrategias Avanzadas y Metodología (3 líneas)

---

#### Línea 16: Gestión de Riesgo y Position Sizing en Pine Script

**Razonamiento**: Equivalente a nuestro "Gestión de Órdenes y Riesgo Broker". Pine Script tiene su propio enfoque para risk management dentro de estrategias. Necesitamos dominar cómo implementar position sizing, stop management, y portfolio risk en Pine.

**Debe cubrir**:
- `strategy.exit()` en detalle: SL, TP, trailing stop, trailing offset, activación condicional
- Position sizing en Pine: `strategy.equity`, cálculo de lots/shares basado en riesgo
- Fixed fractional, Kelly Criterion, y otros modelos implementados en Pine
- Risk per trade: cómo calcular ATR-based stops y sizing dinámico
- Pyramiding: configuración y control de múltiples entradas
- Partial closes: cómo implementar take-profits parciales
- Break-even stops: mover SL a precio de entrada tras X profit
- Drawdown monitoring: `strategy.max_drawdown`, circuit breakers en Pine
- Portfolio-level risk: limitaciones de Pine (single-asset por defecto)
- Commission y slippage modeling: configuración realista para backtesting
- `strategy.risk.*` functions: `strategy.risk.max_drawdown()`, `strategy.risk.max_position_size()`, etc.
- Comparativa con implementaciones equivalentes en MQL5

**Tags esperados**: `#risk-management` `#position-sizing` `#stop-loss` `#trailing` `#pyramiding` `#drawdown` `#commission` `#slippage`

---

#### Línea 17: Backtesting Avanzado — Metodología y Validación

**Razonamiento**: Esto complementa la Línea 06 (que es mecánica del backtester). Aquí nos enfocamos en la METODOLOGÍA estadística de backtesting, exactamente como en nuestro documento de Broker sobre WFA, Monte Carlo, y Deflated Sharpe.

**Debe cubrir**:
- Walk-Forward Analysis (WFA): ¿se puede implementar en Pine? Alternativas
- Out-of-sample testing: cómo dividir datos en TradingView
- Sesgos del backtester de TradingView: look-ahead bias, survivorship bias, overfitting
- Deep Backtesting: qué es, cómo funciona, cuándo usarlo
- Monte Carlo simulation: implementación en Pine vs offline en Python
- Deflated Sharpe Ratio: evaluación de significancia estadística
- Multiple testing correction: Bonferroni, Holm, FDR
- Optimización de hiperparámetros: manual vs systematic
- Forward testing (paper trading): cómo validar una estrategia en modo demo
- Stress testing: cómo evaluar rendimiento en eventos extremos (COVID, Black Monday)
- Pipeline de validación: de backtest positivo a live trading — checklist completa
- Comparativa de capacidades de backtesting: TradingView vs Broker vs Python frameworks (backtrader, vectorbt)

**Tags esperados**: `#WFA` `#monte-carlo` `#overfitting` `#deep-backtesting` `#validación` `#sesgos` `#stress-testing` `#pipeline`

---

#### Línea 18: Estrategias de Trading Algorítmico en TradingView — Patrones y Arquitecturas

**Razonamiento**: Documento de recetas y patrones de alto nivel. Cómo construir diferentes tipos de estrategias en Pine, desde trend-following hasta market-making, con consideraciones específicas de la plataforma.

**Debe cubrir**:
- Trend Following: implementaciones con MA crossover, Supertrend, Donchian Channel
- Mean Reversion: Bollinger Bands, RSI extremes, Z-score
- Breakout: volatilidad-based (ATR breakout), range breakout, opening range
- Momentum: rate of change, RSI momentum, MACD divergencias
- Multi-timeframe strategies: cómo combinar señales de diferentes timeframes en Pine
- Multi-indicator confluence: scoring systems, weighted signals
- Market regime detection: cómo adaptar estrategias al estado del mercado (trending vs ranging)
- Pairs trading y spread strategies: implementación en Pine
- Seasonal patterns: Day-of-week effects, month-of-year, session-based
- News-based / Event-driven: usando datos económicos en Pine (`request.economic()`)
- Machine Learning signals: cómo integrar predicciones de modelos ML externos en Pine
- Strategy composition: combinar múltiples estrategias en un solo script Pine

**Tags esperados**: `#trend-following` `#mean-reversion` `#breakout` `#momentum` `#multi-timeframe` `#confluence` `#regime-detection` `#pairs-trading`

---

### BLOQUE F: Infraestructura y Producción (2 líneas)

---

#### Línea 19: Infraestructura de Producción — TradingView + Ejecución Cloud

**Razonamiento**: Equivalente a nuestro "Broker, Python y Cloud" + "macOS Trading Algorítmico". Cómo montar una infraestructura de trading automatizado usando TradingView como fuente de señales, con ejecución en la nube.

**Debe cubrir**:
- Arquitectura de referencia: TradingView → Webhook → Cloud Function → Broker
- Despliegue en cloud: AWS Lambda, Google Cloud Functions, Azure Functions
- Servidores persistentes: VPS con FastAPI/Express para webhook receiver
- Base de datos para trade log: PostgreSQL, TimescaleDB, SQLite
- Monitoring y alertas: Healthchecks.io, Telegram bot para notificaciones de sistema
- Dashboards de rendimiento: Grafana, Streamlit, dashboards HTML estáticos
- Backup y disaster recovery: qué pasa si TradingView está caído
- Rate limiting y protección de webhooks: autenticación, IP whitelisting
- Multi-cuenta y multi-broker: ejecutar señales en paralelo
- TCO (Total Cost of Ownership): costos de suscripción TradingView + cloud + datos
- Latencia end-to-end: medición y optimización
- Logging estructurado: JSON logs, rotación, análisis post-trade
- Integración con el Gateway del Broker existente: cómo hacer que TradingView dispare órdenes en Broker vía nuestro Gateway

**Tags esperados**: `#cloud` `#infraestructura` `#webhook-receiver` `#VPS` `#monitoring` `#Telegram` `#latencia` `#TCO` `#disaster-recovery`

---

#### Línea 20: IA y Agentes para Desarrollo en TradingView

**Razonamiento**: Equivalente a nuestro "IA para Trading Algorítmico Broker". Cómo usar agentes de IA (Antigravity, Gemini, Claude) para acelerar el desarrollo de Pine Script, con patrones de prompt específicos.

**Debe cubrir**:
- Capacidades y limitaciones de IA para Pine Script vs MQL5
- Prompt engineering para Pine Script: plantillas específicas para indicadores, estrategias, visualización
- Workflow de 7 fases adaptado a Pine Script (pseudocódigo → código → review → test → deploy)
- Knowledge management para TradingView: cómo estructurar SKILL.md y AGENTS.md
- Debugging asistido por IA: patrones de error comunes en Pine y cómo diagnosticarlos
- Code review de estrategias: checklist de calidad para scripts Pine
- Generación de documentación automática para scripts publicados
- Testing de estrategias asistido: generar variaciones de parámetros, evaluar robustez
- Ética y riesgos: trading automático sin supervisión, responsabilidad, disclosure
- Comparativa de agentes de IA para Pine Script: quién genera mejor código
- Integración con el ecosistema de desarrollo: VSCode + Pine extension + IA
- Automatización de publicación en TradingView Market

**Tags esperados**: `#IA` `#agentes` `#prompt-engineering` `#workflow` `#knowledge-management` `#code-review` `#ética`

---

## Resumen: Mapa de Cobertura

| # | Línea de Investigación | Bloque |
|---|---|---|
| 01 | Arquitectura Interna de TradingView | A: Fundamentos |
| 02 | Ecosistema y Modelo de Negocio | A: Fundamentos |
| 03 | UI y Funcionalidades Nativas | A: Fundamentos |
| 04 | Pine Script v6 — Referencia Completa | B: Pine Script |
| 05 | Pine — Indicadores Personalizados | B: Pine Script |
| 06 | Pine — Estrategias y Backtesting | B: Pine Script |
| 07 | Pine — Funciones Avanzadas y Patrones | B: Pine Script |
| 08 | Pine — Tables, Drawings y Visualización | B: Pine Script |
| 09 | Data Engineering en TradingView | C: Datos |
| 10 | Análisis Técnico Built-in (`ta.*`) | C: Datos |
| 11 | Screeners, Heatmaps y Multi-Activo | C: Datos |
| 12 | Alertas y Webhooks | D: Integración |
| 13 | REST API y Charting Library | D: Integración |
| 14 | TV → Broker Execution Pipeline | D: Integración |
| 15 | Integración TV ↔ Python | D: Integración |
| 16 | Gestión de Riesgo en Pine | E: Estrategias |
| 17 | Backtesting Avanzado — Metodología | E: Estrategias |
| 18 | Estrategias Algorítmicas — Patrones | E: Estrategias |
| 19 | Infraestructura de Producción Cloud | F: Infra |
| 20 | IA y Agentes para TradingView | F: Infra |

---

## Orden Recomendado de Ejecución (Generaciones)

### Generación 1 (10 prompts — base fundacional):
1. Línea 01 → Arquitectura
2. Línea 04 → Pine Script Referencia
3. Línea 05 → Indicadores Pine
4. Línea 06 → Estrategias y Backtesting
5. Línea 09 → Data Engineering
6. Línea 10 → Funciones `ta.*`
7. Línea 12 → Alertas y Webhooks
8. Línea 14 → Pipeline TV → Broker
9. Línea 15 → Integración Python
10. Línea 16 → Gestión de Riesgo

### Generación 2 (10 prompts — profundización y temas únicos):
11. Línea 02 → Ecosistema y Modelo de Negocio
12. Línea 03 → UI y Funcionalidades Nativas
13. Línea 07 → Pine Avanzado (Arrays, Matrices, UDT)
14. Línea 08 → Visualización Avanzada (Tables, Drawings)
15. Línea 11 → Screeners y Multi-Activo
16. Línea 13 → Charting Library Empresarial
17. Línea 17 → Metodología de Backtesting
18. Línea 18 → Patrones de Estrategias
19. Línea 19 → Infraestructura Cloud
20. Línea 20 → IA y Agentes

### Generación 3 (7 prompts — Ingeniería hardcore y hacks):
21. Línea 21 → Librerías, Versionamiento y Arquitectura Modular
22. Línea 22 → Profiling, Garbage Collection y Memoria
23. Línea 23 → Algoritmos de Order Flow y Footprint
24. Línea 24 → Ingeniería Inversa del Protocolo WebSocket
25. Línea 25 → Data Engineering Alternativo (Pine Seed)
26. Línea 26 → Middleware de Reconciliación Asíncrona (TV ↔ Broker Externo)
27. Línea 27 → Arbitraje Estadístico y Pairs Trading

> **Nota**: El orden respeta dependencias — la Generación 1 establece la base para que la Generación 2 profundice, y la Generación 3 cruce los límites técnicos de la plataforma.
