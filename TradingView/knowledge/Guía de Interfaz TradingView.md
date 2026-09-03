Guía Técnica Avanzada de la Interfaz de Usuario y Herramientas Nativas de TradingView

1. Tipos de Gráficos Nativos: Interpretación Analítica y Casos de Uso

La interfaz de TradingView integra representaciones gráficas avanzadas que van más allá del análisis temporal clásico, permitiendo aislar la volatilidad, la acumulación institucional y la liquidez^1^. Estos gráficos se clasifican en sistemas basados en tiempo y sistemas basados exclusivamente en el precio^2^.

Velas Japonesas (Candlesticks), Velas Huecas (Hollow Candles) y Barras (OHLC)

Los gráficos de barras y de velas tradicionales estructuran el precio bajo la clásica discretización temporal^1^. La variante de velas huecas (Hollow Candles) enriquece la lectura de la acción del precio al vincular la dirección del precio intradía con la relación de cierre respecto a la barra anterior^4^. Su lógica visual opera bajo cuatro estados discretos:

- **Velas verdes huecas (acumulación fuerte)**: El precio de cierre actual supera el cierre de la vela previa y, a su vez, es superior al precio de apertura de la propia vela^4^. Representa una sesión de firme convicción alcista donde los compradores retienen el control absoluto durante todo el intervalo de tiempo^4^.
- **Velas verdes rellenas (absorción alcista)**: El precio de cierre es superior al cierre previo, pero inferior a la apertura de la sesión actual^4^. Revela un gap alcista de apertura que fue distribuido a la baja durante la sesión, constituyendo una señal de agotamiento u oferta flotante^4^.
- **Velas rojas huecas (absorción bajista)**: El precio de cierre es inferior al cierre anterior, pero el cierre de la sesión logra situarse por encima de la apertura de la misma vela^4^. Muestra un gap bajista inicial que es defendido activamente por los compradores, sugiriendo zonas de soporte o captación de liquidez^4^.
- **Velas rojas rellenas (distribución fuerte)**: El precio de cierre es inferior al cierre anterior y, simultáneamente, inferior al precio de apertura de la vela^4^. Indica una presión de venta constante sin resistencia por parte de la demanda^4^.

Heikin Ashi: Algoritmo de Suavizado y Detección de Tendencias

El gráfico Heikin Ashi modifica el precio de apertura, máximo, mínimo y cierre de cada barra utilizando un promedio ponderado para mitigar el ruido estadístico del mercado^1^. Las fórmulas matemáticas que rigen este gráfico son las siguientes^5^:

- **Ventajas tendenciales**: Las tendencias alcistas sólidas se muestran como series consecutivas de velas Heikin Ashi alcistas sin sombras inferiores^5^. Las tendencias bajistas consolidadas se presentan como velas consecutivas bajistas sin sombras superiores^5^.
- **Trampas y riesgos**: Las cotizaciones mostradas en el gráfico Heikin Ashi son promedios matemáticos y no reflejan los precios reales de ejecución del mercado^5^. Colocar órdenes de tipo stop o límite directamente basándose en el precio visual de Heikin Ashi produce un deslizamiento de ejecución severo^5^. Se debe usar la escala de precios real de la derecha como único referente operativo^5^.

Renko: Configuración de Bloques y Estructuración de Soporte/Resistencia

Los gráficos Renko descartan el tiempo y trazan bloques ("ladrillos") únicamente cuando el precio supera un umbral de movimiento preestablecido^3^. La plataforma implementa tres métodos de cálculo para el tamaño de bloque^2^:

- **Traditional (Tradicional)**: El usuario define un valor absoluto en puntos o unidades monetarias^2^. Un tamaño óptimo suele aproximarse a  de la cotización actual del activo^6^.
- **ATR (Average True Range)**: El sistema calcula dinámicamente el tamaño del bloque según el indicador ATR de 14 periodos en gráficos de velas tradicionales, adaptándose de forma automática a la volatilidad del mercado^2^.
- **Percentage LTP (Porcentaje de Último Precio de Negociación)**: El bloque se calcula como un porcentaje del precio de cierre más reciente, redondeando la cifra obtenida al tamaño de tick mínimo del activo^2^. Este método presenta riesgo de repintado histórico debido a la revalorización de los precios^6^.

La regla de colocación de bloques establece que las esquinas de los ladrillos siempre deben tocarse y nunca puede coexistir más de un bloque en la misma columna vertical^6^. Los gráficos Renko son ideales para identificar soportes y resistencias horizontales estructurales al eliminar las fluctuaciones intradía ruidosas^6^. El analista debe tener en cuenta que el cálculo preciso de los bloques históricos requiere datos de ticks de alta granularidad; de lo contrario, el software utilizará los cierres de intervalos inferiores de tiempo de la barra actual (como barras de 1 minuto) para la reconstrucción, generando leves diferencias visuales según el intervalo seleccionado^6^.

Kagi: Lógica de Reversión y Niveles de Yang y Yin

Los gráficos Kagi consisten en líneas verticales continuas de grosor variable que rastrean la acción del precio sin considerar variables temporales^9^. La línea se dibuja de forma continua en la dirección del movimiento actual^9^. Si el precio invierte su rumbo en una cuantía superior al valor de reversión establecido (fijado mediante el método de ATR o Tradicional), se traza una línea horizontal de conexión y se inicia una nueva columna en la dirección opuesta^9^.

Las líneas se denominan *Yang* cuando se vuelven gruesas (o verdes) al romper por encima del máximo del hombro anterior^9^. Se denominan *Yin* cuando se vuelven delgadas (o rojas) al romper por debajo del mínimo de la cintura anterior^9^. Las uniones horizontales superiores se conocen como *hombros* y actúan como zonas de resistencia estructural, mientras que las inferiores se denominan *cinturas* y actúan como zonas de soporte dinámico^9^. La metodología clásica descrita por Steve Nison propone comprar en la transición de Yin a Yang y vender en la de Yang a Yin, monitorizando a su vez la regla de los nueve giros consecutivos como advertencia de un cambio de tendencia inminente^9^.

Point & Figure (P&F): Proyecciones Verticales y Patrones Clásicos

El gráfico de Punto y Figura registra la fluctuación del precio mediante columnas alternas de "X" (alcistas) y "O" (bajistas)^11^. Se configura a través de dos parámetros: el tamaño de la caja (box size) y el factor de reversión (típicamente de 3 cajas)^11^. El precio debe recorrer el tamaño de la caja para añadir un carácter, y debe revertirse el equivalente al factor multiplicado por el tamaño de caja para iniciar una columna contraria^11^.

Para el análisis de la acumulación según el método Wyckoff, la plataforma incorpora de forma exclusiva la opción *One Step Back Building*^13^. Esta característica permite unificar columnas de "X" y "O" en una sola columna ante retrocesos breves de una sola caja, evitando la fragmentación del gráfico y facilitando la visualización directa de los patrones tradicionales de ruptura de Punto y Figura:

- **Doble Techo/Doble Suelo**: Rupturas simples de la resistencia o soporte inmediatamente anterior^12^.
- **Señal Alcista/Bajista de Triple Techo**: Ruptura coordinada donde la tercera columna supera la altura de las dos resistencias previas, lo que indica una fuerte presión compradora.
- **Proyección de objetivos (Thrust Target)**: Utiliza la metodología de conteo de cajas horizontales multiplicadas por el factor de reversión para proyectar de forma vertical el objetivo potencial de precios una vez que el patrón rompe su base de acumulación o distribución^12^.

Line Break: Filtro de Reversión Basado en Bloques Comparativos

El gráfico Line Break dibuja líneas alcistas o bajistas según la superación de los precios de cierre de las barras precedentes configuradas por el usuario (habitualmente 2, 3 o 4 líneas)^2^.

- **Lógica operativa**: Si el gráfico está configurado en "3 líneas", no se dibujará ninguna línea nueva en dirección opuesta a menos que el precio de cierre actual supere el precio máximo o mínimo de las tres líneas confirmadas anteriores^2^.
- **Interpretación**: Ideal para inversores de tendencia a medio y largo plazo, ya que las consolidaciones menores o los retrocesos breves no alteran el color ni la estructura de las barras, permitiendo mantener la posición hasta que ocurre una ruptura real del soporte o resistencia de control^3^.

Range: Barras Basadas en Rango de Precio Fijo

Las barras de rango se centran de forma exclusiva en la distancia recorrida por el precio, aislando por completo la distorsión del factor temporal^7^. La fórmula fundamental que rige el tamaño mínimo de un intervalo de rango es:

Cada vez que el precio de cotización cruza los límites de precio establecidos de la barra actual (que van desde su máximo hasta su mínimo), la barra se cierra de inmediato y se abre una nueva barra de rango en el mercado^8^. La interfaz permite parametrizar las denominadas *Projection Bars* (velas temporales proyectadas que reflejan la fluctuación del rango en formación) y las *Phantom Bars* (velas de relleno que representan huecos de precios o gaps donde el precio cotizó de forma virtual sin registrar volumen de negociación directa a través del feed de datos del intercambio)^8^. Las barras de rango no son compatibles con el modo de reproducción de barras de la plataforma^8^.

Volume Footprint y Volume Profile (Premium)

Estas herramientas ofrecen un análisis tridimensional (tiempo, precio y volumen) del flujo de transacciones ejecutadas^18^.

El **Volume Footprint** muestra en cada nivel de precio el volumen cruzado en el bid (izquierda) y en el ask (derecha)^18^. El sistema utiliza datos históricos intrabarra de la mayor granularidad disponible (desde ticks y segundos hasta minutos)^18^. Clasifica la naturaleza del volumen vendedor o comprador según las variaciones intradía de los subintervalos analizados^18^. Cuenta con un algoritmo de detección automática de desequilibrios o *imbalances*, resaltando con líneas de color cuando el volumen de compra en un nivel supera de forma diagonal en un porcentaje configurable (por defecto, el 300%) al volumen de venta del precio inmediatamente inferior^19^.

Por su parte, el **Volume Profile** (Perfil de Volumen) estructura la distribución del volumen como un histograma horizontal a lo largo del eje del precio^20^. Al analizar este perfil, se pueden identificar áreas de valor y niveles clave:

- **Punto de Control (POC)**: El nivel de precio con mayor densidad de volumen negociado^20^.
- **Área de Valor (Value Area - VA)**: El rango de precios que concentra el 70% (u otro porcentaje definido) de toda la actividad de trading del perfil^20^.
- **Value Area High (VAH) / Value Area Low (VAL)**: Los límites superior e inferior de dicha área de valor^20^.
- **High Volume Nodes (HVN)**: Zonas de alta densidad de volumen que representan niveles de consolidación y aceptación de valor por parte del mercado institucional^20^.
- **Low Volume Nodes (LVN)**: Zonas de vacío de volumen que el precio cruza con gran velocidad debido a la falta de liquidez y a la desaprobación de valor, actuando frecuentemente como soportes o resistencias dinámicas de alta fiabilidad^20^.

Baseline, Area, Columns, High-Low

- **Baseline (Línea de Base)**: Representa el movimiento del precio en relación con una línea de referencia central elegida de forma manual o automática^1^. El área superior se colorea en tonos verdes/azules indicando primas de cotización, mientras que el área inferior se muestra en tonos rojos reflejando descuentos de cotización^1^. Es muy útil para analizar consolidaciones laterales de largo plazo o fases de acumulación^24^.
- **Area y HLC Area**: El gráfico de área tradicional conecta los cierres y sombrea la sección inferior del eje temporal para enfatizar el volumen acumulado de precios^1^. La variante técnica de **HLC Area** conecta de forma simultánea el máximo, el mínimo y el cierre de cada sesión^1^. Esto permite visualizar en una banda sombreada de color la volatilidad histórica del activo, descartando el precio de apertura que suele aportar menos información analítica^1^.
- **Columns (Columnas)**: Representa la variación de precios mediante barras verticales que se elevan desde el eje inferior del gráfico^1^. El color se define en relación con el cierre previo, resultando ideal para la visualización continuada de indicadores de corte macroeconómico como los rendimientos de bonos soberanos, el PIB o las tasas de desempleo de las naciones^1^.
- **High-Low (Máximo-Mínimo)**: Muestra barras verticales sin cuerpo que abarcan únicamente el rango registrado entre el precio máximo y mínimo de la sesión^1^. Se visualiza utilizando un único color para evitar el sesgo psicológico de la tendencia actual y es idóneo para scalpers y analistas que operan rangos puros de volatilidad estadística^28^.

| **Tipo de Gráfico** | **Factor Principal** | **Variables Visualizadas** | **Ventajas Analíticas** | **Caso de Uso Óptimo** |
| --- | --- | --- | --- | --- |
| **Hollow Candles**<br>[cite: 4] | Tiempo^2^ | Apertura, Máximo, Mínimo, Cierre, Relación previa^4^. | Revela acumulación intradía^4^. | Confirmación de rupturas estructurales^4^. |
| **Heikin Ashi**<br>[cite: 5] | Tiempo y Promedios^5^ | Apertura, Máximo, Mínimo, Cierre suavizados^5^. | Identificación clara de la tendencia dominante^5^. | Gestión de posiciones en tendencias prolongadas^5^. |
| **Renko**<br>[cite: 6] | Rango de Precio^6^ | Bloques de tamaño preestablecido^6^. | Filtra el ruido temporal de corto plazo^3^. | Definición de soportes y resistencias limpios^6^. |
| **Kagi**<br>[cite: 9] | Sentido de Tendencia^9^ | Líneas verticales Yang/Yin, hombros/cinturas^9^. | Destaca los cambios de tendencia significativos^9^. | Estrategias de seguimiento de tendencia limpia^9^. |
| **Point & Figure**<br>[cite: 11] | Dirección de Precio^11^ | Columnas de "X" e "O"^11^. | Proyección matemática de objetivos verticales^11^. | Metodología de análisis de Wyckoff^13^. |
| **Line Break**<br>[cite: 15] | Precio Comparativo^15^ | Bloques basados en  cierres anteriores^2^. | Evita las salidas falsas en tendencias maduras^3^. | Seguimiento de tendencias institucionales^3^. |
| **Range**<br>[cite: 17] | Volatilidad Fija^17^ | Barras basadas en ticks de movimiento^7^. | Independencia del tiempo y de los periodos de inactividad^8^. | Operativa intradiaria de alta velocidad (Scalping)^7^. |
| **HLC Area**<br>[cite: 25] | Tiempo y Volatilidad^25^ | Máximo, Mínimo, Cierre en área sombreada^1^. | Desarta gaps intrascendentes y resalta la volatilidad^25^. | Análisis rápido del rango de volatilidad del mercado^25^. |
| **Columns**<br>[cite: 27] | Precio Absoluto^27^ | Columnas desde base inferior^27^. | Estructura visual para datos comparativos continuos^27^. | Representación de datos macroeconómicos e indicadores de mercado^27^. |
| **High-Low**<br>[cite: 28] | Volatilidad Absoluta^28^ | Rango máximo-mínimo de la barra^28^. | Neutralidad psicológica frente al sesgo alcista/bajista^28^. | Identificación rápida de rangos intradiarios estadísticos^28^. |

2. Herramientas de Dibujo: Catálogo por Categorías y Metodologías

TradingView incorpora un conjunto completo de herramientas de dibujo que permiten realizar análisis geométricos y de proyección de forma precisa^31^.

Fibonacci

- **Retrocesos de Fibonacci**: Permiten medir el porcentaje de corrección de una onda previa en base a los coeficientes tradicionales de la sucesión de Fibonacci (, , , , , , etc.)^30^. Es posible habilitar la extensión indefinida de estos niveles hacia la izquierda o la derecha^32^.
- **Extensiones de Fibonacci**: Proyectan objetivos de precio a partir del fin de una corrección, calculando las distancias de las ondas basadas en los ratios del , , ,  y ^30^.
- **Abanico (Fibonacci Fan)**: Traza líneas diagonales de velocidad a partir de un vector inicial de tendencia, dividiendo el espacio angular según los ratios de Fibonacci para delimitar soportes o resistencias dinámicos.
- **Zonas de Tiempo de Fibonacci**: Líneas verticales espaciadas según la secuencia matemática clásica () que se proyectan a partir de un cambio estructural inicial para anticipar posibles puntos de inflexión temporal en el mercado.
- **Espiral de Fibonacci / Arcos de Fibonacci / Canales de Fibonacci**: Herramientas que calculan proporciones áureas en términos espaciales, angulares o temporales secuenciales en el eje horizontal del gráfico.

Teoría de Gann

- **Abanico de Gann (Gann Fan)**: Compuesto por nueve líneas diagonales trazadas a partir de un máximo o un mínimo significativo que representan la relación entre el tiempo y el precio de cotización del activo^33^. La directriz principal es la línea  (un ángulo de 45° que indica una unidad de precio por una unidad de tiempo)^33^. El abanico incluye a su vez líneas como la  (dos unidades de precio por una de tiempo), , , , y sus equivalentes inversas de tiempo sobre precio (, , , )^33^.
- **Caja de Gann (Gann Box) y Cuadrado de Gann (Gann Square)**: Dividen de manera geométrica un ciclo o rango completo de mercado en partes iguales en el eje temporal y de precios^35^. Estas herramientas permiten identificar tanto los niveles clave de soporte y resistencia como las fechas críticas de inversión de ciclos pasados que tienden a repetirse^35^. Para que mantengan su precisión geométrica, es fundamental activar una escala de relación fija en el gráfico para asegurar la simetría de las coordenadas precio-tiempo^35^.

Pitchfork (Tridente de Andrews) y Variantes

Los tridentes de análisis geométrico proyectan canales dinámicos de tendencia basados en tres pivotes de precios consecutivos que delimitan la volatilidad de un movimiento^39^. Al trazar estos pivotes, se define la mediana y sus líneas paralelas^40^. Las coordenadas de los extremos pueden ajustarse de forma precisa desde la configuración del dibujo, con opción de extender las líneas de forma indefinida^32^.

| **Variante de Pitchfork** | **Fórmula Geométrica del Eje de Mediana** | **Aplicación Práctica en Análisis** |
| --- | --- | --- |
| **Andrews Classic**<br>[cite: 31] | Conecta el Pivote 1 (origen) con el punto medio de la línea imaginaria que une el Pivote 2 y el Pivote 3^41^. | Canales de tendencia estándar de velocidad de mercado media y estable^40^. |
| **Schiff**<br>[cite: 31] | Desplaza el origen (Pivote 1) verticalmente la mitad de la distancia entre el Pivote 1 y el Pivote 2^41^. | Correcciones tendenciales prolongadas o de menor aceleración^39^. |
| **Modified Schiff**<br>[cite: 39] | Desplaza el punto de origen exactamente a la mitad del vector lineal que une el Pivote 1 y el Pivote 2^39^. | Tendencias con fuerte aceleración inicial que se moderan rápidamente^39^. |
| **Inside**<br>[cite: 31] | Desplaza el punto de origen al punto medio del vector vertical y horizontal de los primeros dos puntos de pivote, apuntando directamente al Pivote 3^41^. | Mercados de muy alta volatilidad y canales de oscilación de corto plazo^42^. |

Elliott Wave (Ondas de Elliott)

- **Ondas de Impulso (1-2-3-4-5)**: Permite etiquetar de forma consecutiva las estructuras motrices del mercado^31^.
- **Ondas de Corrección (A-B-C, W-X-Y, W-X-Y-X-Z)**: Diseñadas para estructurar de manera gráfica las fases de consolidación lateral, zig-zags o triángulos correctivos de mayor complejidad^31^.
- **Directrices de control**: El analista puede verificar visualmente las tres reglas irrefutables de la teoría de Elliott:

- La Onda 2 nunca puede retroceder más del  de la Onda 1.
- La Onda 3 nunca puede ser la onda más corta de las tres ondas motrices alcistas o bajistas.
- La Onda 4 nunca debe solaparse con el territorio de la Onda 1 (salvo en estructuras de cuña o diagonales de inicio/final).

Patrones Armónicos

TradingView ofrece la herramienta inteligente **XABCD Pattern** para identificar de forma precisa y trazar a mano alzada las estructuras armónicas basadas en los ratios y retrocesos de Fibonacci descritos por Scott Carney^43^.

| **Patrón Armónico** | **Coeficiente de Fibonacci AB / XA** | **Coeficiente de Fibonacci BC / AB** | **Coeficiente de Fibonacci CD / BC** | **Relación del Punto de Inflexión D** |
| --- | --- | --- | --- | --- |
| **Gartley**<br>[cite: 43] | Exacto<br>[cite: 43] | Entre  y<br>[cite: 43] | Entre  y<br>[cite: 43] | Debe corregir al  de XA^43^. |
| **Bat**<br>[cite: 43] | Entre  y<br>[cite: 43] | Entre  y<br>[cite: 43] | Entre  y<br>[cite: 43] | Debe corregir al  de XA^43^. |
| **Butterfly**<br>[cite: 43] | Exacto | Entre  y | Entre  y | Extensión profunda de  a  de XA^43^. |
| **Crab**<br>[cite: 43] | Entre  y<br>[cite: 43] | Entre  y<br>[cite: 43] | Extensión extrema de  a<br>[cite: 43] | Extensión final de  de XA^43^. |
| **Cypher**<br>[cite: 47] | Entre  y | Extensión de  a  (punto C) | Entre  y | Retroc. exacto de  de XC^30^. |
| **Shark**<br>[cite: 47] | No definido | Entre  y  (punto C) | Entre  y | Proyección de  a  de XA^47^. |

Canales, Formas Geométricas y Proyecciones de Medición

- **Canal Paralelo**: Permite trazar un canal de tendencia estándar definiendo dos puntos extremos de directriz y un tercer punto para establecer el ancho del canal^31^.
- **Canal de Regresión Lineal**: Dibuja un canal basado en un cálculo estadístico de mínimos cuadrados sobre la muestra de precios del rango seleccionado, incluyendo las líneas de desviación estándar para mapear zonas de sobreventa y sobrecompra^31^.
- **Fib Channel**: Un canal paralelo clásico cuyas divisiones internas se proyectan de manera automática según los ratios de Fibonacci^31^.
- **Formas Geométricas**: Incluye rectángulos, elipses, triángulos y arcos para delimitar zonas de consolidación y niveles críticos de soporte y resistencia^31^.
- **Long/Short Position Tools (Proyecciones de Medición)**: Permiten gestionar el riesgo simulando órdenes de entrada de forma visual en el gráfico^31^. El sistema calcula de manera automática los siguientes parámetros contables^48^:

3. Indicadores Integrados (Built-in) y Análisis Confluente sin Código

La plataforma incluye más de 200 indicadores integrados que se calculan de manera nativa sin necesidad de editar código Pine Script^49^. Estos indicadores se organizan en categorías funcionales como tendencia, momentum, volatilidad, volumen, osciladores y análisis de datos fundamentales de la empresa^49^.

Los 20 Indicadores Nativos Más Populares

| **Indicador** | **Categoría** | **Configuración Óptima** | **Componentes Críticos de Análisis** | **Señal Operativa Principal** |
| --- | --- | --- | --- | --- |
| **RSI**<br>[cite: 51] | Oscilador^50^ | 14 periodos, Cierre^51^ | Líneas de control en niveles 70 y 30^52^. | Divergencia clásica alcista o bajista frente al precio^52^. |
| **MACD**<br>[cite: 51] | Tendencia^49^ | 12, 26, 9 (Cierre)^51^ | Líneas MACD, de Señal e Histograma | Cruce de la línea MACD sobre la de Señal e inversión de histograma. |
| **Bollinger Bands**<br>[cite: 49] | Volatilidad^49^ | 20 periodos, 2 Desviaciones | Media móvil central, bandas superior e inferior | Compresión de bandas (Squeeze) que anticipa expansión de volatilidad. |
| **ATR**<br>[cite: 53] | Volatilidad^49^ | 14 periodos | Valor absoluto medido en ticks o divisa^7^ | Definición técnica para colocación de stop loss dinámicos^53^. |
| **Ichimoku Cloud**<br>[cite: 54] | Tendencia^49^ | 9, 26, 52, 26 | Senkou Span A/B (nube), Tenkan-sen, Kijun-sen^54^. | Soporte dinámico definido por la nube y cruce de Tenkan/Kijun^54^. |
| **Stochastic**<br>[cite: 54] | Oscilador^49^ | 14, 3, 3 | Curvas %K y %D, niveles extremos 80/20^54^. | Cruce de líneas en zonas extremas de sobrecompra o sobreventa^54^. |
| **EMA**<br>[cite: 39] | Tendencia^49^ | 9, 21, 200 periodos | Ponderación exponencial de cierre | Soporte dinámico y cruces rápidos de corto y mediano plazo^39^. |
| **SMA**<br>[cite: 49] | Tendencia^49^ | 50, 200 periodos | Media aritmética simple de cierre | Identificación del sesgo tendencial de largo plazo. |
| **VWAP**<br>[cite: 31] | Volumen^49^ | Sesión Diaria | Precio ponderado según volumen diario acumulado | Valor de referencia institucional para detectar compras justas de la sesión. |
| **ADX**<br>[cite: 54] | Tendencia^49^ | 14 periodos | Curva ADX, líneas +DI y -DI^54^. | ADX  confirma tendencia fuerte; cruce de líneas +DI/-DI da dirección^54^. |
| **Supertrend** | Tendencia^49^ | 10 ATR, Multiplicador 3 | Línea de tendencia de volatilidad dinámica | Cambio de color y sentido como señal automatizada de entrada/salida. |
| **Parabolic SAR** | Tendencia^49^ | 0.02, 0.02, 0.2 | Puntos dinámicos de aceleración | Giro de los puntos para stop de arrastre (trailing stop loss). |
| **Awesome Osc.**<br>[cite: 54] | Oscilador^49^ | 5, 34 periodos | Histograma de diferencia de puntos medios | Patrón de platillo (Saucer) y cruce sobre la línea de cero^51^. |
| **CCI**<br>[cite: 51] | Oscilador^49^ | 20 periodos | Medición de desviación estándar del precio típico | Entrada o salida de los límites de ^51^. |
| **Stoch RSI**<br>[cite: 49] | Oscilador^49^ | 14, 14, 3, 3 | Aplicación estocástica a la curva RSI^51^. | Extremos rápidos de momento en tendencias fuertes^54^. |
| **Williams %R**<br>[cite: 54] | Oscilador^49^ | 14 periodos | Relación del cierre con su máximo-mínimo | Identificación de zonas de rebote cerca de bandas límite^51^. |
| **Chaikin M.F.** | Volumen^49^ | 20 periodos | Flujo acumulado de volumen alcista o bajista | Acumulación institucional por encima de la línea neutra. |
| **Keltner Chan.**<br>[cite: 49] | Volatilidad^49^ | 20 EMA, 2 ATR | Bandas construidas a partir de la volatilidad real | Operativa de ruptura de volatilidad y reversión a la media. |
| **Donchian Chan.** | Volatilidad^49^ | 20 periodos | Canales de máximos y mínimos de  periodos | Estrategia clásica de rupturas de rango (Turtle Trading). |
| **Bull Bear Power**<br>[cite: 54] | Oscilador^49^ | 13 periodos | Medición de fuerza de compradores/vendedores | Divergencias de fuerza interna del precio frente a la tendencia^54^. |

Indicadores Exclusivos de la Plataforma

- **Technical Ratings (Clasificación Técnica)**: Este indicador procesa simultáneamente múltiples medias móviles (médias exponenciales, simples, Ichimoku, Hull) y osciladores de momento (RSI, estocástico, MACD, Williams %R, etc.)^51^. Emite una lectura de confluencia matemática que oscila entre un valor estricto de  y ^54^. El sistema asigna categorías como Compra Fuerte (), Compra (de  a ), Neutral (de  a ), Venta (de  a ) y Venta Fuerte ()^51^.
- **Auto Pitchfork**: Un indicador inteligente que analiza de forma automatizada las oscilaciones de precios anteriores mediante un algoritmo de profundidad (depth) parametrizable para trazar el tridente óptimo en pantalla sin necesidad de colocar los puntos de forma manual^41^.
- **TPO Profile (Time Price Opportunity)**: Disponible para usuarios de planes de nivel Premium o superior^56^. Traza perfiles horizontales compuestos por letras individuales asociadas a intervalos de tiempo definidos por el usuario (desde 5 minutos hasta 4 horas)^56^. Permite visualizar la distribución temporal del valor e identificar niveles estructurales clave como el punto de control extendido (POC), el área de valor del 70% (VAH y VAL), impresiones individuales (single prints) e ineficiencias de subasta (poor high/low)^56^.

Combinación de Indicadores Nativos sin Código

La interfaz gráfica permite crear complejos entornos multi-indicador de forma totalmente visual:

- **Súper-Indicadores (Drag and Drop)**: El analista puede arrastrar un indicador del gráfico (como el RSI) y soltarlo directamente sobre otro indicador activo en un panel inferior (como el Estocástico) para consolidar sus curvas en una sola ventana y analizar confluencias de momento.
- **Ruteo de Datos (Source Inputs)**: En la configuración de propiedades del indicador que se desea superponer, la pestaña de "Inputs" (Datos de entrada) permite cambiar la fuente estándar del precio (como el precio de cierre del activo) para que utilice de forma directa la serie de datos calculada por el otro indicador activo. Por ejemplo, es posible calcular de forma visual una media exponencial (EMA) utilizando como datos de entrada la línea del indicador de volumen dinámico Chaikin Money Flow, en lugar de la cotización tradicional del precio del activo^31^.

4. Watchlists y Gestión Profesional de Activos

El módulo de watchlists (listas de seguimiento) de TradingView está diseñado para monitorizar, filtrar y categorizar grandes conjuntos de activos financieros de manera estructurada^59^.

Creación, Estructuración y Organización Avanzada

- **Organización por Secciones**: Los usuarios pueden insertar divisores visuales de texto dentro de una misma lista para segmentar los activos por categorías o tipos de configuración técnica sin necesidad de crear listas independientes.
- **Columnas de Datos**: Es posible configurar la tabla de seguimiento añadiendo columnas con métricas de rendimiento clave como: Último precio, Cambio neto absoluto, Cambio porcentual, Volumen de negociación y Capitalización bursátil.
- **Sincronización de Entorno**: Las listas se guardan en los servidores de la plataforma, actualizándose de forma inmediata en el cliente web, la versión móvil y la aplicación de escritorio nativa^31^.

Importación y Exportación de Listas

- **Exportación de Listas**: El sistema permite guardar cualquier lista de seguimiento activa como un archivo de texto plano (.txt) con los códigos de tickers separados por comas.
- **Importación de Listas**: Admite la carga masiva de tickers mediante archivos formateados, facilitando el trasvase de watchlists complejas generadas desde hojas de cálculo o bases de datos externas de screening de mercado.

Listas Predefinidas de la Comunidad y del Sistema

TradingView proporciona accesos inmediatos a listas indexadas oficiales que se actualizan de forma automática en tiempo real:

- Componentes oficiales del S&P 500 y NASDAQ 100^61^.
- Criptomonedas ordenadas por capitalización total de mercado^61^.
- Líderes de volumen de negociación de la jornada bursátil diaria^61^.

Clasificación Visual por Colores (Coloring Condicional)

TradingView permite el etiquetado rápido de activos mediante banderas de siete colores distintos (rojo, naranja, amarillo, verde, azul, morado, rosa)^59^. El analista puede utilizar el atajo de teclado rápido Alt + Enter para marcar o desmarcar rápidamente un activo seleccionado con la bandera activa actual^59^. Esto permite crear una "watchlist condicional" temporal donde se recopilan instantáneamente todos los activos que presentan un patrón técnico inminente o de alta probabilidad.

Generación de Alertas Directas desde Watchlists

Haciendo clic derecho sobre cualquier activo listado en el panel, la interfaz despliega un menú contextual rápido para configurar alertas específicas sobre dicho símbolo en un solo paso, eliminando la necesidad de abrir previamente el gráfico correspondiente.

5. Stock Screener Nativo (Filtros y Cribado Multimercado)

El Screener de TradingView es un motor de búsqueda cuantitativa multimercado que procesa simultáneamente miles de cotizaciones bajo tres grandes capas de filtrado lógico^49^.

Capas de Filtrado Lógico

- **Filtros Descriptivos**: Permiten filtrar activos según su país de cotización, mercado de intercambio oficial (NYSE, NASDAQ, AMEX), sector e industria, tipo de valor (acciones ordinarias, preferentes, certificados de depósito) o moneda de cotización^49^.
- **Filtros Técnicos**: Evalúan indicadores dinámicos en múltiples escalas de tiempo^49^. El motor de TradingView permite filtrar activos según cruces específicos de medias móviles, lecturas extremas de osciladores de momento (por ejemplo, RSI inferior a 30) o por patrones de velas japonesas identificados automáticamente por la plataforma en el último cierre de barra^49^.
- **Filtros Fundamentales**: Ofrecen acceso a métricas extraídas directamente de los informes financieros oficiales^49^: ratios de valoración (P/E, P/B, EV/EBITDA), rentabilidad por dividendo (dividend yield), crecimiento histórico de ingresos, márgenes operativos y de beneficio neto, niveles de apalancamiento financiero y calificaciones de analistas institucionales^49^.

Diferencias Clave de Campos por Tipo de Activo

Debido a la naturaleza dispar de los mercados financieros mundiales, el motor del screener segmenta la base de datos aplicando campos lógicos exclusivos según la naturaleza del activo^50^:

| **Mercado de Cribado** | **Campos de Filtrado Exclusivos** | **Métricas Críticas Incorporadas** | **Aplicación Analítica** |
| --- | --- | --- | --- |
| **Acciones (Stock Screener)**<br>[cite: 50] | Declaraciones contables TTM, Trimestrales, Anuales e IFRS/GAAP^49^. | Dividendos, EPS, Márgenes operativos, Ratios de valoración (P/E, EV/EBITDA)^49^. | Análisis de valor y selección de empresas sólidas para carteras de inversión^49^. |
| **Forex Screener**<br>[cite: 64] | Parámetros específicos de liquidez bancaria interbancaria. | Swaps alcistas/bajistas, correlaciones entre divisas, diferenciales Bid/Ask^64^. | Identificación de pares con mejores condiciones operativas y estrategias de carry trade. |
| **Crypto Coins Screener**<br>[cite: 50] | Métricas de finanzas descentralizadas, tokens y pares CEX/DEX^50^. | Capitalización de mercado total, volumen por exchanges, tipo de protocolo de blockchain^50^. | Cribado rápido de criptoactivos según su liquidez y el tipo de tecnología blockchain subyacente. |

Funcionalidad de Filtro por Inteligencia Artificial (AI Filter)

Exclusivo para planes Ultimate de la plataforma, TradingView incorpora un filtro impulsado por modelos de lenguaje en procesamiento de lenguaje natural (en fase beta pública)^65^. El analista puede introducir prompts estructurados en el campo de texto (por ejemplo: *"show the companies in India with the highest market cap"*)^65^. El sistema traduce de manera instantánea el lenguaje natural en los correspondientes filtros lógicos descriptivos, técnicos o fundamentales sobre la base de datos de mercado^65^.

Exportación y Sincronización Temporal

- El sistema permite guardar y nombrar configuraciones lógicas de filtros personalizadas (Screens) para cargarlas de manera instantánea^49^.
- Los resultados de cualquier cribado de mercado pueden exportarse de forma nativa a archivos en formato de hoja de cálculo .csv^50^.
- La tabla de datos puede configurarse para actualizarse de manera dinámica en tiempo real (refresco cada 10 segundos o 1 minuto) o bajo demanda estática (Snapshot) para análisis sin fluctuaciones de precio momentáneas^49^.

6. Mapa de Calor (Heatmaps) de Mercado

Los mapas de calor ofrecen una representación visual bidimensional de los mercados financieros mediante rectángulos proporcionales cuya área y color sintetizan las dinámicas de capital y rendimiento sectorial en un solo vistazo^1^.

Estructuración de Stock y Crypto Heatmaps

TradingView ofrece dos mapas de calor integrados:

- **Mapa de Acciones (Stock Heatmap)**: Organiza las acciones en bloques de sectores industriales y subcategorías de actividad de acuerdo con las clasificaciones oficiales del mercado global^1^.
- **Mapa de Criptomonedas (Crypto Heatmap)**: Agrupa los criptoactivos en base a su arquitectura de blockchain (como capa 1, DeFi, monedas estables, oráculos, tokens de utilidad o de gobernanza)^64^.

Métricas de Proporción Espacial (Tamaño)

El tamaño físico de cada bloque rectangular representa el peso de un activo en relación con el conjunto de datos analizado^1^:

- **Capitalización de Mercado (Market Cap)**: Es el parámetro predeterminado, donde las grandes compañías tecnológicas dominan de forma visual el espacio de la cuadrícula^1^.
- **Volumen de Negociación de la Sesión**: Redimensiona el mapa para destacar activos de mediana o baja capitalización que están registrando una actividad comercial inusualmente elevada en la sesión actual.

Métricas de Distribución de Color

La intensidad del color (gradiente continuo entre verde brillante, negro y rojo brillante) indica la variación cuantitativa del parámetro seleccionado para el análisis^1^:

- **Rendimiento Porcentual Diario (% Change)**: Evaluaciones del rendimiento de corto plazo.
- **Rendimiento en el Año Corriente (YTD - Year to Date)**: Permite identificar de forma inmediata la rotación de capital a largo plazo e de las industrias líderes o rezagadas del año^64^.
- **Volumen Relativo (Relative Volume)**: Destaca visualmente en tonos verdes los activos que cotizan con un volumen de negociación sustancialmente superior a su promedio de los últimos 10 días^49^.

7. Multi-Chart Layouts (Diseños Multigráfico y Espacios de Trabajo)

Para la monitorización simultánea de múltiples activos o marcos temporales, TradingView proporciona un potente motor de estructuración gráfica dentro de un único espacio de trabajo^59^.

Estructura de Cuadrículas y Gestión de Layouts

- **Configuración de Cuadrículas**: Soporta layouts de hasta 2, 4, 8 y, en configuraciones profesionales de escritorio, hasta 16 gráficos independientes en una única ventana de navegador o aplicación.
- **Sincronización Selectiva de Atributos**: El analista puede activar o desactivar la sincronización entre los paneles del layout según las necesidades analíticas utilizando cuatro variables principales de control:

- **Símbolo**: Todos los paneles se actualizan de forma inmediata al mismo activo al cambiar el ticker en cualquiera de ellos^31^.
- **Intervalo**: Unifica los marcos temporales de visualización de todos los gráficos del diseño.
- **Mira (Crosshair)**: Sincroniza la posición de visualización del puntero en el eje de precios y tiempo en todas las pantallas de forma simultánea^59^.
- **Tiempo**: Iguala el desplazamiento de la línea de tiempo histórica para realizar análisis retrospectivos paralelos en múltiples activos.

TradingView Desktop: Workspaces y Múltiples Monitores

La versión nativa para sistemas operativos de escritorio eleva la gestión del entorno de visualización:

- **Pestañas Multigráfico**: Permite arrastrar y desprender pestañas fuera de la ventana principal para distribuirlas de forma nativa en múltiples monitores físicos^31^.
- **Persistencia de Datos**: Al cerrar la aplicación, TradingView guarda en caché local la disposición exacta, las pestañas abiertas y la distribución de pantallas para restaurarlas exactamente al reiniciar el sistema sin pérdida de configuraciones técnicas o dibujos activos^60^.

8. Modo Reproducción (Bar Replay) como Simulador Retrospectivo

El simulador de mercado nativo (*Bar Replay*) permite ocultar el comportamiento histórico del precio a partir de un punto temporal seleccionado para reproducir la formación de velas de forma controlada^8^.

Funcionamiento y Parámetros Operativos

- **Punto de Inicio**: Al activar la herramienta, el usuario desplaza un cursor rojo vertical sobre el gráfico para eliminar de forma visual la acción de precio posterior a dicha vela.
- **Velocidad de Reproducción**: Permite configurar la velocidad de avance automático de las velas, desde 1 barra por segundo hasta velocidades aceleradas de hasta 15 barras por segundo.
- **Control Manual Paso a Paso**: Utilizando el atajo de teclado rápido Shift + Flecha Derecha, el usuario puede avanzar la simulación vela a vela para validar manualmente la validez de los setups y análisis técnicos planteados^59^.

Limitaciones de Uso e Histórico de Datos

- **Soporte de Gráficos Especiales**: La reproducción de barras no es compatible con los gráficos de tipo Range^8^.
- **Profundidad del Histórico**: Depende del plan de suscripción del usuario. Al bajar a temporalidades intradiarias de alta granularidad (por ejemplo, gráficos de 1 minuto), la reproducción de barras está limitada por el número máximo de barras históricas disponibles guardadas en los servidores de la plataforma.
- **Diferencia frente al Forward Testing en Tiempo Real**: El Bar Replay no simula de forma dinámica el impacto de las variaciones del diferencial de precios (spread) en tiempo real, la cola de ejecución del libro de órdenes ni el factor emocional inherente al mercado real. Su principal valor radica en la validación estadística de las reglas técnicas de una estrategia sin verse afectado por el sesgo de confirmación visual del histórico futuro.

9. Paper Trading: Configuración y Operativa Dinámica de Simulación

TradingView integra una cuenta de simulación virtual completa que permite operar los mercados mundiales con datos en tiempo real de forma segura y sin arriesgar capital real^66^.

Activación, Configuración de Capital y Gestión de Órdenes

- **Activación**: Se habilita en la barra inferior de herramientas conectando el broker ficticio nativo "Paper Trading"^66^. El usuario puede restablecer el saldo nominal de la cuenta virtual en cualquier momento y configurar el nivel de apalancamiento inicial permitido.
- **Tipos de Órdenes Soportadas**:

- **Market (Mercado)**: Ejecución inmediata al mejor precio disponible en el libro de órdenes^66^. Solo requiere especificar el tamaño de la posición^68^.
- **Limit (Límite)**: Orden condicional de precio que se coloca en el libro y se ejecuta únicamente si el mercado alcanza la cotización establecida o una mejor^68^.
- **Stop-Market**: Orden de stop que se activa cuando el precio toca el nivel de activación definido, convirtiéndose inmediatamente en una orden de mercado para limitar pérdidas o entrar en rupturas^66^.
- **Stop-Limit**: Requiere definir un precio de disparo (trigger price) y un límite de ejecución estricto para evitar deslizamientos severos en mercados de alta volatilidad^68^.

Órdenes de Salida Complejas (Bracket Orders)

TradingView permite asociar órdenes defensivas de manera simultánea en el momento de configurar la orden principal de entrada^53^:

- **Take Profit (Toma de Beneficios)** e **Stop Loss (Límitación de Pérdida)** dinámicas especificadas en valor absoluto de precio, porcentaje, ticks o volumen monetario neto de divisa de la cuenta^48^.
- **Nivel de Salida Múltiple (Exits Escalonados)**: En el Paper Trading, se pueden añadir hasta 4 pares de salidas escalonadas^70^. Cada salida vincula una orden bracket completa (SL y TP) asociada a un porcentaje determinado del volumen total de la posición abierta^53^.

┌──► Take Profit 1 (25% Qty) @ Target A

               ┌──► Expiración 1 ─────┼──► Stop Loss 1 (25% Qty) @ Stop A

               │                      └──► Vinculadas mediante OCA (One Cancels All)

               │

Posición ─────┼──► Expiración 2 ─────┬──► Take Profit 2 (75% Qty) @ Target B

(100% Qty)     │                      └──► Stop Loss 2 (75% Qty) @ Stop B

               └──────────────────────┴──► Si se cancela un SL, su par TP asociado se elimina

- **Trailing Stop Loss**: Órdenes de stop de pérdida dinámicas que acompañan la cotización del precio únicamente en la dirección de la rentabilidad para proteger los beneficios flotantes logrados en la posición^53^.

Seguimiento de Portafolio y Limitaciones Realistas de Simulación

El panel de operaciones inferior resume de manera estructurada las posiciones abiertas, el balance contable líquido, el P&L flotante y el historial de transacciones^67^.

- **Realismo de los Fills (Relleno de Órdenes)**: Las órdenes limitadas en Paper Trading se ejecutan asumiendo una liquidez ideal instantánea tan pronto como el precio toca el nivel objetivo de cotización en el feed del precio.
- **Limitaciones**: No simula de manera fidedigna el impacto en el mercado real de órdenes de gran tamaño, ni el deslizamiento de precios (slippage) real en activos de baja liquidez, ni la probabilidad de no ejecución de órdenes limitadas que se encuentran al final de la cola del libro de órdenes real^68^.

10. Depth of Market (DOM) y Order Book (Libro de Órdenes)

El panel nativo DOM (*Depth of Market*), también conocido como la "escalera de precios" o "libro de órdenes", provee una visión de la microestructura del mercado para activos negociados de forma centralizada^67^.

Exchanges y Brokers Soportados

El DOM se activa únicamente cuando el usuario se conecta a través de un bróker que proporciona flujos de datos estructurados de Nivel 2 directos del mercado (como Interactive Brokers, Tradovate, CQG o brokers asociados de Forex y criptomonedas regulados)^67^.

Estructura de la Interfaz del DOM

- **Visualización de Asks / Bids**: Presenta una escala vertical de precios centralizada. A la izquierda se listan las órdenes de compra pendientes (*Bids*) y a la derecha las órdenes de venta pendientes de ejecución (*Asks*)^67^.
- **Ajuste del Incremento de Precio (Price Step)**: Para activos con un tamaño de tick mínimo extremadamente pequeño, el menú superior del DOM permite consolidar la escala de cotizaciones en pasos o incrementos de mayor tamaño, facilitando la lectura de la liquidez concentrada institucional sin dispersión^71^.
- **Time & Sales (Tiempo y Ventas)**: Tabla dinámica integrada que registra cronológicamente cada transacción ejecutada en el mercado en tiempo real, especificando la hora exacta de la operación, el volumen exacto intercambiado y el sentido alcista o bajista de la cotización final de ejecución.
- **Operativa en Scalping**: Permite colocar órdenes de compra o venta a mercado de forma rápida con los botones "Comprar a mercado" o "Vender a mercado"^67^. Las órdenes limitadas pueden colocarse de forma directa haciendo clic izquierdo sobre la celda de precio de la columna correspondiente del DOM (columna izquierda para comprar y derecha para vender)^67^. Al mantener presionada la tecla Ctrl en Windows o Cmd en macOS y hacer clic sobre una celda, se introduce automáticamente una orden de tipo Stop^67^.

11. Calendario Económico y Datos Fundamentales Integrados

TradingView ofrece un panel de información macroeconómica y empresarial integrado que complementa el análisis de acción del precio con variables cuantitativas del contexto de los fundamentales^1^.

Calendario Económico de Eventos y Filtros de Impacto

- **Calendario Macroeconómico**: Registra de forma cronológica la publicación de datos económicos de los principales países del mundo^1^.
- **Filtros Avanzados**: Permite clasificar los eventos por su nivel de importancia (alto, medio, bajo impacto esperado sobre la volatilidad) y por zona geográfica de interés^1^. Presenta el valor histórico previo de la métrica, la previsión promedio de consenso de los analistas y el dato real publicado finalmente por los organismos oficiales.

Earnings Calendar e Históricos de Rendimiento

- **Calendario de Ganancias**: Mapea las fechas programadas de publicación de informes corporativos trimestrales de dividendos y resultados de beneficios de las empresas cotizadas^1^.
- **Visualización en Gráfico**: Al producirse la publicación de resultados, la interfaz muestra de forma nativa en la parte inferior del gráfico iconos circulares interactivos con la letra "E" (Earnings) o "D" (Dividends)^1^. Al pasar el puntero por encima de ellos, la plataforma despliega gráficos comparativos interactivos de barras que contrastan el beneficio por acción (EPS) estimado frente al real y los ingresos estimados frente a los reales obtenidos^1^.

Mapeo de Datos Fundamentales en Pantalla

A través de la sección de indicadores de tipo "Fundamentales", el analista puede añadir gráficos de series temporales de datos contables directamente en paneles inferiores del gráfico^1^. Esto permite realizar análisis de correlación visual histórica frente al precio de la acción de métricas complejas como:

- Ratio de Precio sobre Beneficios (P/E Ratio) e Ingresos Totales^1^.
- Flujo de Caja Libre (Free Cash Flow Margin)^49^.
- Deuda Neta sobre EBITDA o Márgenes de Rentabilidad de Activos (ROE, ROIC)^49^.

12. Pine Editor (IDE Integrado) como Entorno de Gestión Visual

El Pine Editor presente en la barra inferior de TradingView constituye una interfaz de desarrollo integrado (IDE) con potentes características de gestión visual y analítica^50^.

Características de la Interfaz Visual del IDE

- **Resaltado de Sintaxis (Syntax Highlighting) e Inteligencia de Código**: Facilita la lectura de scripts complejos mediante la coloración por código de las diferentes variables lógicas, funciones integradas de cálculo del precio e instrucciones de control^59^.
- **Autocompletado de Código y Snippets**: Ofrece sugerencias en tiempo real de funciones y variables de sistema nativas a medida que se escribe en el editor, acelerando el proceso de desarrollo^59^.
- **Consola de Errores e Historial de Revisiones**: Panel de advertencias en la parte inferior que destaca de forma inmediata la existencia de incompatibilidades de versión de scripts de la comunidad o código roto al intentar añadirlos al gráfico activo^59^.
- **Gestión de Publicación y Licencias**: Permite al analista publicar de manera gráfica sus propios indicadores o estrategias en la biblioteca comunitaria global^1^. El sistema ofrece tres opciones de publicación directa:

- **Publicación Abierta**: El código fuente es completamente visible y almacenable por cualquier miembro de la plataforma.
- **Publicación Protegida**: El indicador es ejecutable en los gráficos de cualquier usuario de la comunidad, pero su código fuente permanece cifrado y oculto al público.
- **Publicación por Invitación (Invite-Only)**: El autor gestiona de manera directa desde su perfil los permisos individuales de uso a cuentas de terceros de forma temporal o indefinida.

13. Catálogo de Atajos de Teclado (Hotkeys) y Personalización

Para optimizar el flujo de trabajo y la velocidad de ejecución analítica en mercados rápidos, TradingView cuenta con un catálogo de atajos de teclado y opciones de personalización visual del espacio de trabajo^59^.

Catálogo de Atajos de Teclado (Hotkeys) Nativos

Navegación e Interacción del Gráfico

| **Atajo de Teclado (Windows/Linux)** | **Atajo de Teclado (macOS)** | **Acción Ejecutada por la Interfaz** |
| --- | --- | --- |
| Cualquier número o letra<br>[cite: 59] | Cualquier número o letra | Abre la barra de búsqueda rápida de símbolos (Ticker Search)^72^. |
| Alt + G<br>[cite: 72, 73] | ⌥ + G | Abre el buscador de fechas e intervalos temporales específicos^72^. |
| Alt + S<br>[cite: 59] | ⌥ + S | Captura la URL del gráfico activo en el portapapeles^59^. |
| Alt + Ctrl + S<br>[cite: 59] | ⌥ + ⌘ + S | Guarda la imagen física del layout gráfico en el disco duro local^59^. |
| Alt + P<br>[cite: 59] | ⌥ + P | Activa o desactiva la escala de precios porcentual^59^. |
| Alt + L<br>[cite: 59] | ⌥ + L | Cambiar la escala del eje de precios a representación logarítmica^59^. |
| Ctrl + Flecha Arriba<br>[cite: 59] | ⌘ + Flecha Arriba | Acercar el zum de la línea de tiempo (Zoom In)^59^. |
| Ctrl + Flecha Abajo<br>[cite: 59] | ⌘ + Flecha Abajo | Alejar el zum de la línea de tiempo (Zoom Out)^59^. |
| Alt + Shift + Flecha Izquierda<br>[cite: 59] | ⌥ + ⇧ + Flecha Izquierda | Desplaza el gráfico al inicio histórico de la serie temporal disponible^59^. |
| Alt + Shift + Flecha Derecha<br>[cite: 59] | ⌥ + ⇧ + Flecha Derecha | Desplaza el gráfico a la última barra en tiempo real cotizada^59^. |
| F1 o Ctrl + Shift + P<br>[cite: 59] | F1 o ⌘ + ⇧ + P | Abrir la paleta de comandos de búsqueda global de la plataforma^59^. |

Gestión de Dibujos y Elementos Gráficos

| **Atajo de Teclado (Windows/Linux)** | **Atajo de Teclado (macOS)** | **Acción Ejecutada por la Interfaz** |
| --- | --- | --- |
| Ctrl + Z<br>[cite: 31, 59] | ⌘ + Z | Deshacer la última acción de dibujo o modificación de la interfaz^31^. |
| Ctrl + Y<br>[cite: 59, 72, 73] | ⌘ + Y | Redo el último cambio de dibujo o configuración de parámetros^59^. |
| Ctrl + Alt + H<br>[cite: 59, 74] | ⌘ + ⌥ + H | Ocultar o mostrar todos los objetos de dibujo activos^59^. |
| Ctrl + C y Ctrl + V<br>[cite: 72, 73] | ⌘ + C y ⌘ + V | Copiar y pegar cualquier objeto de dibujo seleccionado en el layout^72^. |
| Ctrl + Arrastrar Ratón<br>[cite: 59] | ⌘ + Arrastrar Ratón | Clonar de manera rápida e instantánea cualquier línea o dibujo seleccionado^59^. |
| Mantener Shift<br>[cite: 59] | Mantener Shift | Forzar el trazado de líneas a ángulos rectos estrictos o de 45°^59^. |
| Mantener Ctrl<br>[cite: 31, 59] | Mantener ⌘ | Activar de forma temporal el modo imán (Magnet Mode) para anclar puntos a OHLC^31^. |
| Alt + F<br>[cite: 72, 73] | ⌥ + F | Seleccionar la herramienta de dibujo de rectángulo^72^. |
| Alt + Shift + R<br>[cite: 72, 73] | ⌥ + ⇧ + R | Seleccionar la herramienta de dibujo de cuadrado^72^. |

Gestión de Watchlist

| **Atajo de Teclado (Windows/Linux)** | **Atajo de Teclado (macOS)** | **Acción Ejecutada por la Interfaz** |
| --- | --- | --- |
| Shift + W<br>[cite: 59] | ⇧ + W | Cambia de manera secuencial a la siguiente lista de seguimiento^59^. |
| Arrow Down o Espacio<br>[cite: 59] | Arrow Down o Espacio | Cargar el siguiente símbolo guardado en la lista de seguimiento^59^. |
| Arrow Up o Shift + Espacio<br>[cite: 59] | Arrow Up o ⇧ + Espacio | Retroceder al símbolo previo de la lista de seguimiento activa^59^. |
| Alt + Enter<br>[cite: 59] | ⌥ + Enter | Colocar o quitar la bandera de color condicional activa al activo seleccionado^59^. |
| Alt + W<br>[cite: 59, 72, 73] | ⌥ + W | Añadir el símbolo cotizado actual directamente a la watchlist activa^59^. |

Operativa y DOM

| **Atajo de Teclado (Windows/Linux)** | **Atajo de Teclado (macOS)** | **Acción Ejecutada por la Interfaz** |
| --- | --- | --- |
| Shift + B<br>[cite: 69] | ⇧ + B | Abrir el panel de tickets de orden en sentido de compra (Buy)^69^. |
| Shift + S<br>[cite: 69] | ⇧ + S | Abrir el panel de tickets de orden en sentido de venta (Sell)^69^. |
| Shift + Alt + B<br>[cite: 59, 72, 73] | ⇧ + ⌥ + B | Colocar directamente una orden límite de compra a mercado en el DOM^59^. |
| Shift + Alt + S<br>[cite: 59, 72, 73] | ⇧ + ⌥ + S | Colocar directamente una orden límite de venta a mercado en el DOM^59^. |
| Shift + Alt + C<br>[cite: 72, 73] | ⇧ + ⌥ + C | Centrar verticalmente de manera instantánea el precio en la escalera del DOM^72^. |
| Alt + Ctrl<br>[cite: 59, 75] | ⌥ + ⌘ | Activar bajo el cursor el botón de orden rápida "+" en el eje de precios^59^. |

Aplicación de Escritorio (Desktop App)

| **Atajo de Teclado (Windows/Linux)** | **Atajo de Teclado (macOS)** | **Acción Ejecutada por la Aplicación** |
| --- | --- | --- |
| Ctrl + T<br>[cite: 60] | ⌘ + T | Abrir una nueva pestaña de navegación de forma rápida^60^. |
| Ctrl + N<br>[cite: 60] | ⌘ + N | Abrir una nueva ventana de visualización independiente de la app^60^. |
| Ctrl + W<br>[cite: 60] | ⌘ + W | Cerrar la pestaña de navegación activa del layout actual^60^. |
| Ctrl + Tab<br>[cite: 60] | Ctrl + Tab | Desplazarse a la pestaña de navegación derecha de la ventana^60^. |
| Ctrl + Shift + Tab<br>[cite: 60] | Ctrl + ⇧ + Tab | Desplazarse a la pestaña de navegación izquierda de la ventana^60^. |
| Ctrl + Número (1 a 8)<br>[cite: 60] | ⌘ + Número (1 a 8) | Seleccionar de forma directa la pestaña número  de la barra^60^. |
| Ctrl + 9<br>[cite: 60] | ⌘ + 9 | Seleccionar de forma automática la última pestaña de la derecha^60^. |
| Shift + Ctrl + T<br>[cite: 60] | Shift + Cmd + T | Recuperar de manera instantánea la última pestaña cerrada por error^60^. |
| Shift + Ctrl + Q<br>[cite: 60] | ⌘ + Q | Cerrar de forma completa la aplicación conservando el layout en caché^60^. |

Personalización del Workspace y Configuración del Tema

TradingView ofrece un panel de configuración de diseño que permite adaptar la representación gráfica y las escalas para una legibilidad óptima bajo cualquier condición de luz o tipo de monitor:

- **Tema de Color**: Alternancia de un solo clic entre el modo claro y el modo oscuro con ajuste automático del contraste de las fuentes de texto de las escalas de precio^60^.
- **Configuración del Gráfico de Símbolos**:

- **Cuerpo, Bordes y Mechas**: Modificación de la paleta de colores de cada elemento físico de las velas alcistas o bajistas para mejorar la comodidad visual^4^.
- **Línea de Último Precio y Línea de Cierre Previo**: Activa marcas visuales de trazado horizontal para monitorizar la brecha intradía frente a la sesión anterior^8^.

- **Gestión de Líneas de Cuadrícula**: Configuración de cuadrículas horizontales y verticales en el fondo del gráfico (opciones de patrón continuo, discontinuo o completamente transparentes para lograr un fondo de trabajo liso).
- **Marcas de Sesión (Session Breaks)**: Líneas verticales punteadas de control temporal que separan visualmente cada jornada de negociación diaria en activos de alta volatilidad.
- **Barra Flotante de Favoritos**: Al hacer clic en el icono de la estrella situado junto a cualquier herramienta de dibujo, esta se ancla de forma inmediata a una barra de herramientas flotante personalizable. Esta barra se puede desplazar por cualquier sección de la interfaz para acceder rápidamente a las herramientas favoritas, agilizando el flujo de trabajo sin necesidad de abrir menús laterales.

Fuentes citadas

- TradingView Features — Power Up Your Analysis & Trading, https://www.tradingview.com/features/
- Custom chart intervals — personalizing your analysis - TradingView, https://www.tradingview.com/support/solutions/43000543883-custom-chart-intervals-personalizing-your-analysis/
- Advanced intraday chart types - TradingView, https://www.tradingview.com/support/solutions/43000758617-advanced-intraday-chart-types/
- Hollow candle charts explained - TradingView, https://www.tradingview.com/support/solutions/43000745270-hollow-candle-charts-explained/
- Understanding Heikin Ashi charts - TradingView, https://www.tradingview.com/support/solutions/43000619436-understanding-heikin-ashi-charts/
- Understanding Renko charts - TradingView, https://www.tradingview.com/support/solutions/43000502284-understanding-renko-charts/
- Hiểu về biểu đồ phạm vi - TradingView, https://vn.tradingview.com/support/solutions/43000474007/
- 现在可以在TradingView上使用RANGE BARS！, https://www.tradingview.com/blog/cn/range-bars-now-available-tradingview-8078/
- Learn to use Kagi charts - TradingView, https://www.tradingview.com/support/solutions/43000502272-learn-to-use-kagi-charts/
- Learn to use Kagi charts - TradingView, https://th.tradingview.com/support/solutions/43000502272/
- What are point and figure charts - TradingView, https://www.tradingview.com/support/solutions/43000502276-what-are-point-and-figure-charts/
- Exclusive Scripts & Strategies by David_Linton - TradingView, https://www.tradingview.com/spaces/David_Linton/
- One Step Back Building for P&F Charts — TradingView Blog, https://www.tradingview.com/blog/en/a-new-way-to-build-1-box-p-f-charts-is-available-16018/
- Pine Script Language Reference Manual — TradingView, https://www.tradingview.com/pine-script-reference/v3/
- Introduction to line break charts - TradingView, https://th.tradingview.com/support/solutions/43000502273/
- ¡Las barras de rango ya están disponibles en TradingView!, https://www.tradingview.com/blog/es/range-bars-now-available-tradingview-8078/
- Understanding range charts - TradingView, https://www.tradingview.com/support/solutions/43000474007-understanding-range-charts/
- Gráfico do footprint de volume: um guia completo - TradingView, https://br.tradingview.com/support/solutions/43000726164/
- Wykresy Volume footprint: kompletny przewodnik - TradingView, https://pl.tradingview.com/support/solutions/43000726164/
- Volume profile indicators: basic concepts - TradingView, https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/
- Volume footprint charts: a complete guide - TradingView, https://www.tradingview.com/support/solutions/43000726164-volume-footprint-charts-a-complete-guide/
- Session volume profile charts explained - TradingView, https://www.tradingview.com/support/solutions/43000745275-session-volume-profile-charts-explained/
- S&P 500 Stocks Above 20-Day Average Ideas — INDEX:S5TW - TradingView, https://www.tradingview.com/symbols/INDEX-S5TW/ideas/
- Crypto Total Market Cap Excluding Top 10 Dominance, % Ideas — CRYPTOCAP:OTHERS.D - TradingView, https://www.tradingview.com/symbols/OTHERS.D/ideas/page-12/
- What are HLC area charts - TradingView, https://www.tradingview.com/support/solutions/43000709062-what-are-hlc-area-charts/
- New chart type — HLC area! - TradingView, https://www.tradingview.com/blog/en/new-chart-type-hlc-area-38579/
- Learn to use column charts - TradingView, https://www.tradingview.com/support/solutions/43000673912-learn-to-use-column-charts/
- What are high-low charts - TradingView, https://www.tradingview.com/support/solutions/43000677196-what-are-high-low-charts/
- New chart type — High-Low — TradingView Blog, https://www.tradingview.com/blog/en/new-chart-type-high-low-33180/
- Exclusive Scripts & Strategies by TradingFinder - TradingView, https://www.tradingview.com/spaces/TradingFinder/
- Drawing tools available on TradingView, https://www.tradingview.com/support/solutions/43000703396-drawing-tools-available-on-tradingview/
- Extend Pitchforks, Fibonacci Retracements, and More - TradingView, https://www.tradingview.com/blog/en/extend-pitchforks-fibonacci-retracements-and-more-17768/
- Gann fan drawing tool - TradingView, https://th.tradingview.com/support/solutions/43000518151/
- Gann Fan - TradingView, https://de.tradingview.com/support/solutions/43000518151/
- Gann box drawing tool - TradingView, https://www.tradingview.com/support/solutions/43000518152-gann-box-drawing-tool/
- Gann square drawing tool - TradingView, https://www.tradingview.com/support/solutions/43000518149-gann-square-drawing-tool/
- Gann Square - TradingView, https://de.tradingview.com/support/solutions/43000518149/
- 江恩箱(Gann Box) - TradingView, https://tw.tradingview.com/support/solutions/43000518152/
- SpaceX stock analysis after IPO - TradingView, https://www.tradingview.com/news/forexlive:620ae7af2094b:0-spacex-stock-analysis-after-ipo/
- Pitchfork drawing tool - TradingView, https://www.tradingview.com/support/solutions/43000518141-pitchfork-drawing-tool/
- Auto Pitchfork - TradingView, https://www.tradingview.com/support/solutions/43000657911-auto-pitchfork/
- Inside pitchfork drawing tool - TradingView, https://www.tradingview.com/support/solutions/43000518146-inside-pitchfork-drawing-tool/
- XABCD pattern drawing tool - TradingView, https://www.tradingview.com/support/solutions/43000569909-xabcd-pattern-drawing-tool/
- GMT / TetherUS PERPETUAL CONTRACT Trade Ideas, https://www.tradingview.com/symbols/GMTUSDT.P/ideas/page-42/
- ZEC3xLong/Tether Trade Ideas — GATE:ZECUSDT.3L, https://www.tradingview.com/symbols/ZECUSDT.3L/ideas/page-37/
- Kava / TetherUS PERPETUAL CONTRACT Trade Ideas — BINANCE:KAVAUSDT.P, https://www.tradingview.com/symbols/KAVAUSDT.P/ideas/page-22/
- Script e strategie esclusive di Trendoscope - TradingView, https://it.tradingview.com/spaces/Trendoscope/
- How to use long and short position drawing tools - TradingView, https://www.tradingview.com/support/solutions/43000475660-how-to-use-long-and-short-position-drawing-tools/
- TradingView Stock Screener: trade smarter, not harder, https://th.tradingview.com/support/solutions/43000718866/
- TradingView screeners walkthrough, https://www.tradingview.com/support/solutions/43000718885-tradingview-screeners-walkthrough/
- What do the ratings in the Screener mean? - TradingView, https://www.tradingview.com/support/solutions/43000475547-what-do-the-ratings-in-the-screener-mean/
- BSE Sensex Index Ideas — BSE:SENSEX — TradingView — India, https://in.tradingview.com/symbols/BSE-SENSEX/ideas/page-28/
- Strategies - TradingView, https://www.tradingview.com/pine-script-docs/faq/strategies/
- Technical Ratings - TradingView, https://www.tradingview.com/support/solutions/43000614331-technical-ratings/
- Technical Ratings - TradingView, https://br.tradingview.com/support/solutions/43000614331/
- New indicator available — Time Price Opportunity (TPO) - TradingView, https://www.tradingview.com/blog/en/new-indicator-time-price-opportunities-43010/
- Time Price Opportunity (TPO) — now a chart type - TradingView, https://www.tradingview.com/blog/en/time-price-opportunity-chart-type-43965/
- Time price opportunity (TPO) indicator - TradingView, https://www.tradingview.com/support/solutions/43000713306-time-price-opportunity-tpo-indicator/
- TradingView Keyboard Shortcuts — Hotkey List, https://in.tradingview.com/support/shortcuts/
- Desktop app keyboard shortcuts - TradingView, https://www.tradingview.com/support/solutions/43000623399-desktop-app-keyboard-shortcuts/
- TradingView — Track All Markets, https://www.tradingview.com/
- How to invest in stocks - TradingView, https://es.tradingview.com/support/solutions/43000788754/
- TradingView Bond Screener: simplify your fixed-income research, https://www.tradingview.com/support/solutions/43000743951-tradingview-bond-screener-simplify-your-fixed-income-research/
- Advanced Chart: Widget Code & Settings - TradingView, https://www.tradingview.com/widget-docs/widgets/charts/advanced-chart/
- How to use the AI Filter in Screener? - TradingView, https://fr.tradingview.com/support/solutions/43000785770/
- Mastering stop-market orders - TradingView, https://www.tradingview.com/support/solutions/43000754944-mastering-stop-market-orders/
- Profundidad de mercado (DOM): qué es y cómo pueden utilizarla los traders - TradingView, https://es.tradingview.com/support/solutions/43000516459/
- Types of orders: market, limit, stop - TradingView, https://www.tradingview.com/support/solutions/43000785102-types-of-orders-market-limit-stop/
- What is a limit order - TradingView, https://www.tradingview.com/support/solutions/43000754941-what-is-a-limit-order/
- Multiple take profit and stop loss levels - TradingView, https://www.tradingview.com/support/solutions/43000772334-multiple-take-profit-and-stop-loss-levels/
- How to use adjustable price step in DOM - TradingView, https://www.tradingview.com/support/solutions/43000765952-how-to-use-adjustable-price-step-in-dom/
- Keyboard shortcuts | Advanced Charts Documentation - TradingView, https://www.tradingview.com/charting-library-docs/latest/getting_started/Shortcuts
- Keyboard shortcuts | Advanced Charts Documentation - TradingView, https://www.tradingview.com/charting-library-docs/latest/configuration/Shortcuts/
- Faster and more convenient. We've added new hotkeys for working with charts! - TradingView, https://www.tradingview.com/blog/en/faster-and-more-convenient-hotkeys-for-working-with-charts-20914/
- Quick creation of orders, alerts, and price lines — TradingView Blog, https://www.tradingview.com/blog/en/new-hotkeys-on-the-chart-37650/