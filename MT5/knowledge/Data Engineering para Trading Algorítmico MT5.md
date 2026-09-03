# **Ingeniería de Datos de Alta Performance para Trading Algorítmico con MetaTrader 5: Diseño del Pipeline de Extracción, Almacenamiento y Feature Engineering para Machine Learning**

La viabilidad de los modelos de aprendizaje automático aplicados a mercados financieros no está determinada únicamente por la sofisticación de sus algoritmos, sino por la calidad, consistencia y robustez de sus pipelines de datos.1 El trading cuantitativo se enfrenta a desafíos únicos como la no-estacionariedad de los precios, el sesgo de supervivencia, el sobreajuste en el backtesting y la baja relación señal-ruido.1 El diseño y la implementación de un pipeline de ingeniería de datos optimizado para la plataforma MetaTrader 5 (MT5) mitiga estos problemas estructurales, estructurando flujos de trabajo eficientes desde la ingesta masiva hasta la preparación de conjuntos de datos listos para el entrenamiento de modelos predictivos avanzados.3

## **Extracción masiva de datos de MetaTrader 5**

La interfaz de programación de aplicaciones (API) de Python para MetaTrader 5 actúa como un puente directo para la adquisición de datos de mercado en tiempo real e históricos.3 Sin embargo, su uso a escala industrial exige comprender sus limitaciones técnicas y el diseño de estrategias de paginación robustas ante cortes de conexión y límites de memoria del terminal.5

### **Conectividad y asincronía en MetaTrader 5**

La biblioteca oficial MetaTrader5 expone funciones bloqueantes y síncronas que pueden saturar el hilo principal de ejecución en procesos de alta frecuencia o extracción concurrente.3 Para superar esto, se pueden emplear envoltorios asíncronos como aiomql, el cual traslada las llamadas de MT5 a hilos de ejecución secundarios mediante asyncio.to\_thread.7 Esto garantiza que el bucle de eventos permanezca receptivo y permite orquestar descargas simultáneas de múltiples activos.7  
La inicialización se gestiona mediante mt5.initialize(), especificando opcionalmente la ruta del ejecutable terminal64.exe del broker seleccionado.4 El acceso concurrente requiere controlar los códigos de retorno y estructurar mecanismos de reintento automático ante desconexiones de la red.5

### **Estrategias de paginación y límites de la API**

La terminal de MT5 impone límites estrictos al volumen de datos devuelto en una única llamada.6 Si se solicitan millones de registros sin fragmentar a través de copy\_ticks\_range o copy\_rates\_range, la API puede fallar silenciosamente, devolviendo colecciones incompletas o nulas.3 Además, la terminal restringe la cantidad de barras históricas según el parámetro interno "Max bars in chart" de la configuración de MT5.6  
Para garantizar descargas completas y estables, se implementa una estrategia de **paginación temporal dinámica**. Esta técnica subdivide la ventana de tiempo objetivo en subintervalos lógicos (chunks). Para datos de tick-by-tick de alta liquidez (como el par EURUSD), la paginación óptima se realiza en bloques diarios o de pocas horas para evitar el desbordamiento de memoria RAM y mitigar la latencia en la transmisión.3 Para barras de un minuto (M1), los bloques de 30 a 58 días son el estándar recomendado, ya que evitan la saturación de los buffers de la terminal.6

### **Datos Tick-by-Tick frente a OHLCV**

La elección entre datos agregados (OHLCV) y ticks define el alcance analítico del sistema de trading:

* **OHLCV (Open, High, Low, Close, Volume):** Proporciona intervalos temporales fijos (M1, H1, D1).6 Es computacionalmente eficiente y óptimo para estrategias macro o de mediano plazo, pero sufre del sesgo de agregación: oculta la secuencia interna de precios ocurrida dentro de la barra y diluye la dinámica de liquidez.1  
* **Tick-by-Tick:** Registra cada cambio individual en las cotizaciones de compra (*bid*), venta (*ask*) o transacciones reales (*last*) junto con sus respectivos volúmenes.3 Es indispensable para el análisis de microestructura, el cálculo de métricas de flujo de órdenes y la simulación exacta de deslizamiento (*slippage*) en backtesting.1 Exige una arquitectura con alta velocidad de lectura/escritura y técnicas rigurosas de deduplicación de marcas de tiempo.6

### **Adquisición de datos alternativos**

Las ineficiencias de los mercados financieros rara vez se explican únicamente con el precio histórico.1 Es fundamental integrar datos que MetaTrader 5 no proporciona de manera nativa 12:

* **Compromiso de los Operadores (COT Reports):** Publicados semanalmente por la CFTC, revelan el posicionamiento de grandes especuladores e instituciones comerciales.13 Se pueden recuperar de forma automatizada mediante la biblioteca cot-reports 14 o scripts basados en BeautifulSoup para procesar los archivos ZIP históricos de la CFTC.15  
* **Datos Macroeconómicos:** Indicadores clave como tasas de interés, inflación o empleo se obtienen directamente de bases de datos como la FRED (Federal Reserve Economic Data) mediante su API oficial.16  
* **Datos de Sentimiento y Noticias:** La ingesta de feeds de noticias a través de NewsAPI o plataformas de redes sociales proporciona el sustrato para modelos de procesamiento de lenguaje natural (NLP) que cuantifican el impacto psicológico del mercado.16

## **Calidad e integridad de datos de mercado**

Las bases de datos provistas por brokers minoristas a través de MT5 suelen presentar anomalías que pueden invalidar los modelos de machine learning si no se limpian sistemáticamente.1

### **Anomalías comunes en los datos de broker**

Las anomalías se clasifican en cinco categorías principales, detalladas a continuación:

* **Spikes (Picos anormales):** Cotizaciones erróneas debido a fallos de comunicación en el proveedor de liquidez o ejecuciones fuera de mercado. Generan cambios de precio extremos que se revierten en el tick inmediato, distorsionando el cálculo de volatilidad histórica.19  
* **Gaps Temporales (Huecos):** Periodos de inactividad artificial provocados por caídas del servidor del broker o cierres del mercado que no se alinean correctamente entre zonas horarias.16  
* **Datos Faltantes (Missing Ticks):** Desaparición selectiva de ticks durante periodos de extrema volatilidad, donde la terminal de MT5 descarta cotizaciones debido a retrasos en el búfer de recepción local.  
* **Splits en Acciones:** Ajustes de capitalización que alteran el valor absoluto del activo históricamente. Deben corregirse multiplicando la serie histórica por el factor de ajuste para evitar saltos artificiales que el modelo interprete como desplomes del mercado.  
* **Desalineación de Rollover en Futuros:** Cuando un contrato de futuros expira, se produce un salto de precio respecto al contrato del mes siguiente.20 Si las cotizaciones de ambos contratos se unen directamente para formar un histórico continuo, el salto de precio genera una señal distorsionada.20

### **Métodos de ajuste para contratos de futuros**

La construcción de un contrato de futuros continuo a partir de entregas individuales requiere la aplicación de reglas matemáticas específicas.20 La tabla siguiente expone una comparativa detallada de estos métodos de ajuste 20:

| Método de Ajuste | Mecanismo Matemático | Ventajas | Desventajas | Caso de Uso Recomendado |
| :---- | :---- | :---- | :---- | :---- |
| **Ajuste de Panamá (Back/Forward)** | Desplaza la serie histórica sumando o restando la diferencia absoluta medida en la fecha del rollover: ![][image1].21 | Mantiene estables las relaciones de precios absolutos y preserva el perfil de ganancias y pérdidas acumuladas.20 | Puede generar precios históricos negativos si el activo experimenta un fuerte contango histórico.20 | Backtesting de estrategias de reversión a la media con órdenes límite basadas en precios absolutos. |
| **Ajuste Proporcional** | Ajusta los precios históricos multiplicándolos por la relación de precios observada durante la transición: ![][image2].20 | Elimina la posibilidad de precios negativos y preserva los rendimientos porcentuales exactos, lo que es óptimo para la estabilidad de modelos matemáticos.20 | Altera los niveles absolutos de precios históricos, lo que dificulta la ejecución directa de stops o límites históricos sin recalcularlos.20 | Modelos de Machine Learning basados en retornos de precios e indicadores de momentum de largo plazo. |
| **Método Perpetuo (Continuous Roll)** | Realiza una ponderación lineal decreciente entre ambos contratos durante una ventana de transición de ![][image3] días previos a la expiración.20 | Suaviza la transición eliminando el salto brusco de un solo día, ofreciendo una serie temporal altamente continua.20 | Requiere mantener operaciones abiertas simultáneamente en ambos contratos, elevando los costos de transacción e implícita ejecución.20 | Modelos macroeconómicos o de asignación de activos de baja rotación temporal. |

### **Detección y limpieza de anomalías**

Para identificar *spikes* y valores atípicos de forma robusta, se descarta el desvío estándar debido a su sensibilidad a los propios outliers. En su lugar, se aplica el método del **Desvío Absoluto de la Mediana (MAD)** en ventanas móviles. Para una serie de retornos de precios ![][image4], el MAD se define como:  
![][image5]  
Un retorno se clasifica como anomalía si su puntuación ![][image6] modificada excede un límite de tolerancia (comúnmente ajustado entre ![][image7] y ![][image8]):  
![][image9]  
Los valores identificados como anomalías se eliminan y se reconstruyen mediante interpolaciones lineales o asignando el último valor conocido (*forward fill*) para evitar introducir sesgos de anticipación (*look-ahead bias*).16

### **Validación de la integridad del dataset descargado**

Antes de guardar o procesar los datos, el pipeline debe pasar tres pruebas de validación:

1. **Monotonicidad temporal:** Verificar que las marcas de tiempo sean estrictamente crecientes (![][image10]).  
2. **Consistencia de volumen:** Comprobar que el volumen de tick no sea negativo y que corresponda con el recuento físico de transacciones si la fuente lo permite.  
3. **Auditoría de completitud horaria:** Comparar la cantidad de registros recibidos contra el calendario operativo del activo (descontando festivos y fines de semana) para identificar pérdidas de conexión del broker.16

## **Formatos de almacenamiento óptimos**

El almacenamiento de series temporales de trading requiere equilibrar el espacio en disco, la velocidad de procesamiento secuencial de millones de registros y la integración transparente con entornos analíticos en Python.24

### **Comparativa técnica de formatos de almacenamiento y bases de datos**

La tabla a continuación resume las fortalezas y debilidades de las tecnologías de persistencia más extendidas en el ecosistema financiero 24:

| Formato / Base de Datos | Tipo de Motor | Eficiencia de Compresión | Latencia de Escritura | Latencia de Lectura | Concurrencia | Herramientas Python | Caso de Uso Óptimo |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **CSV** | Archivo plano | Nula (salvo compresión externa) | Muy alta (I/O intensiva) | Muy alta (requiere parseo) | Pobre | pandas nativo | Exportación ligera de muestras de juguete.29 |
| **HDF5** | Archivo jerárquico | Alta (LZO / GZIP) | Media | Baja | Pobre (vulnerable a bloqueos en escritura concurrente) | h5py, pandas.HDFStore | Almacenamiento local de datasets estructurados de investigación estática. |
| **Parquet** | Archivo columnar | Muy alta (Snappy / ZSTD) 24 | Media | Muy baja (I/O selectiva de columnas) 25 | Excelente (lectura distribuida) | pyarrow, fastparquet | Formato estándar de investigación offline, almacenamiento de backtesting e interactividad con Data Lakes.25 |
| **Feather** | Archivo binario | Media-alta | Muy baja | Extremadamente baja (mapeo directo a memoria) | Limitada a lectura local | pyarrow.feather | Persistencia temporal ultrarrápida entre etapas del pipeline en memoria RAM. |
| **SQLite** | Base de datos relacional integrada | Baja | Alta | Media | Limitada por bloqueo de base de datos | sqlite3 nativo, SQLAlchemy | Almacenamiento de metadatos del pipeline, tablas de control de ejecución e históricos agregados de baja frecuencia.7 |
| **TimescaleDB** | Base de datos relacional de series temporales (Postgres) 26 | Alta (compresión nativa por columnas ![][image11]) 24 | Media (acotada por los límites del motor Postgres) 26 | Baja (rápida para consultas agregadas y SQL relacional complejo) 26 | Excelente | psycopg2, SQLAlchemy 27 | Entornos corporativos que requieren integridad relacional clásica y análisis sobre agregados continuos.26 |
| **QuestDB** | Base de datos columnar de series temporales 27 | Extremadamente alta 28 | Muy baja (diseñada para millones de escrituras de ticks/segundo) 24 | Extremadamente baja (motor C++/Rust optimizado con SIMD) 27 | Excelente | questdb client, psycopg2 | Ingestión de ticks en tiempo real a alta frecuencia, almacenamiento centralizado de market data e interoperabilidad analítica.25 |

### **Arquitectura de almacenamiento híbrido: QuestDB y Apache Parquet**

Los pipelines de trading institucional suelen estructurarse bajo un modelo de **almacenamiento híbrido (Hot-Cold Storage)**.25 Los datos de mercado recientes, de alta frecuencia y calientes se canalizan de forma directa a **QuestDB** aprovechando su capacidad de ingesta secuencial masiva a través de *InfluxDB Line Protocol* (ILP).25  
Una vez que estos datos pierden relevancia inmediata para la operativa en tiempo real (por ejemplo, transcurridos 30 días), el pipeline de datos los extrae, los consolida y los exporta a archivos **Apache Parquet** en almacenamiento en la nube (ej. Amazon S3).25 Esta segmentación reduce sustancialmente los costos de almacenamiento en caliente y permite a los investigadores cuantitativos cargar de manera eficiente solo las columnas requeridas (por ejemplo, los precios de cierre de un activo omitiendo los identificadores de transacción) reduciendo drásticamente los cuellos de botella de I/O de disco y memoria RAM en simulaciones históricas masivas.25

## **Feature Engineering para trading**

La transformación de las series de precios crudos en variables explicativas estacionarias con alta capacidad predictiva representa el núcleo del pipeline cuantitativo.1 A continuación, se presenta un catálogo integral de características calculadas de forma vectorial:

### **Características técnicas y de volatilidad**

* **Rango Verdadero Promedio (ATR):** Medida clásica de volatilidad absoluta utilizada para normalizar distancias de precios:

![][image12]  
![][image13]

* **Índice de Fuerza Relativa (RSI):** Oscilador de momentum clásico que mide la velocidad y el cambio de los movimientos de precios.  
* **Volatilidad de Retornos Históricos:** Calculada mediante desviaciones estándar o varianzas exponenciales ponderadas móviles (EWMA) para capturar el régimen de incertidumbre del activo en ventanas deslizantes.

### **Patrones de velas normalizados**

Para asegurar que las características basadas en la acción del precio sean estacionarias y homogéneas a lo largo del tiempo, se evitan los precios nominales absolutos. En su lugar, se calcula la geometría de la vela japonesa normalizada respecto al rango total de oscilación:  
![][image14]  
![][image15]  
![][image16]

### **Características de microestructura de mercado**

* **Horquilla Bid-Ask Promedio (Spread):** Medida implícita de liquidez y fricción de mercado:

![][image17]

* **Desequilibrio de Volumen (Volume Imbalance):** Revela la dominancia de la presión compradora sobre la vendedora en un instante dado:

![][image18]

* **Probabilidad de Negociación Informada Sincronizada por Volumen (VPIN):** El VPIN mide la toxicidad del flujo de órdenes cuantificando el desequilibrio de volumen acumulado sobre barras de volumen constante.10 Para un conjunto de ![][image3] barras de volumen consecutivas con volumen fijo ![][image19] 1, se computa mediante la siguiente fórmula:

![][image20]  
Donde ![][image21] y ![][image22] corresponden al volumen comprado y vendido dentro de la barra de volumen ![][image23], calculados clasificando los flujos mediante la regla del tick u operadores de clasificación inter-barra.1

### **Características temporales y estadísticas**

* **Codificación Cíclica del Tiempo:** Para evitar saltos artificiales entre las 23:59 y las 00:00, las horas del día ($H \\in $) y los días de la semana ($D \\in $) se proyectan en componentes polares de seno y coseno:

![][image24]

* **Z-Scores de Ventana Móvil:** Normalizan variables financieras de alta variabilidad (como el volumen negociado o los spreads) respecto a su distribución local dinámica, garantizando estabilidad en los algoritmos de clasificación 32:

![][image25]

### **Optimización en Pandas y NumPy para el procesamiento vectorial**

La ingeniería de características sobre bases de datos que superan millones de registros exige evitar a toda costa el uso de bucles de control secuencial (for, while, .iterrows(), .itertuples()) en Python.32 Estos bucles introducen latencias elevadas debido al tipado dinámico y la sobrecarga del intérprete de Python.32  
En su lugar, se implementa programación puramente **vectorial**, delegando el cómputo de arrays a funciones nativas en C/C++ optimizadas en **NumPy** y **Pandas** que aprovechan instrucciones SIMD (Single Instruction, Multiple Data) y la difusión (*broadcasting*) de formas.34 Operaciones matemáticas complejas se estructuran mediante la conversión de series a vectores nativos en memoria (df\['close'\].to\_numpy()), permitiendo reducir tiempos de procesamiento de minutos a milisegundos.32

## **Estructuración de Datasets para Machine Learning**

La disposición estructural de los datos financieros para el entrenamiento de modelos supervisados difiere drásticamente de los esquemas convencionales debido a la correlación temporal y el comportamiento asíncrono de las series económicas.2

### **Esquemas de muestreo alternativos**

La partición de datos basada en ventanas de tiempo cronológico constante (barras de 5 minutos, barras de 1 hora) genera problemas de heterocedasticidad (varianza no constante de los retornos) y subestima periodos de alta actividad transaccional donde el mercado asimila la información a un ritmo acelerado.2 Para mitigar esto, se implementan esquemas de muestreo basados en eventos 1:

| Esquema de Muestreo | Criterio de Activación / Corte | Estabilidad de la Varianza | Sincronía Informativa | Propiedades Estadísticas de los Retornos |
| :---- | :---- | :---- | :---- | :---- |
| **Muestreo Temporal** | Se genera una barra al transcurrir un lapso constante ![][image26] (ej. cada 15 minutos).2 | Pobre (sufre de alta heterocedasticidad debido a patrones intradía de volumen).2 | Baja (ignora el volumen y la frecuencia de arribo de información). | Retornos con distribuciones leptocúrticas (colas pesadas, no normales).2 |
| **Muestreo por Ticks** | Se genera un registro tras acumular un número fijo ![][image27] de transacciones individuales. | Moderada (suaviza los picos de varianza provocados por la apertura o cierre del mercado). | Media | Aproxima la serie a un comportamiento transaccional homogéneo. |
| **Muestreo por Volumen** | Se genera un registro cada vez que el volumen físico negociado alcanza un umbral determinado ![][image28].1 | Alta (el volumen se correlaciona con la volatilidad; este muestreo la estabiliza). | Alta (sincroniza el muestreo con la actividad real de los agentes del mercado).2 | Distribuciones de retornos más cercanas a una distribución gaussiana simétrica.2 |
| **Muestreo por Barras de Dólar (Value)** | Se genera un registro cuando el valor monetario total transaccionado excede un umbral definido: ![][image29].1 | Excelente (neutraliza el impacto de grandes variaciones en el nivel nominal del precio del activo).2 | Máxima (captura el flujo de capital real independientemente del precio del activo).1 | Máxima estacionariedad y mínima correlación serial en los residuos de la varianza.2 |

### **Etiquetado predictivo: El Método de la Triple Barrera**

La formulación tradicional de predecir la dirección del retorno a un intervalo de tiempo fijo ![][image30] presenta limitaciones graves: ignora los límites operativos de una transacción real, donde el operador o algoritmo cerraría la posición antes de ![][image30] si se activa un límite de pérdidas (*stop-loss*) o una toma de beneficios (*take-profit*).1  
Para solucionar este sesgo, se implementa el **Método de la Triple Barrera de Marcos López de Prado**.1 Este método define tres barreras operacionales alrededor del precio de entrada ![][image31] 1:

1. **Barrera Horizontal Superior (Take-Profit):** Definida a una distancia ![][image32], donde ![][image33] es un estimador de la volatilidad diaria dinámica calculada mediante una EWMA local.1  
2. **Barrera Horizontal Inferior (Stop-Loss):** Definida a una distancia ![][image34].1  
3. **Barrera Vertical (Expiración):** Un límite de tiempo absoluto expresado como una cantidad máxima de barras o duración máxima desde la entrada.1

La variable objetivo ![][image35] se asigna según la primera barrera que sea cruzada por la trayectoria del precio en el mercado 1:  
![][image36]  
Adicionalmente, se puede aplicar la técnica de **Meta-Labeling (Meta-Etiquetado)**.1 En este enfoque, un modelo primario clasifica la dirección de la operación (![][image37] para una posición larga o ![][image38] para una corta). Posteriormente, se aplica un modelo binario secundario entrenado para determinar si el modelo primario alcanzará la rentabilidad (![][image37]) o fallará (![][image39]) antes de tocar el stop-loss, optimizando de esta manera la gestión de riesgo y el dimensionamiento de las posiciones en cuenta real.1

                 Precio ($)  
                    ^  
                    |          Barrera Superior: Take-Profit (+1)  
  \------------------+-----------------------------------------\\    
 /                  |                                          \\  \<- Trayectoria del precio  
/                   |                                           \\  
|                   |                      |                     \\  
|                   |                      |                      |  
|                   |                      |                      |  
o-------------------+----------------------+----------------------+----\> Tiempo  
 t0                 |                      |                      t1  
                    |                      | (Barrera Vertical)  
                    |                      |  
                    |                      |  
  \------------------+----------------------/                        
                    |          Barrera Inferior: Stop-Loss (-1)

### **Técnicas de balanceo de clases**

Las etiquetas de trading suelen exhibir fuertes desequilibrios (las etiquetas ![][image40] o ![][image38] pueden ser escasas en mercados con baja volatilidad lateralizada). Para evitar sesgos en el entrenamiento de los modelos, se aplican técnicas de balanceo:

* **Ponderación de muestras por unicidad (Sample Weights):** Se asigna un peso a cada observación inverso a su grado de solapamiento temporal con otras muestras, penalizando registros redundantes.1  
* **Submuestreo controlado de la clase mayoritaria:** Generalmente la clase neutra (![][image39]), para forzar al modelo a enfocarse en señales de acción real.

### **Separación rigurosa de datos: Purging y Embargo**

En el aprendizaje automático tradicional, se asume que las muestras son independientes e idénticamente distribuidas (I.I.D.).2 Sin embargo, en el análisis cuantitativo de mercados, las características y las etiquetas derivadas del método de la triple barrera se solapan temporalmente, lo que invalida los enfoques tradicionales de validación cruzada.1 Si una muestra en ![][image41] comparte un intervalo de evaluación con una muestra en ![][image42], colocar una en el conjunto de entrenamiento y otra en el de validación provoca una severa fuga de información (*information leakage*).2 El modelo memoriza el futuro y arroja métricas de precisión artificialmente elevadas que colapsan en fase real.2  
Para asegurar la separación estricta del conjunto de datos, se aplican dos procedimientos durante la validación cruzada 2:

1. **Purging (Purga):** Remueve del conjunto de entrenamiento todas las muestras cuyos intervalos de definición de etiquetas se solapen temporalmente con cualquier etiqueta del conjunto de prueba/validación.2  
2. **Embargo:** Debido a que la autocorrelación serial en los residuos de las variables financieras puede persistir en el tiempo, el embargo elimina de forma adicional una ventana fija de muestras de entrenamiento inmediatamente posteriores al final de las muestras de validación.2

## **Pipelines de datos automatizados y versionamiento**

La automatización sistematizada de la extracción, validación, transformación e ingesta diaria de variables de mercado representa la columna vertebral operativa de un fondo cuantitativo.

### **Orquestación de flujos de datos (ETL)**

El uso de sistemas de planificación tradicionales como cron suele ser insuficiente para el trading algorítmico debido a que carece de control nativo de dependencias complejas, reintentos dinámicos en caso de error y supervisión en tiempo real.30 Por ello, se recomienda implementar frameworks de orquestación modernos:

* **Apache Airflow:** Define las tareas de ETL mediante Grafos Acíclicos Dirigidos (DAGs) escritos en Python.30 Es robusto, altamente escalable y permite gestionar dependencias complejas a nivel corporativo, aunque introduce una curva de aprendizaje pronunciada y mayor sobrecarga de infraestructura.30  
* **Prefect:** Una alternativa moderna centrada en la facilidad de uso y la flexibilidad, idónea para flujos de datos de ejecución rápida y dinámica con soporte nativo para ejecución asíncrona.30

### **Versionamiento de datos: DVC frente a Delta Lake**

Al entrenar modelos de aprendizaje automático financieros, el control de versiones del código fuente a través de Git es insuficiente.30 Se requiere capturar con exactitud el estado del dataset físico con el que se entrenó cada iteración de un modelo para garantizar la reproducibilidad y el linaje de datos 30:

* **Delta Lake:** Extensión construida sobre almacenamiento de objetos (ej. Parquet) que añade una capa transaccional ACID.31 Admite viajes en el tiempo (*time travel*) permitiendo consultar instantáneas del dataset en cualquier punto del pasado histórico.31 Es óptimo para arquitecturas corporativas distribuidas y basadas en Apache Spark.31  
* **DVC (Data Version Control):** Herramienta ligera de línea de comandos que extiende la semántica de Git para la gestión de archivos masivos.30 DVC genera metadatos ligeros de control de versiones y archivos de punteros pequeños (con extensión .dvc e identificadores basados en hashes MD5) que se confirman y rastrean directamente dentro del repositorio de Git convencional.30 Los archivos de datos físicos de gran tamaño (como conjuntos de datos de ticks o características procesadas) se transfieren y almacenan de forma segura en un almacén externo (como AWS S3, Google Cloud Storage o servidores locales de red).30 Al alternar entre ramas de Git con comandos como git checkout \<rama\_tag\> seguido de dvc pull, DVC sincroniza el directorio de trabajo local con el conjunto de datos exacto correspondiente, facilitando auditorías integrales de linaje de datos en sistemas productivos.38

## **Fuentes de datos complementarias y combinación asíncrona**

Para complementar las señales de precio de MT5, el pipeline debe unificar flujos de información externa con diferentes frecuencias temporales.12

### **Integración de múltiples fuentes externas**

Se integran tres fuentes de datos externas mediante solicitudes programáticas 16:

* FRED API: Acceso a datos macroeconómicos oficiales (tasas de desempleo, niveles de deuda, inflación).16  
* **Yahoo Finance & Alpha Vantage:** Proveedores versátiles para recuperar fundamentales corporativos trimestrales o datos de volatilidad implícita.16  
* **NewsAPI & Redes Sociales:** Extracción de flujos textuales de opinión sobre divisas, commodities o índices para alimentar modelos de procesamiento del lenguaje natural (NLP).17

### **Fusión temporal asíncrona mediante uniones Asof**

Uno de los mayores errores de ingeniería de datos financieros consiste en usar una unión tradicional de bases de datos basada en igualdad exacta de fechas (pandas.merge tradicional) al intentar acoplar cotizaciones de precios en tiempo real de divisas (actualizadas al segundo) con variables de baja frecuencia o asíncronas (como un reporte macro de la FRED mensual o una noticia bursátil aleatoria).16 Esto suele provocar pérdida de registros o solapamientos erróneos.29  
La solución óptima consiste en aplicar **uniones condicionales por proximidad temporal hacia atrás (Asof Joins)** mediante pandas.merge\_asof.16 Esta función asocia para cada registro de precio con timestamp ![][image43], el último registro de la fuente externa cuyo timestamp de publicación ![][image44] sea menor o igual al del precio (![][image45]).19

### **Prevención estricta del sesgo de anticipación (Look-Ahead Bias)**

Al integrar datos complementarios, se debe evitar el sesgo de anticipación.16 Este error ocurre cuando el pipeline asocia a una marca de tiempo una información que físicamente no había sido publicada todavía en el mundo real en ese instante.16 Para evitarlo, se aplican dos reglas de diseño obligatorias:

1. **Dirección de búsqueda retrospectiva estricta:** Al utilizar pandas.merge\_asof, el parámetro direction debe configurarse invariablemente como 'backward'.19 Esto garantiza que solo se miren registros que ocurrieron en el pasado de la marca de tiempo de la cotización actual, prohibiendo mirar eventos futuros.29  
2. **Modelar el desfase de publicación (Reporting Lag):** Las cifras oficiales (como el PIB o los niveles de inflación) corresponden a periodos históricos previos, pero no se publican hasta semanas después. Del mismo modo, el informe de posicionamiento semanal COT recopila datos el día martes, pero la CFTC no los publica formalmente hasta el día viernes por la tarde.14 Si el pipeline asocia el dato del COT al martes de esa semana en lugar del viernes, el modelo entrenado tendrá una ventaja predictiva irreal en el backtesting que se traducirá en pérdidas severas en la operativa real.29 Para evitarlo, la marca de tiempo de las fuentes complementarias debe retrasarse artificialmente para reflejar con exactitud la fecha y hora de su publicación efectiva en el mercado real antes de realizar la unión temporal asof.29

## **Pipeline de datos completo en Python (Ejemplo: EURUSD)**

El siguiente script de Python representa un pipeline de ingeniería de datos completo y listo para producción para el par de Forex EURUSD.  
El código se ha diseñado de manera defensiva: intenta conectarse de manera activa a la terminal de MetaTrader 5 instalada localmente; en caso de no encontrarse un entorno activo de MT5 (común en entornos de ejecución Linux o servidores en la nube sin interfaz gráfica), el pipeline genera automáticamente un conjunto de datos sintético estructurado para demostrar el flujo de cálculo vectorial, la generación de características avanzadas y el etiquetado adaptativo mediante la triple barrera.

Python  
import os  
import sys  
import numpy as np  
import pandas as pd  
from datetime import datetime, timedelta

try:  
    import MetaTrader5 as mt5  
except ImportError:  
    mt5 \= None

\# \==========================================  
\# EXTRACCIÓN Y SIMULACIÓN DE DATOS  
\# \==========================================  
def extract\_or\_simulate\_data(symbol="EURUSD", days\_history=15):  
    """  
    Intenta extraer datos tick y de barras desde MetaTrader 5 de forma local.  
    Si MT5 no está disponible o falla la inicialización, genera datos sintéticos  
    estructurados de alta fidelidad para el cálculo de features y ML.  
    """  
    data\_source\_mt5 \= False  
      
    if mt5 is not None:  
        \# Intentar inicializar la terminal de MetaTrader 5  
        if mt5.initialize():  
            print("\[INFO\] Conectado exitosamente a la terminal de MetaTrader 5.")  
              
            utc\_to \= datetime.now()  
            utc\_from \= utc\_to \- timedelta(days=days\_history)  
              
            \# Recuperar barras M1 históricas  
            rates \= mt5.copy\_rates\_range(symbol, mt5.TIMEFRAME\_M1, utc\_from, utc\_to)  
              
            if rates is not None and len(rates) \> 0:  
                df\_rates \= pd.DataFrame(rates)  
                df\_rates\['time'\] \= pd.to\_datetime(df\_rates\['time'\], unit='s')  
                df\_rates.set\_index('time', inplace=True)  
                  
                \# Para evitar fallos en cuentas sin datos de spread reales,   
                \# nos aseguramos de que la columna exista  
                if 'spread' in df\_rates.columns:  
                    \# En MT5, el spread viene expresado en puntos  
                    df\_rates\['spread\_pips'\] \= df\_rates\['spread'\] \* 0.1  
                else:  
                    df\_rates\['spread\_pips'\] \= 1.5  
                  
                print(f"\[INFO\] Se extrajeron exitosamente {len(df\_rates)} barras M1 desde MT5.")  
                mt5.shutdown()  
                return df\_rates, True  
            else:  
                print(" No se recuperaron barras desde MT5. Utilizando datos sintéticos.")  
                mt5.shutdown()  
        else:  
            print(" No se pudo inicializar la terminal MT5 local. Fallback a datos simulados.")  
    else:  
        print("\[INFO\] MetaTrader 5 Python Library no instalada o sistema operativo no Windows. Usando simulación.")

    \# GENERACIÓN DE DATOS SINTÉTICOS DE ALTA COMPLEJIDAD (Simulando EURUSD)  
    print("\[INFO\] Generando datos sintéticos estructurados...")  
    np.random.seed(42)  
    periods \= days\_history \* 1440  \# 1440 minutos por día  
    date\_range \= pd.date\_range(end=datetime.now(), periods=periods, freq='min')  
      
    \# Simulación de paseo aleatorio con reversión a la media leve  
    returns \= np.random.normal(loc=1e-6, scale=0.00015, size=periods)  
    price \= 1.0850 \* np.exp(np.cumsum(returns))  
      
    high \= price \* (1 \+ np.abs(np.random.normal(loc=0.0001, scale=0.00005, size=periods)))  
    low \= price \* (1 \- np.abs(np.random.normal(loc=0.0001, scale=0.00005, size=periods)))  
    open\_p \= price \* (1 \+ np.random.normal(loc=0, scale=0.00005, size=periods))  
      
    \# Corrección lógica de extremos  
    high \= np.maximum(high, np.maximum(open\_p, price))  
    low \= np.minimum(low, np.minimum(open\_p, price))  
      
    volume \= np.random.randint(10, 500, size=periods)  
    spread \= np.random.uniform(0.0001, 0.0003, size=periods) \# 1.0 \- 3.0 pips  
      
    df\_rates \= pd.DataFrame({  
        'open': open\_p,  
        'high': high,  
        'low': low,  
        'close': price,  
        'tick\_volume': volume,  
        'spread\_pips': spread  
    }, index=date\_range)  
      
    df\_rates.index.name \= 'time'  
    return df\_rates, False

\# \==========================================  
\# FEATURE ENGINEERING VECTORIZADO  
\# \==========================================  
def calculate\_advanced\_features(df):  
    """  
    Calcula un catálogo completo de atributos predictivos estructurados de forma vectorial  
    para evitar loops ineficientes en Pandas.  
    """  
    df \= df.copy()  
      
    \# a) Retornos simples y logarítmicos  
    df\['return'\] \= df\['close'\].pct\_change()  
    df\['log\_return'\] \= np.log(df\['close'\] / df\['close'\].shift(1))  
      
    \# b) Volatilidad móvil exponencial (EWM) como estimador de la dispersión de retornos  
    df\['rolling\_volatility'\] \= df\['return'\].ewm(span=100, min\_periods=20).std()  
      
    \# c) Medias móviles exponenciales rápidas y lentas (Tendencia)  
    df\['ema\_fast'\] \= df\['close'\].ewm(span=20, adjust=False).mean()  
    df\['ema\_slow'\] \= df\['close'\].ewm(span=100, adjust=False).mean()  
    df\['ema\_ratio'\] \= df\['ema\_fast'\] / df\['ema\_slow'\]  
      
    \# d) Patrones de velas normalizados (Normalización respecto al Rango de Precio)  
    candle\_range \= df\['high'\] \- df\['low'\]  
    \# Reemplazar ceros temporales para evitar divisiones por cero en periodos ilíquidos  
    candle\_range \= np.where(candle\_range \== 0, 1e-8, candle\_range)  
      
    df\['candle\_body\_norm'\] \= (df\['close'\] \- df\['open'\]) / candle\_range  
    df\['candle\_upper\_shadow'\] \= (df\['high'\] \- np.maximum(df\['open'\], df\['close'\])) / candle\_range  
    df\['candle\_lower\_shadow'\] \= (np.minimum(df\['open'\], df\['close'\]) \- df\['low'\]) / candle\_range  
      
    \# e) Microestructura simulada (Volume Imbalance aproximado para barras OHLCV)  
    \# Si sube el precio, clasificamos volumen mayoritario como compra y viceversa  
    price\_change\_sign \= np.sign(df\['close'\].diff().fillna(0))  
    df\['volume\_imbalance'\] \= price\_change\_sign \* df\['tick\_volume'\]  
    df\['cum\_volume\_imbalance'\] \= df\['volume\_imbalance'\].rolling(window=15).sum() / (df\['tick\_volume'\].rolling(window=15).sum() \+ 1e-8)  
      
    \# f) Características temporales cíclicas (Evita discontinuidades en 23:59 \-\> 00:00)  
    df\['hour'\] \= df.index.hour  
    df\['day\_of\_week'\] \= df.index.dayofweek  
      
    df\['sin\_hour'\] \= np.sin(2 \* np.pi \* df\['hour'\] / 24.0)  
    df\['cos\_hour'\] \= np.cos(2 \* np.pi \* df\['hour'\] / 24.0)  
    df\['sin\_day'\] \= np.sin(2 \* np.pi \* df\['day\_of\_week'\] / 7.0)  
    df\['cos\_day'\] \= np.cos(2 \* np.pi \* df\['day\_of\_week'\] / 7.0)  
      
    \# g) Z-Scores estadísticos (Estacionaridad del volumen y volatilidad)  
    vol\_mean \= df\['tick\_volume'\].rolling(window=20).mean()  
    vol\_std \= df\['tick\_volume'\].rolling(window=20).std() \+ 1e-8  
    df\['volume\_zscore'\] \= (df\['tick\_volume'\] \- vol\_mean) / vol\_std  
      
    df.dropna(inplace=True)  
    return df

\# \==========================================  
\# MUESTREO DE DATOS ALTERNATIVOS: BARRAS DE VOLUMEN  
\# \==========================================  
def sample\_to\_volume\_bars(df, volume\_per\_bar=2000):  
    """  
    Sintetiza la serie temporal en barras de volumen uniforme para mejorar la  
    estacionaridad e información uniforme del conjunto de datos para Machine Learning.  
    """  
    df \= df.copy()  
    df\['cum\_vol'\] \= df\['tick\_volume'\].cumsum()  
    df\['bar\_group'\] \= (df\['cum\_vol'\] // volume\_per\_bar).astype(int)  
      
    \# Agregar estadísticas por barra de volumen  
    volume\_bars \= df.groupby('bar\_group').agg({  
        'open': 'first',  
        'high': 'max',  
        'low': 'min',  
        'close': 'last',  
        'tick\_volume': 'sum',  
        'rolling\_volatility': 'last',  
        'ema\_ratio': 'last',  
        'candle\_body\_norm': 'mean',  
        'cum\_volume\_imbalance': 'last',  
        'sin\_hour': 'last',  
        'cos\_hour': 'last',  
        'sin\_day': 'last',  
        'cos\_day': 'last',  
        'volume\_zscore': 'last'  
    })  
      
    \# Asignar fecha promedio o de cierre del grupo como índice  
    time\_indices \= df.groupby('bar\_group').apply(lambda x: x.index\[-1\], include\_groups=False)  
    volume\_bars.index \= pd.DatetimeIndex(time\_indices)  
    volume\_bars.index.name \= 'time'  
    return volume\_bars

\# \==========================================  
\# ETIQUETADO ADAPTATIVO: TRIPLE BARRERA  
\# \==========================================  
def get\_triple\_barrier\_labels(df, hold\_period\_bars=30, vol\_multiplier=1.5):  
    """  
    Aplica el método de la triple barrera de Marcos López de Prado.  
    Coloca barreras de Take-Profit y Stop-Loss dinámicas basadas en la volatilidad.  
    La barrera vertical actúa como fecha límite temporal.  
    """  
    df \= df.copy()  
    labels \=  
    timestamps \= df.index  
      
    \# Volatilidad diaria dinámica ajustada por barra  
    volatility \= df\['rolling\_volatility'\].values  
    close\_prices \= df\['close'\].values  
      
    for i in range(len(df) \- hold\_period\_bars):  
        t0\_price \= close\_prices\[i\]  
        t0\_vol \= volatility\[i\]  
          
        \# Si la volatilidad es inválida, se salta el registro para evitar sesgar el objetivo  
        if np.isnan(t0\_vol) or t0\_vol \<= 0:  
            labels.append(0)  
            continue  
              
        upper\_barrier \= t0\_price \* (1 \+ vol\_multiplier \* t0\_vol)  
        lower\_barrier \= t0\_price \* (1 \- vol\_multiplier \* t0\_vol)  
          
        \# Evaluar la trayectoria futura dentro de la ventana de expiración  
        future\_prices \= close\_prices\[i+1 : i \+ 1 \+ hold\_period\_bars\]  
          
        barrier\_touched \= 0  \# Default: Expira el tiempo (etiqueta 0\)  
          
        for price in future\_prices:  
            if price \>= upper\_barrier:  
                barrier\_touched \= 1  \# Toca Barrera de Profit antes  
                break  
            elif price \<= lower\_barrier:  
                barrier\_touched \= \-1  \# Toca Barrera de Loss antes  
                break  
                  
        labels.append(barrier\_touched)  
          
    \# Rellenar con ceros las barras finales donde no se puede calcular el futuro completo  
    labels.extend( \* hold\_period\_bars)  
    df\['target'\] \= labels  
    return df

\# \==========================================  
\# INTEGRACIÓN DE FUENTES DE DATOS COMPLEMENTARIAS  
\# \==========================================  
def integrate\_economic\_sentiment(df):  
    """  
    Integra datos sintéticos macroeconómicos y sentimiento con marcas de tiempo asíncronas  
    utilizando pd.merge\_asof con dirección hacia atrás para mitigar el sesgo de look-ahead.  
    """  
    df \= df.copy().sort\_index()  
      
    \# Generar un dataset de eventos macroeconómicos asíncronos (ej. cada pocas horas o días)  
    np.random.seed(99)  
    event\_times \= pd.date\_range(start=df.index \- timedelta(days=1), end=df.index\[-1\], freq='12H')  
      
    \# Puntuación de sentimiento cuantitativo de noticias macroeconómicas (-1.0 muy bajista, \+1.0 muy alcista)  
    sentiment\_data \= pd.DataFrame({  
        'news\_sentiment': np.random.uniform(-0.8, 0.8, size=len(event\_times)),  
        'economic\_surprise\_index': np.random.normal(0.0, 1.0, size=len(event\_times))  
    }, index=event\_times)  
    sentiment\_data.index.name \= 'event\_time'  
    sentiment\_data \= sentiment\_data.sort\_index()  
      
    \# Fusión asof estricta: une con el último evento disponible previo al timestamp del mercado  
    merged\_df \= pd.merge\_asof(  
        df,  
        sentiment\_data,  
        left\_index=True,  
        right\_index=True,  
        direction='backward'  
    )  
      
    \# Tratar los valores vacíos iniciales aplicando ffill y posteriormente bfill  
    merged\_df\['news\_sentiment'\] \= merged\_df\['news\_sentiment'\].ffill().fillna(0.0)  
    merged\_df\['economic\_surprise\_index'\] \= merged\_df\['economic\_surprise\_index'\].ffill().fillna(0.0)  
      
    return merged\_df

\# \==========================================  
\# EJECUCIÓN PRINCIPAL DEL PIPELINE  
\# \==========================================  
if \_\_name\_\_ \== "\_\_main\_\_":  
    print("="\*80)  
    print("INICIANDO PIPELINE DE TRADING CUANTITATIVO Y DATA ENGINEERING")  
    print("="\*80)  
      
    \# Paso 1: Ingesta / Extracción desde MT5 o Simulación robusta  
    df\_raw, source\_is\_mt5 \= extract\_or\_simulate\_data(symbol="EURUSD", days\_history=15)  
      
    \# Paso 2: Feature Engineering Vectorizado  
    df\_features \= calculate\_advanced\_features(df\_raw)  
    print(f" Features vectorizadas computadas. Dimensiones: {df\_features.shape}")  
      
    \# Paso 3: Agregación en Barras de Volumen para mitigar el ruido temporal  
    df\_sampled \= sample\_to\_volume\_bars(df\_features, volume\_per\_bar=2500)  
    print(f" Datos muestreados en Barras de Volumen. Dimensiones: {df\_sampled.shape}")  
      
    \# Paso 4: Fusión asíncrona asof con Sentiment y Macro (Sin Look-Ahead Bias)  
    df\_enriched \= integrate\_economic\_sentiment(df\_sampled)  
    print(f" Datos complementarios fusionados con éxito. Dimensiones: {df\_enriched.shape}")  
      
    \# Paso 5: Etiquetado adaptativo por Triple Barrera de De Prado  
    df\_final \= get\_triple\_barrier\_labels(df\_enriched, hold\_period\_bars=15, vol\_multiplier=2.0)  
    print(f" Etiquetado completado mediante Triple Barrera.")  
      
    print("\\n" \+ "="\*40)  
    print("RESUMEN GENERAL DEL DATASET ALINEADO PARA MACHINE LEARNING")  
    print("="\*40)  
    print(f"Número total de muestras de entrenamiento: {len(df\_final)}")  
    print(f"Distribución de la variable objetivo (clases):")  
    print(df\_final\['target'\].value\_counts())  
      
    print("\\nVista de Atributos Generados:")  
    columnas\_muestra \= \[  
        'close', 'rolling\_volatility', 'candle\_body\_norm',   
        'cum\_volume\_imbalance', 'news\_sentiment', 'economic\_surprise\_index', 'target'  
    \]  
    print(df\_final\[columnas\_muestra\].tail(8))  
      
    print("\\n Pipeline finalizado con éxito. El dataset se encuentra listo para Purging y Modelado.")  
    print("="\*80)

## **Conclusiones y recomendaciones operativas**

El diseño de un pipeline de ingeniería de datos para trading algorítmico exige un rigor metodológico superior al desarrollo clásico de software de machine learning, dada la naturaleza asíncrona y adaptativa de los mercados financieros.1 A modo de síntesis estratégica para optimizar la construcción de sistemas bajo la arquitectura MetaTrader 5 y Python, se proponen las siguientes directrices clave:

* **Minimizar la dependencia de índices cronológicos:** La aserción fundamental de que los mercados operan bajo el tiempo físico induce a una ineficiencia en el modelado.2 Se recomienda la migración sistemática desde las barras basadas en tiempo hacia arquitecturas de **Barras de Valor Monetario (Dollar Bars)** o barras de volumen.1 Estas barras normalizan la densidad informativa y proveen propiedades estadísticas significativamente más aptas para modelos de aprendizaje supervisado.2  
* **Tratar la no-estacionariedad de forma proactiva:** Los precios crudos son no-estacionarios y los retornos tradicionales destruyen por completo la memoria de largo plazo de la serie de tiempo.1 Los investigadores deben evaluar técnicas de **diferenciación fraccional (fractional differentiation)** (comúnmente optimizada a niveles de ![][image46]), logrando alcanzar estacionariedad en las series temporales preservando paralelamente la correlación y memoria del comportamiento histórico.1  
* **Aislar estrictamente los conjuntos de validación:** El autoengaño estadístico debido al solapamiento de etiquetas es el causante de que gran parte de los algoritmos de trading sistemático fallen en entornos reales.2 Es obligatorio integrar funciones de **Purga (Purging) y Embargo** en el proceso de validación cruzada 2, evitando que cualquier traza de información futura influya de manera indirecta en los estimadores de los modelos predictivos.37  
* **Desplegar bases de datos optimizadas para series de tiempo:** Para infraestructuras de alta frecuencia o múltiples instrumentos, el almacenamiento columnar mapeado en memoria (como **QuestDB** y almacenamiento de datos fríos en **Apache Parquet**) reduce drásticamente el espacio de almacenamiento y acelera los tiempos de procesamiento respecto a bases de datos relacionales tradicionales o formatos de texto plano CSV.25

#### **Fuentes citadas**

1. Advances in Financial Machine Learning \- Grokipedia, acceso: junio 28, 2026, [https://grokipedia.com/page/Advances\_in\_Financial\_Machine\_Learning](https://grokipedia.com/page/Advances_in_Financial_Machine_Learning)  
2. The reasons most ML quant funds fail (human-generated summary ..., acceso: junio 28, 2026, [https://fluentnumbers.medium.com/the-reasons-most-ml-quant-funds-fail-human-generated-summary-of-marcos-lopez-de-prado-lecture-e7d6bd95ef50](https://fluentnumbers.medium.com/the-reasons-most-ml-quant-funds-fail-human-generated-summary-of-marcos-lopez-de-prado-lecture-e7d6bd95ef50)  
3. Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5](https://www.mql5.com/en/docs/python_metatrader5)  
4. MetaTrader 5 Python Integration \- Grokipedia, acceso: junio 28, 2026, [https://grokipedia.com/page/MetaTrader\_5\_Python\_Integration](https://grokipedia.com/page/MetaTrader_5_Python_Integration)  
5. Releases · bahadirumutiscimen/silicon-metatrader5 \- GitHub, acceso: junio 28, 2026, [https://github.com/bahadirumutiscimen/silicon-metatrader5/releases](https://github.com/bahadirumutiscimen/silicon-metatrader5/releases)  
6. MetaTrader Portfolio Optimizer: Quantitative Trading MCP Server \- Erick Santana, acceso: junio 28, 2026, [https://ersantana.com/quantitative-trading/metatrader\_portfolio\_optimizer](https://ersantana.com/quantitative-trading/metatrader_portfolio_optimizer)  
7. AIOMQL-The Complete Guide to Building Algorithmic Trading Bots with Python & MetaTrader 5 \- DEV Community, acceso: junio 28, 2026, [https://dev.to/akaichinga/aiomql-the-complete-guide-to-building-algorithmic-trading-bots-with-python-metatrader-5-3bgh](https://dev.to/akaichinga/aiomql-the-complete-guide-to-building-algorithmic-trading-bots-with-python-metatrader-5-3bgh)  
8. AIOMQL \- DEV Community, acceso: junio 28, 2026, [https://dev.to/akaichinga/aiomql-5c6d](https://dev.to/akaichinga/aiomql-5c6d)  
9. Automated Trading using MT5 and Python \- Quantra by QuantInsti, acceso: junio 28, 2026, [https://quantra.quantinsti.com/glossary/Automated-Trading-using-MT5-and-Python](https://quantra.quantinsti.com/glossary/Automated-Trading-using-MT5-and-Python)  
10. SGTYang/VPIN: Volume Synchronized Probability of Informed Trading \- GitHub, acceso: junio 28, 2026, [https://github.com/SGTYang/VPIN](https://github.com/SGTYang/VPIN)  
11. yt-feng/VPIN: Order flow toxicity; Volume-Synchronized Probability of Informed Trading, acceso: junio 28, 2026, [https://github.com/yt-feng/VPIN](https://github.com/yt-feng/VPIN)  
12. francescodisalvo05/66DaysOfData: \#66DaysOfData challenge in Financial Machine Learning and NLP \- GitHub, acceso: junio 28, 2026, [https://github.com/francescodisalvo05/66DaysOfData](https://github.com/francescodisalvo05/66DaysOfData)  
13. CFTC COT Report Tracker \- Weekly Positioning API in Python \- Apify, acceso: junio 28, 2026, [https://apify.com/wiry\_kingdom/cftc-cot-report-tracker/api/python](https://apify.com/wiry_kingdom/cftc-cot-report-tracker/api/python)  
14. cot-reports \- PyPI, acceso: junio 28, 2026, [https://pypi.org/project/cot-reports/](https://pypi.org/project/cot-reports/)  
15. Mcamin/cftc-cot: Python library for downloading, storing, and unpacking official CFTC Commitments of Traders (COT) report archives. \- GitHub, acceso: junio 28, 2026, [https://github.com/Mcamin/cftc-cot](https://github.com/Mcamin/cftc-cot)  
16. The Data Infrastructure Behind Algorithmic Trading: Understanding Financial Data APIs, acceso: junio 28, 2026, [https://www.interactivebrokers.com/campus/ibkr-quant-news/the-data-infrastructure-behind-algorithmic-trading-understanding-financial-data-apis/](https://www.interactivebrokers.com/campus/ibkr-quant-news/the-data-infrastructure-behind-algorithmic-trading-understanding-financial-data-apis/)  
17. Stock Forecasting Using Sequential Models and GNN \- Preprints.org, acceso: junio 28, 2026, [https://www.preprints.org/manuscript/202602.1927](https://www.preprints.org/manuscript/202602.1927)  
18. ToyotaVision: Financial Insights & Forecasts \- Kaggle, acceso: junio 28, 2026, [https://www.kaggle.com/code/pinuto/toyotavision-financial-insights-forecasts](https://www.kaggle.com/code/pinuto/toyotavision-financial-insights-forecasts)  
19. Exploring Stock Price Movements After Major Events | by Steven Wang \- Medium, acceso: junio 28, 2026, [https://medium.com/@steven\_wang/exploring-stock-price-movements-after-major-events-8b35c318ba76](https://medium.com/@steven_wang/exploring-stock-price-movements-after-major-events-8b35c318ba76)  
20. Futures Rollover — arbitragelab 1.0.0 documentation \- the Statistical Arbitrage Laboratory, acceso: junio 28, 2026, [https://hudson-and-thames-arbitragelab.readthedocs-hosted.com/en/latest/data/futures\_rollover.html](https://hudson-and-thames-arbitragelab.readthedocs-hosted.com/en/latest/data/futures_rollover.html)  
21. Build Back Adjusted Continous Futures contract from Historical Data \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/24977952/build-back-adjusted-continous-futures-contract-from-historical-data](https://stackoverflow.com/questions/24977952/build-back-adjusted-continous-futures-contract-from-historical-data)  
22. Comparing the return of different roll strategies \- Quantitative Finance Stack Exchange, acceso: junio 28, 2026, [https://quant.stackexchange.com/questions/16175/comparing-the-return-of-different-roll-strategies](https://quant.stackexchange.com/questions/16175/comparing-the-return-of-different-roll-strategies)  
23. Continuous Futures Contracts for Backtesting Purposes \- QuantStart, acceso: junio 28, 2026, [https://www.quantstart.com/articles/Continuous-Futures-Contracts-for-Backtesting-Purposes/](https://www.quantstart.com/articles/Continuous-Futures-Contracts-for-Backtesting-Purposes/)  
24. The Best Time-Series Databases Compared (2026) \- Tiger Data, acceso: junio 28, 2026, [https://www.tigerdata.com/learn/the-best-time-series-databases-compared](https://www.tigerdata.com/learn/the-best-time-series-databases-compared)  
25. Why Parquet Matters for Time Series and Financial Services \- QuestDB, acceso: junio 28, 2026, [https://questdb.com/blog/why-parquet-matters-for-time-series-and-finance/](https://questdb.com/blog/why-parquet-matters-for-time-series-and-finance/)  
26. Comparing InfluxDB, TimescaleDB, and QuestDB Time-Series Databases, acceso: junio 28, 2026, [https://questdb.com/blog/comparing-influxdb-timescaledb-questdb-time-series-databases/](https://questdb.com/blog/comparing-influxdb-timescaledb-questdb-time-series-databases/)  
27. TimescaleDB vs QuestDB: 2026 Benchmark Results (Clear Winner), acceso: junio 28, 2026, [https://questdb.com/blog/timescaledb-vs-questdb-comparison/](https://questdb.com/blog/timescaledb-vs-questdb-comparison/)  
28. Picking the Fastest Database to Store Time-Series Data | by Sergey Makhnist \- Medium, acceso: junio 28, 2026, [https://medium.com/@smakhnist/picking-the-fastest-database-to-store-time-series-data-411ca3651277](https://medium.com/@smakhnist/picking-the-fastest-database-to-store-time-series-data-411ca3651277)  
29. The best python tools to analyze alternative investment data for $0 \- Informa Connect, acceso: junio 28, 2026, [https://informaconnect.com/the-best-python-tools-to-analyze-alternative-investment-data-for-0/](https://informaconnect.com/the-best-python-tools-to-analyze-alternative-investment-data-for-0/)  
30. Top Tools for AI Test Data Versioning \- Ranger, acceso: junio 28, 2026, [https://www.ranger.net/post/top-tools-ai-test-data-versioning](https://www.ranger.net/post/top-tools-ai-test-data-versioning)  
31. Best 8 Data Version Control Tools for Machine Learning 2023 | DagsHub, acceso: junio 28, 2026, [https://dagshub.com/blog/best-data-version-control-tools/](https://dagshub.com/blog/best-data-version-control-tools/)  
32. How to Speed Up Pandas Data Operations Using Vectorized Operations \- In Plain English, acceso: junio 28, 2026, [https://plainenglish.io/python/pandas-how-you-can-speed-up-50x-using-vectorized-operations](https://plainenglish.io/python/pandas-how-you-can-speed-up-50x-using-vectorized-operations)  
33. Order Flow Toxicity of the Bitcoin April Crash \- Jonathan Heusser, acceso: junio 28, 2026, [https://jheusser.github.io/2013/10/13/informed-trading.html](https://jheusser.github.io/2013/10/13/informed-trading.html)  
34. Top 5 tips to make your pandas code absurdly fast \- Tryolabs, acceso: junio 28, 2026, [https://tryolabs.com/blog/2023/02/08/top-5-tips-to-make-your-pandas-code-absurdly-fast](https://tryolabs.com/blog/2023/02/08/top-5-tips-to-make-your-pandas-code-absurdly-fast)  
35. Pandas Vectorization: The Secret Weapon for Data Masters — CWN \- Medium, acceso: junio 28, 2026, [https://medium.com/@codewithnazam/pandas-vectorization-the-secret-weapon-for-data-masters-cwn-f4b4452e3627](https://medium.com/@codewithnazam/pandas-vectorization-the-secret-weapon-for-data-masters-cwn-f4b4452e3627)  
36. Vectorization and parallelization in Python with NumPy and Pandas, acceso: junio 28, 2026, [https://datascience.blog.wzb.eu/2018/02/02/vectorization-and-parallelization-in-python-with-numpy-and-pandas/](https://datascience.blog.wzb.eu/2018/02/02/vectorization-and-parallelization-in-python-with-numpy-and-pandas/)  
37. Meta labeling in Cryptocurrencies Market. | by Quang Khải Nguyễn ..., acceso: junio 28, 2026, [https://medium.com/@liangnguyen612/meta-labeling-in-cryptocurrencies-market-95f761410fac](https://medium.com/@liangnguyen612/meta-labeling-in-cryptocurrencies-market-95f761410fac)  
38. End-to-end lineage with DVC and Amazon SageMaker AI MLflow apps \- AWS, acceso: junio 28, 2026, [https://aws.amazon.com/blogs/machine-learning/end-to-end-lineage-with-dvc-and-amazon-sagemaker-ai-mlflow-apps/](https://aws.amazon.com/blogs/machine-learning/end-to-end-lineage-with-dvc-and-amazon-sagemaker-ai-mlflow-apps/)  
39. treeverse/dvc: Data Versioning and ML Experiments \- GitHub, acceso: junio 28, 2026, [https://github.com/treeverse/dvc](https://github.com/treeverse/dvc)  
40. Pandas for Financial Data \- MLQ.ai, acceso: junio 28, 2026, [https://mlq.ai/academy/lesson/python-quant-finance-pandas-for-financial-data/](https://mlq.ai/academy/lesson/python-quant-finance-pandas-for-financial-data/)  
41. GitHub \- Snowflake-Labs/sfguide-quantitative-research-ai-functions-and-cortex-code, acceso: junio 28, 2026, [https://github.com/Snowflake-Labs/sfguide-quantitative-research-aisql-cortex?utm\_cta=website-ai-product-resource-gen-ai-ml-school-academy\&mkt\_tok=odyzlu9ury0wmzqaaagikhk6cg5cvjoscq77sofiplg4frlzqrkr9ozsh2wibwtfygiabkjyj4wvzprqzl8\_4pmbpoqlwzox-4\_zsw](https://github.com/Snowflake-Labs/sfguide-quantitative-research-aisql-cortex?utm_cta=website-ai-product-resource-gen-ai-ml-school-academy&mkt_tok=odyzlu9ury0wmzqaaagikhk6cg5cvjoscq77sofiplg4frlzqrkr9ozsh2wibwtfygiabkjyj4wvzprqzl8_4pmbpoqlwzox-4_zsw)  
42. Trading Crude Oil with COT Data: Building a Positioning-Based Strategy in Python, acceso: junio 28, 2026, [https://www.insightbig.com/post/trading-crude-oil-with-cot-data-building-a-positioning-based-strategy-in-python](https://www.insightbig.com/post/trading-crude-oil-with-cot-data-building-a-positioning-based-strategy-in-python)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOAAAAAXCAYAAAASukNAAAAEw0lEQVR4Xu2bWYgdVRCGfzeMCy5RcDco+qLgS0BQVJAgovjgg+BuRJCAggmICwSDoOCKGBQFFR13EFdEBEVHRRQiEY3gvivuifsuav3UqXR1pc+dvnMzd+bePh/85Jyq06f7Vnf1WXoCFAqFQqFQKBQKhUKhq1wv+lH0X9LvonXB9sD61oXp8g2qeFKML+P8V6r/Idpqfetu8Xc0dBF7MCILoPanoqPQN/dAY7ltdCAf/y7Q1d9dg0F4ORoTXX44Nia94vg91Ld3dHSAXEw6w0nQIBwdHdBpUa8Hp9AexjA33bIYbxEdHaDzz9abyAfhEajv+Ogo9MUu0DheER3QpKOPo2AXyT17nSE3wh0Jta+MjkLf3ASN5TbRAd2I+SUaO0TTs9cpLAF/gL6FuSPH+huinVy7ceYg0d0Z3SW6U3SH6HbRbaJb9bDWWIx/hu5+MuFY/0d0rms3zqxFFYc2elsPG29s/XdWdLRkM+jxs8FzmL1z94s9VDkWir4TTUZHYkL0YjT2wXbofX7jXwz/pdvmusaWdzB4AJ6Phj7hTZ8ug177MNgdep0cRXtxBvIJeILotGhsIDea8vybRmMDT0fDEBiFezhjTPVmHgaDnH+QYz37iK7uU23hlJXXuSA6Aqcin4BtuBD5BJzLbKx7OJLwx78fjQ1w+/wc6Dz+MGf3CWzTWa4do49wBLhS9Giyz3NtqPtTu8NFj4mugp7Psz/0r3W4LrsO9f53FX0qugj6lydzhRiHHCdCE3BV+vcV5/N9bCL6QHS26DfRftD2PpYGd1i53jwf2nbzZLd2l4u+hn6CejLZjkptyCfQDaQXRIcmW67P6dImNmPJcuiPXxIdDfzqyjFgvr4YVQIS7/Nl3jgj9nepaEUqn4dqitu03sz1z++X3FSabeya43U3wQTM/R6bxpKbRQen8vbQBCST2HAEjOeN/S8SHSPaK9neRZWAXJ5Yfxej+oTSq8/pMOjxI8cN0N047nhyR47JNdU6jOuHa9H8zdDXT0Y+AT9OdSbffGeP/ZEDRA9Dr+/DZLsAukPrsWO5Por9xPqwYVz5EuAo/hN0FrGs1qIOE9Dv/PnrZ7ysvmMqU9ylNSZRT8A9sWEMWLe1YPSRNagS0Lc1puqzF5+huu42Wq2HFQ5BPUGbboDBzQImqeF9/AbG6RNHNW+3sm1S8EY9lMrHiT5KZU5f+c3MY8ee7spGrM91TkH+5WVJR/hRn/AlxZ3Ty1L9WdHSVOZ0kaNajAHrW7ty5HXUE5AjuGeqPgszwKvQb2DEplS7Ve7aDeHNe8/Vve8LV/YjmbUxG+tMVHIjdB3C6RBtvr/4MPgy14p8OEcJ7oK+5er+9/gR8F5UicGp9i3OfkkqH5H+9X3wmF4vUuJHwGdQH2Ht/vXqszBDfC56CfpXMRPQtYIRbySnDvzfE48nn/mfEH0r+kp0ZrKRB6FTrz1SnZswvKlMvH2hU9bFyXeg6E/om/pY1PvnW5hJx4f4mmQbFTj6cUnA6SqTgBtNLHMKu7PzvSa6L4mfDL7kwQ5uPvkZCGFsObJy88uw/tkvE58wpmbjOckEtC03tzxNfRaGjG0ExAQsFAozzA7QxNsS9alloVAYElyTcXOgUCi05H8l2YY+8Qal3gAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOAAAAAhCAYAAADAmafwAAAFmElEQVR4Xu2cZ6gdVRDHxxKNGmwR7AbbFwW/CIKigojY8kHBoLFFBBELahAboigq9oZiRMW82IJiRUVU9KmIgqJoAmoSe++9K+r8mTO5s/N29+3m+e69uzs/GN45M+ee3Xd255Q5516iIAiCIAiCIAiCoKtcw/IDy79JfmP51unuWV46WFG+pF57QtC+aOc/U/53ljWWlw46h74Ynhkk+ie8IajNHSRtOc0bqLj9g46Ah/+iVybi5fh/KGvH70hsW3hD0H4OIXn4e3sDybSo7MUJqoM2/MsrE9rGU7yhhRzoFY5ZXtF23qBiB3uAxHaANwS12JCkHS/2BhKngw2jYBe4j+VEr0xcznKpV7adohFuDxL9td4Q1OYGkrZcyxtIAjE/e2XLeZjlNKe7kuUqp+sE6oDfk/TCiMghv5hluinXZnZgub1AbmNZwDKf5VaWW1hulo9VRtv4J5LoJxwO+b9ZTjDlusQjLKenNJyvkx29rv+O9oaKrEL5o2c/eIYGd+26FM0ylB1ZvmYZ9YbECMvzXlmDtan8+so/1N9OF074HMkMoZMsoWoPpoxnvaImeOgrykTvvR9sQnKfGEXLOJKKHfAglsO9Moei0RTXX9krc3jSKyYZzCreYjnHG7rCeD1zP5jI9SfyWcuWLJfVlKpgyor7nOENjsOo2AGrgOlckQMOI3C+q1Mae6RnGVtnwIvxtlfmgPD58SzfsOxq9NaBdTqLtaO3AYwAl7A8mPRTTRnIwlRuN5aHSKJhuJ5lW5LTOliXYcFu69+I5UOWM0hOngwLvh2KOJjEAV9Kf182NlvHSizvsBzD8ivLNiTlbVsqiLBivXkqSdlVk17LXcjyBckW1GNJt1cqAz4gmR5imrhL0hXVWQespdX5FDihD8y0mrNJGvxYb8jhF5P2L5PNz6GeAwJrs2k8OMXXdx7LuSl9EvWmuHnrzaL6sX+JoNKg0Xv2950HHLDo/9FpLJjHslNKr0PigGCUxo6A/rq+/j1Z9mXZPOmWUs8BsTzR+s6k3hZKWZ1VuJHlIq9MoGOd65Vt4zqSaBwinojIwbnGW4dh/XAF5e8Z2vxsKnbA91Mezre+0fv6wHYs95Pc37tJh94REVqLfhbrI1+Pz/cbtCs6AYziP5LMIk7JlMgCB8R6SLH3j/bS/HopDUGUVhmlrANuRmPbAHldC3obWEQ9B7RllfHqrMJxXuFApxsYdqasg+Y9AAXBAjipYm3YA8P0CQ1s9ZrWIMVHJJu1YCbLeymN6Sv2zCz62SNMWvH5YedQKu681OkANvUBOilETi9I+adZTk5pTBcxqvk2QH5Nk/a8TlkHxAhuGa/OYBJ4lWTBDHRKtXHPnHkgeHjLTN7aPjVpO5JpGdUhD0cF15OsQzAdgs7W518Gm8ZaES9nk0AU9E2Tt/+PHQHvpJ5jYKp9k9FrNHH39NfWgc+UdaTAjoBPUXaE1edXVmcwSXzM8gLJZukIyVpB8Q/yFZJvT+C0A2xqf5TlK5bPWY5KOnAvydRr05RHEAYPFY63FcmUdU6ybc/yB0lPvR9l60cvDKfDS4wjTU0Cox+WBJiuwgkQaEIaU9gNjO01lruSYMvgM3zYgOCTnYEAtC1GVgS/FK0f9cLxAdpUdbgmGCEpi+CWJa/OoM9oIMA7YBAEk8y6JI63OmWnlkEQ9AmsyRAcCIIgCIL28AnV29sZFAgO5P3EQxA0FuzDbe2VQwy+0hP7UEEruJua9ytoCARFJDZoPDhT2NQXGXuMODAQBI0Fzre/VzYI3L89oRMEjcGfxG8i82nsYe0gaARwPhwJqwJ+vwMn/XHsC9+swNdjcHRs0D+og6gt/g+c2A+CxqCnWlbzhhJQfp8cXd6vfvUT3EOsBYNG8TjVn3768jr64NvSg+R8GntvQTA0/AeC2JVvJya9MAAAAABJRU5ErkJggg==>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAAA3klEQVR4XmNgGAWUgnlA/BmI/0PxAhRZCPjLgJAHYWdUaUyArBgb2AfEKuiC2AAjEG8H4vUMEMOCUKXBAJclGCAfiE2gbFyu+4MugAu8RWJ/YIAYxockpgbEnUh8vADZJaBwAfFvIoktA2IeJD5OAAqvzWhi6F7F5m2sADm8kMVABnRD+b+Q5PCCd+gCUABznTYQt6DJ4QS4vLCbASJ3D4g50eSwAhYg3osuCAVMDJhhhxMwA/EbID6JLoEEvgHxD3RBdLAKiD8yQNIXKF2B8h42oA/E2eiCo2AUDGkAAM4NNN65dbHtAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAAbElEQVR4XmNgGAXUBAZA3AfErFB+EhB3IKQhgA2IDwNxCBD/B+LvQCzFAFEM4sPBfiidCZWQgfJB7FtQNhjUQul7DKgmcCCxUQBI0QF0QWwApNAeXRAdRDCgORwXuMxApMI/QDwFXXAUDCAAAAtnFHCYMWtKAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAxCAYAAABnGvUlAAAFX0lEQVR4Xu3cWchtcxjH8T+Zp4gy52RIGYoMN6YXiZAUchDehDJckEhIxxRSKG6MRYQbF+TC3aHIjaJIhijzmClTxufX+j/2s5/zX8vOu99693m/n3pa///zX2vvtdY+tZ7zX2u9pQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAsHzta7FRTs6o7XJiER0a2keF9izZOicW0d85kXyXE+aX0P4+tAEAmGnvlfaF8bTSzovyP+VkpbE9avuw2t9yNLzkxGNUW8XoYsjFxawWbPF8PWtxaehP06s50SP/G/0t9W9PfQAAZtKLFndYfJ3yd5c1L4bumNI/1sort09OLhGt/Z229SyuSLm1oWBbTCoGJ3GsxVzo/x7arT4AADNJBZvEC/HGjVymsbNzsrS3eaC08//X+RYPW2xo8ZjF+jV/lcXuvlJ1sMVzKSdPWWxTRvulmbWbLPb+d41SnrFYHfpyncVFpZs1fDKNnWnxrsVdKf9h6kss2O6sy/NCbprmLe6rbf0WW9T2xRa31Lbb1eLTlJMrLfYs47/jJRYrQ3+VxcehL/G3etxigzCmc/C6xSMhJ4+W0b9Bd21dXjOW7fzR0xbt3/EpBwDAzGkVbH82cu6eunyitMdbufnSzqvQ+mAghsTPU/ulRv6F0hVsOd/X1m3Lw2v7FYttazuuo9nI+JxU67NUbJzTyEdesGnskLr0/mLQ52rW1Nvf1PYRFuvW9g2lK3qldVy5LdfX5W2l/xj6tp+kLZ+XrmDz/BdhTOL6f4W2m/T2KgAAS5YXbLuV0YzZXnWZL5wydGGVVu7q0s4vRN9+5LaKLsWPpZvdUe6MtI57s4wKtiiuM1/Gi8nWcW1Sxp9Za63jBdsKi/ctjh4NDdIxHNgTQ/J5iebqMp6v50u3Typ2fHbO14m8YIt0G3K/0B/6btEt46F1fFzntWVoW2nlAACYKV6wiS5s56Z+dorF9jU0fsH4cHMbzUh9m5ML1HeRVttnjFr7otyRqe90e84LNq3zdG3Hdc6yeCP083fvUtvxDcXWfsRboq3x13JigfJ+RnG2L1NOM2+xH3nBpuP2Md2W3L+2pe+71dbsYiuftXLuv7bNt0kBAJg5L4e2LnY3pn70VeqfXNZcJ/dXlf43Shei7yKttj/TphcpLqxtPUMlenM1vkkYt1Uh5gVb/kzRDKSeyXq7MabcgyGvY/axfE5kqGDbqua0nJbW8Ti9RCIq3vWcmdOf8IjP+Une1gu2vM5BFg/1jIlm7fSGcsx/Vtv5lqfk741an+/0H4v8nB4AADNFs14fldGF8sQw9mUd84unijU9UP5D7e9YumeLtI6WooulQs8RqShSfvM6Nk3aF32vvkO3Hn0fdq7t+ND8/aXbpxNCTm8WKqeXDHyfVaxoOz8Xm9X8O6UrAH+t+U9Kdx70fJyeA9P3eUGq267+XbotuFPNz1scUNvOC7YdLO6NA5U/bzYNvp/6LbWP8TfXMeuYVGCJXqrQMVxe++IvG+hFDT9fos/T5+h2+jppzJ8l6/utRG2tf1npXibwmc8VZfyt2tMtTg39aFOLW0M/F2zxPyQAAACDciERZ9iyk+pydUwuM/l89fk59fN2uQ8AANDr5tQfKtj0kL1m8Jaz48pks7P5dmcs0DRjp3MJAAAwsbdCey600aa/sTek9ffi/E/SiF6QAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALA2+QeS6lWQbFumkwAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAZCAYAAAA4/K6pAAAAsUlEQVR4XmNgGAXYwHMg/o+EPwHxGyB+jSQmAleNBYAUbEYXBIJjDBA5f3QJZCAPxPfQBYFgGgNEcxu6BDrYBsQcaGJxDBDNu9DEsQJlNL4hA0TzAzRxooAQA0Tzd3QJYgATAyLEyQIwzYxo4gFofKzgFwNEMz+aeDoQW6GJoQBBBojGn+gSDBCX4PUOTAE2RVwMEPFV6BLIAKb5DhDfAuK7QPwMSRyEeeCqR8EooDYAAMkDLOGyGr/bAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABK0lEQVR4Xu2UPUsDURBFbxBJKzYR7NLZKFjbhHSphOB/SC1W+gcsbBRS2WplIySkTG0bULARGxEFBVsLP2Z2dsO82btiYSPsgcvyzsybfewuC9T8JzYkr5IvyZVkKS3/SEdyC9t7HmoJA8mJW5/BNm06V8Wu5NOtdZbupWghFpljaM8acYfBZTygPPQ3N9oG73kH9yX2YY29WAhMwQfeg/uE4pTHsUB4Ax94A+7nHEkuJB+Sbqgxqh7vDNyXWIU1jmMh8Ag+8BrcU6pO66l6R3fgPntUp8EVN9oK3nMAPpB+df1cxkLhFpzbkbTcWtGeZeJGwWVooenW67mbONfIXTzQE+xzLliB9Sw6N0dPpL8RbXjJr8Okw7iU7EUJ2/MMO5jubaflmpqav+Abwb1VfGd8leYAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABLUlEQVR4XmNgGAVDCegD8Vsg/g/EJ4BYAFUaJ/gAxM1ALAvELEBsAcRnUVQggQwgnoTEX8IAsdAISQwXAKlDx4UoKpAATAEhMWwApKYSiBcCcTqaHAZ4woBpKLEW/UEXIAVUMUAs8UKXwAJ+owsQCwIYIJZMRJfAAX4C8VQg/gjEKxggeq1QVGABPUC8Goj/ArEzmhwu8AmI3ZH4ZgwQy4SQxHACaQaI4i3oEkQCkF6QA4gCxCYGVnQBBjx6QUE1G00MptgGTRwZxDJA1JSiiWO1KBiHBEyMGUksFIjFkfhJDBA1oKBGBiCxW2hiYACSYEfi60HFtiGJMULFsDkIGYDiFV0MDkAp5B8DRMEbKA1KsuhgAxCXoImJMEDUg5I3iP7OAHHUKBgFo4DKAADpXE/SWA2LhgAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,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>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKAAAAAaCAYAAAAwnlc+AAADeElEQVR4Xu2aS6hOURTHl0ceESKllJGBxCUpEQZIIkSYIKRMRLpkQMpj4lWKlIh7RaQ8RpTHkIFHMTGQKAMzj8gzz/W39nb3t5zvfOfx3XMO1q/+fd/+77P3t85j77P2vpfIMAzDMIwK8pnVW5uGUQRbWD9Yz3WFYTj6sK6RPCd3WV1qq/OBTr16qLp64NjZ2iyYD6w72iyRgyTX5V9jKMl5+TfkIFfu+vuIHGxg7WJtI+n0aW11JKOpiQHkADEg/qqAeF5pswT6ayMn71nnlHeP9Ul5mQhHrJ8FuwVeFJeo/JE+hqoxCEKqMiB2s76SXKNmgPNaojyftuViNWtfUEbg6PRh4IXMInnt4hg8/XNYU2qO6Hwmk8RwnSSOua5cFkNIfn8VSTwLXLkKbKaOa5SVqSR94LqHrHD+QOWnIuoJ9rNgFK3UcVJnXHlGzRGdD35zE0kML10ZKgvc3I2sJyQxlR1PFMtIYlurKxKAGR1txyl/sfMnKD8xmFIPa5M5RNLxbV3h8Plf0lXQqRidZLWzTrCOs46xev5q1RjEsE6bJYJ4XmizYkwniRNvuqTsJGnTonzM9PCXKj8x9WY5EDcLXqD6dUXRaBA800YE6GN8QvV1beJAPOu16Win7KnKZW00gVGsL6yjuiKCNSTnNlb5i5yPhzo1yOUw+9SjjaTzG7qCxMerr0zOU/wg2KGNCGay5iXUYNemHrihcQNiqzYSsJ81n+LPMyvIW9+yruiKCHwOOFH5y52PLZrUJDmperMgvDQrvb0p1U+axYIYqrDd4Wk0IPLQzH5Hksx8SHmSgpQIMTRtFTyJ5DXaiIskPxAe60e63/qYRsUvQgBiwELEc9N9Yma/xVrZUVUIiOeNKgPcvPusR0FdWjLdZAXuE/pBPpcFtMUmewhmz0yxoVFaebDtEpZfB9+LBDEMd9/xN2xPG8mqFDe9SBDPafcdA3eE+/7OfYbXLC152vrVL/K4PETNdigvVF5DhtGfD1cSHUBjx2PnPQi8okF+hBiwF9ld1cHLlJfkAA+cv1Z6W2IP60hQxur/Y4w06DMtWAyhXTP3I8+yvrlP9J0mDfuvyHLDOpO88WRp36INoxi2k+wlYuVWBXqxvrvvWWPK8gAaJTGA5F/KqvR6QEqQJSe9SpJjY3MbK36sXg3DMAzDMAzDMAzD+Cv4CeUx+c+Y1gZNAAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADQAAAAWCAYAAACPHL/WAAAAsklEQVR4Xu3RPQrCQBiE4U8QwcbGVsHW3lLsrYScQTyB4AGsBC9g5QE8hK29Ip7EFOLPyG5wM4ilfIF54AUz2WaNmYiIVFgfdXn8osaDNz30RA90jb9n6YFEEw149OZ9EbZHN9ShPadnl8Y8RG10t/DFioalExVW58G7lX2+wo7esREP3hzQMnneWLhYlmyFBWrw6M2ah+ho4WJzNEEndCmdcOrXP95CW3RGU3onIiJ/9QLWaRs6747itwAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,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>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAxCAYAAABnGvUlAAAD1ElEQVR4Xu3cOagkRRgA4PJIxBsFD0QEESMvMFKR1cgDPALRRDwQNBADMTN5CGpqJibiEZmKiYk8NRAP8AADE1fxvvBAvK/6nS7f/2q7Z+axs6yz+33w01V/VVd3TzI/Pd1TCgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAsC8c3icOUn/2iTmOrXFin9yP3ugTAMCB5bsau/pk9XeNK2ucP7TvqnHZ0G4eqvHk0G7zztoa3idOKrPjHF3jiBrn1Pg5jR9S49san6dcE/s92icH+boW+SC1Y79LalwwtONzuGJo5zm3D+1dQ38nYn7eJ64x+hem3E7XBADWyINl8Zd9jJ+e+lEkhRtq3J/yYdFaqzB2jKtT++ay55ybhtzdXT68WePLGn/1AyPyumemduiP2UT+4tT/Ycgt67Aym39pyr2W2uHIGhtdDgA4AFw/bBcVDzF+WuqfN2z7gi2KhkVrrUI+RmtflHJRsH2S+uGLMl2w/VLj0LLcuec556Z26Pc/btj2BVv030r9ee4ZtvE55/XjDmOvPz4AcABoX/CxfSLle33B1kTB9nqZ7ft2jR+3jc63e0HME+eToxcFW3h+W3a6YDtq2Mb4GSk/Zux4zdRY5J+t8VSN92vct314rrxma9+ZctnU8QGANbYxbO8o87/sY2yqYMt32MbWaMXQKo0VMfHcWHPrsG1jL6R+X7C9m9oflfFryD7sE8nUvpHv77At67nUjufyTijT+0/lAYA1dWONU1LM+7LfScH2feqHd7r+Koyda861B/wjFwXjw6nfF2zxwkL7DE4te67d/3QZL2lM6fdt9qZg69/ijX1f7nLNTtYFANZA/+X+e5n+SXNewfZA6seD+23d62rcUuP4reGV6c89PJ7a7bmveIs0zx0r2Hp5fpx79PM1jB27mRqL/OVd/7ahHW+9nlzjsa3h/7zUJ8r0McK8MQBgzXxWZg/lt7/DeG/ox0+CX7dJ1W9lNjfyH9f4KY3Fg/qR6/NRNLwytHfy32bLOKbM1h+LeGPz7Bqfltn5tnPaHLZxLe064tyvKrO5UWQ2sU+Mx2fRCqhHtob/NVYUxX7tuLH9NY19NeRjzTiHcG2ZrbO7Tar+SO0Qdyq/KbNzzZ7p+ln73AEAljZW3KyTa4btZsrdW2Z37lYtCuO98WqfAABYRvzEutEn10g8P/Zinyz/z0J0s08AABzsnu4T+1H7qRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgtf4BUp7jl7ulynAAAAAASUVORK5CYII=>

[image14]: <data:image/png;base64,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>

[image15]: <data:image/png;base64,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>

[image16]: <data:image/png;base64,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>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAwCAYAAACsRiaAAAADm0lEQVR4Xu3cO6hcRRgA4BGNr/iIChoLIYKiIEiMjaKNT2wU04VYWAoWYmOhlU0aiwSVFIJIRDuxlkAqQVAUjYmFRYhRo6JiIb7fzp8zw84dd68rd3e93P0++Dn//OfsPbPnNj9zztmUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAefmrxHVluyiH03C+M/sdc3KkL0wQc7qzL87QtTneL/FejrdyvLLiiMmeS8P87u53AAAbV9ugLbphC4tq2C5O03+3D9N8G7aqn0+Mr+/G4xxNGjYAWCp9U9CP521RDdtvafrv9m76fxq2n8fUxokVOQ0bACyRaBBu6YvZYzlezXFFjpdynF7q9+V4quT7yzZE0/VJjieb2u1puO33YlOrns9xa1pcw/ZGGs51rN+RvZbjQI43y/jtHHeVfEeO7SWftb45i/EdJd+V4+VmX3ggDddfwwYAS+bKNDQKNaraTFV9/lMaNWyX5Piy5JtznFPy9jMvNHn/t6Zp2D76l1jNpWV7TRrfJPV5NGz3dLV5iL/dxqaVu8fOreYaNgBYUjvTqDE4r8mrWNkJUb+gqfeNx8fNvr05fi/1cDDH66Pdp+rTNGxrEeeI1apYKYz85mbf56UWcVqpRcP2UKn14tbqOP01aGOSft+jXa3mj3f1mHPbsB1ocgBgA9rWjWtjECtlbZMQt0Tj2a4Q9bbJivFVzTicUepVzeNNzeNd/exmPEnchl0tVvNIk9c3U6uzyjaeWav1aNhuyrEvx4lSq57uxmvRN2zndrWaP9PVo2GrK4AhVjgBgA2sbxomNWw/NnnUo7mootn5rhnvScPPT7TPi8Vnvmjytn5+yeNNzlk3H0/0hfTP8/f5B2n46Y1a21ryB3NcVPJZ6K/9Hzl+aMbj5hZile/eksc1m+WcAIB16Oo0NAPf5/izqdeGLZ5Ni+3Dpf5rjs9KxEsJ1Y1pOK5tLD4t47jV922O20p9S6m/U7b1M/3n1yrOGXP4uql9VWqxSrU7x6E0Om9ci3AyDd/v8ub4EA3VLNyQRueMiGv6TY77m2Pi/xHz+KWMY4Uzjo1519u4cWs3bjkDAEvqwjTb5mkaiz7ff7Ue57ce5wQALEi7ArQoz+a4rC+uI/V5NwCApXUirXz7FAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADY4P4G3sbmL5hBJYEAAAAASUVORK5CYII=>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABHCAYAAAC6YRv5AAAFkUlEQVR4Xu3dWahvUxgA8EXmochMZIgHUyQPXoQHkTlFEV0RRXkg6ZYiQzwgZIhIyoskj5JQKIUiZLglGeOWKTMZ1tdeq7vuss+951z3nPP/n/P71df61rf3/d/9dr72sFZKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGyYe3P8k+OeMm6+9mEAACZBNGpjOQAAEyKatCdyrG5q75bxhTLumobzNsvxbKkthAvLuE2Op9oDxYFpuCtYRwCAJWnsDtuDZbyqHsj+TAvfFP3R5GMN245puKY6AgBMnXpXrK8d2837/O4y3lEPZJvm+KGZ/1/7pvFHsFE7vJu3572TY2XJNWwAwNQba4iOavLaDMXds6+aengmx4o0/hsbS//b2+XYvquFndJw7sU5Ps/xWY5L09CobdGMAABTp2+IbuvmsxUN3Xzor++Xbt7f/dsjx/FlvlcaGrktmxEAYOpEk3NKyXdOk3cXKq5v25Kf0B4o4qODE3Nc0NWjQQMAWBKiIXq85N+0B+ZBPKasj1j7mEkcu6TkL7UHAACWi1VpeJzZL8VxSDdfLNGwvZj++/7cOd0cAGDJuj4NTdHJXf3vbr5YolmL69u9q6/rrhwAsIQd0RfWY9Le99oQsaTH2KPGSWnYjstxc1/M3uwLAMB0ibsvx/XF9Tgjzf2uzbd9YQk5qy9MkB2SjwoAYOpF47V1X5yFuTZs9/eFJeLGMsY6a5Oo3hG8dq0qADBVovHakMeVc23Y6mr/S9HefWHCjC2eCwBMkWi86jZEd5Z5XbIi8vrFYTzSPL3k9dipTd7Wwxs5bmjqbcMW5xxa8lhpP+yf47ccD5X5cznuK3movxvLarze1WKPzkdKDgCw5LQNW52P5Ud28zZ/OA3rhrVie6P2nJnusLXnrMjxcTOvx2LcpKnX2mU5divR/s7GFr+9nAMAWGTxB7ndhqj9A93mB3fzNr+hmf+a45aSt+e0DdurOd4ueXvO+Tnebeb12FjTELUz+2IarwEATLVofOp2RnU+lsfisDMd+zQNm4fHu1z9OStK/kBXH8tXpPGG7ccclzf199PQFL7X1OJx7eo0/JuxBg8AYCq9lYbm5occz6fh3bCYv5bjypJ/mGOXHD+VeXVrjsdyHJ7ji6Ye5xyU44+S/5zjopJHo1XPObdErGH2co5jcvxVjoWvSx7XFSJfmeOaHJuWWjRoT6Vhf89oGOt5i6n+/7Fv59PtAQAABvf0hQXWNoyL3Tz24j3ArXK8koZGt/dBGt5nrCMAwLyIr1MXUzRpsbDwJ2nNgrWPlvHqMobazG3T1OZb3PWsxhq2+FAkGrU6AgBMnWiyYnuqvnZsN+/zumhwLD9SRcN0djP/v/ZN43f0ohaPrdt5e947aXjUHDRsAMDUG2uIjurm9Zxo7Gpev5r9qIxVXXNufeKDj9nor2+7NL5obtz5i3MvTsM6eLEkS7wDGI1aLKJcRwCAqdM3RLd183U5OseeOXbuD8zCSX1hBv31/dLN+7t/e+Q4vsz3SkMjF0u81BEAYOpEk3NYM7+uyecidnQ4ry+uw2l9YQZ9w9aLr3C/zPF7U4u17+KL3PBdju+bEQBg6kRDFFtjhbp910KYS8N2Scnrpu8AAMvKqhx/5ni2PzAPYiHgGjd18/YjglY0bC+mNfu/AgAsO9enoSk6uavf3s03ttneYYtmLa5v966+2EudAAAsmP3Sf98Tq9tx7dPVN6bZNmyxo0S71lqI65rv6wMAmHixxdd8mm3DNpO7+gIAwHKyQ1qzo8EkinfeAACWtSvKeMBa1cnxZFqzhygAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvgX22eWHnZHIHzAAAAAElFTkSuQmCC>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAZCAYAAADXPsWXAAAAo0lEQVR4XmNgGAXYACMQfwDi/0j4LYoKCPjLgJAHsbGC+QwQBQ5o4sgAJI8XJDBAFFWjicPARiA2RhdEB8oMEEO2oUsAARcQP0MXxAVAhnxEFwSCX+gC+AAs4JBBMhDXoInhBdgMQecTBOiGXANiUSQ+UeA7A8IQUEAfQZIjGsxjgBjiB8T30OSIBgkMmF4iGSgyQAxIR5cgFZxGFxgFo4AaAADynCc6DrNJsgAAAABJRU5ErkJggg==>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABDCAYAAAAh8FnvAAAFAElEQVR4Xu3dWchtYxgH8GWKOEpKiswylSncuNAxJJELKVO4Isp4IXIh54KSUrhwowwpxaV5nlIuyFBKKBSZh2MoOY7D+7Te1Xm/x97f/r7v7H3Ojt+vnvb7Pu/61l59N/vfWnuv1XUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wUHllrbzJ8t9UkzBwBgDlxU6u86PrNdoNunvm6zoAsAsAUMgW39gu5sXVzq6Dq+s9Q1zdo8+Li+nl7q8HahGv5nly7o9t7PDQCAEAFiQ6nDSh1aXyNoHFfqhlJ/1G2OGf6gOLG+7ljqhVLnNmuzFoHtkGY+BKB58UUzXiywnbWg2xPYAICxIkScl5tJG4zWNeNpBqZ9u9H7i94RdRyB7YlSj5R6q/Z2rduEb+vr/V2/v51L3VF7m+rC7t/Ht3Xt7V/nL9f5j3V+ZamtSj1e5wIbALAie3f/DiLZcFbt91K/ldqhzq+or9OSj2NV14euwbgzbMPrY8NC8X2pI5v5NOTjOzbNBxd0faiM7T+vdVCdB4ENAFi2OIOVw8iWkI/hxjSPwBaXbcNuXX85N+TgFl7s+uA0Tfn4jk/zW5txvPejzXynbuPfn9P0BwIbADBRnAXKgWRzi/ePYDOMlyNCZ4S5Xep8+2ZtWtpjGnd853cbL+GGOEMY3/ebRGADAJYkQsi2ubkZxftfUsfx3a+V+rDUM7mZxOXMcTVOHF/chy6+zzZtAhsAsCQH5MZmFoHo5VJf54U5Ecd3c6mH88IUCGwAwETX5sYmOrvUn7k5wQPd+EuN8+CzbnbHJ7ABAIvavet/LTptw69Ll2p1qVtys+tD0lBb0ppSp6Tedt10jk9gA4AZearUk6VeaXpv1P7zpY4q9V6td0u9Xeq2jZt2d5d6uuvvLfZS7Q3bnzZsVLzW9e8Tz+2chZtyIxmCyGWlXu/6HyjEpcsQN9jNNVhuYBtl2Mc+C7rzY8/cWCGBDQBmaNRZldxb7vydEb2f0nxaPs2N5JtSH+TmEk0jsIWDc2PORJDdVAIbAMxQBKv8pIA90jyHr5ifkOatOEP3XanLm96XzXhahst4k6p1fZrfNaIG0wpsf+XGnMn/o5UQ2ABghk7qFn5gj/rwzr1J8whsIfrxjM8wi8C2Eqtzg6kQ2ABgxiJYxXMlw5qmP4j1H0r9XMdZ7sX32kKcoRrWxgW2uEnrQ6keLHVfqXub7QAA/tf+6PpnbI6TA1mW159rxutrjQtsKzVc7lTzVwDADAy3drgnL1STPoTzejwHsxXr61JvsF+p2xcpAACqCFVv5maVA1krHsHUrsezMEdtP6oHAMAynJobAADwXxK3Mcnf4Xq16Z3c9Fcibg0S+9nQ9M6ovai9mj4AAGP82vXhaZumt7YZb6pRl5V/yQ0AAMY7tuvvR9YGq/iF7DjX5UbXPxd1nBzYHk1zAAAWcXUzboPVqmY8ykfNeNKtT2K/V9XxcENiAACWqA1pEcLidiXto7kW83E3OayFeI836rgNegAALMGTaZ5/gLCYH7vJD7EPz3T9PuO+eQAALFMOURGsXku9USKsDeJM22Iu7vr9/pkXAAAYLy57jgpRS3kO6le50fXPbF3MUs/aAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwY/8A/NtwWv4xFz4AAAAASUVORK5CYII=>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAaCAYAAAAue6XIAAABpUlEQVR4Xu2WyytFURTGF1EyMCKlmCgzJpijKJIRhQnlj1AoIxmbycRcJiJJzEyNlImhPCaeA0Qe62vv01n3u+dc99alLedXX2evb+2z9rr37PMQ+UcMqzZUn6pV1YpqU/WhajTzggLNWuYSvGDgxgYTvLJQoboXVzzSTc4Mx7vEeYwttrFKcflxH+OI/ImPoxqgz8Szqm7Kp7IublIP+Za0IvBHvMZU16o2k5+SuFnAP87Gt2acyrS4k+bJj9hSdbLp4R+BqwWvyccTkt4seFN1qapV7ZRLpFVckV1OKLWqSzYNvDiAt+THo6pTylkGVI+qffILgiIPbCqvbBC8+KT3cIlBv+osTufNB/DW2CwETuBCM6oF8iKWJT4HwuV8Uh2qqsw8cCzun9uW5HV2KP6WpCIcl5tmfyzqxrJws9hnDSYuN/WqF3HbpuR1niVuFjfckcn9FHUS7+2SOBDXbIs/Bs2iuCbPxb0yg6ZXXLN3nAgRPG7QLN5AaexJ7uMKKuqt89tge9T4Mb5d/wRDqg42Q+WCjZAJ/rEWgc+4KzYzMjLy+QIys25Mb3Cf0gAAAABJRU5ErkJggg==>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAaCAYAAADFTB7LAAABk0lEQVR4Xu2VzStFURTFt6+SqWSglIyZ8AeQEHMjEzHiX0AMZKgMlJkRQ2UiiRlhRnrIVJj4zIDIx9qdfbr77ndvXD29k96vVvfstXfnrTr3vEtUOBqsEQoD0CxUDi1C5/F2HuPQJ9Qt9arUf4bd/MzUSeQoCsjYPQqK3bzd1EkcUYaAZdADuSGv29iE452iPq89L+IdQF3KZ+qgO2gaOlZ+poCeJXKDHcbXpG20TFH4e+Xr+T1oUNa/CjhEbpBf4iTWoDZrGirI7TEKNcv6QsTBV2SOA/bImvlRQL/hum2AGujKmsKwqeegBaie0n+YA/aqOm0uDx58tCZ4tYbiw9S7UJOs36Ba1RuT5wnUp/xMAe3wCDRhPM0kdArtk7tcM/E2bZM74k2pD8ldHD5yDvkE3cjzW5IC2rqo2IB8FPxXEQzPFAXkS7OjekGwRS5gozyDY4pcMH6p9S0Lhk5yAfXXICgqyQXk73MaGxRdJq+W2EQR4aOvlvW8boRGP9RqzZC4tEZoBPkX5KmCrq1ZosR/5Qs8YGw4LOmBbQAAAABJRU5ErkJggg==>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAbCAYAAACqenW9AAAAWUlEQVR4XmNgGAWDFnAA8Vcg/o8D+8AUMkIFFgFxBRDvRGKXAXE+TCEIgExkQuL/QGITBCBbiAIsDCQo7gfiD+iCuADIVJAGogBIsQ66IDYgz0CCe0fBIAEANQ0VXRjhPe4AAAAASUVORK5CYII=>

[image24]: <data:image/png;base64,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>

[image25]: <data:image/png;base64,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>

[image26]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAXCAYAAAAP6L+eAAABAElEQVR4Xu2Svw4BQRDGB4nES3gCXkCiEYXQewEvIAqFRKWRKBSiFo0OL+AFdBqVRKcULRUzZieZm9v1J9feL/mS2++buZvdW4CUH3mgCtZMygD1RF1skBR6qShvshBU27SmposaoYbAxedo7KUMXJu1gYYK9DMppzwfW4j2xeigJmo9Bm44Kk/TAN4+1dxRLVQ1UuHwfVWm9tFD9YHzlVvXIxVIGzW3JjIDbtzbwCHnm7GBEJqK+DT1GsLZ+6yW1lQsgJt3NgD2r9YUgl9UhKYmj65ojArwdr6xAX6Jri05T+5vDdTPk0n+kUDXS69v8lB0wb+aUrPj5LyD8lJSDC+h+VSSTF+gcAAAAABJRU5ErkJggg==>

[image27]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAAXCAYAAACWEGYrAAAB3klEQVR4Xu2WyytFURTGl8fEIxQzUykZmBgpI/EHmPgDPCYGZiIxkEKMzXCjJBMDxUAkRoYYoRTFQJ7JI3mt7+612+ts5xRHHcr91ddd+1v3dNddZ511L1GGDH+bKdYd612UCmQNr+TyUEMwnRy6iDDWWRW+mSRZrBXWIpkim4PpNFHFJ0YXq1biqG6++EbSXKr4hkyRRcqrZI2q86+gO4e5w3lfeXOsQnVOHMzjkuf5tzzs9ieKnkftobAxOT+rXBRvrFLfVDSx7smsvG9z5RuC7WY1a8jLFYivWfXOYfRTzCKjbiU+FLkjVp6XW6bPRX6FXopRZC5rzTeFbPo8m+BR+TaHHYu40b6JOWZNsDZZdeL1sKYlttdPyvmc1cq6YLWJRzlibFsjhAfWk2+SGwPNAbkisRk6JUZhwyqeIdOAPfFAC6tbndNFLrBuyexH7EX8NodRQ+7DNGFF7pIrEnkU4oMisUmQx1bR2M5ueH5s8CTjC4Bied2hYJG4Uz4ocp7MHxSMjcXu4HIyHd5SudicsupZ+eQ6ojuJOZ+VGJzJ6wC5tXbIGpS4nVUlMcDo/JgSMvNq5xldxOhcs8rES5Hp1omc+8isO2iczPW4BruzgzVC5iHDNXigM/wfPgAjNXmGqAfNdQAAAABJRU5ErkJggg==>

[image28]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAXCAYAAACmnHcKAAAB8ElEQVR4Xu2WP0gdQRDGJ5pKK0FFC22sLAJiVAhYKBbBOmKsJGCX1tJAGguLoNgFxD9gl87GKqUIFkkZRYiNmiCYRDHBJGr0+5hdbt5wB+ZxD97B+8HH2/mzy8y+27sVqVGjxv/yADqDbo2+lWQoN5LEOa5qVkULHXJ+C+OF4IVosTPOH9mAHntntdIl2symD4AG6It3Vjts5tw7wV/vKALxgFumoFfOVwjSmvF2YfDNfIJajJ0X7ySfTWqE9iRjrUtJAnwhbJlY3qQWUAbc7NS13osGOsNvJclr/SbJWOu1aOAQGnUxYh/D/jD+Hez4dz+CdqBjaFp0zXXoZ8iLMHcJWoGuoW7jp2ahE+hp8F9BL0VvJ4PBRzKbGRYN/PABg53Ij2hshhyINhFhblsYv4XmXMxibY5HRDe0I/h+JeGS3MxmHooGeF/Lwk7sldJm9qEJY9vcBWjZ2L4A2mNm7KmD3oi+lO7VzH2wE/ugP8behZ4Z2+ayED5SEV8A7bgRPvYE+mfsijTDnebzHvkMPTe2zZ0XvcxGGONuWzttTD5KMrdeNN4e7NZgl8UA9BX6APWILsTDyX+Fh5PnbVz0WnQKXYg28j0oFsUCeanlXZDXJX4zCD8PcZ3J4CNH0Da0CK2JPtLNonnML+SVq0bhuAP84ZDFG+qeAQAAAABJRU5ErkJggg==>

[image29]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJQAAAAXCAYAAADtGGaiAAADVklEQVR4Xu2aWahNURjHP5lTRKYylCizB2OZusiUOXMoHkTIlPJAigfDAx5NKZIHSpQkPPCAlOJJMiazkJSMGf7/vrXv2fu7+56z97n7SPb61a9z1vft4bT3umt9e+0r4vF4PP86U+FMOBvOhfOc8xPq8UT47VwIe8GeTn7vDfvC/rAKboTXQvvQAeLxhGglhc6Rhj6i+7yzCY9nq2jn+GgTCUjbEf8XusFfcKdNeJQPop0j7QUaBVfYYI7oAr/AEzbhKUx9bW3CU5KWotP/VZvIM/2kvHoqLePhDtjQtSfD07Bz9RaVZSA8CIe59tJQrq40gg/gQ9jY5HLJGdEOdd8mMqIT3A+3iZ7nMxwk2rnYXly9ZWX4Co+678fgK6ncH9B1+Ba2sIm88VP0Ii+wiQx47T53i56jaSh3w8UqxSf4w8R4vgsmlhUcoR7BOzaRN+pLYeprYHJ1ZbP75I21nYd/zeFYa/g01I6D62Tc57hNGKaJbtfdxBkbHmrzAWNDqF0OXIp5D6+YeK6ZJXqxWRNUAh57X0ws3KH4cFBq4bSH6D6HbcJgj01YO9nYHImOmmnoKjqllurcueSu6M2qBM1Eb2R7E2fslIllRVyHeh4TK4ehosfZZRMehUXzMhtMwRE4wgZDbJeaN/KQibH24MJhVvDYl2Jil0PtF6J1VlL4HpTHWGUTngKT4FkbTMkmGzAE9VMH1+bUxnYwIrLeYR33XbQeyYKLEu2wwehU5dq33Kft6LUxAU63QU+UdqKP0Wnhy+Q08KZxHShYnX8Gm0S2UJLe3KTcFD3mS9FRxR5/ouhU78mAelLeFMPCmi+KCR+Tb8N7hXQNmoveyI42YWA9csAGM4SdynYoFtSlfpcnIfbiJmGJRPcL6o9ix9ojxfMBwTaPI9Hs4PHta5LgnFsi0Xg4orI8SCJHvlzxBraxwSJw5Zf78AbYKYIjC4v6OFaK7kOXi46KtXFSdLTLetliEdwr+hvOS/Thg+tgT0LtYvB3DUnoYLdPLjgHv4m+2GQnYQ3Fpx0WrZRtXuhg9dzaW6IUG32mwDGi7/JmmNzfgsX0WDgajnPfPRnCkYIF6hq4Fq6D642MMcdtVrvtOdrYf1vhNBDUYSPDCY+nXFjYcqry5Iw/CljOg1R8eWwAAAAASUVORK5CYII=>

[image30]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAaCAYAAADMp76xAAABWklEQVR4Xu2VsUoDQRCGJ2IQQRESsUppKxYGqzxBQB/DThDRJ0grCIKNvdjYWqXUFIqFT+AbmFIUUTM/s3fcze16t3sSEtgPfsj9M8v83M1diCKRmWWVtaPNWWSD9cX6Zf2oWinvrCdtTgkEvtBmGTh0pM2K3GnDg3WS2W1d+IttkkMLulCROoFxZzG7Ej1WnzUkObRnrn2pExi7+81qsE5ZV6y1XEeGY9YJSdg3cw35UicwZr+yHsw1vhbwmmmHBTQcatOD0MAtktn3yofnfNJbJA14JGV0HRpZPKjsnTin4v52jLes/JRbKh5yse/Qs8WDluSYE+yunn1j8XKgONamJ6ErgdmXFu9ReTnQgBcvIVl+H0ICr5DMxr9dAr7F8LAWAC9jATRsmt+f2YIHIYEHVHz0Bxnvmhx7fEbS9MFaVLWqhAR+IfsdRA7k2dWF/yQkcCQSiUTmjAmGL0wsI8WCogAAAABJRU5ErkJggg==>

[image31]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAaCAYAAABCfffNAAABHElEQVR4XmNgGAVUAmpAPBOIfZHESpDYFAFWIP4HxLOBmA+I7YD4PxDXAPFnJHUUAZCBNuiCDBDxKnRBcsACBohh2ABIHORLigHIIHyWUAXALOlFl6Am6GZAWATDM1BUUAnkMWBadAtFBZWBCwPueOJGFyAGBKMLQMFiBkxLfID4ApoYQeAHxAXoglBQyoBpyXkgDkQTIwjOAvE6dEEo+MuAiHwtBtS4WgFTRAyAaeJBE1/LgL0oQfcZUeAJEDMB8QcGiAHvofQCJDUwAApa9PhYBcQSQNyEJk42OAfEQUj8NgaIA0GALB9iAzCDQPHDC8R7schRDFqBeD8DIslvQ5KjmiXoIJ4BEh8gQDNLQOAhELcDsRS6xCgYnAAAjXZC9RuUxaoAAAAASUVORK5CYII=>

[image32]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALYAAAAaCAYAAAAaLqaRAAAFH0lEQVR4Xu2aV8gkRRSFrzm75oA5IArqiwoGZFEQAyZQ0AdREAOCTybMLoqKAbOiT6YHMYd9UUFFRATFAGYUd8054ZrjPVbVP3cO1d3VXT0z/+xfH1ym61R1d3X36Uo9IoVCoVAoTJLDWShMDfNZKDje0ViPxVnEGhq7sFiY4QaN41jM5TqNHzX+9fGrxnek3TdTevZxucb5LBoO0riXxTGxssZP4u7hP5RXGOZ7jR1Y7INgYmYLcfqTnDELWFbidT5LBoaaDS8m6nATi4Uh1pb4s8wGB32BRU+V6ScNXrbrWSRyjb2fxm4stmBDcXXAb6Ee9GpHsJjD0eJu/v6coawi/RkbLSzezDpOYqEG1Gl5FolcYx8geca+Tfq5d3OBqzV+ZzGHt6T65j8sLq+vVYclUt16faqxLYsVbC3VdbbkGvtgyTM2NwpratytsbrRlibmaxwobm4TItZgxthY0p5pMnzzA/uI05u6+7b8orEJaZ9pbE9aHVdKvM5MrrEPkXxjo9UGF2ucqXGsxt8zJZYOXpKBj2KRSpuyjYST/yBudvqbT7+usa4p1yfW3DB12xnxs5J2E1DmfhZbkGPs0ALhOmHuzbwO7e1QaAS0aSD64ANxnlnGp3G9uMZ5MyXSwX5bsdiFML4+njPGAMwNU+/IGQl86KMJXNuDLFawayROE7fGyjqiiVvFnf9dGW4gMG8ZBatqvKlxh8ajkvbi14H9m3qWIyV+HmjnsJgA9sO8Jhvc9FjFYqSWSwXr5eglNueMBBZpLGYxAur8EIsVHBqJSzROj+iIJnBuBCZE+E3ZJ4e/NFYy6efMNmi7lp5ibJR5j0Vx+hksiqvjOiwasB96yWzCzU8htVwKMHXoMmHuTU1eCo9L2oNCnR9hsQU5QxGc+2a/faJPj5Km4zfldwHHxGTRgq+s0FcgHTTVAfk7s9gFHOh9Folg/jYvQR3W1AGYmyeUdWBCm1IXlEG33JWuxsYnfpx7A5/GHMLW9w1xXTW0hRpfi5uAvebz9/B5T2m8KMPLYB9rLBA37AjDOAzpwvN5VdwX5GAufAG1z+8ev08f4HgYAllwLV+S9pWkeQh5TUu4jZwn7kAnc0aEVzQOY7ED32hsw6IHE9eNWKxgO6m/QWBFcWWe54wWdDX2VTJcP0yIQhrDm7X89oUaz/ht8LK43gjsKYN9wpdLzCvs/UP+cmbbtpKxdN/AxBeYNFZ+qtair9G4lkUD5iFZdbxR3CdnGAmt58/S3K3zCTHZxFoy/sASZsNNwGhNQ44FLNSAOuGjD3OquBcI6+Jo3T7R+EJcK9aWrsZGy4vvAxa00qjzFUZDq/2YSWPiFO717uJaYgs/BxjrbL8dMzKnRwFWRXBsRKhLDIzX68bXl4nz4ljhm2LTt5vtcYLu7VIWe6arsVOBEayx95JhYy8eZP0PP4cl4gwBkIfGI1Bl7DuNNk647syfGjuxOEr2lcG66yL/ayuJN3YShM/90wyMjeFHAEONsEwGk39k8gBWsfY2aVx/6DGxjfG0zYsZG2vO4wbj5nB+9FzMajKhZ/mHuElJwFYCk5hJ8bTGKSxOETD2E+J6HwydTvA6TI2h4rfi1vstd4kzPPYJQzGMa1EW+6AXC2lMygMPiPvveptJep+gd8FHvxifS/MwdSwEY6O1wARokmAGPq3/vThXhocic5GLJG0BYyysr3GLjPbTcBuOYWEKwFIg1tjRim45nDWnOIqFQqFQKBQKhUKhMHn+A56FWLVBToDCAAAAAElFTkSuQmCC>

[image33]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAaCAYAAAC6nQw6AAAAsUlEQVR4XmNgGAWjgDaAH4jdgdgLDRMN5IH4Px6cjlCKG/AyQBQXIIm9AuJ/SHyiAMiQDWhiKVBxbIAHXQAEQP7HpmEFA3ZxUBhidekOBuwaQGIf0AWBoB+IJ6ILgsAyBkyDRKBifGjiyIH/Ak2OQRgqAQNMUH40khgyQLcUBdgwIGy6CcSCqNJwIMCAI3xIBX1APAldkBzwF4jFgZgLiC3Q5EgCvkB8Bogb0MRHwZAEAAoVKpzsf4RmAAAAAElFTkSuQmCC>

[image34]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKkAAAAaCAYAAADMi3z0AAAEwUlEQVR4Xu2aW6hVRRjHP0siyUpJy65eupgVSehDb1pERUReMhGKHsqKpIdekiARMSKyhG5KPQUVdBFLH8TLg+aDiVEWaDcqT2FeizKym1L5/ZmZs7/9d619Zp+9zlpr6/zgz1n7P7P3zJr1rVnfmjkiiUQikUhkMZ2NRGXczEZC5CvVCDZrxJmqSWyewJym+o3NTnhe3A/+7/WX6hfy3u2tXT+eVi1g03Cb6h02S+J01e/ixvA/KjvRmaH6hM1OCQHJjBbnb+CCGnCKZPd5vjSCow43GfrwMpsnATjv89jsBPzgVjY9eQFcNbhxXmCTqDpIcZEKv1hdwv3insyFMEfcQN7CBcoQKS5IMfMNZ5N4kI0WoE+D2SSqDtJXpZix61YKO/cvJP/H3hdXVtTb82HJn1X2qC5jM4dxkt9nS9VByjf4Wao3VEONV2cuVN0qLre3igXn3k79XHggAzeI8/t6pLbLn+JO3rJXdSV5rVgi2X1m6hCkmE3BYtVjqntV//bWqCc3SiMusnRVo2pLjqjWs9kfQsOHVL+q/vafd6jOMfWKxAYqAnSCKYths8QH6Qo2S+J8ce3jPBGoF3sf3pehUg25TlwfbzIeVif687aO5cEf2GyXkI/exwUlgEBFgF7DBRHgxGNOHue2ks0cxqgmR+oC95WWvCKu/a+l+WZHng8mqn5SbTFlAwluVvRnPBcQqPMoeW96P4sz2DCslfzvRYMBjP2R2HqxYD0Ws/clXBBBj+p7NjNAn99jMwcsuN8RqZiZH21D//i/+B5zl5QXpG+J68doLjDkpVH7Jdu/XfUZm4Y1kv29tggDGUNsvRgQoCEHRaBeZMpiWCdxC+To8yo2SwJtL/PHD/jPDBa9ywrSGLBklDWu6DsCjvlU3DnkgbQG17oj0Pi3bBIhkNsJ6FbYAA0gUPllqhV4mYvpC+qsZrMEsE2Lts/1nzHz2v7u9H85SOeKu6lwfnanDGnRPNU34h694GPV46oPVT96r1PQzkfkTZXjxxovTjYm3m4u7gXvNx1tBD0hroGHuCCD7appbPaDn1WXsunBS9soNnO4Qo4fOAZ7yKhTxUz1rDT3b6z5/KRqmD+2QYoc1ebZ2DlbKm7Jzs5iIUgRUIGignSKNPcb/cTna41n6esaoLxfy5cvids2RFBgVvtDsqd4C3cGL1pYq3xRNYjK8kDQ9PVYX8RGC9AnbBAwj4i7GbDuulvcBUROVdjuRwTI07D+bMHsiT4/YzwEKWZCgCfaU6bsammMe5ix7KoArhu8A6pTjd8p2FAJ7WEVJWuMAXLsVvko4LgZULgx+/k1c1wmB6X5onYjCNKwHf2dNO/xYxUB4xwmgbPFpQL45x+A4MGN/5yvVzZ4us5k04CVo31sDhRY2A13cI//awdllzkuk7Bl283MVm3zx0iD8HQLvC7uJrxc9bDxwznbnLWKcQhtIj/FvyMyKI9N3woBOwd4kwvYQfncHJfNRmm+gN3ELGmkXOGRP0XcbhTSFez4AeTfi8SN/1FxmwQAL1eYIA6rrvdemeAG2qS6kwvE9f0DNssmBCkeRQttQQUgJ+uWvfCTAaQhyJcrZ6RqudRne+8eNhKVcTcbiUQikUgkEolEt3EMugg0mAZ2WPgAAAAASUVORK5CYII=>

[image35]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAbCAYAAAB1NA+iAAAA3klEQVR4XmNgGAWjgIpgHhDfB+L/QMyIJC4IFcMLDIG4HMoGKc5AklsNFcMLvkNpYwaIYnYkORD/NRIfL3jMgGkbiF+AxO8GYiUkPgoAKX6BxGeGioG8CAN/gFgIiY8CQIqDkPhlUDFkgM6HA3EGTMmPSGKvoGwYxgpAEnpQtg6UvwEhzdAHxP1IfAyQwoCwYRKU1kKS/8uAx/9SaPydDJhORefDASy1TYPyQSkRxPeAq2BgYIGKgcAVJHEwkGZAJCZ+BojCSIQ0HHwB4svogjBgCcRrgLgNXWIU0AEAAHQ6NMuEj6CFAAAAAElFTkSuQmCC>

[image36]: <data:image/png;base64,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fWRdxDnvVACJ/7CWyxh7xhgq/2sYKiiUP/O6EkPr0SU2tLLR4sRyv+5OtmGcmI9hu1XNp2LHmCg/NvaFeK+V0suyXbohiZ9d08TZP8YZEiccZJNxUv6a+jJCrHjQwkiF09flYwiJ81rwmny2prnW6D7kfNH6+VAb3juMdcvYBl82di3hByGf9dBC6se0tYSjazwev5+Ts0MeuA65hrx1svWakI7nmG1EjHvz49uzPvrxgTjXOtert556Gd9OPPcg/gobKuTEXWtdXLPk89qfVeP+OcA5paynef9SmWX8KV9AqVjeyIYvfjyPsX4iIhtC/PDciLjZxRa2ZbHRX5cxyRXS023SKigiIjIK3kqzUdGdyDHSarEsaIngNfFfYcr6up9Nft27yTb2+0FERJaYblAiIiIiS0CVNhEREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREJ/h8tjh25m5l19AAAAABJRU5ErkJggg==>

[image37]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAAZklEQVR4XmNgGLqAGV0AGYAka4D4PxBnocnBwQ0gXgfEfgwEFCKDoaIwB10QGwApzEUXxAZACvPQBbEBkMICdEFsAKSwEF0QHYgwQBT2oEvAwGogfg3ET4D4MZR+CcS/kBWNAsoBAO7yGbPFo+KDAAAAAElFTkSuQmCC>

[image38]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAAYUlEQVR4XmNgGAUjDZxBF6AmOAnE/5EwzUERw6hFZILBZZEwEJsQidWhetABURbJA7EfkdgWqgcdEGURNcDws6iLAWKRKLoEtcAvIH4BxE+A+DGUfg3Ei5EVjYJRMAooBwCZZh7vPiWQwAAAAABJRU5ErkJggg==>

[image39]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAApElEQVR4XmNgGJpAHl0AHZwA4qtA7AbEj4H4AIosFMwF4r9oYv+BuBRNDKvgDKg4HEhDBTyRBYEgByoOBwlQAVNkQSCIgIqrwgQqoQL6MAEoCIaKw22qggqgKwyCioejCxjDBKAgDCoON8AOKmAJE4CCWKg4yLNgwA4VAJmADGBOQgEggUloYtug4igAm24QH+R+DLCcARKNIBqkqABVehRQAwAA4fYow14SzbMAAAAASUVORK5CYII=>

[image40]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAAf0lEQVR4XmNgGAUjDZxBF6AmOAnE/5EwyYAViEvRBfGAIgYyLeJgoJNFPAx0soiXYShbZIIF2wPxJCziIIwNEGWRHxYcDsQLsIiDMDZAlEXYAE2CDhsYtBZ1MUAsEkWXIASItegXEL8A4idA/BhKvwbixciK8AFiLRoFo2CkAwAtOCUn2On9ZQAAAABJRU5ErkJggg==>

[image41]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAAcCAYAAACtQ6WLAAAAe0lEQVR4XmNgGOTAEYht0QVh4D8Qr0UXhAGQZAG6IAjoM0AkmZAFbYDYC4h3QyV9oXwwKALiEqjEWygfhFEASDIXXRAEdBkgkozoEiCwhgEiiRW8ZsAjCZLYhMTfhsQGS1pA2RlIbDAASYK8UwfEK5AlYADkeQl0wREPAGL/GMEfWDMiAAAAAElFTkSuQmCC>

[image42]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAaCAYAAAAue6XIAAAA6klEQVR4Xu2TPQrCQBBGRxG8iK3YWHoCQS9hLYh4DI9iJVjZaiMW3kGFCGrpT6UzbALLkJiZRBeLefBgd/YLfIRdAMMwynDig0/c0A0f/pgd+vIUQ+ERHwpZ8IGSOSjKtsCFq/xASJCyHbSLLsGFe/FeS5CyY3QCLniJ96SWIGUTKDjkQwXByjbBBSv8IIV2huuUGSl9A+KyMxAGkX6G25QZWXef5SIuS6ErHyoJdg0oRI8sYeWtpQQt24jXT/9AQdmy9IOoR+61mYILPtAaO5NStOwdjdADukeP6Bkd+KFvU7SsYRiG8Se8AQboQc2ru8/YAAAAAElFTkSuQmCC>

[image43]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAaCAYAAAC+aNwHAAAAy0lEQVR4XmNgGAVUB9+A+BS6ICngPxAXoAsSC/QZIAYwoUsQAjZA7AXEuxkgBvhC+USDIiAuYYBofgvlgzDJAGRALrogsUCXAWIAI7oEsWANA8QAsgFI8zt0QVIAyABQQMLAESgdCcQnGSBePAfEt4FYG6YIGYAMUIGyfyKJg6I2DojvIIlh9WoPA0TiBxCzoMndAmJ3JD5WA/ABZA15QPwGiU8UQDaAZNujgPgMED8F4u9AzI8qTRjcZSAxXyADEwaIkw3RJUYBKgAAZoYqIh8srogAAAAASUVORK5CYII=>

[image44]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAaCAYAAABozQZiAAAAt0lEQVR4XmNgGAUUgW9AfApdkFjwH4gL0AWJAfoMEM1M6BL4gA0QewHxbgaIZl8onyhQBMQlDBCNb6F8ECYJgDTnogsSA3QZIJoZ0SWIAWsYIJrJAiCN79AFiQUgzaBAg4EjSGx2BojB84H4JpI4HIA0q0DZP5HE+aByMHAMiQ0HPQwQRT+AmAVJ/AUQPwPiQ0D8CohFkeQIApCByuiCxAKQrcZI/G4kNlHgKxAfAOJraOKjgK4AAPVjJRgLXp3UAAAAAElFTkSuQmCC>

[image45]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADoAAAAaCAYAAADmF08eAAAB1UlEQVR4Xu2WSytFURTHl0dhgBFlJkwkr4iJuSLGGBiZKCSMfQEylokvQAmlmEhSngNFecaAvFPyzOu/WufUbnUd9zyu7tX51a/2Xuucfdc+5+6zN1FISEhIHPIE13QwRszDe5iiEw5sww8d9MIX7NXBAEmFO/AUZqhcNHB9UzrolnKSgZJ1IgCy4SVch0kqFy18H9dXoRPRUgcb4ALJQE1WPwjy4TOcVnE3FJPUM0JSX7PVd00fHCAZ5Nbqs36ogZ9wVCc80An74TtJjb7r40G6ddAjD3BGB33C9U3qoFtKSQbyun4ikQnP4Sb5X/f2+izTCbdMkAwUC3j74G3hhLx9aZkuCqg+HuROB2PAHMnemasTv3BNAU6UP0g2y0Y7jeQhjMM9I+6HMfgGC3TiB7i+WaPPD4tphaskS28LHsAS+6JI8EBFVvvViGdZOZsVox0EgyS/8RtcQ4fVPobpVpu3xHZ4aPUZxzc/THLBC8npxeaC5IOyBK9gjpH7S1pI6mPzVG4f1ht9x4n+BN9UqINxhjmxHnhj9KOG32aV0R8y2k40utAv5kQ9vU2bR7gId1XciVoX+qENbsAzkqMmn6n/JUfk8dybSFST/FUrdSIkJCTx+AYGKWdR0L4ArgAAAABJRU5ErkJggg==>

[image46]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEsAAAAaCAYAAAD/nKG4AAACZUlEQVR4Xu2Xy8tOURTGHxFKUkIK+RK5jJSJMkAMFCb8DRKSSxmI+HKZYOI2kNxyKaXIRCQDIwyIlD+BEhO3ktt6vrX3+6293n3e03f0nqj9q6f3rGevfdY5+5x99n6BQqHwHzBdNNObhZQrot9Bu11bG8wVPYXWf+ja6jgN7fdTdNy1kV2im6JFIV4guiba2clowEJo0TG+oc8sh9aNLHZxL76JBkwcH7jliPGjXiQZDeDo+0JtwJpbnPdd9MR5nrHQvp+Mdzt4m413UHQKOnv2i0abtsawyBdv9plp0Lr8tTwIfh3MeWbie8FbbzwO0EoTN+aE6FA4ZhGeuE0OID8ol5D364jTzLIPfzlYe6GvOpmH4SLjOhntcAfdN0fOIu/34i60zyTn816Phrb4EM4lGT3YBO0w3nivglfHedHVCvGbcFl0UXQh5K4d6lXNY+TrnoT6M3xDhqXQFfGN6Dn0W2bh6n7feTz3YedlYeLbjMeVpW1uID9YZ6D+SFfmR9B+U3yDgzm5uglroEl2tSD0Bp3XBlXfLL6ZOb+OJegeiFHmOMI9We35c0+SG0J6dlpWwcXg2AhkV6Ucy6C1m6yGW6E5E53vB4vHH0wcvbrzd15vC3ez0btuG1qCtTc477Poo/O2I/0exRseNF588H6w9pg4en4cupiANGljiKNXe4I+wLfoh4k5bXgdA8aLu3p7fTtE70xMXkNzZhvvq2iqiVdAc+Ybr5JVGC68LXi/Qjw5JrXMS+iG+Bb0OlanzUNw87nOefGvzPvwy/uYlWQonIbxnqk5aXOhUCgUCoVCofAP8gc1/q7XDYBq9AAAAABJRU5ErkJggg==>