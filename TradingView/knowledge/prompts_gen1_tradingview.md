# [SIGNAL] Prompts para Gemini Deep Research — TradingView (Generación 1)

> **Instrucciones de uso**: Copia y pega cada prompt en una sesión nueva de Gemini Deep Research. Cada prompt generará un documento de ~50-120 KB que luego guardaremos en el directorio `knowledge/` del nuevo proyecto TradingView.
> **Fecha de creación**: 2026-07-11

---

## Prompt 01: Arquitectura Interna de TradingView

```
Genera un informe técnico exhaustivo sobre la arquitectura interna de TradingView como plataforma de análisis financiero y charting.

El informe debe cubrir en profundidad, con código de ejemplo cuando sea posible:

1. **Arquitectura Cloud**: Cómo funciona la infraestructura de servidores de TradingView. Dónde se ejecutan los scripts Pine Script (servidor vs cliente). Modelo de procesamiento de gráficos. Arquitectura de microservicios o monolítica. CDN y distribución geográfica.

2. **Motor de Renderizado de Gráficos**: Tecnologías usadas (HTML5 Canvas, WebGL, WebAssembly). Cómo se renderizan los candlesticks, indicadores y objetos de dibujo. Pipeline de renderizado desde datos hasta píxeles. Optimizaciones de rendimiento para gráficos con miles de barras.

3. **Pipeline de Datos de Mercado**: Cómo llegan los datos desde los exchanges hasta el usuario final. Data vendors y proveedores de feeds. Latencia del pipeline. Diferencias entre datos real-time vs delayed. Protocolos de comunicación (WebSocket, polling, etc.).

4. **Modelo de Suscripción y Límites**: Diferencias técnicas entre los planes Free, Pro, Pro+, Premium y Expert. Límites de alertas, indicadores por gráfico, layouts guardados, resoluciones de datos. Qué funcionalidades están restringidas por plan.

5. **Sistema de Ejecución de Pine Script**: Modelo de ejecución barra por barra. Diferencia entre ejecución histórica y en tiempo real. Sandbox de seguridad. Cómo se protege el código fuente de los scripts. Limitaciones de recursos (tiempo de ejecución, memoria, loops).

6. **Plataformas**: Diferencias técnicas entre la app web (navegador), la aplicación de escritorio (Electron), y las aplicaciones móviles (iOS/Android). Qué funcionalidades están disponibles en cada una.

7. **Sistema de Caché y Persistencia**: Cómo se guardan layouts, templates, watchlists, drawings. Sincronización entre dispositivos. Almacenamiento local vs en la nube.

8. **Rate Limits y Throttling**: Limitaciones de la plataforma en cuanto a peticiones, cálculos simultáneos, y uso de recursos. Cómo se maneja la concurrencia de miles de usuarios.

9. **Comparativa Arquitectónica con Plataformas Institucionales**: Diferencias fundamentales entre una arquitectura client-server nativa (Broker) y una arquitectura cloud-first (TradingView). Ventajas y desventajas de cada enfoque para trading algorítmico.

El informe debe ser técnico, con diagramas descritos textualmente, y orientado a un desarrollador de software que quiere entender cómo funciona TradingView por dentro para construir herramientas sobre esta plataforma. Extensión esperada: al menos 5000 palabras.
```

---

## Prompt 02: Pine Script v6 — Referencia Completa del Lenguaje

```
Genera un informe técnico exhaustivo sobre Pine Script v6, el lenguaje de programación de TradingView, tratándolo como una referencia formal del lenguaje.

El informe debe cubrir en profundidad, con código funcional de ejemplo para cada concepto:

1. **Evolución del Lenguaje**: Historia desde Pine Script v1 hasta v6. Cambios breaking entre cada versión. Cómo migrar código de v4/v5 a v6. Qué versiones siguen siendo soportadas.

2. **Sistema de Tipos Completo**: Todos los tipos de datos — int, float, bool, string, color, na. Arrays (`array<type>`). Matrices (`matrix<type>`). Maps (`map<key, value>`). User Defined Types (UDT) con `type`. Casting entre tipos. Comportamiento de `na` (null) en cada tipo.

3. **Sistema de Qualifiers**: Explicación profunda de `const`, `input`, `simple`, `series`. Cómo afectan la ejecución. Cuándo usar cada uno. Errores comunes de incompatibilidad de qualifiers.

4. **Modelo de Ejecución**: Cómo Pine ejecuta barra por barra de izquierda a derecha. Diferencia entre ejecución en barras históricas vs en tiempo real (la última barra). Concepto de `barstate.isrealtime`, `barstate.isconfirmed`, `barstate.islast`. Re-cálculo en la barra actual.

5. **Variables y Persistencia**: Declaración de variables. `var` (inicialización una sola vez, persiste entre barras). `varip` (persiste incluso en la barra actual entre ticks en RT). Variables regulares (recalculadas en cada barra). Scope de variables en funciones vs global.

6. **Operadores y Expresiones**: Aritméticos, comparación, lógicos. Operador ternario. Operador de referencia histórica `[]` (ej: `close[1]`). Precedencia de operadores. Trampas con `na` en operaciones.

7. **Control de Flujo**: `if/else`, `switch`, `for`, `for...in`, `while`. Limitaciones de loops en Pine. `break`, `continue`. Conditional expressions.

8. **Funciones**: Funciones built-in (categorías: `math.*`, `ta.*`, `str.*`, `array.*`, `matrix.*`, `map.*`, `request.*`, `ticker.*`, `timeframe.*`, `syminfo.*`). Funciones definidas por el usuario. Parámetros con valores por defecto. Retorno de múltiples valores con tuplas `[val1, val2]`.

9. **User Defined Types (UDT)**: Declaración con `type`. Constructores. Campos. Methods. Cómo usarlos para encapsulación y diseño modular. Limitaciones vs clases en otros lenguajes.

10. **Methods**: Cómo definir métodos para tipos built-in y UDTs. Method overloading. Encadenamiento de métodos.

11. **Manejo de `na`**: El sistema de null handling de Pine en profundidad. Funciones `na()`, `nz()`, `fixnan()`. Propagación de `na` en operaciones. Trampas comunes. Mejores prácticas.

12. **Annotations y Metadata**: `indicator()`, `strategy()`, `library()`. Parámetros de cada una. `@version`, `@description`, `@param`, `@returns`, `@type`, `@field`.

13. **Limitaciones del Lenguaje**: Qué NO se puede hacer en Pine vs lenguajes generales (Python, MQL5). Sin acceso a filesystem, sin networking, sin threading, sin recursión. Límites de compilación (500 variables locales, etc.).

14. **Gotchas para Desarrolladores**: Trampas específicas para programadores que vienen de Python, JavaScript, C++, o MQL5. Diferencias de comportamiento que causan bugs.

El informe debe ser una referencia técnica completa, con código funcional para cada concepto, equivalente a un manual del lenguaje. Extensión esperada: al menos 8000 palabras.
```

---

## Prompt 03: Pine Script — Indicadores Personalizados

```
Genera un informe técnico exhaustivo sobre la creación de indicadores personalizados en Pine Script para TradingView.

El informe debe cubrir en profundidad, con código funcional completo para cada concepto:

1. **Declaración `indicator()`**: Todos los parámetros — title, shorttitle, overlay, format, precision, scale, timeframe, timeframe_gaps, max_bars_back, max_lines_count, max_labels_count, max_boxes_count, max_polylines_count. Cuándo usar cada uno. Diferencia entre overlay=true e indicator separado.

2. **Sistema de Plots**: `plot()` con todos sus parámetros (title, color, linewidth, style, trackprice, histbase, offset, join, editable, show_last, display). Estilos de plot: line, stepline, cross, circles, columns, area, areabr, stepline_diamond. `plotshape()` con todas las formas. `plotchar()`. `plotarrow()`. `plotcandle()` y `plotbar()` para velas/barras custom.

3. **hline y fill**: `hline()` para líneas horizontales. `fill()` entre dos plots o entre plot y hline. Colores dinámicos en fill. Gradientes.

4. **Colores Dinámicos**: `color.new()` con transparencia dinámica. `color.rgb()`. `color.from_gradient()` para mapear valores numéricos a gradientes de color. Paletas de colores profesionales. Conditional coloring patterns.

5. **Labels**: `label.new()` — posicionamiento (xloc, yloc), estilos, colores, textos, tooltips. Actualización dinámica. Gestión del límite de labels (eliminación de antiguos). Patterns para etiquetas informativas.

6. **Lines**: `line.new()` — coordenadas, estilos (solid, dotted, dashed, arrow_left, arrow_right, arrow_both), extensiones (extend.none, extend.left, extend.right, extend.both). Líneas de tendencia dinámicas. Soporte y resistencia.

7. **Boxes**: `box.new()` — para zonas rectangulares. Supply/demand zones. Order blocks. Session highlights.

8. **Inputs del Usuario**: `input.int()`, `input.float()`, `input.bool()`, `input.string()` con options, `input.color()`, `input.source()`, `input.timeframe()`, `input.symbol()`, `input.session()`, `input.text_area()`. Input groups. Tooltips. Confirm parameter.

9. **Multi-Timeframe**: `request.security()` — sintaxis, parámetros (symbol, timeframe, expression, gaps, lookahead). Trampas de repintado (repainting). `barmerge.gaps_on` vs `barmerge.gaps_off`. `barmerge.lookahead_on` vs `barmerge.lookahead_off` y por qué lookahead_on es peligroso en estrategias. `request.security_lower_tf()`.

10. **Libraries Pine**: Cómo crear una library con `library()`. Exportar funciones. Importar con `import`. Versionamiento. Publicación. Mejores prácticas de código reutilizable.

11. **Debugging**: `log.info()`, `log.warning()`, `log.error()`. Usar `table` para debug visual. `str.tostring()` para inspección. `label` como debug flotante. Pine Logs panel.

12. **Rendimiento y Optimización**: `max_bars_back` y su impacto. Cálculo eficiente vs redundante. Evitar loops innecesarios. Caché de cálculos con `var`. Límites de tiempo de compilación.

13. **3 Indicadores Completos Implementados**:
    - Un VWAP con bandas de desviación estándar y tabla de estadísticas
    - Un indicador de estructura de mercado (Higher Highs, Lower Lows, Break of Structure)
    - Un dashboard multi-timeframe que muestre el estado de varios indicadores en una tabla

Extensión esperada: al menos 7000 palabras, con código funcional completo para los 3 indicadores.
```

---

## Prompt 04: Pine Script — Estrategias y Backtesting

```
Genera un informe técnico exhaustivo sobre la creación de estrategias de trading y backtesting en Pine Script para TradingView.

El informe debe cubrir en profundidad, con código funcional completo:

1. **Declaración `strategy()`**: Todos los parámetros — title, overlay, initial_capital, currency, default_qty_type (fixed, cash, percent_of_equity), default_qty_value, commission_type, commission_value, slippage, margin_long, margin_short, pyramiding, calc_on_order_fills, calc_on_every_tick, process_orders_on_close, close_entries_rule, max_bars_back, risk_free_rate.

2. **Funciones de Entrada**: `strategy.entry()` — id, direction (strategy.long, strategy.short), qty, limit, stop, oca_name, oca_type, comment, alert_message, disable_alert. Diferencia entre entry y order. `strategy.order()` — para órdenes que no generan señales de entrada. `strategy.close()`, `strategy.close_all()`, `strategy.cancel()`, `strategy.cancel_all()`.

3. **Funciones de Salida y Protección**: `strategy.exit()` — from_entry, qty, qty_percent, profit, loss, limit, stop, trail_price, trail_points, trail_offset, comment, alert_message. Trailing stops detallados con trail_points y trail_offset. Múltiples targets (parciales). Stop-loss y take-profit simultáneos.

4. **Modelo de Ejecución de Órdenes**: Cómo se procesan las órdenes barra a barra. Diferencia entre `calc_on_order_fills=true` y `false`. `calc_on_every_tick` y su impacto en backtesting vs realtime. `process_orders_on_close` y cuándo usarlo. Orden de prioridad de ejecución.

5. **Variables de Estado de Estrategia**: `strategy.position_size`, `strategy.position_avg_price`, `strategy.equity`, `strategy.initial_capital`, `strategy.openprofit`, `strategy.netprofit`, `strategy.grossprofit`, `strategy.grossloss`, `strategy.wintrades`, `strategy.losstrades`, `strategy.eventtrades`.

6. **Acceso al Historial de Trades**: `strategy.closedtrades.*` — entry_price, exit_price, entry_bar_index, exit_bar_index, entry_time, exit_time, size, profit, commission, max_runup, max_drawdown. `strategy.opentrades.*` — mismos campos para trades abiertos. Iteración sobre trades históricos.

7. **Strategy Tester de TradingView**: Las 3 pestañas — Overview (resumen de rendimiento), Performance Summary (métricas detalladas), List of Trades (historial completo). Qué métricas muestra cada una. Equity Curve y Drawdown chart.

8. **Deep Backtesting**: Qué es el modo Deep Backtesting. Cómo funciona internamente (usa datos de resolución inferior). Cuándo usarlo. Limitaciones. Diferencias con el backtesting normal.

9. **Métricas de Rendimiento**: Net Profit, Gross Profit/Loss, Max Drawdown (absoluto y %), Sharpe Ratio, Sortino Ratio, Profit Factor, Percent Profitable, Win/Loss Ratio, Average Trade, Largest Winning/Losing Trade, Average # Bars in Winning/Losing Trades, Max Consecutive Wins/Losses.

10. **Limitaciones del Backtester**: Ejecución en el close de la barra vs intra-bar. Look-ahead bias potencial. Cómo el backtester maneja gaps. Limitaciones de precisión en resoluciones bajas. Fill assumptions vs realidad. Slippage modeling.

11. **Comparativa con Strategy Tester de Broker**: Ventajas y desventajas de cada uno. Modos de modelado (Broker tiene "Every Tick" con ticks reales; TV usa resolución de barras). Optimización de parámetros (Broker tiene algoritmo genético; TV no tiene equivalente nativo). Agentes remotos de Broker vs cloud de TV.

12. **3 Estrategias Completas Implementadas**:
    - Estrategia de cruce de medias móviles con trailing stop y risk management
    - Estrategia de RSI con filtro de tendencia multi-timeframe
    - Estrategia de breakout ATR con position sizing dinámico basado en volatilidad

Extensión esperada: al menos 8000 palabras, con código funcional completo para las 3 estrategias.
```

---

## Prompt 05: Data Engineering en TradingView — Feeds, Resoluciones y Fuentes

```
Genera un informe técnico exhaustivo sobre los datos de mercado disponibles en TradingView: feeds, resoluciones, fuentes, y cómo acceder a ellos programáticamente.

El informe debe cubrir en profundidad:

1. **Proveedores de Datos**: Todos los data providers de TradingView. Exchanges cubiertos por clase de activo (equities, forex, crypto, commodities, indices, bonds, futures, options). Diferencias entre exchanges por región (USA, Europa, Asia, Latam). Calidad y fiabilidad de cada feed.

2. **Resoluciones de Datos**: Todas las resoluciones temporales disponibles (1s, 5s, 10s, 15s, 30s, 1m, 3m, 5m, 15m, 30m, 45m, 1h, 2h, 3h, 4h, 1D, 1W, 1M, 3M, 6M, 12M). Cuáles requieren plan premium. Resoluciones personalizadas. Cómo se construyen barras en cada resolución.

3. **Datos en Tiempo Real vs Delayed**: Qué exchanges proporcionan datos real-time gratuitos. Cuáles requieren suscripción adicional. Latencia típica de datos delayed (15min, 20min). Cómo identificar si los datos son real-time en el gráfico.

4. **Profundidad Histórica**: Cuántas barras de historia están disponibles por tipo de activo y resolución. Límites de `max_bars_back`. Datos históricos para crypto (desde cuándo). Datos históricos para equities, forex, commodities.

5. **Extended Hours**: Pre-market y after-hours data. Cómo habilitarlo. Disponibilidad por exchange. Impacto en indicadores y estrategias. Electronic trading hours.

6. **Tipos de Fuentes en Pine**: Variables de precio (`open`, `close`, `high`, `low`, `volume`, `time`). Fuentes compuestas (`hl2`, `hlc3`, `ohlc4`, `hlcc4`). `source` parameter en indicadores. Cómo funciona el parámetro `input.source()`.

7. **Datos Fundamentales (`request.financial()`)**: Qué métricas financieras están disponibles (EPS, Revenue, P/E, Market Cap, etc.). Cobertura por exchange y país. Periodicidad (quarterly, annual, TTM). Gaps en datos fundamentales.

8. **Datos Económicos (`request.economic()`)**: Indicadores macroeconómicos disponibles (GDP, CPI, Unemployment, Interest Rates, PMI, etc.). Cobertura por país. Periodicidad. Cómo usar en indicadores y estrategias.

9. **Datos de Dividendos, Earnings y Splits**: `request.dividends()`, `request.earnings()`, `request.splits()`. Cómo acceder y usar en scripts Pine.

10. **Instrumentos Sintéticos y Spreads**: Cómo crear pares custom en TradingView (ej: `AAPL/MSFT`, `BTCUSD-ETHUSD`, `XAUUSD*USDCLP`). Operadores disponibles. Limitaciones. Uso en estrategias de pairs trading.

11. **Custom Data (`request.seed()`)**: Cómo inyectar datos propietarios en TradingView. Pine Seeds. Proceso de publicación. Limitaciones. Casos de uso (datos alternativos, señales ML).

12. **Exportación de Datos**: Capacidades de exportación desde TradingView. Formatos disponibles. Limitaciones. APIs externas para extracción de datos (`tvdatafeed` en Python). Aspectos legales del web scraping.

13. **Información del Símbolo (`syminfo.*`)**: Todas las variables de `syminfo` — `syminfo.ticker`, `syminfo.root`, `syminfo.prefix`, `syminfo.type`, `syminfo.currency`, `syminfo.basecurrency`, `syminfo.pointvalue`, `syminfo.mintick`, `syminfo.session`, `syminfo.timezone`, `syminfo.volumetype`, etc.

14. **Comparativa con el Modelo de Datos de Broker**: Broker obtiene datos del broker conectado. TradingView obtiene datos de exchanges directamente. Ventajas y desventajas de cada modelo. Implicaciones para backtesting y análisis.

Extensión esperada: al menos 6000 palabras.
```

---

## Prompt 06: Análisis Técnico Built-in — Funciones `ta.*` de Pine Script

```
Genera un informe técnico exhaustivo que sea un catálogo completo de todas las funciones de análisis técnico built-in de Pine Script (namespace `ta.*`), con código de ejemplo para cada una.

El informe debe cubrir TODAS las funciones organizadas por categoría:

1. **Medias Móviles**: `ta.sma()`, `ta.ema()`, `ta.wma()`, `ta.vwma()`, `ta.rma()` (Wilder's MA), `ta.swma()` (Symmetrically Weighted MA), `ta.alma()` (Arnaud Legoux MA), `ta.hma()` (Hull MA), `ta.dema()`, `ta.tema()`. Para cada una: fórmula matemática, parámetros, uso típico, código de ejemplo, y diferencias de comportamiento.

2. **Osciladores**: `ta.rsi()`, `ta.stoch()` (Stochastic), `ta.mfi()` (Money Flow Index), `ta.cci()` (Commodity Channel Index), `ta.cmo()` (Chande Momentum Oscillator), `ta.cog()` (Center of Gravity), `ta.dmi()` (Directional Movement Index). Fórmula, interpretación, y código para cada uno.

3. **Tendencia**: `ta.macd()` (retorna tupla [macdLine, signal, histogram]), `ta.supertrend()`, `ta.sar()` (Parabolic SAR), `ta.vwap()`, `ta.dmi()`, `ta.adx()`. Uso combinado para confirmación de tendencia.

4. **Volatilidad**: `ta.atr()` (Average True Range), `ta.tr()` (True Range), `ta.bb()` (Bollinger Bands — retorna [middle, upper, lower]), `ta.bbw()` (BB Width), `ta.kc()` (Keltner Channels — retorna [middle, upper, lower]), `ta.kcw()` (KC Width), `ta.stdev()` (Standard Deviation), `ta.variance()`.

5. **Volumen**: `ta.obv()` (On Balance Volume), `ta.accdist()` (Accumulation/Distribution), `ta.pvt()` (Price Volume Trend), `ta.vwap()`, `ta.mfi()`. Interpretación de cada indicador de volumen.

6. **Detección de Patrones y Cruces**: `ta.crossover()`, `ta.crossunder()`, `ta.cross()`, `ta.rising()`, `ta.falling()`, `ta.change()`. Cómo usar para generar señales de trading.

7. **Pivotes y Extremos**: `ta.pivothigh()`, `ta.pivotlow()`, `ta.highest()`, `ta.lowest()`, `ta.highestbars()`, `ta.lowestbars()`. Detección de soporte y resistencia.

8. **Búsqueda y Conteo**: `ta.barssince()`, `ta.valuewhen()`, `ta.cum()`. Patrones de uso para encontrar condiciones pasadas.

9. **Estadísticas y Regresión**: `ta.correlation()`, `ta.linreg()`, `ta.percentile_linear_interpolation()`, `ta.percentile_nearest_rank()`, `ta.percentrank()`, `ta.median()`, `ta.mode()`.

10. **Funciones Matemáticas Complementarias (`math.*`)**: `math.abs()`, `math.ceil()`, `math.floor()`, `math.round()`, `math.log()`, `math.log10()`, `math.exp()`, `math.pow()`, `math.sqrt()`, `math.sign()`, `math.max()`, `math.min()`, `math.avg()`, `math.sum()`, `math.random()`, `math.todegrees()`, `math.toradians()`, `math.sin()`, `math.cos()`, `math.tan()`, `math.asin()`, `math.acos()`, `math.atan()`.

11. **Warm-up Period y `na`**: Cómo Pine maneja las primeras barras donde los indicadores aún no tienen suficientes datos. Propagación de `na`. Uso de `nz()` y `fixnan()` para manejar valores indefinidos.

12. **Implementación Manual vs Built-in**: Cuándo conviene escribir tu propio cálculo en lugar de usar la función built-in. Diferencias de rendimiento. Customización de parámetros.

13. **3 Combinaciones Prácticas Implementadas**:
    - Sistema de confluencia: combinar RSI + MACD + Supertrend para scoring de señales
    - Detector de régimen de mercado: usar ATR + ADX + Bollinger Band Width para clasificar trending/ranging/volatile
    - Scanner de divergencias: RSI divergence detector con labels automáticos

Extensión esperada: al menos 7000 palabras, con código funcional para cada función y las 3 implementaciones completas.
```

---

## Prompt 07: Sistema de Alertas y Webhooks de TradingView

```
Genera un informe técnico exhaustivo sobre el sistema de alertas y webhooks de TradingView, cubriendo desde la configuración básica hasta la automatización avanzada de trading.

El informe debe cubrir en profundidad, con ejemplos concretos:

1. **Tipos de Alertas Nativas**: Alertas sobre precio (crossing, moving up, moving down, greater than, less than, entering channel, exiting channel, moving up %, moving down %). Alertas sobre indicadores técnicos. Alertas sobre drawing tools (líneas de tendencia, canales).

2. **Alertas Basadas en Indicadores Pine**: Cómo usar `alertcondition()` en indicadores para que los usuarios de tu indicador puedan configurar alertas. Parámetros: title, message, condición. Limitaciones (no funciona en estrategias). Múltiples alertconditions en un mismo indicador.

3. **Función `alert()` en Pine**: Sintaxis y parámetros. `alert.freq_once_per_bar`, `alert.freq_once_per_bar_close`, `alert.freq_all`. Diferencia con `alertcondition()`. Cuándo usar cada una. Cómo incluir datos dinámicos en el mensaje (precio, símbolo, valores de indicadores).

4. **Alertas de Estrategias**: Cómo `strategy.entry()`, `strategy.exit()`, `strategy.close()` generan alertas automáticamente. `alert_message` parameter en funciones de estrategia. Configuración de la alerta para la estrategia completa.

5. **Webhook Configuration**: Cómo configurar un webhook URL en la alerta. Formatos de payload (JSON, texto plano). Variables de placeholder disponibles: `{{ticker}}`, `{{exchange}}`, `{{close}}`, `{{open}}`, `{{high}}`, `{{low}}`, `{{volume}}`, `{{time}}`, `{{timenow}}`, `{{interval}}`, `{{strategy.order.action}}`, `{{strategy.order.contracts}}`, `{{strategy.order.price}}`, `{{strategy.order.id}}`, `{{strategy.market_position}}`, `{{strategy.market_position_size}}`, `{{strategy.prev_market_position}}`.

6. **Diseño de Payloads JSON**: Cómo construir payloads JSON personalizados combinando variables de placeholder con texto estático. Ejemplos de payloads para diferentes casos de uso (broker execution, logging, notificaciones).

7. **Alertas Server-side vs Client-side**: Diferencia crucial entre alertas que corren en el servidor de TradingView (funcionan 24/7 sin tener el gráfico abierto) y alertas client-side. Cuáles funcionalidades requieren el gráfico abierto.

8. **Límites por Plan**: Cuántas alertas activas permite cada plan (Free, Pro, Pro+, Premium, Expert). Rate limits de webhooks. Throttling. Comportamiento cuando se alcanza el límite.

9. **Notificaciones**: Email, push mobile (app de TradingView), pop-up en la app, sonido. Cómo configurar cada canal. Confiabilidad de cada método.

10. **Latencia de Alertas**: Cuánto tiempo pasa desde que la condición se cumple hasta que se dispara la alerta y se envía el webhook. Factores que afectan la latencia. Mediciones reales documentadas. Diferencias entre alertas de precio vs indicador vs estrategia.

11. **Arquitectura de Webhook Receiver**: Cómo diseñar un servidor que reciba webhooks de TradingView. Ejemplo completo en Python (FastAPI) y Node.js (Express). Autenticación (cómo verificar que el webhook viene de TradingView). Handling de errores. Retry logic del lado de TradingView.

12. **Integración con Servicios Externos**: IFTTT, Make (Integromat), Zapier, n8n. Cómo conectar alertas de TradingView con estos servicios para automatización sin código.

13. **Mejores Prácticas de Fiabilidad**: Redundancia (múltiples canales para la misma alerta). Monitoring (cómo saber si un webhook falló). Logging. Alertas sobre las alertas (meta-monitoring).

14. **2 Implementaciones Completas**:
    - Indicador con `alertcondition()` y `alert()` que detecta cruces de medias móviles y envía webhook con payload JSON
    - Servidor webhook en Python (FastAPI) que recibe alertas, las valida, las loggea, y las envía a Telegram

Extensión esperada: al menos 7000 palabras.
```

---

## Prompt 08: Pipeline de Ejecución — TradingView → Broker

```
Genera un informe técnico exhaustivo sobre cómo construir un pipeline completo de automatización de trading que conecte señales de TradingView con la ejecución real en brokers.

El informe debe cubrir en profundidad, con código funcional:

1. **Arquitectura Completa del Pipeline**: Diagrama del flujo completo: TradingView Pine Script → Alerta → Webhook → Middleware/Servidor → API del Broker → Ejecución. Latencia en cada tramo. Puntos de fallo y cómo mitigarlos.

2. **Brokers con Integración Nativa de TradingView**: Lista completa de brokers que permiten trading directo desde TradingView (TradeStation, OANDA, Interactive Brokers, IBKR, Alpaca, Binance, y otros). Diferencias de funcionalidad. Ventajas y limitaciones del trading directo vs pipeline webhook.

3. **Paper Trading de TradingView**: Cómo funciona. Limitaciones. Cuándo usarlo como validación antes de ir a real. Diferencias con el backtester.

4. **Diseño del Middleware (Webhook Receiver)**: Arquitectura de un servidor Python (FastAPI) o Node.js que: recibe webhooks de TradingView, valida la autenticidad, parsea el payload, aplica reglas de risk management, y envía órdenes al broker. Código completo.

5. **Mapping de Símbolos**: Cómo traducir tickers de TradingView (ej: `BINANCE:BTCUSDT`, `NASDAQ:AAPL`, `FX:EURUSD`) a los tickers que cada broker entiende. Tablas de mapping. Automatización del mapping.

6. **Plataformas Bridge Existentes**: PineConnector (TradingView → MT4/Broker). 3Commas. Cornix. Wunderbit. TradingView-to-Brokers bridges. Análisis de cada uno: funcionalidades, costos, latencia, limitaciones.

7. **Ejecución en Diferentes Tipos de Broker**:
   - Ejecución en Plataformas Institucionales (vía PineConnector o webhook → nuestro Gateway FastAPI existente)
   - Ejecución en Interactive Brokers (vía API REST de IBKR)
   - Ejecución en Alpaca (API REST para equities USA)
   - Ejecución en Binance (API REST para crypto)
   - Ejecución en OANDA (API REST para forex)

8. **Risk Management en el Middleware**: Position sizing basado en equity. Maximum drawdown circuit breaker. Rate limiting (máximo N órdenes por hora). Verificación de horario de mercado. Validación de símbolo y volumen. Kill switch manual.

9. **Logging y Auditoría**: Cómo registrar cada alerta recibida, cada orden enviada, cada fill recibido. Base de datos para trade log. Reconciliación de trades (comparar lo que TradingView señaló vs lo que el broker ejecutó).

10. **Latencia End-to-End**: Medición desde que Pine Script detecta la señal hasta que el broker confirma el fill. Benchmarks documentados. Cómo optimizar cada tramo. Impacto de la latencia en el slippage.

11. **Redundancia y Failover**: Qué pasa si el webhook falla. Qué pasa si el broker está caído. Sistemas de retry. Alertas de fallo. Múltiples canales de ejecución. Health checks.

12. **Multi-Broker Execution**: Enviar la misma señal a varios brokers simultáneamente. Casos de uso (arbitraje, diversificación). Implementación con async/await en Python.

13. **Integración con el Gateway del Broker Existente**: Cómo conectar TradingView con el Gateway FastAPI que ya tenemos (en `api.broker.com`). Mapeo de endpoints. Ejemplo de flujo TV Alert → nuestro webhook → Gateway → Broker.

14. **Implementación Completa**: Código funcional de un middleware Python (FastAPI) que:
    - Recibe webhooks de TradingView
    - Valida autenticidad
    - Aplica risk management
    - Envía a Broker vía nuestro Gateway existente
    - Loggea todo en SQLite
    - Envía confirmación a Telegram

Extensión esperada: al menos 8000 palabras.
```

---

## Prompt 09: Integración TradingView ↔ Python y Ecosistema Externo

```
Genera un informe técnico exhaustivo sobre cómo integrar TradingView con Python y otros sistemas externos para análisis avanzado, machine learning, y automatización.

El informe debe cubrir en profundidad, con código funcional:

1. **Librería `tradingview-ta`**: Instalación, configuración. Cómo obtener análisis técnico de TradingView desde Python (señales buy/sell/neutral para indicadores y oscilladores). Todos los campos disponibles. Múltiples timeframes. Rate limits. Ejemplos completos.

2. **Librería `tvdatafeed`**: Extracción de datos históricos de TradingView desde Python. Autenticación. Tipos de datos disponibles. Resoluciones soportadas. Limitaciones (cantidad de barras, rate limits). Datos en tiempo real vs históricos. Integración con pandas DataFrames.

3. **Lightweight Charts en Python (`lightweight-charts-python`)**: Visualización de gráficos financieros profesionales en Python. Instalación. Tipos de series (Candlestick, Line, Area, Bar, Histogram). Personalización de colores, temas, escalas. Múltiples panels. Interactividad (hotkeys, screenshots). Integración con datos propios.

4. **Pipeline de Machine Learning**: Flujo completo: Datos (de TradingView o API de broker) → Feature Engineering (indicadores técnicos, datos fundamentales) → Training (scikit-learn, XGBoost, LSTM) → Predicción → Señal de vuelta a TradingView (vía `request.seed()` o webhook inverso). Código completo de cada etapa.

5. **Feature Engineering para Trading**: Cómo transformar datos raw de TradingView en features útiles para ML. Normalización, lag features, rolling windows, cross-sectional features. Uso de `ta` functions en Python (equivalentes a las de Pine).

6. **`request.seed()` — Custom Data en TradingView**: Cómo publicar datos propios (señales ML, datos alternativos, métricas custom) para que estén disponibles en Pine Script. Pine Seeds API. Proceso de publicación. Actualización periódica.

7. **Bots de Notificación**: Cómo construir bots que consuman alertas de TradingView y las envíen a:
   - Telegram (con python-telegram-bot)
   - Discord (con discord.py)
   - Slack (con slack-sdk)
   - Email (con smtplib)
   Código completo para cada plataforma.

8. **Herramientas de Desarrollo Pine Script**:
   - VSCode extensions para Pine Script (syntax highlighting, snippets)
   - Linters y formatters
   - Versionamiento de scripts Pine (Git)
   - CI/CD para scripts (testing automatizado)
   - Pine Script documentation generators

9. **APIs de Brokers para Execution Layer**: Guía comparativa de APIs REST de brokers comunes:
   - Interactive Brokers (Client Portal API, TWS API)
   - Alpaca (API v2 para equities USA, Paper Trading)
   - Binance (API REST y WebSocket para crypto)
   - OANDA (API v20 para forex)
   - Kraken (API REST para crypto)
   Para cada uno: autenticación, endpoints principales, rate limits, sandbox/demo.

10. **Cloud Deployment para Automatización**: Cómo desplegar el middleware de trading en:
    - AWS Lambda (serverless, event-driven)
    - Google Cloud Functions
    - Railway / Render / Fly.io (PaaS simples)
    - VPS propio (DigitalOcean, Contabo, Vultr)
    Pros/contras de cada opción. Costos estimados. Ejemplo de deployment completo.

11. **Base de Datos para Trading**: Opciones de almacenamiento:
    - SQLite (simple, local)
    - PostgreSQL (producción)
    - TimescaleDB (time-series optimized)
    - InfluxDB (métricas)
    Schema sugerido para trade log, alertas, rendimiento. Código de creación.

12. **Dashboards de Rendimiento**: Cómo construir dashboards para monitorear el rendimiento del sistema:
    - Streamlit (Python, rápido de prototipar)
    - Grafana (métricas y time-series)
    - HTML estático con Chart.js (como el que ya tenemos en Broker)
    Métricas a mostrar: PnL, drawdown, win rate, alertas recibidas, latencia.

13. **Integración con Jupyter Notebooks**: Cómo usar notebooks para análisis interactivo con datos de TradingView. Visualización con Lightweight Charts. Backtesting offline con vectorbt o backtrader. Research workflow completo.

Extensión esperada: al menos 8000 palabras.
```

---

## Prompt 10: Gestión de Riesgo y Position Sizing en Pine Script

```
Genera un informe técnico exhaustivo sobre la implementación de gestión de riesgo y position sizing en estrategias Pine Script de TradingView.

El informe debe cubrir en profundidad, con código funcional completo:

1. **`strategy.exit()` en Detalle**: Todos los parámetros — from_entry, qty, qty_percent, profit (en ticks), loss (en ticks), limit (precio absoluto), stop (precio absoluto), trail_price, trail_points, trail_offset, when, comment, comment_profit, comment_loss, comment_trailing, alert_message. Diferencia entre profit/loss (relativo) y limit/stop (absoluto). Múltiples exits para la misma entrada.

2. **Trailing Stop Avanzado**: `trail_points` y `trail_offset` en detalle con diagramas textuales. Cómo funciona el trailing: precio de activación, distancia de seguimiento. Trailing stop basado en ATR. Chandelier Exit. Parabolic SAR como trailing stop. Código funcional para cada variante.

3. **Position Sizing Dinámico**: 
   - Fixed Fractional (% del equity por trade)
   - Fixed Ratio
   - Kelly Criterion (implementación en Pine)
   - Volatility-based sizing (ATR-based)
   - Cálculo de lots/shares basado en distancia del stop loss
   - `strategy.equity` vs `strategy.initial_capital` para sizing
   - `default_qty_type` = strategy.percent_of_equity vs strategy.fixed vs strategy.cash

4. **Risk Per Trade**: Cómo calcular el riesgo por trade en Pine. Fórmula: `qty = (equity * risk_pct) / (entry_price - stop_price)`. Ajuste por contract size. Ajuste por apalancamiento. Redondeo a lot size mínimo. Código completo.

5. **Stop Loss Strategies**: 
   - SL fijo en puntos/pips
   - SL basado en ATR (ej: 2x ATR)
   - SL basado en estructura de mercado (swing low/high)
   - SL basado en Bollinger Bands
   - SL en percentile de rango reciente
   Código funcional para cada tipo.

6. **Take Profit Strategies**:
   - TP fijo con ratio R:R (ej: 2:1, 3:1)
   - TP parcial (tomar 50% en 1R, 50% en 2R)
   - TP basado en Fibonacci extensions
   - TP trailing (dejar correr el ganador)
   - Múltiples targets con `strategy.exit()` usando `qty_percent`

7. **Break-Even Stops**: Cómo mover el SL al precio de entrada después de que el trade alcance cierto profit. Implementación en Pine usando `strategy.opentrades.entry_price()` y `strategy.exit()` condicional.

8. **Pyramiding y Scaling**: Configuración de `pyramiding` en `strategy()`. Cómo añadir a posiciones ganadoras. Dollar Cost Averaging en Pine. Grid strategies. Riesgos del pyramiding.

9. **Portfolio-Level Risk**: `strategy.risk.max_drawdown()`, `strategy.risk.max_position_size()`, `strategy.risk.max_intraday_filled_orders()`, `strategy.risk.max_intraday_loss()`, `strategy.risk.allow_entry_in()`. Cómo usar estas funciones como circuit breakers.

10. **Commission y Slippage Modeling**: Configuración realista en `strategy()`. `commission_type` (percent, cash_per_contract, cash_per_order). `slippage` en ticks. Impacto en las métricas de rendimiento. Cómo ajustar para diferentes tipos de activos.

11. **Drawdown Monitoring**: Cómo calcular y monitorear drawdown en tiempo real dentro de Pine. `strategy.max_drawdown`. Custom drawdown calculation. Alertas de drawdown. Circuit breaker automático (cerrar todas las posiciones si drawdown > X%).

12. **Margin y Leverage**: `margin_long` y `margin_short` en `strategy()`. Cómo afectan el sizing y el equity. Margin call simulation. Diferencias en margin entre forex, crypto, equities.

13. **Comparativa con MQL5**: Cómo se implementan estas mismas funcionalidades en MQL5/Broker vs Pine Script. Ventajas y limitaciones de cada plataforma para risk management.

14. **3 Implementaciones Completas**:
    - Estrategia con position sizing ATR-based, trailing stop, y break-even automático
    - Estrategia con pyramiding controlado (máximo 3 entradas), partial TP, y drawdown circuit breaker
    - Módulo de risk management reutilizable (library Pine) con funciones para sizing, SL, TP, y monitoring

Extensión esperada: al menos 8000 palabras.
```

---

## Notas para el Uso

### Cómo usar estos prompts:
1. Abre una nueva sesión de **Gemini Deep Research**
2. Copia y pega UN prompt completo
3. Deja que el agente investigue y genere el documento
4. Guarda el resultado como archivo `.md` en el directorio `knowledge/` del nuevo proyecto TradingView

### Orden de ejecución recomendado:
```
Prompt 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10
```

### Después de la Generación 1:
- Crear el INDEX.md (como en Broker)
- Evaluar gaps de cobertura
- Generar los 10 prompts de la Generación 2 (Líneas 11-20)
