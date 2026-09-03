# **Arquitectura Avanzada de Indicadores Custom en MetaTrader 5 (MQL5): De los Fundamentos de Ejecución al Feature Engineering para Machine Learning**

La evolución de las plataformas de negociación algorítmica ha consolidado a MetaTrader 5 y su lenguaje de programación, MQL5, como un entorno de alto rendimiento para el análisis cuantitativo de mercados financieros.1 A diferencia de los enfoques tradicionales de scripting, la arquitectura de indicadores de MQL5 está diseñada para operar con un modelo asíncrono y de baja latencia mediante el procesamiento óptimo de vectores de datos directamente vinculados a la memoria física de la terminal.1 Este informe detalla de manera exhaustiva la ingeniería detrás de la creación de indicadores personalizados, abarcando desde los fundamentos de la pila de ejecución de bajo nivel hasta el diseño de características estadísticas (*features*) optimizadas para su integración directa en modelos de machine learning.

## **1\. Fundamentos de Indicadores en MQL5 y el Modelo de Ejecución de Bajo Nivel**

El motor de ejecución de MetaTrader 5 procesa los indicadores personalizados en un hilo dedicado para evitar el bloqueo de la interfaz de usuario de la plataforma.2 La sincronización de los datos de precios con este hilo se gestiona mediante eventos estructurados, donde la función OnCalculate() actúa como el punto de entrada principal para toda iteración matemática.4

### **Parámetros de OnCalculate() y Firmas de Entrada**

La plataforma provee dos firmas distintas para la función OnCalculate(), las cuales determinan el origen de los datos a procesar 4:

* **Firma de Series Temporales (Completa)**: Se utiliza por defecto cuando el indicador se aplica de manera directa sobre el gráfico principal.5 Proporciona arrays nativos que representan la totalidad del histórico del gráfico, incluyendo el precio de apertura (open), el precio máximo (high), el precio mínimo (low), el precio de cierre (close), el volumen de ticks (tick\_volume), el volumen real transaccionado (volume) y el spread actual (spread).4  
* **Firma de Array Unidimensional (Reducida)**: Diseñada para la manipulación de datos abstractos provenientes de otros indicadores aplicados en cascada.4 En este caso, el usuario puede seleccionar desde la interfaz gráfica de la terminal qué serie o indicador previo desea pasar como parámetro a través de la opción "Aplicar a" (*Apply to*), recibiendo dichos datos en un único array de entrada denominado price.4

El control de la eficiencia algorítmica en ambas firmas se fundamenta en la relación entre los parámetros rates\_total (tamaño actual de la serie temporal disponible en el gráfico) y prev\_calculated (el número de velas procesadas con éxito en la llamada inmediata anterior a OnCalculate()).4 Si se produce una carga profunda de historial nuevo o se resuelven discrepancias en la base de datos de tiempos del bróker, la terminal restablece de forma automática prev\_calculated a cero, forzando una reconstrucción limpia de todos los buffers.4  
La indexación interna de los arrays de precios recibidos en OnCalculate() se gestiona por defecto en sentido cronológico ascendente, donde el índice 0 representa la vela más antigua del histórico disponible y el índice rates\_total \- 1 representa la vela en formación activa (vela cero en términos gráficos).6 No obstante, mediante la función ArraySetAsSeries(), los desarrolladores pueden alternar el sentido de la indexación para simular la estructura tradicional de series temporales descendentes de MQL4, facilitando cálculos retrospectivos sin alterar la asignación física de la memoria del terminal.1

### **Buffers de Dibujo frente a Buffers de Cálculo**

La gestión de la memoria intermedia en indicadores MQL5 se organiza a través de arrays dinámicos registrados globalmente mediante la función SetIndexBuffer().1 El comportamiento físico y lógico de estos arrays varía drásticamente según el rol asignado por la enumeración ENUM\_INDEXBUFFER\_TYPE 1:

| Tipo de Buffer MQL5 | Enumerador Técnico | Exposición en Ventana de Datos | Gestión de Memoria del Terminal | Aplicación Típica |
| :---- | :---- | :---- | :---- | :---- |
| **Buffer de Datos** | INDICATOR\_DATA | Visible por completo en la ventana de datos de la terminal.1 | Asignación automática ligada a la dimensión del gráfico.1 | Almacena coordenadas físicas utilizadas directamente para el renderizado gráfico.1 |
| **Buffer de Cálculo** | INDICATOR\_CALCULATIONS | Oculto para el usuario de la terminal. | Asignación automática optimizada para cálculos internos. | Almacena valores intermedios (ej. volatilidad base, medias intermedias).9 |
| **Buffer de Color** | INDICATOR\_COLOR\_INDEX | Oculto para el usuario de la terminal. | Sincronización estricta con el buffer de dibujo adyacente.1 | Almacena enteros representativos del índice de color en la paleta activa.1 |

### **Estilos de Dibujo en MQL5**

La API gráfica de MetaTrader 5 ofrece dieciocho variaciones de renderizado a partir de estilos básicos de dibujo.1 La correcta selección del estilo determina la cantidad de buffers INDICATOR\_DATA secuenciales que el desarrollador debe enlazar mediante SetIndexBuffer().1

| Estilo de Dibujo MQL5 | Buffers de Datos Requeridos | Buffers de Color Requeridos | Comportamiento del Motor Gráfico del Terminal |
| :---- | :---- | :---- | :---- |
| DRAW\_LINE | 1 | 0 | Traza una línea continua uniendo los valores no vacíos secuenciales.1 |
| DRAW\_COLOR\_LINE | 1 | 1 | Traza una línea continua cuyo color por tramo se indexa dinámicamente.1 |
| DRAW\_HISTOGRAM | 1 | 0 | Renderiza barras verticales desde el nivel cero del indicador hasta el valor del buffer.1 |
| DRAW\_HISTOGRAM2 | 2 | 0 | Dibuja barras verticales delimitadas entre los valores de dos buffers diferentes.1 |
| DRAW\_ARROW | 1 | 0 | Coloca símbolos gráficos (códigos Wingdings) en los índices de coordenadas provistas.1 |
| DRAW\_CANDLES | 4 | 0 | Renderiza velas japonesas completas utilizando buffers ordenados para Open, High, Low y Close.1 |
| DRAW\_FILLING | 2 | 0 | Sombrea de manera bidireccional el espacio comprendido entre dos curvas de precio o indicador.1 |
| DRAW\_ZIGZAG | 2 | 0 | Une puntos extremos permitiendo la existencia de segmentos verticales en una misma barra.1 |

## **2\. Indicadores Multi-Buffer y Dinámica de Color Avanzada**

La creación de herramientas visuales complejas, tales como nubes de volatilidad o histogramas adaptativos de tendencia, se basa en la manipulación y la combinación de múltiples buffers de datos y de color bajo una misma estructura lógica.1

### **Estilo de Dibujo DRAW\_FILLING y Canales Dinámicos**

El estilo DRAW\_FILLING se utiliza para la construcción de canales visuales dinámicos (como bandas de Bollinger, canales de Keltner o nubes de Ichimoku).12 Este estilo requiere exactamente dos buffers de tipo INDICATOR\_DATA definidos de forma secuencial en las directivas del compilador.1 El motor de renderizado compara en tiempo real los valores de ambos buffers para aplicar el relleno cromático de manera direccional 12:

* **Relleno Alcista (Buffer 1 \> Buffer 2\)**: Se aplica el primer color declarado en la propiedad de color asociada.12  
* **Relleno Bajista (Buffer 1 \< Buffer 2\)**: El motor conmuta automáticamente al segundo color declarado en la paleta.12

Para evitar la distorsión del gráfico debido a la interpolación de valores nulos o históricos ausentes, es mandatorio definir de forma explícita el valor vacío a través del atributo PLOT\_EMPTY\_VALUE utilizando la constante EMPTY\_VALUE.11 De lo contrario, la terminal intentará trazar líneas hacia el origen de coordenadas, alterando el factor de escala visual del gráfico principal.12

### **Dynamic Color Switching y COLOR\_INDEX**

El uso del tipo de buffer INDICATOR\_COLOR\_INDEX permite que un indicador modifique de forma dinámica su apariencia visual basándose en condiciones analíticas complejas en lugar de limitarse a una única propiedad estática.1 Cuando se emplea un estilo multicolor (como DRAW\_COLOR\_LINE o DRAW\_COLOR\_HISTOGRAM), se debe declarar un buffer de color adyacente justo después de los buffers de datos que conforman el dibujo.1  
La paleta base de colores se registra inicialmente mediante la directiva \#property indicator\_color.12 Posteriormente, en el bucle principal de ejecución de OnCalculate(), el desarrollador asigna un valor flotante correspondiente al índice entero del color deseado en el buffer cromático.1  
Por ejemplo, si la propiedad define la secuencia clrLime, clrRed, clrGray, la inyección del valor 0.0 en el buffer de color pintará el segmento correspondiente en verde, 1.0 en rojo y 2.0 en gris.17 Esto optimiza significativamente el uso de memoria, ya que evita tener que duplicar múltiples buffers con valores vacíos para simular líneas segmentadas de diferentes colores.1

## **3\. Modelo de Acceso Descentralizado a Datos: iCustom() frente a Indicadores Nativos**

MQL5 implementa un modelo estrictamente desacoplado para el consumo de datos de otros indicadores, rompiendo con el paradigma de llamadas directas y síncronas propio de MQL4.2 Este diseño separa la carga de cálculo matemático de la lógica de ejecución del cliente, mejorando notablemente el rendimiento general.2

### **Comparación de Estructuras de Acceso**

El acceso a indicadores en MQL5 requiere comprender las diferencias estructurales entre la instanciación de indicadores integrados en la terminal y las llamadas a códigos personalizados externos.2

| Dimensión Técnica | Indicadores Nativos (iMA, iRSI, iMACD, etc.) | Indicadores Personalizados (iCustom) |
| :---- | :---- | :---- |
| **Instanciación** | Ejecutada a través de funciones nativas optimizadas en C++ dentro del núcleo del terminal.19 | Ejecutada cargando un archivo compilado .ex5 desde el directorio de indicadores.8 |
| **Consumo de Memoria** | Muy bajo; comparte cachés globales eficientes entre múltiples EAs o gráficos.19 | Mayor; requiere asignación de buffers independientes para cada instancia personalizada.23 |
| **Uso en Strategy Tester** | Optimización de simulación nativa con velocidad de ejecución máxima.20 | Puede ralentizar el backtesting si el código del indicador no está optimizado para cálculo incremental.23 |
| **Detección de Errores** | El handle devuelto valida los parámetros estándar de inmediato.8 | Errores de carga del archivo .ex5 o de buffers no válidos solo se detectan en tiempo de ejecución.8 |

### **El Flujo de Trabajo Handle \+ CopyBuffer()**

La recuperación física de los valores de un indicador se basa en un flujo estructurado en dos fases 18:

1. **Inicialización de Handle**: Consiste en crear el identificador de indicador en la función OnInit() del Asesor Experto o indicador receptor.18 Este handle funciona como un puntero lógico hacia la instancia del indicador alojada en la caché global de la terminal.18  
2. **Copia de Datos Dinámica**: Ejecutada dentro de las funciones de eventos periódicos como OnTick() u OnCalculate() empleando la función CopyBuffer().15

Fragmento de código  
// Sintaxis detallada de la función de copia  
int CopyBuffer(  
   int       indicator\_handle, // Handle del indicador de origen  
   int       buffer\_num,       // Índice del buffer de origen a copiar (0 a N-1)  
   int       start\_pos,        // Posición inicial de la vela en origen (0 \= vela actual)  
   int       count,            // Cantidad de elementos de velas a transferir  
   double    buffer          // Array dinámico de destino  
);

### **Gestión de Latencia de Datos e Inicialización Asíncrona**

Uno de los principales errores en el desarrollo algorítmico avanzado ocurre al suponer que los datos están disponibles inmediatamente después de la creación del handle.18 Cuando se inicializa un indicador desde un Expert Advisor, la terminal inicia un hilo secundario para descargar el historial de datos requerido y realizar los primeros cálculos matemáticos.15 Durante este breve lapso, las llamadas directas a CopyBuffer() fallarán o devolverán un número de elementos inferior al solicitado.15  
Para evitar excepciones de desbordamiento de array (*array out of range*), es imprescindible validar la disponibilidad de los datos utilizando la función BarsCalculated() antes de invocar a CopyBuffer() 15:

Fragmento de código  
int calculated\_bars \= BarsCalculated(indicator\_handle);  
if(calculated\_bars \< min\_required\_bars)  
  {  
   // Detener la ejecución del ciclo actual y esperar al siguiente tick  
   return;  
  }

## **4\. Implementación de Análisis Técnico Avanzado de Grado Institucional**

El desarrollo de indicadores que no vienen preinstalados en la plataforma MetaTrader 5 requiere el uso de metodologías estructuradas para el procesamiento de datos multidimensionales de precio y volumen.1

### **Volume-Weighted Average Price (VWAP) Intradía**

El VWAP es un precio de referencia utilizado por mesas de dinero institucionales para evaluar la calidad de ejecución de órdenes algorítmicas.3 Se calcula acumulando el producto del precio típico por el volumen de cada periodo y dividiéndolo por el volumen total acumulado a lo largo del día 26:  
![][image1]  
Donde ![][image2] y ![][image3] representa el volumen de tick o volumen real de la vela ![][image4].26 El índice ![][image5] representa el primer elemento temporal correspondiente a la sesión del día actual.26 Al inicio de cada día de negociación del bróker, el acumulador de sumas se reinicia de manera estricta a cero para evitar el arrastre de datos de sesiones previas.26  
Las bandas de volatilidad alrededor del VWAP no se basan en un rango estático de precio, sino en la varianza ponderada por volumen acumulada de la sesión 26:  
![][image6]  
Las bandas se expanden multiplicando esta desviación típica ![][image7] por un factor de dispersión configurable, determinando áreas dinámicas de sobrecompra o sobreventa estadística.26

### **Conceptos de Orderflow y Gráficos Footprint**

MQL5 permite el acceso directo a la estructura de microestructura de mercado mediante las funciones CopyTicks() y CopyTicksRange(). Un indicador de footprint procesa el flujo de órdenes acumulando el volumen transaccionado en el bid (ventas agresivas) y en el ask (compras agresivas) para cada nivel de precio discreto dentro de una misma vela.  
Para lograr esto, se define un vector de ticks MqlTick ticks y se analiza cada tick individualmente aplicando la lógica de clasificación de órdenes por el lado de la transacción:

Fragmento de código  
// Ejemplo de lógica conceptual para clasificar volumen en Orderflow  
for(int i \= 0; i \< total\_ticks; i++)  
  {  
   double tick\_price \= ticks\[i\].last;  
   long tick\_vol \= ticks\[i\].volume;  
     
   if((ticks\[i\].flags & TICK\_FLAG\_BUY)\!= 0\)  
     {  
      // Agresión de compra en el Ask  
      AccumulateAskVolume(tick\_price, tick\_vol);  
     }  
   else if((ticks\[i\].flags & TICK\_FLAG\_SELL)\!= 0\)  
     {  
      // Agresión de venta en el Bid  
      AccumulateBidVolume(tick\_price, tick\_vol);  
     }  
  }

### **Market Profile y Volume Profile**

El Market Profile y el Volume Profile permiten analizar la distribución espacial de los precios y los volúmenes a lo largo del tiempo, facilitando la identificación de zonas clave de aceptación y rechazo del valor:

* **Market Profile (TPO \- Time Price Opportunity)**: Mide el tiempo de permanencia del precio en cada nivel discretizado. Se calcula estructurando una matriz bidimensional donde las columnas representan bloques temporales (por ejemplo, intervalos de 30 minutos) y las filas representan los niveles de precios del activo.  
* **Volume Profile**: Acumula el volumen total negociado en cada nivel de precio durante un periodo determinado. A partir de esta distribución, se definen tres variables de mercado fundamentales:  
  1. **Point of Control (POC)**: El nivel de precio con mayor volumen transaccionado del perfil analizado.  
  2. **Value Area (VA)**: El rango de precios adyacente al POC donde se concentra el ![][image8] del volumen negociado durante la sesión.  
  3. **High/Low Volume Nodes (HVN / LVN)**: Zonas de alta y baja concentración de volumen que actúan respectivamente como niveles de soporte/resistencia magnéticos y zonas de transición rápida de precios.

### **Gráficos Renko y Range Bars como Indicadores Overlay**

El desarrollo de sistemas de representación basados exclusivamente en variaciones de precio (como Renko o Range Bars) como capas superpuestas (*overlays*) en gráficos temporales requiere resolver la disparidad dimensional entre el dominio del tiempo y el dominio del precio.3 Un gráfico estándar de MetaTrader 5 está rígidamente anclado a un eje temporal horizontal.3  
Para dibujar un gráfico Renko de forma superpuesta, el indicador debe implementar una máquina de estados en OnCalculate() que genere ladrillos (*bricks*) virtuales independientes del tiempo. Estos ladrillos se dibujan utilizando el buffer de dibujo DRAW\_CANDLES o mediante la instanciación dinámica de objetos gráficos rectangulares (OBJ\_RECTANGLE\_LABEL), mapeando las coordenadas virtuales a los límites temporales del gráfico subyacente.1

### **Heikin Ashi Smoothed (HA Suavizado)**

La variante suavizada de las velas Heikin Ashi elimina gran parte de las señales falsas generadas en mercados de alta volatilidad o ruido lateralizado.30 Su arquitectura utiliza un proceso de filtrado secuencial de dos etapas en lugar de trabajar directamente sobre la serie de precios original 30:

1. **Primera Etapa de Suavizado**: Se aplican cuatro filtros de suavizado independientes (comúnmente medias móviles exponenciales) sobre las series de precio reales Open, High, Low y Close del activo.30  
2. **Cálculo de Velas Heikin Ashi**: Se aplican las fórmulas tradicionales de construcción de Heikin Ashi, utilizando como datos de entrada los valores ya filtrados de la primera etapa:

![][image9]  
![][image10]  
![][image11]  
![][image12]

### **Algoritmo Supertrend Adaptativo**

El Supertrend es un indicador de seguimiento de tendencia que combina el precio típico del activo con el rango verdadero medio (ATR) para definir niveles dinámicos de stop-loss.10 Su robustez radica en un algoritmo recursivo de bloqueo de cuatro ramas que impide que el stop-loss retroceda en contra de la tendencia activa 31:

* **Banda Superior Base**: ![][image13] 10  
* **Banda Inferior Base**: ![][image14] 10

El algoritmo actualiza y bloquea el stop en cada vela aplicando la siguiente lógica condicional:

SI (Cierre\[i\] \> Soporte\[i-1\] Y Cierre\[i-1\] \> Soporte\[i-1\]) ENTONCES  
   Soporte\[i\] \= Máximo(DOWN\[i\], Soporte\[i-1\]) // El soporte alcista solo puede subir  
SI (Cierre\[i\] \< Resistencia\[i-1\] Y Cierre\[i-1\] \< Resistencia\[i-1\]) ENTONCES  
   Resistencia\[i\] \= Mínimo(UP\[i\], Resistencia\[i-1\]) // La resistencia bajista solo puede bajar

Si el precio cruza la resistencia previa al alza, se produce un cambio de tendencia alcista y el nivel de soporte se inicializa directamente en ![][image15]; si cruza el soporte a la baja, se activa una tendencia bajista y el nivel de resistencia se inicializa en ![][image16].10

### **Componentes de Ichimoku Desplazados al Futuro**

El indicador de origen japonés Ichimoku Kinko Hyo introduce un reto de diseño estructural: la proyección de buffers de datos hacia el futuro (margen derecho del gráfico) y el desplazamiento de datos hacia el pasado. Los componentes principales se definen de la siguiente manera:

* **Tenkan-Sen**: Punto medio de los máximos y mínimos de los últimos 9 periodos.  
* **Kijun-Sen**: Punto medio de los máximos y mínimos de los últimos 26 periodos.  
* **Senkou Span A**: Punto medio entre el Tenkan-Sen y el Kijun-Sen, proyectado y dibujado 26 periodos hacia el futuro.  
* **Senkou Span B**: Punto medio de los máximos y mínimos de los últimos 52 periodos, proyectado y dibujado 26 periodos hacia el futuro.  
* **Chikou Span**: Precio de cierre actual dibujado 26 periodos hacia el pasado.

Para dibujar correctamente las proyecciones futuras de las líneas Senkou Span A y B sin desplazar los arrays subyacentes, MQL5 permite configurar la propiedad de dibujo PLOT\_SHIFT a través de la función PlotIndexSetInteger().9 Esto desplaza de forma visual la representación del buffer en la pantalla sin alterar la alineación temporal de los índices de cálculo del indicador dentro del código.9

## **5\. Feature Engineering Estandarizado para Modelos de Machine Learning**

La aplicación directa de datos de precios brutos a modelos de aprendizaje automático suele provocar fallos de generalización debido a que los precios son series temporales no estacionarias.32 Para resolver esto, los indicadores de MQL5 pueden actuar como motores de transformación matemática en tiempo real, procesando los precios para extraer características estacionarias acotadas y libres de sesgo.33

### **Normalizaciones y Estandarizaciones sobre Ventanas Rodantes**

Toda normalización matemática destinada a modelos predictivos debe calcularse de manera estricta utilizando ventanas rodantes (*rolling windows*).33 Aplicar normalizaciones estáticas sobre un conjunto de datos completo introduce un sesgo de anticipación (*look-ahead bias*), invalidando el entrenamiento del modelo.

| Feature de Normalización | Tipo de Entrada | Rango de Salida | Ecuación Matemática | Propiedad Estadística | Utilidad Práctica en ML |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Z-Score Móvil** | Precio de Cierre.36 | Teóricamente ilimitado (![][image17]).32 | ![][image18] 37 | Estacionariedad estricta con media cero y desviación típica unitaria.32 | Clasificación de niveles de sobreextensión estadística sin techos de saturación.32 |
| **Min-Max Móvil** | Precio de Cierre.39 | Acotado estrictamente a $$.39 | ![][image19] | Homogeneización lineal de la escala de precios dentro de la ventana de análisis. | Evita el desvanecimiento del gradiente en modelos basados en redes neuronales. |

### **Ratios de Indicadores e Indicadores de Momentum**

Los ratios de indicadores y las medidas de momentum ayudan a aislar la velocidad y la aceleración de los movimientos de precios de sus escalas absolutas:

* **Ratios de Volatilidad**: Dividir la volatilidad implícita o un ATR de corto plazo por un ATR de largo plazo genera una métrica limpia de expansión o contracción del rango de precios, útil para identificar fases previas a rupturas de tendencia.  
* **Momentum de Indicadores**: Calcular la tasa de cambio (ROC) o la pendiente de la línea de regresión de un oscilador clásico (como un RSI o una media móvil) permite identificar dinámicas de aceleración antes de que se reflejen de forma evidente en el precio.40

### **Algoritmo de Detección Automática de Divergencias**

El aislamiento algorítmico de divergencias regulares requiere un sistema de detección de pivotes locales basado en ventanas simétricas.41 Un bar ![][image20] es clasificado como un pivote de máximo local (techo) si supera de forma estricta los máximos de sus ![][image21] barras a la izquierda y ![][image22] barras a la derecha 41:  
![][image23]  
Para que la señal sea matemáticamente válida y libre de sesgo retrospectivo en tiempo real, el indicador solo puede confirmar la existencia de este pivote en la vela actual si se ha cerrado la vela ![][image24].41 Una vez identificados dos pivotes de máximos consecutivos en el precio, el indicador analiza el valor del oscilador en esas mismas coordenadas temporales.42 Si el precio muestra una pendiente ascendente mientras que el oscilador muestra una pendiente descendente, el sistema registra de forma automática una divergencia bajista regular.42

### **Filtros de Detección de Regímenes de Mercado**

Para adaptar dinámicamente las estrategias de trading al entorno actual del mercado, se calculan características de estado estructural 38:

* **Exponente de Hurst (![][image25])**: Mide el grado de autocorrelación a largo plazo de la serie de precios.38 Un valor de ![][image26] indica un comportamiento antipersistente de reversión a la media; ![][image27] representa un mercado puramente aleatorio (caminata aleatoria); y ![][image28] confirma una estructura persistente o tendencial.38  
* **Velocidad de Reversión Ornstein-Uhlenbeck**: Calcula el parámetro de velocidad de reversión a la media a través de una regresión lineal sobre los retornos de precios desviados de su promedio, permitiendo estimar el tiempo medio de retorno al valor de equilibrio.38

## **6\. Optimización de Rendimiento Extremo y Perfilado de Código**

En mercados de alta frecuencia donde se procesan miles de ticks por segundo, la optimización del código del indicador es fundamental para garantizar que no se pierdan datos ni se ralentice la toma de decisiones algorítmicas.23

### **Estrategias Matemáticas para Evitar Redibujados Innecesarios**

El cálculo incremental estricto es el pilar fundamental de la optimización en MQL5.6 El uso indebido de bucles que recorren de forma repetida todo el historial del gráfico en cada tick satura el procesador.23  
La lógica de cálculo de un indicador optimizado debe segmentarse bajo tres condiciones exclusivas basadas en el valor de prev\_calculated 4:

Fragmento de código  
int start;  
if(prev\_calculated \== 0\)  
  {  
   // Caso 1: Inicialización completa o recarga del histórico.  
   // Se calculan todas las barras desde el inicio del histórico.  
   start \= InpPeriod \- 1;  
  }  
else if(prev\_calculated \< rates\_total)  
  {  
   // Caso 2: Se ha cerrado una vela y se ha creado una nueva barra.  
   // Se calcula la barra que acaba de cerrarse y la barra activa en formación.  
   start \= prev\_calculated \- 1;  
  }  
else  
  {  
   // Caso 3: Entrada de un nuevo tick que actualiza la vela actual en formación.  
   // Únicamente se actualiza la vela cero.  
   start \= rates\_total \- 1;  
  }

### **Gestión de Memoria y Preasignación Estática de Buffers**

La reserva de memoria en sistemas operativos es una operación lenta. Redimensionar constantemente arrays dinámicos mediante ArrayResize() dentro del ciclo principal de ejecución introduce latencia.  
Para lograr un rendimiento óptimo, se deben asociar todos los arrays intermedios de cálculo como buffers de tipo INDICATOR\_CALCULATIONS en OnInit(), permitiendo que el propio terminal optimice de forma nativa la asignación física de la memoria del sistema.1

### **Tratamiento de Indicadores de Carga Masiva (FFT y Wavelets)**

Los indicadores que realizan análisis espectral mediante Transformadas Rápidas de Fourier (FFT) o transformaciones de Wavelet requieren procesar bloques fijos de datos históricos (por ejemplo, muestras de tamaño ![][image29] o ![][image30] barras). En lugar de calcular una FFT completa para todo el historial disponible en el gráfico, la optimización consiste en implementar una ventana deslizante (*sliding window*).  
En cada tick nuevo, el algoritmo realiza una actualización recursiva de baja complejidad computacional (![][image31] o ![][image32]), en lugar de ejecutar el cálculo completo de complejidad ![][image33] sobre todo el historial.24

### **Perfilado de Código con el Profiler de MetaTrader 5**

Para identificar líneas de código lentas o cuellos de botella en indicadores complejos, MetaEditor incorpora una herramienta de perfilado de rendimiento (*Profiler*). El programador ejecuta el indicador en el Profiler bajo condiciones de simulación real en el Strategy Tester o sobre un gráfico activo. Al finalizar la prueba, el Profiler muestra un reporte detallado que desglosa el porcentaje de tiempo de CPU y la cantidad de llamadas consumidas por cada función individual del código, facilitando la optimización quirúrgica de los fragmentos de código ineficientes.

## **7\. Metodología de Conversión en Señales y Validación Cuantitativa**

Un indicador técnico se convierte en una herramienta operativa cuando sus métricas se transforman sistemáticamente en un vector de señales discretas de tipo Compra (![][image34]), Venta (![][image35]) o Neutral (![][image36]).31

### **Confluencia de Múltiples Indicadores**

Para reducir la tasa de operaciones falsas en mercados volátiles, se diseñan motores de decisión que exigen la confluencia de múltiples indicadores estadísticamente desacoplados.41  
Por ejemplo, un sistema robusto puede requerir que se cumplan simultáneamente tres condiciones independientes: una señal de tendencia alcista (ej. Supertrend con dirección ![][image37]), un oscilador de momentum saliendo de una zona extrema de sobreventa (ej. Z-Score cruzando por encima de ![][image38]) y un filtro de volumen que confirme la participación activa de mercado (ej. Z-Score de volumen de ticks mayor que ![][image39]).31

### **Backtesting y Métricas de Rendimiento de Señal**

La validación cuantitativa de un indicador antes de su implementación en cuentas reales se realiza codificando su lógica dentro de un Asesor Experto y evaluando su desempeño en el Strategy Tester de MetaTrader 5 utilizando simulación con modelado basado en ticks reales de alta precisión.2 Las principales métricas analizadas incluyen:

* **Profit Factor**: Relación matemática entre el beneficio bruto y la pérdida bruta del sistema. Un indicador con un verdadero sesgo predictivo debe arrojar un factor de ganancia superior a ![][image40] de manera consistente en pruebas fuera de muestra (*out-of-sample*).  
* **Drawdown Máximo**: La pérdida máxima acumulada experimentada por la curva de patrimonio durante las fases de mercado desfavorables.  
* Sharpe Ratio: Evalúa el rendimiento del sistema en relación con el riesgo asumido. Permite comprobar si el retorno obtenido compensa la volatilidad de la cartera o si es simplemente el resultado de asumir riesgos excesivos.

## **8\. Implementación de Código MQL5 (3 Indicadores Custom Completos)**

### **Indicador 1: Intraday VWAP con Reset Diario, Desviación Estándar y Relleno Gráfico (DRAW\_FILLING)**

Este indicador calcula el VWAP intradía utilizando volumen real o volumen de ticks.26 Reinicia de forma automática sus acumuladores estadísticos al inicio de cada día del bróker y sombrea el rango de la primera desviación estándar empleando el estilo de dibujo DRAW\_FILLING.12

Fragmento de código  
//+------------------------------------------------------------------+  
//|                                                Intraday\_VWAP.mq5 |  
//|                                                                  |  
//+------------------------------------------------------------------+  
\#property copyright "Copyright 2026"  
\#property version   "1.00"  
\#property indicator\_chart\_window  
\#property indicator\_buffers 5  
\#property indicator\_plots   2

// Configuración del Plot 1: Relleno de las bandas de desviación  
\#property indicator\_label1  "VWAP Deviation Filling"  
\#property indicator\_type1   DRAW\_FILLING  
\#property indicator\_color1  C'34,139,34,30', C'178,34,34,30' // Verde y Rojo traslúcidos

// Configuración del Plot 2: Línea central del VWAP  
\#property indicator\_label2  "VWAP Line"  
\#property indicator\_type2   DRAW\_LINE  
\#property indicator\_color2  clrAqua  
\#property indicator\_style2  STYLE\_SOLID  
\#property indicator\_width2  2

// Parámetros de entrada  
input double InpDeviationMultiplier \= 1.0; // Multiplicador de Banda

// Buffers del indicador  
double BufferUpperBand;  
double BufferLowerBand;  
double BufferVWAP;

// Buffers estadísticos de cálculo intermedio  
double BufferSumPV;  
double BufferSumV;

//+------------------------------------------------------------------+  
//| Custom indicator initialization function                         |  
//+------------------------------------------------------------------+  
int OnInit()  
  {  
   // Mapeo de los buffers destinados al dibujo (PLOT)  
   SetIndexBuffer(0, BufferUpperBand, INDICATOR\_DATA);  
   SetIndexBuffer(1, BufferLowerBand, INDICATOR\_DATA);  
   SetIndexBuffer(2, BufferVWAP,      INDICATOR\_DATA);

   // Mapeo de los buffers destinados a cálculos estadísticos intermedios  
   SetIndexBuffer(3, BufferSumPV,      INDICATOR\_CALCULATIONS);  
   SetIndexBuffer(4, BufferSumV,       INDICATOR\_CALCULATIONS);

   // Declarar el valor vacío para evitar interpolaciones incorrectas en el renderizado  
   PlotIndexSetDouble(0, PLOT\_EMPTY\_VALUE, EMPTY\_VALUE);  
   PlotIndexSetDouble(1, PLOT\_EMPTY\_VALUE, EMPTY\_VALUE);

   IndicatorSetString(INDICATOR\_SHORTNAME, "Intraday VWAP Bands");  
   return(INIT\_SUCCEEDED);  
  }

//+------------------------------------------------------------------+  
//| Custom indicator iteration function                              |  
//+------------------------------------------------------------------+  
int OnCalculate(const int rates\_total,  
                const int prev\_calculated,  
                const datetime \&time,  
                const double \&open,  
                const double \&high,  
                const double \&low,  
                const double \&close,  
                const long \&tick\_volume,  
                const long \&volume,  
                const int \&spread)  
  {  
   if(rates\_total \< 2\)  
      return(0);

   // Punto de partida optimizado para evitar recalcular todo el historial en cada tick  
   int start \= (prev\_calculated \== 0)? 0 : prev\_calculated \- 1;

   for(int i \= start; i \< rates\_total; i++)  
     {  
      // Determinar el inicio del día del bróker para aplicar el reset estadístico  
      datetime current\_day \= time\[i\] \- (time\[i\] % 86400);  
      int session\_start\_idx \= i;

      // Buscar de forma retrospectiva el primer índice de la sesión diaria actual  
      while(session\_start\_idx \> 0 && (time\[session\_start\_idx\] \- (time\[session\_start\_idx\] % 86400)) \== current\_day)  
        {  
         session\_start\_idx--;  
        }  
      session\_start\_idx++; // Ajustar al índice de inicio de la sesión

      double sum\_pv \= 0.0;  
      double sum\_v \= 0.0;

      // Primer paso: Calcular el VWAP acumulado intradía  
      for(int k \= session\_start\_idx; k \<= i; k++)  
        {  
         double typical\_price \= (high\[k\] \+ low\[k\] \+ close\[k\]) / 3.0;  
         double vol \= (volume\[k\] \> 0)? (double)volume\[k\] : ((tick\_volume\[k\] \> 0)? (double)tick\_volume\[k\] : 1.0);

         sum\_pv \+= typical\_price \* vol;  
         sum\_v \+= vol;  
        }

      BufferSumPV\[i\] \= sum\_pv;  
      BufferSumV\[i\] \= sum\_v;

      if(sum\_v \> 0\)  
        {  
         BufferVWAP\[i\] \= sum\_pv / sum\_v;

         // Segundo paso: Calcular la varianza acumulada ponderada por volumen  
         double sum\_variance \= 0.0;  
         for(int k \= session\_start\_idx; k \<= i; k++)  
           {  
            double typical\_price \= (high\[k\] \+ low\[k\] \+ close\[k\]) / 3.0;  
            double vol \= (volume\[k\] \> 0)? (double)volume\[k\] : ((tick\_volume\[k\] \> 0)? (double)tick\_volume\[k\] : 1.0);  
            sum\_variance \+= vol \* MathPow(typical\_price \- BufferVWAP\[i\], 2);  
           }

         double std\_dev \= MathSqrt(sum\_variance / sum\_v);  
         BufferUpperBand\[i\] \= BufferVWAP\[i\] \+ (InpDeviationMultiplier \* std\_dev);  
         BufferLowerBand\[i\] \= BufferVWAP\[i\] \- (InpDeviationMultiplier \* std\_dev);  
        }  
      else  
        {  
         BufferVWAP\[i\] \= close\[i\];  
         BufferUpperBand\[i\] \= close\[i\];  
         BufferLowerBand\[i\] \= close\[i\];  
        }  
     }

   return(rates\_total);  
  }

### **Indicador 2: Heikin Ashi Smoothed Completo con Filtro EMA de Doble Etapa (DRAW\_CANDLES)**

Este indicador implementa la variante suavizada de Heikin Ashi mediante una arquitectura modular.30 Utiliza cuatro handles internos del indicador nativo iMA para realizar un primer filtrado de precios y, posteriormente, calcula las coordenadas correspondientes para dibujarlas como velas japonesas.30

Fragmento de código  
//+------------------------------------------------------------------+  
//|                                         Heikin\_Ashi\_Smoothed.mq5 |  
//|                                                                  |  
//+------------------------------------------------------------------+  
\#property copyright "Copyright 2026"  
\#property version   "1.00"  
\#property indicator\_chart\_window  
\#property indicator\_buffers 8  
\#property indicator\_plots   1

// Configuración del Plot para dibujar las velas del indicador (DRAW\_CANDLES)  
\#property indicator\_label1  "Heikin Ashi Smoothed"  
\#property indicator\_type1   DRAW\_CANDLES  
\#property indicator\_color1  clrForestGreen, clrCrimson, clrForestGreen, clrCrimson // Toro, Oso, Mecha Toro, Mecha Oso

// Parámetros de entrada  
input int            InpSmoothPeriod \= 10;          // Periodo del suavizado inicial  
input ENUM\_MA\_METHOD InpSmoothMethod \= MODE\_EMA;    // Método de suavizado inicial

// Buffers obligatorios para el dibujo de velas (DRAW\_CANDLES)  
double BufferHAOpen;  
double BufferHAHigh;  
double BufferHALow;  
double BufferHAClose;

// Buffers para copiar las series suavizadas mediante los handles MA  
double BufferSmoothOpen;  
double BufferSmoothHigh;  
double BufferSmoothLow;  
double BufferSmoothClose;

// Handles para las medias móviles del suavizado previo  
int handle\_open, handle\_high, handle\_low, handle\_close;

//+------------------------------------------------------------------+  
//| Custom indicator initialization function                         |  
//+------------------------------------------------------------------+  
int OnInit()  
  {  
   // Mapeo de los buffers destinados a DRAW\_CANDLES (deben estar en orden estricto)  
   SetIndexBuffer(0, BufferHAOpen,  INDICATOR\_DATA);  
   SetIndexBuffer(1, BufferHAHigh,  INDICATOR\_DATA);  
   SetIndexBuffer(2, BufferHALow,   INDICATOR\_DATA);  
   SetIndexBuffer(3, BufferHAClose, INDICATOR\_DATA);

   // Mapeo de los buffers internos de cálculo para guardar las medias móviles  
   SetIndexBuffer(4, BufferSmoothOpen,  INDICATOR\_CALCULATIONS);  
   SetIndexBuffer(5, BufferSmoothHigh,  INDICATOR\_CALCULATIONS);  
   SetIndexBuffer(6, BufferSmoothLow,   INDICATOR\_CALCULATIONS);  
   SetIndexBuffer(7, BufferSmoothClose, INDICATOR\_CALCULATIONS);

   // Instanciación de los handles de medias móviles nativas sobre cada serie de precio  
   handle\_open  \= iMA(\_Symbol, \_Period, InpSmoothPeriod, 0, InpSmoothMethod, PRICE\_OPEN);  
   handle\_high  \= iMA(\_Symbol, \_Period, InpSmoothPeriod, 0, InpSmoothMethod, PRICE\_HIGH);  
   handle\_low   \= iMA(\_Symbol, \_Period, InpSmoothPeriod, 0, InpSmoothMethod, PRICE\_LOW);  
   handle\_close \= iMA(\_Symbol, \_Period, InpSmoothPeriod, 0, InpSmoothMethod, PRICE\_CLOSE);

   if(handle\_open  \== INVALID\_HANDLE || handle\_high \== INVALID\_HANDLE ||  
      handle\_low   \== INVALID\_HANDLE || handle\_close \== INVALID\_HANDLE)  
     {  
      Print("Fallo crítico al crear los handles de las medias móviles para el suavizado.");  
      return(INIT\_FAILED);  
     }

   IndicatorSetString(INDICATOR\_SHORTNAME, "Heikin Ashi Smoothed");  
   return(INIT\_SUCCEEDED);  
  }

//+------------------------------------------------------------------+  
//| Custom indicator deinitialization function                       |  
//+------------------------------------------------------------------+  
void OnDeinit(const int reason)  
  {  
   // Liberación obligatoria de los handles para optimizar recursos en el terminal  
   IndicatorRelease(handle\_open);  
   IndicatorRelease(handle\_high);  
   IndicatorRelease(handle\_low);  
   IndicatorRelease(handle\_close);  
  }

//+------------------------------------------------------------------+  
//| Custom indicator iteration function                              |  
//+------------------------------------------------------------------+  
int OnCalculate(const int rates\_total,  
                const int prev\_calculated,  
                const datetime \&time,  
                const double \&open,  
                const double \&high,  
                const double \&low,  
                const double \&close,  
                const long \&tick\_volume,  
                const long \&volume,  
                const int \&spread)  
  {  
   if(rates\_total \< InpSmoothPeriod \+ 2\)  
      return(0);

   // Validar la sincronización asíncrona de los datos calculados por las medias móviles  
   if(BarsCalculated(handle\_open) \< rates\_total  || BarsCalculated(handle\_high) \< rates\_total ||  
      BarsCalculated(handle\_low) \< rates\_total   || BarsCalculated(handle\_close) \< rates\_total)  
     {  
      return(0);  
     }

   // Copiar los datos de precios suavizados hacia los buffers de cálculo internos  
   if(CopyBuffer(handle\_open,  0, 0, rates\_total, BufferSmoothOpen)  \<= 0 ||  
      CopyBuffer(handle\_high,  0, 0, rates\_total, BufferSmoothHigh)  \<= 0 ||  
      CopyBuffer(handle\_low,   0, 0, rates\_total, BufferSmoothLow)   \<= 0 ||  
      CopyBuffer(handle\_close, 0, 0, rates\_total, BufferSmoothClose) \<= 0\)  
     {  
      Print("Fallo al copiar los datos de suavizado de medias móviles.");  
      return(0);  
     }

   // Determinar el índice de inicio del cálculo incremental  
   int start \= (prev\_calculated \== 0)? 1 : prev\_calculated \- 1;

   for(int i \= start; i \< rates\_total; i++)  
     {  
      // Primer cálculo histórico de Heikin Ashi para inicializar la serie  
      if(i \== 1\)  
        {  
         BufferHAOpen\[i\]  \= BufferSmoothOpen\[i\];  
         BufferHAClose\[i\] \= (BufferSmoothOpen\[i\] \+ BufferSmoothHigh\[i\] \+ BufferSmoothLow\[i\] \+ BufferSmoothClose\[i\]) / 4.0;  
         BufferHAHigh\[i\]  \= BufferSmoothHigh\[i\];  
         BufferHALow\[i\]   \= BufferSmoothLow\[i\];  
         continue;  
        }

      // Ecuaciones recursivas de velas Heikin Ashi sobre precios suavizados  
      BufferHAClose\[i\] \= (BufferSmoothOpen\[i\] \+ BufferSmoothHigh\[i\] \+ BufferSmoothLow\[i\] \+ BufferSmoothClose\[i\]) / 4.0;  
      BufferHAOpen\[i\]  \= (BufferHAOpen\[i-1\] \+ BufferHAClose\[i-1\]) / 2.0;  
      BufferHAHigh\[i\]  \= MathMax(BufferSmoothHigh\[i\], MathMax(BufferHAOpen\[i\], BufferHAClose\[i\]));  
      BufferHALow\[i\]   \= MathMin(BufferSmoothLow\[i\],  MathMin(BufferHAOpen\[i\], BufferHAClose\[i\]));  
     }

   return(rates\_total);  
  }

### **Indicador 3: ML Feature Engineering Engine (Rolling Z-Score, Min-Max, Volatilidad de Ticks y Divergencia de RSI)**

Este indicador está diseñado específicamente como un procesador estadístico para alimentar modelos de machine learning.33 Calcula de forma simultánea cuatro variables cuantitativas limpias y estacionales, e inyecta un estado binario representativo del flujo de divergencias en un buffer exclusivo.38

Fragmento de código  
//+------------------------------------------------------------------+  
//|                                         ML\_Feature\_Engine.mq5    |  
//|                                                                  |  
//+------------------------------------------------------------------+  
\#property copyright "Copyright 2026"  
\#property version   "1.00"  
\#property indicator\_separate\_window  
\#property indicator\_buffers 8  
\#property indicator\_plots   5

// Definición de las características del oscilador para ML  
\#property indicator\_label1  "Z-Score de Precio"  
\#property indicator\_type1   DRAW\_LINE  
\#property indicator\_color1  clrOrange

\#property indicator\_label2  "Min-Max de Precio"  
\#property indicator\_type2   DRAW\_LINE  
\#property indicator\_color2  clrLime

\#property indicator\_label3  "Z-Score de Volatilidad"  
\#property indicator\_type3   DRAW\_LINE  
\#property indicator\_color3  clrOrchid

\#property indicator\_label4  "Momentum de RSI"  
\#property indicator\_type4   DRAW\_LINE  
\#property indicator\_color4  clrDeepSkyBlue

\#property indicator\_label5  "Señales de Divergencia"  
\#property indicator\_type5   DRAW\_HISTOGRAM  
\#property indicator\_color5  clrRed

// Parámetros de entrada  
input int InpRollingWindow \= 20; // Ventana rodante para el cálculo de estadísticas  
input int InpRsiPeriod      \= 14; // Periodo para el indicador de momentum RSI

// Buffers expuestos para el consumo del modelo de ML  
double BufferPriceZScore;  
double BufferPriceMinMax;  
double BufferVolZScore;  
double BufferRSIMomentum;  
double BufferDivergence;

// Buffers internos para cálculos auxiliares  
double BufferRSI;  
double BufferRollingMean;  
double BufferRollingStdDev;

// Handle para el indicador RSI integrado  
int rsi\_handle;

//+------------------------------------------------------------------+  
//| Custom indicator initialization function                         |  
//+------------------------------------------------------------------+  
int OnInit()  
  {  
   // Mapeo de buffers de salida (PLOT)  
   SetIndexBuffer(0, BufferPriceZScore, INDICATOR\_DATA);  
   SetIndexBuffer(1, BufferPriceMinMax, INDICATOR\_DATA);  
   SetIndexBuffer(2, BufferVolZScore,   INDICATOR\_DATA);  
   SetIndexBuffer(3, BufferRSIMomentum, INDICATOR\_DATA);  
   SetIndexBuffer(4, BufferDivergence,  INDICATOR\_DATA);

   // Mapeo de buffers intermedios de cálculo  
   SetIndexBuffer(5, BufferRSI,            INDICATOR\_CALCULATIONS);  
   SetIndexBuffer(6, BufferRollingMean,    INDICATOR\_CALCULATIONS);  
   SetIndexBuffer(7, BufferRollingStdDev,  INDICATOR\_CALCULATIONS);

   // Crear el handle del indicador de momentum RSI  
   rsi\_handle \= iRSI(\_Symbol, \_Period, InpRsiPeriod, PRICE\_CLOSE);  
   if(rsi\_handle \== INVALID\_HANDLE)  
     {  
      Print("Fallo al inicializar el handle del indicador RSI.");  
      return(INIT\_FAILED);  
     }

   IndicatorSetString(INDICATOR\_SHORTNAME, "ML\_Feature\_Engine");  
   return(INIT\_SUCCEEDED);  
  }

//+------------------------------------------------------------------+  
//| Custom indicator deinitialization function                       |  
//+------------------------------------------------------------------+  
void OnDeinit(const int reason)  
  {  
   IndicatorRelease(rsi\_handle);  
  }

//+------------------------------------------------------------------+  
//| Custom indicator iteration function                              |  
//+------------------------------------------------------------------+  
int OnCalculate(const int rates\_total,  
                const int prev\_calculated,  
                const datetime \&time,  
                const double \&open,  
                const double \&high,  
                const double \&low,  
                const double \&close,  
                const long \&tick\_volume,  
                const long \&volume,  
                const int \&spread)  
  {  
   if(rates\_total \< InpRollingWindow \+ 5\)  
      return(0);

   // Comprobar la sincronización del indicador de volatilidad intermedio  
   if(BarsCalculated(rsi\_handle) \< rates\_total)  
      return(0);

   // Copiar los valores del RSI hacia el buffer de cálculo  
   if(CopyBuffer(rsi\_handle, 0, 0, rates\_total, BufferRSI) \<= 0\)  
      return(0);

   int start \= (prev\_calculated \== 0)? InpRollingWindow : prev\_calculated \- 1;

   for(int i \= start; i \< rates\_total; i++)  
     {  
      // 1\. Z-Score móvil del precio de cierre  
      double sum \= 0.0;  
      for(int j \= 0; j \< InpRollingWindow; j++)  
         sum \+= close\[i \- j\];  
      double mean \= sum / (double)InpRollingWindow;  
      BufferRollingMean\[i\] \= mean;

      double variance \= 0.0;  
      for(int j \= 0; j \< InpRollingWindow; j++)  
         variance \+= MathPow(close\[i \- j\] \- mean, 2);  
      double std\_dev \= MathSqrt(variance / (double)InpRollingWindow);  
      BufferRollingStdDev\[i\] \= std\_dev;

      BufferPriceZScore\[i\] \= (std\_dev \> 0.0)? (close\[i\] \- mean) / std\_dev : 0.0;

      // 2\. Normalización Min-Max del precio de cierre en ventana deslizante  
      double min\_val \= close\[i\];  
      double max\_val \= close\[i\];  
      for(int j \= 0; j \< InpRollingWindow; j++)  
        {  
         if(close\[i \- j\] \< min\_val) min\_val \= close\[i \- j\];  
         if(close\[i \- j\] \> max\_val) max\_val \= close\[i \- j\];  
        }  
      double range \= max\_val \- min\_val;  
      BufferPriceMinMax\[i\] \= (range \> 0.0)? (close\[i\] \- min\_val) / range : 0.5;

      // 3\. Z-Score móvil del volumen de ticks (Volatilidad estacionalizada)  
      double vol\_sum \= 0.0;  
      for(int j \= 0; j \< InpRollingWindow; j++)  
         vol\_sum \+= (double)tick\_volume\[i \- j\];  
      double vol\_mean \= vol\_sum / (double)InpRollingWindow;

      double vol\_variance \= 0.0;  
      for(int j \= 0; j \< InpRollingWindow; j++)  
         vol\_variance \+= MathPow((double)tick\_volume\[i \- j\] \- vol\_mean, 2);  
      double vol\_std\_dev \= MathSqrt(vol\_variance / (double)InpRollingWindow);

      BufferVolZScore\[i\] \= (vol\_std\_dev \> 0.0)? ((double)tick\_volume\[i\] \- vol\_mean) / vol\_std\_dev : 0.0;

      // 4\. Momentum (ROC) del RSI  
      BufferRSIMomentum\[i\] \= BufferRSI\[i\] \- BufferRSI\[i \- 1\];

      // 5\. Motor de detección automática de divergencias (Salida binaria: \+1 Alcista, \-1 Bajista, 0 Neutro)  
      BufferDivergence\[i\] \= 0.0;  
        
      // La validación del pivote requiere comprobar barras a la izquierda y derecha para evitar sesgos  
      int lookback\_pivot \= i \- 3;  
      if(lookback\_pivot \> InpRollingWindow)  
        {  
         // Comprobación de pivote de mínimo local en el precio de cierre (Trough)  
         bool is\_price\_trough \= true;  
         bool is\_rsi\_trough \= true;  
         for(int d \= 1; d \<= 3; d++)  
           {  
            if(close\[lookback\_pivot \- d\] \<= close\[lookback\_pivot\] || close\[lookback\_pivot \+ d\] \< close\[lookback\_pivot\])  
               is\_price\_trough \= false;  
            if(BufferRSI\[lookback\_pivot \- d\] \<= BufferRSI\[lookback\_pivot\] || BufferRSI\[lookback\_pivot \+ d\] \< BufferRSI\[lookback\_pivot\])  
               is\_rsi\_trough \= false;  
           }

         // Comprobación de divergencia alcista regular  
         if(is\_price\_trough &&\!is\_rsi\_trough && close\[lookback\_pivot\] \< close\[lookback\_pivot \- 10\] && BufferRSI\[lookback\_pivot\] \> BufferRSI\[lookback\_pivot \- 10\])  
           {  
            BufferDivergence\[i\] \= 1.0; // Señal alcista registrada para ML  
           }

         // Comprobación de pivote de máximo local en el precio de cierre (Peak)  
         bool is\_price\_peak \= true;  
         bool is\_rsi\_peak \= true;  
         for(int d \= 1; d \<= 3; d++)  
           {  
            if(close\[lookback\_pivot \- d\] \>= close\[lookback\_pivot\] || close\[lookback\_pivot \+ d\] \> close\[lookback\_pivot\])  
               is\_price\_peak \= false;  
            if(BufferRSI\[lookback\_pivot \- d\] \>= BufferRSI\[lookback\_pivot\] || BufferRSI\[lookback\_pivot \+ d\] \> BufferRSI\[lookback\_pivot\])  
               is\_rsi\_peak \= false;  
           }

         // Comprobación de divergencia bajista regular  
         if(is\_price\_peak &&\!is\_rsi\_peak && close\[lookback\_pivot\] \> close\[lookback\_pivot \- 10\] && BufferRSI\[lookback\_pivot\] \< BufferRSI\[lookback\_pivot \- 10\])  
           {  
            BufferDivergence\[i\] \= \-1.0; // Señal bajista registrada para ML  
           }  
        }  
     }

   return(rates\_total);  
  }

## **9\. Conclusión y Recomendaciones Cuantitativas**

El desarrollo de indicadores personalizados en MetaTrader 5 (MQL5) requiere un enfoque riguroso de ingeniería de software para maximizar la velocidad de cálculo y garantizar la validez estadística de los datos.2 La migración del procesamiento matemático y la normalización de datos directamente al entorno compilado de MQL5 elimina latencias críticas y simplifica de forma notable el proceso de inferencia de los modelos de inteligencia artificial aplicados al trading.2  
Al crear herramientas avanzadas en MQL5, se recomienda priorizar el uso de cálculos puramente incrementales, evitar recalcular innecesariamente el histórico de velas, comprobar de forma estricta la disponibilidad de datos de otros indicadores y aplicar transformaciones matemáticas sobre ventanas rodantes estrictamente cerradas.15 Este enfoque metodológico previene sesgos de anticipación en los modelos de machine learning y asegura que los sistemas de trading algorítmico funcionen de forma consistente y eficiente en entornos de producción en tiempo real.

#### **Fuentes citadas**

1. Indicator Styles in Examples \- Custom Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/indicators\_examples](https://www.mql5.com/en/docs/customind/indicators_examples)  
2. MQL4 vs MQL5: What is the Difference? (2026 EA Development Guide) \- Viprasol, acceso: junio 28, 2026, [https://viprasol.com/blog/mql4-vs-mql5-programming-comparison/](https://viprasol.com/blog/mql4-vs-mql5-programming-comparison/)  
3. Best cTrader Indicators for 2026: Top Free & Custom Tools \- WeMasterTrade, acceso: junio 28, 2026, [https://wemastertrade.com/best-ctrader-indicators/](https://wemastertrade.com/best-ctrader-indicators/)  
4. OnCalculate \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/oncalculate](https://www.mql5.com/en/docs/event_handlers/oncalculate)  
5. Main indicator event: OnCalculate \- Creating application programs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/indicators\_make/indicators\_oncalculate](https://www.mql5.com/en/book/applications/indicators_make/indicators_oncalculate)  
6. Coding Custom Indicators in MQL5: A Practical Guide for Algo Traders | by TradersMarket.io, acceso: junio 28, 2026, [https://medium.com/@tradersmarket.io/coding-custom-indicators-in-mql5-a-practical-guide-for-algo-traders-923bb6f2698b](https://medium.com/@tradersmarket.io/coding-custom-indicators-in-mql5-a-practical-guide-for-algo-traders-923bb6f2698b)  
7. Custom Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind](https://www.mql5.com/en/docs/customind)  
8. Not getting correct results for indicators using iCustom and CopyBuffer \- Price Chart \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/466273](https://www.mql5.com/en/forum/466273)  
9. Drawing Styles \- Indicator Constants \- Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/indicatorconstants/drawstyles](https://www.mql5.com/en/docs/constants/indicatorconstants/drawstyles)  
10. mt-mql/supertrend.mq5 at master · lanastasov/mt-mql · GitHub, acceso: junio 28, 2026, [https://github.com/lanastasov/mt-mql/blob/master/supertrend.mq5](https://github.com/lanastasov/mt-mql/blob/master/supertrend.mq5)  
11. DRAW\_BARS \- Indicator Styles in Examples \- Custom Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/indicators\_examples/draw\_bars](https://www.mql5.com/en/docs/customind/indicators_examples/draw_bars)  
12. DRAW\_FILLING \- Indicator Styles in Examples \- Custom Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/indicators\_examples/draw\_filling](https://www.mql5.com/en/docs/customind/indicators_examples/draw_filling)  
13. DRAW\_FILLING type indicator buffers mixed up? \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/38213](https://www.mql5.com/en/forum/38213)  
14. Indicator DRAW\_FILLING not working peoperly \- Moving Average, MA \- Technical Indicators \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/491802](https://www.mql5.com/en/forum/491802)  
15. CopyBuffer \- Timeseries and Indicators Access \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/copybuffer](https://www.mql5.com/en/docs/series/copybuffer)  
16. Indicator Supertrend on trading view with formular \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/458830](https://www.mql5.com/en/forum/458830)  
17. How can I avoid drawing line from Long to Short Change in Super Trend Indicator \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/436194](https://www.mql5.com/en/forum/436194)  
18. MQL5 CopyBuffer Explained: Syntax, Usage, and Common Errors \- トリロジー金融メディア, acceso: junio 28, 2026, [https://finance.trgy.co.jp/en/mql5-en/reference-en/copybuffer/](https://finance.trgy.co.jp/en/mql5-en/reference-en/copybuffer/)  
19. Technical Indicator Functions \- MQL5 features \- MQL4 Reference, acceso: junio 28, 2026, [https://docs.mql4.com/mql5\_language/mql5\_functions/mql5\_tech\_indicators](https://docs.mql4.com/mql5_language/mql5_functions/mql5_tech_indicators)  
20. Best Automation Tools for MT5 in 2025 | For Traders, acceso: junio 28, 2026, [https://www.fortraders.com/blog/automation-tools-mt5](https://www.fortraders.com/blog/automation-tools-mt5)  
21. How to Add Custom Indicators to MetaTrader 4&5 \- Switch Markets, acceso: junio 28, 2026, [https://www.switchmarkets.com/learn/add-custom-indicators-metatrader](https://www.switchmarkets.com/learn/add-custom-indicators-metatrader)  
22. good practice with OnCalculate() function \- Swing Trading \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/449287](https://www.mql5.com/en/forum/449287)  
23. Optimizing EA Performance: Include Files vs. iCustom() for Indicators \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/482154](https://www.mql5.com/en/forum/482154)  
24. Optimization slow when using custom indicator \- Moving Average, MA \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/10704](https://www.mql5.com/en/forum/10704)  
25. how to return an array of copybuffer? \- Symbols \- Technical Indicators \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/349542](https://www.mql5.com/en/forum/349542)  
26. LumenQuant Intraday VWAP Bands | Buy Trading Indicator for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/market/product/178702](https://www.mql5.com/en/market/product/178702)  
27. AE VWAP mtf | Free Download Trading Indicator for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/market/product/173364](https://www.mql5.com/en/market/product/173364)  
28. VWAP Calculator \[Free Tool\] \- Switch Markets, acceso: junio 28, 2026, [https://www.switchmarkets.com/tools/vwap-calculator](https://www.switchmarkets.com/tools/vwap-calculator)  
29. VWAP indicator (Volume Weighted Average Price) \- InstaForex, acceso: junio 28, 2026, [https://www.instaforex.com/knowledge\_base/274-vwap-indicator](https://www.instaforex.com/knowledge_base/274-vwap-indicator)  
30. Price Action Analysis Toolkit Development (Part 54): Filtering Trends with EMA and Smoothed Price Action \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/20851](https://www.mql5.com/en/articles/20851)  
31. UTBot Alerts | Free Download Trading Indicator for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/market/product/166242](https://www.mql5.com/en/market/product/166242)  
32. Institutional Z-Score Statistical Reversion \- indicator for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/code/71270](https://www.mql5.com/en/code/71270)  
33. Best Practices for Feature Engineering in Trading \- Traidies.com, acceso: junio 28, 2026, [https://www.traidies.com/blog/feature-engineering-best-practices-trading](https://www.traidies.com/blog/feature-engineering-best-practices-trading)  
34. Multifactor Carry Momentum | MetaTrader 5용 트레이딩 로봇 ... \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/ko/market/product/178921](https://www.mql5.com/ko/market/product/178921)  
35. Mastering Algo Trading: From Cointegration Tests to Live Signals | by Saurav | Medium, acceso: junio 28, 2026, [https://medium.com/@writeronepagecode/mastering-algo-trading-from-cointegration-tests-to-live-signals-f586de841d12](https://medium.com/@writeronepagecode/mastering-algo-trading-from-cointegration-tests-to-live-signals-f586de841d12)  
36. indicator for MetaTrader 5 \- ZScore \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/code/19846](https://www.mql5.com/en/code/19846)  
37. JMA Z-score \- indicator for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/code/22432](https://www.mql5.com/en/code/22432)  
38. Neuron Quant Standard Deviation System | Buy Trading Indicator for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/market/product/179806](https://www.mql5.com/en/market/product/179806)  
39. Lyapunov exponent | Buy Trading Indicator for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/market/product/168070](https://www.mql5.com/en/market/product/168070)  
40. ML-Based Momentum Indicator for MT4 | PDF | Applied Mathematics \- Scribd, acceso: junio 28, 2026, [https://www.scribd.com/document/890807271/ML-machine-Learning-Momentum-Indicator](https://www.scribd.com/document/890807271/ML-machine-Learning-Momentum-Indicator)  
41. HTF Reversal Divergences \- indicator for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/code/71611](https://www.mql5.com/en/code/71611)  
42. Automating Trading Strategies in MQL5 (Part 37): Regular RSI Divergence Convergence with Visual Indicators, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/20031](https://www.mql5.com/en/articles/20031)  
43. Why Malaysian Traders Prefer the MT5 Trading Platform for Multi-Asset Trading, acceso: junio 28, 2026, [https://hackthecrisisnorway.com/en/finance-en/why-malaysian-traders-prefer-the-mt5-trading-platform-for-multi-asset-trading/](https://hackthecrisisnorway.com/en/finance-en/why-malaysian-traders-prefer-the-mt5-trading-platform-for-multi-asset-trading/)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAaCAYAAABYQRdDAAAA/0lEQVR4XmNgGAW0AIxA/AGI/yPhtygqIOAvA0IexCYKzGeAaHBAE0cGIHmSQAIDRFM1mjgMbARiY3RBQkCZAWLoNnQJIOAC4mfogsQCkKEf0QWB4Be6ACkAFhHIIBmIa9DESALYDEXnkwzQDb0GxKJIfBDIZoCoCUYTxwm+MyAMBUXcESQ5ZECS6/cwQDTIQWlcAJ8cBqhngGh4DMSeaHIwEArEN6Hs3UB8GEkOK3BkgBj6Hl0CCVwF4iggPgblE3Q1CwNEEag8wAVA8qC8r4QuQQmAuewVENsiS5AL/IH4OpR9HojtgbgfIU0eWMcAMQgEVIH4BgPuCB0FIxIAAHy/OwvbovofAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAbCAYAAACqenW9AAAAo0lEQVR4XmNgGNrgKhD/AeL/QMyJJocV7GWAKCYKgBSSpHg6uiA2IMUAUSyBLoENzGJAdUIbED9FE4MDZPceAmI+IF6FJIYCQIJzgfgSELNCxeYB8T24CiiQZECYnIMmhwEiGCAKQREDovegSqOC6wyobgOxpyDxUQBI8hoafyWU/RFJHAxAkmFo/GwgZgTiY0jiDGJQSWTgBxX7gCY+CgYbAADqfCrdk3T3XwAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAZCAYAAAAIcL+IAAAAdElEQVR4XmNgGAW0AolAvAyIbdAlkMF/IFaAsiuBuAohhQD7gPgEEh+kqROJDwefGCCS84FYFk0OBWgyQBTC8HtUaQiYC8QdSHw5BohiDAAS3I7EV4eKYYDvQJwPxEIMkOABKQKxsQIeII4AYjV0iVFAPQAAyIQVuMnEzLsAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,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>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAaCAYAAAC6nQw6AAAAr0lEQVR4XmNgGAWjgDaAH4jdgdgLDRMN5IH4Px6cjlCKG/AyQBQXIIm9AuJ/SHyiAMiQDWhiKVBxbOAhugAIgPyPTcMKBuziINCILgACOxiwawCJfUAXxAeWMWAaJAIV40MT9wDio0CcgCYOBsIMqAYxQfnRSGIwMB+IfYH4PLoEDNgwIKL5JhALokqjgB9ALI0uSA5ADwayQAMQzwZiOzRxkoEAED9lQE24o2DIAgAJsie8V8hIEAAAAABJRU5ErkJggg==>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAZCAYAAABdEVzWAAABsklEQVR4Xu2VPShGURjHHyUfKVEWm5ASg2JSJpkkWXyVCaWMNmUxKQYGE4uy2WQTm3yUokRkkmRQikIi/k/nHJ73cZ/rvokM91e/3vP8z7nvOfee9z2XKOX/0KGDCBp08JvUwSf/+QKbMrs/OINdOtQcwh04CgdgH+yFPV7JBLyDD3BQ9TFvsMq3S+EjfIVjsA0u+DHXfkwsPNDyVow7huuiPoJbomb4Gqsu95/8RBPBF7eQe/zVsNIrv7RY1QHOSny7zNcSXY9Tgi0M7OsAbMN6UR/Q10kYzhZVLZF1LiXcQotmuKKysLUanT/Dft9uhcOq70ckWUAgKud6Gd6IbBJ2ijprlryaqAUwVi7Jg1eiriX3r94U2bfwJBU6JHsBVi7h8ywg/0RF8ET0mQyRPYm1ACsPTMF2UV/AVVGfi7YJn8bWJPcU3ceZddcF8FJlPH5e1LOibRJ3990U3cdZow49fOJr9MLmRNskbmEM942IetpnUcyQOy40u3BN1Im2kieRP1RNIbkxe+Ter/xqyckY4eAttCbMp8+b4R8/v9b+jFMdKGrIHbYbuiMlJSUlS94BuQl7cpPHMhYAAAAASUVORK5CYII=>

[image9]: <data:image/png;base64,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>

[image10]: <data:image/png;base64,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>

[image11]: <data:image/png;base64,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>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAxCAYAAABnGvUlAAAIV0lEQVR4Xu3ce6ilVRnH8VVqmZmW0dVyRM3saiZUpNAFk+yCUmpp4lBGpQWp3SyqGUuLIq3ASiwKSkWNsj/qL1Es0lLBKEjDoWa6qN0vaBfTyvXjXU/72b/zvu/eZ845M3OO3w8s9lrPu97r3vvd66y13lMKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACdWzyABd7mgeYFNb205S/IC7aRXWvay4Nr3M88sAT/88CcPlPTkzy4Bj2qpk/X9KBW/lh73a+9LoeHeKD6qwcAYC25uSz8AVL58RbL7i4L15lF+1nvwVXmj2X+89YPyikeLNPrK//+VF4pn7ey9vtoi81D693lwe3k0DL/eyE7eaB062/pie1msezosrj9iuo/uOUf3srbmva5dyq/rsXG6Hu+zoMjDi7dNndu5YNqurWm17TyrP0tVt/2jvIAAKwVuuk9MpV3abEh6jV6cRmv02ex9Ve7vvP12MlWXglqKPh+vTyvrV1vexs67r54Xyx7bpldJ+uru6mm6z24gtTT5ceh8jkWy+J7fpbFh/yipp96sEzv9wcpvxzU+N1oMT9PAFgz/AZ3dU33WCy7ovT/AMwyVl/b03aflmIXp/wjUv61Kb9c3lzTl1v+jJoOb/n31vTBlpd31nR5y6uHQsM+sqEs/Mv+31YWXQP1WvS5qL3qXC8pk+Gkr5bpnpHw4ZrO9mB1aU0vankd01Wl28Yr/l+jO45n1fS1FJvH2HsoGvJ7bCq/q6YDUzmGscbewzeUyTDxeWVy7mrcqhzeWNMXWz6vc1xNH2r5MHTcHtfxfc9iWdT39Yb8vkx/dsOPy2Qbn2uv6jGMfNizpivL5Lq9qkx6q46v6eMtP4u+W/+x2KxziO+5Pj/zGNpexPctXQMr0/Yvs5i8o6a3WEzX4Btl+o9L8f1eWNMeFgOAVU8NJN3wPMX8KpeHivxGOSb20+e3NT2n5U9rr7fX9MSa7mzlWFeNgb7tHFDT5pE0D233mJbX0Od1Lb+hpm+1vPc+Kr8u5bVcDin9c9M0h0f1IoUT2+t9Kabl30/57DcpH8t+WLqGizy9dD+44ut+1mL6cZzHqWXhtoKO/7str/0+s3QNR4l1vlnT2y02RMtvSvn/trwaMPFZiWU5H+t4r9DQ/vJ7EelhUzUmNNwXhrbnhuoprs/9kakc4lwVi2Hcf7bX6C39cyv3Dbn38XOMNORXKZ8/k0NeWNM/PGg2Wzl/7/OxfKq96tw+2fInlMkQfnwvg5+H7jW5YQ8Aa4J6AG60mN8As3+l/Fg917efl9T06jK9HTW84iauXr7oXcl1FrPfxcjbjV40UeNraP85/7uaXt7y6v1RGqN1owETPUJHtFcZ2o+ff5QXGw96H+ah9eIHNDy7veZtqrdSk7/Xl27yeW6ABD8G53Vzr93GlPd6QT/aerAi/DLlwzPKwvMZO6780MJYvWyonuLqbYre29fbMonhRfU0xaR9ydv8esqP6TuOvljQ9zCM1QvfrulNHjR5O/69Vz433s5PyyImx5aFPaB9x6c/XgBgTdHNTj+qwXuQsvdYeaheH9X1oYx1LZ6H6m5I+bz9P6S8hoVWQt5fHipUb5X/uPTlf10mw6I6xtPTMvHrpeGdPNyqoZygnrihxrFvR2U98ZkbH58o3fp9Q9e5fG3Kz+LbCRoGzb0wGgqOY1H8CS2f15/1Hvr55p7dj6S81wv7l+mesr6nB9WL6obO8TtWHqrn+uppeDrHc2PspNIte2tNj0vxbOicx3g99Yh91GLB63q5j6YvRG9hlj/fftz5e+/7UDliT035Pr5MQ6fXWAwAVj2/2elHvm8y9D6lG6LMfN0xXjfKfyrTT+/5TV3U6IjGYgy7rYS8b80hC5rr1Xdcntcwbm6IzBq6GSsr/9CU11N3f0vlkPOHpXzE9YSe/oWIxGv0eInqxfyoWYaOVz0jeZ6Tb19ywzHm5omeRPbtip/j7ql8bsp7vfCUMr3OrH2Ieho9FvIxy1A953NB1Yj8icX6zkFzsPL3Lb6T6nV7WYqrflz7oWupz86PLNZXT37ugTJc143VU+NMw9Xx2cjfew2Vq9Ev2sb7Uj7kvE818P1q+DRfIwBY1fSk219KNxcmJsfr3zXoRqreiHyDVyNO8XtT7O8tprk1z09xp22ql0U31UjaTtygo47iG1NMPtDimnOl+TF+Y15O6sFTD5le9YOgOWKaY/Pk0jXEVNb1UkzlLaV7eEDr6DpoErnqaFk8sODHq4aRJn4r+TIZ+oFSIzCXoxc05jGFzS3+FYsrlnvf9N4HzRH0yd1Oy/We5fdQ72n+9x5favHbUkx0zvEefqHl9YOa+f/z0+dP11XXWp895e9oyxTTdX536a67lql+XucxrX6sI/n6aS6eGr/5M63Ps66n3uN4kETUQFK93IOodVRXxzZPY1f7jocM9ECEi2vqD6No+4rrIaCQzyPKuTHp11LnpXPS9dnUYvE99zln2p+uSz6OWH+eeWwxv1T3E73qfcj82ON7n3v4RbHc6JdXtrj+NZDzJ0/zfQoAYPTEpKd1UzUeeNR4WE38/Yu00uZ90nEpzvTAMvLrtZjrpocovCGzFCt5LdUD6eeoNPSQxraQp1CE5byeAIAHiOjVwDD/FxwrRT1rOxI11tTzlXvQlmpbXcsdxbUeAABga2i4Sv/iAtvf8zyAVa3voYk8DA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACsLfcD510q/gSq7gMAAAAASUVORK5CYII=>

[image13]: <data:image/png;base64,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>

[image14]: <data:image/png;base64,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>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF0AAAAaCAYAAADVLFAXAAADl0lEQVR4Xu2YS6hNURzG/96RV14DxU0k8kgGCsmREBMGFMbIo0wYkOQRKQMkxEweAymMyMzbQCklEpKEkPf7bX13rf89//vdtfY5zpUbrV/9O/t839prr/2dtfde+4hkMpnMvFBj2SC03Qg2WoIOrja52udqFHn/Al9cDXXVlw0CbVAb2aiGra5eu/oZ6qOrF6TdbGidpiS+7RZXrVy1cXUyaL3KzepB/9o36qXx7HFRj4x3grxdxlOeuPoq5TatG9v147N9vGlsyyf6brnuqgtpNYWu6CBifJa0B/REYxyW+L76g/Rkw/Fc4vuAIa6OskjgCjsnvo/T5Cmp/lOhL5f4eJsdOgYao7N4fz3pALM0dQIK/POk7Qj6GNKBXgkxfrAQ4birtpKeSLgSr7AYSIWeoubQ54of3CQ2DLETWBG0YaQzsX2XBQ0PI8sg8cHCqyNvtquJpMXQY+0O20uNBxa7mkGa8tdCvyFNQ2FiwcW0GLF204K2lnRom8PnZPKqDeSV2Y4d2z4nmNgx5ot/9sWoOfTYwBhug0Hg+zqjpeB9wcCg7TfaQvG3mwXBW2S8va66mu8pRoq/ApV74vvqbzQei4VDfyz+9vrd1VnyQLNCP8OiYar4NnYVo0G2M1oMzBK0w+AtWFVAv2C0d+ETtzl4dnZdM9tFHBO/clJ6iO/rmdEumW3Ght5P/EQA6OOi8ZSaQtf7eYl0y23xbfoYTUOvxAfx7cazIV7HygcccdUxbNcFDwECHL9aYmOyY13iaorxGBt6KXxiyYv9e5etBmoK/ZbEB2qBj8uLtUr76WxOtVMPq4nLEQ+zGye8nbwieN0N5ojv75Crp+QxfHsBVyV9DjWFXhQK0Icsv2RU2g/ggYU2/HKkaB8P2BCvv5WmP3YRo12tYjGgx6o05ljo2Gcni4GaQ0+tzzeI94ez4dgm3hvMRmC1eB/PgxQaAv42YNRLLe1inHLVnsXAAfH9xR6GFg59ppR/qE7SNPzfDn2N+A75HjdL/Ot46i1T0fU0c1C8PoANomjmQf/GYgH48YsmAYBfYpHg0HFL0jHetUag6tD3iL9s9aT1BPG6j/9ecKDUjGHw9of977h6GLZXNmqRBm0nsBiAx6/cKd6LX5vj7wPc0/n5oNxnIQKHjpWQZoTVDFN16Jk0HHolcuh/gBx6C5BDbwHwXOsmfqVSBNp0lxz6HwH/26Cms0Fou3FsZDKZTOb/5hfldxy1TMlGBAAAAABJRU5ErkJggg==>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAaCAYAAAAaAmTUAAACEklEQVR4Xu2Xu0tcQRjFj42ojUKKgCJCwEKwTyWMgtgIilVSLWghAavYRGKjIJaJ+F9YaCuCnWCfQIjgEwTT+AhifESi38fcccezM3vHFBsJ9wcH13Pmztwzzt5dgYKCGG8zveKAcONecvCc2BB1iVo4IHRMSdTHAXMkuvP0W7Tj5VOUX3mZ47PoJ8pjLkUn5C09jC6zykZGo2ifPIOEMkoz7IK6UzE0z8PdONMB66+RHyuzjMp5DBLLzMNe3MOBxzEbAXSOTTYzQkVjZUIYJJa5QeVCPmOiCTaJN7BzDHAAe2xqVia0kM+BqI5N4hvic6zAZsPkh8q8F31gE4llmmAXCk3siN2kT2xDemH9BQ5QuaY+fHTTdPwMZQYJZWZhL37NgccPNgK4MmeiU9innv7+VfTCG+fjl9HPkc7stV4352WKQUKZa4R31FESvWOTcO+XUQ5y8MvoOsoQwvdjkFAmdjwce2wE2EL1OWLwMVP0YaTHjTFILPOdTQ/9y+WRtyExQmV0nhE28YQyu2xmaMlWNgPoHNtsJsBlPqG8Kfoe9ksZJJTRN1poV7+I+tkM8BH2+nEOEuAyh6Jf2Ws9bj4GCWWUadgbus1+6kT6QVeNRdE57JNLv4ddiP48GpEPl2lD+cg2UGaQWOZfwWWqYVCUqR3/VZl12H8/6jkgdMwgnnmZyUzdHBBuXDsHBQUFf8c9G++MwpEGRhIAAAAASUVORK5CYII=>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEkAAAAWCAYAAACMq7H+AAACdElEQVR4Xu2XS8hNURiGP3dCMiG3AVNKYoCZCUrJ0EBOBkqRlMJAJhLxl5TkNlOMDCiZmJkZKAYSA79rDBQh1+J9rb3O+dZ79toc//51ap+n3jrfu76z1+rb67bNBgwYTdaq0TA2q6HsgA6o2TAWQffUjCyAXqnZUE5B59QkP6HJajYY1iNhNfRVzYZzyWTZfbfBXqTMMJlNDKZ4o0bWQVcsHAoTpC0yDzoMHbWRjWMSNASdgJZIm2crdNnC2KpoF2m6D2rmEfQRumqhD+pWkmH2BHoPrYTmQDegVpLxdyy38Hz+nyuDv39AE13OnsLfBU2FtlnoO0e7Lmt8UCPHrPvO9dRCX/eL+B10ptPc5qYaf2As9FK8DdZ5MWOgLdC3JCMwDTqpZkG7LqxmVZFW9CBP7pmvLbR9gB5Im+eCGhWch8araWE5xULlxkNybZ/jj5blk8jGHuS5I7EnDnqZNjiG1aiAMzTHNQt9cennuK1Gwaf4g3tBVZH+lbdqODiLYqG4VMroZcldV8PBz4zY135pi3xRo6Bdl5k+qJHHahRwD3oGbbL8MjgNLXYx95SDLlYWWvk3F/cbPp9LMfa1KskIL+m5eJFkbAz8KVAH46z7M4cnm7+08loQB8+Nlkc4PwleuBzCWcmcfeJ7hqFZLuahwf/MLWIWI/bF45+Fiznst4yuIu31Rk3wXuSX1s60+TfMYVFiTtlJs9RCoar2HnLROs+5K22Rs9bJeWP5ycErQlIkviHeZ/qdXvapkcJi8n6XwKqVHaP9Aq8q89UcRZJZFFlv+c22H+D96n9xCDqiZuQ4tF3NhjEbeqim0lKjYez2wS+s3ZY9mZ8jaAAAAABJRU5ErkJggg==>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASIAAABiCAYAAAD0kd5uAAAD40lEQVR4Xu3dW+hlUxwH8OVaJuU2jUK8kAcvyqXcGolkihBKzaMXyotLDWVESSGRQm6NvChE8oAXD8IDkShEbvHglgeXGNf1m732/Nd//c9/5n9m7HP+x/l86ttZ63fO6b//D3u19z57rZ0SAAAAAAAAAAAAAAAAAAAAAAAAAACwcxtyHso5sPQvzXk8Z6/tn5iujTknNbU9c9Y1NWBG/ZJzSM6+Of/kvJhzVs760l8NYjtub2p/5Hzf1IAZ9GzOcVU/dvhvq/bf1XvTckDqtqU/WutF7dqmBsygG5t+7NxXlPao07Krcq5ri404ujpxhTm2fGdH7k5Lj8wOLbW9mzow405OS3f41mU5+7XFxlE5F6wwZ5Tv7Egclf3V1B5MO99WYAa9lFbnzh3bdM+I2tamBsyouB70RWnHzv1N9d5hOZuq/tc5P1f9SVibuu06u6lH7Y7S7q9pvZDzYeouuoc4eru8tFfjAAsUsYPen3NMaX/WvNd7e0RtEu5L3d98qqrFYBm1U3LOzzk9dYPmmpz3cs4sn4tTuv4Ct6MnWMVeT91O/Vrp/1j6X27/xILzcj5oiwOLweTP8hrb9WvOHjm3lP77Cx/dph4o63b8n8D/wG85R7TFgcVgcldbXMaRqbu3KPQ/+feeq9rADOt37M2LqsM5OHV/s71/aDlxqvZJaV+c80Npn5ZG34oAzKDvcj5viwO6M41/TSpOHd9I3f1OH+W8mrrpKgC75JGcZ9oiMJ6YlLkldXO2evWvPwCDi9OKPk/k3Ju6yaQAE/FkzkFV/8rUHR3tihjElkss1bEl57GcR3Mezjl627cAKjG58+m2mFY2gRRgt12Uutnjo6xkAumQ6lPHeQvMjavTwpIauyPmVI2Ten0hYI5dn3NhU7s5dUtthGlMIAXmyKmpO/yPNXTitV9e46fy/rQmkAJzpB9wwvOpG3DaSZfTmEAKsMg0JpACLNKflk1qAinAEpOeQAoAAMDcWp+6Xwg3VDl30ScABvJmWjqtwhQLYGI+Td3tCbHIfTg8dYNPrCMNMLhL0ugjnqjd0BYBhhADzsdtMXV1S54AExEDTlycrp1Q6vs0dYBBxICzpqnFzZv1o6x7X6WF55CFV8rrOTm/V3WAscSgc1PVvzWNHlQeKK/19aTl2gBji1/N+p/pNzXv1fZPCwNOPEwxlk3pvVW1AQYTC/7fVtrxWOl4yknv+KoNMJhYMG5jab+bc01pv1xeAQYXD6DcmvNOzrrUXUuKZ9dHGwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD+W/8CQtME1Cg7QCwAAAAASUVORK5CYII=>

[image19]: <data:image/png;base64,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>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAAaCAYAAAB7GkaWAAAAZ0lEQVR4XmNgGHigAMT30QVh4C0Q/0cXpAx0AnECuiAI/IDSIPsckSVmAjETlA2SdEWSY6iF0v0MeFwKkriALggCIgwQSTF0CRA4z4AwshyIpZHkwBI7oOxXyBIg4MwAUfAHXWLEAwCaDRQuuqoUtAAAAABJRU5ErkJggg==>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAaCAYAAACHD21cAAAAk0lEQVR4XmNgGHlgHhB/AuL/SPgjEPchK8IHYJpIAowMEE1n0SUIgWwGiEYvdAlC4CUDGc4EAbL8BwIgTSfQBQkBQv5zQheAgdcM+J0JilOsAJ//aoDYEV0QBJgZIJouoksAgSwDbgMZ+hkgkoFo4jOg4hfQxBkWA/EvIP4LxP8YEM4FYRD/DxB/B2IZmIZRMAoYALcBKZyfMMC3AAAAAElFTkSuQmCC>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAaCAYAAAC+aNwHAAAAy0lEQVR4Xu2TsQ5BQRRER6XSqiVahW8Qrd6/+AGFUqXyIVoKlQbRqXSCkIggzObuS3bHPgrtO8k0M7M3797kAQXKgDpRL68rtafugVfLyt/IysoE5tc1UFxpqiZpwbKlBiFdWKmtARnBsrH4ESukP9+Rt1pEqtSkHtRW/CTusbv8nFpQN++Vw1Ie2f7uWCFr7/9kg3SxD/OrGiip/R0XmF/SQHGlmZrIHxzRg5U6GuBzQDRsSJ2pA+z6R+oZFkgD9mgH+z8qcVxQ8Cdv6xI9Jx1I6SMAAAAASUVORK5CYII=>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAA3CAYAAACxQxY4AAAEKklEQVR4Xu3dS6hvUxgA8IUkRORRSN6UyKsQiiKFQmKkDEyEUiQJpSR5JSQT5SYRMpBHyJQJGXibGWDg/Yi8H+trr9VdZ529/+ffved27/+c36++9re+vc8+++zR19pr75MSAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwiA7oCwvq1b6wBRzRFyYcmmO3vggArB//deMzR2rbjdSmzHvctuyfvlCM/W1/dePrcvzS1aaMnW/KXX0BAFg/+qYhmo03u9q89s7xb19cQD/2haK/V7fkOKerzevhHA/2xRX0vx8AWAeuScubgBjv3NU2dONwcI7Hutr7OS7McXWOw7p9q+mSHI+X/PocZ5T8phy3lbx6JMcnOfZqaqfnOCXHIWlouI7LsX/Zd2WpjXm3G/f3LtzbF9JwT27tavVn78hxebtjhrHfBwCscdEAjEXrxjQ0PVc1td9y7Fry9vjIPxypz/LZCjElzn9xyb/N8U3Jb8/xQsn/zvFxyX/PcXjJQ72+o3Ls2NR/avLWs2n5fer/xs9HavVaQrsv8mgOw7yzkv25AYB1oG8ATutqsXYttLXju/E8eYjGbzW1549m6tGSn9Dtq+5PS5unmEWM42pDV439bBirz1ObuidT+X1puoGLRhkAWEe2T+PNxZ1dLdaltQvr45h4pNiOwwU5PmrqfzT5LPEIcVZMaa/9yRz3lPzoZl9sLyp5PCp9seTVB2n5PYiZuDH9cW/k+LOrhVibVr2UhuNCPIKts4DhsiZvz71vjv2acau/BgBgjYvPVvRvQ441BFHbKQ2P+8LbOU4s+fc5ni95NHXRbIQ9cuye44sy7tfErYb2Wp9KwwxaOLbZ1x7zdY5XchzY7XurbKvncuzS1aLZ6u9NjM/tahvKtj5WPT9tbBLj+GNK3r7x+UCOu3NcW8a16Y3Pozxd8qq/BgBgDYs3QaPZirch6yxRNBnflX2ts9PyRiGakGe6en9MOz6vyVdDzIJFAxkzVrG+LhrDiGjGviz5D2lYsxbX0TZw+5Rjviq1eMwYx7czgjEzVv2ahnNFxEsWsXbv5zTcq9i2dkjL78NDaVj/19bb31VnOuO6QuRXbNy9RH9uAIBRRzb5vA1EHFdfRlgE8/5dKzm5yec9Z6ypi7WDB+W4uanHW65nNWMAgEl1dihmnk5td8zQrt1aBPWx6eZqZ/baN1Fn2bNs31lSnb/hAwDY5n3aFzbR1LfYtob47wkAAGvG2CcxTkrDSwexbg8AgK2sPjp8omxfqzsAANg2vFy2N5TtlvikCAAAm+jSsm0X6K/2J0UAANgMtVGLf6j+elN/Lw0f8wUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAF9j9MaeZmatFLwQAAAABJRU5ErkJggg==>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAaCAYAAADxNd/XAAABdElEQVR4Xu2WzytEURTHv7ESGyWKkj/AkrKdUBYo+QP4G8zCalZjw8ZGfpSlPwALSf4CKUqWsieNjSKKc5zzmjvHnZnr3Reb+6lv793v99R9582Z1wUSiYTLCOnemn/EI+nTUY304qx36qXNeYIU/xcHkP17jN+r/o3xC2OaNG7NHGRv20erLJoZFNfAmzWVtg2sk5atGcgs4hsYgDxg1QbEMSSbskHGq165qOQGgcwhvoFtyP5djtdJOlR/1PEb2CN16D0X8jz/liIayEbkgnRJutP1hlvko6LXTbSZMWXMoxXSksdnheKb/2H1F43vhQuvrelh3iOe27LHZ4UwCNl/zQYQ/9aalj5IYb8NAokdoX3I/t3Gn1D/3Pg/uEJ9fFZJQ04WQmwD2fxbziA+/09bwkWnev/gBoHENMBfmmYNHEH8LWdtf6VvJiGFHzYIJG8DfNZ5hhxh+OzDn/OFhgrgHfJsJ6RdkxVG3gYSiUQikYjiC99fXQ3Dbm3nAAAAAElFTkSuQmCC>

[image25]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAAA0klEQVR4Xu2SPw5BQRDGP1EhcSCJAyChcwmlxAE4gBtoHUKh1ugdAfEnKCiEmcw8kXk7D6GR7C/5mvf78nZ3doHIt4woB8rtKUt1OcrKuC2lrt4lKYeYQlzZihC8Ay7PrVCyFkrRgZSbVijsLvajB8/IW7kKcX0rPJJjtCgNyIBrmpm6wqP9Ai4vKF2Tnjpv1ymSeXnX/dG81vBXrkDcwAqPrGNMIK5oRYg8pPyT9zWElNtWQG7vrZ+NKUfKjrKh7ClXdSXKSb+x484Z8mwikf/nDp2xQiLohmf0AAAAAElFTkSuQmCC>

[image26]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAAAaCAYAAAAUqxq7AAACTklEQVR4Xu2Xv0tWURjHH3VRkxAbImiIlsAtnbSkBhcLbLJoamgJGlSCtgaLaHDQP0CiJRxcXJwMCqMhiyiIwrFNi1I0ooTU58tzTpz7vOe5P3rfrOB84Dvc7/ece597znnPuS9RIpFI/DvcZ22ydgOtuayJ9VFlX1jnXL7f3CKp9RvrqsosTrIesXpYzazjrGnWfNioDH4AYjwmyQ7qYB95x1oMrt+yngXXFoOUnWAIk14JrBR0fKUDR97g1QOee0ibETAxsefD69Sm4gxrgTXDus3qyMbluE7ysGEdOJD90GYddJHMIlZmGV6TPUB48TxOsya0WRXsObECwABJhtGvlxOsbdZDHRRgrWDLDzlFDRgg/6ALrPMkm/CQ03OXtf1qXZ2zJPeYVH5ZrIGw/JA+kglBu1mSDX4p06IE6LzCuqF002VFRVhcJuk7roOKWDVYfghOrw/KQ5+nyjPx+491dCOruv+MkfS7pIPfxBoIyy9ilSr0+0R2436S7I4OCrhL0g/7VyOwBsLyi3hC0u+w8qPkPQTfHcjadVASv5Iu6qAiWxSvEd57bSpi7/fSea3Kr6GFpOGf/v4ZIbnPqA5KggGO1QGvN7jGC2PLCEGbOeXhJI3dr4YpsmcYp1ajBsiDE2WHdU8HJUAd14JrnIi6Nl9vd+DhGwpHvecISZsrgVcDjjss23XWZ9YG66fLDrC+Og8Z2nwn+QRoFMdIjtsHWTsXP2HLrDckNeFLPAQ1vlAewN8U9PUrB38//gvwkziqzUQikUgkEonE32EP6NioAPNsvPEAAAAASUVORK5CYII=>

[image27]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAAAaCAYAAAAUqxq7AAACBElEQVR4Xu2XOywtURSGFxqviE6UlLeQoPKKRoOE7ra30EiUEp0CHQU9IYgoNBoVCSEK3AiJEKXOIx5BBImw/uw9ss8ya+ZMInNOsb/kL+b/186s2TOz9wyRx+Px5A+zrEfWp6MrmxWwrkV2x+qyedoMk+n1hdUnMo161gargVXIqmVNsVbdomwIJiCMTTJZhQxS5JS17hyfsHadY40OyrzBEG56IvCkYOChDCxRk5cGuDFh54dXKU1BO2uNNcMaZZVnxtkxQOZkPTKwIHuTZoockT5BuPAoWlkj0kwK1pywBkAbmQyznyu0J1jzXVroFyYoOFEvq5vMItxptWezku/q9NEmQvNdmlhLZOqWySzw2xkVWYDB56xBoSGbxTXhUsdaVLTAmmfNkdk98XpMm2GRaD1ovgt2rwvhYcyO8FSC9UfbupHlcv0B2kRofhyXlGDcDenFzWSyMRmkjDYRmh/HFplxVcIPJeok+O5AViqDCGpY4wkVxxOF9wjvTJqCsOv7b71i4f+giExhvn7/BPyl8D7gNTrHuGAsGS6oWRHeu/VjmSRTiAYk2LXyZYIA+uh3jies5xL0+8fx8A2FrT6gmkzNP8f7AbY7PLb3rFvWA+vDZmWsZ+shQ80rmU+AXBLcsH3WMZme8Afggh4PhAfwm4KxwZOD3w+Px+PxeDwejycZXziUpIG26eD7AAAAAElFTkSuQmCC>

[image28]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAAAaCAYAAAAUqxq7AAACUklEQVR4Xu2XvWsVQRTFbxLyLSHYSNqks9LYmBixSWME7WxTxEK0FOwsVBDEIvkDgk0IFjY2VgkkKBH8IBgIGkELO6MmSiKigh/3cGfDvPvm7pt9+3immB+cYs+ZYe/ODnN3iRKJRGL/cJe1w/rradNlLayPKttmTbi82VwjqfU7a0plFkdZi6xhVitrkDXDeuAPiiFbgBBLJFmfDprIK9aCd73OWvGuLcap8gVDeOmFwE7BxFUdOPIWL8RxbZQELyZ0f3j92lScYj1kzbJusA5UxnFcJrnZWR04kP3UZg6nSeZc0kGdvCR7gfDgeYyxrmuzKDhzQgWAkyQZVr8oIyRzb+ugINYOtnyfE9SABcpudI51huQQxi6Anrqse290cYZYP1j3dBCJtRCW74OXNE8yDvfHAf+oYkQEmPyGdUXpqstqFRHLQdYWxR2uPlYNlu+D7vVeeZjzWHkm2fljtW5kRc6fGDpZ70g6U5vKQlgLYfm1+EAF5n0ie/AoSXZTByVB13xCcvb1qCyEtRCWX4tlknmHlB8k7yb47kAW8xAxdLDesjZY7SrLY5fCNcJ7rU1F6PleOK9L+VVge2Ngo75/LHD2fCb54KyH8xSuA94x7xoPjCPDB2PuK++X82syTTIQBWjQtcouELoXzq85HdQB6rjoXd9xnk9W72HPwzcUWn3GAMmYSc+rAu0O2/YLSVf5yvrtsl7WN+chwxi0aHwCxHKE9Yd1SwclyF7YM9YaSU04y3xQ43PlATQDzM12Dn4//isXtJFIJBKJRCKR2P/8A7VhqCzF93djAAAAAElFTkSuQmCC>

[image29]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFcAAAAaCAYAAADCDsDeAAACfElEQVR4Xu2Yy6tPURTHvx55lEzERMmNTBSSgZIMmJoof8TtKsnYY2DiWQoTb0qRogwUrgEphjLBQEpehbzzjPVt7d1dZ9n7/H7n6N5zB/tT335nf9c++3d+6+y9zzo/oFAoFApdcUL0SfQn6FQlqvzGSJxaWw2PKZNFP7xpWCi6B73OGy5miX1eiNa4WIoN0P6tsMlLcRN64V3xEL2vkUmysWWuTaaIfpr2PmifO8ZLUfe9tUwQXRVdgg7Au+RpNfAo8BH5a6E/6DzO8rum/Vl0wLTJa+i5s5wfeYX/SO5m0YpwnBvklzc6IpfcOVCfn5ZrwY/E3zfbeEPBO2+8yHrRFuTz0pO35vg9dJCZxlsk2m3aXZJL7nak/ZOo+stFe02b7IT22e988i18tk6uPYn7KtuPjHdONMO0uySX3MtI+4eR9i3voH2mOv8p9AFKWiWX++0V5/mBmgy6RHQ2ozOi09DZxCrlmOiontY3ueTeQto/CPXn+kBgHjR+xPmrRTtM2+ekL+x+az0OFJdPXekz1uSSy9WV8g9B/TgDPYzxRntsRUFaJZdLIkUcbLFol4t1SS65uT33ONI+YX2/1ZvCA9E057VKbu6E69DYE9F0F6tjQLSnoZqQS+4qqN+rWog8hlYCFm5d5HZCMbk83hT61cKlMuzNwES0vFujTC65hL6v0VnX+tXJZ8xK520MytEoF5NEb6CvgTm+YqQUGS/wmnI/krPU1uN8WLPvfONtC15KdSu07+ReEH2A1resa/nfQYql0AJ7PMD98aXoWdBz6IxcYDsJ90VfRBehyVhXDf+TUKsU31H9Xr7NperhQqFQKBQKhUKhUGjOXwDY2KMRaJp8AAAAAElFTkSuQmCC>

[image30]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAAZCAYAAACsGgdbAAABwklEQVR4Xu2VOy8FURSFNyHeglDptDoKicdP0Cg0dAoKjR8gClGJRCJUVDQaf0AUIhJReYVCcxMRhEgQ7+dezjlz9+zZI3SK+ZKVe/ba+6w5mdyZIcrI+L90sq5Yn6wtVmG8HTHKumU9sAZUz6KHXKbFArneM6tf9RLMsOZEjQNgc5PwwCFrVdQHrE1RWyDHOuQpxfNXyOWlgpA2w5Ph1aoOwKvRpueckjmghbWsPKDnIirIDtLejqoD8Oa1yXSzRiiZA6ZZT8oDei7GOKtDeTpc14E0PxzC6rd7751V5b0+1nU08UsQ8qFqfTFg+TlWkV9bfXBM+d66r//EHrnN5cJLu5j2u1hjotZ9yT3l+1BdvJ0OHiBsaFB+2sW0/yrWQPcD8JpZBawbX1tzCWrJDZboBqWHSH+fVSp6wNqXY00ob5Dc3KzyY+DlrcMWxfqOkn0A78ivNwyFQ2I97OesHLDGetSmRD4kAen1kh0Or1WbAutOoq5XHlgi+3X2zQvlw7QkqIdEPem9n7By8HV7U14lJeciGil5sCB968u8v83aJfcuxB/fAt/jM9aJ1wVrSvSxRtal/0VWsehnZGRkZPySLxAzpRzapNadAAAAAElFTkSuQmCC>

[image31]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAaCAYAAAAue6XIAAABwklEQVR4Xu2WTytEURjGH/9ZEAvKAgufQWQjf8IHUCxkslD2SvIRlJIsfAcfwYaNZCU2oiyQBRaUQv6+r3MuM49773tGQ9H86qnxO89953TnzjFAkb/DIAuDZkkpy+/QJlmVrEjqaC2OackcywBeWeTDEtyACf93q+RCcv/R+EqL5JxlFvVI3lSl5IWlhX4cOnCTFzxPSB6q11WTa5Sc+LUoSWxJFlmmocOOWWbRB9fpJ98teSDHWJstQ/p6Dmewy9GdXyP/CPtZtTar6PoAS6YHrrhBnmmA612TV1dDjgnZ7IFkhyWjd0YH8TPHjMP1drNcrXcWIZudh90JGqQcwvX0iIro9c4i5D3GYHSaEDZIietNxrg44q5lOmF0om/hHS8QI3A9PtYy3luEbLYDdidoUFKnC/GeSbo+m1HYHdwgvRQd7BW8gM8TwiJks3r8WZ13tLTHUriEOy3S0Gv1X2YaIZvdR+5Jk8oV3MBtuGdYX+tDb6G9GZYePZP1N8Opj77mczpC5wyxLDSzkluWeVIC+84XDH2jcpZ5sC5ZZvlTDEuOWAaivzmeWf40C5IplgH8+kYjMiwM2iVVLIsU+Q+8AcPof4U5yGDQAAAAAElFTkSuQmCC>

[image32]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAaCAYAAAAaAmTUAAACS0lEQVR4Xu2WvWsVQRTFj5qIJijYmEYNKWzFzqigGCEKYiOWkmAh2GgjMf4JYmUh6P8giJBGUkUb0wgigqhgISJR4xd+a0i8J3c2b97JvJ3Vt7Hx/eDw3px75w47Mzs7QIf/h2E12mSnGn9Lv+ma6Yppo8RSnDZdULMGFtT4Ey7DC4yE9jbTa9P3pYzlbDW9VDNiFl6zkPIMzfHHUWzA9D5qV2I1vNBtDQTmTPNqBthvnZrCTdM9eO5uiZEu0yM1A19MR9Usg4NwhloxBM85KP4e0w/xUrDv2vD7U2LkjOmImoHtSK9okhfIJxcrd138X6j2rnwMv3wQ1uFKxMxIW2GfHjWV/fDEKfGVTfC8D+LTWy+essN0LvzfC+9zpxFeJDeZjF9SU+HMMjG350/A8+5H3obg5bhhWhO12Uf73ZW2MokK2zlVOMUTeB6P4IIDwcuhOReDV6wWa+a+UfxMaJ0mNqP6w6TyTia8FMX7EhPXexUHWjCOzFhceiZ804BwHJ6nx/Zo8MvgV3xMTeMhvG/Vk4o1snmpGVda5Qwi7cdMYPnJRXrhfblqehikuIr8WIvFypKew+PdGkDjhCujLM6PMON893LcMn1VMwULPlDTeAM/7cpgX34MU5yFx1dpIHAY5Q8bwzxetSpR3J+m4e8Q/+9qykjDvOJUKuC2+mR6F8QZPdSU0eCtGi3gONwJK8p502c1a2YLqq9g23Cg1EteF7w1H1NzpeDef6pmTfQhf2+rHd6bTqlZA/9seymjarTJPjU6dOhQD78BqRyWmBpJICMAAAAASUVORK5CYII=>

[image33]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGcAAAAaCAYAAACq/ULmAAAEG0lEQVR4Xu2ZWahOURTHl3kKkRQZkgwRKcn0IEMoT4ZQRIqQSIkMT16QoSTCA8+GQuGFl0tCooQyU+Z5nuf1v3uve/e3vr3PPve63/2+uudXq3P2f+19zv7OPnuvtc9HlJGRURqM1UIdpwNbfS3WBF3ZdrFtZ2ulfD4WsK3UYg3TgK2XFkucv1r4H7aSueAsW+7C9oLtW0WNfDqzPdGiwysy1xTT3KNc/81cdznvKNy+0Lxk+03h+5+i3P4/dXyN2f445WqB6YcL40Y+flH4JmjXVIuKI2yXyNQdqnygIdt1LSrwwvgeTm2wlO00mfuvUj4BA+jjLNsWLVYF3BRvcIhRZOqMVvowtu9K84G2eItw/KF8YDHbBC0qplLxBue1PYZmTz+2TVq0YDn2tUnFI4o3lpl1UOk/KV2seW+PGBhcBzPF5Zkq+5hE8X4WCrnvNXve1/GBfZQcm9FmjBZjjCDTsEzpmjZk6mHtd4HWTGma/mzL7PlwMm2wRLikeegTKVxvOZm1HglMI+UTkE0eYJtpy2VsXyq8YeqxHbXnLcj04WOlu5xQv4QbbBe0GANvPi4cixn4Qah32dFaWi3GITJTW0Ab3e6cKvvwDU5Hq3WzZZnhMypqmIcLbY0t77FlgGMsA1zCNtApI/aiHa4r4DkmsZry+x7F96B83CJTDymzMNJqMXSdDVaT2YRrptkj+QYH5Z1K62N12WOcsWUXlDcrLYTEG2E8mfYym3qzrat0e5lO+X1IpD2lHxxfvTkezYfEGxf3es9dRwJ6cMbZcmtHE6DvtudIhXU/UT6htBC6LXD7v5/McpfEYPJfJ4hkEV+1QzGFTD2dZs+2ehIDyMQDjQTWHvaYBj04e23ZF2Pc3yVxTuhky3g5Y2D2Hdcis4PMNebaY4xBlK5eDmgQaxSqM4T8ugumvs7MgARWzCqdHITQg4O9B8oSb1yg33XK8jLgfjgi9U0Dll78Th/yXNJsJaZR/FnlIZ0N8YCM3/d2SgaXRJJfAitiVxr0D5RAL7FLkH5hDwbmkVnzq8MHLTjcJ3OftdrhAduNpGcRBI2uaJHMWh3LQtAWm0sfyHLgd7MaFwmsaVlIpr6b+a23mgs+N91xyj3J1LlIZpYeY9tI/ljlgn0J2jXXDktbMv5YpguuUm6mWyXk+9d5Mms1zhHEYvjeXCxj2Ae8sYa9BIK3D50JhfjM9pjtIZkN62HHhzQXSwv6Apvv+EA7x6dNkgbNJ7a3ZPqPc7wEPuBLA+4VegYFYwWl72CxwIPBnkwjn6QKjSy/RQE39gX9UgH98y2tsmEtNCfZtmmxtkDsuK3FEkLikpt4TLaaXpJrGrwAoa/VtQYCLLKiUgYDgb8u8DlpkfIViqIPjDBbC3Wc7mxNtJiRkZGRkVFK/AMnBCTHoFJhywAAAABJRU5ErkJggg==>

[image34]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAAf0lEQVR4XmNgGAUjDZxBF6AmOAnE/5EwyYAViEvRBfGAIgYyLeJgoJNFPAx0soiXYShbZIIF2wPxJCziIIwNEGWRHxYcDsQLsIiDMDZAlEXYAE2CDhsYtBZ1MUAsEkWXIASItegXEL8A4idA/BhKvwbixciK8AFiLRoFo2CkAwAtOCUn2On9ZQAAAABJRU5ErkJggg==>

[image35]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAAYUlEQVR4XmNgGAUjDZxBF6AmOAnE/5EwzUERw6hFZILBZZEwEJsQidWhetABURbJA7EfkdgWqgcdEGURNcDws6iLAWKRKLoEtcAvIH4BxE+A+DGUfg3Ei5EVjYJRMAooBwCZZh7vPiWQwAAAAABJRU5ErkJggg==>

[image36]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAApElEQVR4XmNgGJpAHl0AHZwA4qtA7AbEj4H4AIosFMwF4r9oYv+BuBRNDKvgDKg4HEhDBTyRBYEgByoOBwlQAVNkQSCIgIqrwgQqoQL6MAEoCIaKw22qggqgKwyCioejCxjDBKAgDCoON8AOKmAJE4CCWKg4yLNgwA4VAJmADGBOQgEggUloYtug4igAm24QH+R+DLCcARKNIBqkqABVehRQAwAA4fYow14SzbMAAAAASUVORK5CYII=>

[image37]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACoAAAAZCAYAAABHLbxYAAABJElEQVR4Xu2UsUoDQRRFbwohRSIYsM4H2FoGUtjbpvErhNRpUgTBxsK0QrpU/oAfoFiltUsMCEHRNKKBxPeYFYa3j9mZJbvNzoHLMmce7IXZHSASqRbPUnhwTfmlvFM6Ym+vPFJ2VkL4ogyt9TdlZK29OKD0pXRwibCiZ0jPtxSXSR3FFuXj1ubZXUjpooFii/LsRkoYP5PSRRPFF11LCeP5W/WmjKIfUiLjpzxV0qXcKJ6jkafop5QwfivlP+dKepQ7xXM08hT9kRLGv0jpooyj1+bZjaV0se+iA7G+RXq+lji+w70JLXoF85JjuUHcw+xNhWd3Yq2foN8ETnyL8sX9RnmlLJLnijKxZo4oS8qh5Zg2TNkHyhxmJhjfopFIJFJl/gB3lFRfwAdXnwAAAABJRU5ErkJggg==>

[image38]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACoAAAAZCAYAAABHLbxYAAABQ0lEQVR4Xu2UPS8FQRiFj4SSxNXobqnQCUFCpfcL9H6DSqPQaClUWjcSf0AtUUiITiMShYKgEd/ekxkxOTNrN7mzlXmSk9x59p077+zsLlAo/A82LW+Wd8ueXKtjy/JqubMsyLWsPFqm/O8xy5dPEzh3Ixg/w206O7OWW8tw4GbgGj0NXIolxBvqJFwWuHv+8YX4JneVx52qoVtRmYOeZURck0Z5nc+1Qn+usg3m4RbjBv6CNU8q4Tyf1dbhQp8qE7DuXiVqToNv63TDTPg5KQ4sHyorYDMPKlGz0a5luWEW/RxlFemFq2BDLyrh/KXKXMxZrsRVHp+n6ojpdlTmYNxyphJxE+sy3kZcM+DdkPi+GcTvndEcB3WH3u0HjtBNBuMTpL8EfbOLuMGfrAV1o5YbxN/bLlztkeUarqZQKBQKLfANoK9eKcaG78cAAAAASUVORK5CYII=>

[image39]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAA/0lEQVR4Xu2UMWoCYRCFn0UuIIKp7TyGN7DxDiaiqNh5gRReQyzSBISU3kFQsBELRRQtbLUwzjCr7IzzaxbSBPaDx7Lf/5hZ2GWBlP9Ih/Jm5RNKlBnlh9I3Z4oB5QQpct718UPalHPsvgqZ8ZSki7hfdNyHcXckWVSG//RH+F6RZNEI/sAFfK9IsugAf+AUvldwoWZlAO56A8fwvYILdSsDrOEPnMD3Ci40rAwQekdz+F7BhaaVAbrwB/76q2tZGVGh5I3jftZxQ+MUOUipZw+IDPyXv4F8zldeIZ2XmLvxSdlRVpRldN1CfktxviD/Qsse0v+GLCno45SUlL/gAnq9R8qMXCmBAAAAAElFTkSuQmCC>

[image40]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAZCAYAAAC2JufVAAABhUlEQVR4Xu2VTysFYRTGj7BRlBAW2FlLyZ+sfARl5QMIERIpOxsLKwsbpawkKd/Bwk6RrBUb2bD1/zzeM/eeee573ZmFhZpfPd15f++ZtzPz3pkRKSj4e1Y1syxrsK1507xrDmnOc6L50txqmmiugiPNq4QTkLn09K+8aAbtuE3Ka3gazfXauN7G3aWKGuRpaljzqGl2bkjCGpfOnWse3BjsSGXzVcnTFLYN9Tfk+W7heM+NwZj5TORpCuB/0kLON5Vs1WZ5+oc+85Pko+RtihmVsAaaBQM2XilVBDrMr5OPgsJ5ljnA+Z9uPGFu0TnQan6ffBQULrDMyKnmg1y/hDWXyLeb3yIfJXZVWZjRPLNU6iSsuUG+x/w0+Sixq6rFiOaOHNbxx9WevkzvKhQuszSmNJ3kujRX5IBvClt67cZgTdI1VUn2GS82JtkGv1CDc5wLVzduzoPxLrkUeHyfJLx17+0Xb2p8ejxnEr6NCXhyuJkk/B9K7syxhHUP0tMFBQUF/4dvEG5tSArn+OwAAAAASUVORK5CYII=>