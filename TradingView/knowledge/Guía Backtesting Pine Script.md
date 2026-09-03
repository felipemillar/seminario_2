Manual de Ingeniería Cuantitativa: Estrategias Avanzadas de Trading y Modelado de Backtesting en Pine Script v6

1. La Declaración de la Estrategia y Parámetros Globales de Simulación

El desarrollo de sistemas de trading algorítmico en la plataforma TradingView exige una comprensión rigurosa del motor de ejecución que simula las órdenes^1^. Esta configuración inicial se define mediante la función de declaración obligatoria strategy(), la cual establece los parámetros de capital, apalancamiento, comisiones y reglas de ejecución para todo el ciclo de backtesting y posterior ejecución en tiempo real^1^.

La parametrización de la función strategy() determina la precisión matemática de la simulación y su correspondencia con las condiciones reales del mercado^3^. Cada parámetro de esta función influye de manera directa en el cálculo de la curva de equidad y en la validez estadística del informe de rendimiento^2^.

Pine Script

strategy(

     title="Estrategia de Ejemplo", 

     shorttitle="Ejemplo", 

     overlay=true, 

     initial_capital=100000, 

     currency=currency.USD, 

     default_qty_type=strategy.percent_of_equity, 

     default_qty_value=10, 

     commission_type=strategy.commission.percent, 

     commission_value=0.075, 

     slippage=2, 

     margin_long=100.0, 

     margin_short=100.0, 

     pyramiding=0, 

     calc_on_order_fills=false, 

     calc_on_every_tick=false, 

     process_orders_on_close=true, 

     close_entries_rule="ANY", 

     max_bars_back=5000, 

     risk_free_rate=2.0

 )

- **title y shorttitle (const string):** Definen el nombre completo y la abreviatura del script que se mostrarán en la interfaz del gráfico y en el panel del simulador^3^. Si la cadena de caracteres del título principal supera los límites recomendados, el compilador emitirá una advertencia, sugiriendo el uso de la versión abreviada para mantener la legibilidad^5^.
- **overlay (const bool):** Determina la ubicación de los elementos visuales del script^3^. Si se establece en true, los plots, formas e indicadores se dibujarán directamente sobre el gráfico de precios principal^1^. Si se configura en false, se reservará un panel inferior independiente para las representaciones de la estrategia^3^.
- **initial_capital (const float):** Establece el saldo monetario de partida de la cuenta de trading simulada^3^. Este valor funciona como la base sobre la cual se acumulan los rendimientos netos y las pérdidas flotantes, influyendo de manera directa en el cálculo de las reducciones de capital y en el dimensionamiento porcentual de las posiciones^1^.
- **currency (const string):** Especifica la divisa base del capital de la cuenta (p. ej., currency.USD, currency.EUR)^3^. Facilita la conversión automática de comisiones, pérdidas y ganancias cuando el activo bajo análisis cotiza en una moneda diferente a la cuenta base.
- **default_qty_type (const string):** Determina cómo calcular el tamaño por defecto de las órdenes cuando el script no lo indica de forma explícita en las llamadas de entrada^4^. Soporta tres constantes del sistema: strategy.fixed para negociar un número de contratos o lotes fijos, strategy.cash para transaccionar un monto nominal específico en la divisa de la cuenta, y strategy.percent_of_equity para ajustar dinámicamente el tamaño de la posición a un porcentaje del capital líquido total disponible al momento de emitirse la señal^4^.
- **default_qty_value (const float):** Representa el valor numérico que se asociará a la modalidad elegida en default_qty_type (p. ej., número de contratos, cantidad monetaria o porcentaje de capital disponible)^4^.
- **commission_type (const string):** Define la estructura de cobro para las tarifas de intermediación financiera^4^. Soporta tres variantes: strategy.commission.percent (un porcentaje del volumen nominal transaccionado), strategy.commission.cash_per_contract (un cobro plano por cada contrato o lote negociado) y strategy.commission.cash_per_order (una tasa plana por cada orden ejecutada)^4^.
- **commission_value (const float):** Es el valor numérico aplicado a la modalidad de comisión configurada^4^. Por ejemplo, en una cuenta con comisión del  sobre el volumen nominal de cada operación de entrada y de salida, se configuraría como 0.075 bajo la modalidad de porcentaje^4^.
- **slippage (const int):** Especifica la desviación desfavorable en el precio de ejecución para órdenes de mercado o de parada (*stop*), expresada en ticks mínimos de precio (syminfo.mintick)^4^. Este parámetro modela las ineficiencias de liquidez, la diferencia entre bid/ask (*spread*) y la latencia del mercado en el momento de la ejecución^4^.
- **margin_long y margin_short (const float):** Determinan el porcentaje de margen financiero requerido para abrir y mantener posiciones largas y cortas, respectivamente^1^. Un valor de 100.0 indica que no hay apalancamiento, exigiendo el capital total para respaldar el volumen nominal de la posición^1^. Valores inferiores a 100 permiten simular cuentas apalancadas, controlando el punto de llamada de margen y posterior liquidación forzosa si la pérdida flotante excede el capital disponible^10^.
- **pyramiding (const int):** Establece el número máximo de órdenes de entrada consecutivas permitidas en una misma dirección antes de que ocurra una orden de salida^4^. Si se configura en 0, se prohíbe la acumulación de posiciones (*scaling-in*), ignorando señales adicionales de entrada en la dirección del trade activo^4^.
- **calc_on_order_fills (const bool):** Determina si el motor de la estrategia debe recalcular la lógica completa del código de manera inmediata tras el llenado de una orden dentro de una barra^8^. Habilitar este parámetro permite actualizar los stops de protección y la toma de ganancias inmediatamente después de abrir una posición, sin esperar al cierre de la vela actual^9^.
- **calc_on_every_tick (const bool):** Fuerza la ejecución del código en cada cotización o variación de precio en tiempo real^9^. Aunque es útil en condiciones operativas en vivo, no afecta al procesamiento de las barras históricas, las cuales siempre se simulan utilizando sus precios consolidados de apertura, máximo, mínimo y cierre (OHLC)^16^.
- **process_orders_on_close (const bool):** Modifica el comportamiento temporal de la ejecución de órdenes^4^. Cuando se establece en true, el emulador realiza un intento adicional de procesar y llenar las órdenes en el cierre de la vela en la que se generó la señal, en lugar de posponer la transacción para la apertura de la barra siguiente^4^.
- **close_entries_rule (const string):** Configura la prioridad y secuencia de emparejamiento entre las órdenes de entrada y de salida^4^. Su valor por defecto es "FIFO" (First-In, First-Out; obligatorio bajo regulaciones en ciertos mercados de divisas y valores)^13^. Si se configura en "ANY", se permite que las órdenes de salida se vinculen a entradas específicas usando identificadores únicos^13^.
- **max_bars_back (const int):** Define la capacidad de almacenamiento de datos históricos para variables y series de tiempo^3^. Esto evita errores de desbordamiento en operaciones indexadas mediante el operador [] en conjuntos de datos muy densos o extensos^20^.
- **risk_free_rate (const float):** Es la tasa de rendimiento libre de riesgo anual utilizada por el simulador para descontar la volatilidad del portafolio en el cálculo de métricas financieras como los coeficientes de Sharpe y Sortino^21^. Su valor por defecto se establece en un  anual^21^.

2. El Motor de Transacciones: Funciones de Entrada y Gestión de Órdenes

El motor de trading de TradingView opera como un sistema basado en eventos a través de un intermediario simulado (*broker emulator*)^1^. Para interactuar con este motor, Pine Script ofrece funciones dedicadas a la colocación, modificación y cancelación de órdenes de compra y venta^1^.

La Diferencia Operativa entre strategy.entry y strategy.order

En Pine Script existe una distinción técnica fundamental entre iniciar una operación y colocar una orden^1^. Comprender este comportamiento evita errores en la gestión de las posiciones^1^.

- **strategy.entry():** Es una función diseñada para la apertura de posiciones o para el escalamiento de las mismas bajo reglas de piramidación^13^. Esta función cuenta con un mecanismo integrado de reversión automática de posición^1^. Si existe una posición corta activa de 10 lotes y se procesa un comando strategy.entry() de compra larga por un tamaño equivalente, el emulador liquidará automáticamente la posición corta y abrirá una posición larga en un único paso de ejecución^1^.
- **strategy.order():** Es una instrucción de colocación de orden pura^4^. Ignora el estado de la posición actual del portafolio y los límites de piramidación^4^. Si se ejecuta una orden contraria a una posición abierta, esta se reduce en tamaño, pero el comando nunca revertirá la dirección de la posición de forma automática^4^. Su uso principal se limita a la colocación de órdenes pendientes o ajustes puntuales en el volumen de negociación.

Parámetros de strategy.entry

Pine Script

strategy.entry(id, direction, qty, limit, stop, oca_name, oca_type, comment, alert_message, disable_alert)

- **id (series string):** Identificador alfanumérico único para cada orden individual^11^. Este identificador vincula de manera explícita órdenes de cierre o límites de protección de riesgo^11^.
- **direction (const MarketPosition):** Determina si la orden es alcista (strategy.long) o bajista (strategy.short)^27^.
- **qty (series float):** Número de unidades, acciones o contratos a negociar. Si se omite o se establece como na, el emulador calculará la cantidad de forma automática utilizando las propiedades globales definidas en la declaración strategy()^10^.
- **limit (series float):** Precio umbral para una orden limitada. La ejecución solo se realizará a ese precio o a un nivel más favorable para la estrategia^1^.
- **stop (series float):** Precio gatillo para una orden stop. La orden permanecerá inactiva hasta que el precio de mercado cruce el nivel especificado, momento en el cual se activará como una orden de mercado para entrar en breakouts o mitigar pérdidas^1^.
- **oca_name (series string):** Nombre identificador para agrupar varias órdenes dentro de una estructura *One-Cancels-All*^25^.
- **oca_type (const string):** Determina el comportamiento de cancelación del grupo OCA^29^. Soporta la constante strategy.oca.cancel (donde el llenado completo de una orden cancela las demás del grupo) y strategy.oca.reduce (donde el llenado de una porción de una orden reduce proporcionalmente el tamaño de las restantes)^29^.
- **comment (series string):** Cadena de texto descriptivo que se mostrará junto a las flechas de ejecución en el gráfico y en el historial del simulador^25^.
- **alert_message (series string):** Mensaje que sustituye el texto de alerta estándar cuando la orden se ejecuta^25^. Es una herramienta útil para enviar estructuras JSON dinámicas a webhooks conectados con brókeres o sistemas de ejecución reales^31^.
- **disable_alert (series bool):** Permite silenciar alertas específicas de esta orden para evitar envíos duplicados o innecesarios.

Funciones de Control del Portafolio

Para regular el estado general del portafolio, Pine Script proporciona funciones dedicadas a la liquidación y cancelación de órdenes^24^:

Pine Script

// Liquidación de trades específicos o globales

strategy.close(id, comment, qty, qty_percent, alert_message, immediately)

strategy.close_all(comment, alert_message, immediately)

// Cancelación de órdenes pendientes no ejecutadas

strategy.cancel(id)

strategy.cancel_all()

- **strategy.close():** Busca liquidar una posición o una orden específica identificada mediante su id de entrada utilizando una orden de mercado^25^. Permite liquidaciones parciales a través del parámetro qty (para especificar unidades exactas) o qty_percent (especificando un valor porcentual de  a )^25^. El parámetro immediately (booleano) fuerza al motor de ejecución a cerrar el trade en el precio actual del cálculo sin esperar a la apertura de la siguiente vela^29^.
- **strategy.close_all():** Envía órdenes de mercado inmediatas para liquidar cualquier posición abierta en la cuenta, independientemente de su sentido o de su identificador^1^.
- **strategy.cancel():** Desactiva de forma específica cualquier orden pendiente de ejecución (órdenes stop o limitadas) que coincida con el identificador id especificado^24^. No tiene efecto sobre posiciones que ya han sido abiertas.
- **strategy.cancel_all():** Elimina de forma masiva todas las órdenes de entrada o salida que se encuentren en estado pendiente en el emulador^24^.

3. Funciones de Salida y Protección

La gestión cuantitativa del riesgo requiere herramientas avanzadas para la colocación de stops de protección, objetivos de toma de ganancias y cierres dinámicos^29^. Para este fin, la función principal es strategy.exit()^25^.

Estructura de Parámetros de strategy.exit

Pine Script

strategy.exit(id, from_entry, qty, qty_percent, profit, loss, limit, stop, trail_price, trail_points, trail_offset, comment, alert_message)

La función strategy.exit() permite colocar simultáneamente objetivos de toma de ganancias y stops de protección dentro de una sola llamada^26^. Al ser administrados internamente por el emulador del bróker en un grupo OCA implícito, el llenado de uno de los extremos anula automáticamente el otro^29^.

- **id (series string):** Identificador exclusivo de la orden de salida^25^.
- **from_entry (series string):** Indica el identificador del trade de entrada específico que se desea liquidar^13^. Si se omite, el sistema aplicará la liquidación por defecto siguiendo las reglas FIFO definidas en la declaración strategy()^13^.
- **qty o qty_percent (series float):** Determinan la escala de liquidación para salidas parciales^25^. Permiten definir la cantidad de unidades o la proporción porcentual de la posición a cerrar^25^.
- **profit y loss (series int):** Representan el objetivo de ganancia y la detención de pérdida en ticks relativos calculados a partir del precio de entrada de la posición (syminfo.mintick)^25^.
- **limit y stop (series float):** Permiten establecer niveles de precio absolutos en el gráfico donde se colocará la orden limitada de toma de ganancias (limit) o de parada de pérdidas (stop)^11^.

Funcionamiento Detallado del Trailing Stop

El trailing stop es un stop de protección dinámico que acompaña al precio a favor de la tendencia, pero mantiene su posición si el mercado se mueve en contra^29^. Se configura a través de tres parámetros^25^:

- **Activación:** Se puede establecer mediante un precio absoluto en el gráfico con trail_price o especificando una distancia relativa en ticks desde el precio de entrada mediante trail_points^25^.
- **Distancia de Seguimiento:** Se define a través de trail_offset, expresado en ticks de precio^25^.

Evolución de un Trailing Stop en una posición larga:

1. El precio sube y alcanza el nivel definido en "trail_price" o "trail_points". El trailing stop se activa.

2. El stop dinámico se coloca a una distancia fija por debajo del precio máximo alcanzado, definida por "trail_offset" [cite: 34, 36].

3. Con cada nuevo máximo que registre el precio, el stop de protección se desplaza hacia arriba manteniendo la distancia de "trail_offset" [cite: 34].

4. Si el precio retrocede y cruza el nivel de stop dinámico actualizado, la posición se liquida mediante una orden de mercado [cite: 36].

En Pine Script v6, los parámetros absolutos y relativos se evalúan de forma simultánea^11^. Si se especifican de manera conjunta (p. ej., un stop absoluto con stop y un stop relativo basado en ticks con loss), el motor ejecutará la salida utilizando el nivel que se active primero en el mercado^11^.

Gestión de Múltiples Objetivos (Salidas Parciales / Scaled Exits)

Las salidas escalonadas permiten tomar ganancias de forma parcial a medida que el precio se mueve a favor de la tendencia, reduciendo el riesgo de la posición^29^. Para implementarlas en Pine Script v6 de forma segura, se deben realizar múltiples llamadas de strategy.exit() especificando el porcentaje o cantidad exacta de contratos a cerrar en cada nivel^29^.

Pine Script

// Ejemplo de entradas y salidas parciales en Pine Script v6

if (crossover_condition)

    strategy.entry("Largo", strategy.long, qty=10)

if (strategy.position_size > 0)

    // Se liquida el 50% de la posición en el primer objetivo limitado (TP1)

    strategy.exit("TP1", from_entry="Breakout", qty_percent=50, limit=precio_tp1, stop=precio_sl)

    // Se liquida el 100% de la posición restante en el segundo objetivo (TP2)

    strategy.exit("TP2", from_entry="Breakout", qty_percent=100, limit=precio_tp2, stop=precio_sl)

Al utilizar qty_percent, el porcentaje especificado se aplica sobre la posición activa restante en el momento en que se evalúa la orden, no sobre el tamaño inicial^29^. Configurar un qty_percent=100 en la última llamada garantiza el cierre completo de los contratos remanentes en el mercado.

4. Modelo de Ejecución de Órdenes y Mecánica de Barras

El procesamiento de estrategias en TradingView sigue un flujo secuencial regulado por un motor de ejecución basado en eventos^37^. La forma en que se calculan las variables y se simula el llenado de las órdenes depende del tipo de barra (histórica o en tiempo real) y de las propiedades de cálculo configuradas en el script^37^.

Procesamiento Barra a Barra

En el historial del gráfico (barras cerradas), el código de la estrategia se calcula una única vez por cada vela, utilizando los valores consolidados de apertura, máximo, mínimo y cierre (OHLC)^15^. El motor opera bajo el siguiente ciclo secuencial^37^:

- Se actualizan las variables integradas del mercado correspondientes a la barra actual (open, high, low, close, volume)^37^.
- Se ejecuta el código de la estrategia desde la primera hasta la última línea del script^37^.
- Si se cumplen las condiciones lógicas, el script genera órdenes de entrada o salida virtuales^1^.
- Dado que la barra ya está cerrada y no es posible operar hacia el pasado, el simulador retiene estas órdenes y planifica su ejecución para la apertura de la barra siguiente por defecto^1^.

Modificaciones de Flujo: calc_on_order_fills, calc_on_every_tick y process_orders_on_close

El comportamiento estándar del motor de ejecución puede modificarse mediante parámetros en la declaración de la estrategia^4^:

calc_on_order_fills

Cuando se establece en true, el emulador no espera al cierre de la vela para recalcular la estrategia^9^. Si una orden stop o limitada se llena a mitad de la vela, el script se ejecuta inmediatamente tras el llenado^14^. Esto permite ajustar dinámicamente los stops o colocar órdenes de toma de ganancias sin experimentar el retraso de una barra^9^.

En barras históricas, la re-ejecución simulada bajo calc_on_order_fills utiliza un proceso de rollback^14^. Las variables declaradas con la palabra clave var conservan su valor al inicio de la barra y se restablecen antes de cada recalculación intra-vela para mantener la consistencia histórica^14^. En cambio, las variables declaradas con varip (*var intra-period*) conservan sus cambios de estado acumulados en cada ejecución dentro de la misma vela, sin sufrir rollback^14^.

calc_on_every_tick

Habilita el recálculo de la estrategia en cada cambio de precio (tick) durante la formación de las velas en tiempo real^9^. Su impacto operativo principal es el riesgo de repintado y la discrepancia entre el backtesting e trading en vivo^3^: en tiempo real, una orden puede ejecutarse a mitad de una vela si se cumple una condición temporal, mientras que en el historial el sistema solo evaluará la condición en base al cierre definitivo de la vela completa^1^.

process_orders_on_close

Fuerza un intento adicional de ejecución al cierre de la vela en la que se generó la señal^4^. Esto evita el desfase de un periodo entre la señal y la ejecución de mercado^4^. No obstante, en vivo puede ser difícil de replicar con exactitud debido al deslizamiento y la latencia en las subastas de cierre de mercado^4^.

Prioridad de Ejecución de Órdenes

Cuando se generan múltiples señales operativas que deben evaluarse simultáneamente en la misma barra, el emulador de TradingView sigue un protocolo estricto de prioridad de llenado:

- **Órdenes de Mercado:** Se priorizan para ejecutarse en la apertura de la barra siguiente al precio open (o en el cierre de la barra actual si está activado process_orders_on_close)^1^.
- **Órdenes de Stop-Loss:** Se evalúan antes que las órdenes limitadas de toma de ganancias si el emulador determina que el movimiento de precios cruzó primero el nivel de pérdida, evitando simulaciones excesivamente optimistas^14^.
- **Órdenes Stop de Entrada / Breakout y Órdenes Limitadas:** Se procesan a continuación^1^. El orden de llenado dentro del rango diario depende de si se asume un recorrido alcista o bajista (heurística OHLC) o si se utiliza la lupa de barras para validar la secuencia de ticks^12^.

5. Variables de Estado de Estrategia en Tiempo de Ejecución

El seguimiento de las métricas financieras de la cuenta simulada y de las posiciones activas se gestiona a través de variables de estado incorporadas en el sistema de TradingView^27^:

- **strategy.position_size:** Devuelve el tamaño cuantitativo de la posición actual del portafolio. Si el valor es un número flotante positivo (), la estrategia se encuentra en una posición larga^27^. Si el valor es negativo (), la estrategia se encuentra en una posición corta^27^. Si es equivalente a , el portafolio está en estado neutro o líquido (*flat*)^27^.
- **strategy.position_avg_price:** Devuelve el precio promedio ponderado de entrada de la posición activa en el mercado^26^. Si la posición está cerrada (líquida), esta variable devuelve el valor na.
- **strategy.equity:** Representa el capital líquido total disponible de la cuenta simulada en tiempo real^22^. Se calcula de forma dinámica en cada vela aplicando la siguiente ecuación^22^:
- **strategy.initial_capital:** Devuelve la cantidad fija definida originalmente en el parámetro de capital inicial dentro de la declaración strategy()^3^.
- **strategy.openprofit:** El beneficio o pérdida flotante no realizado de la posición abierta actual en la moneda base de la cuenta^28^.
- **strategy.netprofit:** El beneficio neto consolidado acumulado de todas las transacciones históricas cerradas^10^. Se calcula restando las pérdidas brutas y las comisiones totales de las ganancias brutas realizadas.
- **strategy.grossprofit:** El valor acumulado total en la moneda base de todas las transacciones históricas individuales que resultaron en una ganancia neta.
- **strategy.grossloss:** El valor acumulado total en pérdidas de todas las operaciones cerradas que resultaron negativas.
- **strategy.wintrades:** Contador de trades históricos cerrados que generaron beneficios netos.
- **strategy.losstrades:** Contador de trades históricos cerrados que generaron pérdidas netas.
- **strategy.eventtrades:** Contador de operaciones que cerraron exactamente en el precio de equilibrio (punto de breakeven, beneficio neto de cero).

6. Auditoría y Extracción de Datos Históricos de Operaciones

La capacidad de analizar los resultados históricos de forma detallada es fundamental para optimizar los algoritmos y mitigar riesgos. Pine Script v6 ofrece funciones integradas en los espacios de nombres strategy.closedtrades.* y strategy.opentrades.* para auditar el rendimiento comercial de manera programática^28^.

Atributos Clave de Operaciones Cerradas y Abiertas

Las funciones de acceso al historial de trades cerrados se indexan en un formato de lista de base cero, donde el índice 0 representa la operación más antigua registrada y strategy.closedtrades.size() - 1 representa la transacción cerrada más reciente^27^:

Closed Trades Array:

[Trade 0] ---> [Trade 1] ---> ... ---> [Trade N-1 (Último Trade Cerrado)]

| **Función de strategy.closedtrades.*** | **Tipo de Retorno** | **Descripción Específica** |
| --- | --- | --- |
| .entry_price(trade_num) | float | Precio promedio de entrada del trade especificado^28^. |
| .exit_price(trade_num) | float | Precio promedio al que se liquidó y cerró el trade^28^. |
| .entry_bar_index(trade_num) | int | Índice de la barra de gráfico donde se abrió la posición^28^. |
| .exit_bar_index(trade_num) | int | Índice de la barra de gráfico donde se cerró la posición^28^. |
| .entry_time(trade_num) | int | Marca de tiempo UNIX (milisegundos) de la entrada^28^. |
| .exit_time(trade_num) | int | Marca de tiempo UNIX (milisegundos) de la salida^28^. |
| .size(trade_num) | float | Tamaño nominal en unidades (positivo: largo, negativo: corto)^28^. |
| .profit(trade_num) | float | Resultado financiero neto de la operación (comisión deducida)^28^. |
| .commission(trade_num) | float | Costo de comisiones totales pagadas en la entrada y salida^28^. |
| .max_runup(trade_num) | float | Máxima ganancia flotante alcanzada durante la operación^28^. |
| .max_drawdown(trade_num) | float | Máxima pérdida flotante sufrida durante la operación^28^. |

El espacio de nombres strategy.opentrades.* ofrece exactamente la misma estructura de funciones para examinar el estado de las transacciones que componen la posición activa actual en el mercado^27^.

El Límite de Órdenes y el Concepto de Trade Trimming en v6

En Pine Script v6, las simulaciones históricas estándar tienen un límite estricto de 9,000 órdenes totales en sus resultados^11^. Cuando una estrategia de alta frecuencia o con un historial muy extenso supera esta cantidad, el motor del backtester aplica un proceso de recorte automático (*trade trimming*)^11^. Las órdenes más antiguas se eliminan del historial de transacciones conservando solo los registros de las operaciones más recientes para optimizar el rendimiento del servidor^11^.

Si el código intenta acceder a los datos de una operación recortada usando un índice fijo (como el índice 0), el sistema devolverá un valor nulo (na), lo que podría provocar errores de cálculo en la estrategia^11^. Para mitigar este problema, Pine Script v6 introduce la variable integrada strategy.closedtrades.first_index^11^. Esta variable devuelve el índice de la transacción más antigua disponible en la memoria del sistema^11^. Si la estrategia no ha sufrido recortes de órdenes, su valor inicial será 0.

Algoritmo de Iteración Segura sobre Trades Cerrados

Para recorrer el historial de operaciones de forma segura sin generar excepciones por órdenes recortadas, se debe estructurar un bucle for utilizando la variable first_index como límite inferior^11^:

Pine Script

// Estructura de código segura para auditar el historial de operaciones cerradas

int primer_indice = strategy.closedtrades.first_index

int total_operaciones = strategy.closedtrades.size()

float suma_ganancias_maximas = 0.0

if total_operaciones > primer_indice

    for i = primer_indice to total_operaciones - 1

        float beneficio_trade = strategy.closedtrades.profit(i)

        float max_excursion_alcista = strategy.closedtrades.max_runup(i)

        suma_ganancias_maximas := suma_ganancias_maximas + max_excursion_alcista

7. Análisis Holístico del Strategy Tester de TradingView

La interfaz del Strategy Tester en TradingView se divide en pestañas diseñadas para desglosar el rendimiento y la viabilidad comercial de la estrategia simulada^1^.

El Tablero de Diagnóstico Cuantitativo

El simulador organiza las métricas clave de rendimiento en tres pestañas principales^1^:

| **Pestaña del Strategy Tester** | **Métricas Principales Mostradas** | **Visualizaciones y Gráficos Asociados** |
| --- | --- | --- |
| **Overview (Información General)** | Beneficio Neto (Net Profit), Retorno de Comprar y Mantener (Buy & Hold Return), Operaciones Cerradas Totales, Porcentaje de Operaciones Ganadoras (Percent Profitable)^1^. | Curva de Equidad Absoluta/Porcentual, Gráfico de Columnas de Reducción Máxima (Drawdown)^1^. |
| **Performance Summary (Resumen de Rendimiento)** | Ganancia/Pérdida Bruta, Factor de Ganancia (Profit Factor), Ratios de Sharpe y Sortino, Operación Ganadora/Perdedora Mayor, Promedio de Barras en Operación^40^. | Tablas de Métricas consolidadas en categorías (All, Long, Short), Comparación de Rendimientos de Lotes de Activos^40^. |
| **List of Trades (Lista de Operaciones)** | Identificador de Operación, Tipo de Símbolo (Long/Short), Precio de Entrada/Salida, Fecha y Hora Exacta de Transacción, Contratos, Beneficio y Pérdida por Trade^1^. | Botón de Desplazamiento a Barra de Gráfico de Entrada/Salida, Herramienta de Exportación de Datos a CSV^1^. |

Curva de Equidad (***Equity Curve***) y Gráfico de Pérdidas (***Drawdown Chart***)

- **Curva de Equidad:** Representa gráficamente la evolución del saldo neto de la cuenta a lo largo del tiempo, recalculándose con cada operación cerrada^2^. La línea de referencia compara el rendimiento acumulado de la estrategia frente a una estrategia pasiva de compra y mantenimiento (*Buy & Hold*) del mismo activo^1^.
- **Gráfico de Pérdidas:** Visualiza la fluctuación de pérdidas y reducciones de capital sufridas por la cuenta simulada en relación con su pico de beneficio máximo histórico anterior (*highwater mark*)^2^. Permite identificar periodos de pérdidas y evaluar la tolerancia del portafolio en situaciones desfavorables de mercado^40^.

8. Deep Backtesting: Simulación Avanzada sobre Historial Profundo

El entorno de simulación estándar de TradingView está limitado por la capacidad máxima de almacenamiento de velas en los servidores interactivos del gráfico principal (que varía según el tipo de suscripción del usuario entre 5,000 y 40,000 barras históricas)^44^. Esta restricción dificulta el análisis a largo plazo cuando se utilizan marcos temporales cortos^44^.

Mecanismos de Operación e Integración de Datos

El motor de **Deep Backtesting** es un módulo de computación independiente desarrollado para mitigar estas limitaciones de datos^44^. Cuando se activa el modo de Deep Backtesting, el motor realiza las siguientes tareas^47^:

- Permite configurar un periodo histórico específico utilizando filtros de fecha y hora^47^.
- Recupera datos de precios archivados en servidores de almacenamiento históricos de alta capacidad, superando el límite estándar de velas^44^.
- Calcula de forma secuencial la lógica de la estrategia en servidores remotos e independientes del navegador del usuario^47^.
- Si está activada la opción de lupa de barras (*Bar Magnifier*), el sistema recupera automáticamente datos de un marco temporal inferior para simular con mayor precisión los movimientos de precios dentro de las velas principales^12^.

Diferencias Clave y Limitaciones Técnicas

- **Falta de Renderizado Gráfico Completo:** El informe generado por Deep Backtesting es un cálculo puramente computacional^47^. Las operaciones resultantes de la simulación profunda se muestran únicamente en el panel de resultados, pero no se dibujan en las velas del gráfico interactivo convencional^47^. El gráfico interactivo continúa mostrando únicamente las señales correspondientes al backtesting estándar^47^.
- **Límites de Consulta de Datos de Lupa de Barras:** Aunque se cuente con un plan avanzado de datos, el volumen máximo de consultas para reconstruir detalles de marcos temporales inferiores está regulado por restricciones del sistema (hasta un límite de 200,000 velas secundarias consecutivas)^12^.
- **Alineación Temporal de Datos:** En el modo Deep Backtesting, si el script realiza solicitudes complejas de datos mediante funciones como request.security(), las consultas deben estar estrictamente alineadas para evitar sesgos de anticipación (*look-ahead bias*)^3^.

9. Análisis Algorítmico de Métricas Cuantitativas de Rendimiento

La optimización de un sistema de trading requiere comprender las métricas matemáticas que determinan su perfil de riesgo y retorno^40^.

Beneficio Neto, Beneficio Bruto y Pérdida Bruta

- **Beneficio Neto (Net Profit):** Representa el rendimiento acumulado neto del capital de la cuenta tras descontar todas las pérdidas operativas y comisiones pagadas^6^.
Donde  es el beneficio neto,  es el beneficio bruto,  es la pérdida bruta y  representa el acumulado de comisiones transaccionales.
- **Beneficio Bruto (Gross Profit):** Suma absoluta de los rendimientos netos de todas las operaciones históricas cerradas con resultado positivo^41^.
- **Pérdida Bruta (Gross Loss):** Suma absoluta de las pérdidas netas de todas las operaciones históricas cerradas con resultado negativo.

Máxima Reducción (***Maximum Drawdown***)

Representa la mayor pérdida retrospectiva acumulada, medida desde el pico más alto alcanzado por la curva de equidad hasta el valle más bajo antes de registrar un nuevo máximo histórico^40^. Se expresa tanto en términos absolutos de divisa como en porcentaje relativo al valor de equidad en el momento del pico^40^.

Coeficiente de Sharpe (***Sharpe Ratio***)

Mide la recompensa de la estrategia por unidad de volatilidad total, evaluando si el rendimiento promedio del portafolio justifica el riesgo asumido^22^. Un ratio superior a  suele considerarse aceptable en modelos minoristas, mientras que valores por encima de  indican una curva de equidad consistente^23^.

Donde  es el retorno mensual promedio,  es la tasa anual libre de riesgo mensualizada y  es la desviación estándar de los retornos históricos mensuales de la estrategia^22^.

Coeficiente de Sortino (***Sortino Ratio***)

Modifica la fórmula del ratio de Sharpe utilizando únicamente la desviación estándar de los retornos negativos (volatilidad a la baja, )^21^. Esto evita penalizar la volatilidad al alza, proporcionando una métrica de riesgo más adecuada para sistemas de trading con retornos asimétricos positivos^21^.

Factor de Ganancia (***Profit Factor***)

Establece la relación de eficiencia entre el capital ganado y el capital perdido^41^. Un factor de ganancia de 1.5 indica que el algoritmo gana $1.50 por cada dólar que pierde^41^. Un valor superior a 1.5 es un indicador de robustez en sistemas cuantitativos^41^.

Porcentaje de Aciertos y Ratio de Ganancia/Pérdida (Win Rate & Win/Loss Ratio)

- **Porcentaje de Aciertos (Win Rate):** Determina la tasa porcentual de operaciones históricas exitosas en relación al número total de operaciones cerradas^40^.
- **Ratio de Ganancia/Pérdida (Win/Loss Ratio):** Relación de escala promedio entre las operaciones ganadoras y las perdedoras. Un porcentaje de aciertos bajo puede ser viable si el ratio de ganancia/pérdida es proporcionalmente alto^41^.

Otras Métricas Operativas

- **Operación Ganadora/Perdedora Mayor:** Registra el impacto de eventos atípicos en la cartera de trading.
- **Promedio de Barras en Operación:** Mide el costo de oportunidad temporal del capital invertido.
- **Rachas Máximas de Ganancias/Pérdidas Consecutivas:** Ayuda a comprender el comportamiento de las rachas de pérdidas y a definir la tolerancia psicológica requerida para operar el sistema^40^.

10. Limitaciones del Backtester

El backtesting es un modelo de aproximación de la realidad de mercado^40^. El motor de TradingView presenta características de diseño que, si no se parametrizan correctamente, pueden generar resultados excesivamente optimistas que no coinciden con la ejecución en tiempo real^6^.

El Sesgo del Recorrido de los Precios (Intra-bar Assumption)

Al simular operaciones sobre barras de datos históricas normales, el emulador no conoce los movimientos de ticks que ocurrieron dentro de la vela^6^. Por defecto, el sistema aplica una heurística direccional: asume de manera predictiva que el precio se movió desde el valor de apertura (open) hacia el extremo más cercano, luego hacia el extremo opuesto y finalmente al cierre (close)^12^.

OHLC Vela de Gran Rango (Supuestos de Movimiento sin Lupa de Barras):

Apertura (100) ---> Máximo (112) ---> Mínimo (88) ---> Cierre (100)

(Si el sistema asume que el máximo ocurrió primero, se llenará el Take Profit a 110,

ignorando que el mercado pudo caer primero a 88 y activar el Stop Loss).

Si la estrategia utiliza órdenes bracket donde tanto el Stop-Loss como el Take-Profit se encuentran dentro del rango de una misma vela, la heurística tiene un 50% de probabilidad de cometer un error en la secuencia de llenado^14^. Esto puede inflar artificialmente el factor de ganancia de la estrategia^14^.

Para solucionar esta desviación, se debe activar la opción de **Lupa de Barras** (use_bar_magnifier = true en la declaración strategy())^7^. Este parámetro obliga al emulador a validar la secuencia temporal de precios consultando marcos temporales inferiores, logrando resultados más realistas^12^.

El Sesgo de Anticipación (***Look-Ahead Bias***)

El sesgo de anticipación ocurre cuando un algoritmo de simulación toma decisiones operativas basadas en datos que aún no estaban disponibles en el momento en que se generó la orden en el mercado real^3^. En Pine Script, esto ocurre comúnmente al solicitar datos de marcos temporales superiores con la función request.security()^3^.

Si no se desactiva de forma explícita el parámetro de look-ahead (lookahead = barmerge.lookahead_off) u omitiendo el decalaje de vela ([1]), el motor de simulación histórico leerá los valores de cierre de velas superiores antes de que el período del marco temporal menor haya finalizado en el tiempo real^3^. Esto permite al algoritmo "predecir" el comportamiento del mercado con un 100% de acierto teórico, pero el sistema fallará por completo al operar en vivo^3^.

El Manejo de Gaps de Precios y Llenados de Mercado

En mercados financieros con sesiones de negociación discontinuas (p. ej., futuros sobre índices o acciones), el precio de apertura de una vela puede diferir sustancialmente del precio de cierre de la barra anterior^6^. El emulador de TradingView maneja estos escenarios de la siguiente manera:

- Si se activa una orden stop para limitar pérdidas dentro de un gap de apertura desfavorable, el backtester ejecutará la orden al precio de apertura de la nueva vela en lugar del precio stop teórico establecido por el usuario. Esto refleja el deslizamiento real que ocurre en los mercados financieros debido a la falta de liquidez intermedia^6^.
- Si se especifica el parámetro process_orders_on_close = true, el emulador puede omitir el impacto de estos gaps de apertura, ya que simula el llenado de las órdenes en el cierre de la vela de señal^4^. Esto puede maquillar el rendimiento real de la estrategia al ignorar el riesgo de mercado nocturno (*overnight risk*).

11. Comparativa con Strategy Tester de Broker

La evaluación comparativa de las herramientas de simulación es un paso fundamental para los desarrolladores algorítmicos.

| **Dimensión de Análisis** | **TradingView Strategy Tester** | **Plataformas Institucionales (Broker) Strategy Tester** |
| --- | --- | --- |
| **Modelado de Precios** | Resolución de barras con interpolación heurística y lupa de barras basada en sub-barras históricas^12^. | Modelado de ticks reales históricos milisegundo a milisegundo ("Every Tick Based on Real Ticks")^43^. |
| **Optimización de Parámetros** | Sin optimizador nativo incorporado^46^. Requiere soluciones externas o scripts manuales^41^. | Optimizador nativo avanzado con soporte para algoritmos genéticos y fuerza bruta^42^. |
| **Infraestructura de Cálculo** | Procesamiento centralizado en los servidores de la nube de TradingView^47^. | Procesamiento local multi-hilo o distribuido a través de MQL5 Cloud Network^42^. |
| **Soporte de Portafolios (Multiactivo)** | Limitado a un solo activo principal, aunque es posible consultar datos adicionales con request.security^46^. | Soporte nativo y simultáneo para backtesting de múltiples divisas y activos dentro de la misma cuenta^42^. |
| **Simulación de Latencia** | Configurable de forma básica mediante un deslizamiento (*slippage*) de ticks fijo^4^. | Modo de retardo aleatorio incorporado que simula la latencia de red real del bróker^42^. |
| **Lenguaje de Programación** | Pine Script: lenguaje de programación declarativo de alto nivel especializado en series de tiempo^37^. | MQL5: lenguaje orientado a objetos basado en C++ con mayor velocidad de ejecución local^43^. |

Diferencias en los Modos de Modelado y Ticks

La principal diferencia metodológica radica en la precisión del flujo de cotizaciones. Mientras que TradingView simula los movimientos internos de las velas utilizando la lupa de barras (reconstruyendo el comportamiento a partir de velas de temporalidad inferior), Plataformas Institucionales recopila y almacena de forma nativa los ticks reales transmitidos por los brókeres^12^. Esta característica hace que Broker sea la opción idónea para el backtesting de estrategias de alta frecuencia (*High-Frequency Trading*) o algoritmos basados en micro-estructura de libro de órdenes.

Optimización y Red de Agentes

Broker integra un motor de búsqueda de parámetros optimizado mediante algoritmos genéticos^42^. Este motor permite encontrar las variables más estables de una estrategia sin tener que evaluar secuencialmente cada una de las combinaciones posibles, reduciendo el tiempo de cálculo de meses a horas^42^. Además, el sistema permite alquilar la potencia computacional de miles de procesadores a nivel global mediante la red de agentes MQL5 Cloud Network^42^.

TradingView carece de un equivalente nativo, por lo que el desarrollador debe realizar búsquedas manuales o integrar scripts intermedios de optimización utilizando APIs externas para emular esta funcionalidad^46^.

12. Implementación de Sistemas Algorítmicos Completos y Funcionales en Pine Script v6

A continuación, se presentan tres estrategias de trading algorítmico completamente desarrolladas y funcionales en Pine Script v6. Cada una de ellas ilustra las mejores prácticas cuantitativas analizadas anteriormente, utilizando configuraciones explícitas de apalancamiento, gestión de riesgos y dimensionamiento dinámico de posiciones^11^.

Estrategia 1: Cruce de Medias Móviles Exponenciales con Trailing Stop de Precisión y Regla ANY

Esta estrategia implementa un sistema tendencial que utiliza el cruce de dos medias móviles exponenciales (EMA). Para maximizar el rendimiento, se implementa una regla de emparejamiento "ANY" que permite liquidar de forma independiente órdenes de entrada individuales en lugar de aplicar la estructura FIFO por defecto^13^. Adicionalmente, se incorpora un trailing stop dinámico calculado de forma relativa en ticks^25^.

Pine Script

//@version=6

strategy(

     title="Estrategia Cruce EMA con Trailing Stop y Regla ANY",

     shorttitle="Cruce EMA ANY",

     overlay=true,

     initial_capital=10000,

     default_qty_type=strategy.percent_of_equity,

     default_qty_value=10,

     commission_type=strategy.commission.percent,

     commission_value=0.075,

     slippage=1,

     margin_long=100,

     margin_short=100,

     close_entries_rule="ANY"

 )

// --- ENTRADAS DE USUARIO ---

ema_rapida_len = input.int(9, title="Longitud EMA Rápida")

ema_lenta_len = input.int(21, title="Longitud EMA Lenta")

sl_porcentaje = input.float(1.5, title="Stop-Loss Inicial (%)")

tp_porcentaje = input.float(3.0, title="Take-Profit Fijo (%)")

trail_activacion = input.float(1.0, title="Activación de Trailing Stop (%)")

trail_distancia  = input.float(0.5, title="Distancia de Trailing Stop (%)")

// --- CÁLCULO DE INDICADORES ---

ema_rapida = ta.ema(close, ema_rapida_len)

ema_lenta  = ta.ema(close, ema_lenta_len)

// --- LÓGICA DE SEÑALES ---

crossover_largo  = ta.crossover(ema_rapida, ema_lenta)

crossunder_corto = ta.crossunder(ema_rapida, ema_lenta)

// --- EJECUCIÓN OPERATIVA ---

if crossover_largo

    strategy.entry("Largo", strategy.long)

if crossunder_corto

    strategy.entry("Corto", strategy.short)

// --- PROTECCIÓN Y SALIDAS DINÁMICAS (CÁLCULO BASADO EN TICK SIZE) ---

if strategy.position_size > 0

    float precio_entrada_largo = strategy.position_avg_price

    // Conversiones a Ticks basadas en el valor mínimo del instrumento

    int ticks_sl_largo = math.round((precio_entrada_largo * (sl_porcentaje / 100)) / syminfo.mintick)

    int ticks_tp_largo = math.round((precio_entrada_largo * (tp_porcentaje / 100)) / syminfo.mintick)

    int ticks_activacion_largo = math.round((precio_entrada_largo * (trail_activacion / 100)) / syminfo.mintick)

    int ticks_offset_largo = math.round((precio_entrada_largo * (trail_distancia / 100)) / syminfo.mintick)

    strategy.exit(

         "Salida Largo",

         from_entry="Largo",

         loss=ticks_sl_largo,

         profit=ticks_tp_largo,

         trail_points=ticks_activacion_largo,

         trail_offset=ticks_offset_largo

     )

if strategy.position_size < 0

    float precio_entrada_corto = strategy.position_avg_price

    // Conversiones para posiciones cortas

    int ticks_sl_corto = math.round((precio_entrada_corto * (sl_porcentaje / 100)) / syminfo.mintick)

    int ticks_tp_corto = math.round((precio_entrada_corto * (tp_porcentaje / 100)) / syminfo.mintick)

    int ticks_activacion_corto = math.round((precio_entrada_corto * (trail_activacion / 100)) / syminfo.mintick)

    int ticks_offset_corto = math.round((precio_entrada_corto * (trail_distancia / 100)) / syminfo.mintick)

    strategy.exit(

         "Salida Corto",

         from_entry="Corto",

         loss=ticks_sl_corto,

         profit=ticks_tp_corto,

         trail_points=ticks_activacion_corto,

         trail_offset=ticks_offset_corto

     )

// --- VISUALIZACIONES ---

plot(ema_rapida, color=color.lime, title="EMA Rápida")

plot(ema_lenta, color=color.red, title="EMA Lenta")

Estrategia 2: RSI con Filtro de Tendencia Multi-Timeframe e Inspección de Historial (first_index)

Esta estrategia entra al mercado tras correcciones de corto plazo medidas por el Índice de Fuerza Relativa (RSI). Para evitar operar en contra de la tendencia principal, se valida que el precio se encuentre alineado con una media móvil exponencial de un marco temporal superior^56^. Se utiliza una llamada de request.security() con el parámetro calc_bars_count para limitar la carga de datos del historial^49^. Adicionalmente, el script audita los últimos resultados operativos utilizando la variable first_index de la versión 6^11^.

Pine Script

//@version=6

strategy(

     title="Estrategia RSI con Filtro de Tendencia MTF Optimizado",

     shorttitle="RSI MTF Trend",

     overlay=true,

     initial_capital=15000,

     default_qty_type=strategy.percent_of_equity,

     default_qty_value=20,

     commission_type=strategy.commission.percent,

     commission_value=0.1,

     slippage=2,

     margin_long=100,

     margin_short=100

 )

// --- ENTRADAS DE USUARIO ---

rsi_length = input.int(14, title="Longitud del RSI")

rsi_sobrecompra = input.float(70.0, title="Límite de Sobrecompra")

rsi_sobreventa = input.float(30.0, title="Límite de Sobreventa")

tf_tendencia = input.timeframe("D", title="Temporalidad del Filtro de Tendencia")

ema_tendencia_len = input.int(200, title="Longitud EMA Filtro Tendencia")

sl_porcentaje = input.float(2.0, title="Stop-Loss (%)")

tp1_porcentaje = input.float(2.0, title="Take-Profit Parcial 1 (%)")

tp2_porcentaje = input.float(5.0, title="Take-Profit Final 2 (%)")

// --- SOLICITUD DE DATOS MULTI-TIMEFRAME OPTIMIZADA ---

// Se limita la carga histórica de datos en la temporalidad diaria para optimizar el script

ema_tendencia_diaria = request.security(

     syminfo.tickerid, 

     tf_tendencia, 

     ta.ema(close, ema_tendencia_len), 

     calc_bars_count=500

 )

// --- CÁLCULOS LOCALES ---

rsi_valor = ta.rsi(close, rsi_length)

// Se evita el sesgo de anticipación usando datos históricos desfasados de la vela superior [1]

tendencia_alcista  = close > ema_tendencia_diaria[1]

tendencia_bajista = close < ema_tendencia_diaria[1]

// --- CONDICIONES OPERATIVAS ---

senal_compra = tendencia_alcista and ta.crossover(rsi_valor, rsi_sobreventa)

senal_venta  = tendencia_bajista and ta.crossunder(rsi_valor, rsi_sobrecompra)

// --- ENTRADA EN MERCADO ---

if senal_compra

    strategy.entry("Long", strategy.long)

if senal_venta

    strategy.entry("Short", strategy.short)

// --- ARQUITECTURA DE SALIDAS ESCALONADAS (ORDEN BRACKET PARCIAL) ---

if strategy.position_size > 0

    float precio_entrada = strategy.position_avg_price

    float sl_precio = precio_entrada * (1.0 - (sl_porcentaje / 100.0))

    float tp1_precio = precio_entrada * (1.0 + (tp1_porcentaje / 100.0))

    float tp2_precio = precio_entrada * (1.0 + (tp2_porcentaje / 100.0))

    // Se ejecuta el primer objetivo de toma de ganancias sobre el 50% de la posición

    strategy.exit("TP1_Long", from_entry="Long", qty_percent=50, limit=tp1_precio, stop=sl_precio)

    // Se ejecuta el segundo objetivo sobre el remanente de la posición

    strategy.exit("TP2_Long", from_entry="Long", qty_percent=100, limit=tp2_precio, stop=sl_precio)

if strategy.position_size < 0

    float precio_entrada = strategy.position_avg_price

    float sl_precio = precio_entrada * (1.0 + (sl_porcentaje / 100.0))

    float tp1_precio = precio_entrada * (1.0 - (tp1_porcentaje / 100.0))

    float tp2_precio = precio_entrada * (1.0 - (tp2_porcentaje / 100.0))

    strategy.exit("TP1_Short", from_entry="Short", qty_percent=50, limit=tp1_precio, stop=sl_precio)

    strategy.exit("TP2_Short", from_entry="Short", qty_percent=100, limit=tp2_precio, stop=sl_precio)

// --- AUDITORÍA DE OPERACIONES EN TIEMPO DE EJECUCIÓN (first_index) ---

var float tasa_efectividad_reciente = na

int primer_indice = strategy.closedtrades.first_index

int trades_cerrados = strategy.closedtrades.size()

if barstate.islast and trades_cerrados > primer_indice

    int ganadoras = 0

    int total_analizado = 0

    for i = primer_indice to trades_cerrados - 1

        total_analizado += 1

        if strategy.closedtrades.profit(i) > 0

            ganadoras += 1

    tasa_efectividad_reciente := (ganadoras / total_analizado) * 100.0

// --- VISUALIZACIONES ---

plot(ema_tendencia_diaria, color=color.orange, title="EMA de Tendencia MTF")

Estrategia 3: Breakout de Rango ATR con Sizing Dinámico Basado en Volatilidad y Lupa de Barras

Esta estrategia aprovecha los breakouts (rupturas) de volatilidad de los canales de Keltner. El tamaño de cada posición se calcula dinámicamente en base a la volatilidad real del mercado (medida por el Average True Range, ATR) y al riesgo que el usuario desea asumir por operación^31^:

Este cálculo dinámico permite adaptar el tamaño de la posición a las condiciones del mercado: se reduce en periodos de alta volatilidad y se incrementa cuando la volatilidad disminuye^31^. La estrategia está diseñada para ejecutarse bajo la lupa de barras (use_bar_magnifier = true) para garantizar la precisión de los cierres^7^.

Pine Script

//@version=6

strategy(

     title="Estrategia Breakout ATR con Position Sizing Dinámico",

     shorttitle="Breakout ATR Sizing",

     overlay=true,

     initial_capital=20000,

     default_qty_type=strategy.cash,

     commission_type=strategy.commission.percent,

     commission_value=0.05,

     slippage=1,

     margin_long=100,

     margin_short=100,

     use_bar_magnifier=true

 )

// --- ENTRADAS DE USUARIO ---

keltner_longitud = input.int(20, title="Longitud Canales de Keltner")

keltner_multiplicador = input.float(1.5, title="Multiplicador del Canal")

atr_longitud = input.int(14, title="Longitud del ATR para Detención")

atr_multiplicador_stop = input.float(2.0, title="Multiplicador de Stop-Loss")

porcentaje_riesgo_cuenta = input.float(1.0, title="Riesgo de Cuenta por Trade (%)")

// --- CÁLCULO DE CANALES Y VOLATILIDAD ---

atr_valor = ta.atr(atr_longitud)

base_canal = ta.ema(close, keltner_longitud)

keltner_superior = base_canal + (keltner_multiplicador * atr_valor)

keltner_inferior = base_canal - (keltner_multiplicador * atr_valor)

// --- DIMENSIONAMIENTO DINÁMICO DE POSICIONES (POSITION SIZING) ---

capital_riesgo = strategy.equity * (porcentaje_riesgo_cuenta / 100.0)

distancia_stop = atr_valor * atr_multiplicador_stop

// Cálculo de la cantidad en contratos evitando errores de división por cero

float cantidad_contratos = distance_stop > 0 ? (capital_riesgo / distance_stop) : na

// --- EVALUACIÓN DE SEÑALES ---

breakout_largo = ta.crossover(close, keltner_superior)

breakout_corto = ta.crossunder(close, keltner_inferior)

// --- EJECUCIÓN OPERATIVA CON DETALLES DE VOLATILIDAD ---

if breakout_largo and not na(cantidad_contratos)

    strategy.entry("BreakoutLargo", strategy.long, qty=cantidad_contratos)

if breakout_corto and not na(cantidad_contratos)

    strategy.entry("BreakoutCorto", strategy.short, qty=cantidad_contratos)

// --- PROTECCIÓN DINÁMICA ABSOLUTA ---

if strategy.position_size > 0

    float stop_absoluto_largo = strategy.position_avg_price - (atr_valor * atr_multiplicador_stop)

    float tp_absoluto_largo = strategy.position_avg_price + (atr_valor * atr_multiplicador_stop * 2.0)

    strategy.exit("Exit_Long", from_entry="BreakoutLargo", stop=stop_absoluto_largo, limit=tp_absoluto_largo)

if strategy.position_size < 0

    float stop_absoluto_corto = strategy.position_avg_price + (atr_valor * atr_multiplicador_stop)

    float tp_absoluto_corto = strategy.position_avg_price - (atr_valor * atr_multiplicador_stop * 2.0)

    strategy.exit("Exit_Short", from_entry="BreakoutCorto", stop=stop_absoluto_corto, limit=tp_absoluto_corto)

// --- VISUALIZACIONES ---

plot(keltner_superior, color=color.aqua, title="Keltner Superior")

plot(keltner_inferior, color=color.aqua, title="Keltner Inferior")

plot(base_canal, color=color.gray, title="Canal Base")

Fuentes citadas

- Concepts / Strategies - TradingView, https://www.tradingview.com/pine-script-docs/concepts/strategies/
- Concepts / Strategies - TradingView, https://www.tradingview.com/pine-script-docs/v5/concepts/strategies/
- Pine Script Language Reference Manual — TradingView, https://www.tradingview.com/pine-script-reference/v5/
- Propiedades de la Estrategia - TradingView, https://es.tradingview.com/support/solutions/43000628599/
- Language / Declaration statements - TradingView, https://www.tradingview.com/pine-script-docs/language/declaration-statements/
- Your TradingView Backtest Is 30–50% More Optimistic Than Reality, Here's the Exact Fix, https://medium.com/@rangatechnologies/your-tradingview-backtest-is-30-50-more-optimistic-than-reality-heres-the-exact-fix-d4647b22b2c8
- MACD Strategy + 2 Profit Targets - Pine Script Mastery Course, https://courses.theartoftrading.com/pages/macd-strategy-2-profit-targets-in-pine-script
- tradingview-pine-scripts/BEST Strategy Template w- Custom SL-TP Size - Educational.pine at main - GitHub, https://github.com/hasnocool/tradingview-pine-scripts/blob/main/BEST%20Strategy%20Template%20w-%20Custom%20SL-TP%20Size%20-%20Educational.pine
- I Spent 3 Months Backtesting the Same Strategy. Here's What I Got Wrong - Medium, https://medium.com/@betashorts1998/i-spent-3-months-backtesting-the-same-strategy-heres-what-i-got-wrong-c0128a4b8759
- Release notes - TradingView, https://www.tradingview.com/pine-script-docs/v5/release-notes/
- 4 Pine Script v6 Strategy Changes That Alter Backtests - TradersPost, https://blog.traderspost.io/article/pine-script-v6-strategy-changes
- What is bar magnifier backtesting mode - TradingView, https://www.tradingview.com/support/solutions/43000669285-what-is-bar-magnifier-backtesting-mode/
- Pine Script v5 User Manual (350-509) | PDF | Margin (Finance) | Computing - Scribd, https://www.scribd.com/document/707955802/Pine-Script-v5-User-Manual-350-509
- Bar Magnifier | PyneCore Documentation, https://pynecore.org/docs/advanced/bar-magnifier/
- FAQ & Code - PineCoders, https://www.pinecoders.com/faq_and_code/
- My strategy processes orders one candle after the condition has been met - TradingView, https://www.tradingview.com/support/solutions/43000619439-my-strategy-processes-orders-one-candle-after-the-condition-has-been-met/
- Strategy not executing on Open, High, Low, Close as it should with calc_on_order_fills = true and calc_on_every_tick = true - Stack Overflow, https://stackoverflow.com/questions/62505698/strategy-not-executing-on-open-high-low-close-as-it-should-with-calc-on-order
- How to fix trades closing prematurely - pine script - Stack Overflow, https://stackoverflow.com/questions/77891869/how-to-fix-trades-closing-prematurely
- Unable to close/exit a position in Pinescript - Stack Overflow, https://stackoverflow.com/questions/78880423/unable-to-close-exit-a-position-in-pinescript
- The Main Limitations of Pine Script on TradingView - Quant Nomad, https://quantnomad.com/the-main-limitations-of-pine-script-on-tradingview/
- Sortino Ratio - TradingView, https://www.tradingview.com/support/solutions/43000681697-sortino-ratio/
- Sharpe Ratio - TradingView, https://es.tradingview.com/support/solutions/43000681694/
- Another one of these broken backtests. : r/TradingView - Reddit, https://www.reddit.com/r/TradingView/comments/1lcp2mx/another_one_of_these_broken_backtests/
- Language / Built-ins - TradingView, https://www.tradingview.com/pine-script-docs/v5/language/built-ins/
- Few ways to close/exit positions in Pine Script - Quant Nomad, https://quantnomad.com/few-ways-to-close-exit-positions-in-pine-script/
- Pine Script: strategy.exit Error with Trailing Stop and Stop Loss - Stack Overflow, https://stackoverflow.com/questions/78684238/pine-script-strategy-exit-error-with-trailing-stop-and-stop-loss
- pine script - How to know if last trade closed was a long or short in strategy - Stack Overflow, https://stackoverflow.com/questions/73592646/how-to-know-if-last-trade-closed-was-a-long-or-short-in-strategy
- strategy.opentrades | PyneCore Documentation, https://pynecore.org/docs/reference/lib/strategy_opentrades/
- Strategies - TradingView, https://www.tradingview.com/pine-script-docs/faq/strategies/
- strategy.closedtrades | PyneCore Documentation, https://pynecore.org/docs/reference/lib/strategy_closedtrades/
- Pine Script v6 Strategy Code Examples - CrossTrade, https://crosstrade.io/blog/pine-script-v6-strategy-code-examples
- Automated Trading FAQ - Complete Guide to TradingView Automation - PickMyTrade, https://pickmytrade.io/en/general-faq
- Close trade on bar close : r/pinescript - Reddit, https://www.reddit.com/r/pinescript/comments/1dtvqmn/close_trade_on_bar_close/
- How do trail_points and trail_offset work with Takeprofit and Stoploss - Stack Overflow, https://stackoverflow.com/questions/73893459/how-do-trail-points-and-trail-offset-work-with-takeprofit-and-stoploss
- TradingView Pine Script Reference v6 (websites/cn_tradingview_pine-script-reference_v6), https://context7.com/websites/cn_tradingview_pine-script-reference_v6
- How exactly does trail_price, trail_offset work in pinescript? - Stack Overflow, https://stackoverflow.com/questions/65839439/how-exactly-does-trail-price-trail-offset-work-in-pinescript
- Pine Script User Manual Guide | PDF - Scribd, https://www.scribd.com/document/970916586/Pine-Script-v6-User-Manual
- Backtest results differ from real entry and exit signals - Stack Overflow, https://stackoverflow.com/questions/79183930/backtest-results-differ-from-real-entry-and-exit-signals
- Pine Script Repaints in Bar Replay, Shows Different Results in Backtest - Stack Overflow, https://stackoverflow.com/questions/76018685/pine-script-repaints-in-bar-replay-shows-different-results-in-backtest
- Micro S&P 500 Futures Trade Ideas — BMFBOVESPA:WSP1! - TradingView, https://www.tradingview.com/symbols/BMFBOVESPA-WSP1!/ideas/
- TradingView Backtesting: Strategy Tester Guide (2026), https://www.tv-hub.org/guide/tradingview-backtesting
- Strategy Tester: Plataformas Institucionales - Broker | AMP Futures, https://www.ampfutures.com/Brokers/automated-trading/strategy-tester
- Best Automation Tools for Broker in 2025 | For Traders, https://www.fortraders.com/blog/automation-tools-broker
- Basics » Backtesting on TradingView - Whitebox Docs, https://docs.whitebox.so/basics/backtesting-on-tradingview
- Breaking the Boundaries: Pine Script Needs a Higher Calculation Limit! : r/TradingView, https://www.reddit.com/r/TradingView/comments/14b3enw/breaking_the_boundaries_pine_script_needs_a/
- Best Backtesting Software for Traders (2026) - TradeZella, https://www.tradezella.com/best-backtesting-software
- TradingView's Deep Backtesting is out of beta - FX News Group, https://fxnewsgroup.com/forex-news/platforms/tradingviews-deep-backtesting-is-out-of-beta/
- pine script - Backtesting Precision / use_bar_magnifier - Stack Overflow, https://stackoverflow.com/questions/72593336/backtesting-precision-use-bar-magnifier
- Writing / Limitations - TradingView, https://www.tradingview.com/pine-script-docs/writing/limitations/
- Writing / Limitations - TradingView, https://www.tradingview.com/pine-script-docs/v5/writing/limitations/
- S&P 500 FUTURES (Jun 2027) Trade Ideas — TAIFEX:SPFM2027 - TradingView, https://www.tradingview.com/symbols/TAIFEX-SPF1%21/ideas/?contract=SPFM2027
- Advanced Volatility and Risk-Adjusted Return Indicator - Indie Script, https://indie-script.github.io/indicators/Advanced%20Volatility%20And%20Risk-adjusted%20Return%20Indicator/
- pine script needs to have better trailing stops added to it : r/TradingView - Reddit, https://www.reddit.com/r/TradingView/comments/q340hm/pine_script_needs_to_have_better_trailing_stops/
- Best Backtesting Software for Traders (2026 Comparison) - TradeZella, https://www.tradezella.com/blog/best-backtesting-software
- The 'calc_bars_count' parameter doesn't work. TradingView bug? : r/pinescript - Reddit, https://www.reddit.com/r/pinescript/comments/1kn9mow/the_calc_bars_count_parameter_doesnt_work/
- Converting HalfTrend indicator to TradingView Strategy - Tanay Roy - Medium, https://tanayroy.medium.com/converting-halftrend-indicator-to-tradingview-strategy-20b1adf78803
- TradingView Bar Replay Alternative - TradeZella, https://www.tradezella.com/vs/tradingview
- Best AI Tools for Trading Strategy Development - LuxAlgo, https://www.luxalgo.com/blog/best-ai-tools-trading-strategy-development/
- Get Started with Pinescript: Learn everything to build your first Trading Robot - Pinetrader, https://pinetrader.io/coding/pinescript-tutorial
- 5 Causes of Slow Pine Scripts on TradingView - LuxAlgo, https://www.luxalgo.com/blog/5-causes-of-slow-pine-scripts-on-tradingview/