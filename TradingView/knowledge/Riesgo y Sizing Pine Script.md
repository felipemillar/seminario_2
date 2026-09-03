Manual de Ingeniería Cuantitativa: Gestión de Riesgo, Dimensionamiento de Posición y Control de Drawdown en Pine Script v6

1. La Función strategy.exit() en Detalle: Mecánica de Órdenes de Salida

El motor de simulación de TradingView procesa las salidas de mercado mediante la función strategy.exit(), un comando diseñado para generar órdenes de salida vinculadas de forma directa a una o varias entradas específicas^1^. Comprender la totalidad de sus parámetros es un requisito fundamental para diseñar sistemas de trading cuantitativo robustos.

A diferencia de las órdenes de entrada o cierre general (como strategy.close()), las órdenes generadas por strategy.exit() actúan bajo un principio de reserva de volumen^2^. Esto significa que, una vez emitida una orden de salida para una determinada posición, el volumen especificado queda comprometido y no puede ser reclamado por otras órdenes de salida simultáneas, evitando la duplicación de cierres o la exposición no deseada al mercado^2^.

Parámetros de strategy.exit()

La firma de la función strategy.exit() en la versión 6 de Pine Script se compone de los siguientes parámetros fundamentales:

| **Parámetro** | **Tipo de Dato** | **Función Técnica** |
| --- | --- | --- |
| id | series string | Identificador único de la orden de salida. Permite su posterior modificación o cancelación manual mediante el identificador correspondiente^4^. |
| from_entry | series string | ID de la orden de entrada de la cual se desea salir^1^. Si no se especifica, el simulador aplicará la regla FIFO (First In, First Out) por defecto^1^. |
| qty | series int/float | Cantidad exacta de unidades (acciones, contratos o lotes) a cerrar^3^. Si no se define, se liquida la totalidad de la posición de la entrada asociada^6^. |
| qty_percent | series int/float | Porcentaje de la posición abierta actual (o de la entrada especificada en from_entry) que se cerrará, facilitando las salidas parciales^3^. Su valor debe oscilar entre 0 y 100. |
| profit | series int/float | Objetivo de ganancia expresado en **ticks** desde el precio de entrada^2^. Representa una distancia flotante que se calcula dinámicamente según el paso mínimo del activo (syminfo.mintick)^9^. |
| loss | series int/float | Límite de pérdida expresado en **ticks** desde el precio de entrada^2^. Actúa como un stop loss relativo basado en la distancia de ticks especificada^7^. |
| limit | series int/float | Objetivo de ganancia (take profit) especificado como un nivel de **precio absoluto**^8^. Reemplaza el cálculo de distancia por una barrera estática en el gráfico. |
| stop | series int/float | Nivel de stop loss clásico especificado como un **precio absoluto**^4^. Representa el punto exacto de cotización donde la posición debe ser liquidada inmediatamente. |
| trail_price | series int/float | Nivel de **precio absoluto** en el cual se activará el trailing stop dinámico^9^. Hasta que el mercado no alcance este nivel, la orden de trailing permanece inactiva^9^. |
| trail_points | series int/float | Distancia en **ticks** desde el precio de entrada requerida para activar el trailing stop^9^. Ofrece una alternativa dinámica a trail_price. |
| trail_offset | series int/float | Distancia en **ticks** que mantendrá el stop loss con respecto al extremo máximo (para compras) o mínimo (para ventas) alcanzado por el precio^9^. |
| comment | series string | Texto que se mostrará en el gráfico y en la lista de operaciones del probador de estrategias al ejecutarse la orden de salida^11^. |
| comment_profit | series string | Comentario específico que se imprimirá si la salida ocurre por la ejecución del objetivo límite o profit^11^. |
| comment_loss | series string | Comentario específico que se imprimirá si la salida ocurre por la ejecución del stop loss^11^. |
| comment_trailing | series string | Comentario específico que se imprimirá si la salida se ejecuta a través del trailing stop dinámico^11^. |
| alert_message | series string | Mensaje personalizado que se enviará en el payload de las alertas webhooks al completarse la orden de salida^12^. |

Parámetros Eliminados: El Parámetro when en Pine Script v6

Es de vital importancia destacar que el parámetro when, ampliamente utilizado en versiones anteriores de Pine Script para condicionar la colocación de la orden de salida, **ha sido completamente eliminado en Pine Script v6**^8^. En la versión 5, pasar una condición booleana a when permitía controlar si la función se ejecutaba o no^8^.

En la versión v6, este patrón de diseño genera un error de compilación inmediato^8^. El desarrollador debe reestructurar el flujo utilizando bloques condicionales imperativos if^8^. Esta modificación obliga a un diseño de código mucho más limpio y estructurado, evitando la persistencia de órdenes fantasma en la pila de memoria del simulador.

Pine Script

// Patrón de diseño obsoleto (Pine Script v5):

// strategy.exit("Exit_ID", "Long_Entry", loss = 100, when = exit_condition)

// Patrón de diseño obligatorio y optimizado (Pine Script v6):

if (exit_condition)

    strategy.exit("Exit_ID", from_entry="Long_Entry", loss=100)

Diferencia Matemática: Parámetros Relativos (Profit/Loss) vs. Absolutos (Limit/Stop)

La distinción entre los parámetros relativos (profit, loss, trail_points) y los absolutos (limit, stop, trail_price) radica en el método mediante el cual el motor de ejecución calcula y actualiza los precios de liquidación^8^.

Los parámetros relativos miden la distancia desde el precio de entrada del activo utilizando ticks^2^. Matemáticamente, un tick representa el cambio mínimo posible en el precio de un activo, definido en Pine Script por el valor flotante de la variable del sistema syminfo.mintick^9^. Por ejemplo, en el índice S&P 500 (ES), un punto de cotización se compone de 4 ticks de  USD^14^. Si un quant define un parámetro de pérdida relativo loss = 40, el stop loss real en una posición de compra iniciada a un precio de entrada  se calculará mediante la siguiente ecuación:

Sustituyendo los valores para un precio de entrada de  USD:

Por el contrario, los parámetros absolutos (limit, stop, trail_price) requieren que el desarrollador introduzca un nivel de precio real y explícito^8^. Esto permite vincular las salidas de forma directa a indicadores técnicos complejos (como medias móviles, canales de Keltner o estructuras previas del mercado) sin necesidad de realizar conversiones previas a ticks^16^:

Cambios de Comportamiento Críticos entre v5 y v6

En Pine Script v5, cuando una función strategy.exit() recibía tanto un parámetro relativo como un parámetro absoluto correspondiente (por ejemplo, especificar tanto profit como limit), el motor de TradingView descartaba de forma silenciosa el valor relativo y utilizaba exclusivamente el nivel de precio absoluto especificado^8^.

En Pine Script v6, este comportamiento ha cambiado drásticamente: **el motor evalúa ambos niveles de forma concurrente y ejecuta la orden de salida al nivel que el mercado alcance primero**^8^. Si un desarrollador migra un script de v5 a v6 que contenía un parámetro residual profit = 0 junto a un parámetro limit = close + 100, en la versión v6 el simulador interpretará el profit = 0 como un objetivo de salida de cero ticks de distancia, liquidando la posición de forma inmediata en la siguiente barra y arruinando la lógica del sistema^8^.

Múltiples Exits para la Misma Entrada y Reserva de Cantidades

Pine Script permite asociar múltiples órdenes strategy.exit() a un único identificador de entrada^6^. Para que este proceso funcione correctamente sin que las órdenes entren en conflicto o se cancelen mutuamente, el motor de ejecución opera bajo el principio de **reserva de cantidades** en orden de prioridad de llamada^2^.

Cuando se ejecuta una orden de entrada, el total de unidades de la posición queda disponible para ser cerrado^6^. Al declarar la primera función strategy.exit(), esta reclama y reserva para sí una porción del volumen total de la posición basada en el parámetro qty o qty_percent^3^. Las llamadas subsiguientes a strategy.exit() solo podrán reclamar volumen sobre la porción de la posición que permanezca libre de reserva ("unreserved quantity")^3^.

Si la suma de las cantidades especificadas en los diferentes comandos de salida supera la cantidad total de la posición abierta, el motor ajustará automáticamente el tamaño de las últimas órdenes para que coincida exactamente con el volumen remanente de la posición, evitando así que el sistema abra una posición inversa no deseada de forma accidental^6^.

2. Trailing Stop Avanzado: Dinámica de Volatilidad y Estructura

El trailing stop es un algoritmo dinámico que protege los beneficios acumulados permitiendo que la orden de parada de pérdidas acompañe el movimiento favorable del precio, permaneciendo inalterable si el mercado retrocede en su contra^7^.

Parámetros trail_points y trail_offset

El funcionamiento del trailing stop nativo de strategy.exit() se rige por la interacción de dos parámetros definidos en ticks^9^:

- **trail_points**: Define el umbral de ganancia necesario (desde el precio de entrada) para que el trailing stop empiece a funcionar^9^. Hasta que el precio de cierre o el precio intrabarra no alcance este nivel de beneficio acumulado, el trailing stop permanece inactivo^9^.
- **trail_offset**: Establece la distancia fija (en ticks) a la que la orden stop seguirá al precio una vez activada la funcionalidad de trailing^9^.

Mecánica de Activación de Trailing Stop (Posición de Compra / Long):

Precio 

  ^                                                      * [Punto Máximo Alcanzado]

  |                                                     /|

  |                                                    / |

  |                                 * [Precio activa  /  |  <--- trail_offset

  |                                /|  trailing]     /   |       (Distancia de seguimiento)

  |                               / |               /    |

  |                              /  |              /     v

  |                             /   |             /------* [Nuevo Stop Trailed]

  |                            /    |            /

  |                           /     v           /

  |                          /------* [Stop    /

  |                         /          Activado]

  |  * [Precio de Entrada] /

  +--|--------------------/--------------------------------------------> Tiempo

     |<-- trail_points -->|

Una vez que el precio supera el umbral definido por trail_points (expresado en ticks), el stop loss se coloca automáticamente a una distancia de trail_offset ticks por debajo del precio máximo alcanzado^9^. A partir de ese momento, cada vez que el activo registre un nuevo máximo, el stop de salida se desplazará hacia arriba manteniendo estrictamente la distancia del offset^9^. Si el precio cae, el stop de salida permanece inmóvil en el nivel más alto alcanzado, actuando como una barrera de salida definitiva^14^.

Código Funcional para Trailing Stop Basado en ATR

El Average True Range (ATR) proporciona una medida objetiva de la volatilidad del mercado^21^. Un trailing stop adaptativo ajusta la distancia de seguimiento según las condiciones del mercado, ampliando la distancia en regímenes volátiles para evitar salidas prematuras y ajustándola en entornos de baja volatilidad^14^.

Pine Script

//@version=6

strategy("Trailing Stop Basado en ATR", overlay=true, margin_long=100, margin_short=100)

// Parámetros técnicos de entrada

atr_length = input.int(14, title="Periodo ATR")

atr_multiplier = input.float(3.5, title="Multiplicador ATR")

ma_fast_len = input.int(20, title="Media Rápida")

ma_slow_len = input.int(50, title="Media Lenta")

// Cálculo de indicadores

atr = ta.atr(atr_period)

ma_fast = ta.ema(close, ma_fast_len)

ma_slow = ta.ema(close, ma_slow_len)

// Condiciones de cruce para entrada

long_condition = ta.crossover(ma_fast, ma_slow)

short_condition = ta.crossunder(ma_fast, ma_slow)

// Variables de estado persistente para el trailing stop

var float long_trail_stop = na

var float short_trail_stop = na

// Lógica de cálculo dinámico para el Trailing Stop de compra

if (strategy.position_size > 0)

    potential_stop = close - (atr * atr_multiplier)

    // El trailing stop para compras solo puede desplazarse de manera ascendente

    long_trail_stop := na(long_trail_stop[1]) ? potential_stop : math.max(potential_stop, long_trail_stop[1])

else

    long_trail_stop := na

// Lógica de cálculo dinámico para el Trailing Stop de venta

if (strategy.position_size < 0)

    potential_stop = close + (atr * atr_multiplier)

    // El trailing stop para ventas solo puede desplazarse de manera descendente

    short_trail_stop := na(short_trail_stop[1]) ? potential_stop : math.min(potential_stop, short_trail_stop[1])

else

    short_trail_stop := na

// Ejecución de órdenes de mercado y salidas condicionales

if (long_condition and strategy.position_size == 0)

    strategy.entry("Long_Trade", strategy.long)

if (short_condition and strategy.position_size == 0)

    strategy.entry("Short_Trade", strategy.short)

// Cierre de operaciones mediante el uso de stop absoluto dinámico

if (strategy.position_size > 0)

    strategy.exit("Exit_Long", from_entry="Long_Trade", stop=long_trail_stop)

if (strategy.position_size < 0)

    strategy.exit("Exit_Short", from_entry="Short_Trade", stop=short_trail_stop)

// Visualización técnica

plot(strategy.position_size > 0 ? long_trail_stop : na, title="ATR Long Stop", color=color.green, style=plot.style_linebr, linewidth=2)

plot(strategy.position_size < 0 ? short_trail_stop : na, title="ATR Short Stop", color=color.red, style=plot.style_linebr, linewidth=2)

Código Funcional para Chandelier Exit

El Chandelier Exit es un indicador de seguimiento de tendencias desarrollado por Charles Le Beau que sitúa el stop loss a partir del máximo más alto alcanzado durante la operación (para posiciones largas) corregido por un múltiplo de volatilidad (ATR)^20^. Esto permite dar suficiente margen al precio para oscilar dentro del ruido diario normal sin amenazar la permanencia en la tendencia principal^14^.

Pine Script

//@version=6

strategy("Chandelier Exit Trailing", overlay=true, margin_long=100, margin_short=100)

// Parámetros Chandelier Exit

chandelier_period = input.int(22, title="Periodo del Extremo Chandelier")

chandelier_mult = input.float(3.0, title="Multiplicador ATR")

// Indicadores base

atr = ta.atr(chandelier_period)

highest_high = ta.highest(high, chandelier_period)

lowest_low = ta.lowest(low, chandelier_period)

// Cálculo teórico de salidas

chandelier_long_stop = highest_high - (atr * chandelier_mult)

chandelier_short_stop = lowest_low + (atr * chandelier_mult)

// Variables persistentes de control de dirección

var float active_chandelier_stop = na

if (strategy.position_size > 0)

    // El stop de compra solo se mueve a favor del beneficio (hacia arriba)

    active_chandelier_stop := na(active_chandelier_stop[1]) ? chandelier_long_stop : math.max(chandelier_long_stop, active_chandelier_stop[1])

else if (strategy.position_size < 0)

    // El stop de venta solo se mueve a favor del beneficio (hacia abajo)

    active_chandelier_stop := na(active_chandelier_stop[1]) ? chandelier_short_stop : math.min(chandelier_short_stop, active_chandelier_stop[1])

else

    active_chandelier_stop := na

// Entrada de ejemplo mediante cruce de Donchian Channels

if (ta.crossover(close, ta.highest(high[1], 20)) and strategy.position_size == 0)

    strategy.entry("Long_Chandelier", strategy.long)

if (ta.crossunder(close, ta.lowest(low[1], 20)) and strategy.position_size == 0)

    strategy.entry("Short_Chandelier", strategy.short)

// Salida unificada mediante el uso de la variable dinámica de stop absoluto

if (strategy.position_size > 0)

    strategy.exit("Exit_Chandelier_Long", from_entry="Long_Chandelier", stop=active_chandelier_stop)

if (strategy.position_size < 0)

    strategy.exit("Exit_Chandelier_Short", from_entry="Short_Chandelier", stop=active_chandelier_stop)

plot(active_chandelier_stop, title="Chandelier Stop", color=strategy.position_size > 0 ? color.lime : color.orange, style=plot.style_linebr, linewidth=2)

Código Funcional para Parabolic SAR como Trailing Stop

El indicador Parabolic SAR (Stop and Reverse) calcula un stop dinámico que se acelera con el tiempo a medida que la tendencia avanza^20^. Es especialmente efectivo en mercados con un fuerte impulso tendencial.

Pine Script

//@version=6

strategy("Parabolic SAR Trailing Stop", overlay=true, margin_long=100, margin_short=100)

// Configuración del Parabolic SAR

sar_start = input.float(0.02, title="Factor de Inicio (Aceleración)")

sar_inc = input.float(0.02, title="Factor de Incremento")

sar_max = input.float(0.2, title="Factor Máximo de Aceleración")

psar = ta.sar(sar_start, sar_inc, sar_max)

// Entrada basada en la posición relativa del precio con el PSAR

if (ta.crossover(close, psar) and strategy.position_size == 0)

    strategy.entry("Long_PSAR", strategy.long)

if (ta.crossunder(close, psar) and strategy.position_size == 0)

    strategy.entry("Short_PSAR", strategy.short)

// Aplicación del stop utilizando el indicador PSAR como límite estricto de liquidación

if (strategy.position_size > 0)

    strategy.exit("Exit_PSAR_Long", from_entry="Long_PSAR", stop=psar)

if (strategy.position_size < 0)

    strategy.exit("Exit_PSAR_Short", from_entry="Short_PSAR", stop=psar)

plot(psar, title="PSAR Stop Activo", color=color.purple, style=plot.style_cross, linewidth=2)

3. Position Sizing Dinámico: Modelos de Asignación de Capital

El tamaño de la posición determina de forma directa la esperanza matemática y la probabilidad de ruina de un sistema de inversión^23^.

Fixed Fractional (Fracción Fija de Equity)

Bajo el modelo Fixed Fractional, el capital arriesgado en cada operación representa un porcentaje constante del capital total disponible (Equity)^16^. Este método introduce una progresión geométrica que escala el volumen operativo durante periodos de ganancias acumuladas y contrae la exposición tras rachas de pérdidas, protegiendo al sistema de la ruina asintótica^26^.

Matemáticamente, la fórmula para determinar el tamaño de la posición () es^20^:

Donde  representa la fracción del capital a arriesgar (por ejemplo, el 1% o 2%)^20^.

Fixed Ratio (Ryan Jones)

Propuesto por Ryan Jones, el método de Fixed Ratio regula el incremento de contratos en función de un "Delta" (un incremento de beneficio requerido por contrato)^27^. A diferencia de la fracción fija, la tasa de crecimiento del capital requerido para añadir una nueva unidad de riesgo disminuye a medida que aumenta el volumen operado^27^.

La fórmula matemática para determinar la cantidad de contratos o unidades () en función del beneficio acumulado () y la constante  es la siguiente^28^:

Alternativamente, el volumen también se puede calcular en función del balance total de la cuenta^29^:

Criterio de Kelly (Kelly Criterion)

El Criterio de Kelly maximiza el crecimiento logarítmico del capital a largo plazo calculando la fracción óptima de capital a arriesgar basándose en la probabilidad histórica de acierto () y la relación de pago o ratio riesgo-recompensa ()^23^.

Donde:

- : Fracción del capital sugerida para arriesgar^31^.
- : Probabilidad histórica de acierto (Win Rate)^23^.
- : Ratio riesgo-recompensa medio de la estrategia (Ganancia media / Pérdida media)^23^.

Debido a que el Criterio de Kelly completo suele generar una volatilidad extrema en la curva de capital y drawdowns difíciles de asumir en la práctica, se suele aplicar una fracción de este (como el medio o cuarto de Kelly) para amortiguar el riesgo y compensar posibles errores de estimación en los parámetros históricos de la estrategia^23^.

Volatility-Based Sizing (Tamaño Basado en Volatilidad)

Este enfoque ajusta el tamaño de la posición de manera inversa a la volatilidad histórica del activo^16^. Esto asegura que la contribución de riesgo de cada operación permanezca constante a lo largo del tiempo, reduciendo el tamaño de la posición en mercados volátiles y aumentándolo en mercados tranquilos^25^.

Comparativa de Métodos de Sizing

La siguiente tabla detalla la viabilidad operativa y la sensibilidad ante rachas adversas de cada modelo:

| **Modelo de Sizing** | **Input Requerido** | **Sensibilidad al Drawdown** | **Comportamiento del Crecimiento** | **Complejidad de Implementación** |
| --- | --- | --- | --- | --- |
| **Fixed Fractional** | Distancia Stop + Equity^26^ | Proporcional (Auto-ajustable) | Geométrico exponencial^26^ | Muy Baja |
| **Fixed Ratio** | Beneficio Neto + Delta^28^ | Lento en reducir exposición^27^ | Asimétrico parabólico^27^ | Media |
| **Criterio de Kelly** | Tasa de Acierto + R:R^31^ | Muy alta (riesgo de ruina si está mal calibrado)^23^ | Máximo teórico compuesto^31^ | Alta |
| **Volatility-Based** | ATR de mercado^20^ | Controlado por volatilidad^25^ | Lineal / Variable^29^ | Baja |

Diferencia entre strategy.equity y strategy.initial_capital

El cálculo del tamaño de la posición varía significativamente si se utiliza el capital inicial estático o los fondos de la cuenta actualizados en tiempo real:

- **strategy.initial_capital**: Devuelve el capital inicial especificado en la declaración de la estrategia o en el panel de propiedades^33^. Es un valor constante. Su uso en algoritmos de asignación de capital genera una progresión lineal (aritmética) del tamaño de las posiciones, lo cual no aprovecha el interés compuesto.
- **strategy.equity**: Representa el balance total de la cuenta en tiempo real, compuesto por el capital inicial, el beneficio neto realizado de las operaciones cerradas y el beneficio/pérdida latente de las posiciones actualmente abiertas^34^. Su uso introduce un componente dinámico y geométrico de capitalización compuesta^26^.

Configuración de default_qty_type en la Declaración strategy()

El parámetro default_qty_type define cómo interpreta el motor de TradingView el valor numérico especificado en el parámetro qty de las funciones de entrada (como strategy.entry()) cuando este no se especifica de forma explícita^6^:

- **strategy.percent_of_equity**: Interpreta la cantidad como un porcentaje de la equidad total de la cuenta disponible en el momento de la ejecución^33^.
- **strategy.fixed**: Procesa la cantidad de manera estricta como un número constante de contratos, acciones o lotes^13^.
- **strategy.cash**: Interpreta la cantidad como el importe monetario total de la moneda base que se utilizará para abrir la posición^6^.

4. Cálculo de Riesgo por Trade: Fórmula de Lotes y Apalancamiento

El dimensionamiento de la posición en base al riesgo exige calcular con precisión la cantidad de contratos o unidades a comprar o vender antes de enviar una orden al mercado^20^. Este cálculo evita que las fluctuaciones normales del precio pongan en peligro la supervivencia de la cuenta de trading^24^.

La fórmula matemática para determinar la cantidad de unidades () es la siguiente^20^:

Parámetros de la Fórmula

- **Equity**: Capital total disponible en la cuenta en tiempo real (strategy.equity)^34^.
- **Risk %**: El porcentaje de pérdida máximo permitido sobre la equidad para una sola operación (por ejemplo, el 1% o 2%)^20^.
- **Precio Entrada**: El precio de ejecución esperado para la orden de entrada^36^.
- **Precio Stop**: El nivel de precio de salida definitiva del mercado en caso de pérdida^4^.
- **Valor del Punto**: El multiplicador que define el valor monetario de un punto completo del activo para un único contrato (syminfo.pointvalue)^14^. En acciones convencionales este valor es 1.0, mientras que en futuros de materias primas o índices financieros puede variar significativamente^14^.

Ajuste de Apalancamiento e Impacto del Margen

El apalancamiento permite controlar posiciones de mercado de mayor valor que el saldo disponible en la cuenta^34^. Sin embargo, la fórmula de riesgo por trade se calcula en base a la pérdida potencial en dólares (definida por la distancia al stop loss) y no se ve afectada por el apalancamiento financiero^20^.

El apalancamiento únicamente afecta al capital de garantía requerido (margen) para poder abrir la posición^34^. Si la cantidad calculada por la fórmula de riesgo exige un margen superior al saldo disponible de la cuenta (según los parámetros margin_long o margin_short especificados), la operación será rechazada por el simulador por falta de capital de garantía, independientemente de que el riesgo matemático de la operación esté dentro de los límites permitidos^34^.

Redondeo a Lotes Mínimos de Operación

Los brókers y los exchanges de criptomonedas imponen limitaciones de volumen en la colocación de órdenes, exigiendo que el tamaño de la posición sea un múltiplo exacto de su paso de lote mínimo (por ejemplo, operando con múltiplos de 0.01 lotes en Forex, 0.0001 BTC en criptomonedas o lotes de 100 acciones en mercados bursátiles tradicionales)^3^. El motor de TradingView puede simular ejecuciones erróneas o ficticias si el script envía órdenes con decimales que no coinciden con las especificaciones del mercado^3^.

Para resolver esto en Pine Script, el desarrollador debe calcular y aplicar el redondeo descendente más cercano al tamaño de lote mínimo permitido utilizando la función math.floor():

Este procedimiento garantiza la compatibilidad del script con las especificaciones del mercado real^3^.

Código Completo y Compilable de Cálculo de Riesgo con Redondeo

El siguiente script calcula de forma dinámica el tamaño de la posición arriesgando un porcentaje fijo de la equidad disponible, ajustando la orden según el tamaño del contrato del activo y redondeando el volumen final al lote mínimo permitido:

Pine Script

//@version=6

strategy("Cálculo Dinámico de Riesgo y Redondeo", overlay=true, initial_capital=100000, margin_long=100, margin_short=100)

// Parámetros de la estrategia

risk_pct_input = input.float(1.0, title="Riesgo por Operación (%)", minval=0.1, maxval=5.0)

min_lot_size = input.float(0.01, title="Tamaño de Lote Mínimo (Lote Step)")

atr_len = input.int(14, title="Periodo ATR")

atr_multiplier = input.float(2.0, title="Multiplicador ATR")

// Cálculo de indicadores

atr = ta.atr(atr_len)

ema_signal = ta.ema(close, 20)

// Condiciones de cruce

long_condition = ta.crossover(close, ema_signal)

short_condition = ta.crossunder(close, ema_signal)

// Proceso de entrada y cálculo de riesgo para operaciones de compra

if (long_condition and strategy.position_size == 0)

    entry_price = close

    stop_price = entry_price - (atr * atr_multiplier)

    stop_distance = entry_price - stop_price

    if (stop_distance > 0)

        // Aplicación de la fórmula de riesgo por trade ajustada por valor del punto

        total_risk_usd = strategy.equity * (risk_pct_input / 100.0)

        raw_qty = total_risk_usd / (stop_distance * syminfo.pointvalue)

        // Redondeo descendente estricto al lote mínimo permitido

        final_qty = math.floor(raw_qty / min_lot_size) * min_lot_size

        if (final_qty > 0)

            strategy.entry("Long_Entry", strategy.long, qty=final_qty)

            strategy.exit("Exit_Long", from_entry="Long_Entry", stop=stop_price)

// Proceso de entrada y cálculo de riesgo para operaciones de venta

if (short_condition and strategy.position_size == 0)

    entry_price = close

    stop_price = entry_price + (atr * atr_multiplier)

    stop_distance = stop_price - entry_price

    if (stop_distance > 0)

        total_risk_usd = strategy.equity * (risk_pct_input / 100.0)

        raw_qty = total_risk_usd / (stop_distance * syminfo.pointvalue)

        // Redondeo descendente estricto al lote mínimo permitido

        final_qty = math.floor(raw_qty / min_lot_size) * min_lot_size

        if (final_qty > 0)

            strategy.entry("Short_Entry", strategy.short, qty=final_qty)

            strategy.exit("Exit_Short", from_entry="Short_Entry", stop=stop_price)

5. Estrategias de Stop Loss: Invalidación Técnica y Volatilidad

El stop loss no debe ser una distancia arbitraria en el gráfico, sino un umbral de invalidación técnica o estadística de la hipótesis que motivó la entrada al mercado^16^.

1. Stop Loss Fijo en Puntos/Pips

Consiste en establecer una distancia constante en ticks para todas las operaciones, asumiendo una volatilidad estable en el corto plazo^16^. Es útil en mercados que presentan un comportamiento de rango muy regular.

Pine Script

//@version=6

strategy("Stop Loss Fijo", overlay=true)

ticks_distance = input.int(300, title="Distancia de Stop Loss en Ticks")

if (ta.crossover(ta.rsi(close, 14), 30))

    strategy.entry("Long_Fixed", strategy.long)

if (strategy.position_size > 0)

    // El stop se coloca a una distancia fija en ticks calculada desde el precio de entrada de la posición activa

    stop_level = strategy.position_avg_price - (ticks_distance * syminfo.mintick)

    strategy.exit("Exit_Fixed", from_entry="Long_Fixed", stop=stop_level)

2. Stop Loss Basado en ATR (Volatilidad)

Ajusta la distancia de seguridad basándose en el comportamiento de la volatilidad del mercado en el pasado reciente, alejando la parada de pérdidas durante periodos de alta volatilidad y acercándola cuando disminuye el rango de oscilación del precio^14^.

Pine Script

//@version=6

strategy("Stop Loss ATR", overlay=true)

atr_len = input.int(14, title="Periodo ATR")

atr_multiplier = input.float(2.5, title="Multiplicador ATR")

atr = ta.atr(atr_len)

if (ta.crossover(ta.macd(close, 12, 26, 9), 0))

    strategy.entry("Long_ATR", strategy.long)

if (strategy.position_size > 0)

    // Se calcula la distancia del stop en base al valor del ATR

    stop_level = strategy.position_avg_price - (atr * atr_multiplier)

    strategy.exit("Exit_ATR", from_entry="Long_ATR", stop=stop_level)

3. Stop Loss Basado en Estructura de Mercado (Swing High/Low)

Sitúa el stop loss por debajo de los mínimos técnicos recientes (para posiciones largas) o por encima de los máximos técnicos (para posiciones cortas)^16^. Este método se basa en el principio de que una tendencia alcista solo se invalida cuando el precio rompe los mínimos que estructuran el movimiento^16^.

Pine Script

//@version=6

strategy("Stop Loss Estructural", overlay=true)

lookback = input.int(10, title="Periodo de Búsqueda Swing")

// Búsqueda del mínimo más bajo de los últimos 'n' periodos

swing_low = ta.lowest(low, lookback)

// Guardamos el nivel stop de forma estática en el momento de la entrada

var float saved_stop = na

if (ta.crossover(ta.sma(close, 10), ta.sma(close, 30)))

    strategy.entry("Long_Structure", strategy.long)

    saved_stop := swing_low

if (strategy.position_size > 0)

    strategy.exit("Exit_Structure", from_entry="Long_Structure", stop=saved_stop)

else

    saved_stop := na

4. Stop Loss Basado en Bandas de Bollinger

Coloca el stop loss en el exterior de las bandas de desviación estándar, asumiendo que el cierre del precio por fuera de las bandas representa un movimiento de alta probabilidad de reversión^38^.

Pine Script

//@version=6

strategy("Stop Loss Bandas de Bollinger", overlay=true)

bb_len = input.int(20, title="Periodo BB")

bb_dev = input.float(2.0, title="Desviación Estándar")

[middle, upper, lower] = ta.bb(close, bb_len, bb_dev)

if (ta.crossover(close, lower))

    strategy.entry("Long_BB", strategy.long)

if (strategy.position_size > 0)

    // El stop se coloca en el nivel de la banda inferior actualizable en tiempo real

    strategy.exit("Exit_BB", from_entry="Long_BB", stop=lower)

5. Stop Loss Basado en Percentil del Rango Reciente

Esta metodología calcula el stop en un nivel de percentil de los cierres o rangos recientes empleando el método de interpolación lineal, permitiendo que la volatilidad y la distribución de los precios de corto plazo determinen el nivel de salida^17^.

Pine Script

//@version=6

strategy("Stop Loss Percentil", overlay=true)

percentile_period = input.int(20, title="Periodo de Datos")

percentile_pct = input.float(15.0, title="Percentil Objetivo", minval=0.0, maxval=100.0)

// Array para el almacenamiento de datos históricos

var float[] price_array = array.new_float(0)

// Sincronización del tamaño del array con el periodo solicitado

array.push(price_array, low)

if (array.size(price_array) > percentile_period)

    array.shift(price_array)

// Cálculo matemático del percentil

percentile_stop = array.percentile_linear_interpolation(price_array, percentile_pct)

if (ta.crossover(ta.rsi(close, 14), 40))

    strategy.entry("Long_Percentile", strategy.long)

if (strategy.position_size > 0)

    strategy.exit("Exit_Percentile", from_entry="Long_Percentile", stop=percentile_stop)

6. Take Profit Strategies: Maximización Dinámica de Beneficios

La correcta distribución de los objetivos de toma de ganancias permite optimizar la tasa de acierto y la ganancia promedio por operación, influyendo directamente en el ratio de Sharpe del sistema.

1. Take Profit Fijo con Ratio R:R (Riesgo:Recompensa)

Define el objetivo de ganancias multiplicando la distancia del stop loss inicial por un ratio fijo de asimetría matemática (ej.  o )^42^. Esto garantiza una expectativa matemática de retorno positiva incluso con tasas de acierto inferiores al 50%.

Pine Script

//@version=6

strategy("Take Profit Fijo R:R", overlay=true)

rr_ratio = input.float(2.0, title="Ratio Riesgo-Recompensa (X R)")

var float stop_price = na

var float profit_price = na

if (ta.crossover(ta.ema(close, 10), ta.ema(close, 20)))

    strategy.entry("Long_RR", strategy.long)

    // Se guarda la distancia de stop inicial (ej. 2 * ATR)

    stop_distance = ta.atr(14) * 2.0

    stop_price := close - stop_distance

    profit_price := close + (stop_distance * rr_ratio)

if (strategy.position_size > 0)

    strategy.exit("Exit_RR", from_entry="Long_RR", stop=stop_price, limit=profit_price)

2. Take Profit Parcial (Scale-Out)

Cerrar una fracción de la posición al alcanzar un primer objetivo de ganancias ayuda a asegurar beneficios y reduce la exposición del capital durante retrocesos intermedios del precio^6^.

Pine Script

//@version=6

strategy("Take Profit Parcial", overlay=true)

partial_qty_pct = input.float(50.0, title="Porcentaje de Cierre en TP1 (%)")

var float entry_price = na

var float stop_level = na

var float tp_1 = na

var float tp_2 = na

if (ta.crossover(ta.sma(close, 10), ta.sma(close, 20)))

    strategy.entry("Long_Partial", strategy.long)

    entry_price := close

    stop_level := close - (ta.atr(14) * 2.0)

    tp_1 := close + (ta.atr(14) * 1.5)

    tp_2 := close + (ta.atr(14) * 3.5)

if (strategy.position_size > 0)

    // Cierre parcial del volumen asignado al tocar TP1

    strategy.exit("TP1", from_entry="Long_Partial", qty_percent=partial_qty_pct, limit=tp_1, stop=stop_level)

    // Liquidación del remanente al alcanzar el objetivo final TP2

    strategy.exit("TP2", from_entry="Long_Partial", limit=tp_2, stop=stop_level)

3. Take Profit Basado en Extensiones de Fibonacci

Esta técnica sitúa los objetivos de salida en los niveles de expansión matemática derivados de un movimiento previo del precio (retroceso o impulso), que suelen actuar como zonas de resistencia psicológica para el mercado.

Pine Script

//@version=6

strategy("Take Profit Fibonacci", overlay=true)

fib_ext = input.float(1.618, title="Extensión Fibonacci Objetivo")

lookback = input.int(20, title="Periodo de Oscilación")

high_pivot = ta.highest(high, lookback)

low_pivot = ta.lowest(low, lookback)

swing_range = high_pivot - low_pivot

// El objetivo límite se sitúa a partir de la expansión del rango de oscilación

fib_target_price = high_pivot + (swing_range * fib_ext)

if (ta.crossover(close, high_pivot[1]))

    strategy.entry("Long_Fib", strategy.long)

if (strategy.position_size > 0)

    strategy.exit("Exit_Fib", from_entry="Long_Fib", limit=fib_target_price, stop=low_pivot)

4. Take Profit Trailing (Dejar Correr las Ganancias)

En lugar de cerrar la posición en un objetivo estático, se puede definir un nivel de activación para iniciar un trailing stop dinámico, permitiendo maximizar los beneficios durante tendencias prolongadas del mercado^7^.

Pine Script

//@version=6

strategy("Take Profit Trailing Activo", overlay=true)

activation_ticks = input.int(400, title="Ticks para Activar Trailing")

trail_offset_ticks = input.int(100, title="Distancia de Trailing (Ticks)")

if (ta.crossover(ta.ema(close, 20), ta.ema(close, 50)))

    strategy.entry("Long_Trail", strategy.long)

if (strategy.position_size > 0)

    // El trailing stop se activará tras acumular los ticks de beneficio correspondientes

    strategy.exit("Exit_Trail", from_entry="Long_Trail", trail_points=activation_ticks, trail_offset=trail_offset_ticks)

7. Break-Even Stops: Protección del Capital Operativo

La lógica de break-even modifica la orden stop loss original de la operación activa trasladándola al precio promedio de entrada en el momento en que el precio alcanza un umbral determinado de beneficio no realizado (el trigger)^20^. Esto protege el capital de la cuenta, garantizando que una posición ganadora no se convierta en perdedora ante una reversión brusca del precio^44^.

Para implementar un break-even robusto en Pine Script v6, se deben utilizar las funciones de la familia strategy.opentrades.* para acceder al precio promedio real de entrada de la posición^11^:

Pine Script

//@version=6

strategy("Break-Even Sistemático", overlay=true)

// Configuración del Break-Even

trigger_multiplier = input.float(1.5, title="Múltiplo ATR para Activación de BE")

stop_multiplier = input.float(2.0, title="Múltiplo ATR para Stop Loss Inicial")

atr = ta.atr(14)

// Variables persistentes para el control de la posición activa

var float initial_stop = na

var bool break_even_active = false

if (ta.crossover(ta.sma(close, 10), ta.sma(close, 30)))

    strategy.entry("Long_BE", strategy.long)

    initial_stop := close - (atr * stop_multiplier)

    break_even_active := false

if (strategy.position_size > 0)

    // Se obtiene el precio exacto de la entrada para evitar retrasos de ejecución

    entry_price = strategy.opentrades.entry_price(0)

    trigger_level = entry_price + (ta.atr(14) * trigger_multiplier)

    // Si el máximo alcanza el nivel objetivo, se activa la lógica de break-even

    if (high >= trigger_level)

        break_even_active := true

    // Definición del nivel de stop activo final

    final_stop = break_even_active ? entry_price : initial_stop

    strategy.exit("Exit_BE", from_entry="Long_BE", stop=final_stop)

else

    initial_stop := na

    break_even_active := false

8. Piramidación y Escalamiento de Posiciones en Tendencia

La piramidación (pyramiding) es una técnica que consiste en añadir nuevas posiciones a favor de una tendencia ya establecida y en la que la primera operación ya acumula beneficios^45^. Esto permite maximizar las ganancias en tendencias prolongadas.

Mecánica de Piramidación (Escalamiento en Tendencia Alcista):

Precio

  |                                        * [Entrada 3 - Ruptura] (Position Size + 1)

  |                                       / 

  |                   * [Entrada 2] -----/------------------- (Position Size + 1)

  |                  /

  |  * [Entrada 1] -/---------------------------------------- (Position Size 1)

  +--|--------------|---------------------|--------------------> Tiempo

Configuración del Parámetro pyramiding

Para habilitar la adición de nuevas órdenes de entrada en la misma dirección sin requerir un cierre intermedio de la operación previa, se debe especificar el parámetro pyramiding en la declaración de la función strategy() con un valor superior a ^1^:

Pine Script

strategy("Pyramid Strategy", overlay=true, pyramiding=3, margin_long=100, margin_short=100)

Si el parámetro pyramiding no está explícitamente configurado, el motor de ejecución ignorará por defecto cualquier señal de compra adicional si el sistema ya mantiene una posición de compra abierta^1^.

Dollar Cost Averaging (DCA) frente a Estrategias Grid

- **Dollar Cost Averaging (DCA)**: Consiste en acumular posiciones dividiendo el capital total disponible en compras periódicas o ante retrocesos del precio con el fin de promediar el precio de compra hacia niveles inferiores^23^. Es útil en activos con una fuerte tendencia alcista de largo plazo.
- **Estrategias Grid (Rejilla)**: Coloca órdenes límite de compra y de venta a intervalos regulares fijos por encima y por debajo de un precio de referencia preestablecido, sin un stop loss definido^46^. Esta estrategia busca beneficiarse de la oscilación lateral del mercado en rangos definidos, pero presenta un riesgo asimétrico de pérdida total en caso de fuertes movimientos tendenciales unidireccionales de ruptura.

Riesgos Críticos de la Piramidación

La piramidación aumenta la exposición total del de la cuenta de forma asimétrica. Si no se gestiona adecuadamente, una pequeña corrección en contra del movimiento principal puede borrar todas las ganancias acumuladas debido al mayor tamaño de las posiciones más recientes^23^.

Por ello, se recomienda reubicar el stop loss de toda la posición agregada hacia niveles superiores que aseguren un riesgo nulo o mínimo cada vez que se ejecute una nueva entrada.

9. Portfolio-Level Risk: Circuit Breakers de Cartera

Pine Script incluye una serie de funciones nativas diseñadas para limitar el riesgo global de la cuenta directamente desde el código, actuando como interruptores automáticos de seguridad (*circuit breakers*) ante drawdowns excesivos o un número descontrolado de operaciones en un mismo día^6^:

Pine Script

//@version=6

strategy("Portfolio Risk Protection Strategy", overlay=true, margin_long=100, margin_short=100)

// 1. Limitar el Drawdown Máximo al 15% del valor de la cuenta

// Cancela todas las órdenes de la estrategia si las pérdidas superan el 15% de la equidad disponible [cite: 6, 49]

strategy.risk.max_drawdown(15, strategy.percent_of_equity) [cite: 6, 49]

// 2. Limitar el tamaño máximo de posición permitido

// Evita que el algoritmo abra posiciones que superen los 100 contratos de volumen, previniendo errores de cálculo dinámico

strategy.risk.max_position_size(100)

// 3. Limitar el número máximo de órdenes ejecutadas en un solo día

// Detiene la operativa diaria si se alcanzan las 10 órdenes ejecutadas para evitar el "overtrading" excesivo [cite: 6, 50]

strategy.risk.max_intraday_filled_orders(10) [cite: 6, 50]

// 4. Limitar la pérdida intradía permitida al 3%

// Detiene la operativa de la estrategia si las pérdidas del día en curso alcanzan el 3% de la equidad disponible [cite: 6, 13, 51]

strategy.risk.max_intraday_loss(3.0, strategy.percent_of_equity) [cite: 6, 13, 51]

// 5. Restringir la dirección permitida de las operaciones

// Configura al motor para evaluar y permitir únicamente la colocación de órdenes de compra [cite: 6, 19, 52]

strategy.risk.allow_entry_in(strategy.direction.long) [cite: 6, 19, 52]

// Entrada básica de ejemplo

if (ta.crossover(ta.sma(close, 10), ta.sma(close, 20)))

    strategy.entry("Long", strategy.long)

10. Comisión y Deslizamiento: Modelado del Impacto de Fricción Financiera

Un error crítico al desarrollar estrategias cuantitativas es omitir o subestimar el impacto del coste de transacción y el deslizamiento (*slippage*) en la ejecución de las órdenes de mercado^16^. El deslizamiento es la diferencia de precio que se produce entre el momento en que se genera una señal de entrada y el precio real de ejecución de la orden por parte del bróker^14^.

Para simular de forma realista estas comisiones en el probador de estrategias de TradingView, se deben declarar explícitamente estos costes dentro de la función strategy()^55^:

Pine Script

//@version=6

strategy("Realistic Backtest Strategy", 

         overlay=true, 

         initial_capital=100000, 

         commission_type=strategy.commission.percent, 

         commission_value=0.075, // Comisiones del 0.075% por operación (común en brokers de criptomonedas)

         slippage=2,            // Deslizamiento de 2 ticks en cada ejecución [cite: 14]

         margin_long=100, 

         margin_short=100)

Configuración del Tipo de Comisión

- **strategy.commission.percent**: Aplica un cargo porcentual sobre el valor total de mercado de la transacción ejecutada. Es el modelo estándar empleado en bolsas de criptomonedas y mercados bursátiles de acciones.
- **strategy.commission.cash_per_contract**: Cobra una tarifa de dinero fijo por cada contrato negociado. Es la estructura habitual en futuros financieros.
- **strategy.commission.cash_per_order**: Aplica una tarifa fija única por cada orden de entrada o salida completada, independientemente del volumen o cantidad de contratos negociados.

11. Monitorización en Tiempo Real del Drawdown de la Estrategia

El drawdown mide la caída porcentual o absoluta del capital de la cuenta desde su punto máximo acumulado (*peak*) hasta su mínimo posterior, antes de que se registre un nuevo máximo^29^.

Curva de Equidad y Drawdown:

Equidad

  ^      * [Pico Máximo de Equidad]

  |     / \

  |    /   \

  |   /     \     <--- Drawdown Actual (Caída Temporal)

  |  /       \   /

  | /         \ /

  |/           * [Fondo de Equidad]

  +------------------------------------------------------------> Tiempo

Para monitorizar este riesgo en tiempo real y suspender la operativa antes de que el drawdown alcance niveles catastróficos para la cuenta, se puede programar un algoritmo personalizado de cálculo continuo de la caída de capital^44^:

Pine Script

//@version=6

strategy("Drawdown Circuit Breaker Strategy", overlay=true, initial_capital=100000, margin_long=100, margin_short=100)

// Umbral máximo de drawdown tolerado por la cuenta

max_drawdown_allowed_pct = input.float(10.0, title="Drawdown de Cuenta Límite (%)") / 100.0

// Variables de estado persistente

var float equity_peak = 0.0

var bool system_disabled = false

// Actualización del pico histórico de la cuenta

equity_peak := math.max(equity_peak, strategy.equity)

// Cálculo dinámico del drawdown acumulado actual de la cuenta

current_drawdown_pct = equity_peak > 0 ? (equity_peak - strategy.equity) / equity_peak : 0.0

// Alertas y desconexión si se supera el umbral límite de pérdida acumulada

if (current_drawdown_pct >= max_drawdown_allowed_pct)

    system_disabled := true

    strategy.close_all(comment="Circuit Breaker: Drawdown Superado")

    strategy.cancel_all()

// Ejecución condicionada de entradas al estado del sistema

if (not system_disabled and ta.crossover(ta.sma(close, 10), ta.sma(close, 30)))

    strategy.entry("Long_Signal", strategy.long)

plot(equity_peak, title="Pico de Equidad", color=color.blue)

12. Gestión de Margen y Apalancamiento en Multiactivos

El margen representa la porción de capital propio que un operador debe depositar como garantía para abrir o mantener una posición apalancada en el mercado^34^. En TradingView, los parámetros margin_long y margin_short definen el nivel de garantía mínimo que exige el bróker emulado^34^.

Un valor del 20% en margin_long indica un requerimiento de margen del 20%, lo cual equivale a operar con un apalancamiento máximo de ^34^. Si se establece en el 100%, la operativa se realiza sin apalancamiento, exigiendo el respaldo total del capital disponible para abrir cada posición^8^.

Diferencias en los Requerimientos de Margen según el Activo Operado

| **Clase de Activo** | **Apalancamiento Estándar** | **Margen Requerido típico** | **Dinámica de Liquidación y Llamada de Margen** |
| --- | --- | --- | --- |
| **Forex** | Alto ( a ) | a<br>[cite: 34] | Liquidación inmediata intrabarra si la equidad no cubre el margen requerido^34^. |
| **Criptomonedas** | Variable ( a ) | a<br>[cite: 34] | Liquidación dinámica basada en motores de liquidación del exchange^34^. |
| **Acciones** | Bajo ( a ) | a<br>[cite: 34] | Llamadas de margen al final de la jornada de negociación si el colateral disminuye. |

Simulación del Margen Requerido y la Llamada de Margen (Margin Call)

TradingView calcula el colateral mínimo necesario para sostener una posición abierta según la siguiente fórmula^34^:

Si el precio del activo se mueve en contra de la posición y la equidad disponible de la cuenta se reduce por debajo de este margen mínimo requerido, se activa un evento de **Margin Call** (Llamada de Margen)^34^. En este punto, el motor de TradingView liquida de forma automática el volumen de contratos necesario para restablecer la proporción de garantía requerida de la cuenta^34^.

13. Comparativa de Implementación de Sistemas: Pine Script v6 frente a MQL5

Tanto Pine Script v6 como MQL5 (el lenguaje de programación empleado en la suite Plataformas Institucionales) son lenguajes líderes en el desarrollo de trading algorítmico, pero presentan importantes diferencias en su arquitectura y modo de ejecución^58^.

MQL5 es un lenguaje de programación estructurado y orientado a objetos de tipado estricto basado en C++, diseñado principalmente para ejecutar robots de negociación directa (Expert Advisors) en entornos de muy baja latencia^58^. En contraste, Pine Script v6 es un lenguaje de programación funcional basado en vectores y series de tiempo, diseñado por TradingView para simplificar el análisis de gráficos, la visualización de datos y el diseño rápido de estrategias^58^.

A continuación, se comparan sus capacidades arquitectónicas de gestión de riesgos:

| **Característica Técnica** | **Pine Script v6 (TradingView)** | **MQL5 (Plataformas Institucionales)** |
| --- | --- | --- |
| **Arquitectura de Ejecución** | Ejecución en el servidor de TradingView^61^. Cálculos automáticos sincronizados por series temporales de datos^61^. | Ejecución local en la terminal cliente o en servidores VPS^59^. Código compilado de muy baja latencia^60^. |
| **Gestión de Órdenes** | Gestión simplificada mediante el motor simulado (strategy.exit, strategy.entry)^33^. | Gestión de bajo nivel mediante solicitudes comerciales directas (MqlTradeRequest, CSimpleTrade)^59^. |
| **Control de Riesgo de Cuenta** | Control dinámico simplificado mediante variables del sistema de nivel superior^25^. | Acceso de bajo nivel a los datos del balance de la cuenta, margen dinámico, apalancamiento y llamadas de margen^59^. |
| **Modelado de Fricción** | Modulación de deslizamiento y comisiones de fácil configuración en los parámetros^55^. | Requiere simulación de ticks personalizados e importación de spreads históricos del bróker. |
| **Velocidad de Backtesting** | Rápida en servidores, pero restringida por el tamaño de la base de datos de barras^60^. | Excelente, permitiendo optimizaciones complejas y multi-hilo en la nube^59^. |

14. Tres Implementaciones de Sistemas Completos en Pine Script v6

A continuación, se presentan tres implementaciones funcionales completas escritas bajo el estándar de Pine Script v6, listas para su ejecución directa en la plataforma TradingView.

Implementación 1: Position Sizing Basado en ATR, Trailing Stop y Break-Even Automático

Este algoritmo calcula el tamaño de la posición en cada operación en función de la volatilidad del activo (ATR) para arriesgar un porcentaje fijo del capital de la cuenta, gestionando la salida con una lógica automática de break-even y un trailing stop dinámico basado en ATR^14^.

Pine Script

//@version=6

strategy("ATR Sizing, Trailing and BE Strategy", 

         overlay=true, 

         initial_capital=100000, 

         default_qty_type=strategy.percent_of_equity, 

         default_qty_value=100,

         commission_type=strategy.commission.percent,

         commission_value=0.03,

         slippage=1,

         margin_long=100,

         margin_short=100)

// Parámetros de Riesgo y Asignación de Capital

risk_pct = input.float(1.5, title="Riesgo por Operación (%)", minval=0.1, maxval=5.0) / 100.0

atr_period = input.int(14, title="Periodo ATR")

atr_sl_multiplier = input.float(2.0, title="Multiplicador ATR para Stop Loss")

atr_be_multiplier = input.float(1.5, title="ATR para Activar Break-Even")

atr_trail_multiplier = input.float(3.0, title="ATR para Trailing Stop")

// Parámetros Técnicos de Entrada

fast_len = input.int(9, title="EMA Rápida")

slow_len = input.int(21, title="EMA Lenta")

// Indicadores

atr = ta.atr(atr_period)

fast_ema = ta.ema(close, fast_len)

slow_ema = ta.ema(close, slow_len)

// Condiciones de Entrada

long_condition = ta.crossover(fast_ema, slow_ema)

// Variables de Control

var float trade_stop_price = na

var float trade_be_trigger = na

var bool is_be_active = false

var float highest_high_since_entry = na

// Lógica de Ejecución al Generar Señales

if (long_condition and strategy.position_size == 0)

    entry_price = close

    initial_sl_distance = atr * atr_sl_multiplier

    stop_level = entry_price - initial_sl_distance

    // Cálculo dinámico del tamaño de posición ajustado por riesgo

    risk_value = strategy.equity * risk_pct

    raw_qty = risk_value / (initial_sl_distance * syminfo.pointvalue)

    // Redondeo respetando la precisión del contrato

    trade_qty = math.floor(raw_qty / 0.001) * 0.001

    if (trade_qty > 0)

        strategy.entry("Long_Entry", strategy.long, qty=trade_qty)

        trade_stop_price := stop_level

        trade_be_trigger := entry_price + (atr * atr_be_multiplier)

        is_be_active := false

        highest_high_since_entry := high

// Seguimiento dinámico de la posición abierta

if (strategy.position_size > 0)

    highest_high_since_entry := math.max(highest_high_since_entry, high)

    entry_price = strategy.opentrades.entry_price(0)

    // Verificación de activación del Break-Even

    if (not is_be_active and highest_high_since_entry >= trade_be_trigger)

        is_be_active := true

        trade_stop_price := entry_price

    // Lógica de Trailing Stop tras superar el break-even

    if (is_be_active)

        new_trail_stop = highest_high_since_entry - (atr * atr_trail_multiplier)

        trade_stop_price := math.max(trade_stop_price, new_trail_stop)

    // Envío dinámico de la orden de salida

    strategy.exit("Exit_Management", from_entry="Long_Entry", stop=trade_stop_price)

else

    trade_stop_price := na

    trade_be_trigger := na

    is_be_active := false

    highest_high_since_entry := na

// Visualización de niveles en el gráfico

plot(strategy.position_size > 0 ? trade_stop_price : na, title="Nivel de Stop Activo", color=color.red, style=plot.style_linebr, linewidth=2)

plot(strategy.position_size > 0 ? trade_be_trigger : na, title="Límite Activación BE", color=color.blue, style=plot.style_linebr, linewidth=1)

Implementación 2: Piramidación Controlada, Take Profit Parcial y Circuit Breaker de Drawdown

Este algoritmo implementa una lógica de adición escalada de posiciones (piramidación limitada a 3 entradas) a favor de la tendencia, gestionando la salida con cierres parciales de beneficios y suspendiendo de forma automática la operativa si el drawdown de la cuenta supera el 10%^1^.

Pine Script

//@version=6

strategy("Pyramiding, Scale-Out and Drawdown Breaker", 

         overlay=true, 

         initial_capital=100000, 

         pyramiding=3, 

         default_qty_type=strategy.percent_of_equity, 

         default_qty_value=10, // Cada orden representa un 10% de la equidad

         commission_type=strategy.commission.percent,

         commission_value=0.05,

         margin_long=100,

         margin_short=100)

// Parámetros de Riesgo y Cartera

max_account_drawdown_pct = input.float(10.0, title="Límite Drawdown Cuenta (%)") / 100.0

tp_partial_pct = input.float(50.0, title="Porcentaje de Cierre en TP Parcial (%)")

// Indicadores de Tendencia

long_period = input.int(50, title="SMA Filtro de Tendencia")

sma_trend = ta.sma(close, long_period)

// Variables para el Circuit Breaker de Drawdown de Cuenta

var float max_equity_observed = 0.0

var bool operational_shutdown = false

max_equity_observed := math.max(max_equity_observed, strategy.equity)

current_drawdown_pct = max_equity_observed > 0 ? (max_equity_observed - strategy.equity) / max_equity_observed : 0.0

// Si se supera el límite de drawdown permitido, se cierran las posiciones y se bloquea el sistema

if (current_drawdown_pct >= max_account_drawdown_pct)

    operational_shutdown := true

    strategy.close_all(comment="Circuit Breaker: Límite Drawdown Superado")

    strategy.cancel_all()

// Condiciones de Entrada y Piramidación

bullish_trend = close > sma_trend

pullback_trigger = ta.crossover(ta.rsi(close, 14), 40) and bullish_trend

// Variables de Control para la Gestión de Operaciones

var float baseline_stop_loss = na

var float take_profit_1 = na

var float take_profit_2 = na

if (pullback_trigger and not operational_shutdown)

    // Entrada inicial o piramidación

    entry_id = "Long_" + str.tostring(strategy.opentrades + 1)

    strategy.entry(entry_id, strategy.long)

    // Al realizar la primera entrada, se definen los objetivos

    if (strategy.position_size == 0)

        baseline_stop_loss := ta.lowest(low, 10)

        take_profit_1 := close + (ta.atr(14) * 1.5)

        take_profit_2 := close + (ta.atr(14) * 3.5)

    else

        // Ajuste ascendente del stop loss al promediar posiciones para mitigar riesgos

        baseline_stop_loss := math.max(baseline_stop_loss, ta.lowest(low, 10))

// Ejecución de órdenes de salida parciales y finales

if (strategy.position_size > 0)

    // TP parcial al alcanzar el primer objetivo de ganancias para consolidar beneficios

    strategy.exit("TP_Parcial", qty_percent=tp_partial_pct, limit=take_profit_1, stop=baseline_stop_loss)

    // Salida definitiva del remanente al alcanzar el objetivo final

    strategy.exit("TP_Final", limit=take_profit_2, stop=baseline_stop_loss)

else

    baseline_stop_loss := na

    take_profit_1 := na

    take_profit_2 := na

// Visualización de niveles

plot(strategy.position_size > 0 ? baseline_stop_loss : na, title="Stop Loss General", color=color.red, style=plot.style_linebr)

plot(strategy.position_size > 0 ? take_profit_1 : na, title="Take Profit Parcial", color=color.green, style=plot.style_linebr)

plot(strategy.position_size > 0 ? take_profit_2 : na, title="Take Profit Final", color=color.teal, style=plot.style_linebr)

Implementación 3: Librería de Funciones Reutilizables de Gestión de Riesgo (Library)

Las librerías en Pine Script permiten empaquetar funciones y cálculos complejos para importarlos de forma sencilla en diferentes proyectos^63^. Este módulo reutilizable proporciona las funciones fundamentales para el cálculo dinámico del tamaño de posición, niveles de stop loss basados en ATR, y la monitorización en tiempo real del drawdown del sistema^20^.

Pine Script

//@version=6

// @description Librería profesional de gestión de riesgo y sizing para sistemas cuantitativos

library("RiskManagementSuite", overlay=true)

// @function Calcula el tamaño de posición en contratos/acciones en base al riesgo dinámico.

// @param account_equity Valor actual de la equidad disponible de la cartera.

// @param risk_percent Porcentaje del capital que se desea arriesgar (ej. 1.5).

// @param stop_loss_distance Distancia en precio absoluto entre la entrada y el stop.

// @param contract_point_value Multiplicador por punto del instrumento financiero operado.

// @param lot_step_precision Precisión mínima de volumen permitida por el bróker (ej. 0.01).

// @returns Cantidad de unidades/lotes finales sugerida para abrir la posición.

export calculate_position_size(float account_equity, float risk_percent, float stop_loss_distance, float contract_point_value, float lot_step_precision) =>

    float capital_at_risk = account_equity * (risk_percent / 100.0)

    float calculated_quantity = 0.0

    if (stop_loss_distance > 0)

        raw_quantity = capital_at_risk / (stop_loss_distance * contract_point_value)

        calculated_quantity := math.floor(raw_quantity / lot_step_precision) * lot_step_precision

    calculated_quantity

// @function Determina el nivel de precio stop en base a la volatilidad histórica promedio (ATR).

// @param execution_price Precio promedio o precio de ejecución de la entrada.

// @param atr_val Valor del indicador ATR calculado para el activo.

// @param multiplier Coeficiente multiplicador para ajustar la distancia del stop loss.

// @param is_long_direction Parámetro lógico para indicar si la dirección es de compra (true) o de venta (false).

// @returns Nivel de precio stop absoluto resultante.

export calculate_atr_stop(float execution_price, float atr_val, float multiplier, bool is_long_direction) =>

    float stop_price = na

    if (is_long_direction)

        stop_price := execution_price - (atr_val * multiplier)

    else

        stop_price := execution_price + (atr_val * multiplier)

    stop_price

// @function Evalúa el drawdown en tiempo real de la cartera contra un umbral de seguridad preestablecido.

// @param max_equity_peak Variable persistente con el valor de equidad más alto registrado por la estrategia.

// @param current_equity Valor actual de la equidad disponible de la cartera.

// @param max_drawdown_limit_pct Porcentaje de pérdida acumulada permitido antes del bloqueo (ej. 15.0).

// @returns Tupla con el porcentaje de drawdown actual calculado y una variable booleana de desconexión.

export evaluate_drawdown_control(float max_equity_peak, float current_equity, float max_drawdown_limit_pct) =>

    float current_drawdown = max_equity_peak > 0 ? (max_equity_peak - current_equity) / max_equity_peak : 0.0

    bool trigger_circuit_breaker = current_drawdown >= (max_drawdown_limit_pct / 100.0)

    [current_drawdown, trigger_circuit_breaker]

Fuentes citadas

- Pine Script v5 User Manual (350-509) | PDF | Margin (Finance) | Computing - Scribd, https://www.scribd.com/document/707955802/Pine-Script-v5-User-Manual-350-509
- There seems to be no mention in the docs that strategy.exit can only be used once per script, https://www.reddit.com/r/pinescript/comments/19dzbhl/there_seems_to_be_no_mention_in_the_docs_that/
- Releases · PyneSys/pynecore - GitHub, https://github.com/pynesys/pynecore/releases
- pine script - strategy.exit() not closing position even when stop loss is reached, https://stackoverflow.com/questions/75154330/strategy-exit-not-closing-position-even-when-stop-loss-is-reached
- SL and TP not triggered by strategy,exit function - Stack Overflow, https://stackoverflow.com/questions/78294122/sl-and-tp-not-triggered-by-strategy-exit-function
- Pine Script v5 기본 개념 - 2 (Strategies) - 컴돈AI - 티스토리, https://comdon-ai.tistory.com/100
- Strategies - TradingView, https://www.tradingview.com/pine-script-docs/faq/strategies/
- 4 Pine Script v6 Strategy Changes That Alter Backtests - TradersPost, https://blog.traderspost.io/article/pine-script-v6-strategy-changes
- How exactly does trail_price, trail_offset work in pinescript? - Stack Overflow, https://stackoverflow.com/questions/65839439/how-exactly-does-trail-price-trail-offset-work-in-pinescript
- How do trail_points and trail_offset work with Takeprofit and Stoploss - Stack Overflow, https://stackoverflow.com/questions/73893459/how-do-trail-points-and-trail-offset-work-with-takeprofit-and-stoploss
- strategy.opentrades | PyneCore Documentation, https://pynecore.org/docs/reference/lib/strategy_opentrades/
- Alert condition name or title access in the alert message? : r/TradingView - Reddit, https://www.reddit.com/r/TradingView/comments/1amui6f/alert_condition_name_or_title_access_in_the_alert/
- PineScript is exiting strategy and opening a double sized order on the same bar (sending webhook with double the quantity to the broker) - Stack Overflow, https://stackoverflow.com/questions/78421530/pinescript-is-exiting-strategy-and-opening-a-double-sized-order-on-the-same-bar
- Stop loss automation - ClearEdge Trading, https://clearedge.trading/post/automated-futures-trading-stop-loss-strategies
- Money Management Archives - QUANTITATIVE RESEARCH AND TRADING, http://jonathankinlay.com/tag/money-management/
- Trading Algorítmico: Guía Definitiva - Qué Es, Plataformas y Capital Necesario [2026], https://tradingwyckoff.com/trading-algoritmico/que-es-trading-algoritmico/
- A minimal reference to pine script v5 - GitHub Gist, https://gist.github.com/kdkiss/731e6288e2314a7e6f36383888e5bc40
- How to Convert Pine Script v5 to v6 Without Bugs - TradersPost, https://blog.traderspost.io/article/pine-script-v5-to-v6-migration-guide
- How to force the TradingView strategy-tester to open/exit Long positions only ? (Remove short) + set TP/SL not giving any result - Stack Overflow, https://stackoverflow.com/questions/74717297/how-to-force-the-tradingview-strategy-tester-to-open-exit-long-positions-only
- Best Practices for Managing Risk with Large Lot Sizes - Lopez Tacos, https://lopeztacos.com/en/lifestyle/best-practices-for-managing-risk-with-large-lot-sizes/
- Pine Script (TradingView) - A Step-by-step Guide - AlgoTrading101 Blog, https://algotrading101.com/learn/pine-script-tradingview-guide/
- Chandelier Exit Indicator Script | PDF - Scribd, https://www.scribd.com/document/791414851/Chandelier-Exit
- The best Forex advanced money management techniques - Tradeciety, https://tradeciety.com/advanced-money-management-techniques
- Risk of Ruin | CrossTrade, https://crosstrade.io/learn/risk-management/risk-of-ruin
- Trading Bot in Practice: Overfitting, Risk Management, and What Backtests Don't Tell You, https://petrvojacek.cz/en/blog/trading-bot-risks-and-tools/
- Applying Fixed Fractional Trading Strategy On Your Trading - WeMasterTrade, https://wemastertrade.com/fixed-fractional-trading-strategy/
- Fixed Ratio Trading Explained | PDF | Leverage (Finance) | Profit (Accounting) - Scribd, https://www.scribd.com/document/276600269/Fixed-Ratio
- Fixed Ratio Position Sizing for Trading - Stator AFM, https://www.stator-afm.com/tutorial/fixed-ratio-position-sizing/
- Fixed Ratio Position Sizing: Meaning, Definition And Example - QuantifiedStrategies.com, https://www.quantifiedstrategies.com/fixed-ratio-position-sizing/
- Fixed Ratio Betting in Trading - DayTrading.com, https://www.daytrading.com/fixed-ratio-betting
- What is Kelly criterion betting, and how to use it in crypto trading? - TradingView, https://www.tradingview.com/news/cointelegraph:77c3abbbb094b:0-what-is-kelly-criterion-betting-and-how-to-use-it-in-crypto-trading/
- Kelly Criterion Position Sizing Explained - TradersPost, https://blog.traderspost.io/article/kelly-criterion-position-sizing-automated-trading
- Pine Script Tutorial | How To Develop Real Trading Strategies On TradingView, https://jamesbachini.com/pine-script-tutorial/
- How to simulate trading with leverage in Pine Script - TradingView, https://www.tradingview.com/support/solutions/43000717375-how-to-simulate-trading-with-leverage-in-pine-script/
- Cómo hacer trading simulado con apalancamiento en Pine Script - TradingView, https://es.tradingview.com/support/solutions/43000717375/
- Get the Exact Entry Price in Pine Script - Stack Overflow, https://stackoverflow.com/questions/72624659/get-the-exact-entry-price-in-pine-script
- Pinescript - Pullback strategy - Fixed stoploss, dynamic take profit : r/TradingView - Reddit, https://www.reddit.com/r/TradingView/comments/1hmlpqo/pinescript_pullback_strategy_fixed_stoploss/
- Bollinger Bands Strategy in Pine Script | PDF - Scribd, https://www.scribd.com/document/859737638/Bollinger-Bands-Strategy-directed-20-2-0
- AliHaider0343/CodeLlama-Format · Datasets at Hugging Face, https://huggingface.co/datasets/AliHaider0343/CodeLlama-Format
- pine script - Improve Pinescript Efficiency - Array calculation and plotting? - Stack Overflow, https://stackoverflow.com/questions/76719118/improve-pinescript-efficiency-array-calculation-and-plotting
- A minimal reference to pine script v5 - GitHub Gist, https://gist.github.com/dnavarrom/5b8a36411a8a6fb2a0380d12cfe52673
- pine script - Adjust SL to Entry Price at First TP? - Stack Overflow, https://stackoverflow.com/questions/75839954/adjust-sl-to-entry-price-at-first-tp
- Here's My Strategy : r/TradingView - Reddit, https://www.reddit.com/r/TradingView/comments/1k894ya/heres_my_strategy/
- Sharing My PineScript Strategy Framework for Free – Feedback Welcome! : r/TradingView - Reddit, https://www.reddit.com/r/TradingView/comments/1l8gno1/sharing_my_pinescript_strategy_framework_for_free/
- Master TradingView Pine Script V6 with AI | PDF | Artificial Intelligence - Scribd, https://www.scribd.com/document/973680559/Mastering-TradingView-Pine-Script-V6-With-ChatGPT-and-Claude-AI
- Bitcoin trading strategy - DCA and grid bot setups for BTC, settings + backtest (4h) - Reddit, https://www.reddit.com/r/pinescript/comments/1umbr31/bitcoin_trading_strategy_dca_and_grid_bot_setups/
- Using Pine Script to DCA into SPY | by Sze Zhong LIM | Data And Beyond | Medium, https://medium.com/data-and-beyond/using-pine-script-to-dca-into-spy-73daa875684
- Pine script - check to see how many active trades I'm in - Stack Overflow, https://stackoverflow.com/questions/73582360/pine-script-check-to-see-how-many-active-trades-im-in
- How to Automate Pine Script Strategies with AI? (Pine Script Guide for TradingView Users), https://rangatechnologies.medium.com/how-to-automate-pine-script-strategies-with-ai-pine-script-guide-for-tradingview-users-e47d8e76cdd8
- Backtesting Automated Futures Strategies - ClearEdge Trading, https://clearedge.trading/post/backtesting-automated-futures-strategies-guide
- FMZ PINE Script Doc - 发明者量化, https://www.fmz.com/bbs-topic/9293
- Release notes - TradingView, https://www.tradingview.com/pine-script-docs/v5/release-notes/
- Best Algorithmic Trading Software: Top Picks for 2026 - Quantt, https://www.quantt.co.uk/resources/best-algorithmic-trading-software
- Pine Script / MQL5: Should Traders Master Both for Chart Analysis and Algorithmic Trading?, https://medium.com/@msn.asg/pine-script-mql5-should-traders-master-both-for-chart-analysis-and-algorithmic-trading-d09b339a5aa5
- Practical Beginner's Guide to MQL5 Programming - Forex VPS Hosting, https://www.vpsforextrader.com/blog/beginners-guide-to-mql5/
- MQL5 vs. Pine Script: which one should you learn? - Elite CurrenSea, https://elitecurrensea.com/education/mql5-vs-pine-script-which-one-should-you-learn
- 16 AI Trading Tools That Beat 99% of Traders - Gadget Review, https://www.gadgetreview.com/ai-trading-tools-that-beat-99-traders
- Concepts / Strategies - TradingView, https://www.tradingview.com/pine-script-docs/concepts/strategies/
- Built a free all-in-one trend + breakout indicator in Pine Script v6 — MTF bias table, auto SL/TP, and a 0-100 setup score : r/TradingView - Reddit, https://www.reddit.com/r/TradingView/comments/1rz9nve/built_a_free_allinone_trend_breakout_indicator_in/