Tratado Técnico Multidimensional y Catálogo de Funciones de Análisis Técnico y Matemático en Pine Script v5

El diseño de sistemas de trading algorítmico y la investigación cuantitativa en la plataforma TradingView exigen una comprensión profunda de su entorno de ejecución^1^. Este tratado proporciona un catálogo exhaustivo y un análisis analítico del namespace de análisis técnico (ta.*) y de las funciones matemáticas complementarias (math.*) en Pine Script versión 5^3^. A lo largo de este documento, se desglosará la teoría matemática subyacente, el comportamiento computacional ante el motor de ejecución barra por barra y la implementación práctica optimizada de cada función integrada^1^.

1. Medias Móviles

Las medias móviles actúan como filtros espectrales de paso bajo diseñados para atenuar las fluctuaciones de alta frecuencia (ruido) y aislar las bajas frecuencias correspondientes a la tendencia del precio^5^. La siguiente tabla resume las propiedades fundamentales de transferencia espectral y fase para cada filtro disponible en el namespace ta.*:

| **Función** | **Tipo de Filtro** | **Fórmula de Fase / Retraso (Lag)** | **Sensibilidad a Datos Extremos (Outliers)** |
| --- | --- | --- | --- |
| ta.sma()<br>[cite: 4, 7] | FIR (Respuesta al impulso finita) | Lineal, simétrico:<br>[cite: 5, 6] | Alta (Distribución uniforme de pesos)^5^ |
| ta.ema()<br>[cite: 4] | IIR (Respuesta al impulso infinita) | Asimétrico: decaimiento exponencial^5^ | Moderada-Alta (Atenuación progresiva) |
| ta.wma()<br>[cite: 8, 9] | FIR | Lineal decreciente hacia el extremo | Moderada (Ponderación lineal del precio) |
| ta.vwma()<br>[cite: 8, 9] | FIR adaptativo por volumen | Dinámico según distribución de volumen^5^ | Variable (Ponderada por volumen de transacción)^5^ |
| ta.rma()<br>[cite: 3, 4] | IIR (Suavizado Wilder) | Equivalente a EMA de longitud<br>[cite: 3, 10] | Baja (Alta inercia estructural) |
| ta.swma()<br>[cite: 8, 9] | FIR simétrico estático | Fase constante (4 barras fijas)^4^ | Muy Baja (Ventana estrecha predefinida) |
| ta.alma()<br>[cite: 4] | FIR basado en distribución gaussiana | Ajustable mediante sesgo analítico (offset)^4^ | Controlable (Filtro óptimo contra ruido)^6^ |
| ta.hma()<br>[cite: 4] | FIR combinado de bajo desfase | Compensación de lag de segundo orden^6^ | Muy Alta (Propenso a sobreoscilaciones) |
| ta.dema()<br>[cite: 12, 13] | IIR con corrección de primer orden | Reducción de fase mediante resta de error^12^ | Alta (Alta reactividad direccional) |
| ta.tema()<br>[cite: 13, 14] | IIR con corrección de segundo orden | Corrección de desfase de triple orden^14^ | Extremadamente Alta (Reactividad máxima)^14^ |

ta.sma() (Simple Moving Average)

- **Fórmula matemática**:
- **Parámetros**:

- source (series float): Serie temporal de datos de entrada^4^.
- length (simple int): Ventana de observación hacia atrás^4^.

- **Comportamiento**: Asigna idéntico peso ponderado a cada una de las barras dentro del rango especificado. Esto introduce un retraso simétrico y produce el conocido "efecto de doble salto", donde el indicador reacciona de forma brusca no solo cuando entra un cambio de precio importante en la ventana, sino también cuando dicho precio sale de ella tras transcurrir  períodos.

Pine Script

//@version=5

indicator("Catálogo - Simple Moving Average", overlay=true)

sma_len = input.int(20, title="Longitud SMA", minval=1)

sma_val = ta.sma(close, sma_len)

plot(sma_val, color=color.blue, title="SMA")

ta.ema() (Exponential Moving Average)

- **Fórmula matemática**:
Donde el coeficiente de suavizado  se define como:
- **Parámetros**:

- source (series float): Serie temporal de datos de entrada^4^.
- length (simple int): Ventana de observación^4^.

- **Comportamiento**: Como filtro de respuesta al impulso infinita (IIR), la EMA retiene memoria de todos los datos históricos del gráfico mediante un factor de decaimiento exponencial. Otorga mayor peso a los eventos de precio recientes, reduciendo el retraso de fase en comparación con una SMA equivalente.

Fragmento de código

//@version=5

indicator("Catálogo - Exponential Moving Average", overlay=true)

ema_len = input.int(20, title="Longitud EMA", minval=1)

ema_val = ta.ema(close, ema_len)

plot(ema_val, color=color.orange, title="EMA")

ta.wma() (Weighted Moving Average)

- **Fórmula matemática**:
Donde la suma de los pesos  se calcula como:
- **Parámetros**:

- source (series float) y length (simple int)^8^.

- **Comportamiento**: Aplica una ponderación lineal decreciente hacia el extremo izquierdo de la ventana de datos. El precio actual se multiplica por , el anterior por , hasta llegar a la barra más lejana que se pondera por 1. Reduce el lag significativamente en comparación con la SMA.

Pine Script

//@version=5

indicator("Catálogo - Weighted Moving Average", overlay=true)

wma_len = input.int(20, title="Longitud WMA", minval=1)

wma_val = ta.wma(close, wma_len)

plot(wma_val, color=color.green, title="WMA")

ta.vwma() (Volume-Weighted Moving Average)

- **Fórmula matemática**:
Donde  corresponde al volumen negociado en la barra respectiva.
- **Parámetros**:

- source (series float) y length (simple int)^8^.

- **Comportamiento**: Pondera la cotización histórica del activo en función del volumen de transacciones registrado^5^. Esto permite que el indicador avance más rápido (reduciendo su desfase) en barras con alta participación institucional y que ralentice su respuesta ante movimientos de bajo volumen o ruido de mercado^5^.

Pine Script

//@version=5

indicator("Catálogo - Volume-Weighted Moving Average", overlay=true)

vwma_len = input.int(20, title="Longitud VWMA", minval=1)

vwma_val = ta.vwma(close, vwma_len)

plot(vwma_val, color=color.teal, title="VWMA")

ta.rma() (Rolling Moving Average)

- **Fórmula matemática**:
Donde el coeficiente de ponderación de Wilder es:
- **Parámetros**:

- source (series float) y length (simple int)^4^.

- **Comportamiento**: Se trata del promedio exponencial clásico diseñado por J. Welles Wilder para estabilizar el comportamiento de osciladores de volatilidad y momentum^3^. Presenta un nivel de suavizado mucho más profundo que una EMA estándar de la misma longitud, pues equivale matemáticamente a una EMA con un período de ^3^.

Pine Script

//@version=5

indicator("Catálogo - Rolling Moving Average", overlay=true)

rma_len = input.int(14, title="Longitud RMA", minval=1)

rma_val = ta.rma(close, rma_len)

plot(rma_val, color=color.red, title="RMA")

ta.swma() (Symmetrically Weighted Moving Average)

- **Fórmula matemática**:
- **Parámetros**:

- source (series float)^7^. No requiere un parámetro de longitud, ya que es un filtro de ventana fija de 4 barras^4^.

- **Comportamiento**: Es un filtro simétrico de respuesta al impulso finita (FIR) no recursivo con una fase constante. Su curva resultante está libre de retraso temporal y distorsiones de fase, lo que lo hace ideal para suavizar señales críticas de momentum sin alterar la sincronización de los cruces de precios.

Pine Script

//@version=5

indicator("Catálogo - Symmetrically Weighted Moving Average", overlay=true)

swma_val = ta.swma(close)

plot(swma_val, color=color.purple, title="SWMA")

ta.alma() (Arnaud Legoux Moving Average)

- **Fórmula matemática**:
Aplica una campana de distribución gaussiana como ventana de ponderación para los pesos :
Donde:
El valor final se normaliza mediante:
- **Parámetros**:

- source (series float)^4^.
- length (simple int): Longitud de la ventana de análisis^4^.
- offset (simple float): Parámetro de desplazamiento que controla la inclinación de la campana gaussiana hacia los datos más recientes (comúnmente ajustado a 0.85)^4^.
- sigma (simple float): Desviación estándar aplicada al ancho del filtro de campana (comúnmente ajustado a 6)^4^.

- **Comportamiento**: Combina un suavizado excepcional con un bajo desfase (lag) mediante la optimización de la distribución gaussiana^6^. Al desplazar la media de la campana hacia las barras más recientes usando el offset, se reduce de forma controlada el desfase del indicador^6^.

Pine Script

//@version=5

indicator("Catálogo - Arnaud Legoux Moving Average", overlay=true)

alma_len = input.int(9, title="Longitud ALMA", minval=1)

alma_off = input.float(0.85, title="Offset ALMA", minval=0.0, maxval=1.0)

alma_sig = input.float(6.0, title="Sigma ALMA", minval=0.01)

alma_val = ta.alma(close, alma_len, alma_off, alma_sig)

plot(alma_val, color=color.maroon, title="ALMA")

ta.hma() (Hull Moving Average)

- **Fórmula matemática**:
- **Parámetros**:

- source (series float) y length (simple int)^4^.

- **Comportamiento**: Diseñada específicamente por Alan Hull para eliminar casi por completo el retraso de fase de los promedios ponderados tradicionales^6^. Combina la diferencia entre dos WMAs de distintas longitudes para compensar el lag, aplicando luego una WMA final sobre la raíz cuadrada de la longitud original para suavizar el resultado^6^. Sin embargo, esta alta reactividad la hace propensa a la sobreoscilación (overshooting), lo que significa que la curva puede sobrepasar temporalmente las cotizaciones extremas ante giros violentos del precio.

Pine Script

//@version=5

indicator("Catálogo - Hull Moving Average", overlay=true)

hma_len = input.int(16, title="Longitud HMA", minval=2)

hma_val = ta.hma(close, hma_len)

plot(hma_val, color=color.yellow, title="HMA")

ta.dema() (Double Exponential Moving Average)

- **Fórmula matemática**:
Donde:
- **Parámetros**:

- source (series float) y length (simple int)^13^.

- **Comportamiento**: Reduce drásticamente el desfase al restar el error acumulado de una doble EMA a partir del doble de la EMA lineal básica^12^. Esto le permite reaccionar de forma extremadamente rápida a cambios de tendencia, manteniendo las características de un filtro exponencial continuo^12^.

Pine Script

//@version=5

indicator("Catálogo - Double Exponential Moving Average", overlay=true)

dema_len = input.int(21, title="Longitud DEMA", minval=1)

dema_val = ta.dema(close, dema_len)

plot(dema_val, color=color.fuchsia, title="DEMA")

ta.tema() (Triple Exponential Moving Average)

- **Fórmula matemática**:
Donde:
- **Parámetros**:

- source (series float) y length (simple int)^8^.

- **Comportamiento**: Añade una capa adicional de compensación de error matemático en comparación con la DEMA^14^. Su latencia de respuesta es prácticamente nula, lo que la convierte en una de las medias móviles más reactivas disponibles para el análisis técnico^14^. No obstante, esta alta sensibilidad la hace propensa a generar señales falsas en mercados laterales o con alto ruido^14^.

Pine Script

//@version=5

indicator("Catálogo - Triple Exponential Moving Average", overlay=true)

tema_len = input.int(21, title="Longitud TEMA", minval=1)

tema_val = ta.tema(close, tema_len)

plot(tema_val, color=color.navy, title="TEMA")

2. Osciladores

Los osciladores cuantitativos miden el momentum o la tasa de variación de los precios respecto a un rango definido^2^. Sirven para identificar divergencias estructurales y condiciones extremas de sobrecompra o sobreventa en el mercado^15^.

ta.rsi() (Relative Strength Index)

- **Fórmula matemática**:
La fuerza relativa () se define como el cociente entre el promedio de las ganancias y pérdidas suavizadas mediante una RMA de  períodos^3^:
- **Interpretación**: Es un indicador normalizado entre 0 y 100^15^. Los niveles por encima de 70 indican sobrecompra, mientras que los niveles por debajo de 30 indican sobreventa^15^. La v5 de Pine Script exige de forma estricta que la longitud del RSI sea un valor entero simple (simple int), impidiendo el uso de variables dinámicas de tipo serie temporal para la longitud de cálculo^3^.

Pine Script

//@version=5

indicator("Catálogo - Relative Strength Index", overlay=false)

rsi_len = input.int(14, title="Longitud RSI", minval=1)

rsi_val = ta.rsi(close, rsi_len)

plot(rsi_val, color=color.purple, title="RSI")

hline(70, "Sobrecompra", color=color.red, linestyle=hline.style_dashed)

hline(30, "Sobreventa", color=color.green, linestyle=hline.style_dashed)

ta.stoch() (Stochastic Oscillator)

- **Fórmula matemática**:
Donde  es el precio de cierre actual,  es el mínimo más bajo de los últimos  períodos, y  es el máximo más alto de los últimos  períodos.
- **Interpretación**: Mide la posición del cierre relativo dentro del rango de precios en un período de tiempo predefinido. Valores cercanos a 100 indican que el precio cierra cerca de los máximos de la ventana temporal; valores cercanos a 0 ubican al cierre en los mínimos de dicha ventana.

Pine Script

//@version=5

indicator("Catálogo - Stochastic", overlay=false)

stoch_len = input.int(14, title="Longitud Estocástico", minval=1)

stoch_k = ta.stoch(close, high, low, stoch_len)

plot(stoch_k, color=color.blue, title="%K Estocástico")

hline(80, "Sobrecompra", color=color.red)

hline(20, "Sobreventa", color=color.green)

ta.mfi() (Money Flow Index)

- **Fórmula matemática**:
Donde  se acumula si  y  si .
- **Interpretación**: Considerado un "RSI ponderado por volumen"^15^. Al incorporar el flujo monetario real del activo, permite la detección temprana de divergencias de volumen que anteceden a giros estructurales de los precios^15^.

Pine Script

//@version=5

indicator("Catálogo - Money Flow Index", overlay=false)

mfi_len = input.int(14, title="Longitud MFI", minval=1)

mfi_val = ta.mfi(close, mfi_len)

plot(mfi_val, color=color.green, title="MFI")

hline(80, "Sobrecompra", color=color.red)

hline(20, "Sobreventa", color=color.green)

ta.cci() (Commodity Channel Index)

- **Fórmula matemática**:
Donde  es el precio típico () y  es la desviación media absoluta (Mean Deviation):
- **Interpretación**: Mide la desviación del precio típico actual respecto a su promedio móvil simple en un período de tiempo. Al dividir por la desviación media absoluta, se normaliza la métrica. Valores por encima de  indican una fortaleza inusual del precio (por encima de la dispersión esperada), mientras que valores inferiores a  denotan una debilidad extrema.

Pine Script

//@version=5

indicator("Catálogo - Commodity Channel Index", overlay=false)

cci_len = input.int(20, title="Longitud CCI", minval=1)

cci_val = ta.cci(close, cci_len)

plot(cci_val, color=color.aqua, title="CCI")

hline(100, "Extremo Superior", color=color.red, linestyle=hline.style_dashed)

hline(-100, "Extremo Inferior", color=color.green, linestyle=hline.style_dashed)

ta.cmo() (Chande Momentum Oscillator)

- **Fórmula matemática**:
Donde:
- **Interpretación**: A diferencia del RSI, el CMO mide el impulso directamente en el numerador y el denominador sin aplicar un suavizado de datos (RMA) previo. Oscila en un rango de  a . Un valor de  indica que la suma de variaciones alcistas duplica a la de variaciones bajistas en la ventana especificada.

Pine Script

//@version=5

indicator("Catálogo - Chande Momentum Oscillator", overlay=false)

cmo_len = input.int(9, title="Longitud CMO", minval=1)

cmo_val = ta.cmo(close, cmo_len)

plot(cmo_val, color=color.blue, title="CMO")

hline(50, "Sobrecompra", color=color.red)

hline(-50, "Sobreventa", color=color.green)

ta.cog() (Center of Gravity)

- **Fórmula matemática**:
- **Interpretación**: Diseñado por John Ehlers, este indicador interpreta los precios dentro de una ventana de observación como si fueran masas distribuidas a lo largo de una barra física rígida. El centro de gravedad es el punto de equilibrio resultante. Ofrece una respuesta de fase prácticamente nula ante los giros cíclicos de precios, anticipándose de forma regular a otros osciladores clásicos.

Pine Script

//@version=5

indicator("Catálogo - Center of Gravity", overlay=false)

cog_len = input.int(10, title="Longitud COG", minval=1)

cog_val = ta.cog(close, cog_len)

plot(cog_val, color=color.olive, title="COG")

ta.dmi() (Directional Movement Index)

- **Fórmula matemática**:
Calcula los movimientos direccionales positivo y negativo:
Suaviza los valores de los movimientos y del rango medio utilizando la RMA^3^:
- **Interpretación**: Evalúa tanto la dirección como la fuerza de una tendencia^16^. El cruce de  por encima de  genera señales alcistas; el cruce inverso genera señales bajistas^16^. Valores de ADX superiores a 25 confirman la presencia de una tendencia sólida en desarrollo^17^.

Pine Script

//@version=5

indicator("Catálogo - Directional Movement Index", overlay=false)

dmi_len = input.int(14, title="Longitud DI")

adx_smooth = input.int(14, title="Suavizado ADX")

[plusDI, minusDI, adx] = ta.dmi(dmi_len, adx_smooth)

plot(plusDI, color=color.green, title="+DI")

plot(minusDI, color=color.red, title="-DI")

plot(adx, color=color.black, linewidth=2, title="ADX")

3. Tendencia

La correcta clasificación de las tendencias del mercado permite filtrar señales falsas y optimizar los sistemas de trading^6^. A continuación, se detalla la integración de los principales algoritmos de tendencia para crear un modelo de confluencia y confirmación direccional fuerte.

Lógica de Acoplamiento y Sincronización

La evaluación de tendencias es más robusta cuando combina diferentes dimensiones analíticas:

- **Momentum direccional**: Proporcionado por el histograma y cruces de línea del MACD^17^.
- **Límites de volatilidad dinámicos**: Proporcionados por el Supertrend y el Parabolic SAR^2^.
- **Nivel medio de consenso institucional**: Representado por el volumen medio ponderado por precio (VWAP)^2^.

Pine Script

//@version=5

indicator("Análisis de Tendencia Combinado", overlay=true)

// Parámetros de Configuración de Tendencia

macd_fast   = input.int(12, "MACD Fast")

macd_slow   = input.int(26, "MACD Slow")

macd_signal = input.int(9, "MACD Signal")

st_factor   = input.float(3.0, "Supertrend Multiplicador")

st_period   = input.int(10, "Supertrend Periodo")

sar_start   = input.float(0.02, "SAR Inicio")

sar_inc     = input.float(0.02, "SAR Incremento")

sar_max     = input.float(0.2, "SAR Max")

// Cálculos de las Funciones de Tendencia Integradas

[macdLine, signalLine, histLine] = ta.macd(close, macd_fast, macd_slow, macd_signal) [cite: 4, 18]

[supertrend, direction] = ta.supertrend(st_factor, st_period) [cite: 2, 20]

psar_val = ta.sar(sar_start, sar_inc, sar_max)

vwap_val = ta.vwap // Variable de serie temporal de volumen ponderado

[plusDI, minusDI, adx_val] = ta.dmi(14, 14) [cite: 16, 21]

// Lógica de Validación de Confluencia

bool tend_alcista = (macdLine > signalLine) and (direction < 0) and (close > psar_val) and (close > vwap_val) and (plusDI > minusDI and adx_val > 25)

bool tend_bajista = (macdLine < signalLine) and (direction > 0) and (close < psar_val) and (close < vwap_val) and (minusDI > plusDI and adx_val > 25)

// Visualización en Gráfico Principal

bgcolor(tend_alcista ? color.new(color.green, 90) : tend_bajista ? color.new(color.red, 90) : na)

plot(supertrend, color=direction < 0 ? color.green : color.red, linewidth=2, title="Supertrend Overlay")

plot(psar_val, style=plot.style_cross, color=color.purple, title="Parabolic SAR dots")

plot(vwap_val, color=color.orange, style=plot.style_circles, title="VWAP")

4. Volatilidad

La volatilidad cuantifica la dispersión estadística de los retornos de un activo financiero en un período de tiempo predefinido^6^.

ta.tr() (True Range)

- **Fórmula matemática**:
- **Parámetros**:

- handle_gaps (simple bool): Permite especificar si se deben tener en cuenta los huecos (gaps) de apertura entre sesiones para el cálculo del rango de fluctuación^2^.

Pine Script

//@version=5

indicator("Catálogo - True Range", overlay=false)

tr_val = ta.tr(true) // Considera gaps

plot(tr_val, color=color.red, title="True Range")

ta.atr() (Average True Range)

- **Fórmula matemática**:
- **Parámetros**:

- length (simple int): Ventana de observación hacia atrás^4^.

Pine Script

//@version=5

indicator("Catálogo - Average True Range", overlay=false)

atr_len = input.int(14, "Longitud ATR")

atr_val = ta.atr(atr_len)

plot(atr_val, color=color.red, title="ATR")

ta.bb() (Bollinger Bands)

- **Fórmula matemática**:
Donde  es la desviación estándar poblacional en la ventana de cálculo ^4^.
- **Parámetros**:

- series (series float), length (simple int), mult (simple float)^4^.

- **Comportamiento**: Retorna una tupla con tres series de datos: la banda superior, la media y la banda inferior^4^. Las bandas se expanden o contraen de forma dinámica en respuesta directa al comportamiento de la desviación estándar de los precios^4^.

Pine Script

//@version=5

indicator("Catálogo - Bollinger Bands", overlay=true)

bb_len = input.int(20, "Longitud BB")

bb_mult = input.float(2.0, "Multiplicador BB")

[middle, upper, lower] = ta.bb(close, bb_len, bb_mult)

plot(middle, color=color.blue, title="BB Media")

plot(upper, color=color.teal, title="BB Superior")

plot(lower, color=color.teal, title="BB Inferior")

ta.bbw() (Bollinger Bands Width)

- **Fórmula matemática**:
- **Parámetros**: Identifica el mismo conjunto de Bollinger Bands y normaliza la distancia entre las bandas extremas para facilitar la comparación entre activos.

Pine Script

//@version=5

indicator("Catálogo - Bollinger Bands Width", overlay=false)

bbw_len = input.int(20, "Longitud BBW")

bbw_mult = input.float(2.0, "Multiplicador BBW")

bbw_val = ta.bbw(close, bbw_len, bbw_mult)

plot(bbw_val, color=color.blue, title="BBW")

ta.kc() (Keltner Channels)

- **Fórmula matemática**:
- **Parámetros**:

- series (series float), length (simple int), mult (simple float), useTrueRange (simple bool)^4^.

- **Comportamiento**: Retorna la tupla con los valores de las bandas superior, media e inferior^4^. A diferencia de Bollinger, emplea el rango medio (ATR) para ensanchar el canal, lo que produce una estructura de tendencia más estable y menos sensible a picos transitorios de volatilidad^4^.

Pine Script

//@version=5

indicator("Catálogo - Keltner Channels", overlay=true)

kc_len = input.int(20, "Longitud KC")

kc_mult = input.float(1.5, "Multiplicador KC")

[kc_mid, kc_up, kc_dn] = ta.kc(close, kc_len, kc_mult, true)

plot(kc_mid, color=color.orange, title="KC Medio")

plot(kc_up, color=color.red, title="KC Superior")

plot(kc_dn, color=color.green, title="KC Inferior")

ta.kcw() (Keltner Channels Width)

- **Fórmula matemática**:

Pine Script

//@version=5

indicator("Catálogo - Keltner Channels Width", overlay=false)

kcw_len = input.int(20, "Longitud KCW")

kcw_mult = input.float(1.5, "Multiplicador KCW")

kcw_val = ta.kcw(close, kcw_len, kcw_mult, true)

plot(kcw_val, color=color.orange, title="KCW")

ta.stdev() (Standard Deviation)

- **Fórmula matemática**:
Donde  es la media de la serie temporal en los últimos  períodos.

Pine Script

//@version=5

indicator("Catálogo - Standard Deviation", overlay=false)

stdev_len = input.int(20, "Longitud StDev")

stdev_val = ta.stdev(close, stdev_len)

plot(stdev_val, color=color.teal, title="Desviación Estándar")

ta.variance() (Variance)

- **Fórmula matemática**:

Pine Script

//@version=5

indicator("Catálogo - Variance", overlay=false)

var_len = input.int(20, "Longitud Varianza")

var_val = ta.variance(close, var_len)

plot(var_val, color=color.purple, title="Varianza")

5. Volumen

El volumen representa la densidad transaccional que valida o contradice la sostenibilidad de los movimientos del precio en el análisis cuantitativo^5^.

ta.obv() (On Balance Volume)

- **Fórmula matemática**:
- **Interpretación**: Es un indicador acumulativo que asocia el volumen negociado directamente con la dirección del precio de cierre. Permite detectar acumulaciones institucionales silenciosas (cuando el OBV sube mientras el precio se mantiene en un rango estrecho) o distribuciones de posiciones.

Pine Script

//@version=5

indicator("Catálogo - On Balance Volume", overlay=false)

obv_val = ta.obv

plot(obv_val, color=color.blue, title="OBV")

ta.accdist() (Accumulation/Distribution Line)

- **Fórmula matemática**:
Donde  representa el Close Location Value, que oscila entre  (cuando el precio cierra exactamente en el mínimo) y  (cuando cierra en el máximo).
- **Interpretación**: Evalúa la presión compradora o vendedora según la ubicación relativa del precio de cierre dentro del rango de fluctuación de la barra (máximo-mínimo)^4^.

Pine Script

//@version=5

indicator("Catálogo - Accumulation Distribution", overlay=false)

adl_val = ta.accdist

plot(adl_val, color=color.orange, title="A/D Line")

ta.pvt() (Price Volume Trend)

- **Fórmula matemática**:
- **Interpretación**: A diferencia del OBV, el PVT acumula únicamente una fracción del volumen diario, ponderada de forma proporcional a la magnitud del cambio porcentual registrado en el precio de cierre^4^.

Pine Script

//@version=5

indicator("Catálogo - Price Volume Trend", overlay=false)

pvt_val = ta.pvt

plot(pvt_val, color=color.teal, title="PVT")

ta.vwap y ta.mfi()

Estas funciones combinan el precio y el volumen en su cálculo matemático^5^. En el caso de ta.vwap, se calcula de forma acumulativa a lo largo de la sesión intradía^2^:

Por su parte, ta.mfi() utiliza el volumen para ponderar las fuerzas de momentum relativas^15^.

Pine Script

//@version=5

indicator("Catálogo - VWAP y MFI Integrados", overlay=true)

mfi_out = ta.mfi(close, 14) // Oscilador de volumen

vwap_out = ta.vwap // Variable built-in de volumen ponderado por precio

plot(vwap_out, color=color.orange, linewidth=2, title="VWAP Session")

6. Detección de Patrones y Cruces

La lógica de decisión de un sistema algorítmico depende de la identificación precisa de transiciones de estado en las variables continuas para convertirlas en señales lógicas discretas^2^.

ta.crossover(), ta.crossunder(), ta.cross()

- **Lógica de Operación**:

- ta.crossover(x, y): Retorna true si la serie  cruza por encima de  en la barra actual ( y )^4^.
- ta.crossunder(x, y): Retorna true si la serie  cruza por debajo de  en la barra actual ( y )^4^.
- ta.cross(x, y): Retorna true si se produce cualquiera de los dos eventos anteriores en la barra actual^4^.

Pine Script

//@version=5

indicator("Catálogo - Cruces de Señales", overlay=true)

fast_ma = ta.ema(close, 9)

slow_ma = ta.ema(close, 21)

cruce_up = ta.crossover(fast_ma, slow_ma)

cruce_dn = ta.crossunder(fast_ma, slow_ma)

plot(fast_ma, color=color.green)

plot(slow_ma, color=color.red)

plotshape(cruce_up, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)

plotshape(cruce_dn, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)

ta.rising(), ta.falling(), ta.change()

- **Lógica de Operación**:

- ta.rising(source, length): Retorna true si los valores de la serie son estrictamente crecientes durante el período especificado ( para todo )^1^.
- ta.falling(source, length): Retorna true si los valores de la serie son estrictamente decrecientes durante el período especificado^4^.
- ta.change(source, length): Retorna la diferencia de la serie actual respecto a su valor de hace  barras ()^4^.

Pine Script

//@version=5

indicator("Catálogo - Pendiente y Cambios", overlay=false)

subiendo = ta.rising(close, 3) [cite: 1]

bajando  = ta.falling(close, 3)

cambio   = ta.change(close, 1)

plot(cambio, color=cambio > 0 ? color.green : color.red, style=plot.style_columns)

7. Pivotes y Extremos

Los extremos y pivotes estructurales permiten identificar niveles históricos de soporte y resistencia en los gráficos de precios^23^.

ta.pivothigh() y ta.pivotlow()

- **Mecánica Temporal**: Estas funciones evalúan si un punto es un extremo local comparando su valor con un número de barras a su izquierda (leftbars) y a su derecha (rightbars)^4^. Esto significa que la confirmación de un pivote introduce un desfase temporal obligatorio de  barras (equivalente a rightbars) antes de que el indicador pueda confirmar y retornar el valor del extremo^24^. No se pueden utilizar para entradas en tiempo real sin tener en cuenta este desfase, ya que de lo contrario se introduciría un sesgo de anticipación (lookahead bias) en el backtesting^24^.

Pine Script

//@version=5

indicator("Catálogo - Pivotes Confirmados", overlay=true)

piv_high = ta.pivothigh(high, 5, 5)

piv_low  = ta.pivotlow(low, 5, 5)

// Se grafican con un desplazamiento hacia atrás (offset) para ubicarlos en la barra real del pivote [cite: 25]

plotshape(not na(piv_high), "PH", shape.labeldown, location.abovebar, color.red, offset=-5)

plotshape(not na(piv_low), "PL", shape.labelup, location.belowbar, color.green, offset=-5)

ta.highest(), ta.lowest(), ta.highestbars(), ta.lowestbars()

- **Parámetros**:

- source (series float), length (simple int)^4^.

- **Comportamiento**:

- ta.highest() y ta.lowest() retornan los valores máximos y mínimos alcanzados por la serie dentro de la ventana de análisis^4^.
- ta.highestbars() y ta.lowestbars() devuelven el índice relativo de la barra (desplazamiento hacia atrás, representado como un valor entero negativo o cero) donde ocurrió dicho extremo dentro de la ventana^4^.

Pine Script

//@version=5

indicator("Catálogo - Rangos de Extremos", overlay=true)

max_val = ta.highest(high, 20)

min_val = ta.lowest(low, 20)

max_bar_offset = ta.highestbars(high, 20)

plot(max_val, color=color.green, style=plot.style_line)

plot(min_val, color=color.red, style=plot.style_line)

8. Búsqueda y Conteo

Estas funciones permiten buscar y rastrear eventos o condiciones pasadas a lo largo de las series temporales^2^.

ta.barssince(), ta.valuewhen(), ta.cum()

- ta.barssince(condition): Cuenta el número de barras transcurridas desde la última vez que la condición se evaluó como true^4^.
- ta.valuewhen(condition, source, occurrence): Captura el valor que tenía la serie source en el instante exacto en que la condición lógica se cumplió, permitiendo especificar el índice de ocurrencia histórica (0 para la más reciente, 1 para la anterior, etc.)^1^.
- ta.cum(source): Calcula la suma acumulada de la serie desde la primera barra histórica disponible en el gráfico^4^.

Pine Script

//@version=5

indicator("Catálogo - Búsqueda de Condiciones", overlay=false)

cond_cierre_verde = close > open

barras_desde = ta.barssince(cond_cierre_verde)

precio_anterior = ta.valuewhen(cond_cierre_verde, close, 1)

suma_cierres = ta.cum(close)

plot(barras_desde, color=color.blue, title="Barras desde cierre verde")

9. Estadísticas y Regresión

El análisis estadístico permite evaluar el comportamiento y las relaciones entre diferentes variables de mercado^2^.

ta.correlation() y ta.linreg()

- ta.correlation(source1, source2, length): Calcula el coeficiente de correlación de Pearson entre dos series sobre una ventana de  períodos^4^.
- ta.linreg(source, length, offset): Calcula el valor proyectado utilizando mínimos cuadrados sobre una recta de regresión lineal^4^. El parámetro offset permite desplazar la recta hacia adelante o hacia atrás en el eje temporal^4^.

Pine Script

//@version=5

indicator("Catálogo - Correlación y Regresión", overlay=false)

correlacion = ta.correlation(close, volume, 20)

regresion   = ta.linreg(close, 20, 0)

plot(correlacion, color=color.green, title="Correlación Precio/Volumen")

ta.percentile_linear_interpolation() y ta.percentile_nearest_rank()

Estas funciones ordenan los datos de la serie y calculan el valor correspondiente a un percentil determinado^4^. La primera utiliza interpolación lineal para calcular valores intermedios, mientras que la segunda devuelve el valor real más cercano de la serie ordenada^4^.

Pine Script

//@version=5

indicator("Catálogo - Percentiles Estadísticos", overlay=false)

percentil_lin = ta.percentile_linear_interpolation(close, 20, 90)

percentil_nr  = ta.percentile_nearest_rank(close, 20, 90)

plot(percentil_lin, color=color.blue, title="Percentil Lineal")

plot(percentil_nr, color=color.orange, title="Percentil Nearest")

ta.percentrank(), ta.median(), ta.mode()

- ta.percentrank(source, length): Retorna la posición relativa (en porcentaje) del valor actual respecto a todos los demás valores dentro de la ventana de análisis^4^.
- ta.median(source, length): Retorna el valor central (percentil 50) de la serie ordenada en la ventana^4^.
- ta.mode(source, length): Retorna el valor con mayor frecuencia de aparición en la serie de datos^4^. Si hay múltiples valores con la misma frecuencia, devuelve el más pequeño^4^.

Pine Script

//@version=5

indicator("Catálogo - Tendencia Central", overlay=false)

rango_p = ta.percentrank(close, 50)

mediana = ta.median(close, 50)

moda    = ta.mode(close, 50)

plot(rango_p, color=color.purple)

10. Funciones Matemáticas Complementarias (math.*)

El namespace math.* provee funciones aritméticas de alto rendimiento optimizadas para el motor de ejecución nativo de TradingView^4^.

Redondeos, Truncamientos y Valores Absolutos

- math.abs(x): Retorna el valor absoluto de la serie^4^.
- math.ceil(x): Redondea hacia arriba al número entero más cercano^10^.
- math.floor(x): Redondea hacia abajo al número entero más cercano^10^.
- math.round(x, precision): Redondea un valor al número especificado de decimales^4^.

Pine Script

//@version=5

indicator("Catálogo - Redondeo Matemático", overlay=false)

val = -5.674

redondeo_abs   = math.abs(val)

redondeo_ceil  = math.ceil(val)

redondeo_floor = math.floor(val)

redondeo_std   = math.round(val, 2)

plot(redondeo_std, title="Redondeo")

Potencias, Logaritmos y Raíces

- math.log(x): Calcula el logaritmo natural (base )^10^. Es fundamental para calcular los retornos logarítmicos continuos de un activo: .
- math.log10(x): Calcula el logaritmo en base 10^7^.
- math.exp(x): Calcula la función exponencial ^10^.
- math.pow(base, exponent): Eleva un valor a la potencia especificada^4^.
- math.sqrt(x): Calcula la raíz cuadrada de un valor^4^.
- math.sign(x): Retorna el signo de un número (1 para positivo, -1 para negativo, 0 para cero)^4^.

Pine Script

//@version=5

indicator("Catálogo - Logaritmos y Potencias", overlay=false)

retorno_log = math.log(close) - math.log(close[1])

raiz_calc   = math.sqrt(math.abs(close))

signo_cambio = math.sign(ta.change(close))

plot(retorno_log, title="Retornos Logarítmicos")

Comparación, Agregación y Selección de Datos

- math.max(x1, x2, ...) y math.min(x1, x2, ...): Retornan el valor máximo y mínimo de una lista de argumentos^8^.
- math.avg(x1, x2, ...): Calcula el promedio de una lista de valores^9^.
- math.sum(source, length): Calcula la suma acumulada de los últimos  valores de una serie^10^.
- math.random(min, max): Genera un valor pseudoaleatorio dentro del rango especificado^4^.

Pine Script

//@version=5

indicator("Catálogo - Agregadores", overlay=false)

precio_max = math.max(open, high, low, close)

precio_avg = math.avg(open, close)

suma_cierre = math.sum(close, 10)

plot(precio_max, title="Máximo de Vela")

Trigonometría y Conversiones de Ángulo

Las funciones trigonométricas operan utilizando radianes^4^. Para facilitar su uso en modelos cíclicos, se proporcionan funciones de conversión de ángulos^7^.

- math.toradians(degrees): Convierte grados sexagesimales a radianes^7^.
- math.todegrees(radians): Convierte radianes a grados^7^.
- math.sin(), math.cos(), math.tan(): Calculan el seno, coseno y tangente de un ángulo en radianes^4^.
- math.asin(), math.acos(), math.atan(): Funciones inversas que retornan el ángulo en radianes^10^.

Pine Script

//@version=5

indicator("Catálogo - Trigonometría Cíclica", overlay=false)

angulo_grados = 45.0

angulo_rad = math.toradians(angulo_grados)

seno_calc = math.sin(angulo_rad)

plot(seno_calc, title="Seno 45 Grados")

11. Warm-up Period y Manejo de Datos na

El motor de ejecución de TradingView ejecuta el script de forma secuencial sobre cada barra histórica disponible en el gráfico^1^. En las primeras barras, cualquier indicador que dependa de un período de observación hacia atrás (length) no dispondrá de suficientes datos históricos para su cálculo y devolverá el valor de indefinición matemática na^1^.

El Fenómeno del Warm-up Period

Si un indicador como una EMA requiere un período de 200 barras, el valor devuelto durante las primeras 199 barras del gráfico será na^4^. Este comportamiento es normal y necesario para garantizar la estabilidad matemática de los cálculos recursivos^3^.

Propagación de Valores na

El valor na es altamente "contagioso" en las operaciones de Pine Script^9^. Cualquier operación aritmética (+, -, *, /) o de comparación que involucre un valor na dará como resultado un valor na^9^. Esto puede provocar fallos en cadena que dejen sin calcular los indicadores del gráfico.

Mitigación y Recuperación con nz() y fixnan()

- nz(source, replacement): Evalúa la serie y, si encuentra un valor na en la barra actual, lo sustituye por un valor alternativo (por defecto 0.0)^4^. Es indispensable para inicializar variables acumulativas de estado que requieren autorreferenciarse.
- fixnan(source): Soluciona discontinuidades temporales sustituyendo el valor na actual por el último valor válido anterior (non-na) registrado en la serie histórica^4^.

Pine Script

//@version=5

indicator("Catálogo - Manejo Avanzado de na", overlay=false)

// Ejemplo de inicialización segura para evitar contagios de na

var float acumulador = 0.0

acumulador := acumulador + nz(close) // nz previene que el acumulador se rompa si close es na

// Reparación de series discontinuas

precio_alcista = close > open ? close : na

precio_continuo = ta.fixnan(precio_alcista) // Reemplaza na con el último cierre alcista válido

plot(precio_continuo, color=color.blue, title="Serie Temporal Reparada")

12. Implementación Manual vs. Built-in

La elección entre utilizar las funciones integradas de Pine Script o codificar un algoritmo de cálculo manual afecta directamente a la eficiencia computacional y a la flexibilidad del código^2^.

Eficiencia y Optimización Computacional

Las funciones del namespace ta.* se ejecutan en un entorno precompilado optimizado en C++ dentro de los servidores de TradingView^2^. El uso de bucles manuales (for, while) para calcular promedios o indicadores en cada barra consume recursos de procesamiento significativos, lo que puede ralentizar la carga de gráficos y provocar fallos por exceso de tiempo de ejecución en conjuntos de datos históricos extensos^4^.

Flexibilidad y Personalización Dinámica de Parámetros

En Pine Script v5, la mayoría de los indicadores integrados requieren parámetros de longitud estáticos de tipo simple int para asegurar que el motor de ejecución pueda reservar la memoria necesaria para el histórico de datos^3^. Si el modelo de trading requiere variar la longitud de un indicador de forma dinámica en cada barra (por ejemplo, adaptándolo a la volatilidad o a ciclos de mercado), el desarrollador está obligado a crear una implementación matemática manual empleando arrays o bucles^2^.

A continuación se muestra un ejemplo comparativo entre la implementación matemática de un indicador EMA integrado y uno manual dinámico adaptativo:

Pine Script

//@version=5

indicator("EMA Built-in vs Dinámica Adaptativa", overlay=true)

long_base = input.int(20, "Longitud Base")

// 1. Ejecución optimizada utilizando la función integrada (Longitud constante)

ema_builtin = ta.ema(close, long_base)

// 2. Implementación manual dinámica adaptativa (Longitud variable en tiempo real)

// En este escenario, la longitud se adapta inversamente a la volatilidad del ATR

atr_ratio = ta.atr(14) / ta.atr(100)

longitud_dinamica = math.max(5, math.min(100, math.round(long_base / nz(atr_ratio, 1.0))))

// Función de cálculo manual recursivo para EMA con longitud variable tipo serie

f_ema_dinamica(src, len) =>

    alpha = 2.0 / (len + 1.0)

    var float val_ema = na

    val_ema := na(val_ema[1]) ? src : (alpha * src) + ((1.0 - alpha) * nz(val_ema[1], src))

    val_ema

ema_dinamica = f_ema_dinamica(close, longitud_dinamica)

plot(ema_builtin, color=color.gray, linewidth=1, title="Built-In Estática")

plot(ema_dinamica, color=color.blue, linewidth=2, title="Manual Adaptativa")

13. Tres Combinaciones Prácticas Implementadas

A continuación se presentan tres scripts completos de nivel profesional, escritos en Pine Script v5 y listos para ser implementados en producción^1^.

A. Sistema de Confluencia: RSI + MACD + Supertrend para Scoring de Señales

Este sistema de confluencia asigna una puntuación ponderada al estado del mercado evaluando de forma simultánea el momentum, la inercia y los límites de volatilidad del precio^2^.

Pine Script

//@version=5

indicator("Sistema Avanzado de Scoring de Señales", overlay=true, max_labels_count=500)

// Parámetros de Optimización de Filtros

rsi_len = input.int(14, "Periodo RSI", group="Configuración RSI")

rsi_ob  = input.int(70, "Sobrecompra RSI", group="Configuración RSI")

rsi_os  = input.int(30, "Sobreventa RSI", group="Configuración RSI")

macd_f  = input.int(12, "MACD Rápido", group="Configuración MACD")

macd_s  = input.int(26, "MACD Lento", group="Configuración MACD")

macd_sg = input.int(9,  "MACD Señal", group="Configuración MACD")

st_fact = input.float(3.0, "Supertrend Multiplicador", group="Configuración Supertrend")

st_atr  = input.int(10, "Supertrend Periodo", group="Configuración Supertrend")

score_crit = input.int(3, "Score Mínimo Requerido", minval=1, maxval=4)

// Declaración de Variables de Cálculo Nativas

rsi_val = ta.rsi(close, rsi_len)

[macd_line, signal_line, _] = ta.macd(close, macd_f, macd_s, macd_sg) [cite: 4, 18]

[st_val, st_dir] = ta.supertrend(st_fact, st_atr)

ema_filtro = ta.ema(close, 200)

// Evaluación del Scoring Direccional

int score_alcista = 0

int score_bajista = 0

// Factor 1: Condición Inercial MACD

score_alcista := score_alcista + (macd_line > signal_line ? 1 : 0)

score_bajista := score_bajista + (macd_line < signal_line ? 1 : 0)

// Factor 2: Fuerza del Impulso RSI

score_alcista := score_alcista + (rsi_val > 50 ? 1 : 0)

score_bajista := score_bajista + (rsi_val < 50 ? 1 : 0)

// Factor 3: Límite de Volatilidad Supertrend

score_alcista := score_alcista + (st_dir < 0 ? 1 : 0)

score_bajista := score_bajista + (st_dir > 0 ? 1 : 0)

// Factor 4: Dirección Tendencial de Largo Plazo (Media Móvil 200)

score_alcista := score_alcista + (close > ema_filtro ? 1 : 0)

score_bajista := score_bajista + (close < ema_filtro ? 1 : 0)

// Generación de Señales por Confluencia de Puntuación

bool buy_trigger  = (score_alcista >= score_crit) and (score_alcista[1] < score_crit)

bool sell_trigger = (score_bajista >= score_crit) and (score_bajista[1] < score_crit)

// Representación en Pantalla

plotshape(buy_trigger, "Compra Confirmada", shape.triangleup, location.belowbar, color.green, size=size.medium, text="BUY SCORE")

plotshape(sell_trigger, "Venta Confirmada", shape.triangledown, location.abovebar, color.red, size=size.medium, text="SELL SCORE")

// Pintar Fondo de Acuerdo al Scoring de Mercado

color_scoring = score_alcista >= score_crit ? color.new(color.green, 92) : score_bajista >= score_crit ? color.new(color.red, 92) : na

bgcolor(color_scoring)

B. Detector de Régimen de Mercado: ATR + ADX + Bollinger Band Width para Clasificar trending/ranging/volatile

Este indicador analiza de forma combinada la volatilidad del precio y la fuerza de la tendencia para clasificar el entorno de mercado actual en uno de cuatro estados o regímenes de volatilidad^5^.

Pine Script

//@version=5

indicator("Detector de Régimen de Mercado Pro", overlay=false)

// Configuración de Parámetros de Entrada

adx_len   = input.int(14, "Periodo ADX")

adx_level = input.int(25, "Umbral ADX para Tendencia")

bb_len    = input.int(20, "Periodo Bandas de Bollinger")

bb_mult   = input.float(2.0, "Multiplicador Bollinger")

ma_filtro_bbw = input.int(50, "Media para Normalizar BBW")

// Cálculos de Estructuras Dinámicas

[_, _, adx_val] = ta.dmi(adx_len, adx_len) [cite: 16, 21]

bbw_val = ta.bbw(close, bb_len, bb_mult)

ma_bbw  = ta.sma(bbw_val, ma_filtro_bbw)

// Lógica de Clasificación de Régimen

bool es_tendencial = adx_val > adx_level

bool es_compresion = bbw_val < ma_bbw

string regimen = "Indefinido"

color color_regimen = color.gray

if es_tendencial and not es_compresion

    regimen := "Tendencial Volátil"

    color_regimen := color.green

else if es_tendencial and es_compresion

    regimen := "Tendencial en Compresión"

    color_regimen := color.teal

else if not es_tendencial and not es_compresion

    regimen := "Rango Volátil Lateral"

    color_regimen := color.orange

else if not es_tendencial and es_compresion

    regimen := "Acumulación / Compresión Extrema"

    color_regimen := color.red

// Renderizado de las Series Temporales de Volatilidad

plot(bbw_val, "Ancho de Bollinger", color=color.blue, linewidth=2)

plot(ma_bbw, "Promedio del Ancho", color=color.gray, style=plot.style_dashed)

// Panel Informativo Flotante en Pantalla

var table info_box = table.new(position.top_right, 2, 2, bgcolor=color.new(color.black, 30), border_color=color.black, border_width=1)

if barstate.islast

    table.cell(info_box, 0, 0, "Régimen Actual:", text_color=color.white, text_size=size.small)

    table.cell(info_box, 1, 0, regimen, bgcolor=color_regimen, text_color=color.white, text_size=size.small)

    table.cell(info_box, 0, 1, "Fuerza ADX:", text_color=color.white, text_size=size.small)

    table.cell(info_box, 1, 1, str.tostring(adx_val, "#.##"), text_color=color.white, text_size=size.small)

C. Scanner de Divergencias: RSI Divergence Detector con Labels Automáticos

Este scanner avanzado localiza de manera automática divergencias regulares (tanto alcistas como bajistas) entre el precio y el oscilador RSI utilizando pivotes estructurales confirmados^15^.

Pine Script

//@version=5

indicator("Scanner de Divergencias de RSI", overlay=true, max_lines_count=500, max_labels_count=500)

// Configuración de Filtros

rsi_periodo = input.int(14, "Longitud RSI")

izq_piv     = input.int(5, "Pivotes Izquierda")

der_piv     = input.int(5, "Pivotes Derecha")

rsi_val = ta.rsi(close, rsi_periodo)

// Localización de Estructuras Pivote en el RSI y en los Precios

piv_alto_rsi  = ta.pivothigh(rsi_val, izq_piv, der_piv) [cite: 25]

piv_bajo_rsi  = ta.pivotlow(rsi_val, izq_piv, der_piv)

piv_alto_pr   = ta.pivothigh(high, izq_piv, der_piv) [cite: 25]

piv_bajo_pr   = ta.pivotlow(low, izq_piv, der_piv)

// Captura de Coordenadas de los Pivotes Previos Confirmados con sus Índices Reales

var float  p_alto_rsi_prev = na

var int    idx_alto_rsi_prev = na

var float  p_alto_pr_prev  = na

var int    idx_alto_pr_prev  = na

var float  p_bajo_rsi_prev = na

var int    idx_bajo_rsi_prev = na

var float  p_bajo_pr_prev  = na

var int    idx_bajo_pr_prev  = na

// 1. Evaluación de Estructuras para Divergencias Bajistas

if not na(piv_alto_rsi) and not na(piv_alto_pr) [cite: 25]

    if not na(p_alto_rsi_prev)

        // Divergencia Regular Bajista: Precio hace un máximo más alto, RSI hace un máximo más bajo

        if high[der_piv] > p_alto_pr_prev and rsi_val[der_piv] < p_alto_rsi_prev

            line.new(x1=idx_alto_pr_prev, y1=p_alto_pr_prev, x2=bar_index - der_piv, y2=high[der_piv], color=color.red, width=2) [cite: 1]

            label.new(x=bar_index - der_piv, y=high[der_piv], text="Divergencia Bajista", color=color.red, textcolor=color.white, style=label.style_label_down) [cite: 1]

    // Actualizar registros históricos de pivotes altos

    p_alto_rsi_prev := piv_alto_rsi

    idx_alto_rsi_prev := bar_index - der_piv

    p_alto_pr_prev  := high[der_piv]

    idx_alto_pr_prev  := bar_index - der_piv

// 2. Evaluación de Estructuras para Divergencias Alcistas

if not na(piv_bajo_rsi) and not na(piv_bajo_pr)

    if not na(p_bajo_rsi_prev)

        // Divergencia Regular Alcista: Precio hace un mínimo más bajo, RSI hace un mínimo más alto

        if low[der_piv] < p_bajo_pr_prev and rsi_val[der_piv] > p_bajo_rsi_prev

            line.new(x1=idx_bajo_pr_prev, y1=p_bajo_pr_prev, x2=bar_index - der_piv, y2=low[der_piv], color=color.green, width=2)

            label.new(x=bar_index - der_piv, y=low[der_piv], text="Divergencia Alcista", color=color.green, textcolor=color.white, style=label.style_label_up)

    // Actualizar registros históricos de pivotes bajos

    p_bajo_rsi_prev := piv_bajo_rsi

    idx_bajo_rsi_prev := bar_index - der_piv

    p_bajo_pr_prev  := low[der_piv]

    idx_bajo_pr_prev  := bar_index - der_piv

Fuentes citadas

- Writing / Debugging - TradingView, https://www.tradingview.com/pine-script-docs/v5/writing/debugging/
- Open-source transpiler that converts TradingView Pine Script (v5 and early v6) indicators to clean, executable JavaScript for Node.js. - GitHub, https://github.com/MeridianAlgo/Pine-A-Script
- To Pine Script® version 5 - Migration guides - TradingView, https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-5/
- A minimal reference to pine script v5 - GitHub Gist, https://gist.github.com/kdkiss/731e6288e2314a7e6f36383888e5bc40
- TradingView Pine Script ta.vwma - Volume Weighted Moving Average - offline-pixel, https://offline-pixel.github.io/tradingview-pinescript/ta-vwma/
- TradingView Pine Script ta.kama - Kaufman Adaptive Moving Average - offline-pixel, https://offline-pixel.github.io/tradingview-pinescript/ta-kama/
- A minimal reference to pine script v5 - GitHub Gist, https://gist.github.com/dnavarrom/5b8a36411a8a6fb2a0380d12cfe52673
- Pine Script Dili Başvuru Kitabı — TradingView, https://tr.tradingview.com/pine-script-reference/v6/
- Pine Script Language Reference Manual — TradingView, https://www.tradingview.com/pine-script-reference/v5/
- Migration_guides / 迁移至Pine Script™ 版本5, https://pine-script-docs-zh.netlify.app/pine-script-docs/migration-guides/to-pine-version-5/
- python - Arnaud Legoux Moving Average (ALMA) in NumPy - Stack Overflow, https://stackoverflow.com/questions/46990098/arnaud-legoux-moving-average-alma-in-numpy
- Pine Script Double EMA (DEMA) - Complete TradingView Guide - offline-pixel, https://offline-pixel.github.io/pinescript-strategies/pine-script-DEMA.html
- Trend - What is OpenAlgo? | Documentation, https://docs.openalgo.in/trading-platform/python/indicators/trend
- Pine Script Triple EMA (TEMA) - Complete TradingView Guide, https://offline-pixel.github.io/pinescript-strategies/pine-script-TEMA.html
- TradingView Pine Script ta.mfi - Money Flow Index - offline-pixel, https://offline-pixel.github.io/tradingview-pinescript/ta-mfi/
- I want to make a PineScript V5 Strategy with ADX and RSI But keep receiving the same error, https://stackoverflow.com/questions/75828537/i-want-to-make-a-pinescript-v5-strategy-with-adx-and-rsi-but-keep-receiving-the
- Algo Play: Turbocharging MACD with ATR, DEMA, and ADX - ChartVPS, https://chartvps.com/workshop/algo-play-turbocharging-macd-with-atr-dema-and-adx/
- Why doesn't Pinescript recognise DEMA? - Stack Overflow, https://stackoverflow.com/questions/77160897/why-doesnt-pinescript-recognise-dema
- Newest 'tradingview-api' Questions - Stack Overflow, https://stackoverflow.com/questions/tagged/tradingview-api?tab=Newest
- I'm writing Pine Script in Trading View but I keep getting this error - Stack Overflow, https://stackoverflow.com/questions/79289935/im-writing-pine-script-in-trading-view-but-i-keep-getting-this-error
- A minimal reference to pine script v5 - GitHub Gist, https://gist.github.com/kaigouthro/b95a8b4c43e607ea71897e204904b9c0
- How can I access future bars high/low in pinescript - Reddit, https://www.reddit.com/r/pinescript/comments/1gp9kat/how_can_i_access_future_bars_highlow_in_pinescript/
- How pivothigh() and pivotlow() function work on Tradingview Pinescript? - Stack Overflow, https://stackoverflow.com/questions/64019553/how-pivothigh-and-pivotlow-function-work-on-tradingview-pinescript
- pine script - Plotting pivot high/lows with offset vs Actually saving the price of pivot high/low, https://stackoverflow.com/questions/78279005/plotting-pivot-high-lows-with-offset-vs-actually-saving-the-price-of-pivot-high
- Manual de referencia del lenguaje Pine Script — TradingView, https://es.tradingview.com/pine-script-reference/v5/
- How do I optimize my Pinescript script (make it faster and simpler to read)? - Stack Overflow, https://stackoverflow.com/questions/76755549/how-do-i-optimize-my-pinescript-script-make-it-faster-and-simpler-to-read
- TradingView 自動下單教學｜免費程式碼、設定步驟一次搞懂 - 謝富傑期貨分析師, https://itradesoeasy.com/tradingview-touchance-auto-trade/