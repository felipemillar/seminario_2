# **Desarrollo de Indicadores Personalizados y Arquitectura Gráfica Interactiva en MetaTrader 5**

## **1\. Anatomía Avanzada de un Indicador MQL5 y el Ciclo de Ejecución de OnCalculate**

La arquitectura de ejecución de un indicador personalizado en MetaTrader 5 (MT5) difiere de otros programas de la plataforma, como los Scripts o los Expert Advisors (EAs). Los indicadores se ejecutan de manera asíncrona dentro del hilo principal de la interfaz gráfica del terminal para garantizar la sincronización directa del renderizado visual de los gráficos. La puerta de entrada para el procesamiento de ticks e historial en estos programas es el controlador de eventos OnCalculate().  
Existen dos firmas válidas para la función OnCalculate(), y solo una de ellas puede implementarse en un mismo archivo de código fuente :

### **Firma completa (Basada en series temporales del gráfico)**

Esta firma proporciona acceso directo a todos los datos de precios de la barra del gráfico actual, correspondientes al símbolo y marco temporal en el que se ejecuta el indicador.2

Fragmento de código  
int OnCalculate(  
   const int        rates\_total,       // Número total de barras en el gráfico  
   const int        prev\_calculated,   // Barras procesadas en la llamada anterior  
   const datetime&  time,            // Hora de apertura de cada barra  
   const double&    open,            // Precios de apertura  
   const double&    high,            // Precios máximos  
   const double&    low,             // Precios mínimos  
   const double&    close,           // Precios de cierre  
   const long&      tick\_volume,     // Volumen de ticks (transacciones)  
   const long&      volume,          // Volumen real de transacciones (intercambio)  
   const int&       spread           // Spreads históricos por barra  
);

### **Firma reducida (Basada en un array de datos de entrada o indicadores encadenados)**

Esta firma permite procesar una única serie de datos de entrada.2 Se utiliza cuando el indicador se configura para procesar los datos resultantes de *otro* indicador en lugar de los precios directos del gráfico.2

Fragmento de código  
int OnCalculate(  
   const int        rates\_total,       // Tamaño del array de datos de entrada  
   const int        prev\_calculated,   // Elementos procesados en la llamada anterior  
   const int        begin,             // Índice donde comienzan los datos significativos  
   const double&    price            // Array de datos de entrada (precio o buffer externo)  
);

### **Análisis de parámetros y optimización incremental**

La optimización de recursos y la CPU depende de la correcta interpretación de rates\_total y prev\_calculated.3 El parámetro rates\_total indica la cantidad total de barras disponibles en el gráfico.2 Por su parte, prev\_calculated almacena el valor de retorno devuelto por la última ejecución exitosa de OnCalculate().2  
Cuando el indicador se carga por primera vez en el gráfico, o cuando ocurren cambios estructurales en el historial (por ejemplo, recarga del gráfico, sincronización de datos con el servidor o descarga de un historial más profundo), el terminal restablece automáticamente el valor de prev\_calculated a ![][image1].2 Esto obliga al indicador a realizar un cálculo completo de todo el historial.  
El parámetro begin de la firma reducida indica el índice a partir del cual el array price contiene datos válidos para el cálculo.2 Por ejemplo, si el indicador actual está encadenado a una media móvil simple (SMA) con un período de 14, las primeras 13 barras no dispondrán de un valor matemático real (EMPTY\_VALUE), por lo que el terminal establecerá begin \= 13\.2 El algoritmo debe omitir estas barras para evitar cálculos sobre datos inexistentes.2  
En condiciones de funcionamiento normal de mercado, la llegada de un nuevo tick activa OnCalculate() con un valor de prev\_calculated igual a rates\_total de la llamada inmediatamente anterior o, en el caso de la formación de una nueva barra, igual a ![][image2].6 El patrón algorítmico correcto para el cálculo incremental evita recalcular innecesariamente las barras históricas estáticas 3:

Fragmento de código  
int start;  
if(prev\_calculated \== 0\)  
{  
   // Inicialización completa del cálculo histórico  
   start \= PeriodoCalculo \+ begin;   
}  
else  
{  
   // Recalcular la barra actual en desarrollo (índice final) y barras adyacentes si es necesario  
   start \= prev\_calculated \- 1;   
}

for(int i \= start; i \< rates\_total &&\!IsStopped(); i++)  
{  
   // Algoritmo matemático del indicador  
}  
return(rates\_total); // El retorno define el próximo prev\_calculated

El uso de prev\_calculated \- 1 en lugar de prev\_calculated es crítico.5 Dado que la barra actual (índice ![][image2]) está en constante formación y sus precios cambian con cada tick, el cálculo de dicha barra no es definitivo.5 Al restar ![][image3], se garantiza el recálculo constante de la barra activa y se asientan definitivamente los valores de las barras cerradas previas.5

## **2\. Memoria y Gestión de Indicator Buffers**

Los buffers de indicador son arrays dinámicos de tipo double cuyo ciclo de vida y dimensionamiento en memoria física son gestionados directamente por el subsistema de ejecución de MetaTrader 5\.8 Está estrictamente prohibido intentar redimensionar un buffer de indicador mediante la función ArrayResize(); cualquier intento de alterar el tamaño de forma manual resultará en un fallo de ejecución o comportamiento indefinido.9

### **Configuración mediante directivas de compilación**

La reserva e inicialización de buffers se gestiona a nivel del preprocesador de MQL5 utilizando propiedades específicas 10:

* \#property indicator\_buffers: Define la cantidad *total* de arrays dinámicos que el terminal mantendrá en memoria para este indicador.10 Esto incluye buffers de datos, de colores y de cálculos internos.11  
* \#property indicator\_plots: Define cuántas series de datos visuales reales se dibujarán en el gráfico.10

Un indicador puede tener, por ejemplo, un solo plot (indicator\_plots 1\) pero requerir múltiples buffers (indicator\_buffers 5), como en el caso de estilos complejos multicolores o figuras que necesitan buffers para almacenar cálculos de tendencias intermedias.13

### **Vinculación y modos de buffer**

En la función de inicialización OnInit(), los arrays dinámicos declarados globalmente deben ser asociados formalmente al motor gráfico de MT5 utilizando SetIndexBuffer().11 Esta función determina el comportamiento lógico del buffer mediante la de la enumeración ENUM\_INDEXBUFFER\_TYPE 11:

1. **INDICATOR\_DATA**: El buffer contiene los valores numéricos directos que se utilizarán para trazar los gráficos en pantalla.11 Estos valores se exponen directamente en la ventana "Data Window" (Ventana de Datos) del terminal.12  
2. **INDICATOR\_COLOR\_INDEX**: Almacena números enteros (castados implícitamente a double) que actúan como índices para mapear un esquema de color específico definido en el plot.11 No se dibuja de forma independiente, sino que complementa a un buffer de tipo INDICATOR\_DATA.11  
3. **INDICATOR\_CALCULATIONS**: Se utiliza como un área de memoria temporal para cálculos matemáticos auxiliares (por ejemplo, almacenar una media móvil intermedia).11 Estos buffers no se renderizan visualmente ni se exponen en la Ventana de Datos, ahorrando recursos de procesamiento gráfico.12

### **Control de dibujo y valores vacíos**

El valor EMPTY\_VALUE (equivalente a DBL\_MAX) se utiliza para indicar la ausencia de datos en una barra específica.16 Cuando el motor de renderizado de MT5 encuentra EMPTY\_VALUE en un buffer de tipo INDICATOR\_DATA, suspende el trazo gráfico en esa coordenada temporal.16  
La manipulación avanzada de las propiedades de los gráficos se realiza a través de las funciones de la familia PlotIndexSet... 4:

* **PlotIndexSetInteger(plot\_index, property\_id, value)**: Configura enteros como el grosor de línea (PLOT\_LINE\_WIDTH), estilo de línea (PLOT\_LINE\_STYLE) o el tipo de dibujo (PLOT\_DRAW\_TYPE).10  
* **PlotIndexSetDouble(plot\_index, PLOT\_EMPTY\_VALUE, empty\_value)**: Define qué valor específico del buffer debe interpretarse como "vacío" para que el renderizador ignore la barra en el dibujo.4  
* **PlotIndexSetString(plot\_index, PLOT\_LABEL, label\_text)**: Asigna la etiqueta descriptiva que se visualizará en la Ventana de Datos y en los mensajes emergentes interactivos del cursor.10

## **3\. Catálogo Exhaustivo de Estilos de Dibujo (ENUM\_PLOT\_TYPE)**

MQL5 amplía las capacidades de dibujo con respecto a su predecesor MQL4, permitiendo combinar estilos que varían según los requisitos de buffers lógicos de datos y buffers de índices de color.11

### **Especificaciones técnicas por estilo de dibujo**

La siguiente tabla resume los requisitos de buffers y la descripción de cada uno de los 18 estilos de dibujo disponibles en MQL5 11:

| Identificador del Estilo | Buffers de Datos (INDICATOR\_DATA) | Buffers de Color (INDICATOR\_COLOR\_INDEX) | Descripción Técnica y Aplicación Típica |
| :---- | :---- | :---- | :---- |
| **DRAW\_NONE** | 1 | 0 | No dibuja nada. Los datos existen solo para ser consultados por EAs o la Ventana de Datos.11 |
| **DRAW\_LINE** | 1 | 0 | Línea estándar continua entre barras continuas que contienen datos válidos.11 |
| **DRAW\_SECTION** | 1 | 0 | Dibuja líneas continuas solo entre barras no vacías consecutivas, dejando huecos en barras vacías.11 |
| **DRAW\_HISTOGRAM** | 1 | 0 | Barras verticales desde la línea cero (0.0) hasta el valor especificado en el buffer.11 |
| **DRAW\_HISTOGRAM2** | 2 | 0 | Barras de histograma dibujadas entre los valores del primer y del segundo buffer de datos.11 |
| **DRAW\_ARROW** | 1 | 0 | Renderiza caracteres de la fuente Wingdings u otros símbolos gráficos en los valores indicados.11 |
| **DRAW\_ZIGZAG** | 2 | 0 | Dibuja segmentos de línea continuos uniendo alternadamente valores de dos buffers diferentes.11 |
| **DRAW\_FILLING** | 2 | 0 | Relleno sólido de color entre los valores de dos buffers independientes de datos.11 |
| **DRAW\_BARS** | 4 | 0 | Dibuja barras de precios occidentales (Open, High, Low, Close) completas.11 |
| **DRAW\_CANDLES** | 4 | 0 | Dibuja velas japonesas estándar requiriendo la secuencia: Open, High, Low, Close.11 |
| **DRAW\_COLOR\_LINE** | 1 | 1 | Línea continua que cambia dinámicamente de color barra a barra según un índice de color.11 |
| **DRAW\_COLOR\_SECTION** | 1 | 1 | Segmentos independientes donde cada sección puede tener un color predefinido.11 |
| **DRAW\_COLOR\_HISTOGRAM** | 1 | 1 | Histograma de una línea con coloración individual por cada barra vertical.11 |
| **DRAW\_COLOR\_HISTOGRAM2** | 2 | 1 | Histograma entre dos líneas con control de coloración individual por cada barra.11 |
| **DRAW\_COLOR\_ARROW** | 1 | 1 | Símbolos (flechas) cuyos colores se asignan dinámicamente según un índice de color.11 |
| **DRAW\_COLOR\_ZIGZAG** | 2 | 1 | Zigzag clásico con color configurable para cada segmento independiente.11 |
| **DRAW\_COLOR\_BARS** | 4 | 1 | Barras tradicionales completas con coloración individual controlada.11 |
| **DRAW\_COLOR\_CANDLES** | 4 | 1 | Velas japonesas detalladas con cambio de color de cuerpo y bordes dinámico.11 |

### **Comportamiento cromático y mecánicas específicas**

* **DRAW\_NONE**: Útil para indicadores que calculan datos que solo deben ser consumidos por un EA mediante CopyBuffer(), reduciendo la carga del hilo de renderizado gráfico de la CPU.11  
* **DRAW\_LINE**: Une valores contiguos del buffer. Si un valor es EMPTY\_VALUE, la línea se rompe temporalmente hasta encontrar un nuevo valor numérico válido.12  
* **DRAW\_SECTION**: Dibuja líneas continuas solo entre barras consecutivas que no contengan valores vacíos, ideal para trazar canales dinámicos y niveles de soporte y resistencia móviles.12  
* **DRAW\_HISTOGRAM**: Proyecta barras verticales que parten de la línea horizontal de cero. Ideal para visualizar volúmenes o valores de osciladores tradicionales como el MACD clásico.12  
* **DRAW\_HISTOGRAM2**: Renderiza un área sombreada verticalmente que abarca el espacio comprendido entre los valores numéricos de dos buffers de datos.12  
* **DRAW\_ARROW**: Pinta un símbolo estático en una barra específica. El símbolo se define asignando el código Wingdings a la propiedad PLOT\_ARROW\_CODE usando la función PlotIndexSetInteger().21  
* **DRAW\_ZIGZAG**: Este estilo es particular debido a que permite dibujar segmentos verticales y diagonales sobre una misma barra.16 Utiliza dos buffers de datos para definir los extremos de cada sección.13  
* **DRAW\_FILLING**: No cuenta con una versión multicolor directa (DRAW\_COLOR\_FILLING).12 Para su configuración, se asignan dos colores principales utilizando la función PlotIndexSetInteger con el modificador de color indexado 19:  
  ![][image4]  
  ![][image5]  
  Esto permite crear de forma nativa sombreados dinámicos de cruces de medias móviles (nubes Ichimoku o canales de volatilidad) sin necesidad de renderizadores personalizados pesados.19  
* **DRAW\_BARS**: Renderiza una barra con cuatro puntos clave por elemento: apertura (izquierda), máximo (arriba), mínimo (abajo) y cierre (derecha).11  
* **DRAW\_CANDLES**: Permite configurar hasta un máximo de tres colores fijos a través del preprocesador.17 El primer color define los contornos y las mechas, el segundo el cuerpo de las velas alcistas (bullish) y el tercero el cuerpo de las velas bajistas (bearish).17  
* **Estilos multicolores (DRAW\_COLOR\_...)**: Requieren un buffer dinámico auxiliar adicional configurado bajo el tipo INDICATOR\_COLOR\_INDEX.11 Este buffer almacena números enteros que hacen referencia de manera secuencial a un índice dentro de un array especial de colores predefinidos del indicador (con un límite máximo de 64 colores simultáneos).12

## **4\. Control del Entorno Gráfico: Multi-ventana vs Overlay**

La ubicación física donde un indicador renderiza sus componentes se define de manera estática mediante una directiva de preprocesamiento 10:

Fragmento de código  
\#property indicator\_chart\_window    // Se dibuja superpuesto en el gráfico de precios principal

o

Fragmento de código  
\#property indicator\_separate\_window // Se dibuja en una subventana independiente debajo del precio

Si ambas directivas se especifican simultáneamente, el compilador priorizará la última declarada. No es posible alternar esta propiedad de manera dinámica en tiempo de ejecución a través de funciones del terminal.10

### **Control dimensional y límites de escala en subventanas**

Cuando un indicador se ejecuta dentro de su propia ventana separada (indicator\_separate\_window), el desarrollador adquiere control preciso sobre la escala vertical y las líneas de nivel horizontal mediante funciones programáticas o directivas 10:

* **Límites Fijos de Escala**: Algunos osciladores normalizados requieren rangos definidos de forma matemática, como el rango de ![][image1] a ![][image6] en el RSI o de ![][image1] a ![][image7] en el Porcentaje de Rango de Williams (WPR).23 Para forzar estos límites y evitar el autoescalado dinámico por defecto del terminal, se utilizan las siguientes propiedades 10:  
  * INDICATOR\_MINIMUM: Establece el límite inferior de la escala vertical del subgráfico.10  
  * INDICATOR\_MAXIMUM: Establece el límite superior de la escala vertical del subgráfico.10

### **Gestión dinámica de niveles horizontales**

Los niveles horizontales estáticos (como los umbrales de sobrecompra y sobreventa en osciladores) pueden definirse inicialmente a través de \#property indicator\_levelN (donde ![][image8] representa el índice que empieza en ![][image3]).10 Sin embargo, para permitir la parametrización dinámica y que los niveles se ajusten según la volatilidad del mercado en tiempo real, se debe utilizar la función IndicatorSetDouble().23  
Es de vital importancia destacar una discrepancia crítica entre las directivas del compilador y las funciones en tiempo de ejecución: **las directivas de preprocesador indexan los niveles comenzando desde ![][image3], mientras que las funciones programáticas de MQL5 los indexan con base cero (![][image1])**.10

Fragmento de código  
// Definición programática dinámica de un nivel en el índice 0 (Nivel 1\)  
IndicatorSetInteger(INDICATOR\_LEVELS, 2);                      // Define el número total de niveles   
IndicatorSetDouble(INDICATOR\_LEVELVALUE, 0, \-20.0);            // Define el valor del primer nivel   
IndicatorSetDouble(INDICATOR\_LEVELVALUE, 1, \-80.0);            // Define el valor del segundo nivel   
IndicatorSetInteger(INDICATOR\_LEVELCOLOR, 0, clrRed);          // Modifica el color del primer nivel   
IndicatorSetInteger(INDICATOR\_LEVELSTYLE, 0, STYLE\_DOT);       // Estilo de línea punteada   
IndicatorSetInteger(INDICATOR\_LEVELWIDTH, 0, 1);               // Grosor de línea de 1 píxel   
IndicatorSetString(INDICATOR\_LEVELTEXT, 0, "Sobrecompra");     // Etiqueta de texto personalizada \[10, 25\]

### **Indicadores híbridos (Dibujo simultáneo)**

Aunque la arquitectura nativa restringe que un indicador pertenezca únicamente a una de las dos ventanas, es común el diseño de indicadores híbridos. Estos son programas que calculan un oscilador principal en una subventana independiente pero, al mismo tiempo, necesitan proyectar líneas de tendencia o etiquetas directamente en el gráfico principal de precios. Para lograr esto, el indicador se declara con la directiva indicator\_separate\_window 10, y todos los dibujos deseados sobre el precio se crean e inyectan dinámicamente mediante la manipulación de objetos gráficos (OBJ\_TREND, OBJ\_HLINE, etc.) apuntando explícitamente a la ventana con índice ![][image1] (el gráfico principal).26

## **5\. Consumo Seguro de Recursos: Acceso a Indicadores y Caching de Handles**

La reutilización de lógica de indicadores existentes se gestiona mediante el sistema de manejadores (handles) de MetaTrader 5\.20 La plataforma distingue conceptualmente entre indicadores técnicos nativos optimizados e indicadores personalizados (iCustom).28

### **Invocación estándar y alternativa dinámica**

La forma más común y eficiente de obtener el manejador de un indicador nativo es a través de sus funciones específicas 29:

Fragmento de código  
int handle\_ma \= iMA(\_Symbol, \_Period, 21, 0, MODE\_EMA, PRICE\_CLOSE); // \[29, 30\]

Como alternativa avanzada para sistemas algorítmicos dinámicos que cambian sus parámetros o tipos de indicador bajo demanda en tiempo de ejecución, se dispone de IndicatorCreate().31 Esta función requiere poblar un array de estructuras MqlParam que encapsulan el tipo de datos y los valores correspondientes 32:

Fragmento de código  
MqlParam params;  
params.type          \= TYPE\_INT;  
params.integer\_value \= 21;          // Período de la media \[30, 33\]  
params.type          \= TYPE\_INT;  
params.integer\_value \= 0;           // Shift horizontal \[30, 33\]  
params.type          \= TYPE\_INT;  
params.integer\_value \= MODE\_EMA;    // Tipo de suavizado \[30, 33\]  
params.type          \= TYPE\_INT;  
params.integer\_value \= PRICE\_CLOSE; // Precio aplicado \[30, 33\]

int handle\_dynamic \= IndicatorCreate(\_Symbol, \_Period, IND\_MA, 4, params); // \[30, 32\]

Para indicadores personalizados de terceros o propios compilados en disco, se utiliza iCustom(), donde la ruta al archivo .ex5 y los parámetros requeridos deben coincidir de forma estricta en tipo y orden jerárquico 28:

Fragmento de código  
int handle\_custom \= iCustom(\_Symbol, \_Period, "Directorio\\\\MiIndicadorCustom", param\_1, param\_2); // 

### **Mecánica del Caché Interno de MT5 y Conteo de Referencias**

MetaTrader 5 gestiona un almacén global optimizado para evitar la duplicación de cálculos idénticos en memoria.29 Cuando un script, EA o indicador solicita un manejador (vía iCustom o funciones nativas), el terminal verifica los siguientes criterios en el caché para determinar la identidad del recurso 34:

1. Coincidencia exacta del símbolo financiero y el período temporal (Timeframe).34  
2. Coincidencia binaria de todos los parámetros de entrada y su secuencia.34  
3. Para indicadores personalizados (iCustom), coincidencia exacta de la ruta física del archivo .ex5 en el disco local.34  
4. La ventana del gráfico heredada en la que opera el programa solicitante.34

Si se localiza una coincidencia en el caché, **el terminal no instancia un nuevo indicador ni asigna nuevos recursos de cálculo**.29 En su lugar, simplemente devuelve el manejador existente e incrementa un contador de referencias interno en ![][image9].29 Al solicitar múltiples manejadores idénticos dentro del mismo programa, el contador de referencias aumentará solo una vez.29  
Cuando un programa de MQL5 finaliza su ejecución de manera ordenada o se desvinccula del gráfico, el terminal decrementa de manera automática el contador de referencias de todos los manejadores creados por ese programa en ![][image10].34 Si el contador de referencias para un indicador específico llega a cero (![][image1]), el terminal procede a descargar por completo los buffers de cálculo de la memoria RAM con un breve retraso controlado.34  
El desarrollador puede forzar la liberación anticipada de memoria utilizando IndicatorRelease() 31:

Fragmento de código  
if(handle\_ma\!= INVALID\_HANDLE)  
{  
   if(IndicatorRelease(handle\_ma)) // \[31, 36\]  
   {  
      handle\_ma \= INVALID\_HANDLE;  // Evita el uso posterior de un manejador huérfano \[35\]  
   }  
}

Es importante señalar que **durante la optimización o backtesting en el Strategy Tester (Probador de Estrategias), la función IndicatorRelease() se ignora intencionalmente** para priorizar la velocidad de cálculo del pipeline de ticks simulados.35

### **El patrón de extracción de datos**

Para extraer los datos calculados de forma segura, se debe utilizar CopyBuffer().20 Sin embargo, la copia directa solo debe ejecutarse tras comprobar mediante BarsCalculated() que los datos requeridos ya han sido procesados y están disponibles en el buffer interno del terminal 30:

Fragmento de código  
// Comprobar que el indicador haya calculado al menos las barras necesarias  
int calculados \= BarsCalculated(handle\_ma); // \[30, 31\]  
if(calculados \< rates\_total)  
{  
   return(0); // Sincronización incompleta, abortar este tick y reintentar  
}

double temp\_array;  
ArraySetAsSeries(temp\_array, true); // Indexación estilo serie (0 representa el tick más reciente) \[8, 20, 38\]

int copiado \= CopyBuffer(handle\_ma, 0, 0, 3, temp\_array); // Copiar las últimas 3 barras \[20, 31, 39\]  
if(copiado \<= 0\)  
{  
   int error \= GetLastError();  
   Print("Fallo al copiar los datos. Error: ", error); //   
   return(0);  
}

## **6\. El Lienzo del Gráfico: Manipulación de Objetos Gráficos**

Los objetos gráficos se integran directamente sobre el lienzo visual del gráfico.21 Se dividen categóricamente en dos grupos bien definidos por su sistema de coordenadas de referencia 21:

### **Objetos basados en coordenadas de mercado (Tiempo y Precio)**

Son objetos de análisis técnico tradicional (OBJ\_TREND, OBJ\_HLINE, OBJ\_VLINE, OBJ\_RECTANGLE, OBJ\_TRIANGLE, OBJ\_ELLIPSE, OBJ\_FIBO, OBJ\_CHANNEL).21 Su posición se altera al desplazar el gráfico u ocurrir cambios en la escala vertical.21 Requieren coordenadas explícitas de fecha/hora (datetime) y precio (double) para sus puntos de anclaje (parámetros modificadores de punto).21

### **Objetos basados en coordenadas de pantalla (Píxeles y Esquinas)**

Diseñados específicamente para construir paneles de control e interfaces interactivas (OBJ\_TEXT, OBJ\_LABEL, OBJ\_BUTTON, OBJ\_BITMAP, OBJ\_BITMAP\_LABEL, OBJ\_EDIT, OBJ\_RECTANGLE\_LABEL).40 Su ubicación física se mantiene fija en el monitor sin importar el movimiento del fondo del precio del gráfico.21

### **Especificaciones técnicas de manipulación de objetos gráficos**

La siguiente tabla describe la mecánica operativa de los quince principales objetos gráficos de la plataforma 21:

| Tipo de Objeto (ENUM\_OBJECT) | Sistema de Coordenadas Principal | Métodos de Anclaje Compatibles (OBJPROP\_CORNER / OBJPROP\_ANCHOR) | Propiedades Clave de Configuración | Uso Arquitectural Típico |
| :---- | :---- | :---- | :---- | :---- |
| **OBJ\_TREND** | Tiempo y Precio | No aplica (puntos de anclaje libres) | OBJPROP\_RAY\_RIGHT, OBJPROP\_COLOR, OBJPROP\_STYLE 21 | Directrices de tendencia, soportes diagonales. |
| **OBJ\_HLINE** | Precio únicamente | No aplica (horizontal fija en eje Y) | OBJPROP\_COLOR, OBJPROP\_STYLE, OBJPROP\_WIDTH 21 | Niveles de ruptura de precio, zonas estáticas clave. |
| **OBJ\_VLINE** | Tiempo únicamente | No aplica (vertical fija en eje X) | OBJPROP\_COLOR, OBJPROP\_STYLE, OBJPROP\_WIDTH 21 | Separadores de sesiones, eventos macroeconómicos. |
| **OBJ\_RECTANGLE** | Tiempo y Precio | No aplica (dos puntos libres) | OBJPROP\_FILL, OBJPROP\_COLOR, OBJPROP\_BACK 21 | Bloques de ordenes (order blocks), zonas de oferta/demanda. |
| **OBJ\_TRIANGLE** | Tiempo y Precio | No aplica (tres puntos libres) | OBJPROP\_FILL, OBJPROP\_COLOR, OBJPROP\_WIDTH 21 | Delimitación de patrones chartistas geométricos. |
| **OBJ\_ELLIPSE** | Tiempo y Precio | No aplica (tres puntos libres) | OBJPROP\_FILL, OBJPROP\_COLOR, OBJPROP\_BACK 21 | Resaltado de clústeres temporales o de volumen. |
| **OBJ\_FIBO** | Tiempo y Precio | No aplica (dos puntos libres) | OBJPROP\_LEVELS, OBJPROP\_LEVELCOLOR, OBJPROP\_LEVELVALUE 21 | Trazado de retrocesos y extensiones de Fibonacci. |
| **OBJ\_CHANNEL** | Tiempo y Precio | No aplica (tres puntos libres) | OBJPROP\_FILL, OBJPROP\_COLOR, OBJPROP\_STYLE 21 | Canales de regresión o equidistantes clásicos. |
| **OBJ\_TEXT** | Tiempo y Precio | ENUM\_ANCHOR\_POINT 21 | OBJPROP\_ANGLE, OBJPROP\_FONTSIZE, OBJPROP\_COLOR 21 | Anotaciones que siguen a barras de precios específicas. |
| **OBJ\_LABEL** | Píxeles | ENUM\_BASE\_CORNER y ENUM\_ANCHOR\_POINT 40 | OBJPROP\_XDISTANCE, OBJPROP\_YDISTANCE, OBJPROP\_FONTSIZE 21 | Texto informativo estático dentro del HUD de la interfaz. |
| **OBJ\_BUTTON** | Píxeles | ENUM\_BASE\_CORNER 40 | OBJPROP\_XSIZE, OBJPROP\_YSIZE, OBJPROP\_STATE, OBJPROP\_BGCOLOR 21 | Botón interactivo para ejecutar funciones inmediatas.44 |
| **OBJ\_BITMAP** | Tiempo y Precio | ENUM\_ANCHOR\_POINT 40 | OBJPROP\_XOFFSET, OBJPROP\_YOFFSET, OBJPROP\_BMPFILE 21 | Renderizado de imágenes de fondo ligadas al precio. |
| **OBJ\_BITMAP\_LABEL** | Píxeles | ENUM\_BASE\_CORNER y ENUM\_ANCHOR\_POINT 40 | OBJPROP\_XDISTANCE, OBJPROP\_YDISTANCE, OBJPROP\_BMPFILE 21 | Iconos interactivos y sprites de interfaz en paneles. |
| **OBJ\_EDIT** | Píxeles | ENUM\_BASE\_CORNER 40 | OBJPROP\_XSIZE, OBJPROP\_YSIZE, OBJPROP\_TEXT, OBJPROP\_READONLY 21 | Campos de texto editables para configurar parámetros.44 |
| **OBJ\_RECTANGLE\_LABEL** | Píxeles | ENUM\_BASE\_CORNER 40 | OBJPROP\_XSIZE, OBJPROP\_YSIZE, OBJPROP\_BGCOLOR, OBJPROP\_BORDER\_TYPE 21 | Paneles contenedores y fondos para GUIs complejas.45 |

### **Parámetros de anclaje y jerarquía visual**

* **OBJPROP\_CORNER**: Define el origen del sistema cartesiano bidimensional. Permite anclar elementos de forma relativa a cualquiera de las cuatro esquinas mediante ENUM\_BASE\_CORNER (CORNER\_LEFT\_UPPER, CORNER\_LEFT\_LOWER, CORNER\_RIGHT\_LOWER, CORNER\_RIGHT\_UPPER).41 Esto es indispensable para construir paneles responsivos al redimensionado de pantalla.21  
* **OBJPROP\_ANCHOR**: Especifica el punto de pivote interno dentro del propio cuadro delimitador del objeto gráfico (ENUM\_ANCHOR\_POINT).40 Por ejemplo, configurar ANCHOR\_RIGHT\_UPPER alinea el vértice superior derecho del objeto con la coordenada del píxel de anclaje, facilitando los cálculos de interfaz.40  
* **OBJPROP\_ZORDER**: Controla el nivel de profundidad visual (eje Z).21 El valor por defecto al crear un objeto es ![][image1].21 Si varios elementos se superponen en pantalla, **aquel que posea el OBJPROP\_ZORDER numérico más alto se renderizará al frente y capturará de forma exclusiva los eventos de clic del ratón**.21

La creación y manipulación de cualquier objeto se gestiona a través de la API nativa de objetos gráficos del terminal 21:

Fragmento de código  
string obj\_name \= "DashboardBackground";  
// Crear objeto sin coordenadas de precio/tiempo iniciales (para objetos basados en coordenadas de pantalla)  
if(ObjectCreate(0, obj\_name, OBJ\_RECTANGLE\_LABEL, 0, 0, 0)) // \[26, 42\]  
{  
   // Modificar propiedades enteras, reales y de texto  
   ObjectSetInteger(0, obj\_name, OBJPROP\_CORNER, CORNER\_LEFT\_UPPER); // \[21, 41\]  
   ObjectSetInteger(0, obj\_name, OBJPROP\_XDISTANCE, 10); // Distancia X desde la esquina   
   ObjectSetInteger(0, obj\_name, OBJPROP\_YDISTANCE, 10); // Distancia Y desde la esquina   
   ObjectSetInteger(0, obj\_name, OBJPROP\_XSIZE, 220); // Ancho en píxeles   
   ObjectSetInteger(0, obj\_name, OBJPROP\_YSIZE, 120); // Alto en píxeles   
   ObjectSetInteger(0, obj\_name, OBJPROP\_BGCOLOR, clrDarkSlateGray); //   
   ObjectSetInteger(0, obj\_name, OBJPROP\_ZORDER, 1); // Prioridad baja   
}

## **7\. Diseño y Programación de Paneles Interactivos Complejos**

La construcción de interfaces de usuario (GUI) en MetaTrader 5 se puede realizar mediante dos enfoques: la manipulación manual directa utilizando objetos gráficos nativos o a través de la programación orientada a objetos (POO) utilizando la Biblioteca Estándar de Controles de MT5 (MQL5\\Include\\Controls).46

### **Eventos clave en el flujo interactivo**

Para procesar de manera eficaz la interacción del usuario en un panel de control dentro del gráfico, el desarrollador debe interceptar los flujos de información capturados por el controlador OnChartEvent() 47:

1. **CHARTEVENT\_OBJECT\_CLICK**: Se genera de forma síncrona cuando el usuario hace clic izquierdo dentro del área límite de un objeto gráfico con prioridad de selección.47 El parámetro sparam transmite el nombre único del objeto que fue cliqueado, permitiendo ejecutar condicionales selectivas para botones o celdas de tablas.44  
2. **CHARTEVENT\_OBJECT\_DRAG**: Se emite continuamente mientras un objeto interactivo con la propiedad OBJPROP\_SELECTABLE activa es arrastrado por la pantalla.44  
3. **CHARTEVENT\_KEYDOWN**: Captura las pulsaciones físicas del teclado.47 Transmite el código ASCII de la tecla en lparam, facilitando la construcción de atajos interactivos dentro del gráfico.47  
4. **CHARTEVENT\_MOUSE\_MOVE**: Ofrece coordenadas exactas en tiempo real del puntero (![][image11] e ![][image12]) y el estado binario de los botones del ratón mediante una máscara de bits.47 Requiere la activación explícita en el gráfico mediante ChartSetInteger(0, CHART\_EVENT\_MOUSE\_MOVE, true) debido a su consumo moderado de procesamiento.47  
5. **CHARTEVENT\_OBJECT\_ENDEDIT**: Se genera cuando el usuario presiona "Enter" o cambia de foco tras modificar el texto dentro de un objeto de edición de entrada de datos (OBJ\_EDIT).44 Permite la validación de valores o la captura de parámetros de entrada directamente en el panel interactivo.44

### **La biblioteca estándar de controles (CAppDialog)**

El núcleo para el desarrollo estructurado de interfaces complejas es la clase CAppDialog.46 Esta clase actúa como un contenedor base que administra el ciclo de vida de los controles integrados (como botones, etiquetas, áreas editables y paneles).46  
Para inicializar la ventana y sus elementos, CAppDialog dispone de métodos especializados según el contexto de ejecución del programa MQL5 49:

* **CreateCommon()**: Inicialización interna básica de uso general.49  
* **CreateExpert()**: Método diseñado para Expert Advisors.49 Asume que el panel se ejecutará en la ventana principal del gráfico (índice 0\) con comportamiento y escalado adaptados para interactuar con sistemas de trading automatizados.46  
* **CreateIndicator()**: Método específico para **indicadores**.49 Es el que debe usarse cuando el panel se ejecuta en un indicador, especialmente si se ubica en una subventana independiente.46 Este método realiza cálculos de posicionamiento relativos para evitar solapamientos y puede ajustar automáticamente el alto del subgráfico basándose en los elementos visuales del panel.46  
* **SubwinOff()**: Devuelve el desplazamiento (offset) en el eje Y de la subventana en la cual está operando el indicador actual.49 Esto permite asegurar que los objetos secundarios no queden fuera de los márgenes visibles de la ventana separada del indicador.46

El uso de la biblioteca estándar frente a la implementación manual directa de objetos presenta diferencias clave de diseño: la biblioteca estándar permite un desarrollo rápido, robusto y extensible para interfaces complejas 46, mientras que la composición manual de objetos gráficos planos es preferible cuando se requiere un control estricto sobre cada píxel con un consumo mínimo de memoria física en entornos de baja latencia.21

## **8\. Optimización Algorítmica y Gestión de Baja Latencia**

La programación en MQL5 requiere altos estándares de optimización, dado que los indicadores lentos pueden congelar la interfaz de usuario. Al ejecutarse en el mismo hilo de renderizado del terminal, un mal bucle en un indicador no optimizado degradará de inmediato el tiempo de respuesta del sistema algorítmico global.

### **El patrón de prevención de la complejidad computacional: Algoritmo ![][image13]**

El mayor cuello de botella en los indicadores es el recálculo constante de todo el historial en cada nuevo tick entrante.1 Un indicador lineal ingenuo realiza un bucle que recorre las ![][image8] barras acumuladas del gráfico en cada actualización, lo cual representa una complejidad temporal de ![][image14] por tick. Al implementar de manera estricta el patrón de cálculo incremental mediante el control de prev\_calculated, el indicador solo procesa la barra activa en desarrollo.5 Esto reduce la complejidad temporal a un coste constante de ![][image13] por tick.  
Para indicadores que emplean medias móviles, es posible optimizar el cálculo incremental para que no requiera recorrer el período de la media en cada nueva barra. La técnica conocida como **Suma Acumulada Desplazada (Running Sum)** permite calcular un promedio de gran período con la misma velocidad que uno pequeño 5:  
![][image15]  
Esto elimina por completo los bucles aninados en el bucle principal de OnCalculate.5

### **Impacto de ArraySetAsSeries() en la memoria**

La función ArraySetAsSeries() es una herramienta de abstracción lógica; **no reorganiza ni desplaza físicamente los elementos de los datos en la memoria RAM del ordenador**.8 Cambiar la propiedad de indexación simplemente altera el direccionamiento del índice en tiempo de ejecución 8:  
![][image16]  
![][image17]  
El uso indiscriminado de alternancia de indexación (llamar reiteradamente a ArraySetAsSeries() de true a false sobre el mismo array dinámico de cálculo intermedio dentro de bucles o funciones frecuentes) introduce una pequeña sobrecarga de sincronización de metadatos que degrada la velocidad.51 Es recomendable establecer la indexación definitiva deseada una sola vez en el OnInit() o usar exclusivamente indexación de baja latencia secuencial estándar.8

### **Directrices para el perfilado y límites operativos**

1. **Evitar impresiones continuas en el log**: El uso excesivo de Print() satura el registro del terminal, generando retrasos significativos por operaciones de escritura en el disco duro.5 Las impresiones diagnósticas deben comentarse o inhabilitarse por completo antes de compilar y distribuir la versión final para entornos de producción.5  
2. **Control estricto de la creación de objetos gráficos**: Crear y destruir objetos dinámicamente mediante ObjectCreate() y ObjectDelete() en cada tick es una de las tareas más costosas para el procesador.21 Se debe preferir la estrategia de crear los objetos en la fase de inicialización (OnInit()) y luego limitarse a actualizar sus propiedades espaciales mediante ObjectSetInteger() u ObjectSetDouble().21  
3. **Límites de indicadores concurrentes**: Aunque MT5 admite la ejecución paralela de múltiples programas, un chart que albergue más de 10 a 15 indicadores con cálculos no optimizados generará latencia de colas, ya que la cola de eventos visuales del terminal se saturará, degradando el tiempo de respuesta del terminal.1

## **9\. Comportamiento de Indicadores en el Strategy Tester**

Durante los procesos de optimización y backtesting en el Strategy Tester de MetaTrader 5, los indicadores se comportan de una manera especializada diseñada para acelerar los ciclos de simulación 1:

### **Simulación visual vs No visual**

* **Modo No Visual**: Es el modo estándar de optimización masiva de parámetros mediante algoritmos genéticos.1 En este entorno, **MT5 inhabilita por completo la creación física de objetos gráficos y el renderizado visual de los buffers de indicador**. Además, las llamadas a OnChartEvent() no se ejecutan, ya que no existe un gráfico real en pantalla.48 Toda lógica de trading de un EA que dependa de consultar propiedades de un objeto gráfico (como el precio de una línea dibujada por el indicador) fallará, retornando valores vacíos o nulos. Las llamadas que intenten leer buffers de datos utilizando CopyBuffer() operarán normalmente de manera optimizada.20  
* **Modo Visual**: Utilizado para auditar visualmente el comportamiento de los algoritmos.52 En este caso, el motor gráfico se ejecuta y los objetos y buffers se procesan y renderizan en la ventana interactiva virtual.52 No obstante, cabe recordar que OnChartEvent() sigue sin capturar interacciones manuales reales del usuario del terminal en el probador de estrategias.48

### **Uso de la propiedad \#property tester\_indicator**

Cuando un indicador o un EA consume recursos dinámicos, es mandatorio comunicárselo de antemano al compilador y al terminal para que empaquete las dependencias necesarias.28 Si se utiliza la función IndicatorCreate() o se pasa una variable de tipo string no constante como parámetro de nombre en iCustom(), el Strategy Tester no podrá detectar de forma automatizada las dependencias que deben cargarse en los agentes de prueba (especialmente si son agentes remotos o en la red en la nube MQL5 Cloud Network).28  
Para prevenir fallos de carga que devuelvan manejadores inválidos en tiempo de ejecución de las pruebas, se debe declarar explícitamente la propiedad de preprocesamiento de dependencias en el archivo principal del programa que realiza la invocación 28:

Fragmento de código  
\#property tester\_indicator "Directorio\\\\NombreDeMiIndicador.ex5" // 

### **Overhead crítico y optimización de backtests**

El consumo excesivo de memoria por el uso de múltiples indicadores personalizados dentro de un EA durante la optimización ralentiza exponencialmente los ciclos de prueba del Strategy Tester. Cada llamada a iCustom() para obtener el handle de un indicador pesado implica que el probador de estrategias mantendrá en caché interna múltiples buffers de gran tamaño por cada paso de prueba.1  
Para optimizar al máximo la velocidad de los backtests, la práctica recomendada consiste en **eliminar la necesidad de cargar manejadores de indicadores dentro del EA y, en su lugar, migrar las fórmulas matemáticas directamente al código del EA**. Por ejemplo, en lugar de invocar un indicador RSI personalizado pesado en cada tick, el EA puede implementar localmente una función matemática optimizada que calcule el RSI de forma directa sobre arrays estáticos locales poblados mediante CopyRates() o CopyClose(), ahorrando el consumo de memoria de los manejadores y la sobrecarga de sincronización de buffers.1

## **10\. Implementaciones Prácticas y Código MQL5 Compilable**

A continuación, se presentan tres desarrollos de código MQL5 avanzados, totalmente compilables y estructurados según las mejores prácticas analizadas.

### **Caso de Estudio 1: Indicador Visual Dinámico de Velas Modificadas por Volatilidad (DRAW\_COLOR\_CANDLES)**

Este indicador calcula un canal de volatilidad basado en desviación estándar y dibuja velas personalizadas en una subventana independiente, coloreando dinámicamente el cuerpo según la fuerza relativa del volumen de transacciones en comparación con su media móvil.

Fragmento de código  
//+------------------------------------------------------------------+  
//|                                           DynamicColorCandles.mq5|  
//|                                  Architectural Quantitative Dev  |  
//|                                                                  |  
//+------------------------------------------------------------------+  
\#property copyright "Architectural Quantitative Dev"  
\#property version   "1.00"  
\#property indicator\_separate\_window // \[15\]

// Definición de Buffers e Indicadores \[10, 15\]  
\#property indicator\_buffers 5  
\#property indicator\_plots   1

\#property indicator\_label1  "CandlesVol"  
\#property indicator\_type1   DRAW\_COLOR\_CANDLES // \[15\]  
// Definir 3 colores en el array especial (Verde fuerte, Rojo fuerte, Gris para volumen neutro) \[15, 17\]  
\#property indicator\_color1  clrLimeGreen, clrCrimson, clrDarkGray // \[15\]

// Parámetros de Entrada  
input int      InpVolPeriod \= 20; // Periodo de Media del Volumen

// Buffers requeridos para el estilo DRAW\_COLOR\_CANDLES \[15\]  
double   ExtOpenBuffer;  // Buffer de datos 1 \[15\]  
double   ExtHighBuffer;  // Buffer de datos 2 \[15\]  
double   ExtLowBuffer;   // Buffer de datos 3 \[15\]  
double   ExtCloseBuffer; // Buffer de datos 4 \[15\]  
double   ExtColorBuffer; // Buffer de índices de color (0, 1, 2\) \[15\]

// Manejador del volumen medio  
int      VolMaHandle;

//+------------------------------------------------------------------+  
//| Custom indicator initialization function                         |  
//+------------------------------------------------------------------+  
int OnInit()  
{  
   // Mapeo de buffers \[11, 12, 15\]  
   SetIndexBuffer(0, ExtOpenBuffer,  INDICATOR\_DATA);  
   SetIndexBuffer(1, ExtHighBuffer,  INDICATOR\_DATA);  
   SetIndexBuffer(2, ExtLowBuffer,   INDICATOR\_DATA);  
   SetIndexBuffer(3, ExtCloseBuffer,  INDICATOR\_DATA);  
   SetIndexBuffer(4, ExtColorBuffer,  INDICATOR\_COLOR\_INDEX); //   
     
   // Definir el valor vacío para no pintar \[15, 17\]  
   PlotIndexSetDouble(0, PLOT\_EMPTY\_VALUE, EMPTY\_VALUE); //   
     
   // Nombre descriptivo \[10, 25\]  
   IndicatorSetString(INDICATOR\_SHORTNAME, "Dynamic Volume Candles (" \+ (string)InpVolPeriod \+ ")"); //   
   IndicatorSetInteger(INDICATOR\_DIGITS, \_Digits); //   
     
   // Inicializar el manejador de la media móvil simple para volumen   
   VolMaHandle \= iMA(\_Symbol, \_Period, InpVolPeriod, 0, MODE\_SMA, VOLUME\_TICK); // \[29, 30\]  
   if(VolMaHandle \== INVALID\_HANDLE)  
   {  
      return(INIT\_FAILED);  
   }  
     
   return(INIT\_SUCCEEDED);  
}

//+------------------------------------------------------------------+  
//| Custom indicator deinitialization function                       |  
//+------------------------------------------------------------------+  
void OnDeinit(const int reason)  
{  
   if(VolMaHandle\!= INVALID\_HANDLE)  
   {  
      IndicatorRelease(VolMaHandle); //   
   }  
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
   // Verificar disponibilidad de historial \[5, 30\]  
   if(rates\_total \< InpVolPeriod) return(0);  
     
   if(BarsCalculated(VolMaHandle) \< rates\_total) // \[30, 31\]  
   {  
      return(0); // Forzar reentrada en el próximo tick  
   }  
     
   // Copiar datos de la media del volumen   
   double vol\_ma;  
   ArraySetAsSeries(vol\_ma, false); // Indexación estándar de izquierda a derecha   
   if(CopyBuffer(VolMaHandle, 0, 0, rates\_total, vol\_ma) \<= 0\) // \[31, 39\]  
   {  
      return(0);  
   }  
     
   // Determinar punto de partida para cálculo incremental   
   int start \= prev\_calculated \- 1;  
   if(start \< InpVolPeriod)  
   {  
      start \= InpVolPeriod;  
   }  
     
   // Inicialización de buffers de datos no calculados para evitar basura gráfica  
   if(prev\_calculated \== 0\)  
   {  
      ArrayInitialize(ExtOpenBuffer, EMPTY\_VALUE);  
      ArrayInitialize(ExtHighBuffer, EMPTY\_VALUE);  
      ArrayInitialize(ExtLowBuffer, EMPTY\_VALUE);  
      ArrayInitialize(ExtCloseBuffer, EMPTY\_VALUE);  
      ArrayInitialize(ExtColorBuffer, 2); // Color gris por defecto \[15\]  
   }  
     
   // Bucle principal de ejecución   
   for(int i \= start; i \< rates\_total &&\!IsStopped(); i++)  
   {  
      // Copiar estructura OHLC a la subventana \[2, 15\]  
      ExtOpenBuffer\[i\]  \= open\[i\];  
      ExtHighBuffer\[i\]  \= high\[i\];  
      ExtLowBuffer\[i\]   \= low\[i\];  
      ExtCloseBuffer\[i\] \= close\[i\];  
        
      // Lógica cromática basada en el volumen relativo \[15\]  
      double current\_vol \= (double)tick\_volume\[i\];  
      double average\_vol \= vol\_ma\[i\];  
        
      if(current\_vol \> average\_vol \* 1.5) // Volumen alto  
      {  
         if(close\[i\] \>= open\[i\])  
         {  
            ExtColorBuffer\[i\] \= 0; // Índice de Color 0 (LimeGreen) \[15\]  
         }  
         else  
         {  
            ExtColorBuffer\[i\] \= 1; // Índice de Color 1 (Crimson) \[15\]  
         }  
      }  
      else  
      {  
         ExtColorBuffer\[i\] \= 2; // Índice de Color 2 (DarkGray \- Volumen neutro) \[15\]  
      }  
   }  
     
   return(rates\_total); //   
}

### **Caso de Estudio 2: Panel Interactivo de Control en Gráfico utilizando la Biblioteca Estándar**

Este indicador demuestra la creación de un panel interactivo (CAppDialog) integrado sobre el gráfico que permite modificar propiedades visuales de los niveles horizontales y cambiar el color de fondo dinámicamente mediante eventos de clic.

Fragmento de código  
//+------------------------------------------------------------------+  
//|                                         InteractiveDashboard.mq5 |  
//|                                  Architectural Quantitative Dev  |  
//|                                                                  |  
//+------------------------------------------------------------------+  
\#property copyright "Architectural Quantitative Dev"  
\#property version   "1.00"  
\#property indicator\_chart\_window // El panel se renderiza en la ventana principal 

// Inclusión de dependencias de la biblioteca estándar de MT5   
\#include \<Controls\\Dialog.mqh\> //   
\#include \<Controls\\Button.mqh\> //   
\#include \<Controls\\Label.mqh\>  // 

// Clase personalizada que hereda de CAppDialog   
class CInteractiveDashboard : public CAppDialog  
{  
private:  
   CButton     m\_btn\_toggle\_color; // Botón interactivo   
   CLabel      m\_lbl\_status;       // Etiqueta descriptiva   
   bool        m\_state\_toggle;     // Estado interno  
     
public:  
   CInteractiveDashboard(void) : m\_state\_toggle(false) {}  
   \~CInteractiveDashboard(void) {}  
     
   // Sobreescribir el método de creación   
   virtual bool Create(const long chart, const string name, const int subwin,  
                       const int x1, const int y1, const int x2, const int y2);  
                         
   // Procesador de eventos para el mapa interno   
   virtual bool OnEvent(const int id, const long \&lparam, const double \&dparam, const string \&sparam);  
     
protected:  
   // Funciones creadoras de controles secundarios   
   bool CreateButton(void);  
   bool CreateLabel(void);  
     
   // Manejador del evento de clic sobre el botón  
   void OnClickToggleButton(void);  
};

// Inicialización de la clase derivada   
bool CInteractiveDashboard::Create(const long chart, const string name, const int subwin,  
                                   const int x1, const int y1, const int x2, const int y2)  
{  
   // Crear el marco del contenedor base llamando a la clase madre   
   if(\!CAppDialog::Create(chart, name, subwin, x1, y1, x2, y2))  
      return(false);  
        
   // Crear controles subordinados   
   if(\!CreateButton()) return(false);  
   if(\!CreateLabel())  return(false);  
     
   return(true);  
}

// Implementación del botón dinámico   
bool CInteractiveDashboard::CreateButton(void)  
{  
   // Dimensionar en base a coordenadas relativas del panel principal \[40, 54\]  
   int x1 \= 15;  
   int y1 \= 40;  
   int x2 \= 165;  
   int y2 \= 80;  
     
   if(\!m\_btn\_toggle\_color.Create(m\_chart\_id, m\_name \+ "BtnToggle", m\_subwin, x1, y1, x2, y2))  
      return(false);  
        
   m\_btn\_toggle\_color.Text("Cambiar Fondo"); // \[22\]  
     
   if(\!Add(m\_btn\_toggle\_color)) // Vincular al contenedor de la biblioteca estándar   
      return(false);  
        
   return(true);  
}

// Implementación del Label de Estado   
bool CInteractiveDashboard::CreateLabel(void)  
{  
   int x1 \= 15;  
   int y1 \= 15;  
   int x2 \= 165;  
   int y2 \= 35;  
     
   if(\!m\_lbl\_status.Create(m\_chart\_id, m\_name \+ "LblStatus", m\_subwin, x1, y1, x2, y2))  
      return(false);  
        
   m\_lbl\_status.Text("Estado: Normal");  
   m\_lbl\_status.Color(clrWhite);  
     
   if(\!Add(m\_lbl\_status))  
      return(false);  
        
   return(true);  
}

// Manejo lógico del mapa de eventos   
bool CInteractiveDashboard::OnEvent(const int id, const long \&lparam, const double \&dparam, const string \&sparam)  
{  
   // Verificar clics sobre botones del panel \[46, 47\]  
   if(id \== CHARTEVENT\_OBJECT\_CLICK && sparam \== m\_btn\_toggle\_color.Name()) // \[44, 47\]  
   {  
      OnClickToggleButton();  
      return(true); // El evento fue consumido con éxito  
   }  
     
   // Reenviar eventos restantes a la clase base \[46, 55\]  
   return(CAppDialog::OnEvent(id, lparam, dparam, sparam));  
}

// Función ejecutora de la lógica del clic  
void CInteractiveDashboard::OnClickToggleButton(void)  
{  
   m\_state\_toggle \=\!m\_state\_toggle;  
     
   if(m\_state\_toggle)  
   {  
      ChartSetInteger(m\_chart\_id, CHART\_COLOR\_BACKGROUND, clrDarkSlateGray); // \[47\]  
      m\_lbl\_status.Text("Estado: Fondo Alterado");  
      m\_lbl\_status.Color(clrYellow);  
   }  
   else  
   {  
      ChartSetInteger(m\_chart\_id, CHART\_COLOR\_BACKGROUND, clrBlack);  
      m\_lbl\_status.Text("Estado: Normal");  
      m\_lbl\_status.Color(clrWhite);  
   }  
     
   // Forzar redibujo inmediato del lienzo del chart   
   ChartRedraw(m\_chart\_id); //   
}

//--- Estructura Global para lanzar el panel del indicador  
CInteractiveDashboard ExtPanel;

//+------------------------------------------------------------------+  
//| Custom indicator initialization function                         |  
//+------------------------------------------------------------------+  
int OnInit()  
{  
   // Crear el diálogo interactivo de la biblioteca estándar (id de chart, nombre, subventana, coords)   
   // El método especializado para indicadores es CreateIndicator   
   if(\!ExtPanel.Create(0, "DashMQL5", 0, 30, 30, 210, 150)) // \[46, 54\]  
   {  
      return(INIT\_FAILED);  
   }  
     
   // Ejecutar el panel interactivo \[46, 56\]  
   if(\!ExtPanel.Run()) // \[46, 56\]  
   {  
      return(INIT\_FAILED);  
   }  
     
   return(INIT\_SUCCEEDED);  
}

//+------------------------------------------------------------------+  
//| Custom indicator deinitialization function                       |  
//+------------------------------------------------------------------+  
void OnDeinit(const int reason)  
{  
   // Destrucción estructurada obligatoria para evitar objetos huérfanos en pantalla   
   ExtPanel.Destroy(reason); //   
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
   // Los indicadores con paneles interactivos puros no requieren buffers de cálculo continuo  
   return(rates\_total);  
}

//+------------------------------------------------------------------+  
//| ChartEvent event handler                                         |  
//+------------------------------------------------------------------+  
void OnChartEvent(const int id, const long \&lparam, const double \&dparam, const string \&sparam)  
{  
   // Redirigir de manera síncrona todos los eventos del terminal al objeto del panel \[46, 57\]  
   ExtPanel.ChartEvent(id, lparam, dparam, sparam); // \[46, 57\]  
}

### **Caso de Estudio 3: Indicador de Consulta Externa Segura (iCustom Proxy)**

Este indicador de cálculo de overlays implementa la inicialización robusta del manejador de una media móvil compleja de un indicador personalizado mediante la función iCustom(), validando la descarga de historial, previniendo duplicados y gestionando la liberación de recursos.

Fragmento de código  
//+------------------------------------------------------------------+  
//|                                                iCustomProxy.mq5  |  
//|                                  Architectural Quantitative Dev  |  
//|                                                                  |  
//+------------------------------------------------------------------+  
\#property copyright "Architectural Quantitative Dev"  
\#property version   "1.00"  
\#property indicator\_chart\_window // Superpuesto en el gráfico principal 

\#property indicator\_buffers 1  
\#property indicator\_plots   1

\#property indicator\_type1   DRAW\_LINE     //   
\#property indicator\_color1  clrDodgerBlue //   
\#property indicator\_label1  "SmoothedProxy"

// Parámetros del indicador Proxy  
input string   InpIndicatorPath \= "Examples\\\\Custom Moving Average"; // Ruta del custom en disco   
input int      InpMAPeriod      \= 14;                                // Periodo de cálculo  
input int      InpMAShift       \= 0;                                 // Desplazamiento horizontal 

double ExtProxyBuffer; // Buffer principal de datos

int    CustomIndicatorHandle \= INVALID\_HANDLE; // Manejador de caché interna \[28, 35\]

//+------------------------------------------------------------------+  
//| Custom indicator initialization function                         |  
//+------------------------------------------------------------------+  
int OnInit()  
{  
   // Registrar buffer de datos dinámico   
   SetIndexBuffer(0, ExtProxyBuffer, INDICATOR\_DATA);  
     
   // Sanitización del path para cumplir con el formato de localización de la API   
   string clean\_path \= InpIndicatorPath;  
   StringTrimLeft(clean\_path);  // \[30\]  
   StringTrimRight(clean\_path); // \[58\]  
     
   // Carga segura del manejador en caché central del terminal   
   // El compilador registra la dependencia y el conteo de referencias aumenta en 1   
   CustomIndicatorHandle \= iCustom(\_Symbol, \_Period, clean\_path, InpMAPeriod, InpMAShift, MODE\_SMA, PRICE\_CLOSE); //   
     
   if(CustomIndicatorHandle \== INVALID\_HANDLE)  
   {  
      int error \= GetLastError();  
      Print("Fallo al instanciar el indicador custom. Código de Error: ", error); // \[28, 30\]  
      return(INIT\_FAILED);  
   }  
     
   // Establecer el nombre del indicador dinámicamente \[10, 25\]  
   IndicatorSetString(INDICATOR\_SHORTNAME, "Proxy MA (" \+ clean\_path \+ ")"); // \[10, 25\]  
     
   return(INIT\_SUCCEEDED);  
}

//+------------------------------------------------------------------+  
//| Custom indicator deinitialization function                       |  
//+------------------------------------------------------------------+  
void OnDeinit(const int reason)  
{  
   // Desvinculación de recursos en la descarga del indicador \[35\]  
   if(CustomIndicatorHandle\!= INVALID\_HANDLE)  
   {  
      // Disminuir en 1 el contador de referencias global   
      if(IndicatorRelease(CustomIndicatorHandle)) //   
      {  
         CustomIndicatorHandle \= INVALID\_HANDLE; // \[35\]  
      }  
   }  
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
   // Impedir procesamiento si el historial de datos es insuficiente  
   if(rates\_total \< InpMAPeriod) return(0);  
     
   // Consultar al subsistema si el indicador ya calculó los datos en caché   
   int calculated\_bars \= BarsCalculated(CustomIndicatorHandle); // \[30, 31\]  
   if(calculated\_bars \< rates\_total)  
   {  
      // No detener la ejecución completa; retornar 0 para recalcular en el siguiente ciclo síncrono \[5, 39\]  
      return(0);   
   }  
     
   // Cálculo incremental del tamaño de transferencia de los buffers de datos \[5, 39\]  
   int to\_copy;  
   if(prev\_calculated \<= 0\)  
   {  
      to\_copy \= rates\_total; // Inicialización de todo el historial en memoria \[39\]  
   }  
   else  
   {  
      to\_copy \= rates\_total \- prev\_calculated; // Slices de actualización mínima \[39\]  
      to\_copy++; // Sincronizar el último estado mutante de la barra en desarrollo \[39\]  
   }  
     
   // Matriz temporal estática de transferencia rápida \[31, 39\]  
   double temp\_data;  
   ArrayResize(temp\_data, to\_copy);  
     
   // Operación de lectura de memoria sobre el buffer remoto de la caché central \[20, 39\]  
   if(CopyBuffer(CustomIndicatorHandle, 0, 0, to\_copy, temp\_data) \<= 0\) // \[31, 39\]  
   {  
      int error \= GetLastError();  
      Print("Fallo al copiar los datos remotos del buffer en OnCalculate. Error: ", error); // \[20\]  
      return(0);  
   }  
     
   // Transferencia local al buffer del indicador actual \[39\]  
   int buffer\_start \= rates\_total \- to\_copy;  
   for(int i \= 0; i \< to\_copy; i++)  
   {  
      ExtProxyBuffer\[buffer\_start \+ i\] \= temp\_data\[i\];  
   }  
     
   return(rates\_total); //   
}

#### **Fuentes citadas**

1. How to Improve Optimization Speed in MetaTrader 5 Strategy Tester? \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/497727](https://www.mql5.com/en/forum/497727)  
2. Main indicator event: OnCalculate \- Creating application programs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/indicators\_make/indicators\_oncalculate](https://www.mql5.com/en/book/applications/indicators_make/indicators_oncalculate)  
3. OnCalculate \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/oncalculate](https://www.mql5.com/en/docs/event_handlers/oncalculate)  
4. Custom Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind](https://www.mql5.com/en/docs/customind)  
5. Coding Custom Indicators in MQL5: A Practical Guide for Algo Traders | by TradersMarket.io, acceso: junio 28, 2026, [https://medium.com/@tradersmarket.io/coding-custom-indicators-in-mql5-a-practical-guide-for-algo-traders-923bb6f2698b](https://medium.com/@tradersmarket.io/coding-custom-indicators-in-mql5-a-practical-guide-for-algo-traders-923bb6f2698b)  
6. OnCalculate() returned value and prev\_calculated parameter \- Price Chart \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/152462](https://www.mql5.com/en/forum/152462)  
7. (SOLVED) OnCalculate being called twice with prev\_calculated \= 0 \- Spreads \- Technical Indicators \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/359770](https://www.mql5.com/en/forum/359770)  
8. Indexing Direction in Arrays, Buffers and Timeseries \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/bufferdirection](https://www.mql5.com/en/docs/series/bufferdirection)  
9. Buffers as series or not? \- Indexes \- Technical Indicators \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/466944](https://www.mql5.com/en/forum/466944)  
10. Connection between Indicator Properties and Functions \- Custom Indicators \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/propertiesandfunctions](https://www.mql5.com/en/docs/customind/propertiesandfunctions)  
11. Drawing Styles \- Indicator Constants \- Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/indicatorconstants/drawstyles](https://www.mql5.com/en/docs/constants/indicatorconstants/drawstyles)  
12. Indicator Styles in Examples \- Custom Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/indicators\_examples](https://www.mql5.com/en/docs/customind/indicators_examples)  
13. DRAW\_COLOR\_ZIGZAG \- Indicator Styles in Examples \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/indicators\_examples/draw\_color\_zigzag](https://www.mql5.com/en/docs/customind/indicators_examples/draw_color_zigzag)  
14. DRAW\_COLOR\_BARS \- Indicator Styles in Examples \- Custom Indicators \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/indicators\_examples/draw\_color\_bars](https://www.mql5.com/en/docs/customind/indicators_examples/draw_color_bars)  
15. DRAW\_COLOR\_CANDLES \- Indicator Styles in Examples \- Custom Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/indicators\_examples/draw\_color\_candles](https://www.mql5.com/en/docs/customind/indicators_examples/draw_color_candles)  
16. DRAW\_ZIGZAG \- Indicator Styles in Examples \- Custom Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/indicators\_examples/draw\_zigzag](https://www.mql5.com/en/docs/customind/indicators_examples/draw_zigzag)  
17. DRAW\_CANDLES \- Indicator Styles in Examples \- Custom Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/indicators\_examples/draw\_candles](https://www.mql5.com/en/docs/customind/indicators_examples/draw_candles)  
18. Indicator Constants \- Constants, Enumerations and Structures \- MQL4 Reference, acceso: junio 28, 2026, [https://docs.mql4.com/constants/indicatorconstants](https://docs.mql4.com/constants/indicatorconstants)  
19. DRAW\_FILLING \- Indicator Styles in Examples \- Custom Indicators ..., acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/indicators\_examples/draw\_filling](https://www.mql5.com/en/docs/customind/indicators_examples/draw_filling)  
20. MQL5 CopyBuffer Explained: Syntax, Usage, and Common Errors \- トリロジー金融メディア, acceso: junio 28, 2026, [https://finance.trgy.co.jp/en/mql5-en/reference-en/copybuffer/](https://finance.trgy.co.jp/en/mql5-en/reference-en/copybuffer/)  
21. Object Properties \- Objects Constants \- Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/objectconstants/enum\_object\_property](https://www.mql5.com/en/docs/constants/objectconstants/enum_object_property)  
22. OBJ\_BUTTON \- Object Types \- Objects Constants \- Constants, Enumerations and Structures \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/objectconstants/enum\_object/obj\_button](https://www.mql5.com/en/docs/constants/objectconstants/enum_object/obj_button)  
23. Indicators in separate subwindows: sizes and levels \- Creating application programs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/indicators\_make/indicators\_separate\_window](https://www.mql5.com/en/book/applications/indicators_make/indicators_separate_window)  
24. IndicatorSetDouble \- Custom Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customind/indicatorsetdouble](https://www.mql5.com/en/docs/customind/indicatorsetdouble)  
25. ObjectCreate \- Object Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/objects/objectcreate](https://www.mql5.com/en/docs/objects/objectcreate)  
26. how to get the previous data of indicator \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/7203](https://www.mql5.com/en/forum/7203)  
27. iCustom \- Technical Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/indicators/icustom](https://www.mql5.com/en/docs/indicators/icustom)  
28. Technical Indicator Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/indicators](https://www.mql5.com/en/docs/indicators)  
29. iMA \- Technical Indicators \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/indicators/ima](https://www.mql5.com/en/docs/indicators/ima)  
30. Access to Timeseries and Indicator Data \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series](https://www.mql5.com/en/docs/series)  
31. IndicatorCreate \- Timeseries and Indicators Access \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/indicatorcreate](https://www.mql5.com/en/docs/series/indicatorcreate)  
32. The Structure of Input Parameters of Indicators (MqlParam) \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/structures/mqlparam](https://www.mql5.com/en/docs/constants/structures/mqlparam)  
33. Handles and counters of indicator owners \- Creating application programs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/indicators\_use/indicators\_descriptors](https://www.mql5.com/en/book/applications/indicators_use/indicators_descriptors)  
34. Deleting indicator instances: IndicatorRelease \- Creating application programs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/indicators\_use/indicators\_indicatorrelease](https://www.mql5.com/en/book/applications/indicators_use/indicators_indicatorrelease)  
35. IndicatorRelease \- Timeseries and Indicators Access \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/indicatorrelease](https://www.mql5.com/en/docs/series/indicatorrelease)  
36. Synch CopyBuffer in EA using iCustom \- Indices \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/500128](https://www.mql5.com/en/forum/500128)  
37. MQL5 Object Properties Overview | PDF | Cartesian Coordinate System | Pixel \- Scribd, acceso: junio 28, 2026, [https://www.scribd.com/document/518783358/Obj](https://www.scribd.com/document/518783358/Obj)  
38. Chart Corner \- Objects Constants \- Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/objectconstants/enum\_basecorner](https://www.mql5.com/en/docs/constants/objectconstants/enum_basecorner)  
39. Methods of Object Binding / Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/objectconstants/enum\_anchorpoint](https://www.mql5.com/en/docs/constants/objectconstants/enum_anchorpoint)  
40. OBJ\_RECTANGLE\_LABEL \- Object Types \- Objects Constants \- Constants, Enumerations and Structures \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/objectconstants/enum\_object/obj\_rectangle\_label](https://www.mql5.com/en/docs/constants/objectconstants/enum_object/obj_rectangle_label)  
41. Graphical object events \- Creating application programs \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/events/events\_objects](https://www.mql5.com/en/book/applications/events/events_objects)  
42. CPanel \- Panels and Dialogs \- Standard Library \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/standardlibrary/controls/cpanel](https://www.mql5.com/en/docs/standardlibrary/controls/cpanel)  
43. Panels and Dialogs \- Standard Library \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/standardlibrary/controls](https://www.mql5.com/en/docs/standardlibrary/controls)  
44. OnChartEvent \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/onchartevent](https://www.mql5.com/en/docs/event_handlers/onchartevent)  
45. Event handling function OnChartEvent \- Creating application programs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/events/events\_onchartevent](https://www.mql5.com/en/book/applications/events/events_onchartevent)  
46. CAppDialog \- Panels and Dialogs \- Standard Library \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/standardlibrary/controls/cappdialog](https://www.mql5.com/en/docs/standardlibrary/controls/cappdialog)  
47. Can you please give me sample code of OBJ\_BUTTON because MQL documentation SUCKS \- Indices \- MQL4 and MetaTrader 4 \- MQL4 programming forum \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/160393](https://www.mql5.com/en/forum/160393)  
48. technical question about mql5 ArraySetAsSeries() function \- Limit Orders, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/484732](https://www.mql5.com/en/forum/484732)  
49. Strategy Optimization \- Algorithmic Trading, Trading Robots \- MetaTrader 5 Help, acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/algotrading/strategy\_optimization](https://www.metatrader5.com/en/terminal/help/algotrading/strategy_optimization)  
50. Advanced way to create indicators: IndicatorCreate \- Creating ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/indicators\_use/indicators\_indicatorcreate](https://www.mql5.com/en/book/applications/indicators_use/indicators_indicatorcreate)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAApElEQVR4XmNgGJpAHl0AHZwA4qtA7AbEj4H4AIosFMwF4r9oYv+BuBRNDKvgDKg4HEhDBTyRBYEgByoOBwlQAVNkQSCIgIqrwgQqoQL6MAEoCIaKw22qggqgKwyCioejCxjDBKAgDCoON8AOKmAJE4CCWKg4yLNgwA4VAJmADGBOQgEggUloYtug4igAm24QH+R+DLCcARKNIBqkqABVehRQAwAA4fYow14SzbMAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIgAAAAaCAYAAABsFBQaAAADzklEQVR4Xu2ZWchNURTHlzGzFMn4fTyYMpYMeTCV8EAiKQ9keFCkKHkgDySRoRBJ+swl4kHkAV88igfeKIokYySZh/W31/7OPuuee++59+getH717+79X2fvs+85++yz9r1EhmEYhmH8w7RmDdWmYYBnrJ+iPBnEeq7NPLnL+q7NHOhF2W5O1vYA7b9oswZMY72kaIK+iIfzBQO6oM0cOEfZbnDW9gDtt2qzxvxVE6QZuQGN1IEcwDjeaLMCsrbvR66PDjpQYzJNENzIXaxWUl/C2haFC1jF2qRNZjBrJrm+MKBZUk9iIesMa7gOCC1Z61l7WH1VLA0zyJ0b4zgm5e6xIxxdWEdEbQM/bfv5rEOsjjogNFD2FehPUPUEQYZ9kzWPXCcfWT3JTRL9xWaLhwvZXMrQQImvYK1lfRN/jSjkuMRGSL2RNacp6hhGrg+cAzxkdY3CZcGxOO9Bio+jfXgQ8551ScqYkDgW1yFNe5QRmyx1rDKon246wgEvj/xDU/UEuS6fuLnopLfUUb4vZTBAvCGBt1M8DTy8uzWXqfD4uVT4fsYx06XcRuqdo3BqSuUP8K8q77z4nnLtTwb1TuKNDTwAb4vy8gDjQMJaMRvlE09peDFwY0IQ0xfrSYLn8w/96mgh/n6p4wncQG7F0vhzYWxY4aoFfbzSJnObCscNTlDcL9b+DhW2X5rg1YnXTvlJYNUcnVLV5DMYx2ttVgI6aNSm0I1cPGn5vKK8leJrdpDzsWxvZi2m4hfuAEWTBNodD6cGbVdrk5z/VZvktuXh2Eu119/xUYKHvEZ7xcCWFDlbGuF+VArGgddg1aCDidoUkCwi7nMND7zxyvP7bs01SvY1WIE8Uyj5ZqQBv1yinc9jQuAj+dXAfyzlcu3TPCzwPisvLzCWt9pMywIqfRN8AhuyLPCWs/pLGd5FKQM/KLxOdB+eqfLpV6p1QWwR60dQT8tZip/vRlCGj11UyHbx/YQo135CUPcJ+yRyE/yo+PB8foVfVPMEY3mnzbTco+I3z4N4HynXS923CbN0eJg8AHlNmMsg5icSwMXEslcvdWwZ9YX8xBqlvDTcomh8Y8i92jxPWQ+COuI4NkzAS7WHf1jV/bHY8vqfC+CNIzfJ9UpbazCWpHwvFdhS7tOmoo6iC7FXPCyfqOMCevxqBPUIfICdCFYDHz8VD/8Gno/jC+lktxLQHv1gddBgRfDnwesviVLtP5CL4S8F0Cj1BqkDTCJ4+BkhD/CaxAOIBwIbCggPILb3/yXXKbqppWQYhmEYhmEYhmEYhmEYFfELuMwo859I6BUAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAAZklEQVR4XmNgGLqAGV0AGYAka4D4PxBnocnBwQ0gXgfEfgwEFCKDoaIwB10QGwApzEUXxAZACvPQBbEBkMICdEFsAKSwEF0QHYgwQBT2oEvAwGogfg3ET4D4MZR+CcS/kBWNAsoBAO7yGbPFo+KDAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,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>

[image5]: <data:image/png;base64,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>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAZCAYAAADJ9/UkAAABSklEQVR4Xu2UvS4HURDFj0SjEYVoNAoPIFEqNJ5A4QU0PkJItLwAjYSO6Cgo1KgkElQkwgPQiEThKyISZjJ3Zfbce9nkX7q/5GRnzszO5O5uFigUgAXRJJuORdGT6E00TrWKftGZ6Et0RLWIHdEHrFk1VS//cC06dPmV6MTlyjBsRsUA5b+SW96J9BD1uijnJ6cHOyUvSW75BfLLN0LcE3K9eg6C/ye55dUrYby/5GLPFtJ+RCvL913sWUfaj9CmaTbRbPmxiz2rML+XC4w2zbCJZsu3XexZg/ntXGC0aZZNNFuee+ebSPsR2jTHpvCM9AD1bkI8FPKWvvZ5NoUxpAeoN0j5qMuVF9EjeRHdsJtXuBDQ2oTLl4Pn0VN+urwN1tPnvBq7ogfRneg2XO9hfyZPB2zQuehS9A4bzmjtVbQH6x+plwuFwn/hG6lpbbnBW51jAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAZCAYAAAChBHccAAABcElEQVR4Xu2VvytGYRTHj7DIIhQD78ZqMInFpJTBavMH6I0iZbNIBhksysJA/AdGkzIZDLIRSvkD5Nc5nfNc937vPa+3PCbPp769fT/P83RPt7fnEiUSid9wiQI44XxyrjkdsBaY5zxy3jgbsBadC9KBQqpoJ10btN5qvT/boZxyHnL9kPOS63/GIvnDn3PuwW1Reb/0tgo3BS46jYYXvwtuzHxgG3pA3C3K2HjDh7/IGvia+Vnrr9YRcVU+Kt7wI6Re1vP0ml+x7g3p+ah4w0+S+gXwXeb3rHtDej6jmzPaZIbtDOINP0Tq6+B7zK9b94b0fEaNM9NkJuwM4g3fQupXwQ+Yn7Mu93rV+R+Hj4E3vCDeu23CXX9mHRH3gTI2jYZ/51yBW6bi/j7oAXFLKGOzSfoguUWQcSoPJn0HnLzho1yfpvK5qMj9/ET6Bb2z32fOQX4Tfb/pY9Iz+8XlDFm7If0qy/7O4nIikUgk/gtf7m1yTQF6CeMAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAAA3klEQVR4XmNgGAWUgnlA/BmI/0PxAhRZCPjLgJAHYWdUaUyArBgb2AfEKuiC2AAjEG8H4vUMEMOCUKXBAJclGCAfiE2gbFyu+4MugAu8RWJ/YIAYxockpgbEnUh8vADZJaBwAfFvIoktA2IeJD5OAAqvzWhi6F7F5m2sADm8kMVABnRD+b+Q5PCCd+gCUABznTYQt6DJ4QS4vLCbASJ3D4g50eSwAhYg3osuCAVMDJhhhxMwA/EbID6JLoEEvgHxD3RBdLAKiD8yQNIXKF2B8h42oA/E2eiCo2AUDGkAAM4NNN65dbHtAAAAAElFTkSuQmCC>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAAf0lEQVR4XmNgGAUjDZxBF6AmOAnE/5EwyYAViEvRBfGAIgYyLeJgoJNFPAx0soiXYShbZIIF2wPxJCziIIwNEGWRHxYcDsQLsIiDMDZAlEXYAE2CDhsYtBZ1MUAsEkWXIASItegXEL8A4idA/BhKvwbixciK8AFiLRoFo2CkAwAtOCUn2On9ZQAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAAYUlEQVR4XmNgGAUjDZxBF6AmOAnE/5EwzUERw6hFZILBZZEwEJsQidWhetABURbJA7EfkdgWqgcdEGURNcDws6iLAWKRKLoEtcAvIH4BxE+A+DGUfg3Ei5EVjYJRMAooBwCZZh7vPiWQwAAAAABJRU5ErkJggg==>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAAAxElEQVR4XmNgGAWUgmgg/gnE/5HwGyT5X2hyt5HkcAI3Bojip2ji3ED8D4i50MQJApjt6GJkgZUMEM3NUD6IzYyQJg0wMiBc9w2IBVClSQe/GSCG2aNLkANOMkAMu4cuQSqYBcTlDNgjgiSQDcRLoGxYRIAMJhm4APFpJD5yRJAE1IH4BbogAyLlS6BLYAPsQDyfAaKBDU0OBIoZIHLP0CXQwS0g/gDEb4H4IxB/RZVmeAcVB8mD2J+BuBJFxSgYBUMVAABeDDWMwfmAxgAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAZCAYAAADXPsWXAAAAnElEQVR4XmNgGAXYwDIg/gHE/5HwTRQVDAyMSHIg/AVVGgEOMEAU1KCJw8AMIN6MLogOhBgQNqEDOyA+iy6IC2AzBGT4ZzQxvGARA8SQiUhi6IYSBCwMqK75B8TMCGniAcyQ90AsiyZHNOhngBgShi5BCnjNQEY4oAOQAR/QBUkB+gwQQ0rQJYgBMUB8hAERqCCXHEBWMApGwaAAAJrRKHZiVir5AAAAAElFTkSuQmCC>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAaCAYAAAAue6XIAAABwklEQVR4Xu2WTytEURjGH/9ZEAvKAgufQWQjf8IHUCxkslD2SvIRlJIsfAcfwYaNZCU2oiyQBRaUQv6+r3MuM49773tGQ9H86qnxO89953TnzjFAkb/DIAuDZkkpy+/QJlmVrEjqaC2OackcywBeWeTDEtyACf93q+RCcv/R+EqL5JxlFvVI3lSl5IWlhX4cOnCTFzxPSB6q11WTa5Sc+LUoSWxJFlmmocOOWWbRB9fpJ98teSDHWJstQ/p6Dmewy9GdXyP/CPtZtTar6PoAS6YHrrhBnmmA612TV1dDjgnZ7IFkhyWjd0YH8TPHjMP1drNcrXcWIZudh90JGqQcwvX0iIro9c4i5D3GYHSaEDZIietNxrg44q5lOmF0om/hHS8QI3A9PtYy3luEbLYDdidoUFKnC/GeSbo+m1HYHdwgvRQd7BW8gM8TwiJks3r8WZ13tLTHUriEOy3S0Gv1X2YaIZvdR+5Jk8oV3MBtuGdYX+tDb6G9GZYePZP1N8Opj77mczpC5wyxLDSzkluWeVIC+84XDH2jcpZ5sC5ZZvlTDEuOWAaivzmeWf40C5IplgH8+kYjMiwM2iVVLIsU+Q+8AcPof4U5yGDQAAAAAElFTkSuQmCC>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAaCAYAAAAaAmTUAAACS0lEQVR4Xu2WvWsVQRTFj5qIJijYmEYNKWzFzqigGCEKYiOWkmAh2GgjMf4JYmUh6P8giJBGUkUb0wgigqhgISJR4xd+a0i8J3c2b97JvJ3Vt7Hx/eDw3px75w47Mzs7QIf/h2E12mSnGn9Lv+ma6Yppo8RSnDZdULMGFtT4Ey7DC4yE9jbTa9P3pYzlbDW9VDNiFl6zkPIMzfHHUWzA9D5qV2I1vNBtDQTmTPNqBthvnZrCTdM9eO5uiZEu0yM1A19MR9Usg4NwhloxBM85KP4e0w/xUrDv2vD7U2LkjOmImoHtSK9okhfIJxcrd138X6j2rnwMv3wQ1uFKxMxIW2GfHjWV/fDEKfGVTfC8D+LTWy+essN0LvzfC+9zpxFeJDeZjF9SU+HMMjG350/A8+5H3obg5bhhWhO12Uf73ZW2MokK2zlVOMUTeB6P4IIDwcuhOReDV6wWa+a+UfxMaJ0mNqP6w6TyTia8FMX7EhPXexUHWjCOzFhceiZ804BwHJ6nx/Zo8MvgV3xMTeMhvG/Vk4o1snmpGVda5Qwi7cdMYPnJRXrhfblqehikuIr8WIvFypKew+PdGkDjhCujLM6PMON893LcMn1VMwULPlDTeAM/7cpgX34MU5yFx1dpIHAY5Q8bwzxetSpR3J+m4e8Q/+9qykjDvOJUKuC2+mR6F8QZPdSU0eCtGi3gONwJK8p502c1a2YLqq9g23Cg1EteF7w1H1NzpeDef6pmTfQhf2+rHd6bTqlZA/9seymjarTJPjU6dOhQD78BqRyWmBpJICMAAAAASUVORK5CYII=>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAA9CAYAAAAQ2DVeAAAKnUlEQVR4Xu3dd6xsVRXH8aVgQwQrthifqFhRBLuoY0VBFI0SEJWgKBp7r5Fnw5ZgbAixoIgauyZqrAgS1D/0xa5gVOwtPuxid/+y93LWrLvPnfdm5t373p3vJ1mZvdc5c+bcc8+d2XefffaYAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANh4/lHivyX+WOLvrbyjXa7Ea3JyRheWuHSJX5X45uSidXWU1WOpuKjEX1t5kTaVeHhOdujY+L64B4bch0N+Z/YHq/v7t1B+38Qa8/tWTmwD7YfO6Xl8JicAAIiOtZUNiVxftINL3CAnZ5D3M9fXm/bnkE5uUR5bYq+cHOCNs8eE3NNCeVeRj5/qN0q5eXw2J6bQuax9uF9esAr93j6Ycl9LdQAAJujD5qWd3K4g76d6XXYmef+kl1sLHyvxEJt8/fXal1l5r2Wk+gEpt5bUq6t9ODkvWIXWv2ROAgCwmvwB+OMSV2rlJ5b4fomrtPq72qNcUOLcEncr8WWb3I4urf6zxB4lzitxcVimS3hx3R+2+iarl6Py/ohyaowd1slr/3x/nXordKnX3SaU/2KT+/avlleu99rzyNv7bYlLtbJffr59iZ/+f43q3yV+b/VSr/tOifNtvM3TQtldwerzcl68gaBlvl393qIflfh4qMftXKLVYy4esy0lXhyWvdmG92VW2tbLQ13nnm/f90/HV8f5z75S8Uurxy/ui46H6jr/jiuxv9Xz745hHdH5cZbVy9pDflPi66Eez3/9bv11b9jK8Tiqh/QrJZ7e6u7nVv++XtDq+ZzO+6N9H/r7AQBsAPENXuX9Ql22lrhlK/u6e6d6LL861XN5Wl0ffjdp5d3Tsvw8eaNNfgC63vNel+q5fGAoL8LvSpxe4tQStw15b2D6a3vj4lYhd1WrjTmJ+6gPbR8vFfPfK/GoUI/L4hi1Y2zlsRKNCzvIamNHbl3iB638UauNB/Exc+e0x7it17dH7UvUe71ZaDs6nm8r8ZS0TPuv5dcscZkSn2v5+Nr+j8OHSpzZyo8o8ewSVyzxkRJPbnlRo8upgZx541b7k3/GWI/j7Lxh6e5r9WeJv6O4XOXRQL5X7tUBABtA/K/9PrbyzX7og+HIEl8M9W19nsQPQhlaV+WnprpT70WUXyNvJxpapt63nvtPiR59wF8vJ5Pefmls03M7+Z447imvM/Qzev39KSfKe0+cejS98a68GsZ5zJsa7nnbknO5LvkYTjue0ttO1Fv+kxInlrhpyPXWk5jfXGLPUFevZ6RGqW7UUfRuKBk6/h+wyUahxOWPT/VeWY1p9cDlvKgXOu8LAGAXp96Fe4W6enrym73X1QugngldhvK8LsHJXiX+U+KEVn9TiVe08sus9opco9VvYfWS3BmtLr0PpdwYuIONe3/UG6Keiiiuq4H+fseoX/p6a6urt8v3bV+bvFybf/Z5TNuWeoLia0vvOTpuvfyT2uPn22NcRz0/6i1yzwtl2WL9bfZ+D7kcfcPqOSSfDvnV9mVWvV6srLf8iJyw/nq5NzePh8zPiZfZr2WTy+P5L1rm53/ejnhOl3PVoHttWOY3J8RzeqvVvyOd0+oVzr8r9ZQCABbo6BbZg6yfX7T84aG6Il4a9HX0qB4j72mIz9WAdjWo3ttZ5mU16ORn7VHriy6j+dinZ1jtXfpEq7+kxF1aWdu5WStrzE98DY2V2i3U9QGqDzXR677DxuPv4vPU+xLHLGmZLmMuQj62mT58RymnRtgjW1l3H/odpr3j6Y9qLMe6fnb1+LgrW73ZINucEzbexo1DWeIYu1eWuGwrv8rGvUVqQLihfZmHtun/EAw5Oyes/o5d79zVuDI1aHWJVJeg/TKwxm3q0qpo7KD30Olnz79bXb7u/Y5EvWGfsvH578s0zk2OL/Ecm7wk6o1Frev/mMRz2reRz2ld7o4NZwBYKL0J6w3H35wWeffU9a1eNtKAYD1+1caNiu2lMTH5jVr0xqtxV7PQG/WQUU6skRda/XBw+p14L0Uc9H94KMuDQ1mXS6NDUz1O6ZEvG/Z6RCQeezUURB+0bwn56OpWPyzl5iEf9+06oSw+Vm8t+Pi0TL2PGteUPTonin1S/c62sudxe3mPmXijWtRD1BvjpwaP30gRHWvz78uiPCwnirvbyuOc57S7bok7pdy2yOf/vVM9X/Z9aKo7/SMSxXP6qLjA1uYfPABLLDeAhj5856E3z/w6uT6NPqw0ZiVe5hDfzgMmstsuN9h0J5sbhfKy8uOrucN0Bxyw0fk575fyAWCnkN+QnpDqi6DLIPmOsvy603zX6oD8bHu3k+UGWzTKiSV0Sol32+T0FsBGpkvMuoQ6SnkAWFd+KTRORyAaE6KxJJre4UtW19FYHA3G/UKrR5p24NdWp07wcScur6u6D5b3+tDcU173uN1APrpry/kYFdHgbI1LU97n/ZLYYNMYF/0cbhTKAAAA68bvgPPwMS9qvGxqOTdU1p2NPiA4N55EuXuWuIfV70/8dlimwejiz9PA9aFt9OiOrkh3mr0h1E+y2oAT30bcljfYTmuPcdkolCM1Nt+Z4u1W76LTZKUAAAA7jBorPvWCaMyYTzmhO+fOCsuGGm+5YaWxZTmnug9aFzUSfaoK9bTl3j7J2xBNXnrtlNN6unyqR59AVtSQelGou9jDpoHbB4T6KJQXRftFEMTyBADMLb+Z+NQQLi5X2acSUMPGl6nBk9eL1FP3rJTTOvFusPiVMvn5ojuz4mVMp7mWst7zZSgfG2xxAlsZpbrTJV81OIcCAABgYWIjRtM8qGcqGmqI+diw49qjL9OjBuzGhk9uKP3CVt6673dmxrmn4jQFGksXG5Iub1s0saxTr+CmVu6tK7HBpnXi9wmOQhkAAGDN+TxcuntTc6Np5vpMNxm4+D2MorFokc8BpnmoZjE095QMNbaG8pq3yb8r0mk+uJ7YYPMvWHejVAcAAEByYYnn28qGmeq6PLuIGfGZ1gOrucjq+aZeY02iqrL+wZmVen3jHdLT/MlWnv8AAOxUdNPDBTlp9QMsf3n5rGiwYZrcYFJdEwnPYpavLfpkTgAAsGw0Zi2OW3OPs34ey8WnvYlUzxNB7yiaLodJiwEAAFahG2I0cbS7mvUbcOeVOLnVNS+h7o7WVDLK79/yuoR/cSs7fd2XordNbSN/R67WPdcm5zIEAABYamo4nW51UuQT0zKJXw6uO6CdN8A03u3yNm6oxYZZr5G2Z8oPlc8vcXioAwAALK3cqIo0MfOpJZ5ZYo+0rPe8LSWOCPXYc3eY1ecoTgh5387ZNrm+8oeEOgAAwFLSVDO9hpc7Mycafc3Z5py08bZOKXGgjS+V+rKD2qM7vsQ5Vie0Vj6vDwAAsPTUKHpPTib7tkd9vZpPAD3UmFJ+n1A/oz0eY+O7R7e2R/FGmr4u7WAbr68xcnv7SgAAAFid5lTLk0UfmepOk0/vFuq7lzg61N1+VpfJoSE/tD4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATPc/Rk6W09UYgxQAAAAASUVORK5CYII=>

[image16]: <data:image/png;base64,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>

[image17]: <data:image/png;base64,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>