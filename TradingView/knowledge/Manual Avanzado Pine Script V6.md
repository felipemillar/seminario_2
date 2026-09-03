Manual Técnico de Visualización Avanzada y Dashboards en Pine Script v6

El motor de renderizado de TradingView ha experimentado una evolución fundamental con la llegada de Pine Script v6^1^. Esta versión transforma la manera en que los desarrolladores cuantitativos diseñan interfaces gráficas dentro del gráfico (*in-chart*), abstrayendo las limitaciones de memoria de versiones anteriores y desbloqueando capacidades dinámicas para construir consolas analíticas de nivel institucional^1^. El presente manual profundiza en los mecanismos del motor de visualización, detallando la implementación óptima de tablas, polilíneas, rellenos avanzados, gestión de recursos de memoria y la construcción de sistemas interactivos dinámicos de alto rendimiento.

1. El Sistema de Tablas Completo (table.new())

El sistema de tablas en Pine Script v6 representa la herramienta principal para el diseño de interfaces flotantes que permanecen fijas frente a las operaciones de escalado o desplazamiento del gráfico principal^4^. El motor procesa las tablas como coordenadas relativas al espacio visual de la pantalla (*viewport*), lo que las hace idóneas para albergar estadísticas de rendimiento, señales de múltiples marcos temporales (*multi-timeframe*) y datos consolidados del mercado^5^.

Declaración y Parámetros del Constructor

La instanciación de una tabla requiere el uso de la función table.new(), cuya firma detallada se compone de la siguiente forma:

Pine Script

table.new(position, columns, rows, bgcolor, frame_color, frame_width, border_color, border_width)

Las posiciones espaciales de la interfaz están definidas mediante constantes dentro del espacio de nombres position.*^6^. Se categorizan de acuerdo con la distribución bidimensional de la pantalla del usuario:

| **Constante de Posición** | **Ubicación en Pantalla (Viewport)** | **Coordenadas de Referencia** |
| --- | --- | --- |
| position.top_left | Esquina superior izquierda | Origen superior izquierdo |
| position.top_center | Centro del margen superior | Centrado horizontal superior |
| position.top_right | Esquina superior derecha | Origen superior derecho |
| position.middle_left | Alineado a la izquierda, centrado verticalmente | Centrado vertical izquierdo |
| position.middle_center | Centro absoluto de la pantalla | Centro geométrico bidimensional |
| position.middle_right | Alineado a la derecha, centrado verticalmente | Centrado vertical derecho |
| position.bottom_left | Esquina inferior izquierda | Origen inferior izquierdo |
| position.bottom_center | Centro del margen inferior | Centrado horizontal inferior |
| position.bottom_right | Esquina inferior derecha | Origen inferior derecho^6^ |

Escritura y Formateo Avanzado de Celdas (table.cell())

Para poblar las coordenadas bidimensionales de una tabla, se recurre a la función table.cell(). Pine Script v6 añade soporte nativo para el control tipográfico avanzado de puntos y estilos de texto^1^:

Pine Script

table.cell(table_id, column, row, text, width, height, text_color, bgcolor, text_halign, text_valign, text_size, text_font_family, tooltip, text_formatting)

- **text_size (Tipografía basada en puntos):** En versiones previas, los programadores estaban limitados a constantes de tamaño discretas como size.normal o size.large^1^. En v6, es posible definir tamaños exactos en puntos tipográficos pasando un entero (por ejemplo, text_size = 12), lo que proporciona un control preciso sobre la escala de las interfaces^1^.
- **text_font_family:** Permite alternar entre la fuente sans-serif por defecto de la plataforma (font.family_default) y una fuente monoespaciada (font.family_monospace), indispensable para mantener las columnas de cifras numéricas perfectamente alineadas^4^.
- **text_formatting (Estilos avanzados):** Permite enfatizar la jerarquía de los encabezados o señales mediante las constantes text.format_bold (negrita), text.format_italic (cursiva), o la combinación aritmética de ambas para lograr cursivas negritas: text.format_bold + text.format_italic^10^.
- **tooltip:** Permite adjuntar descripciones flotantes interactivas que se muestran cuando el usuario sitúa el cursor sobre una celda, evitando el hacinamiento de texto en pantallas pequeñas^12^. Las cadenas de tooltips admiten saltos de línea literales y una longitud máxima de hasta 40,960 caracteres^1^.

Combinación Dinámica de Celdas (table.merge_cells())

La estructuración de tablas complejas requiere a menudo la unificación de columnas para albergar encabezados generales o separadores de secciones^12^. Mediante la función table.merge_cells(), es posible fusionar un bloque rectangular especificando las coordenadas del extremo superior izquierdo al extremo inferior derecho^12^:

Pine Script

table.merge_cells(table_id, start_column, start_row, end_column, end_row)

Las celdas fusionadas asumen los parámetros estéticos y el texto de la celda origen en (start_column, start_row)^12^. El tamaño de la celda resultante se adapta automáticamente a las dimensiones de las filas y columnas adyacentes^12^.

Gestión de Memoria y Ciclo de Vida: table.delete() y table.clear()

La manipulación interactiva de dashboards exige mantener un control estricto sobre los objetos en ejecución para no saturar los límites de memoria locales.

- table.clear(table_id, start_col, start_row, end_col, end_row) vacía el contenido tipográfico y restablece el fondo de las celdas especificadas dentro de un área, manteniendo la estructura general de la tabla intacta^9^.
- table.delete(table_id) destruye el objeto por completo, liberando inmediatamente los recursos utilizados en el hilo de renderizado del lado del cliente^9^.

Rendimiento: Instanciación Estática (var) vs. Recreación por Barra

La inicialización de tablas es una operación costosa para el hilo de ejecución principal de Pine Script^16^. Recrear una tabla completa en cada barra histórica es una ineficiencia severa que puede provocar advertencias de rendimiento o exceder el tiempo de cálculo permitido^16^.

- **Patrón de Recreación Dinámica (Ineficiente):** Inicializar la tabla en cada barra histórica provoca miles de operaciones redundantes de asignación de memoria.
- **Patrón de Instanciación Única (Óptimo):** Declarar la tabla una sola vez utilizando la palabra clave var en el bloque global^6^. Posteriormente, las llamadas a table.cell() deben restringirse mediante condicionales de estado de barra (barstate.islastconfirmedhistory o barstate.isrealtime) para que la interfaz se actualice únicamente cuando sea estrictamente necesario^18^:

Pine Script

//@version=6

indicator("Optimized Table Example", overlay = true)

// Inicialización única de la tabla mediante la palabra clave var

var table my_table = table.new(position.top_right, 2, 2, bgcolor = color.new(color.black, 80))

// Actualización restringida a la última barra histórica y actualizaciones en tiempo real

if barstate.islastconfirmedhistory or barstate.isrealtime

    table.cell(my_table, 0, 0, "Métrica", text_color = color.white, text_size = 10, text_formatting = text.format_bold)

    table.cell(my_table, 1, 0, "Valor", text_color = color.white, text_size = 10, text_formatting = text.format_bold)

    table.cell(my_table, 0, 1, "Precio Cierre", text_color = color.gray, text_size = 10)

    table.cell(my_table, 1, 1, str.tostring(close, format.mintick), text_color = color.yellow, text_size = 10, text_formatting = text.format_bold)

2. Patrones de Dashboard Profesional

La combinación de la modularidad sintáctica de Pine Script v6 y la posibilidad de ejecutar llamadas multidimensionales dinámicas abre un nuevo abanico de posibilidades de arquitectura analítica dentro del gráfico^1^.

Dashboard Multi-Timeframe (MTF)

Con la habilitación de peticiones dinámicas en Pine Script v6, las llamadas a request.security() aceptan expresiones de tipo series string^1^. Esto permite iterar a través de estructuras de arrays para evaluar tendencias en múltiples temporalidades de forma estructurada sin necesidad de escribir bloques repetitivos en el código^1^.

Pine Script

// Patrón de iteración dinámico MTF

var string[] timeframes = array.from("5", "15", "60", "240", "D")

for tf in timeframes

    float close_tf = request.security(syminfo.tickerid, tf, close)

    // Procesamiento y asignación a celdas de la tabla correspondientes

Screener In-Chart Multi-Símbolo

El motor v6 permite realizar escaneos de múltiples activos directamente en la pantalla de visualización principal^18^. Es crucial utilizar el parámetro ignore_invalid_symbol = true en las peticiones de datos, asegurando que tickers delistados o errores tipográficos en las cadenas ingresadas por el usuario no detengan la ejecución del indicador completo ni generen errores en tiempo de ejecución^18^.

Pine Script

// Ejemplo conceptual de escaneo multi-símbolo tolerante a errores

var string[] tickers = array.from("NASDAQ:AAPL", "NASDAQ:MSFT", "NASDAQ:INVALID_TICKER", "NASDAQ:GOOGL")

for ticker in tickers

    float close_val = request.security(ticker, "D", close, ignore_invalid_symbol = true)

    // Si el ticker es inválido, close_val devolverá na, evitando la detención del script

Panel de Estadísticas de Estrategia en Tiempo Real

Para traders cuantitativos y de sistemas, consolidar métricas operativas sobre el rendimiento de las operaciones es indispensable. La incorporación de la variable strategy.closedtrades.first_index permite verificar la cantidad de registros históricos depurados automáticamente por el motor al superar el límite de transacciones, manteniendo un cálculo estable de métricas acumulativas como el factor de ganancia (*profit factor*), ratio de acierto (*win rate*) o el *drawdown* máximo directamente en la interfaz visual^2^.

Matrices NxN de Correlación Cruzada con Gradiente de Color

Las funciones analíticas tradicionales como ta.correlation() requieren consistencia histórica estricta, lo que imposibilita su llamada dentro de bucles dinámicos o condicionales locales, ya que su estado histórico se corrompería^23^. El patrón profesional para la resolución de matrices NxN de correlación requiere el desarrollo de algoritmos de correlación de Pearson sin estado (*stateless*), que procesen datos pre-almacenados dinámicamente en estructuras de arrays de tamaño fijo^24^:

Este cálculo se realiza de forma iterativa en arrays y se mapea cromáticamente mediante color.from_gradient() en celdas de tabla^24^.

Panel de Análisis Técnico Consolidado

La unificación de múltiples indicadores en una consola simplificada permite condensar datos complejos en señales legibles. Un panel profesional combina linestyles dinámicos (para distinguir entre niveles de soporte/resistencia principales y secundarios) y tablas informativas unificadas para dar estructura a la información técnica^10^.

3. polyline.new() — Dibujo de Formas Complejas

La adición de la polilínea en Pine Script v6 representa uno de los mayores hitos visuales de la plataforma, permitiendo la creación de figuras complejas y geometrías de múltiples vértices con un impacto mínimo en los límites globales de renderizado^1^.

El Constructor de Coordenadas Bidimensionales

Para construir una polilínea, es mandatorio crear en primera instancia un array que almacene objetos de tipo chart.point^28^. Cada punto encapsula coordenadas cartesianas temporales o de barra del gráfico^28^. Las funciones constructoras admitidas son:

- chart.point.new(time, index, price): Genera un objeto que almacena coordenadas de tiempo UNIX (milisegundos), índice de barra y precio de mercado simultáneamente^28^. Esto provee la máxima adaptabilidad sintáctica^28^.
- chart.point.from_index(index, price): Método óptimo para modelar figuras basadas en barras relativas en la pantalla actual^28^.
- chart.point.from_time(time, price): Método predilecto para el mapeo de niveles a largo plazo que abarcan más de 9,999 barras de historial, utilizando marcas temporales exactas^28^.

Polilíneas Abiertas, Cerradas e Interpolaciones de Curvas

El constructor principal de la polilínea define las propiedades de interacción visual sobre el lienzo^28^:

Pine Script

polyline.new(points, curved, closed, xloc, line_color, fill_color, line_style, line_width, force_overlay)

- **curved = true:** Aplica un algoritmo de interpolación suavizada entre los puntos del vector de coordenadas en lugar de trazar vectores lineales secantes directos^28^. Es ideal para aproximar curvas matemáticas de distribución, proyecciones senoidales o trayectorias elípticas^28^.
- **closed = true:** Fuerza un vector de cierre automático que conecta el último elemento del array de puntos con el primero, permitiendo habilitar rellenos cromáticos internos uniformes sin costuras visuales mediante fill_color^28^.

Pine Script

//@version=6

indicator("Curved Closed Polyline Example", overlay = true)

if barstate.islastconfirmedhistory

    var points = array.new<chart.point>()

    array.push(points, chart.point.from_index(bar_index - 30, close[30]))

    array.push(points, chart.point.from_index(bar_index - 20, high[20]))

    array.push(points, chart.point.from_index(bar_index - 10, low[10]))

    array.push(points, chart.point.from_index(bar_index, close))

    // Generar polilínea curvada y cerrada con relleno translúcido

    polyline.new(

         points = points, 

         curved = true, 

         closed = true, 

         line_color = color.blue, 

         fill_color = color.new(color.blue, 85), 

         line_style = line.style_solid, 

         line_width = 2

         )

Límites Técnicos y Casos de Uso Críticos

El uso seguro del objeto polyline exige ceñirse a las restricciones impuestas por el núcleo de TradingView para asegurar la estabilidad fluida del navegador^28^:

- **Límite de Vértices:** Un único objeto polyline puede contener un máximo de 10,000 puntos en su array interno^1^.
- **Límite de Objetos:** Un script puede renderizar simultáneamente un máximo de 100 polilíneas independientes en pantalla utilizando el parámetro de inicialización de cabecera max_polylines_count = 100^1^.
- **Restricción de Barras en Indexación:** Cuando se utiliza xloc.bar_index, todos los puntos ingresados deben ubicarse dentro de un rango de 9,999 barras de proximidad respecto a la barra de cálculo actual^28^. Para dibujar elementos fuera de este rango histórico, es mandatorio utilizar xloc.bar_time y marcas temporales UNIX^28^.

4. linefill.new() — Rellenos entre Líneas

La función linefill.new() permite rellenar de manera dinámica el área confinada entre dos líneas independientes creadas mediante line.new(), permitiendo modelar canales de desviación, nubes de medias móviles personalizadas o zonas de transición de valor de manera limpia y nativa^29^.

Firma y Dinámica de Enlace

El constructor de linefill acepta las referencias únicas de dos objetos de tipo line y un color que admite canal alfa para definir la transparencia^30^:

Pine Script

linefill.new(line1, line2, color)

El objeto de relleno carece de coordenadas directas; su geometría depende en su totalidad de las líneas padre referenciadas^30^. Si las coordenadas extremas de las líneas line1 y line2 se modifican dinámicamente mediante las funciones setter del espacio de nombres line.* (como line.set_xy1() o line.set_xy2()), la nube cromática intermedia se redibuja en tiempo real en la siguiente iteración del motor de renderizado^29^.

Pine Script

//@version=6

indicator("Dynamic Linefill Channel", overlay = true)

var line upper_line = na

var line lower_line = na

var linefill channel_fill = na

if barstate.islastconfirmedhistory

    // Destruir instancias previas para evitar acumulación redundante

    line.delete(upper_line)

    line.delete(lower_line)

    // Crear líneas de referencia proyectadas hacia la derecha

    upper_line := line.new(bar_index - 50, high[50], bar_index, high, extend = extend.right, color = color.green, width = 1)

    lower_line := line.new(bar_index - 50, low[50],  bar_index, low,  extend = extend.right, color = color.red,   width = 1)

    // Enlazar el relleno dinámico entre ambas líneas

    channel_fill := linefill.new(upper_line, lower_line, color.new(color.blue, 90))

Reglas de Exclusividad y Modificación Cromática

- **Límite de Asociación:** Únicamente se permite la existencia de un solo objeto linefill activo entre un par de líneas determinado^30^. Ejecutar una llamada consecutiva de linefill.new() sobre las mismas referencias destruirá la ID del relleno previo para dar paso al nuevo elemento instanciado^30^.
- **Actualización Estética:** La propiedad cromática se puede mutar dinámicamente utilizando linefill.set_color(id, color)^30^.
- **Ciclo de Vida:** Si cualquiera de las líneas asociadas (line1 o line2) es destruida o procesada por el colector de basura automático de la plataforma, el objeto linefill adyacente es eliminado de forma inmediata del gráfico, evitando referencias huérfanas en la memoria interna^30^.

5. line.new() — Uso Avanzado y Gestión de Memoria

Las líneas tradicionales instanciadas dinámicamente ofrecen la versatilidad de posicionar referencias de análisis geométrico en cualquier parte del gráfico, incluyendo el plano de proyección futuro hacia la derecha de la barra actual^29^.

Coordenadas Dinámicas: Tiempo vs. Barras

El motor gráfico permite utilizar coordenadas basadas en el índice de la barra (xloc.bar_index) o tiempo UNIX (xloc.bar_time)^29^. La elección de la coordenada correcta es vital para evitar el colapso visual de los dibujos:

- **xloc.bar_index:** Ideal para análisis técnicos a corto plazo de barras adyacentes. La escala horizontal se expande de forma natural con cada barra que se dibuja en tiempo real^29^.
- **xloc.bar_time:** Obligatoria al trazar proyecciones basadas en temporalidades superiores o cuando se extienden líneas de análisis sobre zonas con huecos horariales (*gaps* de fin de semana), garantizando que la línea mantenga su trayectoria matemática a lo largo del eje temporal absoluto^29^.

Extensiones y Jerarquía Visual Estilizada

Las líneas de soporte, resistencia y directrices de tendencia requieren a menudo extenderse lateralmente para alertar sobre zonas calientes del precio^29^. Las opciones de la propiedad extend permiten proyecciones automáticas estables:

- extend.none: El segmento finaliza estrictamente en las coordenadas extremas dadas.
- extend.right: La línea se proyecta de forma infinita hacia el margen derecho del gráfico, ideal para proyectar líneas de ruptura de estructura^30^.
- extend.left / extend.both: Proyección infinita a la izquierda o en ambos sentidos.

Pine Script v6 hereda la capacidad de estructurar la importancia de las líneas aplicando estilos discontinuos para denotar jerarquías de plazos superiores sin obstaculizar la visibilidad^10^:

Pine Script

// Línea principal sólida de ruptura estructural

line.new(bar_index - 5, high, bar_index, high, style = line.style_solid, width = 3)

// Línea secundaria de retroceso intermedia punteada

line.new(bar_index - 5, low, bar_index, low, style = line.style_dotted, width = 1)

| **Estilo de Línea** | **Tipo de Trazado** | **Aplicación Sugerida** |
| --- | --- | --- |
| line.style_solid | Línea continua estándar | Niveles estructurales principales e inmediatos^10^ |
| line.style_dashed | Línea discontinua por guiones | Niveles de referencia secundarios de plazos medios^10^ |
| line.style_dotted | Línea compuesta de puntos | Líneas de tendencia menores, proyecciones a largo plazo^10^ |

El Mecanismo de Colector de Basura (***Garbage Collection***)

TradingView asigna un presupuesto máximo de dibujos dinámicos por script para mantener estable el rendimiento de renderizado en el navegador del usuario^17^. Por defecto, el número máximo de líneas dinámicas activas es de 50^17^. Este límite se puede incrementar explícitamente en el encabezado del indicador hasta un máximo absoluto de 500^17^:

Pine Script

//@version=6

indicator("Estrategia Avanzada de Niveles", overlay = true, max_lines_count = 500)

Cuando un script en ejecución intenta rebasar el límite establecido de líneas, el motor de ejecución activa de manera silenciosa su colector de basura interno (*garbage collection*), que elimina automáticamente las líneas más antiguas creadas por el indicador para conceder espacio de asignación de punteros a los nuevos objetos instanciados^29^.

6. box.new() — Zonas Rectangulares Avanzadas

El objeto box representa la herramienta geométrica por excelencia para delimitar canales horizontales, bloques de órdenes (*order blocks*), zonas de desequilibrio de liquidez (*fair value gaps*) y rangos horarios de operación para diversas sesiones^10^.

Pine Script

box.new(left, top, right, bottom, border_color, border_width, border_style, extend, xloc, bgcolor, text, text_size, text_color, text_halign, text_valign, text_wrap, text_font_family, text_formatting)

Bloques de Órdenes y Rellenos de Sesiones Horarias

El dibujo de un rango se parametriza a través del constructor de cajas, permitiendo definir colores opacos de contorno y fondos traslúcidos que no interrumpan la lectura de las velas japonesas subyacentes^10^:

- **bgcolor:** Almacena el color de fondo del bloque bidimensional^30^. Se recomienda instanciar este parámetro con tonalidades con un alto porcentaje de transparencia (color.new(color, 90)) para asegurar la legibilidad del gráfico^10^.
- **border_style:** Permite asignar constantes de estilo como line.style_solid o line.style_dashed para categorizar la solidez o debilidad de la zona de soporte o resistencia proyectada^10^.

Personalización Estética Avanzada en v6

La sintaxis v6 potencia considerablemente el formato de la información contenida dentro de los rectángulos del gráfico^1^:

- **Puntos Tipográficos Nativos:** Posibilidad de escalar el texto interno usando enteros exactos, como text_size = 11, para asegurar la uniformidad de la interfaz^1^.
- **Énfasis de Estilo Estructurado:** El parámetro text_formatting permite aplicar negrita o cursiva (text.format_bold o text.format_italic) directamente a la información de precios, permitiendo que niveles macro se diferencien de las microestructuras intradía^10^.

7. label.new() — Anotaciones y Paneles Flotantes

Las etiquetas representan la herramienta óptima para situar anotaciones de texto explicativas, alertas dinámicas de ruptura y construir paneles compactos de información que sigan la última vela cotizada^5^.

Modificaciones Tipográficas y Tooltips Dinámicos de Gran Longitud

La actualización del motor de TradingView en agosto de 2025 expandió drásticamente el límite máximo de longitud de las cadenas de texto (*string*) de 4,096 caracteres a un total de 40,960 caracteres codificados^1^. Este incremento de diez veces permite la creación de descripciones interactivas (*tooltips*) masivas y detalladas para el usuario^1^. Al situar el puntero sobre una etiqueta de señal, se puede desplegar un desglose exhaustivo de los factores de confirmación del algoritmo^1^:

Pine Script

//@version=6

indicator("Advanced Tooltip Example", overlay = true)

if barstate.islastconfirmedhistory

    // Construcción de un informe técnico detallado multilínea para el tooltip

    string debug_report = "--- INFORME TÉCNICO DE SEÑAL ---\n" +

                          "Filtro de Tendencia: ALCISTA (EMA 200)\n" +

                          "Oscilador Estocástico: Cruce alcista en zona de sobreventa\n" +

                          "Estructura de Mercado: Ruptura de máximo previo (BOS)\n" +

                          "Volumen Relativo: 1.8x superior a la media de 20 periodos\n" +

                          "Volatilidad ATR: Expandiendo"

    label.new(

         x = bar_index,

         y = high,

         text = "BUY",

         color = color.green,

         textcolor = color.white,

         text_size = 12,

         text_formatting = text.format_bold,

         tooltip = debug_report

         )

Adicionalmente, el formato text_formatting se combina de forma nativa para estructurar las alertas visuales en negrita y cursiva de forma simultánea, incrementando sustancialmente la legibilidad sin sobrecargar el espacio visual de la pantalla del usuario^10^.

8. Sistema de Color Avanzado

Un dashboard profesional requiere un esquema de color adaptativo que traduzca de forma intuitiva los datos cuantitativos duros en una escala cromática legible^2^.

El Uso Cuantitativo de color.from_gradient()

La función de interpolación cromática dinámicos color.from_gradient() toma un valor de entrada variable de tipo series float, lo evalúa dentro de un rango determinado por un límite inferior y un límite superior, e interpola su color resultante de manera proporcional entre dos tonos dados^26^:

Pine Script

color.from_gradient(value, bottom_value, top_value, bottom_color, top_color)

Este mecanismo es el pilar fundamental para modelar mapas de calor del mercado, matrices de correlación y visualizadores de fuerza de volumen dinámicos^26^.

Paletas Profesionales Científicas y Heatmaps

En el desarrollo de herramientas financieras es crítico evitar gradientes de color que resulten confusos bajo diferentes configuraciones de pantalla o que no sean aptos para usuarios con daltonismo. Se aconseja replicar de forma manual paletas analíticas estándar como *Viridis* y *Magma* mediante funciones de mapeo de segmentos múltiples, las cuales ofrecen una percepción uniforme del contraste luminoso de los datos analizados.

| **Paso de Paleta** | **Tono Viridis (Hex)** | **Tono Magma (Hex)** | **Representación Cuantitativa** |
| --- | --- | --- | --- |
| Paso 0 (Mínimo) | #440154 | #000004 | Extremo inferior / Valores negativos máximos |
| Paso 1 (Medio-Bajo) | #3b528b | #50127b | Zona de transición baja |
| Paso 2 (Medio) | #21918c | #b63679 | Centro neutro / Cero absoluto |
| Paso 3 (Medio-Alto) | #5ec962 | #fb8861 | Zona de transición alta |
| Paso 4 (Máximo) | #fde725 | #fcfdbf | Extremo superior / Valores positivos máximos |

Transparencia Dinámica y Transiciones Cromáticas Suaves

En Pine Script v6, los valores cromáticos devueltos por color.from_gradient() pueden modificarse para ajustar su nivel de opacidad utilizando la función color.new(), la cual asume la referencia del color interpolado y le asigna un porcentaje de transparencia de tipo de serie^31^:

Pine Script

// Generar un color dinámico basado en la fuerza del oscilador y aplicarle un 80% de transparencia

color color_gradiente = color.from_gradient(rsi_val, 30.0, 70.0, color.red, color.green)

color color_translucido = color.new(color_gradiente, 80)

Adaptación Nativa a los Temas de TradingView (Light vs. Dark)

Para asegurar la legibilidad de las herramientas gráficas creadas en entornos de distribución pública, es una mala práctica fijar colores de texto rígidos que puedan colapsar con los fondos de pantalla elegidos por los usuarios^37^. El motor de TradingView proporciona dos variables globales altamente útiles que detectan la configuración estética activa en el panel de visualización del cliente^26^:

- chart.bg_color: Devuelve el color de fondo exacto utilizado por el gráfico activo del cliente^26^.
- chart.fg_color: Devuelve un tono que contrasta de manera ideal con el fondo del gráfico actual (por ejemplo, blanco en temas oscuros, negro en temas claros)^26^.

Al basar las tipografías y bordes de los dashboards en la variable chart.fg_color, la interfaz se autoadapta de manera armoniosa y dinámica sin importar la personalización gráfica del usuario^4^.

9. Gestión de Límites de Objetos y Optimización de Rendimiento

El motor de ejecución de TradingView opera en servidores en la nube con límites de uso de recursos compartidos para salvaguardar la experiencia de navegación^39^. Un script que sature el procesador o consuma memoria de forma desmedida será detenido automáticamente, arrojando errores críticos de ejecución^16^.

Límites Máximos Declarativos de Dibujo

Para maximizar el presupuesto de almacenamiento de elementos en pantalla, el desarrollador cuantitativo debe declarar los límites máximos permitidos dentro de la cabecera del indicador utilizando las propiedades del compilador^17^:

| **Parámetro de Cabecera** | **Límite por Defecto** | **Límite Máximo Absoluto** |
| --- | --- | --- |
| max_lines_count | 50 | 500^17^ |
| max_labels_count | 50 | 500^17^ |
| max_boxes_count | 50 | 500^17^ |
| max_polylines_count | 50 | 100^15^ |

Optimización y Prevención de Timeouts de Ejecución

El código cuantitativo óptimo debe mitigar activamente el tiempo de compilación y ejecución de bucles pesados^16^. A continuación, se detallan las directrices fundamentales para la optimización de rendimiento:

- **Reducir Tokens en Bucles Dinámicos:** La arquitectura del compilador de Pine Script traduce el código a una representación intermedia limitada a un máximo estricto de 80,000 tokens internos^16^. Evite anidar estructuras condicionales masivas dentro de bucles de búsqueda for o while^41^.
- **Mapear el Límite de Ejecución de Bucles:** Las variables de término de un bucle for se evalúan de manera dinámica en v6 en cada iteración^6^. Para prevenir ejecuciones infinitas, fije de manera constante o asigne a una variable estática externa la longitud de iteración antes de iniciar el ciclo repetitivo^42^:
Pine Script
// INEFICIENTE: Evalúa la función de tamaño en cada paso del bucle
for i = 0 to array.size(vector_datos) - 1
    // Lógica
// EFICIENTE: El tamaño se calcula una sola vez y permanece estable
int limite_bucle = array.size(vector_datos) - 1
for i = 0 to limite_bucle
    // Lógica
- **Encapsular la Evaluación Perezosa (*****Short-Circuit*****):** Pine Script v6 introduce cortocircuito de evaluación para los operadores lógicos and y or^1^. Si la primera condición de una expresión lógica con and evalúa a false, la siguiente parte de la ecuación jamás se calcula, ahorrando recursos computacionales significativos^1^. No obstante, se debe recordar que las funciones con estado histórico (como ta.rsi() o ta.ema()) jamás deben situarse en el lado derecho de una operación lógica de cortocircuito o dentro de condicionales locales, ya que su cálculo intermitente rompería la consistencia matemática de la serie temporal^23^.

Patrón de Limpieza Manual de Objetos mediante Estructura de Cola (FIFO)

Para evitar que el colector de basura automático de TradingView elimine de forma errática niveles importantes creados por el indicador, se aconseja implementar una cola estructurada de tipo FIFO utilizando arrays de referencias^31^. Al instanciarse un nuevo objeto de dibujo, su puntero de referencia se añade a la cola; si el array supera el límite de control establecido por el desarrollador, el objeto más antiguo es eliminado explícitamente mediante su función destructora nativa y retirado de la pila de memoria del script^31^.

Pine Script

//@version=6

indicator("FIFO Garbage Collection Pattern", overlay = true, max_lines_count = 100)

var line[] line_queue = array.new<line>()

int max_line_retention = 10

if ta.crossover(ta.sma(close, 10), ta.sma(close, 50))

    // Generar nueva línea de ruptura

    line new_lvl = line.new(bar_index - 5, close, bar_index, close, color = color.blue, width = 2)

    array.push(line_queue, new_lvl)

    // Ejecutar depuración manual controlada

    if array.size(line_queue) > max_line_retention

        line oldest_lvl = array.shift(line_queue)

        line.delete(oldest_lvl)

10. Implementaciones Completas de Referencia

A continuación, se exponen tres indicadores con su código de ejecución completo y funcional bajo los estándares normativos de Pine Script v6. Cada script aborda un caso de estudio real de análisis financiero y visualización avanzada.

Script de Referencia 1: Dashboard Profesional Multi-Timeframe (MTF Bias)

Este indicador crea una consola flotante en la esquina superior derecha del gráfico utilizando el sistema de tablas de Pine Script v6^5^. El script implementa un bucle dinámico que recorre un array de marcos temporales para evaluar el sesgo de mercado combinado entre el promedio móvil exponencial (EMA) y el índice de fuerza relativa (RSI) de forma estructurada y con alto rendimiento^1^.

Pine Script

//@version=6

indicator("MTF Trend and Momentum Board", overlay = true)

// ==========================================

// CONFIGURACIÓN DE PARÁMETROS DEL PANEL

// ==========================================

int   tbl_text_size = 10

color panel_bg_color = color.new(#151924, 10)

color panel_border   = #363a45

// Declaración estructurada del array de marcos temporales

var string[] tf_intervals = array.from("5", "15", "30", "60", "240", "D")

// Inicialización de la tabla flotante con var para optimización de rendimiento

var table mtf_dashboard = table.new(

     position = position.top_right, 

     columns = 5, 

     rows = 7, 

     bgcolor = panel_bg_color, 

     border_color = panel_border, 

     border_width = 1

     )

// Función para mapear el sesgo de mercado combinado

f_calculate_trend_bias(float fast, float slow, float rsi_val) =>

    bool is_bullish = fast > slow

    string bias = "NEUTRO"

    color  col  = color.gray

    if is_bullish and rsi_val > 50.0

        bias := "ALCISTA"

        col  := color.green

    else if not is_bullish and rsi_val < 50.0

        bias := "BAJISTA"

        col  := color.red

    [bias, col]

// Restringir el cálculo visual exclusivamente en la última barra confirmada

if barstate.islastconfirmedhistory

    // Inicializar encabezados de columna de forma explícita

    table.cell(mtf_dashboard, 0, 0, "Marco Temp.", text_color = color.white, bgcolor = #1e222d, text_size = tbl_text_size, text_formatting = text.format_bold)

    table.cell(mtf_dashboard, 1, 0, "EMA 20/50",    text_color = color.white, bgcolor = #1e222d, text_size = tbl_text_size, text_formatting = text.format_bold)

    table.cell(mtf_dashboard, 2, 0, "RSI (14)",     text_color = color.white, bgcolor = #1e222d, text_size = tbl_text_size, text_formatting = text.format_bold)

    table.cell(mtf_dashboard, 3, 0, "Condición",    text_color = color.white, bgcolor = #1e222d, text_size = tbl_text_size, text_formatting = text.format_bold)

    table.cell(mtf_dashboard, 4, 0, "Sesgo Final",  text_color = color.white, bgcolor = #1e222d, text_size = tbl_text_size, text_formatting = text.format_bold)

    // Bucle dinámico sobre los marcos temporales definidos en el vector

    int tf_count = array.size(tf_intervals) - 1

    for i = 0 to tf_count

        string current_tf = array.get(tf_intervals, i)

        // Peticiones dinámicas de datos de mercado en v6

        float ema_20_val = request.security(syminfo.tickerid, current_tf, ta.ema(close, 20))

        float ema_50_val = request.security(syminfo.tickerid, current_tf, ta.ema(close, 50))

        float rsi_14_val = request.security(syminfo.tickerid, current_tf, ta.rsi(close, 14))

        // Procesar lógicas internas

        bool is_bullish_trend = ema_20_val > ema_50_val

        string trend_text = is_bullish_trend ? "ALCISTA" : "BAJISTA"

        color trend_color = is_bullish_trend ? color.green : color.red

        string rsi_state = rsi_14_val > 70.0 ? "SOBRECOMPRA" : rsi_14_val < 30.0 ? "SOBREVENTA" : "NEUTRO"

        color rsi_color  = rsi_14_val > 70.0 ? color.orange : rsi_14_val < 30.0 ? color.blue : color.gray

        [bias_text, bias_color] = f_calculate_trend_bias(ema_20_val, ema_50_val, rsi_14_val)

        int row_index = i + 1

        // Rellenar las celdas correspondientes de forma secuencial

        table.cell(mtf_dashboard, 0, row_index, current_tf, text_color = color.white, text_size = tbl_text_size)

        table.cell(mtf_dashboard, 1, row_index, trend_text, text_color = trend_color, text_size = tbl_text_size, text_formatting = text.format_bold)

        table.cell(mtf_dashboard, 2, row_index, str.tostring(rsi_14_val, "0.00"), text_color = rsi_color, text_size = tbl_text_size)

        table.cell(mtf_dashboard, 3, row_index, rsi_state, text_color = rsi_color, text_size = tbl_text_size)

        table.cell(mtf_dashboard, 4, row_index, bias_text, text_color = color.white, bgcolor = color.new(bias_color, 40), text_size = tbl_text_size, text_formatting = text.format_bold)

// Plot dummy obligatorio para permitir compilación de tipo indicador

plot(close, "Trace", color = color.new(color.blue, 100))

Script de Referencia 2: Indicador de Zonas de Soporte/Resistencia con Boxes y Labels

Este script localiza estructuras de pivotes de precio para proyectar zonas de soporte y resistencia institucionales utilizando rectángulos dinámicos de tipo box y anotaciones con etiquetas estructuradas^10^. Incorpora un amortiguador de volatilidad basado en el Rango Verdadero Medio () para estructurar las bandas y realiza una recolección manual de basura para mantener la carga gráfica optimizada^31^.

Pine Script

//@version=6

indicator("Dynamic Support and Resistance Zones", overlay = true, max_boxes_count = 100, max_labels_count = 100)

// ==========================================

// PARÁMETROS DE DETECCIÓN Y ESTÉTICA

// ==========================================

int   pivot_left   = 10

int   pivot_right  = 10

int   max_zones    = 4

color zone_res     = color.new(color.red, 85)

color zone_sup     = color.new(color.green, 85)

// Identificar pivotes estructurales del mercado

float pivot_hi_val = ta.pivothigh(pivot_left, pivot_right)

float pivot_lo_val = ta.pivotlow(pivot_left, pivot_right)

// Arrays dinámicos para almacenar punteros de objetos de dibujo

var box[] active_resistances = array.new<box>()

var box[] active_supports    = array.new<box>()

float current_atr = ta.atr(14)

// Ruptura de pivots y creación de nuevas zonas de soporte / resistencia

if not na(pivot_hi_val)

    // Inicializar zona de resistencia proyectada a la derecha

    box res_box = box.new(

         left = bar_index - pivot_left,

         top = pivot_hi_val,

         right = bar_index,

         bottom = pivot_hi_val - (current_atr * 0.25),

         bgcolor = zone_res,

         border_color = color.new(color.red, 30),

         border_width = 1,

         border_style = line.style_solid,

         text = "Bloque de Venta (O)",

         text_color = color.white,

         text_size = 9,

         text_formatting = text.format_bold,

         text_halign = text.align_right,

         text_valign = text.align_center

         )

    array.push(active_resistances, res_box)

    // Control manual de colector de basura FIFO

    if array.size(active_resistances) > max_zones

        box oldest_res = array.shift(active_resistances)

        box.delete(oldest_res)

if not na(pivot_lo_val)

    // Inicializar zona de soporte proyectada a la derecha

    box sup_box = box.new(

         left = bar_index - pivot_left,

         top = pivot_lo_val + (current_atr * 0.25),

         right = bar_index,

         bottom = pivot_lo_val,

         bgcolor = zone_sup,

         border_color = color.new(color.green, 30),

         border_width = 1,

         border_style = line.style_solid,

         text = "Bloque de Compra (D)",

         text_color = color.white,

         text_size = 9,

         text_formatting = text.format_bold,

         text_halign = text.align_right,

         text_valign = text.align_center

         )

    array.push(active_supports, sup_box)

    // Control manual de colector de basura FIFO

    if array.size(active_supports) > max_zones

        box oldest_sup = array.shift(active_supports)

        box.delete(oldest_sup)

// Bucle dinámico para extender los límites derechos de las zonas activas

int active_res_size = array.size(active_resistances)

if active_res_size > 0

    for i = 0 to active_res_size - 1

        box current_box = array.get(active_resistances, i)

        box.set_right(current_box, bar_index)

int active_sup_size = array.size(active_supports)

if active_sup_size > 0

    for i = 0 to active_sup_size - 1

        box current_box = array.get(active_supports, i)

        box.set_right(current_box, bar_index)

Script de Referencia 3: Panel de Análisis con Heatmap de Correlación

Este indicador avanzado genera una matriz  de correlación cruzada cuantitativa directamente sobre el gráfico^24^. Para evitar fallos en marcos locales, calcula dinámicamente el coeficiente de Pearson utilizando arrays de datos dinámicos, traduciendo los resultados numéricos en un gradiente térmico adaptado en tiempo real^24^:

Pine Script

//@version=6

indicator("Cross Correlation Heatmap Panel", overlay = false)

// ==========================================

// PARÁMETROS DEL SISTEMA DE COEFICIENTE

// ==========================================

string ticker_1 = ""

string ticker_2 = "NASDAQ:AAPL"

string ticker_3 = "NASDAQ:MSFT"

int    corr_period = 20

// Definir nombres de activos reales

string sym_1 = ticker_1 == "" ? syminfo.tickerid : ticker_1

string sym_2 = ticker_2

string sym_3 = ticker_3

// Extracción dinámica de datos históricos en el marco global

float close_s1 = request.security(sym_1, timeframe.period, close)

float close_s2 = request.security(sym_2, timeframe.period, close)

float close_s3 = request.security(sym_3, timeframe.period, close)

// Almacenamiento histórico en arrays

var float[] history_s1 = array.new<float>()

var float[] history_s2 = array.new<float>()

var float[] history_s3 = array.new<float>()

// Insertar datos actuales y mantener la longitud bajo control estricto de memoria

array.push(history_s1, close_s1)

array.push(history_s2, close_s2)

array.push(history_s3, close_s3)

if array.size(history_s1) > corr_period

    array.shift(history_s1)

    array.shift(history_s2)

    array.shift(history_s3)

// ==========================================

// CÁLCULO ESTADÍSTICO DE PEARSON SIN ESTADO

// ==========================================

f_calculate_pearson_r(float[] data_x, float[] data_y) =>

    int n_elements = array.size(data_x)

    float sum_x  = 0.0

    float sum_y  = 0.0

    float sum_xy = 0.0

    float sum_x2 = 0.0

    float sum_y2 = 0.0

    if n_elements > 1

        for i = 0 to n_elements - 1

            float val_x = array.get(data_x, i)

            float val_y = array.get(data_y, i)

            sum_x  += val_x

            sum_y  += val_y

            sum_xy += val_x * val_y

            sum_x2 += val_x * val_x

            sum_y2 += val_y * val_y

    float numerator   = n_elements * sum_xy - sum_x * sum_y

    float denominator = math.sqrt((n_elements * sum_x2 - sum_x * sum_x) * (n_elements * sum_y2 - sum_y * sum_y))

    float pearson_r   = denominator != 0.0 ? numerator / denominator : 0.0

    pearson_r

// Inicialización estática de la tabla de visualización heatmap

var table correlation_table = table.new(

     position = position.middle_center, 

     columns = 4, 

     rows = 4, 

     border_width = 1, 

     border_color = color.gray

     )

// Generar visualización final una vez completado el buffer de historial de datos

if barstate.islastconfirmedhistory and array.size(history_s1) == corr_period

    // Calcular coeficientes bidireccionales de Pearson para la matriz

    float r11 = 1.0

    float r12 = f_calculate_pearson_r(history_s1, history_s2)

    float r13 = f_calculate_pearson_r(history_s1, history_s3)

    float r21 = r12

    float r22 = 1.0

    float r23 = f_calculate_pearson_r(history_s2, history_s3)

    float r31 = r13

    float r32 = r23

    float r33 = 1.0

    // Función de interpolación cromática térmica (Rojo: Inversa, Blanco: Nula, Verde: Directa)

    f_interpolate_thermal(float value) =>

        color.from_gradient(value, -1.0, 1.0, color.red, color.green)

    // Dibujo de encabezados horizontales y verticales

    table.cell(correlation_table, 0, 0, "Matrices", text_color = color.white, bgcolor = color.darkgray, text_size = 9, text_formatting = text.format_bold + text.format_italic)

    table.cell(correlation_table, 1, 0, sym_1,      text_color = color.white, bgcolor = color.black,    text_size = 8, text_formatting = text.format_bold)

    table.cell(correlation_table, 2, 0, sym_2,      text_color = color.white, bgcolor = color.black,    text_size = 8, text_formatting = text.format_bold)

    table.cell(correlation_table, 3, 0, sym_3,      text_color = color.white, bgcolor = color.black,    text_size = 8, text_formatting = text.format_bold)

    table.cell(correlation_table, 0, 1, sym_1,      text_color = color.white, bgcolor = color.black,    text_size = 8, text_formatting = text.format_bold)

    table.cell(correlation_table, 0, 2, sym_2,      text_color = color.white, bgcolor = color.black,    text_size = 8, text_formatting = text.format_bold)

    table.cell(correlation_table, 0, 3, sym_3,      text_color = color.white, bgcolor = color.black,    text_size = 8, text_formatting = text.format_bold)

    // Poblar las celdas calculadas y aplicar el mapeo de color dinámico del gradiente

    // Fila estructural 1

    table.cell(correlation_table, 1, 1, str.tostring(r11, "0.00"), bgcolor = f_interpolate_thermal(r11), text_color = color.black, text_size = 10, text_formatting = text.format_bold)

    table.cell(correlation_table, 2, 1, str.tostring(r12, "0.00"), bgcolor = f_interpolate_thermal(r12), text_color = color.black, text_size = 10, text_formatting = text.format_bold)

    table.cell(correlation_table, 3, 1, str.tostring(r13, "0.00"), bgcolor = f_interpolate_thermal(r13), text_color = color.black, text_size = 10, text_formatting = text.format_bold)

    // Fila estructural 2

    table.cell(correlation_table, 1, 2, str.tostring(r21, "0.00"), bgcolor = f_interpolate_thermal(r21), text_color = color.black, text_size = 10, text_formatting = text.format_bold)

    table.cell(correlation_table, 2, 2, str.tostring(r22, "0.00"), bgcolor = f_interpolate_thermal(r22), text_color = color.black, text_size = 10, text_formatting = text.format_bold)

    table.cell(correlation_table, 3, 2, str.tostring(r23, "0.00"), bgcolor = f_interpolate_thermal(r23), text_color = color.black, text_size = 10, text_formatting = text.format_bold)

    // Fila estructural 3

    table.cell(correlation_table, 1, 3, str.tostring(r31, "0.00"), bgcolor = f_interpolate_thermal(r31), text_color = color.black, text_size = 10, text_formatting = text.format_bold)

    table.cell(correlation_table, 2, 3, str.tostring(r32, "0.00"), bgcolor = f_interpolate_thermal(r32), text_color = color.black, text_size = 10, text_formatting = text.format_bold)

    table.cell(correlation_table, 3, 3, str.tostring(r33, "0.00"), bgcolor = f_interpolate_thermal(r33), text_color = color.black, text_size = 10, text_formatting = text.format_bold)

// Plot dummy obligatorio para permitir compilación de tipo indicador

plot(close_s1, "Cierre Activo Principal", color = color.new(color.blue, 100))

Fuentes citadas

- What's New in Pine Script v6: All Features Covered - TradersPost, https://blog.traderspost.io/article/pine-script-v6-complete-guide
- Pine Script™ v6: An Exciting Update for Traders and Developers - CrossTrade, https://crosstrade.io/blog/pine-script-v6-an-exciting-update-for-traders-and-developers
- How To Create TA Indicators on TradingView - Binance, https://www.binance.com/en/academy/articles/how-to-create-ta-indicators-on-tradingview
- Visuals / Text and shapes - TradingView, https://www.tradingview.com/pine-script-docs/visuals/text-and-shapes/
- New TradingView Feature: Pine Script Tables - Quant Nomad, https://quantnomad.com/new-tradingview-feature-pine-script-tables/
- To Pine Script version 6 - Migration guides - TradingView, https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/
- Ha llegado Pine Script® v6: TradingView Blog, https://www.tradingview.com/blog/es/pine-script-v6-has-landed-48830/
- Pine Script v6 - Visual Studio Marketplace, https://marketplace.visualstudio.com/items?itemName=TradesDontLie.pinescript-v6-vscode
- table | PyneCore Documentation, https://pynecore.org/docs/reference/lib/table/
- Pine Script v6 Visuals: Polylines, Linestyles, Text - TradersPost, https://blog.traderspost.io/article/pine-script-v6-custom-chart-visuals
- Pine Script™ (v6) Notes - 3: Trying out the new v6 feature: text_formatting｜rca, https://note.com/rca_co_jp/n/n9c7484ae06a7?hl=en
- Unite and annotate: Pine Tables now support headers and tooltips - TradingView, https://www.tradingview.com/blog/en/pine-tables-now-support-headers-and-tooltips-29924/
- Pine Script v6 Release Notes Explained (2024-2026) - TradersPost, https://blog.traderspost.io/article/pine-script-v6-release-notes-explained
- pine script - Is there a table.cell_merge() function? - Stack Overflow, https://stackoverflow.com/questions/69559140/is-there-a-table-cell-merge-function
- Pine now does polyline drawings — TradingView Blog, https://www.tradingview.com/blog/en/pine-script-polyline-drawings-41467/
- 5 Causes of Slow Pine Scripts on TradingView - LuxAlgo, https://www.luxalgo.com/blog/5-causes-of-slow-pine-scripts-on-tradingview/
- The Main Limitations of Pine Script on TradingView - Quant Nomad, https://quantnomad.com/the-main-limitations-of-pine-script-on-tradingview/
- Pine Script v6: request.security() Inside Loops - TradersPost, https://blog.traderspost.io/article/pine-script-v6-dynamic-requests
- 10 Pine Script v6 Features for Algorithmic Trading - TradersPost, https://blog.traderspost.io/article/pine-script-v6-features-algorithmic-traders
- Concepts / Other timeframes and data - TradingView, https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/
- Language / Built-ins - TradingView, https://www.tradingview.com/pine-script-docs/language/built-ins/
- Pine Script® v6 has landed — TradingView Blog, https://www.tradingview.com/blog/en/pine-script-v6-has-landed-48830/
- Pine Script v6 Breaking Changes the Converter Misses - TradersPost, https://blog.traderspost.io/article/pine-script-v6-breaking-changes
- how to use ta.correlation() correctly in for_loop context - Stack Overflow, https://stackoverflow.com/questions/75923704/how-to-use-ta-correlation-correctly-in-for-loop-context
- It is recommended to extract the call from this scope in Pine Script - Stack Overflow, https://stackoverflow.com/questions/76873267/it-is-recommended-to-extract-the-call-from-this-scope-in-pine-script
- Language / Type system - TradingView, https://www.tradingview.com/pine-script-docs/language/type-system/
- color | PyneCore Documentation, https://pynecore.org/docs/reference/lib/color/
- How to Draw Polylines in Pine Script v6 - TradersPost, https://blog.traderspost.io/article/pine-script-v6-polyline-drawing
- Visuals / Lines and boxes - TradingView, https://www.tradingview.com/pine-script-docs/visuals/lines-and-boxes/
- Visuals / Fills - TradingView, https://www.tradingview.com/pine-script-docs/visuals/fills/
- Pine Script v5 User Manual (200-350) | PDF | Parameter (Computer Programming) - Scribd, https://www.scribd.com/document/707960100/Pine-Script-v5-User-Manual-200-350
- Fibonacci Levels Indicator Script | PDF - Scribd, https://www.scribd.com/document/903060576/fibo
- SSIS-689 Code Fixes and Recommendations | PDF | Parameter (Computer Programming) - Scribd, https://www.scribd.com/document/905638889/Correction
- text | PyneCore Documentation, https://pynecore.org/docs/reference/lib/text/
- Pinescript correlation(source_a, source_b, length) -> to python - Stack Overflow, https://stackoverflow.com/questions/62041944/pinescript-correlationsource-a-source-b-length-to-python
- O Pine Script® v6 foi lançado — Blog TradingView, https://www.tradingview.com/blog/pb/pine-script-v6-has-landed-48830/
- Newest 'pine-script-v6' Questions - Stack Overflow, https://stackoverflow.com/questions/tagged/pine-script-v6?tab=Newest
- Manual de referencia del lenguaje Pine Script — TradingView, https://es.tradingview.com/pine-script-reference/v5/
- Pine Script User Manual Guide | PDF - Scribd, https://www.scribd.com/document/970916586/Pine-Script-v6-User-Manual
- Pine Script™ v6 User Manual | PDF | Scope (Computer Science) | Time Series - Scribd, https://www.scribd.com/document/860957045/1-Pine-Script-V6-User-Manual-PDF-1
- Language / Loops - TradingView, https://www.tradingview.com/pine-script-docs/language/loops/
- Pine Script For Loops Now Re-Evaluate Boundaries - TradersPost, https://blog.traderspost.io/article/pine-script-dynamic-for-loops
- TradingView Pine Script v6: What You Need to Know - TradersPost, https://blog.traderspost.io/article/tradingview-pine-script-v6-release-guide
- A minimal reference to pine script v5 - GitHub Gist, https://gist.github.com/dnavarrom/5b8a36411a8a6fb2a0380d12cfe52673