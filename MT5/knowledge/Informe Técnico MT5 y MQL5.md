# **Arquitectura y Desarrollo Avanzado en MetaTrader 5: Guía Técnica de Ingeniería para Trading Algorítmico**

La transición de sistemas de trading heredados hacia entornos de alto rendimiento exige un conocimiento profundo de la infraestructura física, los protocolos de comunicación y la semántica interna del lenguaje de programación. MetaTrader 5 (MT5) y su lenguaje nativo, MQL5, han sido diseñados para superar las limitaciones de procesamiento secuencial de sus predecesores, introduciendo una arquitectura de clúster distribuida y un entorno de ejecución fuertemente tipado.1 Este informe técnico analiza de manera exhaustiva la arquitectura interna de la plataforma, el sistema de tipos de MQL5, el ciclo de vida de sus programas, las particularidades de su compilador y los mecanismos avanzados de acceso a datos de mercado para el desarrollo de sistemas algorítmicos cuantitativos de baja latencia.

## **1\. Arquitectura Interna de MetaTrader 5**

La plataforma MetaTrader 5 implementa un modelo de infraestructura de red distribuida y escalable de 64 bits.2 A diferencia de los entornos de ejecución monolíticos, la terminal del cliente se comunica de forma cifrada mediante protocolos TCP/IP propietarios con un clúster de servidores altamente especializados.2 Esta segregación de funciones garantiza el procesamiento paralelo de las cotizaciones, el almacenamiento masivo de datos históricos y la ejecución asíncrona de transacciones comerciales con una desviación mínima de precios.2

### **El Modelo de Clúster de Servidores**

La topología de servidores de MetaTrader 5 divide el procesamiento operativo de la firma de corretaje en capas independientes.2 Esta distribución modular permite escalar el sistema de forma dinámica y aplicar políticas rigurosas de tolerancia a fallos mediante la redundancia de hardware en múltiples centros de datos financieros globales.2

* **Main Trade Server (Servidor Principal de Negociación)**: Es el núcleo transaccional encargado de validar y procesar todas las operaciones de trading en tiempo real, gestionar el riesgo neto de las cuentas y liquidar las transacciones financieras.2  
* **History Server (Servidor de Historial)**: Almacena y distribuye la base de datos de barras de un minuto (M1) y ticks históricos.8 Requiere sistemas de almacenamiento de estado sólido de alto rendimiento (SSD NVMe en arreglos RAID 10\) para minimizar los tiempos de lectura y escritura durante la descarga simultánea por miles de terminales cliente.2  
* **Access Server (Servidor de Acceso o Proxy)**: Funciona como un intermediario o pasarela perimetral entre las terminales de los clientes y el servidor de negociación principal.8 Su propósito fundamental es absorber el tráfico entrante, balancear la carga de conexiones concurrentes y mitigar proactivamente ataques distribuidos de denegación de servicio (DDoS).2 Al geodistribuir los servidores de acceso cerca de los hubs de conectividad financiera (como Equinix LD4 en Londres, NY4 en Nueva York o SG1 en Singapur), los brokers reducen la latencia física de red a valores inferiores a los ![][image1].6  
* **Backup Server (Servidor de Respaldo)**: Réplica en tiempo real los datos transaccionales del servidor principal mediante mecanismos de sincronización síncrona.7 Para garantizar la continuidad operativa, es mandatorio co-ubicar estos servidores con diferentes proveedores de hosting e infraestructura de red, impidiendo que una caída general del centro de datos primario afecte al sistema de respaldo.7  
* **SQL Export Servers (Servidores de Exportación SQL)**: Transfieren de forma continua la base de datos de operaciones comerciales hacia esquemas relacionales externos para propósitos de reportería institucional, cumplimiento regulatorio y automatización de sistemas CRM.8

Para optimizar la latencia transaccional y el procesamiento de datos de mercado en tiempo real, el hardware físico del clúster de servidores debe configurarse a nivel de BIOS desactivando todos los estados de ahorro de energía de la CPU (como el C-state) y fijando el perfil de memoria en alto rendimiento para garantizar un ancho de banda constante de lectura/escritura.7

| Servidor del Clúster MT5 | Función Operativa Principal | Tipo de Sincronización y Redundancia | Requisitos Mínimos de Hardware |
| :---- | :---- | :---- | :---- |
| **Main Trade Server** | Procesamiento transaccional, cálculo de margen y ejecución.2 | Réplica síncrona activa hacia el Backup Server.7 | Procesador de alta frecuencia de reloj por núcleo, RAM de baja latencia.2 |
| **History Server** | Almacenamiento e indexación de datos de ticks históricos y barras M1.7 | Almacenamiento persistente en caché distribuida y archivos TKC/HCC.9 | Arreglos RAID 10 SSD NVMe, velocidad de transferencia superior a ![][image2].2 |
| **Access Server** | Control de conexiones de clientes, balanceo de carga y mitigación DDoS.8 | Balanceo DNS y enrutamiento dinámico regional de terminales.10 | Entorno virtual o dedicado, 2 vCPU, 4GB RAM, ancho de banda mínimo de 100 Mbps.11 |
| **Backup Server** | Conmutación por error ante caídas catastróficas del servidor principal.8 | Sincronización bidireccional en tiempo real mediante IPs externas dedicadas.7 | Hardware idéntico al servidor de producción principal, en centro de datos aislado.2 |

### **Sincronización de Ticks y Base de Datos Histórica**

La terminal de MetaTrader 5 implementa una sincronización local y remota de cotizaciones para minimizar el tráfico de red.9 Cuando el terminal solicita datos históricos de un símbolo por primera vez, descarga los datos comprimidos en barras de un minuto desde el History Server y los almacena localmente en archivos de extensión .hcc.9 La base de datos de ticks reales se descarga bajo demanda y se guarda de forma mensual en archivos binarios optimizados con extensión .tkc dentro del directorio \\bases\\\[servidor\_broker\]\\ticks\\\[símbolo\]\\.14  
Para la estimación matemática de ticks en fases de backtesting donde no se cuenta con el historial de ticks reales del broker, el motor de MT5 utiliza un algoritmo de modelado basado en puntos de control extraídos de las barras de un minuto.9 La distribución matemática de los puntos de control en barras con tres o más ticks se calcula dividiendo la barra en tres secciones lógicas: la sombra de apertura (Open a High/Low), el rango de oscilación principal de la vela (High a Low) y la sombra de cierre (High/Low a Close).14 Si el número de pips de recorrido supera la cantidad de ticks disponibles en la barra, el sistema genera una secuencia en diente de sierra (sawtooth sequence), mientras que si la cantidad de pips es significativamente alta, se aplica una progresión lineal para simular el comportamiento microestructural del precio.14

### **Arquitectura de Eventos Interna de la Terminal**

La terminal cliente de MetaTrader 5 opera bajo un modelo arquitectónico guiado por eventos (event-driven).18 El sistema operativo asigna colas de mensajes específicas para cada hilo de ejecución de los programas MQL5.18 La terminal inyecta los eventos del mercado y del usuario de forma asíncrona dentro de estas colas, las cuales tienen un tamaño máximo de 1024 elementos.18 Si la cola de eventos de un programa MQL5 se satura debido a un procesamiento lento o bloqueante del hilo de ejecución, las notificaciones más antiguas pueden ser descartadas o sobrescritas por los nuevos eventos entrantes, un comportamiento crítico conocido como saturación de cola que degrada la precisión operativa del algoritmo de trading.19

## **2\. El Lenguaje MQL5 en Detalle**

MQL5 es un lenguaje orientado a objetos de tipado estático y fuerte cuya sintaxis y semántica derivan directamente de C++.1 Sin embargo, la gestión del ciclo de vida de los objetos, la ausencia de punteros físicos a memoria y la estructura interna de sus variables dinámicas se asemejan al comportamiento de ejecución observado en C\#.1

### **El Sistema de Tipos y Alineación en Memoria**

MQL5 clasifica las estructuras en tipos simples y complejos, imponiendo restricciones estrictas en la copia de datos y en la interoperabilidad con librerías nativas del sistema operativo 23:

* **Estructuras Simples (Simple Structs)**: Son aquellas compuestas exclusivamente por tipos de datos primitivos como enteros, flotantes, booleanos, enumeraciones o subestructuras simples.23 No contienen cadenas dinámicas (string), arreglos dinámicos, objetos de clases o descriptores.23 Las estructuras simples se pueden copiar directamente mediante asignación simple (structA \= structB) si comparten exactamente el mismo tipo de datos o si heredan linealmente de una estructura base común.23 Son los únicos tipos de datos estructurados que se pueden pasar directamente por referencia a funciones exportadas en DLLs escritas en C++ nativo.23  
* **Estructuras Complejas (Complex Structs)**: Incorporan de forma directa o indirecta miembros administrados por el entorno de ejecución, como strings de formato Unicode, arreglos dinámicos, punteros u objetos de clases.23 Cuando el compilador detecta una estructura compleja, le asigna de forma implícita un constructor por defecto cuya función es inicializar y limpiar la memoria dinámica de los strings y redimensionar correctamente las referencias a los arreglos dinámicos.23 Las estructuras complejas tienen prohibido el casting explícito a tipos de datos simples y no pueden pasarse a funciones importadas de DLLs nativas debido a que la representación interna de su memoria física está fuertemente acoplada al motor de ejecución de la terminal.23

El empaquetado por defecto de las variables dentro de una estructura en MQL5 se realiza de manera lineal sin alineación física (lo que en C++ clásico equivale a la directiva \#pragma pack(1)).23 Cuando se requiere interoperar con DLLs externas que esperan un empaquetado de memoria alineado a fronteras específicas, se debe aplicar la directiva pack(n) en la declaración de la estructura, donde ![][image3] bytes.23  
Al compilar con pack(n), el offset en bytes de cada miembro respecto al inicio físico de la estructura se ajusta de tal manera que las variables con un tamaño menor que ![][image4] se alineen a múltiplos de su propio tamaño nativo, mientras que las variables de tamaño igual o mayor que ![][image4] se alineen estrictamente a múltiplos de ![][image4] bytes.23 Para verificar la distribución física de memoria y calcular con precisión los offsets de depuración, el lenguaje provee la función integrada offsetof(), la cual acepta como parámetros el identificador de la estructura y el nombre del miembro evaluado.23

### **Descriptores de Objetos y Gestión Dinámica de Memoria**

Un error habitual para un desarrollador con experiencia en lenguajes nativos es asumir que los punteros declarados en MQL5 mediante el operador asterisco (\*) representan direcciones físicas en la memoria virtual del proceso.27  
En MQL5, las variables declaradas como punteros (por ejemplo, CMyClass \*ptr) contienen **descriptores de objetos** (object handles).27 Estos descriptores son números enteros sin signo de 8 bytes (ulong) administrados por una tabla interna de la terminal, actuando como llaves lógicas de acceso indirecto a la instancia física del objeto que reside en el montón (heap) asignado al programa.27 Debido a este direccionamiento indirecto, la aritmética de punteros está prohibida.21  
La liberación de la memoria dinámica en el montón requiere la invocación explícita de la función delete sobre el descriptor del objeto creado dinámicamente mediante new.27 Si un puntero dinámico sale del ámbito físico del programa sin ser destruido, se generará una fuga de memoria (memory leak) que quedará registrada en el diario de la terminal al descargar el módulo.27  
Para prevenir accesos inválidos a memoria que provoquen el cierre crítico del hilo de ejecución del programa algorítmico, el desarrollador debe emplear la función de validación CheckPointer().27 Esta función retorna una constante de la enumeración ENUM\_POINTER\_TYPE:

* POINTER\_INVALID: Indica que el descriptor es nulo o apunta a un bloque de memoria física que ya ha sido liberado mediante el operador delete.27  
* POINTER\_DYNAMIC: Confirma que el descriptor está vinculado a un objeto asignado dinámicamente en el montón y que es seguro invocar sus métodos o aplicarle el operador delete.27  
* POINTER\_AUTOMATIC: Representa un objeto instanciado estáticamente en la pila del programa o como una variable anidada de otra clase.27 El programador tiene prohibido aplicar el operador delete sobre este tipo de descriptores, ya que el compilador se encarga de liberar su memoria de forma automática al salir de su bloque de ejecución.27

Fragmento de código  
// Implementación defensiva de una clase con deasignación segura de punteros  
class CMemoryManager  
{  
private:  
   double             m\_data;  
   CMemoryManager\*    m\_next\_node;

public:  
   CMemoryManager(void) : m\_next\_node(NULL) {}  
   \~CMemoryManager(void) { SafeCleanup(); }

   void SetNext(CMemoryManager \*next\_ptr)  
   {  
      m\_next\_node \= next\_ptr;  
   }

   void SafeCleanup(void)  
   {  
      // Validación estricta del descriptor dinámico antes de la deasignación  
      if(CheckPointer(m\_next\_node) \== POINTER\_DYNAMIC)  
      {  
         delete m\_next\_node;  
         m\_next\_node \= NULL;  
      }  
   }  
};

A nivel de bajo nivel, el administrador de memoria de MetaTrader 5 implementa una optimización de alto rendimiento: la memoria física liberada por delete se devuelve inmediatamente al pool de memoria local asignado al módulo MQL5.24 Sin embargo, para evitar la fragmentación y las llamadas recurrentes al sistema operativo (kernel context switches) durante ráfagas rápidas de ticks de mercado, la terminal devuelve de forma consolidada la memoria liberada de ese pool hacia el sistema operativo únicamente al finalizar la ejecución del controlador del evento activo (por ejemplo, después de retornar de OnTick() o OnCalculate()).24

### **Diferencias Críticas y Restricciones Sintácticas Respecto a C++**

A pesar de la similitud visual del código, existen marcadas discrepancias estructurales entre el compilador de MQL5 y los estándares modernos de C++ (C++11/14/17/20) que alteran los patrones de diseño algorítmico 1:

1. **Herencia Múltiple Prohibida**: MQL5 no admite herencia múltiple de clases.30 Una clase solo puede heredar directamente de un único ancestro base.30  
2. **Abstracción de Interfaces Limitada**: Aunque existe la palabra clave interface, el compilador de MQL5 la interpreta sintácticamente como una clase abstracta pura sin constructor.21 Dado que MQL5 carece de herencia múltiple de clases y no soporta herencia de interfaces independiente del árbol jerárquico tradicional de CObject, el polimorfismo multidireccional fuera del árbol principal está severamente acoplado a la herencia simple, reduciendo la efectividad del diseño de colecciones genéricas independientes del framework nativo.34  
3. **Restricciones de Plantillas (Templates)**: El motor de plantillas de MQL5 no admite deducción avanzada de argumentos de plantilla de tipo estandarizado ni técnicas complejas de metaprogramación basadas en SFINAE o conceptos.21  
4. **Ausencia de Manejo de Excepciones**: No existen bloques para la captura estructurada de excepciones (try, catch, throw).21 Cualquier fallo grave en tiempo de ejecución (como una división por cero en coma flotante o la de-referenciación de un descriptor inválido) provoca la terminación abrupta y crítica del programa algorítmico por parte de la terminal, descargando el Expert Advisor de memoria de forma permanente para proteger la estabilidad operativa de la plataforma.21  
5. **Limitaciones en Sobrecarga de Operadores**: No se pueden declarar operadores sobrecargados de forma global fuera del cuerpo de una estructura o clase.21 Adicionalmente, el compilador restringe la sobrecarga de ciertos operadores críticos de C++ como el operador de llamada a función (()), resolución de ámbito (::), acceso a miembro (-\>) y el operador coma (,).35  
6. **Ausencia de la Palabra Clave mutable**: No es posible modificar miembros de una clase dentro de métodos constantes (const), forzando al desarrollador a utilizar castings explícitos agresivos para eludir la const-correctness cuando se implementan patrones de actualización interna perezosa (lazy evaluation).21

| Característica de Diseño | MetaQuotes MQL5 | Estándar C++ Moderno (C++11/14/20) | Implicación en el Desarrollo Algorítmico |
| :---- | :---- | :---- | :---- |
| **Punteros a Memoria** | Descriptores de objeto abstractos de ![][image5] (ulong).27 | Direcciones de memoria física nativas (punteros crudos y std::shared\_ptr/unique\_ptr).36 | Impide la aritmética de punteros física. Requiere validación pasiva mediante CheckPointer().21 |
| **Herencia** | Herencia simple estricta.30 | Herencia múltiple directa de clases nativas.30 | Limita la implementación de patrones de diseño basados en mixins. Obliga al uso de composición.34 |
| **Manejo de Excepciones** | Inexistente. Interrupción crítica del hilo de ejecución ante fallos graves.21 | Soporte estructurado nativo (try, catch, throw).21 | Obliga al desarrollador a realizar validaciones preventivas exhaustivas de parámetros y punteros antes de cada cálculo.21 |
| **Alineación de Estructuras** | Configuración predeterminada pack(1) (sin alineación) o manual vía pack(n).23 | Alineación natural implícita por el compilador o directiva \#pragma pack(n).23 | Requiere control estricto de offsets mediante offsetof() al estructurar datos para interoperabilidad con DLLs.23 |

## **3\. Tipos de Programas MQL5 y sus Modelos de Ejecución**

MetaTrader 5 categoriza los desarrollos de software en cinco tipos de programas diferenciados con permisos operativos específicos y contextos de hilos de ejecución aislados para garantizar la estabilidad visual y transaccional de la terminal.1

### **Clasificación y Arquitectura de Hilos de Ejecución**

* **Expert Advisors (EAs)**: Son sistemas autónomos continuos diseñados para la toma de decisiones y el envío de operaciones comerciales.39 Cada Expert Advisor adjunto a un gráfico de precios se ejecuta en su propio hilo de procesamiento dedicado asignado por el terminal.18 Esto previene que retrasos transaccionales o cálculos lógicos pesados congelen la interfaz de usuario de la plataforma.18  
* **Custom Indicators (Indicadores Personalizados)**: Son módulos matemáticos orientados al cálculo secuencial y la representación visual de series temporales sobre los gráficos de precios.39 Todos los indicadores aplicados a un mismo símbolo financiero comparten un único e idéntico hilo de ejecución.18 Este hilo es también el responsable del refresco visual y el renderizado gráfico de ese símbolo.18 Por este motivo, los indicadores tienen estrictamente prohibido invocar funciones comerciales y no deben realizar llamadas de red síncronas (WebRequest) o cálculos intensivos que superen una complejidad temporal de ![][image6] por tick entrante, evitando así la congelación visual del terminal.18  
* **Scripts**: Son rutinas orientadas a la automatización de procesos puntuales de una sola ejecución.39 Al ser arrastrados a un gráfico, se ejecutan de manera lineal y secuencial dentro de su propio hilo de procesamiento dedicado y se descargan automáticamente de la memoria una vez que retornan de la función de entrada OnStart().18  
* **Services (Servicios)**: Programas de segundo plano global que se ejecutan sin necesidad de estar vinculados a un gráfico o símbolo activo.39 Se inician de forma automática al arrancar la terminal y corren en su propio hilo de procesamiento global.18 Tienen permisos comerciales completos y acceso a funciones de red, pero carecen de interfaz de usuario o capacidad de procesar eventos gráficos interactivos.39 Para persistir operativos de forma indefinida, deben implementar bucles infinitos controlados mediante temporizadores pasivos.39  
* **Libraries (Librerías \- EX5/DLL)**: Contenedores estáticos o dinámicos de funciones auxiliares que no poseen un hilo de ejecución independiente ni controladores de eventos nativos.39 Sus funciones se ejecutan bajo el contexto de hilo y los permisos de seguridad del programa MQL5 que las invoca.39

### **El Ciclo de Vida de los Programas Algorítmicos**

El ciclo de vida de los programas asíncronos en MQL5 se gestiona mediante la captura de eventos a través de controladores predefinidos en el código fuente 18:

* OnInit(): Es el controlador de inicialización invocado por la terminal inmediatamente después de cargar el programa en memoria.42 Debe validar los parámetros de entrada y configurar los búferes y recursos del sistema.42 Su retorno obligatorio es una constante de la enumeración ENUM\_INIT\_RETCODE.42 Si retorna INIT\_FAILED o INIT\_PARAMETERS\_INCORRECT, el programa abortará de inmediato su ejecución, invocando al controlador de descarga OnDeinit() con el motivo de deinicialización REASON\_INITFAILED.42  
* OnDeinit(const int reason): Invocado antes de descargar el módulo de la memoria.42 El parámetro entero reason identifica el motivo de la descarga de acuerdo a la enumeración ENUM\_DEINIT\_REASON, permitiendo al desarrollador implementar políticas de limpieza selectivas.42 El motivo de deinicialización también puede consultarse de forma global mediante la función UninitializeReason() o leyendo la variable predefinida \_UninitReason.42  
* OnTick(): Controlador exclusivo de los Expert Advisors que se ejecuta ante cada nueva cotización (tick de precio) recibida por el símbolo al que está adjunto el programa.19  
* OnCalculate(): Controlador exclusivo de los indicadores que se dispara ante la llegada de cada tick del símbolo para actualizar de manera secuencial los búferes de dibujo matemático del indicador.18  
* OnTimer(): Procesador de eventos de tiempo periódicos configurados a nivel de microsegundos mediante la función EventSetMillisecondTimer().4  
* OnTrade() / OnTradeTransaction(): Controladores exclusivos de los Expert Advisors encargados de capturar los cambios en el estado de la cuenta comercial, órdenes activas, posiciones y ejecuciones de tratos.19

                \[Inicio del Programa MQL5\]  
                           |  
                           v  
                     \[Llamada OnInit()\]  
                           |  
            \+--------------+--------------+  
            |                             |  
     (Retorna ERROR)               (Retorna SUCESS)  
            |                             |  
            v                             v  
                      
 (REASON\_INITFAILED)              /       |        \\  
            |               OnTick()  OnTimer()  OnTradeTransaction()  
            v                  \\          |         /  
                   \[Evento de Cierre\]  
                                          |  
                                          v  
                                    
                                          |  
                                          v  
                                  

Un comportamiento crítico que todo desarrollador algorítmico debe prever es el comportamiento asíncrono y la posible corrupción de estados al cambiar la temporalidad o el símbolo de un gráfico.42 Al cambiar la temporalidad del gráfico, la terminal inicia inmediatamente una nueva instancia del programa MQL5 en paralelo y le envía el evento OnInit() antes de que la instancia previa haya finalizado de procesar su propia función OnDeinit().42 Si el programa no utiliza semáforos globales o si limpia de forma agresiva recursos compartidos (como variables globales o archivos en disco) dentro de su destructor, la nueva copia activa heredará un estado inconsistente de ejecución.42  
Adicionalmente, bajo escenarios de alta volatilidad o demoras en la descarga de datos históricos temporales, el compilador puede corromper el código del motivo de deinicialización, reportando de manera errónea una desinstalación total del gráfico (REASON\_REMOVE) en lugar de un cambio de marco temporal (REASON\_CHARTCHANGE).42

| Evento del Ciclo de Vida | Expert Advisor | Custom Indicator | Script | Service | Restricción Crítica de Ejecución |
| :---- | :---- | :---- | :---- | :---- | :---- |
| OnInit() | Sí 42 | Sí 42 | No 31 | No 39 | Retorna ENUM\_INIT\_RETCODE. No admite bucles bloqueantes.42 |
| OnDeinit() | Sí 43 | Sí 43 | No 31 | No 39 | Invocación asíncrona concurrente durante cambios de gráfico.42 |
| OnTick() | Sí 45 | No 45 | No 45 | No 45 | Solo se activa si el mercado está abierto y se recibe cotización nueva.45 |
| OnCalculate() | No 24 | Sí 24 | No 24 | No 24 | Ejecución en el hilo gráfico principal; requiere optimización estricta.18 |
| OnTimer() | Sí 9 | Sí 17 | No 39 | No 39 | Retrasos implícitos si la CPU está saturada por cálculos concurrentes.9 |
| OnTradeTransaction() | Sí 19 | No 45 | No 45 | No 45 | Cola máxima de 1024 transacciones. Desorden en marcas de tiempo.19 |
| OnStart() | No 31 | No 31 | Sí 31 | Sí 39 | Punto de entrada lineal. Su retorno implica la descarga del módulo.31 |

## **4\. Entorno de Compilación, Depuración y Estructura de Proyectos**

El desarrollo de sistemas de trading cuantitativos de grado institucional requiere la estructuración de proyectos modulares utilizando el formato de manifiesto de proyectos .mqproj administrado por MetaEditor.49

### **Estructura de Proyectos Modulares (.mqproj)**

El formato .mqproj es un archivo de configuración en formato JSON que unifica el control de dependencias, almacenamiento remoto en MQL5 Storage, control de versiones nativo y metadatos de compilación de un proyecto.49  
La principal ventaja del modelo de proyectos modulares radica en que las propiedades especificadas interactivamente en el panel del proyecto anulan y toman precedencia absoluta sobre las directivas de preprocesamiento \#property insertadas en el código fuente, facilitando la creación de perfiles de compilación específicos para depuración, optimización avanzada o distribución comercial sin necesidad de alterar los fuentes originales.49 Las dependencias locales declaradas con comillas dobles (\#include "cabecera.mqh") se gestionan de forma relativa al directorio del proyecto, mientras que las dependencias globales declaradas con llaves angulares (\#include \<cabecera.mqh\>) se recuperan directamente de la ruta centralizada del sistema MQL5\\Include.49  
La compilación a nivel de producción permite activar la bandera de "Optimización de Código Adicional", la cual aplica técnicas de reordenamiento de registros para acelerar hasta tres veces la velocidad de ejecución física del binario ejecutable .ex5, a costa de un tiempo de compilación ligeramente mayor y de la pérdida de resolución fina durante el proceso de depuración paso a paso.41

### **Profiling por Muestreo (Sampling Profiling)**

A partir de la revisión global del profiler de MetaEditor, se descartó el antiguo e impreciso método de perfilado por instrumentación de código y se implementó el **Perfilado por Muestreo (Sampling Profiling)**.41 El perfilado por instrumentación modificaba el binario inyectando contadores de ciclo de reloj al inicio y al final de cada función, lo cual introducía un sesgo temporal artificial (overhead) que distorsionaba la medición en bucles matemáticos de alta velocidad.41  
El perfilado por muestreo opera interrumpiendo brevemente de forma pasiva la ejecución del programa a una frecuencia ultra rápida de hasta 10,000 muestras por segundo para capturar el estado instantáneo del puntero de instrucción y la pila de llamadas activa.41 Este método no altera el rendimiento real de ejecución del código optimizado, garantizando que el análisis de cuellos de botella se realice sobre el mismo binario de producción.41 Al finalizar el perfilado, el desarrollador cuantitativo dispone de dos métricas cruciales de rendimiento para guiar su optimización matemática 53:

* **Total CPU \[unit, %\]**: Muestra la cantidad acumulada de veces que una función específica o una línea de código apareció presente dentro de la pila de llamadas capturada durante todo el análisis.53 Incluye tanto su propio tiempo de ejecución como el consumo temporal de todas las subfunciones invocadas secuencialmente por ella.53  
* **Self CPU \[unit, %\]**: Mide el porcentaje de muestras donde la pausa del muestreo ocurrió estrictamente dentro del cuerpo físico de las instrucciones de la propia función, excluyendo de forma rigurosa las llamadas externas a otras clases o subfunciones.53 Un valor elevado de *Self CPU* es el indicador de que la lógica interna de esa sección de código está acaparando ciclos del procesador y requiere de una refactorización algorítmica inmediata.53

Para analizar funciones puras que hayan sido insertadas en línea por el compilador debido a las optimizaciones internas de rendimiento, el MetaEditor permite desactivar temporalmente el inlining de funciones dentro del panel de configuración de depuración, garantizando la visibilidad de la pila de llamadas completa durante el profiling.53

## **5\. El Modelo de Ejecución y Concurrencia**

MetaTrader 5 destaca por su robustez ante aumentos de volatilidad en los mercados financieros, lo cual se debe a la estricta separación de los contextos de procesamiento en hilos independientes.2

### **Limitaciones de Concurrencia y el Riesgo de Hilos Nativos**

A pesar del entorno multinúcleo de la terminal, los programas MQL5 se ejecutan bajo un bucle de eventos asíncrono que opera sobre un modelo estrictamente mono-hilo.18 Un Expert Advisor o un indicador no dispone de librerías nativas dentro del lenguaje MQL5 para instanciar hilos secundarios de procesamiento paralelo.55  
Si un desarrollador cuantitativo intenta utilizar las funciones de la API de Windows importadas de forma directa desde la librería kernel32.dll (como CreateThread) para spawnear un hilo nativo del sistema operativo dentro de un programa MQL5, se enfrentará a fallos críticos de acceso a memoria.55 Las librerías y funciones integradas del terminal cliente (incluyendo las funciones de acceso a datos de mercado e instrucciones comerciales) asumen que la ejecución se realiza de manera aislada dentro del almacenamiento local del hilo (Thread-Local Storage) inicializado de manera exclusiva por el motor de MT5 para ese módulo específico.55 Un hilo extranjero instanciado a nivel de sistema operativo carecerá de este contexto de ejecución debidamente inicializado, provocando la desincronización de variables de estado globales, condiciones de carrera no controladas y, en última instancia, el crash crítico de la terminal.55  
La aproximación correcta para procesamientos en paralelo pesados (como el entrenamiento de modelos de aprendizaje automático o cálculos de optimización de carteras en tiempo real) consiste en delegar dicho procesamiento a una DLL externa compilada en C++ nativo.55 La DLL puede implementar de forma segura esquemas de concurrencia avanzados (mediante std::thread o hilos de OpenMP), gestionar de manera independiente la concurrencia a nivel de sistema operativo y transferir los resultados finales consolidados hacia el hilo principal de MQL5 de forma no bloqueante a través de funciones exportadas de lectura de colas seguras.55

### **El Modelo de Simulación en el Strategy Tester**

El Strategy Tester de MetaTrader 5 fue reestructurado para operar de manera distribuida y multi-hilo, permitiendo el aprovechamiento simultáneo de todos los núcleos físicos de la CPU local, de agentes de cálculo distribuidos en red local (Remote Agents) y de los recursos de la red global descentralizada MQL5 Cloud Network.20  
El Strategy Tester opera mediante agentes independientes instanciados como servicios del sistema operativo, los cuales aíslan la ejecución de cada pasada de optimización.56 Al finalizar una simulación, los agentes persisten en caché los datos comprimidos de los resultados históricos por un intervalo de 5 minutos, acelerando las subsecuentes pasadas de optimización que utilicen los mismos parámetros de entrada al omitir el proceso de transferencia de red e inicialización de datos de mercado.9  
El tester ofrece cuatro modos fundamentales de modelado de datos de mercado con implicaciones directas en el rendimiento de los hilos de cálculo de los agentes 9:

1. **Cada Tick (Every Tick)**: Genera secuencias de ticks simulados basándose en los puntos de control de las barras M1 locales, proporcionando un equilibrio óptimo entre precisión microestructural y velocidad de cálculo.9  
2. **Cada Tick basado en Ticks Reales (Every Tick based on Real Ticks)**: Es el modo de máxima precisión operativa.9 Utiliza los datos reales de ticks transados proporcionados e indexados históricamente por el broker.14 El simulador valida sistemáticamente que los ticks reales coincidan con los límites de apertura, máximo, mínimo y cierre de las barras M1 correspondientes; si se detecta una divergencia o pérdida de consistencia física de volumen, el tester descarta los ticks corruptos para ese minuto y recurre de manera segura al generador del modo estándar "Cada Tick".14  
3. **1 Minuto OHLC (1 Minute OHLC)**: Construye la secuencia simulada disparando el evento OnTick() únicamente en las cotizaciones correspondientes a los cuatro puntos de control de apertura, máximo, mínimo y cierre de cada barra de un minuto.9 Reduce drásticamente el tiempo de cálculo de la optimización a cambio de una pérdida en el detalle de la microestructura del precio.9  
4. **Solo Precios de Apertura (Open Prices Only)**: Dispara el evento OnTick() de manera exclusiva en el precio de apertura de cada barra del marco temporal seleccionado para la prueba.9 Es el método más rápido pero introduce restricciones severas de ejecución: el Expert Advisor simulado tiene estrictamente prohibido acceder a datos históricos o indicadores de temporalidades inferiores a la seleccionada para la simulación, y se desactivan los retrasos de red transaccionales dinámicos.9

Durante el backtesting, el Strategy Tester de MT5 emula de forma determinista un entorno de sincronización temporal unificada.9 Las funciones TimeLocal(), TimeTradeServer() y TimeGMT() retornan exactamente el mismo valor de marca de tiempo coincidente con la hora exacta del tick simulado en curso, impidiendo evaluar latencias de red dinámicas calculando desfases horarios.9

## **6\. Acceso a Series Temporales y Microestructura de Mercado**

El acceso optimizado a los datos históricos y a la información de microestructura de mercado en tiempo real es una condición crítica de diseño para el funcionamiento de algoritmos comerciales de alto rendimiento.57

### **API de Copia de Datos de Mercado y Gestión de Memoria**

Para transferir las cotizaciones históricas hacia la memoria activa del programa MQL5, la terminal implementa funciones de copia en cascada que realizan reasignaciones de memoria física de acuerdo al tipo de variable y al arreglo receptor de destino 57:

* CopyRates(): Copia los campos de barras históricas a arreglos estructurados de tipo MqlRates.57  
* CopyTicks() / CopyTicksRange(): Extrae ticks de cotización en formato binario hacia estructuras de tipo MqlTick.59 Al realizar la primera invocación, la terminal inicia una sincronización asíncrona de los archivos de base de datos .tkc locales respecto al servidor del broker, retornando de inmediato únicamente los ticks disponibles localmente mientras la descarga continúa en segundo plano.59 El terminal mantiene una memoria caché de acceso rápido de los últimos 4,096 ticks transados por cada símbolo estándar, extendiéndose automáticamente a 65,536 ticks para instrumentos que cuenten con flujo activo de profundidad de mercado.59  
* CopyBuffer(): Transfiere los valores numéricos calculados de un indicador personalizado desde su handle lógico hacia vectores numéricos locales.62

Las series temporales físicas copias de cotizaciones se indexan secuencialmente de forma predeterminada desde el pasado hacia el presente, ubicando el dato cronológicamente más antiguo en el índice físico 0 del arreglo de memoria.57  
Para trabajar bajo la convención estándar de analistas cuantitativos, donde el índice 0 de la serie temporal apunta de manera dinámica al dato de la cotización o vela activa de mercado, el programador debe invertir la lógica de indexación de la variable receptora invocando la función ArraySetAsSeries(array, true).57  
Cuando el tamaño de los datos de mercado a recuperar de forma recurrente es constante y conocido (por ejemplo, evaluar únicamente la media móvil de las últimas ![][image7] barras), se debe evitar el uso de arreglos dinámicos como buffers de recepción.57 El redimensionamiento asíncrono e implícito realizado por el motor de ejecución sobre arreglos dinámicos indefinidos provoca la de-asignación y reasignación constante de páginas de memoria en el montón (heap fragmentation).57  
Para prevenir esto, el desarrollador debe declarar arreglos estáticos locales de tamaño exacto y predeterminado como receptores de las funciones de copia de cotizaciones, garantizando asignaciones estables ![][image6] en la pila de ejecución del hilo de procesamiento.57

| Función de Copia de Datos | Tipo de Estructura Receptora | Comportamiento del Arreglo Dinámico | Comportamiento del Arreglo Estático |
| :---- | :---- | :---- | :---- |
| **CopyRates()** | Estructura MqlRates.57 | Reasignación automática del tamaño físico del arreglo.57 | Límite estricto de copia. Recomendado para optimizar fragmentación de memoria.57 |
| **CopyTicks()** | Estructura MqlTick.59 | Redimensionamiento dinámico automático. Caché optimizado de ticks.59 | Genera error de buffer pequeño si la cantidad solicitada excede la capacidad estática.61 |
| **CopyBuffer()** | Vector numérico nativo.62 | Asignación elástica administrada por el motor de la terminal.62 | No admite reasignación dinámica física de tamaño durante la llamada.62 |

### **Lectura de la Profundidad de Mercado (DOM)**

El acceso asíncrono de baja latencia a la profundidad de mercado (Libro de Órdenes o DOM) de MetaTrader 5 permite capturar la liquidez microestructural y predecir el impacto de spreads dinámicos o calcular precios medios ponderados por volumen (VWAP) para la colocación óptima de órdenes de ejecución a mercado.58

#### **El Flujo de Registro asíncrono de Depth of Market**

Para registrar y recuperar la información del DOM, un Expert Advisor debe estructurar el siguiente flujo asíncrono de eventos e instrucciones integradas en el lenguaje 58:

1. **Suscripción al Flujo de Red**: Se invoca a la función de suscripción MarketBookAdd(símbolo).58 Si el símbolo seleccionado no se encuentra listado en el panel de Observación de Mercado, la terminal lo inyectará de forma automática para activar el flujo.58 El terminal maneja un contador de referencias de suscripciones al DOM de forma aislada para cada gráfico activo.58 Cada invocación a MarketBookAdd incrementa este contador en 1, mientras que cada llamada a MarketBookRelease lo disminuye en 1\.58 El flujo asíncrono de cotizaciones en tiempo real cesará por completo únicamente cuando el contador alcance el valor cero.58  
2. **Captura del Evento de Actualización**: La terminal inyecta en la cola de eventos el mensaje OnBookEvent(const string \&symbol) inmediatamente después de detectar un cambio en el volumen u oferta de precios de los creadores de mercado.58 El evento es de tipo broadcast por gráfico, por lo que el EA debe validar que el parámetro symbol coincida estrictamente con el instrumento operado.58  
3. **Captura de la Instantánea Física (Snapshot)**: Los eventos recibidos por OnBookEvent son notificaciones de mutación y no contienen la información del libro.58 El EA debe llamar de forma explícita a la función de extracción MarketBookGet(symbol, book) para rellenar un arreglo dinámico de estructuras de tipo MqlBookInfo.58 Esta instantánea reflejará el estado del DOM en el milisegundo exacto de la llamada a MarketBookGet(), el cual puede diferir ligeramente del estado microestructural exacto que disparó el evento original en la cola de mensajes si el mercado está experimentando ráfagas masivas de volatilidad extrema.58

#### **Estructura y Validación de Anomalías de Datos de Microestructura**

La estructura MqlBookInfo contiene la información elemental de cada nivel de oferta o demanda presente en el libro 58:

Fragmento de código  
struct MqlBookInfo  
{  
   ENUM\_BOOK\_TYPE type;         // Tipo de cotización (BOOK\_TYPE\_SELL, BOOK\_TYPE\_BUY, etc.)  
   double         price;        // Nivel de precio del límite de la oferta/demanda  
   long           volume;       // Volumen en unidades enteras  
   double         volume\_real;  // Volumen de alta precisión en punto flotante para cripto/CFDs  
};

La terminal cliente organiza de manera secuencial los elementos de la estructura ordenando los niveles de venta (Ask) en la mitad superior del arreglo físico de memoria y las órdenes de compra (Bid) en la mitad inferior.58 Esto produce un arreglo donde los precios se indexan de manera descendente desde el índice 0 (precio Ask más alto del límite superior de liquidez) hasta el último índice (precio Bid más bajo).58 El desfase central entre ambas mitades del arreglo identifica el spread instantáneo de mercado.58  
No obstante, durante volatilidad extrema o en periodos de baja liquidez, el desarrollador algorítmico debe prever y mitigar anomalías estructurales severas en los datos suministrados por el broker antes de proceder a calcular ratios cuantitativos como el desequilibrio de volumen (volume imbalance) o el precio medio ponderado por volumen (VWAP) 58:

* **Libro Cruzado (Crossed Book)**: Ocurre cuando el precio de una orden de compra (Bid) en el arreglo supera físicamente el precio de una oferta de venta (Ask), distorsionando el cálculo del spread implícito del creador de mercado.58  
* **Niveles de Precio Duplicados**: Se detectan cotizaciones idénticas registradas en índices adyacentes de la instantánea del DOM, lo cual denota inconsistencias de agregación en la pasarela o puente de liquidez del broker.58  
* **Asimetría e Invalidez de Datos**: Desequilibrio total donde el DOM carece por completo de la sección de Ask o Bid, o niveles donde los volúmenes transados se reportan con valores menores o iguales a cero.58

Fragmento de código  
// Algoritmo optimizado de validación y cálculo de volumen ponderado  
bool ProcessAndValidateBook(const string symbol, double \&bid\_vwap, double \&ask\_vwap, const double target\_volume)  
{  
   MqlBookInfo book;  
   if(\!MarketBookGet(symbol, book)) return false;

   int size \= ArraySize(book);  
   if(size \== 0\) return false;

   double accumulated\_bid\_volume \= 0.0;  
   double accumulated\_ask\_volume \= 0.0;  
   double bid\_weighted\_price \= 0.0;  
   double ask\_weighted\_price \= 0.0;

   // Validación estructural secuencial  
   for(int i \= 0; i \< size; i++)  
   {  
      // Detección de precios corruptos o nulos  
      if(book\[i\].price \<= 0.0 || (book\[i\].volume \<= 0 && book\[i\].volume\_real \<= 0.0))  
      {  
         return false;  
      }

      // Validación de ordenación estrictamente descendente  
      if(i \> 0 && book\[i\].price \>= book\[i \- 1\].price)  
      {  
         return false; // Error estructural en el orden de precios del DOM  
      }

      // Cálculo defensivo de VWAP de mercado  
      double current\_vol \= (book\[i\].volume\_real \> 0.0)? book\[i\].volume\_real : (double)book\[i\].volume;  
        
      if(book\[i\].type \== BOOK\_TYPE\_BUY && accumulated\_bid\_volume \< target\_volume)  
      {  
         double fill \= fmin(current\_vol, target\_volume \- accumulated\_bid\_volume);  
         bid\_weighted\_price \+= book\[i\].price \* fill;  
         accumulated\_bid\_volume \+= fill;  
      }  
      else if(book\[i\].type \== BOOK\_TYPE\_SELL && accumulated\_ask\_volume \< target\_volume)  
      {  
         double fill \= fmin(current\_vol, target\_volume \- accumulated\_ask\_volume);  
         ask\_weighted\_price \+= book\[i\].price \* fill;  
         accumulated\_ask\_volume \+= fill;  
      }  
   }

   // Validación final de consistencia física del spread  
   if(accumulated\_bid\_volume \< target\_volume || accumulated\_ask\_volume \< target\_volume)  
   {  
      return false; // Liquidez insuficiente para procesar el volumen solicitado  
   }

   bid\_vwap \= bid\_weighted\_price / target\_volume;  
   ask\_vwap \= ask\_weighted\_price / target\_volume;  
     
   if(bid\_vwap \>= ask\_vwap)  
   {  
      return false; // Condición anómala de libro cruzado (Crossed Book) detectada  
   }

   return true;  
}

## **7\. Conclusiones y Recomendaciones de Ingeniería**

Para desarrollar e implementar sistemas de trading algorítmico robustos y eficientes en la plataforma MetaTrader 5, se deben aplicar las siguientes directrices técnicas derivadas del análisis de su arquitectura y de la semántica del lenguaje MQL5:

1. **Aislamiento y Mitigación de Hilos Gráficos**: No ejecute cálculos matemáticos complejos, ciclos de optimización pesados o llamadas de red dentro de funciones destinadas a Indicadores Personalizados.18 Dichos componentes comparten un único hilo físico de procesamiento con el motor de renderizado del gráfico de precios.18 Delegue estas tareas a hilos dedicados mediante la estructuración de Expert Advisors o Servicios.18  
2. **Gestión de Memoria Determinista sin Aritmética de Punteros**: Los punteros en MQL5 son descriptores de asignación indirecta administrados por la terminal, no direcciones físicas de memoria.27 Implemente una gestión proactiva y segura utilizando la función de validación CheckPointer() sobre descriptores dinámicos antes de deasignarlos con el operador delete.27 Defina variables receptoras estáticas para la copia periódica de cotizaciones para prevenir la fragmentación del montón (heap) provocada por reasignaciones dinámicas continuas de memoria.57  
3. **Procesamiento Defensivo de Eventos de Mercado Asíncronos**: El enrutamiento de transacciones comerciales a través de OnTradeTransaction() y solicitudes por OrderSendAsync() no garantiza una entrega secuencial ordenada de mensajes debido a la topología distribuida del clúster de servidores de MT5.19 Estructure los algoritmos comerciales basando el seguimiento de los trades en identificadores de solicitud únicos (request\_id) para enlazar de manera determinista las notificaciones asíncronas de órdenes, ejecuciones de tratos e historial comercial permanente.47  
4. **Alineación Precisa de Memoria para Interoperabilidad**: Al interactuar con DLLs de C++ nativo o APIs de Windows en sistemas x64 de 64 bits, configure las estructuras compartidas utilizando de forma estricta la directiva de empaquetado pack(8) e inserte variables de relleno de alineación calculando las offsets de memoria de manera exacta mediante el operador offsetof() para evitar fugas y desbordamientos de búfer en memoria.23

#### **Fuentes citadas**

1. Introduction to MQL5 and development environment \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/intro](https://www.mql5.com/en/book/intro)  
2. MT5/MT4 Broker Maintenance and Server Hosting: What You Actually Need \- FINXSOL, acceso: junio 28, 2026, [https://finxsol.com/blog/mt5-mt4-broker-maintenance-server-hosting/](https://finxsol.com/blog/mt5-mt4-broker-maintenance-server-hosting/)  
3. A Guide on MetaTrader 5 Online Trading Platform \- VPFX, acceso: junio 28, 2026, [https://www.vpfx.net/a-guide-on-metatrader-5-online-trading-platform/](https://www.vpfx.net/a-guide-on-metatrader-5-online-trading-platform/)  
4. The Ultimate MT5 Data Bridge: Hybrid REST & WebSocket TraderMade Plugin, acceso: junio 28, 2026, [https://tradermade.com/tutorials/MT5-tradermade-plugin](https://tradermade.com/tutorials/MT5-tradermade-plugin)  
5. Trade Server Architecture Explained, acceso: junio 28, 2026, [https://tradingfxvps.com/trade-server-architecture-to-build-trading-infrastructure/](https://tradingfxvps.com/trade-server-architecture-to-build-trading-infrastructure/)  
6. MT5 Server Requirements: Speed, Hosting, Performance \- Trading FX VPS, acceso: junio 28, 2026, [https://tradingfxvps.com/mt5-trade-server-requirements-for-hosting-and-fast-execution/](https://tradingfxvps.com/mt5-trade-server-requirements-for-hosting-and-fast-execution/)  
7. MetaTrader 5 System Requirements Guide | PDF | Server (Computing) | Backup \- Scribd, acceso: junio 28, 2026, [https://www.scribd.com/document/826852907/Mt5-System-requirement](https://www.scribd.com/document/826852907/Mt5-System-requirement)  
8. The Critical Role of Server Time Synchronization in MetaTrader 5 (MT5) Cluster, acceso: junio 28, 2026, [https://netshopisp.medium.com/the-critical-role-of-server-time-synchronization-in-metatrader-5-mt5-cluster-6d24e5fb8bc9](https://netshopisp.medium.com/the-critical-role-of-server-time-synchronization-in-metatrader-5-mt5-cluster-6d24e5fb8bc9)  
9. How the Tester Downloads Historical Data \- Algorithmic Trading, Trading Robots \- MetaTrader 5 Help, acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/algotrading/test\_preparation](https://www.metatrader5.com/en/terminal/help/algotrading/test_preparation)  
10. What Is A MetaTrader5 Access Server? \- MT Proxy, acceso: junio 28, 2026, [https://mtproxy.io/what-is-a-metatrader5-access-server/](https://mtproxy.io/what-is-a-metatrader5-access-server/)  
11. Introduction to MetaQuotes MT5 Proxy Server \- NetShop ISP, acceso: junio 28, 2026, [https://netshop-isp.com.cy/blog/introduction-to-metaquotes-mt5-proxy-server/](https://netshop-isp.com.cy/blog/introduction-to-metaquotes-mt5-proxy-server/)  
12. MT5 VPS: What It Is and Why Algorithmic Traders Need It \- ForexVPS, acceso: junio 28, 2026, [https://www.forexvps.net/resources/mt5-vps/](https://www.forexvps.net/resources/mt5-vps/)  
13. MT5 Access Server for Forex Brokers: Virtual vs. Dedicated \- NetShop ISP, acceso: junio 28, 2026, [https://netshop-isp.com.cy/blog/mt5-access-server-for-forex-brokers-virtual-vs-dedicated/](https://netshop-isp.com.cy/blog/mt5-access-server-for-forex-brokers-virtual-vs-dedicated/)  
14. Real and Generated Ticks \- Algorithmic Trading, Trading Robots \- MetaTrader 5 Help, acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/algotrading/tick\_generation](https://www.metatrader5.com/en/terminal/help/algotrading/tick_generation)  
15. MT5 White Label Cost: Pricing & Fee Breakdown (2026) \- B2BROKER, acceso: junio 28, 2026, [https://b2broker.com/news/mt5-white-label-cost/](https://b2broker.com/news/mt5-white-label-cost/)  
16. FXCubic Server Architecture Overview | PDF \- Scribd, acceso: junio 28, 2026, [https://www.scribd.com/document/806249149/FXCubic-Server-Architecture-Specifications](https://www.scribd.com/document/806249149/FXCubic-Server-Architecture-Specifications)  
17. Testing Trading Strategies \- MQL5 programs, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/runtime/testing](https://www.mql5.com/en/docs/runtime/testing)  
18. Threads \- Creating application programs \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/runtime/runtime\_threads](https://www.mql5.com/en/book/applications/runtime/runtime_threads)  
19. OnTradeTransaction \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/ontradetransaction](https://www.mql5.com/en/docs/event_handlers/ontradetransaction)  
20. C++ and Metatrader 5 \- Forex Trading Books \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/528](https://www.mql5.com/en/forum/528)  
21. how similar is C++ verses MQL5? \- MetaTrader 4 \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/210326](https://www.mql5.com/en/forum/210326)  
22. MQL is simpler and more user-friendly than C++ and C\#, making it ideal for traders \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/413337/page70](https://www.mql5.com/en/forum/413337/page70)  
23. Structures, Classes and Interfaces \- Data Types \- Language Basics ..., acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/classes](https://www.mql5.com/en/docs/basis/types/classes)  
24. How to fix the problem with MQs' delete operator \- MQL4 and MetaTrader 4 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/148851/page5](https://www.mql5.com/en/forum/148851/page5)  
25. User asks about 7-byte placeholder in Variant B without fillers, referencing MQL5 alignment, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/393227/page64](https://www.mql5.com/en/forum/393227/page64)  
26. Packing structures in memory and interacting with DLLs \- Object Oriented Programming, acceso: junio 28, 2026, [https://www.mql5.com/en/book/oop/structs\_and\_unions/structs\_pack\_dll](https://www.mql5.com/en/book/oop/structs_and_unions/structs_pack_dll)  
27. Object Pointers \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/object\_pointers](https://www.mql5.com/en/docs/basis/types/object_pointers)  
28. Pointers \- Object Oriented Programming \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/oop/classes\_and\_interfaces/classes\_pointers](https://www.mql5.com/en/book/oop/classes_and_interfaces/classes_pointers)  
29. Dynamic creation of objects: new and delete \- Object Oriented Programming \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/oop/classes\_and\_interfaces/classes\_new\_delete\_pointers](https://www.mql5.com/en/book/oop/classes_and_interfaces/classes_new_delete_pointers)  
30. How significant is the correlation between MQL5 syntax/structure & that of C++?, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/268989](https://www.mql5.com/en/forum/268989)  
31. Creating and Deleting Objects \- Variables \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/variables/object\_live](https://www.mql5.com/en/docs/basis/variables/object_live)  
32. GetPointer \- Common Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/common/getpointer](https://www.mql5.com/en/docs/common/getpointer)  
33. Inheritance \- Object Oriented Programming \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/oop/classes\_and\_interfaces/classes\_inheritance](https://www.mql5.com/en/book/oop/classes_and_interfaces/classes_inheritance)  
34. Writing generic code in MQL for Objects \[solved\] \- page 3 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/449290/page3](https://www.mql5.com/en/forum/449290/page3)  
35. Operator overloading \- Object Oriented Programming \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/oop/classes\_and\_interfaces/classes\_operator\_overloading](https://www.mql5.com/en/book/oop/classes_and_interfaces/classes_operator_overloading)  
36. Smart pointers (Modern C++) | Microsoft Learn, acceso: junio 28, 2026, [https://learn.microsoft.com/en-us/cpp/cpp/smart-pointers-modern-cpp?view=msvc-170](https://learn.microsoft.com/en-us/cpp/cpp/smart-pointers-modern-cpp?view=msvc-170)  
37. What are Smart Pointers in C++? (With Examples) \- Codecademy, acceso: junio 28, 2026, [https://www.codecademy.com/article/what-are-smart-pointers-in-cpp](https://www.codecademy.com/article/what-are-smart-pointers-in-cpp)  
38. Tricky C++: Making Memory Management Easier with Smart Pointers | by Drew Coleman, acceso: junio 28, 2026, [https://drewcampbell92.medium.com/tricky-c-making-memory-management-easier-with-smart-pointer-82c3f2a7baf4](https://drewcampbell92.medium.com/tricky-c-making-memory-management-easier-with-smart-pointer-82c3f2a7baf4)  
39. MQL5 Project Types Uses and Best Practice advice needed, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/439380](https://www.mql5.com/en/forum/439380)  
40. Threads in the context of Indicators, Experts and Scripts \- Spreads \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/55539](https://www.mql5.com/en/forum/55539)  
41. New MetaTrader 5 platform build 2615: Fundamental analysis and complex criteria in the Strategy Tester \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/350881](https://www.mql5.com/en/forum/350881)  
42. Reference events of indicators and Expert Advisors: OnInit and OnDeinit \- Creating application programs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/runtime/runtime\_oninit\_ondeinit](https://www.mql5.com/en/book/applications/runtime/runtime_oninit_ondeinit)  
43. OnDeinit \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/ondeinit](https://www.mql5.com/en/docs/event_handlers/ondeinit)  
44. Uninitialization Reason Codes \- Named Constants \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/namedconstants/uninit](https://www.mql5.com/en/docs/constants/namedconstants/uninit)  
45. OnTrade \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/ontrade](https://www.mql5.com/en/docs/event_handlers/ontrade)  
46. OnTrade event \- Trading automation \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_ontrade](https://www.mql5.com/en/book/automation/experts/experts_ontrade)  
47. OrderSendAsync \- Trade Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/trading/ordersendasync](https://www.mql5.com/en/docs/trading/ordersendasync)  
48. MT5, mql5 bugs to be fixed. \- Timeframes \- Expert Advisors and Automated Trading, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/167049](https://www.mql5.com/en/forum/167049)  
49. General rules for working with local projects \- Advanced language tools \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/project/project\_mqproj](https://www.mql5.com/en/book/advanced/project/project_mqproj)  
50. Working with Projects \- Projects and MQL5 Storage \- MetaEditor Help \- MetaTrader 5, acceso: junio 28, 2026, [https://www.metatrader5.com/en/metaeditor/help/mql5storage/projects](https://www.metatrader5.com/en/metaeditor/help/mql5storage/projects)  
51. Developing a multi-currency Expert Advisor (Part 21): Preparing for an important experiment and optimizing the code \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/16373](https://www.mql5.com/en/articles/16373)  
52. New MetaTrader 5 Platform build 4150: Trading report export and new machine learning methods in MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/459335](https://www.mql5.com/en/forum/459335)  
53. New MetaTrader 5 platform build 2650: Background chart loading and MQL5 code profiler improvements, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/352981](https://www.mql5.com/en/forum/352981)  
54. About the MT5 code profiler \- MT5 \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/416279](https://www.mql5.com/en/forum/416279)  
55. Asynchronous and multi-threaded programming in MQL \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/414192](https://www.mql5.com/en/forum/414192)  
56. Strategy Testing \- Algorithmic Trading, Trading Robots \- MetaTrader 5 Help, acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/algotrading/testing](https://www.metatrader5.com/en/terminal/help/algotrading/testing)  
57. CopyRates \- Timeseries and Indicators Access \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/copyrates](https://www.mql5.com/en/docs/series/copyrates)  
58. Reading the current Depth of Market data \- Trading automation ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/marketbook/marketbook\_get](https://www.mql5.com/en/book/automation/marketbook/marketbook_get)  
59. CopyTicks \- Timeseries and Indicators Access \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/copyticks](https://www.mql5.com/en/docs/series/copyticks)  
60. CopySeries \- Timeseries and Indicators Access \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/copyseries](https://www.mql5.com/en/docs/series/copyseries)  
61. CopyTicksRange \- Timeseries and Indicators Access \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/copyticksrange](https://www.mql5.com/en/docs/series/copyticksrange)  
62. CopyIndicatorBuffer \- Initialization \- Matrix and Vector Methods \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/matrix/matrix\_initialization/matrix\_copyindicatorbuffer](https://www.mql5.com/en/docs/matrix/matrix_initialization/matrix_copyindicatorbuffer)  
63. Receiving events about changes in the Depth of Market \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/marketbook/marketbook\_events](https://www.mql5.com/en/book/automation/marketbook/marketbook_events)  
64. OnBookEvent \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/onbookevent](https://www.mql5.com/en/docs/event_handlers/onbookevent)  
65. OnTradeTransaction event \- Trading automation \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_ontradetransaction](https://www.mql5.com/en/book/automation/experts/experts_ontradetransaction)  
66. Discussion of article "Working with sockets in MQL, or How to become a signal provider" \- page 2, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/91815/page2](https://www.mql5.com/en/forum/91815/page2)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAAZCAYAAACsGgdbAAABl0lEQVR4Xu2UvStGURzHD0omWcisRDaDRamHWQZhUgYLJi8ZRBmQScnGIiWy2eQ/8BiYsKgnIXnPQBm8fL+d33k699fxeJ7tDudTn+79fc/v3nM698WYSCSdTMA92CJ1M9yG4/mOFLAIf5SniY4UMA/X4BacgxXJ4XTAhXXqMG3MmtIX2QGn4DqsgeVwGK7Caq9vDO7AjJc5GuABPIMj8Cg5nGQGLhn7Lm7KkZMXYhCeGNvbBTck75GsHuYkq5VsRWrSDS+8mh8te/5kEh6qjBcsqCwE+64CmZ7wU2WPcNerib7mX0IThWDPUCA7V9mb5I5lqV/hNKz0xoKU6QB8meIXORDIjlX2JLkPn57bDLqfHE7ChudApm8agj29gSyrsgfJHXXeeZWx/2WO8yMMwkFuuc6KXWRfINM7yXfQvx/PuTgfZu0qy/Nh7BfoyBh7QZOXheAk7BtVObNLlb1L7uB5zqtdVhA+brd7lP+wQnCn7uA1vDV2Ef3wXrIb+CK9fB9ZM+djbzN2jlY50m/YKP2RSCQSKYFfmwt0vCWgNfwAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEQAAAAWCAYAAAB5VTpOAAACw0lEQVR4Xu2XS6hOURTHl0ckb0YegxsTUhQZKCbEQClRxsqAiZmRGBhTokyQgWQiM5S87kReeSbK83pF8iYMvNa/tfdnnf9d+9zTVya+71f/e8/+r7X3Od/69t5nfyJdunSJGctGJ7NRNZNNZo7qreq36qJqXDXcYqvqk+qrah3FIt6IjZk1sRquMEyquXge8Ej13fm4fq96p/qWvCsptwnIr2WDardrHxLrNNd54I7qlGvfVp137TqeiY15jQOOE6qzUn7gXBBmhJRjzGDVaTaZaDD2xlA7A680mzwPVa8kHiPzWtorCLgnFlvDAeKgajSbzHPpfyO++Q1qZ+DtZzMABZkllr+aYmCB2LJttyDXxWKY7XWU+teyWazjcueVHqbkMygIQO4PH0h8SP/bLUhdLDNZtYtNZZHY0r/EAbBSbGDuWLphyWdyQQ5LnH80/W9SkOlJM1QrknfL5ZWIcraL7ZkhO1RHVD9VSyhW+uAln8GbAmBTQ/5eF9uiGpqumxRkcdJSsVmMzR2zrqeVGfOLDbHx1rPJTBFLPOa80gcv+Uyfu8aD+T7+uklBIo6LxTDDI5ZJfEy4INavTwYoDN+c25mSzzx112vF+vSoRkp1I2y3IKAu/oUNxwOhvlgi+1phIycsTO3Pqc3Au8tmAM4hHvR7rOol/18VBK/0iEnuegL+4BUYDZS9IamN9zvnAHjz2Ax4Qe37Yn2fkN9uQbAcEMMJltmkms9mIhwP5nDXnp08nBw98Pz0xg4dDkhsE8vzx/apyZvmPHA1+aPIB6WC5GJEMVDyAWIn2cRUyRtd/u2xp5Jh5CPyZdVNsd8UgyoZ/cE3hoMflsxL1TkX88sIJ0hM65yLGZXPJh/l7wfOwlsF98dSRn60YQK81XrZdGAsvK3qCvpfcUDsZ0eXREd8600Zr9rJZidzho1OZxUbA/EHyPv9sNrMZFUAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJwAAAAaCAYAAABCUTWIAAAE+UlEQVR4Xu2aW8gWRRjHn6QyOmll2EFKEQoqMSiiE11YZBBG4OnCiyiFTuBFURFZn/UFUUGFdVEgEmheWVKkopbYQSuwMjoQVhfRwc7nA3TQnn+z4zv739nd2dn1+z5f5wcP7zv/Z95nZnefnZ2ZfUUSiUQiMbwcqTaHxcSQcL7auSz2K2eo7VZ7S20K+RJDwyFqd4m5Dt+Qr+/AQb7GoodtLDTkKTFt/al2L/lieVPtURYDWSymP/+qLcq7GnOg2l8sEhPVvhLT5nN5Vw74H2Sxn8ABPsBixhti/NZiwW/HZd+nZmVc6DZgNEacmIR7UW2aU75D7WenHMqHEnZ+Hlf72yk/o7beKbsgzkYWRwqj1K5Ru96xI3I16sEB3sMicZNUn9AqblPbLqavllvExHvI0ZqyS+ISDv34mkUxsU5kMZBfpPz8XCxFH8o/kWaB72UWh5uzxHQMz/0z1U5WO07tGLUDnHohIM4Ai0SbhHtdzG8fIx1abEyMvFjkxCTcleJvF9pEFgOpSjjoH5GGa1UG6m9hMQY8ApapHZaVMRItVntE8nd/HTjBT7DYgr2dcIeqPS35Yxwt8Ql3qtqT2feYhMP5t21PzrTTsnIsZQnHN8V0tYN6bi+oHzKnrgQneI3aPDEBB6V30nCxfZ31gQPYxGJL0DbmMFW0STgft4uJdyM7AnD7EZNwYLX0kg6r89/y7saUJRymONBxvKvEJPtmqV5goH7bBdr/k1RgE+5ux4eRztdZH6+w0BK7JTKeHUTXCYdYP7AYACbTdvEBYhMOvCe9pIO12RIqSzg8iWx8F5TfIc3ythTrNwaTZPCBFIPhLmetDNQ7u8ZCHs94lGBOhXiXks9HlwmH+cx3LAZwgpjVnUtswv2uNjv7vkN6SXH4nhrNKEs4bG9AX0k6Vui++hbcDKgzkx1NQSNbScNyvKpxF9S7osYO3lO7nAvEzKsQ73Ty+egq4bAX9z6Lgfjaj0m4FWqvknahmFixfStLuKvE6PNJL6tveViM/wYJG0BKQZDLPBqe8SFg36dL8DoF7R/FDqKLhFuotoG0JjExnWDD77/MvmNxEgJ+YxcLLndKs/64lCXQGDE65nIuGGF99cFSKfc1Yq4UA2FYt9rRUtw6YI5Xe5bFlqD9tosGbM9UcZHachalOKLUxWHQJx7hsC1U9eYAv5nForJA7WOnXBfHpSzhAHQkEWtV9VsvGsC7UmzkeUfDa48QcIJxN3YF2q+70HgTgXrHskN6K7617MjAZqo9wWz3OfXq4jAY0VCf50ffZ/qtpFvwBwW+DgCaOx2pi+Pyh/hjAmzMsw9lbAj7gK+Tfbh/pHg3Yk/Gnvyx5KvCbl5eJ+aChj5OfCDOAIsZWL7jRvhc7bPs81vJj1YYmaHxSbVgkWCPke08p15dHBeMKF9Ir09YhNg3LHh1hmT5NCv7uFpMO9gOwXXBd3f1C0Li/Kq2U0w/YOgTVt/8yF4ipo1Psk+7YPEB/0ssjhROUrtZzAYyXk8Nin8UqgIH6G7TxBLzLtJHV3HWsRBJV3FCwfV4gcV+Agd4P4sNOUXMHmNbuoqDEWwCixF0FacJuB54SdC34ADL/rkQCl6kd0FXcULnw3V0FacJuB543dm3zBBzkFj9TiJfKE3/MFBGV3H2Ra4Vs9n7Izv6lXPEHHRi6Llc7RIxf+RMJBKJRCKRSOyH/Afbsmcq3By51AAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAbCAYAAABIpm7EAAAAiklEQVR4XmNgGAVDGnwH4k9AfBjKfwrEJ4D4PxCfhimCgTQgVgdiGwaIgn9IcspQMRTwB0pPZ4BIMiLJaUHFsAKQxC80sfVQcawAJHEMTewjVBwrAEl4YBGrRBMDg3AGTJNCkcSEgHgKkhzDZQZMDVuQxF4gS4AAKKQmo4mxMkA0gLAAmtwoGGoAAFUtI0LZEJOuAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAAAWCAYAAACVIF9YAAACc0lEQVR4Xu2WzUuVQRTGjxZKZEkFBbVRSykJw0AKIiISgnDjIj+gpYvaFLayXeS+3Gi4Ewwigigo2vQXFIQthGjRQsSFEX6AaIXYeZxz7nvuacZLpHHv5f7g4Z15zsy897zzdYkqVCh7mrxRrBxkzbE2WF9Z9fnhP/hGoS2028WKjhoKySlVFH54u/FiHKadSRBjbiuL3mBOs9a96cAsl0SCGPCW886IvxX7aPsTfEiF3/vXLFAY9J3xMKsXTT1GHYV+WOJtrEescVa1aYNyh8Sx5C+Lf4B1gXXeeL2U7etrov0SU3BWvGJ9YN1xMXCfNcOaYJ1VcxdlA0NIrkuDW6AJrlGYcXBOvJtSx9jD4kEPxD9GYQvAe8yqZd017VCGsM8VjeOMAF9YP7LwZgyrSsHE5ThK+UlO22CCvRTannD+DfGRnDIinuUla4/z9P0erAT4V5wPTz+u75c7JK+yVqV8ibKXfNIGCTTBRh+g4E9GvDFX96QSHKXgH3GChxUCtC8+XN72ig2IdRzzLYUS/O481HVM7L8BE1NSCc5S8Dsj0vfrtWVF17UQAT4OgRSFEnzvvFPit1K2Yjw+wdfyfOr8GNjHChLfbI91muqY8pVUgsfFb3E+gI+ZTC1/n+BHeeL0hN9jYgAHzj0p5x0qTLcW0FFPNwX1Ked5NMFl5/+idALYg+iDayLGW8oSPMnqMzHMJmJ2puZNGbFmUx8yZVqi0OCzPJ/YYAIk+EbK9r/pYK5FHDtDMXS/4RrwIGF9z0/WIRPDPY4DRuPPTOy/gcv3tjdLHXxN3I1gxQbKBSSIC/o5q9/FygKcqi9YDc6v8K/8BthGrpim1sCOAAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAaCAYAAAAue6XIAAABwklEQVR4Xu2WTytEURjGH/9ZEAvKAgufQWQjf8IHUCxkslD2SvIRlJIsfAcfwYaNZCU2oiyQBRaUQv6+r3MuM49773tGQ9H86qnxO89953TnzjFAkb/DIAuDZkkpy+/QJlmVrEjqaC2OackcywBeWeTDEtyACf93q+RCcv/R+EqL5JxlFvVI3lSl5IWlhX4cOnCTFzxPSB6q11WTa5Sc+LUoSWxJFlmmocOOWWbRB9fpJ98teSDHWJstQ/p6Dmewy9GdXyP/CPtZtTar6PoAS6YHrrhBnmmA612TV1dDjgnZ7IFkhyWjd0YH8TPHjMP1drNcrXcWIZudh90JGqQcwvX0iIro9c4i5D3GYHSaEDZIietNxrg44q5lOmF0om/hHS8QI3A9PtYy3luEbLYDdidoUFKnC/GeSbo+m1HYHdwgvRQd7BW8gM8TwiJks3r8WZ13tLTHUriEOy3S0Gv1X2YaIZvdR+5Jk8oV3MBtuGdYX+tDb6G9GZYePZP1N8Opj77mczpC5wyxLDSzkluWeVIC+84XDH2jcpZ5sC5ZZvlTDEuOWAaivzmeWf40C5IplgH8+kYjMiwM2iVVLIsU+Q+8AcPof4U5yGDQAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAABCklEQVR4Xu2TMWpCQRRFH9hKTCFWWYBYZQtWbkPIBjRdiGKhbsBOEERIobgAkXSCdSKIpUsQVBTEIt6X+T/O3P+HFGL3Dxzk3fdmRnRGJOFeVOEIFoI6Dz9g5W/iSh3u4BG+UM+hBX/IL2fCsIKfVr2Ec6t2aMAOHMAaTLntXx7EHMZo9sihohsVOSS+xb9pj0PlXf7fNPxZGF8ub7AtptkPPrvOhH+xL5dXOKVMB5tUxy325bHwMNchvlzWsEzZWW7YNB2EB8p5WB9HZLGYTP+PCPqtGB22L3Z4uH2HM0EWiz63BXyCObiFe2fCMIMbqz6J546G6KlDOIYl6tk8w4mYF5ilXkLCPbgAZ7xMv3UJ6PMAAAAASUVORK5CYII=>