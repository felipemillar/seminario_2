# **Arquitectura de Simulación de MetaTrader 5: Manual Técnico del Strategy Tester para Ingeniería Cuantitativa**

El motor de simulación histórica (*Strategy Tester*) de MetaTrader 5 representa la base tecnológica sobre la cual se validan, optimizan y depuran los sistemas de negociación algorítmica de nivel profesional. Su diseño de sesenta y cuatro bits, soporte multihilo nativo y capacidad de cómputo distribuido asíncrono permiten estructurar entornos de validación de alta fidelidad que minimizan el desfase operativo (*backtest slippage*) entre los entornos de simulación y la ejecución en producción real.

## **1\. Modos de modelado de ticks y fidelidad de datos**

La reconstrucción del precio en el tiempo es el pilar de la validez de cualquier simulación histórica.1 El Strategy Tester de MetaTrader 5 implementa cuatro modos de modelado de ticks estructurados para equilibrar la fidelidad matemática, el tiempo de procesamiento y el consumo de recursos de hardware.1

### **Cada tick basado en ticks reales (Every tick based on real ticks)**

Este modo representa el estándar de máxima fidelidad en la simulación histórica, utilizando los registros históricos de ticks provistos directamente por el servidor de operaciones de la casa de corretaje (*broker*).1 Estos datos corresponden a transacciones de mercado y cotizaciones de proveedores de liquidez institucionales.1

* **Disponibilidad del bróker:** Casas de corretaje orientadas al corretaje de acceso directo al mercado (DMA) o con spreads de tipo ECN (como LMAX, Pepperstone, IC Markets, RoboForex o Dukascopy) proveen historiales completos de ticks reales para activos de divisas, índices y contratos por diferencia.1 Si un intermediario no cuenta con registros de ticks reales para un activo o período específico, el motor de pruebas conmuta de manera automática al modo de emulación sintética de "Cada tick".2  
* **Procedimiento de descarga:** Para realizar la descarga preliminar del historial y evitar latencias de red durante el backtest, se utiliza la ventana de Símbolos (Ctrl+U), seleccionando la pestaña de *Ticks*, definiendo el activo y el rango temporal exacto, y presionando el botón *Solicitar*.4 Los datos descargados se integran directamente en la base de datos local de la terminal.2  
* **Sincronización con Barras de 1 Minuto (M1):** El simulador valida sistemáticamente los ticks reales frente a las barras M1 consolidadas para garantizar la consistencia matemática.5 Los ticks de cada minuto deben coincidir con los precios Open, High, Low y Close de la vela M1 correspondiente, así como con el volumen reportado.5 Si se detecta cualquier discrepancia física o incoherencia en el volumen, el Strategy Tester descarta la base de datos de ticks reales para ese minuto y recurre a la generación sintética basada en el algoritmo de "Cada tick".5  
* **Mecanismo de Caché y Acceso a Datos de Ticks:** El Strategy Tester almacena los ticks activos de la simulación en un búfer de memoria de acceso rápido limitado a un máximo de ![][image1] ticks en caché.2 Al superarse este límite, los datos antiguos se desplazan bajo un principio FIFO.2 No obstante, si el código MQL5 del robot de trading utiliza la función CopyTicks, el simulador realiza una consulta directa a la base de datos completa de ticks de la terminal, sorteando el caché para garantizar el acceso al historial íntegro.2

### **Cada tick (Every tick)**

Cuando los registros de ticks reales no están disponibles o se desea optimizar el uso del ancho de banda y almacenamiento, el motor genera cotizaciones sintéticas basadas en los datos de barras M1 de la terminal.1

* **Generación de Puntos de Control:** El motor desglosa cada barra M1 en un máximo de once puntos de control geométricos (excluyendo el precio de apertura) determinados por el volumen de ticks de la vela.1  
* **Trayectorias Lineales e Interpolación de Tipo Sierra:** Si el volumen de ticks de la vela es superior al número de puntos posibles entre dos referencias, se genera un patrón de oscilación constante de tipo "sierra" (con incrementos o decrementos unitarios de ![][image2] pip).1 Si el rango de pips entre los puntos de referencia es lo suficientemente amplio, el simulador genera progresiones lineales de ticks para rellenar la barra de forma uniforme.1 En este modo, el diferencial de precios (*spread*) permanece estático según el valor fijado en la barra M1 correspondiente, calculándose el precio Ask como:

![][image3]

### **OHLC de 1 minuto (1 minute OHLC)**

En este modo de simulación rápida, el Strategy Tester limita la generación de cotizaciones únicamente a los precios de apertura, máximo, mínimo y cierre (OHLC) de cada barra de un minuto.1

* **Velocidad de Cómputo:** Al descartar la simulación de cotizaciones intermedias, las llamadas a la función OnTick() se reducen estrictamente a cuatro por minuto, acelerando exponencialmente la velocidad del backtest.2  
* **El Sesgo del "Santo Grial" del Probador:** Al perderse la información del recorrido intra-barra (la secuencia temporal exacta entre el máximo y el mínimo de la vela M1), se genera un comportamiento determinista.2 Un algoritmo mal estructurado puede explotar este patrón comprando sistemáticamente en el precio mínimo simulado y vendiendo en el máximo.2 Esto genera curvas de balance artificialmente perfectas que colapsan en ejecución real, haciendo obligatoria la posterior validación en modo de ticks reales antes del despliegue en producción.2

### **Solo precios de apertura (Open prices only)**

Representa el modo operativo con mayor velocidad de ejecución del motor.1 La terminal genera una única llamada a la función OnTick() en el momento exacto en que se abre una nueva vela del período seleccionado para la simulación.1

* **Verificaciones de Fondo ("Hidden Ticks"):** A pesar de que la función OnTick() solo se ejecuta al abrirse la barra, el Strategy Tester simula de forma implícita el transcurso intra-vela para calcular los requerimientos de margen, procesar la ejecución o cancelación de órdenes pendientes por expiración, y activar órdenes de protección de tipo *Stop Loss* o *Take Profit*.2 Si la estrategia no tiene posiciones u órdenes activas, el motor desactiva estas rutinas secundarias, logrando un incremento masivo en la velocidad de optimización.2  
* **Excepciones para Períodos Semanales y Mensuales:** Para los períodos W1 (semanal) y MN1 (mensual), el motor genera ticks utilizando los precios OHLC de las barras diarias (D1) correspondientes, en lugar de utilizar directamente las aperturas semanales o mensuales, asegurando así un control preciso de la volatilidad intra-período.2

| Parámetro Comparativo | Cada tick basado en ticks reales | Cada tick (Sintético) | OHLC de 1 minuto | Solo precios de apertura |
| :---- | :---- | :---- | :---- | :---- |
| **Precisión Matemática** | Excelente (100% Real) 2 | Alta (Estimación geométrica) 2 | Media-Baja (4 puntos/vela) 1 | Mínima (1 punto/vela) 2 |
| **Consumo de Memoria RAM** | Muy Alto 2 | Moderado | Bajo 2 | Mínimo 2 |
| **Velocidad de Backtest** | Lenta 2 | Moderada-Lenta 2 | Rápida 2 | Ultra Rápida 2 |
| **Comportamiento del Spread** | Dinámico (Variable real) 1 | Estático por barra M1 1 | Estático por barra M1 1 | Estático por barra seleccionada |
| **Caso de Uso Óptimo** | Sistemas de Scalping, HFT, Arbitraje y validación final.2 | Optimización general y robustez en ausencia de ticks reales.2 | Cribado inicial de parámetros en carteras extensas de divisas.2 | Validación estructural de lógica y sistemas basados en velas cerradas.2 |
| **Limitaciones Estrictas** | Dependencia de la conexión de red del bróker.1 | Puede obviar micropatrones de volatilidad real. | Sesgo de determinismo intra-vela ("Santo Grial" artificial).2 | Incompatible con el modo de retraso aleatorio de ejecución.1 |

## **2\. El modo visual de pruebas y depuración de estrategias**

El Strategy Tester incorpora una terminal gráfica de simulación independiente que permite analizar dinámicamente el comportamiento operativo del robot de trading en tiempo real simulado.7

### **Control Dinámico de la Simulación**

El operador dispone de una barra deslizante para graduar la velocidad del backtest visual.7 Al ajustar este control, se varía el intervalo de milisegundos entre el procesamiento de cada tick en la interfaz gráfica. El sistema permite pausar la ejecución en cualquier instante presionando la tecla Espacio o el botón correspondiente, y avanzar de forma secuencial vela a vela o tick a tick mediante la opción de paso único, lo cual resulta indispensable para analizar eventos críticos como la gestión de márgenes y ejecuciones parciales.7  
Para incorporar indicadores técnicos sobre el gráfico visual existen dos metodologías estructuradas:

1. **Carga mediante Plantillas (Templates):** Si en el directorio /profiles/templates de la plataforma se guarda un archivo con el formato \[Nombre\_del\_EA\].tpl, el entorno de simulación visual aplicará automáticamente todos los indicadores, colores y objetos de dibujo contenidos en esa plantilla al iniciar la prueba.7  
2. **Invocación en Código:** La ejecución de funciones de tipo iCustom o indicadores nativos dentro del código fuente del robot fuerza de manera automática su inserción en el gráfico del Strategy Tester visual.10

### **El Comportamiento de los Objetos Gráficos**

Existe una divergencia crítica en el comportamiento del Strategy Tester según el modo visual seleccionado.9 En el modo no visual (el cual se emplea durante la optimización genérica para maximizar la velocidad), el Strategy Tester desactiva por completo el procesamiento y la asignación de recursos a los objetos gráficos.9 Las llamadas a la función ObjectCreate se ignoran o retornan identificadores de error, y cualquier llamada para consultar propiedades de un objeto (ObjectGetDouble, ObjectGetInteger) devolverá valores nulos o erróneos.9  
Si la lógica operativa de un robot depende estructuralmente de las propiedades físicas de objetos gráficos (como líneas de tendencia o canales dinámicos), el sistema fallará o arrojará resultados incoherentes en las pruebas automáticas no visuales.9 Por lo tanto, el código cuantitativo debe estar desacoplado de la interfaz gráfica, procesando la lógica numérica mediante arreglos en memoria o estructuras de datos abstractas.

### **Depuración Histórica y Perfilado (Profiling)**

La integración entre el MetaEditor y el Strategy Tester permite ejecutar tareas de depuración en datos históricos mediante la combinación de teclas Ctrl \+ F5.12 El compilador genera un binario temporal que conserva la tabla de símbolos de depuración y las referencias a las líneas de código fuente.12 Al establecer puntos de interrupción (*breakpoints*) en secciones sensibles del archivo .mq5, el simulador pausará su ejecución en el tick exacto donde se cumpla la condición de parada, permitiendo al desarrollador inspeccionar el estado de las variables globales y locales.12  
Complementariamente, el proceso de perfilado de código sobre datos históricos (Profiling) analiza la ejecución del programa a una tasa de muestreo de hasta 10,000 veces por segundo.13 El compilador evalúa el tiempo relativo consumido por cada función y subrutina matemática en el ciclo de ejecución de la simulación, identificando cuellos de botella de rendimiento de manera rápida.12

## **3\. Arquitectura del motor de optimización**

Para identificar las combinaciones más robustas de variables de entrada, MetaTrader 5 incorpora un motor de optimización matemática multihilo altamente parametrizable.15

### **Algoritmo Completo Lento (Slow Complete Algorithm)**

Este procedimiento ejecuta una búsqueda exhaustiva en cuadrícula (*grid search*) sobre todo el espacio de parámetros seleccionado.15 Garantiza la localización exacta del óptimo global dentro de los límites establecidos, pero su coste computacional crece exponencialmente con la dimensionalidad de las variables, requiriendo en ocasiones años de procesamiento para un solo activo.15

### **Algoritmo Genético Rápido (Fast Genetic Based Algorithm)**

El algoritmo genético de MetaTrader 5 está diseñado para resolver problemas de optimización en espacios de búsqueda masivos, reduciendo drásticamente el número total de ejecuciones.15 Se activa de forma automática si la cardinalidad del espacio de búsqueda excede un umbral predefinido de un millón de iteraciones en arquitecturas de 32 bits, o cien millones en arquitecturas de 64 bits.15  
Su funcionamiento interno se modela según la teoría evolutiva clásica 15:

1. **Población Inicial:** El sistema genera aleatoriamente una población de individuos (conjuntos de parámetros de entrada) estructurada en cromosomas, donde cada gen representa una variable específica.15 El tamaño habitual de la población oscila entre 64 y 256 individuos.15  
2. **Evaluación de la Aptitud (Fitness):** Cada individuo es sometido a un proceso de simulación histórica individual.15 Al finalizar, se calcula la puntuación del criterio de optimización seleccionado (por ejemplo, Sharpe Ratio o el Criterio Complejo).15  
3. **Selección:** El motor compara los resultados y selecciona a los individuos más aptos para formar la base de la siguiente generación, descartando las combinaciones que arrojaron rendimientos deficientes.15  
4. **Cruzamiento (Crossover):** Los miembros de la población seleccionada se cruzan de forma aleatoria intercambiando sus genes para dar origen a descendientes híbridos.15  
5. **Mutación e Inversión:** Para evitar la homogeneización del código genético, el sistema introduce de manera estocástica variaciones imprevistas en los valores de los genes (mutaciones) y altera el orden de los mismos dentro del cromosoma.15  
6. **Criterio de Convergencia:** El proceso se repite generación tras generación.15 La estimación de parada se calcula basándose en la falta de mejoras significativas en el resultado del criterio de optimización durante un número consecutivo de generaciones.15 El total estimado de ejecuciones responde a la fórmula matemática 15:

![][image4]  
Donde ![][image5] es el tamaño predefinido de la población, ![][image6] es el número incondicional de generaciones (típicamente entre 15 y 31\) y ![][image7] representa las generaciones adicionales requeridas para validar la convergencia (equivalente a exactamente un tercio de las generaciones incondicionales previas sin variaciones positivas).15  
A lo largo del proceso, MetaTrader 5 guarda de forma continua los datos de cada generación en archivos de caché estructurados con la extensión .gen.15 En caso de interrupción del sistema por fallos eléctricos o del sistema operativo, el Strategy Tester retomará el proceso desde la última generación calculada.15

### **Todos los símbolos seleccionados en Observación de Mercado (Market Watch)**

Este modo ejecuta la simulación histórica de forma secuencial utilizando exactamente el mismo conjunto de parámetros de entrada fijos, pero variando iterativamente el activo principal de la prueba sobre toda la selección de instrumentos activos en la ventana de *Market Watch* de la terminal.15 Esto resulta indispensable para evaluar la robustez intrínseca de una estrategia multi-activo y verificar si su ventaja matemática es de naturaleza estructural u puramente circunstancial de un mercado específico.15 Como limitación técnica crítica, este modo operativo **no cuenta con soporte** de ejecución dentro de la red descentralizada MQL5 Cloud Network.15

### **Mitigación de Óptimos Locales y Convergencia Prematura**

El principal desafío matemático del algoritmo genético es la convergencia prematura.18 Esto ocurre cuando la población se homogeneiza rápidamente en torno a un óptimo local subóptimo, perdiendo la diversidad necesaria para explorar regiones más prometedoras del espacio de búsqueda.18 Para mitigar este efecto, se sugieren las siguientes técnicas avanzadas:

* **Ampliación Estructural de la Población:** Configurar poblaciones iniciales amplias (entre 200 y 250 individuos) incrementa significativamente la diversidad de la muestra inicial, reduciendo la probabilidad de que un óptimo local inicial domine rápidamente el acervo génico.20  
* **Ajuste de la Tasa de Mutación:** Incrementar la probabilidad de mutación estocástica actúa como un mecanismo de fuerza bruta para escapar de las cuencas de atracción locales.18 Al mutar un gen con mayor frecuencia, se introducen puntos aleatorios distantes en el espacio de parámetros, reiniciando la exploración heurística.18  
* **Hibridación Exógena:** Implementar optimizaciones sucesivas fijando subconjuntos de variables o combinando el algoritmo con optimizadores externos mediante APIs (como Particle Swarm Optimization \- PSO o librerías de Python como PyTorch) permite explotar la potencia de búsqueda global antes de refinar los parámetros de gestión monetaria dentro de MetaTrader.19  
* **Diseño de Criterios Complejos Robustos:** Utilizar funciones de aptitud multi-objeto personalizadas a través de OnTester() desalienta la selección de sistemas con curvas de balance artificiales o ajustadas a un único parámetro lineal de ganancia.20

## **4\. Configuración y análisis del Forward Testing automático**

Para blindar las estrategias algorítmicas frente al sobreajuste, el Strategy Tester de MetaTrader 5 incorpora un motor automatizado de pruebas fuera de muestra (*Forward Testing*).23  
Este sistema automatiza la división matemática del intervalo temporal de prueba en dos segmentos diferenciados 23:

1. **Periodo In-Sample (De Optimización):** Corresponde a la sección del historial sobre la cual el algoritmo genético realiza las pruebas de aptitud y ajusta los parámetros de entrada.23  
2. **Periodo Out-of-Sample (Forward):** Representa una muestra de datos históricos ciega para el optimizador.23 Tras completar las simulaciones en la muestra inicial, el motor toma de forma automática una fracción de los mejores resultados de cada generación y ejecuta pruebas individuales en el periodo Forward sin alterar sus parámetros.23

La proporción del periodo Forward puede parametrizarse en fracciones predefinidas: un medio (1/2), un tercio (1/3), un cuarto (1/4) del rango total de datos, o mediante la especificación de una fecha límite personalizada.23

Rango Total de Datos Históricos  
├─────────────────────────────────────────────────────────────────────────────┤  
│                    In-Sample (Optimización)           │   Forward (Ciego)   │  
│◄───────────────────────── 75% ───────────────────────►│◄────── 25% ────────►│

### **Identificación de Sobreajuste y Robustez**

El análisis comparativo de los resultados obtenidos en ambas fases es la métrica de robustez del sistema:

* **Estrategia Sobreajustada:** Presenta métricas excepcionales durante el periodo de optimización in-sample (como altos factores de beneficio y curvas de balance lineales), pero sufre un colapso en la muestra Forward externa, evidenciando una pérdida de consistencia debida a que el modelo ha memorizado el ruido histórico en lugar de aprender patrones de mercado explotables.4  
* **Estrategia Robusta:** Consigue mantener la estabilidad y un perfil de rendimiento proporcionalmente consistente tanto en la muestra interna como en la externa, demostrando inmunidad relativa frente a los cambios de volatilidad o microestructura del mercado.

## **5\. Distribución de carga: Arquitectura de agentes de ejecución**

La velocidad de cómputo del Strategy Tester se fundamenta en su arquitectura de ejecución distribuida en paralelo, gobernada por agentes de simulación independientes.16

### **Agentes Locales**

Son hilos de ejecución que corren de forma nativa en el procesador de la máquina local.25 Por defecto, la plataforma genera de manera automática un agente por cada núcleo lógico o procesador virtual (incluyendo hilos de hiperprocesamiento o Hyper-Threading) del sistema.25 Estos agentes se inician sin interfaz de usuario directamente bajo demanda de la terminal principal.25

### **Agentes Remotos**

Permiten la creación de granjas de cálculo locales utilizando la infraestructura de hardware distribuida en una red de área local (LAN).25

* **Instalación:** Se despliegan de forma independiente utilizando el componente MetaTester.exe.25  
* **Comunicaciones y Puertos:** Cada agente asignado a un procesador abre un puerto TCP específico (comenzando por el puerto por defecto 2000, e incrementándose secuencialmente por cada núcleo adicional, p. ej., 2001, 2002\) para escuchar las conexiones entrantes de la terminal administradora.25  
* **Seguridad:** Las conexiones se protegen mediante contraseñas cifradas obligatorias para restringir el acceso a usuarios no autorizados de la red local.25 Si se requiere acceder a agentes remotos a través de cortafuegos o routers de Internet, es necesario realizar una reconfiguración estática de puertos (*port-forwarding*) en el enrutador para dirigir el tráfico de los puertos TCP correspondientes (del rango 2000 al 2007, por ejemplo) hacia la dirección IP privada del servidor correspondiente.25 Como los puertos de escucha operan bajo IP locales independientes, múltiples máquinas en la misma LAN pueden duplicar los rangos de puertos sin generar colisiones de red.28

### **MQL5 Cloud Network**

Es una red de cómputo global, descentralizada y remunerada, compuesta por miles de agentes de usuarios de la comunidad MQL5 a nivel mundial.26

* **Protocolo de Conectividad:** A diferencia de los agentes remotos tradicionales, los agentes conectados a la red MQL5 Cloud no requieren configuraciones de puertos complejes ni direccionamiento IP estático entrante.28 Todos los agentes de la nube establecen conexiones salientes seguras mediante el protocolo SSL/TLS a través del puerto estándar 443 (HTTPS) hacia los servidores de gestión de tareas (*Network Poolers*) geográficamente más cercanos.28 Esto permite esquivar de forma automática cortafuegos y proxies locales.28  
* **Optimización de Rendimiento:** El administrador de la terminal principal distribuye de manera balanceada los paquetes de simulación histórica a los poolers de la red de la nube, minimizando el tiempo muerto de los procesadores locales. La red de la nube no da soporte al modo de optimización multi-símbolo ("All symbols selected in Market Watch") debido a las restricciones de tamaño de los conjuntos de datos de múltiples activos en agentes distribuidos.15

## **6\. Modelado de criterios de optimización**

El Strategy Tester evalúa la viabilidad de un conjunto de parámetros basándose en un único valor escalar resultante de la simulación, denominado criterio de optimización.15

### **Criterios Nativos de Evaluación**

* **Maximum Balance:** Selecciona las combinaciones basándose puramente en la ganancia absoluta final, lo que suele favorecer sistemas con alto apalancamiento y riesgo de ruina elevado.15  
* **Maximum Profit Factor:** Prioriza la relación entre el beneficio bruto y la pérdida bruta. Si la pérdida bruta es cero, el valor resultante se establece en el límite superior matemático DBL\_MAX.15  
* **Maximum Expected Payoff:** Mide la expectativa matemática de beneficio neto esperada para cada transacción individual.15  
* **Minimum Drawdown:** Se enfoca en minimizar la pérdida máxima de saldo registrada en términos porcentuales durante el transcurso de la prueba.15  
* **Maximum Sharpe Ratio:** Evalúa el retorno ajustado al riesgo del sistema de negociación, midiendo la consistencia de la curva de rendimientos frente a su volatilidad.15  
* **Maximum Recovery Factor:** Mide la velocidad de recuperación del capital tras experimentar pérdidas severas, calculándose como la relación matemática entre el beneficio neto total y la reducción máxima del saldo absoluto de la cuenta.15  
* **Complex Criterion Max:** Es una métrica compuesta desarrollada por MetaQuotes que evalúa simultáneamente el número total de transacciones ejecutadas, el factor de recuperación, la expectativa matemática de ganancias y el Sharpe Ratio para seleccionar sistemas estables.15

### **Desarrollo de Criterios Personalizados mediante OnTester()**

Para sortear las limitaciones de las métricas de rendimiento tradicionales, el desarrollador cuantitativo puede programar una función matemática de evaluación de objetivos múltiples utilizando el manejador de eventos OnTester().15 Esta función debe devolver un valor numérico de tipo double.22 El optimizador genético organizará la jerarquía evolutiva de forma descendente, clasificando los valores más altos devueltos por OnTester() como las combinaciones óptimas de la generación.22  
El uso de criterios personalizados resulta de gran utilidad para penalizar estadísticamente a los sistemas que ejecutan un número de transacciones insuficiente (lo que reduce la significación estadística de la prueba) o que presentan caídas de saldo (*drawdowns*) inaceptables para el gestor de riesgos de la cuenta.21

## **7\. Funciones avanzadas de control y procesamiento asíncrono (Frames API)**

En optimizaciones a gran escala con miles de pases individuales ejecutándose en procesadores remotos o en la nube, la transferencia ininterrumpida y centralizada de estadísticas representa un cuello de botella de rendimiento de primer orden.32 Para resolver este problema de sincronización de datos, MetaTrader 5 incorpora la arquitectura de comunicación por tramas de datos (*Frames*).32

### **Eventos de Control de Optimización y Flujo de Trabajo**

El flujo de procesamiento distribuido se orquesta a través de tres manejadores de eventos especializados 32:

* **OnTesterInit:** Se ejecuta una única vez en la terminal local antes del inicio del primer pase de optimización.32 En este evento, la terminal crea de forma automática un gráfico oculto en segundo plano bajo el modo de servicio de tramas (MQL\_FRAME\_MODE), donde se monta una instancia de supervisión del EA que no ejecuta transacciones y solo responde a tareas de administración y recepción de datos.32 Aquí se suelen inicializar archivos de salida o ajustar dinámicamente los rangos de optimización con ParameterSetRange.32  
* **OnTesterPass:** Se genera de manera asíncrona en la terminal local cada vez que un agente remoto finaliza un pase de optimización individual y envía una trama de datos personalizada mediante la función FrameAdd.32 Este evento permite actualizar interfaces dinámicas en vivo o procesar flujos continuos de datos históricos de operaciones.32  
* **OnTesterDeinit:** Se activa una vez que todas las combinaciones programadas en la cuadrícula o en el optimizador genético han concluido su ejecución.32 Se destina a tareas finales de consolidación, cierre de archivos de persistencia local y ordenamiento final de tramas mediante algoritmos complejos de filtrado.32

### **Protocolo de Comunicación Mediante Tramas (Frames API)**

Para gestionar las tramas de datos, MetaTrader 5 proporciona un conjunto de funciones de bajo nivel que operan con un puntero interno de lectura asíncrona 36:

* **FrameAdd:** Se invoca exclusivamente dentro de la función OnTester() del agente remoto.32 Permite empaquetar y despachar un bloque estructurado de memoria (ya sea un arreglo de tipo simple, una estructura serializada o un archivo binario completo generado en el entorno aislado del agente) acompañado de etiquetas de identificación numéricas y de texto (id y name).32  
* **FrameFirst:** Restablece de forma estática el puntero de lectura de tramas al inicio de la colección almacenada en el archivo interno .mqd de la terminal, desactivando los filtros dinámicos previos.36  
* **FrameFilter:** Restringe de forma selectiva la lectura de tramas a un identificador numérico o etiqueta textual específica, reposicionando el puntero al inicio de la subcolección resultante.36  
* **FrameNext:** Extrae la información de la trama apuntada actualmente y desplaza el puntero de manera secuencial hacia el siguiente elemento disponible.36 Esta función recupera el número del pase de optimización correspondiente, la información escalar y el bloque de datos binarios de la trama.36 Si el bloque de datos recibido es un archivo ANSI o Unicode, debe transformarse apropiadamente empleando funciones de conversión de tipos como CharArrayToString o ShortArrayToString.36  
* **FrameInputs:** Recupera el conjunto exacto de parámetros de entrada y sus respectivos valores numéricos con los cuales se generó el pase de optimización referenciado, facilitando el análisis inverso del modelo.36

Dada la asincronía en las comunicaciones por red, las tramas de datos pueden transmitirse agrupadas en ráfagas desde los agentes, llegando con un desfase temporal con respecto a la finalización de los pases en el motor del Strategy Tester.32 Es una regla fundamental de arquitectura cuantitativa estructurar un bucle de lectura secuencial que limpie los "marcos de datos pendientes" tanto en OnTesterPass como al final de OnTesterDeinit utilizando la función FrameNext.32

## **8\. Extracción y análisis de métricas de rendimiento (Tester DB)**

El análisis cuantitativo avanzado de los resultados de una simulación exige acceder de forma precisa a un amplio espectro de variables de rendimiento y riesgo financiero.

### **Consulta de Métricas de Rendimiento mediante TesterStatistics**

A través de la función nativa TesterStatistics(), el desarrollador puede extraer métricas específicas al cierre de cada simulación individual.30 Esta función requiere un argumento identificativo procedente de la enumeración estructurada ENUM\_STATISTICS.30

| Identificador de Parámetro | Tipo de Dato | Descripción Cuantitativa de la Métrica |
| :---- | :---- | :---- |
| STAT\_INITIAL\_DEPOSIT | double | Depósito inicial simulado en la divisa de cuenta establecida.30 |
| STAT\_WITHDRAWAL | double | Monto acumulativo de retiros de capital efectuados durante la simulación.30 |
| STAT\_PROFIT | double | Beneficio o pérdida neta absoluta registrada al final del período de prueba.30 |
| STAT\_GROSS\_PROFIT | double | Suma absoluta de todas las transacciones con rendimiento positivo.30 |
| STAT\_GROSS\_LOSS | double | Suma absoluta de todas las transacciones con rendimiento negativo.30 |
| STAT\_MAX\_PROFITTRADE | double | Rendimiento máximo positivo obtenido en una única transacción.30 |
| STAT\_MAX\_LOSSTRADE | double | Rendimiento mínimo negativo (pérdida máxima) obtenido en una única transacción.30 |
| STAT\_BALANCEMIN | double | Nivel mínimo absoluto alcanzado por el saldo de la cuenta.30 |
| STAT\_BALANCE\_DD | double | Descenso máximo absoluto del saldo respecto a su pico previo (*balance drawdown*).30 |
| STAT\_EQUITYMIN | double | Nivel mínimo absoluto de liquidez flotante (*equity*) registrado.30 |
| STAT\_EQUITY\_DD | double | Caída de liquidez máxima en términos monetarios acumulados.30 |
| STAT\_EQUITY\_DDREL\_PERCENT | double | Reducción máxima del valor de liquidación de la cuenta (*equity drawdown*) expresada en porcentaje.30 |
| STAT\_PROFIT\_FACTOR | double | Relación matemática de rentabilidad total (![][image8]).30 |
| STAT\_EXPECTED\_PAYOFF | double | Expectativa matemática de ganancias promedio por cada transacción individual.30 |
| STAT\_SHARPE\_RATIO | double | Coeficiente ajustado al riesgo del rendimiento neto promedio de la estrategia.30 |
| STAT\_RECOVERY\_FACTOR | double | Factor de recuperación absoluta de pérdidas frente al retroceso de capital máximo de saldo.30 |
| STAT\_MIN\_MARGINLEVEL | double | Nivel de margen porcentual mínimo registrado durante el transcurso de la prueba.30 |
| STAT\_TRADES | int | Número total de operaciones cerradas y liquidadas de la cuenta.30 |

Esta función solo devuelve valores coherentes cuando es invocada dentro de las rutinas de cierre OnTester() u OnDeinit() ejecutadas de forma nativa en el entorno de simulación; en cualquier otro contexto de ejecución, su resultado matemático es indefinido.30

### **Seguimiento Dinámico de la Curva de Balance y Equidad**

Durante el transcurso de la simulación histórica, MetaTrader 5 no proporciona un método estructurado directo de acceso en tiempo real a arreglos dinámicos que representen la curva de equidad paso a paso. Para realizar análisis estadísticos avanzados o implementar estrategias de gestión de capital basadas en la pendiente de la curva de balance, el desarrollador cuantitativo debe estructurar una de las siguientes soluciones de ingeniería 40:

1. **Mecanismo de Balance Virtual:** Mantener variables globales e internas dentro del handler OnTick() o en el procesamiento de transacciones OnTradeTransaction() que capturen la evolución del saldo neto.2 Cada vez que se liquida una transacción, se almacena el estado actual de la equidad en un array dinámico estructurado en memoria para calcular medias móviles del balance u otras métricas de control de riesgo operativo.40  
2. **Volcado Dinámico de Archivos:** Escribir periódicamente en archivos binarios o de texto en formato CSV dentro de la carpeta local aislada del probador (MQL5/Files) los pares de datos temporales (fecha/hora y saldo de equidad) para su procesamiento asíncrono o visualización externa.40

## **9\. Limitaciones estructurales y diferencias del entorno de ejecución**

El Strategy Tester de MetaTrader 5 proporciona un entorno de simulación altamente optimizado, pero presenta limitaciones de microestructura que impiden replicar con total exactitud la ejecución en vivo en los mercados reales.

### **Limitaciones de Ejecución y Microestructura**

* **Deslizamiento Real (Slippage):** El probador no puede recrear el deslizamiento de precios real causado por el agotamiento de la liquidez en las colas del libro de órdenes.24 Aunque se implementen los modos de retardo aleatorio de ejecución (*Random Delay*), la transacción se liquidará al precio del tick simulado actual, omitiendo el impacto real en el precio debido al volumen negociado y los tiempos de ida y vuelta de red (*RTT*).24  
* **Latencia Estructural de Red:** La simulación asume un procesamiento de transacciones instantáneo o con un desfase uniforme parametrizado, obviando la latencia dinámica propia de la red real durante fases de extrema volatilidad, donde las colas de órdenes del bróker sufren demoras severas.24  
* **Ejecución Parcial e Impacto de Mercado:** El Strategy Tester asume por defecto una liquidez infinita al precio de cotización simulado. No modela el llenado parcial de órdenes de volumen institucional ni el consecuente impacto de mercado (el desplazamiento del Bid/Ask debido a la propia actividad de negociación del robot de trading).  
* **Spread Variable Exógeno:** Aunque el modo de "Cada tick basado en ticks reales" incluye el spread real registrado en el historial, carece de la capacidad de reproducir la apertura súbita e impredecible de los spreads que ocurre durante noticias macroeconómicas de alto impacto debido a la retirada preventiva de los creadores de mercado en cuentas en tiempo real.1

### **Divergencias Operativas en Funciones MQL5**

Ciertas funciones del lenguaje MQL5 modifican drásticamente su comportamiento operativo normal cuando son llamadas dentro del entorno del Strategy Tester:

* **Sleep():** En cuentas reales, suspende de forma física el hilo de ejecución del programa durante un intervalo de tiempo de milisegundos indicado.43 En el Strategy Tester, la función Sleep() no detiene el proceso de simulación física del motor.8 En su lugar, el simulador avanza automáticamente el tiempo histórico por el período especificado en el parámetro, reproduciendo de forma inmediata todos los ticks intermedios que habrían ocurrido en ese intervalo y ejecutando de forma instantánea cualquier orden de detención o pendientes que hubiesen sido tocadas durante el avance rápido del reloj.44  
* **WebRequest():** Esta función está estrictamente deshabilitada en el Strategy Tester por razones de arquitectura distribuida y para evitar ataques masivos de denegación de servicio (*DDoS*) accidentales sobre servidores web.45 Cualquier llamada retornará un identificador de error 4014 (función no permitida en simulación).45 Para mitigar esta restricción en el desarrollo de modelos de aprendizaje automático o algoritmos dependientes de datos exógenos (como calendarios de noticias), el desarrollador debe recurrir a la lectura de bases de datos o archivos CSV guardados de forma estática antes del backtest en la carpeta local, o bien emplear librerías dinámicas DLL de C++ que canalicen las llamadas REST HTTP fuera de la terminal de pruebas.46  
* **SendNotification() y SendMail():** Se desactivan silenciosamente de forma nativa en el Strategy Tester para evitar spam masivo de notificaciones móviles durante las optimizaciones masivas de parámetros.  
* **Sincronización del Reloj:** Las funciones de tiempo TimeLocal(), TimeTradeServer() y TimeGMT() devuelven exactamente el mismo valor temporal del reloj histórico simulado del tick que se está procesando actualmente, eliminando el cálculo de husos horarios locales y forzando una coincidencia artificial de tiempos.44  
* **MQLInfoInteger(MQL\_FRAME\_MODE):** Retorna de forma lógica true únicamente si la instancia actual del EA está operando de forma activa como el manejador supervisor local de tramas de datos dentro de la terminal administradora durante el proceso de optimización, ayudando a discriminar y aislar el código operacional del código puramente organizativo.32

## **10\. Estructuración y automatización de reportes del tester**

El análisis científico de las simulaciones requiere la estructuración estandarizada y exportación automatizada de las métricas obtenidas.

### **Formato de Reportes HTML y PDF**

La terminal proporciona un motor de generación de reportes avanzados que estructura la información de rendimiento y riesgo en gráficos e informes detallados.13 Estos incluyen la curva acumulada de balance y equidad, histogramas detallados sobre la distribución horaria e instrumentación de las operaciones ejecutadas, y diagramas de correlación de tiempos de retención.13 Los reportes detallados pueden salvarse manualmente haciendo clic derecho en la pestaña "Historial" del panel del Strategy Tester y seleccionando "Guardar como reporte detallado".50

### **Automatización y Ejecución desde la Línea de Comandos**

Para flujos de trabajo cuantitativos industriales, MetaTrader 5 permite la automatización total del proceso de pruebas mediante su ejecución silenciosa desde la consola del sistema operativo empleando archivos de configuración de inicialización estática .ini.23  
Para ejecutar el Strategy Tester de forma automatizada, se utiliza la siguiente instrucción de comandos:

Bash  
terminal64.exe /config:C:\\Metatrader\\config\_opt.ini

La estructura fundamental y sintaxis paramétrica del archivo de inicialización config\_opt.ini se detalla a continuación 23:

Ini, TOML  
\[Common\]  
Login\=100000                   ; Cuenta operativa simulada   
ProxyEnable\=0                  ; Deshabilitación de proxy de red

Expert\=Advisors\\EACuantitativo.ex5  ; Ruta relativa del robot de trading   
ExpertParameters\=EACuantitativo.set ; Configuración de parámetros de entrada   
Symbol\=EURUSD                       ; Activo de referencia para la simulación   
Period\=H1                           ; Marco temporal de ejecución   
Model\=4                             ; Modelo de ticks (4 \= Cada tick basado en ticks reales)   
ExecutionMode\=0                     ; Modo de ejecución comercial (0 \= Normal, \-1 \= Delay aleatorio)   
FromDate\=2025.01.01                 ; Fecha de inicio del backtest   
ToDate\=2026.01.01                   ; Fecha de finalización del backtest   
Optimization\=2                      ; Tipo de optimización (2 \= Algoritmo genético rápido)   
OptimizationCriterion\=6             ; Criterio de optimización (6 \= Criterio personalizado OnTester) \[15, 30\]  
ForwardMode\=2                       ; Configuración del Forward (2 \= Un tercio del rango)   
Report\=Informes\\ReporteEA           ; Ruta de exportación del reporte estructurado

Al concluir el backtest o la optimización masiva de forma automatizada, el Strategy Tester generará de manera autónoma el informe en formato HTML o XML en la ruta indicada bajo la variable Report, facilitando su importación directa por sistemas externos de análisis de carteras o plataformas integradas en Python.23

## **11\. Guías paso a paso de configuración y desarrollo**

### **Configuración para Backtest de "Cada tick basado en ticks reales"**

Para realizar una simulación histórica con la máxima fidelidad de precios y spreads reales disponibles, se deben seguir estos pasos estructurados en la interfaz de la plataforma:

1. **Apertura de la Herramienta:** En la barra de menú superior de la terminal MetaTrader 5, seleccionar Ver \-\> Strategy Tester o presionar la combinación de teclas Ctrl \+ R.  
2. **Selección del Programa:** En el panel de configuración inicial, hacer clic en el botón Configurar y seleccionar el Robot de Negociación .ex5 deseado.23  
3. **Configuración del Instrumento y Marco Temporal:**  
   * En el campo Símbolo, seleccionar el activo financiero de interés (p. ej., XAUUSD).  
   * En el campo Temporalidad, seleccionar el marco temporal de trabajo de la estrategia (p. ej., H1).23  
4. **Descarga Previa de Datos de Ticks Reales:**  
   * Presionar la combinación de teclas Ctrl \+ U para abrir el panel de gestión de símbolos.  
   * Seleccionar el activo de interés, hacer clic en la pestaña Ticks e indicar el rango de fechas exacto requerido.4  
   * Hacer clic en el botón Solicitar.4 Esto fuerza a la terminal a descargar el historial completo de ticks reales directamente desde el servidor del bróker a la base de datos local antes de iniciar la prueba, mitigando retardos iniciales de red durante la simulación.4  
5. **Configuración del Probador:**  
   * En el desplegable de Modelado, seleccionar estrictamente la opción Cada tick basado en ticks reales.1  
   * En el campo Intervalo, seleccionar la opción de fechas personalizadas e indicar el inicio y final de la prueba.  
   * En Depósito, ingresar la cantidad nominal inicial y la divisa de cuenta de pruebas.  
   * En el campo de Retraso, simular las condiciones de red reales seleccionando un retraso representativo de ejecución (p. ej., 5 ms o Retraso aleatorio para pruebas de estrés).23  
6. **Desactivación de Optimización:** Asegurarse de que el interruptor de Optimización esté apagado para ejecutar un único pase de prueba visual o no visual.7  
7. **Ejecución:** Hacer clic en el botón Empezar en la esquina inferior derecha para iniciar el proceso.52

### **Configuración para Optimización Genética con Forward Testing**

Para configurar un proceso de búsqueda inteligente de parámetros evolutivos combinado con pruebas cruzadas fuera de muestra, se debe aplicar el siguiente protocolo técnico:

1. **Activación de la Optimización:** En el panel de configuración principal del Strategy Tester, localizar el campo Optimización y seleccionar la opción Algoritmo genético rápido.15  
2. **Configuración del Rango Temporal e Intervalo Forward:**  
   * Establecer la fecha de inicio y de finalización de la simulación.  
   * En el campo Forward, seleccionar la proporción deseada para las pruebas ciegas fuera de muestra (se recomienda seleccionar 1/3 del rango total de fechas).23  
3. **Selección del Criterio de Selección Evolutiva:** En el campo Criterio de optimización, seleccionar Criterio personalizado max (OnTester) para guiar la evolución genética mediante la métrica estructurada cuantitativa propia definida en el código.21  
4. **Parámetros de Entrada de la Estrategia:**  
   * Hacer clic en la pestaña Parámetros de entrada en la parte superior del Strategy Tester.  
   * Marcar la casilla de selección ubicada a la izquierda de cada variable que se desea optimizar (p. ej., períodos de medias móviles, niveles de umbral del oscilador).  
   * Definir los valores de Inicio, Paso de incremento aritmético y valor de parada de búsqueda (Stop) para cada variable marcada.  
5. **Gestión de Agentes de Cómputo:**  
   * Hacer clic en la pestaña Agentes en la parte inferior del Strategy Tester.  
   * Hacer clic derecho sobre los agentes locales e habilitar todos los núcleos disponibles.25  
   * Hacer clic derecho sobre el nodo MQL5 Cloud Network para activar el uso de la red de nube si se requiere mayor velocidad de procesamiento.  
6. **Lanzamiento:** Volver a la pestaña principal de configuración y hacer clic en el botón Empezar.52

### **Código Completo de un EA que utiliza OnTester() para un Criterio Custom**

El siguiente programa fuente en MQL5 define un robot de trading de plantilla estructurado. Este incorpora una función OnTester() que combina dinámicamente tres métricas fundamentales de rendimiento: el beneficio absoluto, la reducción máxima de equidad y la significación estadística a través del volumen de operaciones ejecutadas.22  
El criterio de optimización personalizado personalizado se calcula mediante la siguiente expresión matemática:  
![][image9]  
Donde la penalización de muestra se aplica de forma estricta si el sistema ejecuta menos de 30 transacciones históricas.22

Fragmento de código  
//+------------------------------------------------------------------+  
//|                                              EACuantitativo.mq5  |  
//|                        Derechos de autor 2026, Ingeniero Cuant.  |  
//+------------------------------------------------------------------+  
\#property copyright "Derechos de autor 2026, Ingeniero Cuant."  
\#property link      "https://www.mql5.com"  
\#property version   "1.00"  
\#property strict

// Parámetros de Entrada para Optimización  
input double   InpLots             \= 0.1;       // Tamaño del lote operativo  
input int      InpMovingAverage    \= 14;        // Período del Filtro MA  
input int      InpStopLossPips     \= 30;        // Detención de pérdidas en pips

// Variables globales internas  
int            HandleIndicador;                 // Manejador del indicador técnico

//+------------------------------------------------------------------+  
//| Función de Inicialización del Robot de Negociación               |  
//+------------------------------------------------------------------+  
int OnInit()  
{  
   // Inicialización del indicador dinámico  
   HandleIndicador \= iMA(\_Symbol, \_Period, InpMovingAverage, 0, MODE\_SMA, PRICE\_CLOSE);  
   if(HandleIndicador \== INVALID\_HANDLE)  
   {  
      Print("Error crítico al inicializar el manejador iMA.");  
      return(INIT\_FAILED);  
   }  
   return(INIT\_SUCCEEDED);  
}

//+------------------------------------------------------------------+  
//| Función de Desinicialización del Robot                           |  
//+------------------------------------------------------------------+  
void OnDeinit(const int reason)  
{  
   // Liberación de recursos de memoria en el sistema  
   IndicatorRelease(HandleIndicador);   
}

//+------------------------------------------------------------------+  
//| Procesamiento de Eventos de cada Tick de Precios                 |  
//+------------------------------------------------------------------+  
void OnTick()  
{  
   // Lógica de negociación simplificada  
   // En esta plantilla, la estructura se centra en la función evaluadora OnTester  
}

//+------------------------------------------------------------------+  
//| Evaluador de Criterio de Optimización Personalizado              |  
//+------------------------------------------------------------------+  
double OnTester()  
{  
   // Extracción de métricas financieras del simulador  
   double beneficio\_neto   \= TesterStatistics(STAT\_PROFIT);            // Beneficio neto   
   double max\_drawdown\_pct \= TesterStatistics(STAT\_EQUITY\_DDREL\_PERCENT); // Drawdown de equidad %   
   double factor\_recup     \= TesterStatistics(STAT\_RECOVERY\_FACTOR);    // Factor de recuperación   
   int total\_operaciones   \= (int)TesterStatistics(STAT\_TRADES);        // Operaciones cerradas 

   // Validación inicial de división por cero y drawdowns nulos  
   if(max\_drawdown\_pct \<= 0.0)  
   {  
      max\_drawdown\_pct \= 0.01;   
   }

   // Cálculo de la penalización de muestra estadísticamente no significativa  
   // Se busca penalizar severamente los sistemas que tengan menos de 30 operaciones  
   double factor\_penalizacion \= 1.0;  
   if(total\_operaciones \< 30\)  
   {  
      factor\_penalizacion \= (double)total\_operaciones / 30.0;  
   }

   // Algoritmo matemático para evaluar la aptitud cuantitativa  
   // El resultado premia el beneficio neto alto y la velocidad de recuperación de pérdidas,  
   // mientras penaliza duramente las caídas de saldo elevadas y las muestras pequeñas de trades.  
   double valor\_criterio\_custom \= (beneficio\_neto \* factor\_recup) / (max\_drawdown\_pct \+ 1.0);  
   valor\_criterio\_custom \= valor\_criterio\_custom \* factor\_penalizacion;

   // Escritura en el registro de la terminal para control de pases  
   PrintFormat("Mapeo de Pase de Optimización \-\> Operaciones: %d, Beneficio: %.2f, DD: %.2f%%, Criterio: %.4f",  
               total\_operaciones, beneficio\_neto, max\_drawdown\_pct, valor\_criterio\_custom);

   // Retorno del escalar double que el Strategy Tester organizará de forma descendente   
   return(valor\_criterio\_custom);  
}

## **11\. Arquitectura de adquisición asíncrona de tramas (Manejo de Frames)**

El siguiente script ilustra la implementación avanzada del manejo de tramas de datos dentro del EA Supervisor de la terminal local.32 El EA "maestro" captura dinámicamente cada trama de datos generada de forma remota, permitiendo escribir un archivo de consolidación consolidado libre de colisiones de lectura.32

Fragmento de código  
//+------------------------------------------------------------------+  
//|                                             SupervisorFrames.mq5 |  
//|                        Derechos de autor 2026, Ingeniero Cuant.  |  
//+------------------------------------------------------------------+  
\#property copyright "Derechos de autor 2026, Ingeniero Cuant."  
\#property link      "https://www.mql5.com"  
\#property version   "1.00"  
\#property strict

// Identificadores de tramas  
\#define FRAME\_METRIC\_ID 1001

// Estructura de métricas empaquetadas enviada por los agentes  
struct TramaDatos  
{  
   ulong  NumeroPase;  
   double Rentabilidad;  
   double RatioSharpe;  
   char   NombreSimbolo;  
};

//+------------------------------------------------------------------+  
//| Evento ejecutado antes de iniciar la optimización                 |  
//+------------------------------------------------------------------+  
int OnTesterInit()  
{  
   Print("Inicializando el gestor supervisor de tramas de optimización.");  
   // Creación o reseteo de archivos consolidados locales  
   int handle \= FileOpen("Consolidado\_Opt.csv", FILE\_WRITE|FILE\_CSV|FILE\_ANSI);  
   if(handle\!= INVALID\_HANDLE)  
   {  
      FileWrite(handle, "Pase", "Rentabilidad", "Sharpe", "Activo");  
      FileClose(handle);  
   }  
   return(INIT\_SUCCEEDED);  
}

//+------------------------------------------------------------------+  
//| Evento ejecutado de forma asíncrona al recibir una nueva trama    |  
//+------------------------------------------------------------------+  
void OnTesterPass()  
{  
   ulong  pass\_id;  
   string name;  
   ulong  frame\_id;  
   double value;  
   TramaDatos datos;

   // Procesamiento de tramas en lote para evitar cuellos de botella  
   // FrameNext extrae la información de la trama apuntada actualmente   
   while(FrameNext(pass\_id, name, frame\_id, value, datos))  
   {  
      if(frame\_id \== FRAME\_METRIC\_ID)  
      {  
         // Apertura del archivo en modo compartido para escritura segura  
         int handle \= FileOpen("Consolidado\_Opt.csv", FILE\_READ|FILE\_WRITE|FILE\_CSV|FILE\_ANSI|FILE\_COMMON);  
         if(handle\!= INVALID\_HANDLE)  
         {  
            FileSeek(handle, 0, SEEK\_END);  
            FileWrite(handle,   
                      datos.NumeroPase,   
                      datos.Rentabilidad,   
                      datos.RatioSharpe,   
                      CharArrayToString(datos.NombreSimbolo));  
            FileClose(handle);  
         }  
      }  
   }  
}

//+------------------------------------------------------------------+  
//| Evento ejecutado al finalizar el proceso completo de optimización |  
//+------------------------------------------------------------------+  
void OnTesterDeinit()  
{  
   Print("Proceso de optimización finalizado. Ejecutando barrido de tramas tardías.");  
     
   ulong  pass\_id;  
   string name;  
   ulong  frame\_id;  
   double value;  
   TramaDatos datos;

   // Forzar lectura de marcos retrasados que no activaron OnTesterPass antes del cierre   
   FrameFirst();   
   while(FrameNext(pass\_id, name, frame\_id, value, datos))  
   {  
      if(frame\_id \== FRAME\_METRIC\_ID)  
      {  
         int handle \= FileOpen("Consolidado\_Opt.csv", FILE\_READ|FILE\_WRITE|FILE\_CSV|FILE\_ANSI|FILE\_COMMON);  
         if(handle\!= INVALID\_HANDLE)  
         {  
            FileSeek(handle, 0, SEEK\_END);  
            FileWrite(handle,   
                      datos.NumeroPase,   
                      datos.Rentabilidad,   
                      datos.RatioSharpe,   
                      CharArrayToString(datos.NombreSimbolo));  
            FileClose(handle);  
         }  
      }  
   }  
   Print("Barrido de tramas consolidado con éxito.");  
}

#### **Fuentes citadas**

1. Real and Generated Ticks \- Algorithmic Trading, Trading Robots ..., acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/algotrading/tick\_generation](https://www.metatrader5.com/en/terminal/help/algotrading/tick_generation)  
2. Generating ticks in tester \- Trading automation \- MQL5 Programming ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/tester/tester\_ticks](https://www.mql5.com/en/book/automation/tester/tester_ticks)  
3. Differences between "Every Tick" and "Every tick based on real ticks" \- MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/441266](https://www.mql5.com/en/forum/441266)  
4. every tick data vs every tick based on real ticks \- Trading Accounts \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/479741](https://www.mql5.com/en/forum/479741)  
5. Testing Trading Strategies \- MQL5 programs, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/runtime/testing](https://www.mql5.com/en/docs/runtime/testing)  
6. MT5 Strategy Tester: Every Tick vs Real Ticks \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/451232](https://www.mql5.com/en/forum/451232)  
7. Testing Visualization \- Algorithmic Trading, Trading Robots \- MetaTrader 5 Help, acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/algotrading/visualization](https://www.metatrader5.com/en/terminal/help/algotrading/visualization)  
8. How to use sleep(and) in the Strategy Tester; What do you need and why? \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/143298/page2](https://www.mql5.com/en/forum/143298/page2)  
9. Testing visualization: chart, objects, indicators \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/tester/tester\_chart\_limits](https://www.mql5.com/en/book/automation/tester/tester_chart_limits)  
10. MQL5: Using custom indicator in strategy tester to debug an EA. \- Price Chart \- General, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/471380](https://www.mql5.com/en/forum/471380)  
11. Different result from non visual to visual mode. \- Strategy Tester \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/478892](https://www.mql5.com/en/forum/478892)  
12. Debugging and profiling \- Trading automation \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/tester/tester\_debug\_profile](https://www.mql5.com/en/book/automation/tester/tester_debug_profile)  
13. MetaTrader 5 Platform build 4150: Trading report export and new machine learning methods in MQL5 \- Release Notes \- MetaQuotes, acceso: junio 28, 2026, [https://www.metaquotes.net/en/metatrader5/news/5430](https://www.metaquotes.net/en/metatrader5/news/5430)  
14. New MetaTrader 5 Platform build 4150: Trading report export and new machine learning methods in MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/459335](https://www.mql5.com/en/forum/459335)  
15. Optimization Types \- Algorithmic Trading, Trading Robots ..., acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/algotrading/optimization\_types](https://www.metatrader5.com/en/terminal/help/algotrading/optimization_types)  
16. Strategy Testing \- Algorithmic Trading, Trading Robots \- MetaTrader 5 Help, acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/algotrading/testing](https://www.metatrader5.com/en/terminal/help/algotrading/testing)  
17. Discussing the article: "Population optimization algorithms: Binary Genetic Algorithm (BGA). Part I" \- Symbols \- Articles, Library comments \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/467269](https://www.mql5.com/en/forum/467269)  
18. How to avoid getting stuck on local optimum, for genetic algorithms, acceso: junio 28, 2026, [https://cs.stackexchange.com/questions/54828/how-to-avoid-getting-stuck-on-local-optimum-for-genetic-algorithms](https://cs.stackexchange.com/questions/54828/how-to-avoid-getting-stuck-on-local-optimum-for-genetic-algorithms)  
19. Is there a way to change any internal parameters of the fast genetic optimization? \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/456050](https://www.mql5.com/en/forum/456050)  
20. How to overcome strong local minima in Genetic Algorithm? \- ResearchGate, acceso: junio 28, 2026, [https://www.researchgate.net/post/How-to-overcome-strong-local-minima-in-Genetic-Algorithm](https://www.researchgate.net/post/How-to-overcome-strong-local-minima-in-Genetic-Algorithm)  
21. How to set up a Custom Max criterion for fast genetic optimization in MT5? \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/499078](https://www.mql5.com/en/forum/499078)  
22. OnTester \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/ontester](https://www.mql5.com/en/docs/event_handlers/ontester)  
23. Platform Start \- For Advanced Users \- Getting Started \- MetaTrader 5 Help, acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/start\_advanced/start](https://www.metatrader5.com/en/terminal/help/start_advanced/start)  
24. Strategy Tester Slippage Inquiry \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/430831](https://www.mql5.com/en/forum/430831)  
25. Ideology of the MetaTrader 5 trading strategy tester: Agents \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/378](https://www.mql5.com/en/forum/378)  
26. Download MetaTrader 5 Strategy Tester Agent \- MQL5 Cloud Network, acceso: junio 28, 2026, [https://cloud.mql5.com/en/download](https://cloud.mql5.com/en/download)  
27. Cloud and remote agent \- Risk Management \- General \- MQL5 programming forum \- Page 2, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/7325/page2](https://www.mql5.com/en/forum/7325/page2)  
28. Is it necessary to set up different port ranges for MetaTester 5 Agent Manager software on different computers? \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/470286](https://www.mql5.com/en/forum/470286)  
29. Questions about how to set up MetaTester 5 Agents Manager \- MQL5 Cloud Network, acceso: junio 28, 2026, [https://cloud.mql5.com/en/faq/settings](https://cloud.mql5.com/en/faq/settings)  
30. Getting testing financial statistics: TesterStatistics \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/tester/tester\_testerstatistics](https://www.mql5.com/en/book/automation/tester/tester_testerstatistics)  
31. Testing Statistics \- Environment State \- Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/environment\_state/statistics](https://www.mql5.com/en/docs/constants/environment_state/statistics)  
32. Group of OnTester events for optimization control \- Trading ... \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/tester/tester\_ontester\_init\_pass\_deinit](https://www.mql5.com/en/book/automation/tester/tester_ontester_init_pass_deinit)  
33. OnTesterInit \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/ontesterinit](https://www.mql5.com/en/docs/event_handlers/ontesterinit)  
34. OnTesterPass \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/ontesterpass](https://www.mql5.com/en/docs/event_handlers/ontesterpass)  
35. Getting pass number while EA is going through optimization in strategytester? \- page 2, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/35683/page2](https://www.mql5.com/en/forum/35683/page2)  
36. Getting data frames in terminal \- Trading automation \- MQL5 ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/tester/tester\_framenext](https://www.mql5.com/en/book/automation/tester/tester_framenext)  
37. FrameAdd using data file \- EA Forum \- Expert Advisors and Automated Trading \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/165457](https://www.mql5.com/en/forum/165457)  
38. How to Optimize the Results in OnTesterPass? \- General \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/393733/page2437](https://www.mql5.com/en/forum/393733/page2437)  
39. TesterStatistics \- Common Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/common/testerstatistics](https://www.mql5.com/en/docs/common/testerstatistics)  
40. Equity curve trading money management system in MQL5. How to implement it?, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/356788](https://www.mql5.com/en/forum/356788)  
41. Export History Data to CSV | Free Download Trading Utility for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/market/product/156489](https://www.mql5.com/en/market/product/156489)  
42. Deviation (slippage) Limitation and Strategy Tester Random Delay Mode \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/58635](https://www.mql5.com/en/forum/58635)  
43. Sleep \- Common Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/common/sleep](https://www.mql5.com/en/docs/common/sleep)  
44. Time management in the tester: timer, Sleep, GMT \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/tester/tester\_time](https://www.mql5.com/en/book/automation/tester/tester_time)  
45. Testing WebRequest on MT5 \- mql5 \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/75292676/testing-webrequest-on-mt5](https://stackoverflow.com/questions/75292676/testing-webrequest-on-mt5)  
46. Enable WebRequest / Socket in Strategy Tester\!\!\! \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/375405](https://www.mql5.com/en/forum/375405)  
47. WebRequest() alternative for backtesting..... \- Liquidity \- MQL4 and MetaTrader 4 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/203624](https://www.mql5.com/en/forum/203624)  
48. Call REST endpoints from MQL5 in BackTesting | by Kyriakos Anastasakis \- Medium, acceso: junio 28, 2026, [https://medium.com/@kyriakosanastasakis/call-rest-endpoints-from-mql5-in-backtesting-ae4c683f3164](https://medium.com/@kyriakosanastasakis/call-rest-endpoints-from-mql5-in-backtesting-ae4c683f3164)  
49. MetaTrader 5 build 4150: Trading report export and new machine learning methods in MQL5 \- Release Notes, acceso: junio 28, 2026, [https://www.metatrader5.com/en/releasenotes/terminal/2342](https://www.metatrader5.com/en/releasenotes/terminal/2342)  
50. How to Export a Trading Report in MetaTrader 5 \- YouTube, acceso: junio 28, 2026, [https://www.youtube.com/shorts/DyJoIMCaP00](https://www.youtube.com/shorts/DyJoIMCaP00)  
51. Exporting Graph Data from Strategy Test \- MetaTrader \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/462891](https://www.mql5.com/en/forum/462891)  
52. MetaTrader 5 (MT5) Integration / Export to MQL5 Expert Advisor \- Forex Strategy Studio, acceso: junio 28, 2026, [https://www.forexstrategystudio.com/metatrader.html](https://www.forexstrategystudio.com/metatrader.html)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEcAAAAZCAYAAABjNDOYAAAC8UlEQVR4Xu2YS8hNURTH/15lgpJXiSSSKEyUDBBhIElKplLez2RCJlIGJkQGXqVQSB4h0jdg4JWBQiRveedTXpHX+n9r7++us+4+51wMKOdXq7PXf629z7777te9QEVFRcXfZaXYfC8azoj9EGsWm+1ikUFi76B5V8XaZcMNM0DsErSdsy5m2QHNeSTW18Ui48RuQfP2ulgh+8W+QCvSFmTDrTDWIZRnBf9lLdwCO3fB+J2geV2M1ghjoPUiw50f+S420fjMmWx8sgKaF5mHdFul5A3OKbEjTjsBzZ9qtNRLF4nd9mIJbMfPYH6BF42/DvXvm5LQ6A9OaBucVkre4HyFxmYYbUjQXhiN/gjjk6ViD5xWRA9oO3xa4pKOsHzT+BHqfUJ5WvA9n5HWC8kbnN5ie5w2FprPfSVCn7bFaZ2NX8ZapDu+G/WDk9qLqG8O5abge+4jrReSNzgpTkPzhxqtZ9CifRMbaOKNwOWb6vhW1A/OMeNHqHMbIG+D77mBtF4IKyz0YgKeQMy94gPCKGQH6Gg2XMo5pDu+CapzFrcN5cOZDIX6HVNOtXUNab0QVljsxQSfkF1OkTViD0N5Lmqd29WaUc4+pDvOpUq9ffBZ9ocEoX4+lJ8G33Mdab0QVljiRQen5AEvojabPB+R1vPI23N2IquzzKXtob49lPP2nLtI64WwwjIvGg6JrXfa4/DknhDLnl/pyGho/p+cVjNDeXXwPb99Wi33YmAV6u8e3IA5KIT18l7o9Tli3Z1mYf50p70Xe2N8Doxvd2RCo981oR13WiHdoJU2+oAwHhpL2SSTR9/eWMlJsW3GH4Za3Tw4S3i3irSB5vczGj8wtY5G488Wvxc+hx7dkV7QevG2X8hBsVdiT6DLgk9e7HgjjfgBscaTI8KO8vimfi88ObU9l6HvLIInygfoUmY7E7LhFqgxxhORv/fsTxfLa+hn4hfF/P7Z8L+HnRkVjngXqXA8g+4jFQny/nepqKio+C/5Cckj7aBN9SFjAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAAeklEQVR4XmNgGAVDGTACcSi6IAFwBl2AGMAJxCXogljASSD+j4RJBjxAXIouiAcUMZBpES/DqEVEWIQcmcRgWYg2FECURdgATXyEDYxaRDeLuhggFomiSyAD9FRFCEtDtIHBLyB+AcRPgPgxlH4NxIuR1IyCUTAKqAAAXAw2yaVd5TUAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAwCAYAAACsRiaAAAAD2ElEQVR4Xu3cS+htUxgA8EVeeZUoAwNKkYlMhJLHiIEMKCUDZEAykBgg9ecWEkkGBjLAREiKAcojE1ESytTA24C8H3mtr7NW/+W7e//vce+5Ov/b71dfe61vrbPXPucM9tfe+5xSAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAVfg7J2Z8U5af+1+93+K9Gu/UeKPGCcN4ODX1ux9q3J2TeyDeY8SzNR5OY3vbL2X6M35xi5hyWk4AANtbFAiX5eSMqWJiVfK+36xx7dDP46NVFWwfpP5Wa+4tc2t+VeOQlOtzYxvFXs4DAPuI58ryJ/hl5+2OqX1P5aYsU7DdkhMT8nrvpv7/IR9DFwXbgSn3TOoDAPugh9p2qki4vMYnNc4Zcn3eeWVxi/LEzaE9lo/h/hp3tvalrT+6uMY9rb2qgu3PGi/lZHVNjUdb+66yWLu7qSxun5495MJjZeeC6qkaj6dcuKLG7a2dP4cuCrYDWvvKtj2mbW8ui2MIJ9V4sLW7M2u8knIAwDYx3lK7asifWzZvv4234fr862s8MuRHH+8i5sS+x+gFTNfXzu2LyuoKtjAew4Upf3Jr31AWRWQ4so2FH9t2PL4oenuu33oexz8c2jvKv8dGUbBF0fVW2XnO6TX+GvrjeDzj1wu9j2ocNIwBAGtu/xpP13iyxttl5yKgFy2vp1wUBlcPuVXJ64cx19tnpXyYKtj68c/FMqbWn+qP7Ttaf2qtuAr3R8pttd/ReIUtCubR0WW+YMv7y30AYI19nfrjifzgof17jY3W7nO2Ounft4uYM7XPqcLjkpQP96b+lGWusOX9/lTjsNbOY1PHFuKHEnluiFy/ujX32ql+FwXb3NWxo8pyBVt8r3P7BwDW0M+pHyfy11p7Y8iH/kxUP9kfO7RXJe/vlJSbax9X44GhP2d3Cra5NY8vi2fUuq1eFwVvzs21z0/9URRsh+dkE8+yLVOwxfN54y9vAYA1dWiNL2p8XuPllvutxmdl8bxV/N/aRo3ryuJk/2mbEwVDjH9b4/mWj+ejViHW6REFTux3fGD/17JYL46h6/Pj/cT21mFsyjIFW6z7Zdnc9xHDWPTjVnBs47PrYn7/3EbxmY7F0o2tH9vbyuJZtK6vt9/QHn1XFu8/4vs0FrdJ4/uM7++Jlsuvf7XlLkh5AIC1sux/zc3JRdA6OqNtt8OxAgCsVL/qte6FUPz1yAtl8StWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgNX7B+sgCI0xK87sAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAxCAYAAABnGvUlAAAEhElEQVR4Xu3dN6gtRRgA4DEHMGAEQ2GhIBbmgAqigoIBtREUKwtBsBA7EQU7LcRGRQsFBQsDIoZGVAQLsVIRTIg555zT/OwMd868PfddzjtXved8H/zMzL/37J5dD+z/ZoMpAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzM/JfaI4IsfNzXifpr8RXZnjqtI/sV0wB3f1CQBYBn/n2LsZ71pyyyj2e+vSv7GM5+WvPpHdlybzj6b5bvPfFt/93Gb8Whrf7y1xQpr8vQLAwju8tH2RcFY3Xgb7pU2PQ4wv7nKzeL9PpGHdB/fJtOl3+K/92CemGPveN+XYs0/Owdi2AGBhfVnaOAHGzFo4pLTL5pUcz3W5aYVBXNrct8t92I1b/XoeHMlVL/SJ/9haCraYRXu3T2ZX94k5iZk7AFga35T28bRSQHxU2o3o7c3EamL/dy7988t4Nac3/Y+b/ph+XTHeKLOYaynY+v1bb5enyUuvALDQjmn69aT7W5NrXdonZlSLxP+bWYqOn3J81idH9Ovux9vlOC3HKTnO6Jath2fS9IIxHoCI30WNn7vxmH5/zstxahr2aZtu2Twcn+OGPgkAi+jIbhwn3RfT5MzRstg/bVp0rEXMrK2lAO3X3Y/DYWk8v16mFWy9WWfYHshxYJ+ckyhqr+uTALCIxk6ybS5OuOGt0h5X2mNz7J5W7k+qn4l2j9Lu0uQfaZbv1uTr+mOWKtSZvZjRCXU79e+jv15iG3f2yc34oOnHsYmHFqbpj/VjaWW/q/ib25rxvaWNG/dDPbbh69K+V9r6JGa8TiPsmIYitBZb9XM/lPb2NN+C7Y8cD3e5fp/r+IAcT5f+maW9Pw3/WAjX5Ng2Tf6uti/96o4cO3U5AFg43+b4KsefXb6e0EOcKOPpxk+aXJuPuCzHk5OLJ060bVv1489L+0Zp4366ULdTC5sYf1r68/R9Gh6+iMLkoW7ZNLWIao098Vn1+xyuSEM+tj+2/KLSHtXk+mPafu7Npt8vr0XXL6UN8yzYwlNp2F7E9WkoGquz0+Q76NrvHetvn8St37EWofEaj97Y8QKApTTtpPhd049ZnFpw1XuV+mKhtvXdWXVc33dWx6+Xts7ItdtpXdsnNoCj08oM5VpdUNr25vr+mNb20Bx3l36IIjDU5fVYtv9Nz2n6q3m5T8xgq7TyIt2D0uT3iIK/Fqfh19LukOOSJt+a9tsAgKX0exped9GL2bA62xUzSzFDFUVJuDUNn4mTclzeCu/k2CvHS2n42+jfk4ZXQdTCLfIXpmHmrxYcsZ1bSv/5NDkDuNFMK4BX80QaHgKIz76a44s0vFw32npsY5a0FstxqTGWhSh84pjG/zUh2pPScJ/cs2mYXZvl+2yJuITeFn8xk1Yvo8Yl3rgXMC6H11fNhHrJt9XP6AIARZzcY5aELRNFF7OLGV33rgHAKhRsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMBC+AcP3/cDKXKrEgAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAaCAYAAAC+aNwHAAAApElEQVR4XmNgGAXoYAIQfwTi/1D8HYjfoYmtgqvGA2CK0YE8A0R8F7oEOgApOo4uCAW4DIeDCAaIAnd0CSDgZCDCgGsMuBWsZ4DIBaBLIANcNjgyQMQnokugA5gBH4D4PRD/gPIvA7EwkjqsAOb/JHQJYsFNBuzOJxrg8j/RAKT5DrogsaCaAWJAOroEITAZiD8zQEIclO6/AvE/FBWjYBTQGgAA/GAxOhsgBN4AAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD8AAAAaCAYAAAAAPoRaAAACKUlEQVR4Xu2YO4xNURSGf28Zj0IUEkwhUYlGSJAICZ1CaLSITiTiEVEIGoVEJZ5BhA6lgohKolQgCo9CFArveMSb/7fWzlmz3Jljihl3jvMlf+7e69+vdfa+O+deoKWlJTGT2kadpOaE+NJQbhwXqJ/UQ2o1NZc6Rj2jlrjXSJTYV2pSNsgemH8nG03gG+p3Vf66HBzpvIElNiYbibqHM+KYD0vqSTY60Ljkv8OSmpKN/wEl3rgd/VsGSn4NtZJaTq2gVqH+XviXnEf/uXREjZ/noLOF2ofqAe2mRvdp0X0MOvm6DvIf5GCXUpdLH+7DOkzIhrMV5q9P8fjQdnn5avLmURdhL07T3BOLYaftAPU+xG9Sh6nr1FqPnYCNpVN4j7pLnXNPjKI+U6ep2xhk8qIsNh/p3uB1IsZ3oEpelAWLZdRTL493r/DFPy9Tm0L8JTXLy2epH8GL/VWOG9ffWgfkBqpEX/mndkZoYZ2IE23Hn8kXFlGfvHwItlMZtR8X6pdQjXcKdgIKZWztek4214eMONFO6lqoR28BquT3w16lM2o/PdSvULe8fJw6Erwy9uRQLuT6kBEnegw7PYXoLUR1vEX0ZlMTqTPU3hDXy9cML8vTAyjE/ir3pPqwsJl6BLs0N8Am1mX1gXoB+82gI/8a9h3++LuX7Zi+WrqgNnpMHIS1VbupHtP/CWorHYVdkBr7rftjqXewefXTW2sYtgfQ0tLS0tLN/AJj6Zach6I2wQAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC4AAAAaCAYAAADIUm6MAAABpklEQVR4Xu2WzStEURjGXx9lIRtbZaGUko0oREZkY6Fs/BEiK7KQ/BNKFhQ2WNmThb/AgmIlCwufKZKPeJ7OOc17X2PuLGbm3sX91dO8533unXnP15wjkpFRFlqgeWgdalP5ARWnim3oB7qCJqB2aA26hfq9lzpY1CfUaA2wJM4/s0bSfEn8aNKfsskkeRZXVJ01DHEdqypd4gq6tkYBUlX4t7iCmqyRdlh0qkayVIoVPgmNQsNQDhqT+H1QNVj0nU16ZqAVyXduEaqNPJEgxUY8QP/SJpPmXFxhDdbwzIrzp60BTqBdaAeaU/k3aEHcTDb7XBigTmhP3EFnvTCArz7e8O1/CS/ZZdCqPMsWtO/jEejUxzzIanxM9LuMufzIEHSjPF41Nn3M9/mdJXEk+SIf/eeq9w7CQwr6gzYpfzvJdp+KA73Qu2qz2OBzBisGfyRnk1K48HEVB7olWjjhbHVAhyZfVpYlumG5V8iHRA8zu1QCPeKe1fAe9ALVm3zZ4Y2RJy+vC/r//Ri6kOhNkhvuXty9iMvkCXoQt5E1dsYyMjIyKswvwl1rc72dZtsAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,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>

[image9]: <data:image/png;base64,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>