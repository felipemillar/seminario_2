# [SIGNAL] Prompts para Gemini Deep Research — TradingView (Generación 2)

> **Instrucciones de uso**: Copia y pega cada prompt en una sesión nueva de Gemini Deep Research. Cada prompt generará un documento de ~50-120 KB que guardaremos en `knowledge/`.
> **Fecha de creación**: 2026-07-11
> **Nota crítica**: Cada prompt incluye una sección "Ya documentado — NO cubrir" para evitar duplicación con los 10 documentos de Gen 1.

---

## Prompt 11: Ecosistema y Modelo de Negocio de TradingView

```
Genera un informe exhaustivo sobre el ecosistema comercial, social y empresarial de TradingView como plataforma integral de análisis financiero.

CONTEXTO: Ya tenemos documentada la arquitectura técnica interna de TradingView (microservicios, Kubernetes, pipeline de datos, motor de renderizado). Este informe debe enfocarse en el ECOSISTEMA DE NEGOCIO, no en la tecnología subyacente.

El informe debe cubrir en profundidad:

1. **Modelo de Negocio y Monetización**: Estructura completa de planes de suscripción (Basic, Essential, Plus, Premium, Expert, Ultimate). Ingresos por suscripciones, publicidad, datos de mercado premium, y comisiones de brokerage. Modelo freemium y tasas de conversión estimadas. Historia financiera de la empresa (valuación, rondas de inversión, posible IPO).

2. **TradingView Social Network**: Sistema de Ideas (publicaciones de análisis). Perfiles de usuario, reputación y seguidores. Scripts públicos vs privados vs invite-only. Sistema de likes, comentarios y engagement. Cómo funciona la viralidad del contenido financiero. Moderación y políticas de contenido.

3. **TradingView Market (Pine Marketplace)**: Proceso completo para publicar indicadores/estrategias de pago. Requisitos de calidad, revisión de código, y políticas de publicación. Modelo de revenue-sharing entre desarrollador y TradingView. Precios típicos del mercado. Estrategias exitosas de monetización. Protección de propiedad intelectual (invite-only scripts). Métricas de éxito y descubrimiento.

4. **TradingView Brokerage Integration**: Modelo de integración para brokers (Broker API). Proceso de onboarding de un broker en la plataforma. Brokers integrados por región (EE.UU., Europa, Asia, Latam). Ingresos por comisiones compartidas con brokers. Diferencias entre Paper Trading y trading real a través de brokers integrados.

5. **TradingView para Empresas (B2B)**: Charting Library como producto empresarial (solo overview, no técnico). Lightweight Charts (open source) como estrategia de adquisición. Clientes conocidos que usan la Charting Library. Modelo de licenciamiento empresarial.

6. **Competidores y Posicionamiento**: Comparativa detallada con TrendSpider (IA y scanner), Finviz (screener fundamental), StockCharts (charting clásico), Sierra Chart (trading profesional), QuantConnect (backtesting Python), Plataformas Institucionales (ecosistema de ejecución). Fortalezas y debilidades relativas. Cuota de mercado estimada.

7. **Diferencias Regionales**: Disponibilidad de exchanges y datos por país/región. Restricciones regulatorias (MiFID II en Europa, SEC en EE.UU.). Mercados con mejor vs peor cobertura. Idiomas soportados en la plataforma.

8. **Programa de Afiliados y Partnerships**: Estructura del programa de afiliados. Partnerships con medios financieros, educadores y creadores de contenido. Integración con plataformas educativas.

9. **Historial de Evolución y Roadmap**: Timeline desde la fundación (2011) hasta la actualidad (2026). Hitos clave (Pine Script v1→v6, lanzamiento de app móvil, integración de brokers, heatmaps, screeners). Funcionalidades recientemente añadidas y dirección futura conocida.

10. **Comunidad de Desarrolladores Pine**: Foros de soporte, documentación oficial, TradingView blog técnico. Eventos, competiciones y hackathons. Influencers clave del ecosistema Pine Script.

NO cubrir en este documento (ya documentado en Gen 1):
- Arquitectura técnica interna (microservicios, Kafka, WebSockets)
- Detalles técnicos de Pine Script como lenguaje de programación
- Pipeline de datos de mercado (exchanges → servidores → cliente)
- Límites técnicos por plan (indicadores por gráfico, alertas, barras históricas)
- Motor de renderizado de gráficos (Canvas, WebGL)
```

---

## Prompt 12: Interfaz de Usuario y Funcionalidades Nativas de TradingView

```
Genera una guía técnica exhaustiva sobre todas las funcionalidades nativas de la interfaz de usuario de TradingView que están disponibles SIN necesidad de escribir código Pine Script.

CONTEXTO: Ya tenemos documentado Pine Script (lenguaje, indicadores, estrategias, funciones ta.*). Este informe debe enfocarse en las HERRAMIENTAS NATIVAS de la plataforma que el usuario puede usar directamente desde la interfaz gráfica.

El informe debe cubrir en profundidad:

1. **Tipos de Gráficos Nativos**: Documentar TODOS los tipos de gráficos disponibles en TradingView, con su interpretación analítica y casos de uso óptimos:
   - Candlestick, Hollow Candles, Bars (OHLC)
   - Heikin Ashi: cómo se calculan, ventajas para detección de tendencia, trampas a evitar
   - Renko: configuración de tamaño de bloque (ATR vs fijo), uso para soporte/resistencia limpio
   - Kagi: lógica de reversal, uso para niveles clave
   - Point & Figure: box size, reversal factor, patrones clásicos P&F
   - Line Break: configuración de líneas (2, 3, 4), interpretación
   - Range: barras basadas en rango de precio fijo
   - Volume Footprint y Volume Profile (planes premium)
   - Baseline, Area, Columns, High-Low

2. **Herramientas de Dibujo Completas**: Catálogo exhaustivo de TODAS las herramientas de dibujo organizadas por categoría:
   - Fibonacci: Retrocesos, extensiones, abanico, arcos, espiral, canales, zonas de tiempo
   - Gann: Abanico de Gann, cuadrado de Gann, box de Gann
   - Pitchfork: Andrews, Schiff, Inside, variantes
   - Elliott Wave: herramienta de conteo de ondas, reglas y guías
   - Patrones Armónicos: Gartley, Butterfly, Bat, Crab, Shark, Cypher — reconocimiento y ratios
   - Canales: paralelos, regresión, Fib channel
   - Formas geométricas: rectángulos, elipses, triángulos, arcos
   - Proyecciones: regresión de tendencia, fecha/precio, rango de precios
   - Herramientas de medición: Long/Short Position tool, rangos, porcentajes

3. **Indicadores Built-in**: Taxonomía completa de los 200+ indicadores nativos:
   - Categorías: Tendencia, Momentum, Volatilidad, Volumen, Osciladores, Fundamentales
   - Los 20 indicadores más populares con configuración óptima
   - Indicadores exclusivos de TradingView (no disponibles en otras plataformas)
   - Cómo combinar indicadores nativos sin código (multi-indicador visual)

4. **Watchlists y Gestión de Activos**: Creación y organización de watchlists. Columnas personalizables. Importación/exportación. Watchlists de la comunidad. Listas predefinidas (S&P 500, NASDAQ 100, criptomonedas por capitalización). Coloring condicional. Alerts desde watchlists.

5. **Stock Screener Nativo**: Filtros disponibles por categoría (técnicos, fundamentales, descriptivos). Combinación de filtros lógicos. Screener de acciones, forex, crypto — diferencias de campos. Exportación de resultados. Screener en tiempo real vs snapshot.

6. **Heatmap de Mercado**: Métricas de tamaño (market cap, volumen). Métricas de color (cambio %, rendimiento YTD, etc.). Navegación por sectores e industrias. Heatmap de criptomonedas. Personalización y uso práctico para detección de oportunidades.

7. **Multi-Chart Layouts**: Layouts de 2, 4, 8, 16 gráficos. Sincronización entre paneles (símbolo, intervalo temporal, crosshair). Templates de layouts. Layouts en múltiples monitores. Gestión de pestañas y workspaces.

8. **Replay Mode (Simulador de Mercado)**: Funcionamiento del Bar Replay. Velocidades disponibles. Limitaciones (resoluciones, datos históricos). Uso para práctica de trading y análisis retrospectivo. Diferencias con forward testing real.

9. **Paper Trading Nativo**: Activación y configuración. Panel de órdenes. Tipos de órdenes disponibles (market, limit, stop, stop-limit). Portfolio virtual y P&L tracking. Limitaciones vs trading real. Realismo de los fills simulados.

10. **DOM (Depth of Market) y Order Book**: Exchanges que soportan DOM en TradingView. Visualización del libro de órdenes. Time & Sales. Uso práctico para scalping y análisis de flujo de órdenes.

11. **Calendario Económico y Datos Fundamentales**: Calendario integrado de eventos económicos. Earnings calendar. Datos fundamentales de acciones (P/E, EPS, Revenue, etc.). Comparativas de empresas. Información de dividendos.

12. **Pine Editor (IDE Integrado)**: Capacidades del editor (syntax highlighting, autocompletado, snippets). Panel de errores y warnings. Gestión de versiones de scripts. Publicación de scripts. Vinculación con la documentación oficial.

13. **Hotkeys y Personalización**: Catálogo completo de atajos de teclado por categoría. Personalización del workspace (temas, colores, fuentes). Configuración de alertas rápidas. Favoritos y acceso rápido a herramientas.

NO cubrir en este documento (ya documentado en Gen 1):
- Programación en Pine Script (el código de los indicadores)
- Funciones ta.* o math.* de Pine Script
- strategy() y backtesting desde código
- Arquitectura técnica interna de la plataforma
- Sistema de alertas desde Pine Script (alert(), alertcondition())
```

---

## Prompt 13: Pine Script Avanzado — Arrays, Matrices, Maps y Patrones de Diseño

```
Genera un manual técnico exhaustivo de las estructuras de datos avanzadas y patrones de diseño de software en Pine Script v6.

CONTEXTO: Ya tenemos documentado el sistema de tipos básico de Pine Script v6 (int, float, bool, string, color, na, qualifiers const/input/simple/series), el modelo de ejecución barra-por-barra, variables var/varip, UDTs a nivel introductorio, y methods básicos. Este documento debe PROFUNDIZAR en las capacidades avanzadas que permiten construir sistemas profesionales complejos.

El informe debe cubrir en profundidad, con código funcional para cada concepto:

1. **Arrays en Profundidad**: 
   - Declaración tipada: array.new<int>(), array.new<float>(), array.new<string>(), array.new<color>(), array.new<line>(), array.new<label>()
   - TODAS las operaciones: push, pop, shift, unshift, insert, remove, set, get, first, last, size, clear
   - Sorting: array.sort(), array.sort_indices()
   - Slicing: array.slice(), array.copy(), array.concat()
   - Búsqueda: array.includes(), array.indexof(), array.lastindexof(), array.binary_search(), array.binary_search_leftmost(), array.binary_search_rightmost()
   - Estadísticas: array.avg(), array.sum(), array.min(), array.max(), array.stdev(), array.variance(), array.median(), array.mode(), array.range(), array.covariance(), array.percentile_linear_interpolation(), array.percentile_nearest_rank(), array.percentrank()
   - Iteración: for...in loops con arrays
   - Arrays de objetos gráficos (line[], label[], box[])
   - Patrones: rolling windows, buffers circulares, pilas (LIFO) y colas (FIFO) con arrays
   - Rendimiento: impacto en memoria y tiempo de ejecución con arrays grandes

2. **Matrices (matrix.*)**:
   - Declaración: matrix.new<type>(rows, columns, initial_value)
   - Acceso: matrix.get(), matrix.set(), matrix.row(), matrix.col()
   - Operaciones matriciales: matrix.add(), matrix.mult(), matrix.diff(), matrix.sum(), matrix.avg()
   - Álgebra lineal: matrix.det(), matrix.inv(), matrix.transpose(), matrix.eigenvalues(), matrix.eigenvectors(), matrix.rank(), matrix.trace(), matrix.pinv()
   - Reshape: matrix.reshape(), matrix.reverse(), matrix.swap_rows(), matrix.swap_columns()
   - Conversión: matrix.submatrix(), arrays a matrices y viceversa
   - Casos de uso reales: tablas de correlación entre activos, matrices de covarianza para portfolio optimization, regresión lineal múltiple implementada con matrices

3. **Maps (map.*)**:
   - Declaración tipada: map.new<string, float>(), map.new<int, string>(), etc.
   - Operaciones: map.put(), map.get(), map.contains(), map.remove(), map.clear(), map.size()
   - Iteración: map.keys(), map.values()
   - Casos de uso: almacenamiento de niveles de soporte/resistencia por símbolo, diccionarios de configuración, registros de trades activos, lookup tables para traducción de símbolos

4. **User Defined Types (UDT) — Profundización**:
   - Declaración avanzada con campos opcionales y valores por defecto
   - Constructors con .new() y factory methods
   - Métodos encadenados (method chaining)
   - UDTs anidados (tipos que contienen otros tipos)
   - Arrays de UDTs y Maps de UDTs
   - Export/import de UDTs en librerías
   - State machines implementadas con UDTs
   - Event-driven patterns en un lenguaje barra-por-barra

5. **request.security() Avanzado**:
   - barmerge: barmerge.gaps_on vs gaps_off
   - Lookahead: barmerge.lookahead_on vs lookahead_off — cuándo es seguro usarlo
   - Expresiones complejas dentro de request.security(): tuplas, arrays, UDTs como retorno
   - Riesgo de repainting: cómo detectarlo y prevenirlo
   - Límite de 40 llamadas: estrategias para no excederlo

6. **request.security_lower_tf()**: acceso a timeframes inferiores, formato de retorno, casos de uso

7. **ticker.* — Manipulación de Símbolos**:
   - ticker.new(), ticker.modify(), ticker.heikinashi(), ticker.renko(), ticker.kagi(), ticker.linebreak(), ticker.pointfigure(), ticker.standard()

8. **Patrones de Diseño de Software en Pine Script**:
   - State Machine Pattern, Strategy Pattern, Observer Pattern simulado, Builder Pattern, Singleton Pattern con var
   - Anti-patterns comunes en Pine

9. **Manejo de Errores y Edge Cases Avanzado**: cascada de na, nz(), fixnan(), overflow numérico, gaps de mercado

NO cubrir en este documento (ya documentado en Gen 1):
- Sistema de tipos básico (int, float, bool, string, color)
- Modelo de ejecución barra-por-barra (histórico vs real-time)
- Variables var y varip (comportamiento básico)
- Operadores y control de flujo básico (if/else, for, while)
- Funciones ta.* (catálogo de indicadores técnicos)
- request.financial(), request.economic(), request.dividends(), request.earnings(), request.splits()
```

---

## Prompt 14: Visualización Avanzada en Pine Script — Tables, Polylines y Dashboards

```
Genera un manual técnico exhaustivo sobre las capacidades avanzadas de visualización y construcción de dashboards en Pine Script v6.

CONTEXTO: Ya tenemos documentado el sistema básico de plots (plot(), plotshape(), plotchar()), labels, lines y boxes a nivel introductorio, hline(), fill(), y los fundamentos de color.rgb() y color.from_gradient(). Este documento debe PROFUNDIZAR en las herramientas avanzadas de visualización que permiten construir interfaces profesionales dentro del gráfico.

El informe debe cubrir en profundidad, con código funcional completo para cada concepto:

1. **table.new() — Sistema Completo de Tablas**:
   - Declaración: table.new(position, columns, rows, bgcolor, frame_color, frame_width, border_color, border_width)
   - Posiciones: position.top_left, top_center, top_right, middle_left, middle_center, middle_right, bottom_left, bottom_center, bottom_right
   - table.cell(): text, width, height, text_color, bgcolor, text_halign, text_valign, text_size, text_font_family, tooltip
   - table.merge_cells(): combinación de celdas
   - table.delete(), table.clear(): gestión del ciclo de vida
   - Rendimiento: cuándo crear la tabla una sola vez con var vs recrearla en cada barra

2. **Patrones de Dashboard Profesional**:
   - Dashboard multi-timeframe: señales en múltiples marcos temporales usando request.security()
   - Screener in-chart: múltiples símbolos con coloring condicional
   - Panel de estadísticas de estrategia en tiempo real
   - Dashboard de correlación: matriz NxN con gradiente de color
   - Panel de análisis técnico consolidado

3. **polyline.new() — Dibujo de Formas Complejas**:
   - chart.point.new(), polilíneas abiertas vs cerradas, curvas suavizadas
   - Límites y casos de uso

4. **linefill.new() — Rellenos entre Líneas**: bandas dinámicas, rellenos personalizados

5. **line.new() — Uso Avanzado**: coordenadas de tiempo vs barras, extensiones, estilos, gestión de ciclo de vida, garbage collection

6. **box.new() — Zonas Rectangulares Avanzadas**: zonas de oferta/demanda, marking de sesiones, boxes con texto

7. **label.new() — Anotaciones Avanzadas**: tooltips dinámicos, estilos, text_font_family, paneles flotantes

8. **Sistema de Color Avanzado**: color.from_gradient() basado en datos, paletas profesionales (viridis, magma), heatmaps con datos, transparencia dinámica, adaptación a temas

9. **Gestión de Límites de Objetos**: max_lines_count, max_labels_count, max_boxes_count, max_polylines_count, garbage collection manual

10. **Implementaciones Completas de Referencia**:
    - Dashboard profesional multi-timeframe (script completo)
    - Indicador de zonas de soporte/resistencia con boxes y labels (script completo)
    - Panel de análisis con heatmap de correlación en tabla (script completo)

NO cubrir en este documento (ya documentado en Gen 1):
- plot(), plotshape(), plotchar(), plotarrow() básicos
- hline() y fill() básico
- indicator() declaration
- Input system (input.int, input.float, etc.)
- color.new() básico con constantes predefinidas
```

---

## Prompt 15: Screeners, Heatmaps y Análisis Multi-Activo en TradingView

```
Genera un informe técnico exhaustivo sobre las herramientas de screening, heatmaps y análisis multi-activo disponibles en la plataforma TradingView.

CONTEXTO: Ya tenemos documentado Pine Script (lenguaje, indicadores, estrategias), el sistema de datos de mercado (proveedores, resoluciones, request.security()), y las alertas/webhooks. Este documento debe enfocarse en las capacidades de ANÁLISIS MULTI-ACTIVO que son exclusivas de TradingView y no tienen equivalente en Plataformas Institucionales.

El informe debe cubrir en profundidad:

1. **Stock Screener Nativo**: Arquitectura del screener, filtros técnicos (RSI, MACD, cruces de medias, volumen relativo, ATR), filtros fundamentales (P/E, P/B, EPS, Revenue, Market Cap, Dividend Yield, ROE), filtros descriptivos (sector, industria, país, exchange), combinación AND/OR, columnas personalizables, exportación.

2. **Crypto Screener**: Campos exclusivos de crypto, filtros por blockchain/categoría DeFi/NFT/Layer2, exchanges cubiertos, métricas on-chain.

3. **Forex Screener**: Filtros específicos de pares, cross rates, análisis de fuerza de moneda, filtros por carry trade.

4. **Heatmap de Mercado**: Estructura jerárquica (mercado→sectores→industrias→empresas), métricas de tamaño y color, heatmap por índices, heatmap de crypto, personalización, uso para rotación sectorial.

5. **Pine Screener (Screener Programático)**: Screeners con Pine Script, request.security() para múltiples símbolos, rankings y scoring systems, limitaciones.

6. **Análisis Sectorial y Rotación**: Comparación de sectores, Relative Rotation Graphs, breadth indicators, líderes y rezagados.

7. **Watchlists Avanzadas**: Columnas personalizadas, coloring condicional, importación/exportación, alertas desde watchlists.

8. **Análisis de Correlación**: Overlay de activos, spread charts, ratios, correlación rolling con ta.correlation().

9. **Datos de Opciones**: Cadenas de opciones, volatilidad implícita, Greeks, Open Interest, Put/Call ratios.

10. **Renta Fija, Yields y Macroeconomía**: Curvas de rendimiento, spreads de crédito, datos de bancos centrales, indicadores macro integrados.

NO cubrir en este documento (ya documentado en Gen 1):
- Código Pine Script de funciones ta.*
- request.security() a nivel técnico/código
- request.financial() y request.economic() — endpoints específicos
- Pipeline de datos de mercado
- Alertas y webhooks
```

---

## Prompt 16: TradingView Charting Library y Lightweight Charts — API Empresarial

```
Genera un informe técnico exhaustivo sobre las APIs de gráficos empresariales de TradingView: la Charting Library (licenciada) y la Lightweight Charts (open source).

CONTEXTO: Ya tenemos documentado Pine Script como lenguaje, el motor de renderizado interno de TradingView, y la integración Python con lightweight-charts-python. Este documento debe enfocarse en el uso de estas librerías como HERRAMIENTAS DE DESARROLLO para construir plataformas propias.

El informe debe cubrir en profundidad, con código de ejemplo:

1. **TradingView Charting Library (Advanced Charts)**: Qué es, modelo de licenciamiento, arquitectura, inicialización (TradingView.widget()), Datafeed API (onReady, searchSymbols, resolveSymbol, getBars, subscribeBars), Broker API (placeOrder, modifyOrder, cancelOrder), personalización visual, eventos/callbacks, SaveLoadAdapter, limitaciones.

2. **Lightweight Charts (Open Source)**: Instalación, createChart(), series de datos (Candlestick, Line, Area, Bar, Baseline, Histogram), marcadores, múltiples paneles, personalización, eventos, responsive design, plugins, React/Vue/Angular integration.

3. **Datafeed API — Implementación Completa**: Backend Python (FastAPI) que sirve datos OHLCV, WebSocket para streaming, formatos de resolución, caché.

4. **Trading Terminal Widget**: Widget extendido para brokers con panel de trading, Account Manager.

5. **Widget de Gráfico Embebible (Gratuito)**: Mini Chart, Advanced Chart, Ticker Tape, Screener, Symbol Overview, Economic Calendar.

6. **Comparativa con Competidores**: HighCharts Stock, ApexCharts, Plotly/Dash, D3.js, AnyChart Stock.

7. **Ejemplo de Implementación Completa**: Dashboard financiero con Lightweight Charts + backend Python.

NO cubrir en este documento (ya documentado en Gen 1):
- Pine Script como lenguaje de programación
- Motor de renderizado interno de TradingView.com (Canvas, WebGL, path batching)
- lightweight-charts-python (librería Python)
- Webhook receivers o automatización de trading
```

---

## Prompt 17: Metodología Avanzada de Backtesting — Validación Estadística y Robustez

```
Genera un informe técnico exhaustivo sobre la metodología estadística de backtesting, validación de estrategias y detección de overfitting, con enfoque en TradingView y herramientas complementarias en Python.

CONTEXTO: Ya tenemos documentada la MECÁNICA del backtester de TradingView (strategy(), strategy.entry(), strategy.exit(), trailing stops, Deep Backtesting, métricas del Strategy Tester). Este documento debe enfocarse en la METODOLOGÍA ESTADÍSTICA de validación.

El informe debe cubrir en profundidad, con código de ejemplo:

1. **Walk-Forward Analysis (WFA)**: Teoría, IS vs OOS, Rolling vs Anchored WFA, implementación en Python (backtrader/vectorbt), Walk-Forward Efficiency, pipelines Pine→Python.

2. **Monte Carlo Simulation**: Tipos (shuffling, perturbación, bootstrapping), métricas, implementación en Python con 10,000 permutaciones.

3. **Deflated Sharpe Ratio (DSR)**: Fórmula de Bailey & López de Prado, multiple testing, implementación Python.

4. **Correcciones por Multiple Testing**: Bonferroni, Holm-Bonferroni, Benjamini-Hochberg (FDR), aplicación práctica.

5. **Sesgos del Backtester de TradingView**: Look-ahead, survivorship, overfitting, selection, data-snooping, repainting — checklist de detección.

6. **Optimización de Hiperparámetros**: Grid search, Bayesian Optimization (Optuna), plateau detection, parameter sensitivity analysis.

7. **Stress Testing**: Eventos extremos (COVID, Flash Crash), gap simulation, slippage extremo.

8. **Forward Testing**: Paper trading como validación, criterios de aprobación, comparación backtest vs forward test.

9. **Pipeline Completo de Validación**: 7 fases desde idea hasta producción con criterios numéricos.

10. **Comparativa de Frameworks**: TradingView vs backtrader vs vectorbt vs QuantConnect.

NO cubrir en este documento (ya documentado en Gen 1):
- Cómo declarar strategy() y sus parámetros
- strategy.entry(), strategy.exit() — mecánica de funciones
- Métricas del Strategy Tester de TradingView
- Deep Backtesting como funcionalidad
- Explicación de la API de strategy() (ya documentada)
```

---

## Prompt 18: Patrones y Arquitecturas de Estrategias de Trading Algorítmico en TradingView

```
Genera un catálogo técnico exhaustivo de patrones de estrategias de trading algorítmico implementados en Pine Script v6, organizados por filosofía de mercado.

CONTEXTO: Ya tenemos documentado strategy() y su mecánica, strategy.entry()/exit(), trailing stops, position sizing, gestión de riesgo, y funciones ta.*. Este documento debe enfocarse en los PATRONES DE ALTO NIVEL con implementaciones completas.

El informe debe cubrir con código Pine Script v6 completo para cada patrón:

1. **Trend Following**: MA Crossover (EMA9/21 + ADX filter), Supertrend, Donchian Channel (Turtle Trading), Parabolic SAR + momentum, Ichimoku Cloud completo.

2. **Mean Reversion**: Bollinger Bands, RSI Extremes con filtro de tendencia, Z-Score, Keltner Channel squeeze.

3. **Breakout**: ATR Breakout, Range Breakout, Opening Range Breakout (ORB), Volatility Contraction (VCP), Inside Bar.

4. **Momentum**: ROC Strategy, MACD Divergence, RSI Momentum (>50 como tendencia), Dual Momentum (Antonacci).

5. **Estrategias Multi-Timeframe**: Triple Screen (Elder), filtro de tendencia superior + entrada inferior, problemas de repainting en MTF.

6. **Multi-Indicator Confluence**: Scoring System, Weighted Signal Aggregation, confirmación secuencial.

7. **Market Regime Detection**: ADX trending/ranging, BB Bandwidth, Hurst Exponent, regime-switching strategy.

8. **Pairs Trading**: Cointegración, Z-Score del spread, hedging ratio, ejemplos (GOLD/SILVER, BTC/ETH).

9. **Seasonal/Session-Based**: Day-of-Week, Month-of-Year, Session-Based (London/NY Open), End-of-Day effects.

10. **Event-Driven**: request.economic() para macro, earnings-based, volatilidad pre/post evento.

11. **Strategy Composition**: Combinar estrategias, equity curve trading, kill switch.

NO cubrir (ya documentado): strategy.entry()/exit() mecánica, trailing stops, position sizing, funciones ta.*, métricas del Strategy Tester, commission/slippage modeling.
```

---

## Prompt 19: Infraestructura de Producción — TradingView + Ejecución Cloud

```
Genera un manual técnico exhaustivo sobre cómo diseñar, desplegar y mantener una infraestructura de trading automatizado de producción que use TradingView como fuente de señales y ejecute órdenes en brokers reales.

CONTEXTO: Ya tenemos documentado el pipeline TradingView → Webhook → Middleware → Broker a nivel conceptual, incluyendo un webhook receiver en FastAPI, validación HMAC, clientes de ejecución para 5 brokers, y la arquitectura de 6 capas con análisis de latencia. Este documento debe enfocarse en la OPERACIONALIZACIÓN EN PRODUCCIÓN.

El informe debe cubrir con código y configuraciones:

1. **Arquitecturas de Referencia**: VPS Dedicado (Nginx→FastAPI→PostgreSQL→Broker), Serverless (API Gateway→Lambda→DynamoDB→Broker), Containerizada (Docker/K3s). Tabla comparativa de costo, complejidad, latencia.

2. **SSL/TLS y Seguridad de Red**: Let's Encrypt, Nginx reverse proxy, IP Whitelisting de TradingView, firewall rules, rate limiting.

3. **Base de Datos para Trade Log**: SQLite vs PostgreSQL vs TimescaleDB, schema recomendado (alerts_received, orders_sent, fills_confirmed), backup automático.

4. **Monitoring y Alertas de Sistema**: Healthchecks.io, UptimeRobot, Telegram Bot de notificaciones, logging JSON estructurado, log rotation, Sentry, Grafana+Prometheus.

5. **Dashboard de Rendimiento**: Streamlit dashboard (equity curve, drawdown, P&L), HTML estático con Chart.js.

6. **Disaster Recovery y Redundancia**: Timeout de TradingView, cola de mensajes, retry con exponential backoff, circuit breaker, failover, idempotencia, recovery manual.

7. **Multi-Cuenta y Multi-Broker**: Routing de señales a N cuentas, sizing por cuenta, estados independientes.

8. **Integración con Gateway de Brokers**: TV Alert → Webhook → FastAPI → Broker API (Ej. Interactive Brokers, Binance), mapeo de símbolos, adaptación de payload.

9. **TCO (Total Cost of Ownership)**: Costos por perfil (hobby $30/mo, semi-pro $80/mo, profesional $200/mo).

10. **Logging y Análisis Post-Trade**: Formato de logs, análisis de slippage, desglose de latencia, reportes semanales automatizados.

NO cubrir (ya documentado): Webhook receiver FastAPI con HMAC, clientes de ejecución por broker, presupuesto de latencia teórico, mapeo de símbolos TV→Broker, alertas/webhooks de TradingView.
```

---

## Prompt 20: IA y Agentes para Desarrollo en TradingView

```
Genera un informe técnico exhaustivo sobre cómo usar inteligencia artificial y agentes de programación (Gemini, Claude, GPT) para acelerar el desarrollo de Pine Script y sistemas de trading en TradingView.

CONTEXTO: Este es un documento META — no sobre trading algorítmico per se, sino sobre cómo usar IA como herramienta de desarrollo para ser más productivo en el ecosistema TradingView.

El informe debe cubrir en profundidad:

1. **Capacidades y Limitaciones de IA para Pine Script**: Errores comunes de modelos (mezcla v5/v6, qualifiers incorrectos, repainting, funciones depreciadas). Tabla de qué genera bien la IA vs qué genera mal.

2. **Prompt Engineering para Pine Script**: Templates para indicadores, estrategias, visualización, debugging. Ejemplos de prompts excelentes vs malos con análisis.

3. **Workflow de Desarrollo Asistido (7 Fases)**: Ideación → Pseudocódigo → Generación → Review → Testing → Optimización → Documentación. Ejemplo end-to-end.

4. **Knowledge Management para TradingView**: Estructura SKILL.md/AGENTS.md, organización de carpetas (pine/indicators/, pine/strategies/, knowledge/), versionamiento con Git.

5. **Debugging Asistido por IA**: Errores de compilación comunes, errores de runtime, repainting bugs, uso de log.info(), tabla de errores con diagnóstico.

6. **Code Review — Checklist de Calidad**: Correctness, anti-repainting, rendimiento, robustez, realismo de backtest, legibilidad, seguridad.

7. **Generación Automática de Documentación**: Template para scripts publicados, parámetros con tooltips, screenshots.

8. **Testing Asistido**: Variaciones de parámetros, edge cases, stress testing verbal, comparación de versiones.

9. **Ética y Riesgos**: Responsabilidad legal, disclaimers, automatización sin supervisión, sesgo de confirmación, regulaciones por jurisdicción.

10. **Comparativa de Agentes**: Gemini 2.5, Claude Opus 4, GPT-4o, Antigravity IDE, Cursor, GitHub Copilot — para Pine Script.

11. **Automatización de Publicación**: Versionamiento semántico, changelog, marketing de indicadores, FAQ automatizados.

NO cubrir (ya documentado): Pine Script sintaxis/tipos/funciones, mecánica del backtesting, arquitectura interna de TradingView, integración Python-TradingView.
```

---

## Orden de Ejecución Recomendado

| Prioridad | # | Línea | Justificación |
|---|---|---|---|
| [INACTIVO] Alta | 11 | Ecosistema y Negocio | Contexto fundamental del ecosistema completo |
| [INACTIVO] Alta | 12 | UI Nativa | Dominar la plataforma antes de código avanzado |
| [INACTIVO] Alta | 15 | Screeners/Heatmaps | Funcionalidad avanzada exclusiva del ecosistema |
| [INACTIVO] Alta | 16 | Charting Library | Capacidad empresarial para plataformas propias |
| [PENDIENTE] Media | 13 | Pine Avanzado | Profundización para herramientas profesionales |
| [PENDIENTE] Media | 14 | Visualización Pro | Dashboards in-chart de grado profesional |
| [ACTIVO] Normal | 17 | Metodología Backtest | Rigor estadístico para validar estrategias |
| [ACTIVO] Normal | 18 | Patrones Estrategias | Catálogo de recetas de trading algorítmico |
| [ACTIVO] Normal | 19 | Infraestructura Prod | Operacionalización real del sistema completo |
| [ACTIVO] Normal | 20 | IA y Agentes | Meta-skill para acelerar el desarrollo futuro |
