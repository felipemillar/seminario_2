Catálogo Técnico de Patrones de Trading Algorítmico en Pine Script v6

Paradigma de Ingeniería Cuantitativa en Pine Script v6

El diseño de sistemas automatizados en TradingView ha experimentado una transformación con la consolidación de Pine Script v6^1^. Esta iteración evoluciona desde un entorno de tipado dinámico y evaluación laxa hacia un lenguaje de programación estructurado y optimizado para la ejecución de algoritmos con nivel de producción institucional^1^. La eliminación de estados indeterminados en tipos lógicos (bool ya no admite el valor na)^3^, el procesamiento condicional mediante evaluación por cortocircuito (*short-circuit evaluation*)^1^ y la flexibilización de llamadas externas en ámbitos locales revolucionan la arquitectura de software financiero en esta plataforma^1^.

La selección de la filosofía de mercado y el patrón de diseño correspondientes determina la viabilidad de una estrategia. La siguiente tabla compara los enfoques operativos descritos en este catálogo técnico:

| **Filosofía de Mercado** | **Dimensión Temporal Típica** | **Métrica de Control Crítica** | **Principal Riesgo de Régimen** | **Mecanismo de Cobertura Nativo** |
| --- | --- | --- | --- | --- |
| **Trend Following** | Diaria / Semanal (1D, 1W) | Ratio de Sharpe / Calmar | Consolidación prolongada (*Chop*) | Filtro de fuerza direccional () |
| **Mean Reversion** | Horaria / Intradiaria (1H, 4H) | Desviación de colas estadísticas | Tendencia persistente (*Fat Tails*) | Filtro de tendencia de largo plazo |
| **Breakout** | Intradiaria (5M, 15M, 1H) | Factor de Ganancia (*Profit Factor*) | Rupturas falsas (*Fakeouts*) | Filtros de volumen y compresión ATR |
| **Momentum** | Semanal / Mensual (1W, 1M) | Ratio de Sortino | Pérdida de aceleración abrupta | Dual Momentum (Rotación defensiva) |
| **Pairs Trading** | Diaria (1D) | Estacionaridad del Spread | Ruptura de cointegración histórica | Cobertura dinámica por ratio Beta |
| **Event-Driven** | Evento / Tick (1T, 5M) | Latencia de ejecución / Deslizamiento | Falta de liquidez asimétrica | Filtros de volatilidad pre-anuncio |

1. Trend Following (Seguimiento de Tendencia)

Las estrategias de seguimiento de tendencia operan bajo la hipótesis de que los mercados financieros presentan una persistencia direccional a mediano y largo plazo debido a procesos de incorporación gradual de información fundamental y comportamientos de rebaño de carácter institucional. El núcleo de este enfoque radica en la asimetría de retornos: capturar grandes movimientos unidireccionales mientras se limitan de manera estricta las pérdidas en fases de consolidación lateral.

Modelos y Fórmulas Matemáticas

Medias Móviles Exponenciales ()

La ponderación decreciente asigna mayor peso a las observaciones recientes:

Índice Direccional Medio ()

Mide la fuerza de la tendencia sin importar su dirección, derivado de la normalización del movimiento direccional positivo () y negativo ():

Canales de Donchian

Delimitan los extremos del precio en una ventana temporal :

Ichimoku Cloud completo

Estructura de cinco líneas que representan el consenso de valor, el soporte dinámico y la proyección temporal:

- **Tenkan-sen (Línea de Conversión):**

- **Kijun-sen (Línea de Base):**

- **Senkou Span A (Línea de Proyección A):**

- **Senkou Span B (Línea de Proyección B):**

- **Chikou Span (Línea de Retraso):** Cierre actual proyectado  períodos atrás.

Implementación Completa en Pine Script v6

Pine Script

//@version=6

strategy("Trend Following Unified Master Suite", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

// Selectores de Sistema y Parámetros

sysSelect   = input.string("EMA Crossover", "Sistema Activo", options=["EMA Crossover", "Supertrend", "Donchian Turtle", "Parabolic SAR", "Ichimoku Cloud"])

emaFastLen  = input.int(9, "EMA Rápida longitud")

emaSlowLen  = input.int(21, "EMA Lenta longitud")

adxFilterThreshold = input.float(25.0, "Umbral Filtro ADX")

// Cómputo Global de Indicadores (Garantiza consistencia del historial en Pine v6)

emaFast = ta.ema(close, emaFastLen)

emaSlow = ta.ema(close, emaSlowLen)

[diPlus, diMinus, adxValue] = ta.dmi(14, 14)

isTrending = adxValue > adxFilterThreshold

// 1. MA Crossover (EMA 9/21 + ADX Filter)

maLong  = ta.crossover(emaFast, emaSlow) and isTrending

maShort = ta.crossunder(emaFast, emaSlow) and isTrending

// 2. Supertrend

[supertrendVal, supertrendDir] = ta.supertrend(3.0, 10)

stLong  = ta.change(supertrendDir) < 0

stShort = ta.change(supertrendDir) > 0

// 3. Donchian Channel (Turtle Trading System)

donchianHigh      = ta.highest(high, 20)

donchianLow       = ta.lowest(low, 20)

donchianExitHigh  = ta.highest(high, 10)

donchianExitLow   = ta.lowest(low, 10)

dcLong            = close > donchianHigh[1]

dcShort           = close < donchianLow[1]

// 4. Parabolic SAR + Momentum

psar = ta.sar(0.02, 0.02, 0.2)

psarMomentum = ta.mom(close, 14)

psarLong  = close > psar and psarMomentum > 0.0

psarShort = close < psar and psarMomentum < 0.0

// 5. Ichimoku Cloud Complete

ichimokuHigh(len) => ta.highest(high, len)

ichimokuLow(len)  => ta.lowest(low, len)

tenkan  = (ichimokuHigh(9) + ichimokuLow(9)) / 2.0

kijun   = (ichimokuHigh(26) + ichimokuLow(26)) / 2.0

senkouA = (tenkan + kijun) / 2.0

senkouB = (ichimokuHigh(52) + ichimokuLow(52)) / 2.0

ichimokuLong  = close > senkouA[26] and close > senkouB[26] and tenkan > kijun and close > close[26]

ichimokuShort = close < senkouA[26] and close < senkouB[26] and tenkan < kijun and close < close[26]

// Rutas de Entrada y Salida Condicionadas

var bool runLong  = false

var bool runShort = false

var bool closeLong  = false

var bool closeShort = false

if sysSelect == "EMA Crossover"

    runLong    := maLong

    runShort   := maShort

    closeLong  := ta.crossunder(emaFast, emaSlow)

    closeShort := ta.crossover(emaFast, emaSlow)

else if sysSelect == "Supertrend"

    runLong    := stLong

    runShort   := stShort

    closeLong  := stShort

    closeShort := stLong

else if sysSelect == "Donchian Turtle"

    runLong    := dcLong

    runShort   := dcShort

    closeLong  := close < donchianExitLow[1]

    closeShort := close > donchianExitHigh[1]

else if sysSelect == "Parabolic SAR"

    runLong    := psarLong and ta.change(close > psar) != 0

    runShort   := psarShort and ta.change(close < psar) != 0

    closeLong  := close < psar

    closeShort := close > psar

else if sysSelect == "Ichimoku Cloud"

    runLong    := ichimokuLong and ta.crossover(tenkan, kijun)

    runShort   := ichimokuShort and ta.crossunder(tenkan, kijun)

    closeLong  := ta.crossunder(tenkan, kijun)

    closeShort := ta.crossover(tenkan, kijun)

// Envío de Órdenes a Mercado

if runLong

    strategy.entry("Trend_L", strategy.long)

if runShort

    strategy.entry("Trend_S", strategy.short)

if closeLong

    strategy.close("Trend_L")

if closeShort

    strategy.close("Trend_S")

2. Mean Reversion (Reversión a la Media)

Las estrategias de reversión a la media asumen que el precio de un activo financiero se comporta como un proceso estocástico de retorno a la media (por ejemplo, un proceso de Ornstein-Uhlenbeck)^6^. Las desviaciones extremas respecto a un promedio central o banda de volatilidad representan anomalías temporales de liquidez o sobrerreacciones emocionales que tienden a corregirse^6^.

Modelos y Fórmulas Matemáticas

Bandas de Bollinger ()

Establecen un canal basado en desviaciones estándar () sobre una media aritmética ():

Z-Score del Precio

Mide la distancia de la cotización respecto a su media en unidades de desviación estándar^6^:

Keltner Channel Squeeze

Ocurre cuando la volatilidad histórica de corto plazo (medida por Bollinger Bands) se contrae por debajo de la volatilidad promedio de mediano plazo (medida por los canales de Keltner basados en el Rango Verdadero Medio, ):

Implementación Completa en Pine Script v6

Pine Script

//@version=6

strategy("Mean Reversion Master Suite", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

mrSelect = input.string("Bollinger Bands", "Fórmula Activa", options=["Bollinger Bands", "RSI Trend Filter", "Z-Score Reversion", "Keltner Squeeze"])

// Variables comunes calculadas globalmente (Evita distorsiones de historial)

sma20 = ta.sma(close, 20)

stdev20 = ta.stdev(close, 20)

rsi14 = ta.rsi(close, 14)

ema50 = ta.ema(close, 50)

// 1. Bollinger Bands

bbUpper = sma20 + (2.0 * stdev20)

bbLower = sma20 - (2.0 * stdev20)

bbLong  = ta.crossunder(close, bbLower)

bbShort = ta.crossover(close, bbUpper)

// 2. RSI Extremes con Filtro de Tendencia EMA 200

ema200 = ta.ema(close, 200)

rsiLong  = rsi14 < 30.0 and close > ema200

rsiShort = rsi14 > 70.0 and close < ema200

// 3. Z-Score

zScore = (close - sma20) / stdev20

zLong  = zScore < -2.0

zShort = zScore > 2.0

// 4. Keltner Channel Squeeze (Bollinger Bands dentro de Keltner Channels)

ema20  = ta.ema(close, 20)

atr20  = ta.atr(20)

kcUpper = ema20 + (1.5 * atr20)

kcLower = ema20 - (1.5 * atr20)

isSqueezed = (bbUpper < kcUpper) and (bbLower > kcLower)

// Disparador de ruptura del squeeze con confirmación de oscilador

squeezeLong  = not isSqueezed and isSqueezed[1] and close > bbUpper

squeezeShort = not isSqueezed and isSqueezed[1] and close < bbLower

// Controladores de Transición de Estados en Pine v6

var bool enterL = false

var bool enterS = false

var bool exitL  = false

var bool exitS  = false

if mrSelect == "Bollinger Bands"

    enterL := bbLong

    enterS := bbShort

    exitL  := ta.crossover(close, sma20)

    exitS  := ta.crossunder(close, sma20)

else if mrSelect == "RSI Trend Filter"

    enterL := rsiLong

    enterS := rsiShort

    exitL  := rsi14 >= 50.0

    exitS  := rsi14 <= 50.0

else if mrSelect == "Z-Score Reversion"

    enterL := zLong

    enterS := zShort

    exitL  := zScore >= 0.0

    exitS  := zScore <= 0.0

else if mrSelect == "Keltner Squeeze"

    enterL := squeezeLong

    enterS := squeezeShort

    exitL  := ta.crossunder(close, ema20)

    exitS  := ta.crossover(close, ema20)

// Lógica de Órdenes

if enterL

    strategy.entry("MR_L", strategy.long)

if enterS

    strategy.entry("MR_S", strategy.short)

if exitL

    strategy.close("MR_L")

if exitS

    strategy.close("MR_S")

3. Breakout (Ruptura)

Las estrategias de ruptura se basan en el principio de que los rangos estrechos de precios acumulan energía transaccional^9^. Cuando el precio vulnera los límites de una consolidación, la activación masiva de órdenes de parada (*stops*) y el ingreso de flujos de impulso aceleran la formación de un nuevo movimiento direccional^12^.

Modelos y Fórmulas Matemáticas

Ruptura de Rango por

Define canales asimétricos sumando o restando un múltiplo del rango verdadero medio al extremo del canal histórico^13^:

Opening Range Breakout ()

Ruptura del máximo o mínimo establecido durante la primera ventana de tiempo () tras la apertura oficial de la sesión bursátil:

Volatility Contraction Pattern ()

Identifica series de contracciones sucesivas en el rango del precio () acompañadas de una disminución sistemática del volumen de negociación antes de la ruptura final^14^.

Implementación Completa en Pine Script v6

Pine Script

//@version=6

strategy("Breakout Master System", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

boSelect = input.string("ATR Breakout", "Patrón de Ruptura", options=["ATR Breakout", "Range Breakout", "ORB Session", "VCP Contraction", "Inside Bar"])

// Componentes Computados en Ámbito Global

atr14 = ta.atr(14)

highestClose30 = ta.highest(close, 30)[1]

lowestClose30  = ta.lowest(close, 30)[1]

// 1. ATR Breakout

atrUpper = highestClose30 + (1.5 * atr14)

atrLower = lowestClose30 - (1.5 * atr14)

atrLong  = close > atrUpper

atrShort = close < atrLower

// 2. Range Breakout (50 Barras)

rangeHigh = ta.highest(high, 50)[1]

rangeLow  = ta.lowest(low, 50)[1]

rangeLong  = close > rangeHigh

rangeShort = close < rangeLow

// 3. Opening Range Breakout (ORB NY Open 09:30-10:30 EST)

inOrbSession = not na(time(timeframe.period, "0930-1030:23456"))

var float orbHigh = na

var float orbLow  = na

if inOrbSession

    if not inOrbSession[1]

        orbHigh := high

        orbLow  := low

    else

        orbHigh := math.max(orbHigh, high)

        orbLow  := math.min(orbLow, low)

orbLong  = not inOrbSession and close > orbHigh[1] and ta.change(inOrbSession) != 0

orbShort = not inOrbSession and close < orbLow[1] and ta.change(inOrbSession) != 0

// 4. Volatility Contraction Pattern (VCP)

volSma = ta.sma(volume, 30)

atrSma = ta.sma(atr14, 30)

isVcpContracting = (atr14 < atrSma * 0.8) and (volume < volSma)

vcpLong  = isVcpContracting[1] and ta.crossover(close, ta.highest(high, 20)[1])

// 5. Inside Bar Breakout

isInsideBar = (high < high[1]) and (low > low[1])

insideLong  = isInsideBar[1] and close > high[1]

insideShort = isInsideBar[1] and close < low[1]

// Enrutamiento de Señales de Compra y Venta

var bool boL = false

var bool boS = false

if boSelect == "ATR Breakout"

    boL := atrLong

    boS := atrShort

else if boSelect == "Range Breakout"

    boL := rangeLong

    boS := rangeShort

else if boSelect == "ORB Session"

    boL := orbLong

    boS := orbShort

else if boSelect == "VCP Contraction"

    boL := vcpLong

    boS := false // Estructura típicamente alcista

else if boSelect == "Inside Bar"

    boL := insideLong

    boS := insideShort

if boL

    strategy.entry("BO_L", strategy.long)

if boS

    strategy.entry("BO_S", strategy.short)

4. Momentum (Momento)

Las estrategias de momentum explotan el fenómeno de persistencia del movimiento del precio inducido por la infravaloración inicial de la información fundamental y los efectos de flujo de capitales de corto plazo. Se busca operar en la dirección de la aceleración del precio y cerrar las posiciones cuando dicha fuerza muestre signos de agotamiento.

Modelos y Fórmulas Matemáticas

Tasa de Cambio ()

Mide el cambio porcentual del precio de cierre actual respecto a una barra de referencia  períodos atrás:

MACD Divergence (Divergencia Regular)

Ocurre cuando el precio registra un mínimo más bajo (u oscilación alcista más alta) mientras que el histograma del MACD genera un mínimo más alto (u oscilación bajista más baja), lo que indica una desaceleración de la tendencia subyacente.

Dual Momentum (Antonacci)

Evalúa simultáneamente el momento relativo (comparando el rendimiento del activo frente a un índice de referencia) y el momento absoluto (asegurando que el rendimiento supere a la tasa libre de riesgo o un activo monetario refugio)^8^.

Implementación Completa en Pine Script v6

Pine Script

//@version=6

strategy("Momentum Consolidated Suite", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

momSelect = input.string("ROC Trend", "Sistema de Momento", options=["ROC Trend", "MACD Divergence", "RSI Trend >50", "Dual Momentum"])

// Variables Globales Calculadas Seguramente

rocVal = ta.roc(close, 14)

[macdLine, signalLine, macdHist] = ta.macd(close, 12, 26, 9)

rsiVal = ta.rsi(close, 14)

// 1. ROC Cross

rocLong  = ta.crossover(rocVal, 0.0)

rocShort = ta.crossunder(rocVal, 0.0)

// 2. MACD Divergence (Filtro Libre de Repintado con Pivotes de 5 períodos)

plPrice = ta.pivotlow(low, 5, 5)

plMacd  = ta.pivotlow(macdHist, 5, 5)

var float lastPlPrice = na

var float lastPlMacd  = na

if not na(plPrice)

    lastPlPrice := low[5]

if not na(plMacd)

    lastPlMacd  := macdHist[5]

macdDivLong = ta.change(plMacd) != 0 and low[5] < lastPlPrice and macdHist[5] > lastPlMacd

// 3. RSI Momentum (>50 como sesgo tendencial)

rsiTrendLong  = ta.crossover(rsiVal, 50.0)

rsiTrendShort = ta.crossunder(rsiVal, 50.0)

// 4. Dual Momentum (Antonacci)

benchmarkClose = request.security("SPY", timeframe.period, close, barmerge.gaps_off, barmerge.lookahead_off)

assetROC = ta.roc(close, 126)

benchROC = ta.roc(benchmarkClose, 126)

dualMomLong  = assetROC > 0.0 and assetROC > benchROC

dualMomShort = assetROC < 0.0 or assetROC < benchROC

// Máquina de Estados de Señal

var bool momL = false

var bool momS = false

if momSelect == "ROC Trend"

    momL := rocLong

    momS := rocShort

else if momSelect == "MACD Divergence"

    momL := macdDivLong

    momS := false

else if momSelect == "RSI Trend >50"

    momL := rsiTrendLong

    momS := rsiTrendShort

else if momSelect == "Dual Momentum"

    momL := dualMomLong

    momS := dualMomShort

if momL

    strategy.entry("MOM_L", strategy.long)

if momS

    strategy.entry("MOM_S", strategy.short)

5. Estrategias Multi-Timeframe (MTF)

El análisis de múltiples escalas temporales minimiza el riesgo de operar contra la tendencia de largo plazo^16^. Sin embargo, la implementación de modelos MTF en TradingView presenta un riesgo crítico: el sesgo de anticipación (*lookahead bias*), el cual genera un repintado ficticio en los datos históricos^17^. Esto ocurre cuando el simulador asigna valores de una barra de una temporalidad superior (por ejemplo, el cierre diario) a las barras de la temporalidad inferior (por ejemplo, gráficos de 5 minutos) antes de que la sesión correspondiente haya concluido oficialmente^17^.

Para neutralizar de manera absoluta el efecto de repintado en Pine Script v6, se deben cumplir tres reglas de diseño:

- Utilizar siempre el parámetro barmerge.lookahead_off en las llamadas a request.security()^19^.
- Solicitar datos de la barra anterior ya consolidada utilizando el operador de desfase [1] directamente dentro de la expresión de cálculo^17^.
- Establecer barmerge.gaps_off para asegurar una propagación continua de la serie en el flujo temporal del gráfico^19^.

Comparativa de Modelos de Petición MTF

La siguiente tabla detalla la diferencia de comportamiento técnico entre un script con repintado (inviable para producción) y un script protegido (libre de repintado):

| **Característica Técnica** | **Implementación Tradicional (Con Repintado)** | **Implementación Segura en Pine v6 (Sin Repintado)** |
| --- | --- | --- |
| **Sintaxis de Solicitud** | request.security(sym, "1D", close)<br>[cite: 17] | request.security(sym, "1D", close[1], barmerge.gaps_off, barmerge.lookahead_off) |
| **Fecha de Asignación** | Asigna el valor de cierre antes de que concluya el día^17^. | Propaga el valor confirmado del día anterior en la primera barra del día actual^17^. |
| **Precisión del Backtest** | Resultados artificialmente optimistas y no replicables. | Rendimiento real idéntico al comportamiento en vivo. |
| **Consistencia del Historial** | Cambia la trayectoria del precio retrospectivamente^17^. | Inalterable a lo largo del tiempo. |

Implementación Completa en Pine Script v6 (Triple Screen de Alexander Elder Segura)

Pine Script

//@version=6

strategy("Triple Screen MTF Elder Guard", overlay=true, initial_capital=10000)

// Captura de datos MTF mediante funciones encapsuladas (Garantiza lookahead_off)

htfEmaTrend() =>

    emaMarea = ta.ema(close, 26)

    macdVal  = ta.macd(close, 12, 26, 9)[0]

    [emaMarea, macdVal]

// Petición Segura Multi-Timeframe (Libre de Repintado)

[htfEma, htfMacd] = request.security(syminfo.tickerid, "D", htfEmaTrend(), barmerge.gaps_off, barmerge.lookahead_off)

// Cómputo en Timeframe Operativo (Mecanismo táctico de Elder)

rsiOperativo = ta.rsi(close, 14)

pullbackLong  = rsiOperative < 30.0 and close > htfEma and htfMacd > 0.0

pullbackShort = rsiOperative > 70.0 and close < htfEma and htfMacd < 0.0

// Trigger de entrada por ruptura en escala menor

if pullbackLong and close > high[1]

    strategy.entry("Triple_L", strategy.long)

if pullbackShort and close < low[1]

    strategy.entry("Triple_S", strategy.short)

6. Multi-Indicator Confluence (Confluencia Multi-Indicador)

Los sistemas cuantitativos combinan múltiples señales técnicas no correlacionadas para reducir los errores de clasificación y las señales erráticas. Este catálogo propone tres métodos de confluencia: un sistema de puntuación acumulativa (*Scoring System*), una ponderación asimétrica basada en la fuerza predictiva del indicador (*Weighted Aggregation*) y un proceso condicional jerárquico (*Sequential Confirmation*).

MÉTODOS DE CONFLUENCIA DE SEÑAL:

[Scoring System] ───►  +1 (EMA Cross) + +1 (RSI Extremes) + +1 (Volume Spike) ───► Si Score >= 2 ──► Ejecución

[Weighted Signal] ──►  (EMA Cross * 0.50) + (RSI * 0.30) + (Volume * 0.20)  ───► Si Peso >= 0.7 ──► Ejecución

[Sequential System] ─►  Paso 1: Cruce de Medias ──► Paso 2 (Max 10 barras): Pullback RSI ───► Ejecución

Implementación Completa en Pine Script v6

Pine Script

//@version=6

strategy("Multi-Indicator Confluence Engine", overlay=true, initial_capital=10000)

confMethod = input.string("Scoring System", "Modelo de Confluencia", options=["Scoring System", "Weighted Signal", "Sequential System"])

// Indicadores de Entrada Base

ema9  = ta.ema(close, 9)

ema21 = ta.ema(close, 21)

rsi   = ta.rsi(close, 14)

volSma = ta.sma(volume, 20)

// Condiciones booleanas normalizadas

emaBull = ema9 > ema21

rsiBull = rsi < 40.0

volBull = volume > volSma

emaBear = ema9 < ema21

rsiBear = rsi > 60.0

volBear = volume > volSma

// 1. Scoring System (Lógica de Votación Equitativa)

scoreL = (emaBull ? 1 : 0) + (rsiBull ? 1 : 0) + (volBull ? 1 : 0)

scoreS = (emaBear ? 1 : 0) + (rsiBear ? 1 : 0) + (volBear ? 1 : 0)

scoringBuy  = scoreL >= 2

scoringSell = scoreS >= 2

// 2. Weighted Signal Aggregation (Ponderación Asimétrica de Factores)

weightL = (emaBull ? 0.50 : 0.0) + (rsiBull ? 0.30 : 0.0) + (volVol = volBull ? 0.20 : 0.0)

weightS = (emaBear ? 0.50 : 0.0) + (rsiBear ? 0.30 : 0.0) + (volVol = volBear ? 0.20 : 0.0)

weightedBuy  = weightL >= 0.70

weightedSell = weightS >= 0.70

// 3. Sequential Confirmation (Filtro Cronológico Estricto)

var int lastEmaCrossBar = -1

if ta.crossover(ema9, ema21)

    lastEmaCrossBar := bar_index

// La entrada exige un cruce de medias previo y un posterior pullback de RSI dentro de un límite de 10 barras

sequentialBuy = (bar_index - lastEmaCrossBar <= 10) and lastEmaCrossBar != -1 and rsi < 35.0

// Enrutamiento definitivo de señales

var bool triggerLong  = false

var bool triggerShort = false

if confMethod == "Scoring System"

    triggerLong  := scoringBuy

    triggerShort := scoringSell

else if confMethod == "Weighted Signal"

    triggerLong  := weightedBuy

    triggerShort := weightedSell

else if confMethod == "Sequential System"

    triggerLong  := sequentialBuy

    triggerShort := false

if triggerLong

    strategy.entry("Conf_L", strategy.long)

if triggerShort

    strategy.entry("Conf_S", strategy.short)

7. Market Regime Detection (Detección de Régimen de Mercado)

Un error crítico en el desarrollo de estrategias algorítmicas es aplicar la misma lógica operativa bajo condiciones cambiantes del mercado. Este motor implementa una arquitectura adaptativa que detecta el régimen del mercado para conmutar dinámicamente sus parámetros, evaluando tres dimensiones complementarias: la fuerza de la tendencia (), la amplitud de la volatilidad (*Bollinger Bandwidth*) y el exponente de Hurst ()^7^.

Modelos y Fórmulas Matemáticas

Bollinger Bandwidth

Mide la anchura relativa de los canales de volatilidad normalizada respecto a su media aritmética:

Exponente de Hurst ()

Mide el grado de memoria a largo plazo y la dimensionalidad fractal de una serie temporal de precios^21^. El exponente de Hurst clasifica el comportamiento del mercado en tres regímenes distintos^7^:

- **(Persistente / Tendencial):** El precio presenta memoria de tendencia^7^. Cada incremento tiende a ser seguido por otro incremento^21^.
- **(Anti-persistente / Reversión a la media):** El precio presenta un comportamiento de reversión sistemática^7^.
- **(Movimiento aleatorio):** Caminata aleatoria pura sin memoria histórica significativa^21^.

Implementación Completa en Pine Script v6 (Aproximación de Hurst por Regresión de Retornos Logarítmicos)

Pine Script

//@version=6

strategy("Market Regime Switching Suite", overlay=true, initial_capital=10000)

// Cómputo del Exponente de Hurst (Aproximación numérica mediante regresión de varianza de rezagos)

calculateHurstExponent(src, len) =>

    logRet = math.log(src / src[1])

    varX1 = ta.stdev(logRet - logRet[2], len)

    varX2 = ta.stdev(logRet - logRet[4], len)

    varX4 = ta.stdev(logRet - logRet[8], len)

    varX8 = ta.stdev(logRet - logRet[16], len)

    // Matriz de mínimos cuadrados para resolver la pendiente de la relación logarítmica

    sumX  = math.log(2.0) + math.log(4.0) + math.log(8.0) + math.log(16.0)

    sumX2 = math.pow(math.log(2.0), 2) + math.pow(math.log(4.0), 2) + math.pow(math.log(8.0), 2) + math.pow(math.log(16.0), 2)

    sumY  = math.log(varX1) + math.log(varX2) + math.log(varX4) + math.log(varX8)

    sumXY = (math.log(2.0) * math.log(varX1)) + (math.log(4.0) * math.log(varX2)) + (math.log(8.0) * math.log(varX4)) + (math.log(16.0) * math.log(varX8))

    hurstSlope = (4.0 * sumXY - sumX * sumY) / (4.0 * sumX2 - sumX * sumX)

    math.max(0.0, math.min(1.0, hurstSlope))

// Cómputo de Indicadores Base de Régimen

hurstVal = calculateHurstExponent(close, 50)

[_, _, adx] = ta.dmi(14, 14)

bbBasis = ta.sma(close, 20)

bbUpper = bbBasis + (2.0 * ta.stdev(close, 20))

bbLower = bbBasis - (2.0 * ta.stdev(close, 20))

bbBandwidth = (bbUpper - bbLower) / bbBasis

// Identificación del Régimen de Mercado

isTrending = hurstVal > 0.53 and adx > 25.0

isMeanReverting = hurstVal < 0.47 and bbBandwidth > 0.05

// Lógica Operativa Condicionada al Régimen Activo

ema9  = ta.ema(close, 9)

ema21 = ta.ema(close, 21)

// Ejecución adaptativa

if isTrending

    // Estrategia de Tendencia: Cruce de Medias Móviles

    if ta.crossover(ema9, ema21)

        strategy.entry("Regime_L", strategy.long)

    if ta.crossunder(ema9, ema21)

        strategy.entry("Regime_S", strategy.short)

else if isMeanReverting

    // Estrategia de Reversión: Reversión en Banda Externa

    if ta.crossunder(close, bbLower)

        strategy.entry("Regime_L", strategy.long)

    if ta.crossover(close, bbUpper)

        strategy.entry("Regime_S", strategy.short)

// Indicador Visual de Régimen de Mercado en el Fondo del Gráfico

bgcolor(isTrending ? color.new(color.green, 92) : (isMeanReverting ? color.new(color.blue, 92) : color.new(color.gray, 92)))

8. Pairs Trading (Trading de Pares)

El trading de pares es una estrategia de arbitraje estadístico de mercado neutral que explota las ineficiencias de precios entre dos activos altamente correlacionados y cointegrados^8^. Al estimar continuamente el ratio de cobertura dinámico () mediante mínimos cuadrados, se construye una serie estacionaria conocida como *Spread*^8^. Las desviaciones de este Spread respecto a su media histórica se operan bajo la expectativa de una convergencia estadística inminente^6^.

Modelos y Fórmulas Matemáticas

Ratio de Cobertura Dinámico ()

Calculado de forma móvil como la covarianza de ambos activos dividida por la varianza del activo de cobertura^8^:

Spread de Cointegración

Expresa el equilibrio del sistema dinámico^8^:

Z-Score del Spread

Normaliza la desviación para generar señales operativas estandarizadas^6^:

Implementación Completa en Pine Script v6 (Estrategia GLD/SLV o BTC/ETH Cointegrada)

Pine Script

//@version=6

strategy("Pairs Trading Cointegration Engine", overlay=false, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

// Selección dinámica de la segunda pata de cobertura (Uso de request.security en v6)

assetB_ticker = input.symbol("NYSE:SLV", "Activo de Cobertura (B)")

regressionLen = input.int(60, "Ventana de Regresión Dinámica")

// Obtención del flujo de precios libre de desfase temporal histórico (lookahead_off)

priceA = close

priceB = request.security(assetB_ticker, timeframe.period, close, barmerge.gaps_off, barmerge.lookahead_off)

// Cómputo del Ratio Beta Dinámico de Cobertura

meanA = ta.sma(priceA, regressionLen)

meanB = ta.sma(priceB, regressionLen)

covarianceAB = ta.covariance(priceA, priceB, regressionLen)

varianceB = ta.variance(priceB, regressionLen)

betaRatio = covarianceAB / varianceB

// Construcción del Spread de Cointegración

spreadSeries = priceA - (betaRatio * priceB)

spreadMean   = ta.sma(spreadSeries, regressionLen)

spreadStdev  = ta.stdev(spreadSeries, regressionLen)

zScoreSpread = (spreadSeries - spreadMean) / spreadStdev

// Lógica de Reversión del Spread (Compra/Venta del Spread)

longSpread  = zScoreSpread < -2.0

shortSpread = zScoreSpread > 2.0

exitLong    = zScoreSpread >= 0.0

exitShort   = zScoreSpread <= 0.0

if longSpread

    strategy.entry("Pairs_Long", strategy.long) // Posición larga en Activo A (El activo principal del gráfico)

if shortSpread

    strategy.entry("Pairs_Short", strategy.short) // Posición corta en Activo A

if exitLong

    strategy.close("Pairs_Long")

if exitShort

    strategy.close("Pairs_Short")

// Visualización de la serie del Spread Normalizado

plot(zScoreSpread, "Z-Score del Spread", color=color.purple, linewidth=2)

hline(2.0, "Límite de Venta", color=color.red, style=hline.style_dashed)

hline(-2.0, "Límite de Compra", color=color.green, style=hline.style_dashed)

hline(0.0, "Media", color=color.gray)

9. Seasonal/Session-Based (Estacionalidad y Sesiones)

Las ineficiencias estacionales e intradiarias se derivan de la concentración temporal de los flujos de liquidez institucional, los procesos de liquidación de márgenes diarios y los patrones de comportamiento de los operadores bursátiles. Este motor explota tres anomalías cuantitativas clásicas: el efecto de "Turn-of-the-Month", la direccionalidad del lunes ("Monday Effect") y la ruptura de rangos intradiarios en las aperturas de las sesiones de Londres y Nueva York.

Implementación Completa en Pine Script v6

Pine Script

//@version=6

strategy("Seasonal & Session-Based Suite", overlay=true, initial_capital=10000)

seasonalType = input.string("London/NY Breakout", "Patrón de Estacionalidad", options=["London/NY Breakout", "Day of Week Anomaly", "Turn of the Month"])

// 1. London/NY Session Breakout (Rango entre las 07:00 y las 09:00 UTC)

inSession = not na(time(timeframe.period, "0700-0900:23456"))

var float sessionHigh = na

var float sessionLow  = na

if inSession

    if not inSession[1]

        sessionHigh := high

        sessionLow  := low

    else

        sessionHigh := math.max(sessionHigh, high)

        sessionLow  := math.min(sessionLow, low)

sessionBuy  = not inSession and close > sessionHigh[1] and ta.change(inSession) != 0

sessionSell = not inSession and close < sessionLow[1] and ta.change(inSession) != 0

// 2. Day of Week Anomaly (Efecto Lunes - Compra al cierre del lunes, salida el viernes)

isMonday = dayofweek == dayofweek.monday

isFriday = dayofweek == dayofweek.friday

// 3. Turn of the Month (Compra en el penúltimo día bursátil del mes, salida el tercer día bursátil del nuevo mes)

isEndOfMonth = dayofmonth >= 28 and dayofmonth <= 31

isStartOfMonth = dayofmonth >= 1 and dayofmonth <= 4

// Causalidad y ruteo de órdenes

var bool enterL = false

var bool enterS = false

var bool exitAll = false

if seasonalType == "London/NY Breakout"

    enterL := sessionBuy

    enterS := sessionSell

    exitAll := hour == 18 and minute == 00 // Cierre forzado al final de la sesión americana

else if seasonalType == "Day of Week Anomaly"

    enterL := isMonday and ta.change(dayofweek) != 0

    enterS := false

    exitAll := isFriday

else if seasonalType == "Turn of the Month"

    enterL := isEndOfMonth and ta.change(month) != 0

    enterS := false

    exitAll := isStartOfMonth and ta.change(month) != 0

if enterL

    strategy.entry("Seasonal_L", strategy.long)

if enterS

    strategy.entry("Seasonal_S", strategy.short)

if exitAll

    strategy.close_all("Cierre Estacional Estructural")

10. Event-Driven (Operación Basada en Eventos)

Las ineficiencias de mercado asociadas a eventos ocurren debido a la asimetría de información y a los desequilibrios de inventario que sufren los proveedores de liquidez tras la publicación de noticias de alto impacto^17^. Pine Script v6 incorpora funciones avanzadas de consulta de bases de datos macroeconómicas e institucionales a través de request.economic()^25^ y request.earnings()^17^, permitiendo operar de forma directa y asíncrona la volatilidad e inercia generada por reportes macroeconómicos u hojas de balances corporativos^1^.

Implementación Completa en Pine Script v6

Pine Script

//@version=6

strategy("Event-Driven Quantitative Strategy", overlay=true, initial_capital=10000)

// Consulta asíncrona de variables macroeconómicas clave (GDP de EE. UU.)

us_gdp = request.economic("US", "GDP", barmerge.gaps_off, true)

gdpTrendRising = ta.change(us_gdp) > 0.0

// Consulta de Reportes Trimestrales Corporativos (Earnings Surprise)

actualEps    = request.earnings(syminfo.tickerid, "actual", barmerge.gaps_off, barmerge.lookahead_off, true)

estimatedEps = request.earnings(syminfo.tickerid, "estimate", barmerge.gaps_off, barmerge.lookahead_off, true)

epsSurprise  = (actualEps > estimatedEps) and ta.change(actualEps) != 0.0

// Cómputo de la Expansión de Volatilidad Relativa (ATR Spike)

atr = ta.atr(14)

volSma = ta.sma(volume, 20)

volatilitySpike = atr > ta.sma(atr, 20) * 1.50 and volume > volSma

// Apertura de posiciones basada en la confluencia de sorpresas de resultados y expansión de volatilidad

if epsSurprise and volatilitySpike and gdpTrendRising

    strategy.entry("Event_L", strategy.long)

// Cierre al normalizarse la volatilidad del activo

if atr < ta.sma(atr, 20)

    strategy.close("Event_L")

11. Strategy Composition (Composición de Estrategias)

La composición de estrategias gestiona una cartera de sistemas algorítmicos correlacionando dinámicamente sus rendimientos individuales en tiempo real. Al aplicar el concepto de seguimiento de tendencia sobre la propia curva de capital acumulado de la estrategia (strategy.equity), el sistema puede desconectar de manera automática a los modelos operativos en periodos de pérdidas o bajo rendimiento y reincorporarlos cuando las condiciones del mercado vuelvan a favorecer su lógica de negociación.

El motor integra además un interruptor de pánico (*Kill Switch*) diseñado para mitigar pérdidas extraordinarias durante la sesión intradiaria.

Estructura de Control de Riesgos

La gestión del capital se articula en tres niveles jerárquicos de toma de decisiones:

JERARQUÍA DEL CONTROL DE RIESGOS:

  Nivel 1: Filtro de Equity (Filtro Macro)

  ├─ ¿Equity por encima de su SMA de 50 períodos?

  │   ├─ Sí: Permitir nuevas entradas de capital.

  │   └─ No: Suspender nuevas entradas (Permitir solo gestión de posiciones abiertas).

  │

  Nivel 2: Filtro Táctico (Ejecución de Estrategias)

  ├─ Señal de Compra / Venta de los Componentes Operativos.

  │

  Nivel 3: Interruptor de Pánico (Kill Switch de Sesión)

  └─ ¿Drawdown diario supera el 3%?

      ├─ Sí: Forzar cierre de posiciones y suspender operaciones hasta el día siguiente.

      └─ No: Operación normalizada.

Implementación Completa en Pine Script v6

Pine Script

//@version=6

strategy("Composite Strategy & Equity Guard Suite", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

// 1. Componentes Operativos Independientes

// Componente A: Tendencial (Cruce de Medias)

emaFast = ta.ema(close, 10)

emaSlow = ta.ema(close, 50)

trendLong  = ta.crossover(emaFast, emaSlow)

trendShort = ta.crossunder(emaFast, emaSlow)

// Componente B: Reversión (RSI en extremos)

rsiVal = ta.rsi(close, 14)

rsiLong  = rsiVal < 30.0

rsiShort = rsiVal > 70.0

// Señales Combinadas

compositeLong  = trendLong or rsiLong

compositeShort = trendShort or rsiShort

// 2. Filtro de Tendencia sobre la Curva de Capital (Equity Curve Trend Filter)

equitySma = ta.sma(strategy.equity, 50)

isEquityHealthy = strategy.equity >= equitySma

// 3. Interruptor de Pánico Intradiario (Daily Drawdown Kill Switch al 3%)

var float dailyStartEquity = na

if ta.change(time("D")) != 0

    dailyStartEquity := strategy.equity

// Manejo del estado inicial en la primera barra de la sesión

effectiveStartEquity = na(dailyStartEquity) ? strategy.equity : dailyStartEquity

dailyDrawdown = ((strategy.equity - effectiveStartEquity) / effectiveStartEquity) * 100.0

isKillSwitchActive = dailyDrawdown < -3.0

// Lógica de Ejecución bajo Control de Riesgos de Tres Capas

if not isKillSwitchActive

    if isEquityHealthy

        if compositeLong

            strategy.entry("Composite_L", strategy.long)

        if compositeShort

            strategy.entry("Composite_S", strategy.short)

else

    strategy.close_all("Cierre por Emergencia: Kill Switch Activo")

Fuentes citadas

- What's New in Pine Script v6: All Features Covered - TradersPost, https://blog.traderspost.io/article/pine-script-v6-complete-guide
- Cracking Pine script version 6. Get my strategy - Medium, https://medium.com/@drwebdev.future/cracking-pine-script-version-6-61faad4d5c9d
- To Pine Script version 6 - Migration guides - TradingView, https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/
- Pine Script® v6已发布— TradingView博客, https://www.tradingview.com/blog/cn/pine-script-v6-has-landed-48830/
- Pine Script® v6 has landed — TradingView Blog, https://www.tradingview.com/blog/en/pine-script-v6-has-landed-48830/
- Algorithmic Trading Strategies: Mean Reversion, Momentum, AI | Moore Tech, https://www.mooretechllc.com/algorithmic-trading/algorithmic-trading-strategies-explained/
- Harnessing Mean Reversion with Hurst Exponent: A QuantConnect Backtesting Guide | by Pham The Anh | Funny AI & Quant | Medium, https://medium.com/funny-ai-quant/harnessing-mean-reversion-with-hurst-exponent-a-quantconnect-backtesting-guide-948b7817283e
- Correlation Trading Strategies - QuantifiedStrategies.com, https://www.quantifiedstrategies.com/correlation-trading-strategies/
- TTM Squeeze Pro Indicator Overview | PDF - Scribd, https://www.scribd.com/document/905597150/TTM-Squeeze-Pro-TV
- Squeeze Momentum Indicator v4_pine - LuxAlgo, https://www.luxalgo.com/library/indicator/2dosxwBH-squeeze-momentum-indicator-v4-pine/
- Using Webhooks to Automate the Squeeze Indicator - Option Alpha, https://optionalpha.com/community/posts/using-webhooks-to-automate-the-squeeze-2024072314560
- NR7 Trading Strategy – Toby Crabels Narrow Range 7 Pattern – QuantifiedStrategies.com, https://www.quantifiedstrategies.com/nr7-trading-strategy-toby-crabel/
- Pine Script Keltner Channels - Complete TradingView Guide, https://offline-pixel.github.io/pinescript-strategies/pine-script-KeltnerChannels.html
- VCP Breakout Screener in Pine Script | PDF | Teaching Methods & Materials | Technology & Engineering - Scribd, https://www.scribd.com/presentation/689136080/VCP-screener-Pine-script-tradeview
- What 90% of Traders Miss Before a Breakout — Script It Yourself | by Betashorts - Medium, https://medium.com/@betashorts1998/what-90-of-traders-miss-before-a-breakout-script-it-yourself-190f1e63dfae
- tradingview-pine-scripts/Elder Ray (Bull Power) TP and SL.pine at main - GitHub, https://github.com/hasnocool/tradingview-pine-scripts/blob/main/Elder%20Ray%20(Bull%20Power)%20TP%20and%20SL.pine
- Concepts / Other timeframes and data - TradingView, https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/
- Manual de referencia del lenguaje Pine Script — TradingView, https://es.tradingview.com/pine-script-reference/v6/
- Pine Script Compatibility | PyneCore Documentation, https://pynecore.org/docs/overview/compatibility/
- request | PyneCore Documentation, https://pynecore.org/docs/reference/lib/request/
- Boost Your Trading Edge with the Hurst Exponent and PineConnector, https://www.pineconnector.com/blogs/pico-blog/boost-your-trading-edge-with-the-hurst-exponent-and-pineconnector
- Quitting software engineering to trade full-time. Here are the stats behind my algorithmic edge. : r/Daytrading - Reddit, https://www.reddit.com/r/Daytrading/comments/1tusk9c/quitting_software_engineering_to_trade_fulltime/
- How I improved results on a scalping algo (mean reversion logic) : r/algotrading - Reddit, https://www.reddit.com/r/algotrading/comments/1rtepah/how_i_improved_results_on_a_scalping_algo_mean/
- Pairs Trading: Methods & Analysis Notes | PDF | Covariance | Variance - Scribd, https://www.scribd.com/document/335181773/Some-Notes-From-the-Book-Pairs-Trading-Quantitative-Methods-and-Analysis-by-Ganapathy-Vidyamurthy-Weatherwax-vidyamurthy-notes
- What economic data is available in Pine? - TradingView, https://www.tradingview.com/support/solutions/43000665359-what-economic-data-is-available-in-pine/
- ¿Qué datos económicos están disponibles en Pine? - TradingView, https://es.tradingview.com/support/solutions/43000665359/