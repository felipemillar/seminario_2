# **Arquitectura de Ejecución y Semántica de Sistemas en MQL5: Guía de Ingeniería para Desarrolladores de C++, Java y Python**

MQL5 no es simplemente una herramienta de scripting para plataformas de corretaje financiero; constituye un lenguaje de programación formal, fuertemente tipado, de tipado estático y orientado a objetos.1 Diseñado originalmente para interactuar con la infraestructura del terminal cliente de MetaTrader 5, MQL5 hereda la sintaxis y una parte considerable de la semántica de la especificación C++98, introduciendo modificaciones arquitectónicas críticas que rigen la seguridad del hilo de ejecución, la gestión de memoria y el aislamiento del sistema operativo anfitrión.1  
Para los ingenieros de software procedentes de ecosistemas de desarrollo como C++, Java o Python, dominar MQL5 requiere desactivar asunciones comunes relativas a la aritmética de punteros, la resolución de plantillas, la gestión de la memoria dinámica y la estructura de compilación. Este informe técnico desglosa la especificación formal del lenguaje y documenta de forma exhaustiva sus componentes clave.

## **1\. Sistema de tipos e infraestructura de datos predefinidos**

El sistema de tipos de MQL5 es riguroso. La máquina virtual del terminal cliente no implementa mecanismos de tipado dinámico ni resolución en tiempo de ejecución de tipos libres (duck typing), aproximándose directamente al paradigma de C++.

### **Tipos primitivos y su representación binaria**

MQL5 hereda la representación de tipos enteros y de punto flotante de la arquitectura x86/x64 estándar.3 Los tipos primitivos, su tamaño en memoria y su análogo en C++ se detallan en la siguiente tabla:

| Tipo MQL5 | Tamaño (Bytes) | Rango de Representación | C++ Análogo | Comportamiento en la Máquina Virtual MQL5 |
| :---- | :---- | :---- | :---- | :---- |
| char | 1 | ![][image1] a ![][image2] | char | Entero con signo de 8 bits para datos de texto simples.5 |
| uchar | 1 | ![][image3] a ![][image4] | unsigned char | Requerido para almacenamiento de datos binarios planos.5 |
| bool | 1 | ![][image3] (false), ![][image5] (true) | bool | Operaciones lógicas fundamentales.3 |
| short | 2 | ![][image6] a ![][image7] | short | Entero de 16 bits con signo.5 |
| ushort | 2 | ![][image3] a ![][image8] | unsigned short | Representación interna de caracteres Unicode.5 |
| int | 4 | ![][image9] a ![][image10] | int | Entero de 32 bits para índices y cálculos generales.5 |
| uint | 4 | ![][image3] a ![][image11] | unsigned int | Requerido para máscaras de bits y contadores.5 |
| long | 8 | ![][image12] a ![][image13] | long long | Entero de 64 bits para identificadores persistentes.5 |
| ulong | 8 | ![][image3] a ![][image14] | unsigned long long | Utilizado para tickets de órdenes de mercado y transacciones.5 |
| float | 4 | Precisión simple (IEEE 754\) | float | Utilizado para optimizar memoria en grandes volúmenes de datos. |
| double | 8 | Precisión doble (IEEE 754\) | double | Tipo por defecto para precios históricos y cálculos analíticos. |
| datetime | 8 7 | Segundos desde 01/01/1970 7 | \_\_time64\_t | Almacenamiento plano en entero sin signo de 64 bits. |
| color | 4 8 | Formato hexadecimal RGB 8 | int / COLORREF | El primer byte es ignorado; los 3 restantes guardan RGB.8 |

Los caracteres literales (ej. 'A') se procesan bajo el capó como enteros de tipo ushort, que representa el índice del carácter dentro de la tabla de caracteres Unicode.6 Por ende, almacenar un carácter literal en una variable de tipo char de 8 bits provocará una truncación implícita si el valor del carácter supera ![][image2].5 Además, los enums en MQL5 son fuertemente tipados pero convertibles de forma implícita a int.4 No se permite declarar enumeraciones anónimas.11

### **Tipos compuestos: estructuras, clases y uniones**

MQL5 impone límites estrictos entre estructuras y clases, alejándose del paradigma de C++ donde la única discrepancia radica en el nivel de acceso por defecto 2:

* **struct**: No pueden heredar de una clase, ni una clase de una estructura.12 No admiten funciones virtuales ni herencia múltiple.2 Por defecto, todos sus miembros de datos son públicos.12 Los datos se alinean contiguamente en la memoria de manera exacta, equivalente a la directiva de compilación \#pragma pack(1) en C++.12 Si la estructura contiene tipos dinámicos (como string o arrays dinámicos), el compilador inyecta un constructor implícito que inicializa estos elementos de forma segura.12  
* **class**: Soporta encapsulamiento, herencia simple y polimorfismo mediante funciones virtuales.12 Por defecto, sus miembros son privados.12 Una clase siempre posee una tabla de funciones virtuales (vtable) implícita para la gestión interna de sus destructores.2  
* **union**: Permite compartir el mismo espacio de memoria física entre múltiples miembros de diferentes tipos.12 Su principal uso radica en la serialización de datos: permite descomponer estructuras simples (sin punteros ni objetos dinámicos) en un array contiguo de bytes uchar para su transmisión a través de sockets o funciones API externas.12

### **Arrays estáticos y dinámicos**

MQL5 soporta arrays con un máximo de 4 dimensiones.14 Al declarar un array dinámico (sin especificar el tamaño del primer índice en los corchetes), el compilador genera un objeto descriptor de array dinámico de control interno que asocia la memoria contigua en el montón (heap) con la variable lógica.14  
Cuando un array estático se declara dentro de una estructura, no se genera este objeto descriptor para asegurar la compatibilidad estructural de la API de Windows.14 No obstante, al pasar estos arrays estáticos como parámetros a funciones, el compilador crea de forma transparente un descriptor dinámico temporal en el stack que apunta al búfer estático preasignado.14

### **Estructuras de datos predefinidas de la API de MetaTrader 5**

La API expone exactamente 12 estructuras de control nativas esenciales para interactuar con la plataforma de corretaje. El siguiente cuadro resume detalladamente sus campos de control y propósitos:

| Estructura Predefinida | Campos y Representaciones Binarias | Propósito en el Runtime de MQL5 |
| :---- | :---- | :---- |
| **MqlDateTime** | year, mon, day, hour, min, sec, day\_of\_week, day\_of\_year.17 | Representación de fecha y hora descompuesta en enteros de 32 bits.17 |
| **MqlParam** | type, integer\_value, double\_value, string\_value. | Almacena parámetros dinámicos para la inicialización formal de indicadores. |
| **MqlRates** | time 18, open, high, low, close 18, tick\_volume, spread, real\_volume. | Almacena la estructura completa de un elemento de barra histórica (vela). |
| **MqlBookInfo** | type, price, volume, volume\_real. | Almacena registros de profundidad de mercado de la cartera de órdenes (DOM). |
| **MqlTradeRequest** | action 19, magic, order 19, symbol, volume, price 19, sl, tp 19, deviation 19, type, type\_filling 19, type\_time 19, expiration 19, comment 19, position 19, position\_by.19 | Define de forma determinista una instrucción comercial de entrada al mercado. |
| **MqlTradeCheckResult** | retcode, balance, equity, margin, margin\_free, margin\_level, comment. | Almacena el resultado de la comprobación estática previa al envío de una orden. |
| **MqlTradeResult** | retcode 20, deal, order 20, volume, price 20, bid, ask 20, comment 20, request\_id 20, retcode\_external.20 | Contiene la respuesta síncrona del servidor ante un envío de OrderSend().16 |
| **MqlTradeTransaction** | deal, order, symbol, type, party, price, trigger, volume, position, position\_by. | Estructura asíncrona que detalla eventos de cambios en cuentas y transacciones. |
| **MqlTick** | time, bid, ask, last, volume, time\_msc, flags 21, volume\_real. | Registra fluctuaciones de cotización instantánea de alta resolución. |
| **MqlCalendarCountry** | id, name, code, currency, currency\_symbol. | Almacena información geográfica y monetaria del calendario económico.22 |
| **MqlCalendarEvent** | id, type, sector, importance, mode, source\_url, event\_code. | Almacena especificaciones de los eventos macroeconómicos programados.22 |
| **MqlCalendarValue** | id, event\_id, time, period, actual\_value, forecast\_value, revised\_value, prev\_value. | Registra los datos de publicación real, estimada e histórica de un evento.22 |

### **Conversión de tipos y trampas de precisión**

Las conversiones implícitas de tipos flotantes a enteros truncan los decimales de forma directa. La conversión implícita de tipos de datos de un tamaño superior a uno inferior (ej. long a int o double a float) provoca pérdidas catastróficas de datos sin generar errores en tiempo de compilación 9:

Fragmento de código  
int   max\_int   \= 2147483647;  
float lossy\_flt \= max\_int; // lossy\_flt contendrá 2147483648.0 debido a limitaciones de mantisa (IEEE 754\) 

La adición de una string con cualquier tipo numérico promueve implícitamente todo el conjunto a un operando de cadena de texto (string), lo que puede causar fallas de cálculo silenciosas si se agrupan expresiones aritméticas complejas sin la separación adecuada de paréntesis.9

Fragmento de código  
//+------------------------------------------------------------------+  
//| EJEMPLO COMPILABLE 1: SISTEMA DE TIPOS Y TRAMPAS DE CONVERSIÓN   |  
//+------------------------------------------------------------------+  
\#property strict

// Estructura sin alineación explícita (MQL5 emula \#pragma pack(1) nativo)   
struct UnalignedStruct  
{  
   char   id;            // Offset 0 (1 Byte)  
   double value;         // Offset 1 (8 Bytes) \- Desalineado en C++ estándar   
};

// Estructura con alineación manual para compatibilidad DLL   
struct AlignedStruct  
{  
   uchar  slippage;      // Offset 0 (1 Byte)  
   char   reserved1;     // Offset 1 (1 Byte) \- Relleno   
   short  reserved2;     // Offset 2 (2 Bytes) \- Relleno   
   int    reserved4;     // Offset 4 (4 Bytes) \- Relleno   
   double limit\_price;   // Offset 8 (8 Bytes) \- Alineado a borde de 8 bytes   
};

union BinaryPacker  
{  
   AlignedStruct data\_payload;  
   uchar         raw\_bytes; // Mapeo plano para serialización directa   
};

void OnStart()  
{  
   // Demostración de trampa de casting implícito de signo (bit preservation loss)   
   uint unsigned\_val \= 4294967295; // Valor máximo de uint (0xFFFFFFFF)   
   int  signed\_val   \= unsigned\_val; // signed\_val se convierte silenciosamente en \-1   
     
   PrintFormat("unsigned\_val: %u | signed\_val casted: %d", unsigned\_val, signed\_val);   
     
   // Trampa de conversión string-número en operaciones de adición   
   string msg \= "Resultado: " \+ 10 \+ 20; // Evaluará como "Resultado: 1020" y no "Resultado: 30"   
   Print(msg);   
}

## **2\. Programación Orientada a Objetos (POO) en MQL5**

La implementación de la Programación Orientada a Objetos en MQL5 se asemeja al estándar C++ tradicional, pero introduce restricciones severas diseñadas para garantizar la estabilidad del hilo del terminal.1

### **Herencia, interfaces y modificadores de acceso**

**MQL5 no soporta herencia múltiple de clases**.2 Un diseño arquitectónico que requiera composición jerárquica cruzada debe resolverse utilizando interfaces. La palabra clave interface es una abstracción sintáctica para clases abstractas puras. Todos sus métodos miembros son implícitamente public y virtual por defecto.  
Los modificadores de acceso (public, protected, private) y las directivas de visibilidad de herencia actúan de manera convencional bajo la norma de C++98.24 No obstante, la herencia en MQL5 de clases base a descendientes debe ser siempre explícitamente definida, heredando de forma predeterminada como tipo private si se omite el especificador en la cabecera de declaración de la subclase.24

### **Polimorfismo y métodos virtuales**

A diferencia de C++, **los objetos de clase en MQL5 siempre poseen una tabla de funciones virtuales (VMT)**, incluso si la clase no define métodos virtuales explícitamente.2 Esto se debe a que la máquina virtual requiere un punto de entrada dinámico consistente para ejecutar de manera segura los destructores implícitos de los descriptores cuando el programa es descargado o removido del terminal cliente.2  
Las estructuras de datos (struct) no soportan en ningún caso métodos declarados con el especificador virtual ni herencia de clases.12

### **Sobrecarga de operadores y restricciones**

MQL5 admite la sobrecarga de un subconjunto específico de operadores utilizando la firma de función precedida por la palabra clave operator.25 No obstante, impone limitaciones rígidas frente a C++ 2:

* Los operadores de asignación (=), adición binaria (+, \-, \*, /), lógicos, relacionales y el indexador de arrays (\`\`) pueden ser sobrecargados.25  
* **No se permiten operadores sobrecargados definidos fuera del cuerpo de la clase o estructura**. Todos los operadores deben ser necesariamente funciones miembro de la entidad correspondiente.

### **Clases y funciones de plantilla (Templates)**

Las plantillas admiten la parametrización formal de clases y funciones mediante tipos genéricos utilizando el token template \<typename T\>.26 Un bloque de plantilla en MQL5 está restringido a un máximo de 8 parámetros formales de tipo.26  
El motor de resolución del compilador es sustancialmente más rudimentario que el estándar C++ moderno; técnicas complejas como la metaprogramación de plantillas o la aplicación de SFINAE (Substitution Failure Is Not An Error) no se pueden implementar debido a limitaciones de deducción automática de argumentos. Además, las funciones declaradas como plantillas no pueden llevar los especificadores virtual ni exportarse en DLLs.26

Fragmento de código  
//+------------------------------------------------------------------+  
//| EJEMPLO COMPILABLE 2: PROGRAMACIÓN ORIENTADA A OBJETOS          |  
//+------------------------------------------------------------------+  
\#property strict

// Definición formal de una Interfaz en MQL5   
interface IRunnable  
{  
   bool Run(const double input\_val);  
};

// Clase base que gestiona polimorfismo mediante VMT \[12, 28\]  
class BaseProcessor : public IRunnable  
{  
protected:  
   double m\_threshold;

public:  
   BaseProcessor(double thr) : m\_threshold(thr) {}  
     
   // Destructor implícitamente virtual debido al comportamiento de la VMT en MQL5   
   \~BaseProcessor() { Print("BaseProcessor Destruido"); }   
     
   // Implementación del método de la interfaz  
   virtual bool Run(const double input\_val) override  
   {  
      return (input\_val \>= m\_threshold);  
   }  
};

// Demostración de clases de plantilla (Templates) \[27\]  
template \<typename T\>  
class SafeArrayContainer  
{  
private:  
   T m\_internal\_array;

public:  
   SafeArrayContainer(int size)  
   {  
      ArrayResize(m\_internal\_array, size); \[15\]  
   }  
     
   // Sobrecarga estricta del operador de indexación\[25, 27\]  
   T operator(int idx)  
   {  
      int max\_idx \= ArraySize(m\_internal\_array) \- 1; \[29\]  
      if(idx \< 0 || idx \> max\_idx)  
      {  
         Print("Índice fuera de límites. Retornando elemento de resguardo.");   
         static T fallback\_element;  
         return fallback\_element;  
      }  
      return m\_internal\_array\[idx\];  
   }  
     
   // Firma para mutación de elementos  
   void SetValue(int idx, T val)  
   {  
      if(idx \>= 0 && idx \< ArraySize(m\_internal\_array))  
         m\_internal\_array\[idx\] \= val; \[29\]  
   }  
};

void OnStart()  
{  
   // Demostración práctica de polimorfismo  
   IRunnable\* executor \= new BaseProcessor(1.5); \[30, 31\]  
   if(CheckPointer(executor)\!= POINTER\_INVALID)   
   {  
      bool state \= executor.Run(1.8); // Resuelve dinámicamente vía VMT  
      PrintFormat("Resultado de la ejecución del procesador: %s", (string)state);   
        
      // Debe destruirse explícitamente ya que no hay recolector de basura \[30, 33\]  
      delete executor;   
   }  
     
   // Instanciación de clase de plantilla genérica \[27\]  
   SafeArrayContainer\<double\> double\_store(5);  
   double\_store.SetValue(0, 10.5);  
   PrintFormat("Elemento en posición 0: %.2f", double\_store);   
}

## **3\. Manejo de memoria y gestión del montón (Heap)**

El ciclo de vida de los datos en MQL5 impone una separación estricta de responsabilidades entre la pila (stack) de ejecución y el montón (heap) dinámico.15 **MQL5 carece por completo de un recolector de basura (Garbage Collector)**.33

### **Gestión de memoria y punteros inteligentes**

MQL5 utiliza punteros de clase representados por descriptores lógicos de 8 bytes, que actúan bajo la sintaxis clásica de desreferenciación directa.2 El ciclo de vida de las variables se controla explícitamente por el programador o de forma implícita por el sistema dependiendo de su inicialización 30:

* **Punteros Automáticos (POINTER\_AUTOMATIC)**: Instanciados directamente al declarar objetos locales o miembros internos de clases (ej. CObject obj;).30 Son creados en el stack y su liberación es controlada por el entorno de ejecución al salir de la visibilidad del bloque.14 Intentar aplicar delete sobre estos objetos generará un error en tiempo de compilación o ejecución.30  
* **Punteros Dinámicos (POINTER\_DYNAMIC)**: Instanciados mediante el operador new (ej. CObject\* obj \= new CObject();).30 Residen en el heap y deben liberarse manualmente invocando el operador delete.30

La función CheckPointer() evalúa la validez de un puntero y devuelve un valor de la enumeración ENUM\_POINTER\_TYPE.30 Un intento de desreferenciar un puntero destruído o que apunte a NULL detendrá de inmediato el hilo de ejecución mediante una interrupción crítica del terminal.30

### **Redimensionamiento físico y el parámetro de reserva**

La gestión dinámica de colecciones de memoria se realiza a través de la API ArrayResize().15 Esta función acepta tres parámetros fundamentales: ArrayResize(array, nuevo\_tamaño, reserva).15  
El parámetro reserva representa el elemento central para evitar la fragmentación física de la memoria.15 Si se omite, cada incremento en el tamaño del array forzará un proceso de reasignación física en el montón (búsqueda de un nuevo bloque contiguo de memoria y copia completa de los elementos existentes).35 Si el parámetro de reserva es mayor a cero, la máquina virtual preasigna un segmento de memoria superior que actúa como área de reserva interna 15:

Fragmento de código  
// Comportamiento de preasignación física  
ArrayResize(arr, 1, 1000000); // Se reserva memoria contigua para 1,000,000 de elementos de inmediato 

Las llamadas subsiguientes a ArrayResize() dentro del límite preasignado solo actualizarán los metadatos lógicos del array en tiempo de microsegundos, evitando reasignaciones del heap.15 No obstante, si el tamaño del array es reducido a cero (ArrayResize(arr, 0)), la memoria reservada no se libera automáticamente al sistema, manteniendo la reserva física del búfer interna.35 Para liberar de inmediato la memoria de un búfer dinámico, debe utilizarse explícitamente ArrayFree().15

### **Fugas de memoria (Memory Leaks) e impacto en el Runtime**

Cuando un script, indicador o Expert Advisor finaliza su ejecución, la máquina virtual realiza un análisis exhaustivo del heap asignado al programa. Si detecta descriptores dinámicos que no fueron liberados con el operador delete, registrará en el diario del terminal de MetaTrader 5 un reporte detallado con la cantidad de leaks detectados y el tamaño de la memoria huérfana.33  
A nivel operativo de producción, dado que los programas corren en hilos continuos de alta frecuencia, una fuga persistente saturará el proceso de 64 bits terminal64.exe, provocando latencia de procesamiento o la detención del terminal completo.33

### **Límites de direccionamiento físico**

La memoria de un programa MQL5 se ejecuta dentro de los límites del espacio de direcciones virtuales del proceso de MetaTrader 5 (un espacio completo de 64 bits bajo arquitecturas de Windows x64).35 Sin embargo, existen restricciones de subprocesamiento importantes:

* Los indicadores técnicos se ejecutan en un único hilo común compartido por todos los indicadores cargados para un símbolo específico.38 Un desbordamiento de memoria o un error de pila en un indicador congelará o detendrá el procesamiento de datos del resto de indicadores asociados a ese instrumento financiero.38  
* El tamaño máximo absoluto del segmento de pila (stack) asignado para scripts y Expert Advisors es de 8 MB, mientras que para indicadores técnicos está fijado de forma rígida en 1 MB.39

Fragmento de código  
//+------------------------------------------------------------------+  
//| EJEMPLO COMPILABLE 3: GESTIÓN DE MEMORIA Y REDIMENSIONAMIENTO    |  
//+------------------------------------------------------------------+  
\#property strict

class ManagedBlock  
{  
public:  
   double m\_buffer;  
     
   ManagedBlock()  
   {  
      // Evitamos fragmentación reservando espacio de búfer masivo   
      ArrayResize(m\_buffer, 0, 10000);   
   }  
};

void OnStart()  
{  
   // Monitoreo de memoria disponible y utilizada mediante variables del sistema   
   long mem\_available \= TerminalInfoInteger(TERMINAL\_MEMORY\_AVAILABLE);   
   long mem\_used      \= MQLInfoInteger(MQL\_MEMORY\_USED);   
   PrintFormat("Consumo de inicio: %d MB | Disponible Sistema: %d MB", mem\_used, mem\_available); \[23, 35\]  
     
   // Creación segura de un objeto dinámico   
   ManagedBlock\* ptr\_block \= new ManagedBlock();   
     
   if(CheckPointer(ptr\_block) \== POINTER\_DYNAMIC)   
   {  
      // Redimensionamiento de alto rendimiento dentro de la reserva lógica   
      for(int i \= 1; i \<= 5000; i++)  
      {  
         ArrayResize(ptr\_block.m\_buffer, i, 10000);   
      }  
      PrintFormat("Tamaño final del búfer: %d", ArraySize(ptr\_block.m\_buffer)); \[23, 29\]  
   }  
     
   // Liberación rigurosa de memoria para prevenir leaks persistentes \[30, 33\]  
   if(CheckPointer(ptr\_block) \== POINTER\_DYNAMIC)   
   {  
      delete ptr\_block;   
   }  
}

## **4\. Sistema de preprocesamiento e infraestructura de compilación**

El preprocesador actúa antes de la compilación binaria del código fuente.40 Sus directivas resuelven la composición final de la unidad de traducción antes de su análisis gramatical.40

### **Directivas de preprocesamiento y uso de \#property**

* **\#define**: Establece reglas de sustitución léxica para constantes y macros parametrizadas complejas.39  
* **\#include**: Inserta textualmente la cabecera indicada en el archivo fuente principal.39 El uso de corchetes angulares \<\> apunta a directorios de la biblioteca estándar de MQL5, mientras que las comillas dobles "" buscan la ruta relativa local del archivo fuente.40  
* **\#property**: Permite inyectar metadatos descriptivos directamente en el encabezado del ejecutable compilable final .ex5.39 El terminal cliente de MetaTrader 5 lee estas propiedades en modo estático sin cargar ni inicializar el hilo de ejecución.39 Ejemplos cruciales son \#property strict (activa la validación restrictiva de tipos de datos) 39, \#property stacksize (redefine el tamaño de la pila) 39, o parámetros de compilación condicional para el simulador de estrategias, como \#property tester\_file.39  
* **\#import**: Define el mapa de importación de funciones.39 Permite enlazar dinámicamente tanto módulos compilados externos de MQL5 (.ex5) como bibliotecas nativas de enlace dinámico de C++ compiladas para arquitecturas Windows de 64 bits (.dll).39

Fragmento de código  
// Sintaxis de importación externa DLL  
\#import "user32.dll"  
int MessageBoxW(int hWnd, string lpText, string lpCaption, uint uType);  
\#import

### **Proceso de compilación y la unidad de traducción monolítica**

En C++, el compilador procesa múltiples archivos .cpp de forma aislada para generar archivos de objeto independientes .obj que luego son unificados en una fase de enlace (linking) externa.  
En MQL5, **no existe la etapa de linkado externa**. Todo el proceso de compilación opera bajo un esquema de **unidad de traducción monolítica**:

1. El compilador del MetaEditor de MetaTrader 5 recibe como entrada únicamente el archivo principal de ejecución activo con extensión .mq5.1  
2. El preprocesador parsea de forma secuencial y lineal el archivo de cabecera .mqh importado mediante \#include.39 Los archivos de cabecera no se pueden compilar de forma aislada como código ejecutable independiente, y sus directivas internas alteran directamente la estructura global del archivo primario.39  
3. El motor del compilador genera como única salida final un archivo empaquetado binario ejecutable estructurado con extensión .ex5.39 El bytecode embebido dentro del .ex5 es interpretado de manera segura en tiempo de ejecución por el motor de MetaTrader utilizando aceleración JIT (Just-In-Time) directa a nivel de ensamblador de CPU x64.

Fragmento de código  
//+------------------------------------------------------------------+  
//| EJEMPLO COMPILABLE 4: PREPROCESAMIENTO Y METADATOS              |  
//+------------------------------------------------------------------+  
\#property strict  
\#property copyright "Senior Systems Developer"   
\#property version   "1.05" 

// Macro parametrizada con control de ámbito seguro \[27, 40\]  
\#define SAFE\_DIV(a, b) ((b \== 0.0)? 0.0 : (a / b))

// Inclusión del archivo de cabecera de la biblioteca estándar de control  
\#include \<Controls\\Button.mqh\> \[36, 39\]

// Declaración del uso de compilación condicional   
\#ifdef \_DEBUG  
   \#define DEBUG\_LOG(msg) Print("DEBUG: " \+ msg)   
\#else  
   \#define DEBUG\_LOG(msg)  
\#endif

void OnStart()  
{  
   double x \= 10.5;  
   double y \= 0.0;  
     
   // Evaluación segura por macro del preprocesador  
   double res \= SAFE\_DIV(x, y);  
   PrintFormat("Resultado de la división de protección: %.2f", res);   
     
   // Telemetría condicional basada en banderas del compilador   
   DEBUG\_LOG("Finalizada de forma segura la ejecución OnStart()");  
}

## **5\. Arquitectura de control de errores y recuperación**

Dado que MQL5 carece de soporte para el manejo de excepciones (try-catch), un desarrollador de C++ o Java debe implementar un diseño de control imperativo estructurado. La detección temprana y la recuperación preventiva de fallas constituyen el único mecanismo de protección de software robusto.2

### **El búfer global \_LastError**

La máquina virtual mantiene internamente una variable reservada de control global por hilo denominada \_LastError.41 Cuando un error ocurre durante la ejecución de una llamada interna de la API del terminal, el código de identificación numérico es escrito directamente en esta variable de estado.41 Para interactuar de forma segura con el búfer de error, se implementan tres métodos primarios 23:

1. **ResetLastError()**: Pone a cero la variable \_LastError.23 Es obligatorio invocar este método antes de ejecutar cualquier llamada crítica a la API que pueda interactuar con el entorno del terminal o del bróker.41 De lo contrario, se corre el riesgo de capturar un error heredado residual de llamadas previas.44  
2. **GetLastError()**: Devuelve el código de error numérico almacenado en \_LastError sin limpiar su valor.41  
3. **SetUserError(code)**: Escribe un código de error personalizado definido por el usuario dentro del búfer de error global, sumando un valor de desplazamiento estándar representado por la constante de control ERR\_USER\_ERROR\_FIRST para no colisionar con los códigos nativos de la plataforma.23

### **Patrón robusto de verificación post-llamada**

La correcta gestión de errores exige comprobar el estado lógico después de cada llamada a la API.41 El flujo de control debe dividirse en:

* **Comprobación de Retorno Estructural**: Validar si el retorno directo de la función de la API de MetaTrader indica falla (punteros nulos, variables booleanas en false, descriptores de archivo igual a INVALID\_HANDLE o retornos enteros menores a cero).18  
* **Inspección del Código de Error de Sistema**: Si se detecta un retorno inválido, se debe leer de inmediato el código mediante GetLastError() y derivar una lógica de remediación automatizada.41

Fragmento de código  
//+------------------------------------------------------------------+  
//| EJEMPLO COMPILABLE 5: CONTROL DE ERRORES Y MOTOR DE RESILIENCIA  |  
//+------------------------------------------------------------------+  
\#property strict

// Estructura de un despachador defensivo para copiar precios históricos  
bool SafeCopyRates(const string symbol, ENUM\_TIMEFRAMES timeframe, int start\_pos, int count, MqlRates \&rates\_array)  
{  
   // Paso 1: Resetear el búfer de error de forma preventiva antes de invocar la API   
   ResetLastError();   
     
   // Paso 2: Invocar la función crítica del API \[22, 47\]  
   int copied\_elements \= CopyRates(symbol, timeframe, start\_pos, count, rates\_array); \[22, 47\]  
     
   // Paso 3: Validar el retorno inmediato de la llamada   
   if(copied\_elements \<= 0\)  
   {  
      // Paso 4: Capturar y derivar según el código de error devuelto   
      int error\_code \= GetLastError();   
      PrintFormat("Fallo crítico en CopyRates para %s. Código de Error: %d", symbol, error\_code); \[23, 41\]  
        
      switch(error\_code)  
      {  
         case 4004: // ERR\_NOT\_ENOUGH\_MEMORY: No hay suficiente memoria en el terminal \[43\]  
            Print("Remediación: Ejecutando limpieza de cachés y garbage collection manual...");   
            break;  
              
         case 4401: // ERR\_HISTORY\_NOT\_FOUND: Los datos históricos no están sincronizados o no existen \[45\]  
            Print("Remediación: Forzando sincronización activa del búfer de precios...");   
            break;  
              
         default:  
            Print("Falla inesperada. El error no puede ser procesado localmente.");   
            break;  
      }  
      return false;  
   }  
     
   return true;  
}

void OnStart()  
{  
   MqlRates data;  
   // Ejecución del envoltorio seguro  
   if(SafeCopyRates(\_Symbol, PERIOD\_CURRENT, 0, 100, data))  
   {  
      PrintFormat("Datos sincronizados exitosamente. Registros copiados: %d", ArraySize(data)); \[23, 29\]  
   }  
}

## **6\. Manipulación de strings, sistemas de archivos y telemetría (I/O)**

La manipulación de flujos de texto y archivos en MQL5 está regulada por restricciones de aislamiento diseñadas para asegurar la estabilidad del sistema.48

### **Manipulación de strings**

Las strings en MQL5 se gestionan como objetos de longitud dinámica que codifican caracteres de forma nativa en Unicode de 16 bits.6 Al contrario de C++, donde un std::string puede manejarse como un búfer plano finalizado en nulo (\\0), las strings en MQL5 tienen una estructura interna controlada por la máquina virtual. Las funciones clave del sistema para la manipulación de texto incluyen 23:

* **StringFind(source, target)**: Busca la posición de una subcadena de texto en una string de origen.  
* **StringReplace(source, target, replacement)**: Reemplaza caracteres en la string de origen de manera eficiente in-place.  
* **StringFormat(pattern,...)**: Permite el formateo de datos con la misma estructura y rendimiento que la función sprintf de C++ clásica.  
* **StringSplit(source, delimiter, results)**: Tokeniza una cadena de texto dividiéndola según un delimitador y guardando los resultados en un array de strings.48

### **El Sandbox de archivos y políticas de seguridad**

Para salvaguardar la integridad del sistema operativo y evitar que código malicioso manipule archivos del sistema de forma no autorizada, **todas las llamadas de I/O en MQL5 están estrictamente restringidas a una sandbox local aislada** 48:

* **Ruta Local Segura**: Resuelve directamente bajo el directorio específico del terminal cliente en la ruta de datos (MQL5\\Files o MQL5\\Tester\\Files en el caso del agente de pruebas del Strategy Tester).48 No se admite el uso de rutas absolutas que apunten fuera de este sandbox (ej. C:\\Windows\\...).48  
* **Ruta Compartida de Terminales (FILE\_COMMON)**: Para sincronizar información entre múltiples terminales de MetaTrader ejecutándose de manera simultánea en el mismo host físico, se utiliza una ruta compartida centralizada de datos.48 Para forzar la creación y el acceso en esta zona de persistencia global, es obligatorio incluir la bandera FILE\_COMMON en las funciones de manipulación de archivos.49

### **Telemetría y logs**

MQL5 ofrece interfaces de telemetría esenciales para el registro de eventos y auditoría del sistema 23:

* **Print() / PrintFormat()**: Escribe una línea de texto estructurada en el registro general de Expertos del terminal, con almacenamiento automático en discos duros físicos locales de auditoría de la plataforma.23  
* **Comment()**: Genera un overlay de texto renderizado directamente sobre la esquina superior izquierda de la pantalla gráfica activa del instrumento financiero analizado.23 Es útil para telemetría visual de alta frecuencia.  
* **Alert()**: Lanza una ventana emergente del sistema (pop-up) que bloquea momentáneamente el foco del terminal de MetaTrader 5 y emite una señal sonora que alerta al usuario del sistema de un evento asíncrono excepcional.23

Fragmento de código  
//+------------------------------------------------------------------+  
//| EJEMPLO COMPILABLE 6: ARCHIVOS EN EL SANDBOX Y CADENAS DE TEXTO  |  
//+------------------------------------------------------------------+  
\#property strict

void OnStart()  
{  
   string payload\_source \= "ID:405;VOL:1.50;ST\_CODE:K";  
   string parsed\_values;  
     
   // Tokenización de datos de texto   
   int tokens\_count \= StringSplit(payload\_source, ';', parsed\_values);   
     
   if(tokens\_count \>= 3\)  
   {  
      // Reemplazo de subcadenas e inyección de formato   
      string clean\_id \= parsed\_values;  
      StringReplace(clean\_id, "ID:", "");  
        
      string formatted\_log \= StringFormat("Procesando Token ID: %s | Bloque de Datos Completo: %s",   
                                          clean\_id, payload\_source);   
        
      // Escritura persistente en el Sandbox bajo ruta común \[48, 49\]  
      string filename \= "audit\_log.txt";  
      ResetLastError();   
        
      int file\_handle \= FileOpen(filename, FILE\_WRITE | FILE\_TXT | FILE\_COMMON); \[48, 49\]  
      if(file\_handle\!= INVALID\_HANDLE)  
      {  
         // Escritura directa del flujo de caracteres en formato de texto plano   
         FileWrite(file\_handle, formatted\_log);   
         FileClose(file\_handle);   
           
         PrintFormat("Registro guardado con éxito en el Sandbox Común: %s", filename);   
      }  
      else  
      {  
         PrintFormat("Error al inicializar el archivo en el Sandbox. Código: %d", GetLastError()); \[23, 41\]  
      }  
   }  
}

## **7\. Biblioteca matemática, manipulación de arrays y optimización vectorial**

El procesamiento estadístico y el cálculo algorítmico intensivo en MQL5 están optimizados a nivel binario mediante métodos acelerados de ejecución directa.29

### **Funciones matemáticas de alto rendimiento**

MQL5 hereda la biblioteca matemática clásica de C (math.h) y optimiza su ejecución JIT para microprocesadores modernos de 64 bits.22 Las API matemáticas cubren funciones trigonométricas (acos, asin, atan), funciones de redondeo aritmético (ceil), cálculo estadístico, así como exponenciales avanzadas, cálculo de raíces y logaritmos (MathAbs, MathSqrt, MathPow, MathLog, MathRand).22

### **Métodos acelerados de manipulación de arrays**

Para evitar la sobrecarga del bucle de iteración clásico de nivel de usuario, la API proporciona funciones nativas para operaciones en bloque 22:

* **ArrayCopy()**: Realiza una copia contigua directa de memoria en bloque (memcpy o memmove a nivel binario) entre un array origen y un array destino.22  
* **ArraySort()**: Ordena arrays dinámicos unidimensionales de tipo numérico utilizando algoritmos de ordenación de alta velocidad (introsort).22  
* **ArrayBsearch()**: Ejecuta una búsqueda binaria altamente eficiente sobre un array ordenado de manera ascendente, devolviendo el índice de coincidencia exacta con un costo computacional de ![][image15].22  
* **ArrayMaximum() y ArrayMinimum()**: Localizan el índice del valor más alto o más bajo en la dimensión primaria del array analizado sin costo de ejecución en bucles explícitos de usuario.22

### **Cómputo matricial vectorizado nativo**

En arquitecturas de cálculo cuánticas y modelos modernos de aprendizaje automático, el terminal de MetaTrader 5 incorpora tipos vectorizados dedicados: matrix, matrixf (float), vector y vectorf.52 Estos tipos no son meros contenedores lógicos; están acelerados por instrucciones SIMD (AVX/SSE) directas del microprocesador para ejecutar operaciones matriciales en paralelo 52:

Fragmento de código  
//+------------------------------------------------------------------+  
//| EJEMPLO COMPILABLE 7: OPTIMIZACIÓN VECTORIAL Y MATRICES NATIVAS  |  
//+------------------------------------------------------------------+  
\#property strict

void OnStart()  
{  
   // Demostración de optimización de manipulación de arrays planos   
   double raw\_data;  
   ArrayResize(raw\_data, 100); \[15\]  
     
   for(int i \= 0; i \< 100; i++)  
   {  
      raw\_data\[i\] \= MathRand(); // Llenado inicial con valores seudoaleatorios   
   }  
     
   // Ordenación de alto rendimiento nativa   
   ArraySort(raw\_data);   
     
   // Búsqueda binaria de velocidad logarítmica   
   double target\_value  \= raw\_data;  
   int    detected\_index \= ArrayBsearch(raw\_data, target\_value);   
     
   PrintFormat("Búsqueda Binaria exitosa. Índice de coincidencia: %d | Valor: %.2f",   
               detected\_index, raw\_data\[detected\_index\]);   
                 
   // CÁLCULO VECTORIZADO MEDIANTE MATRICES ACELERADAS POR SIMD   
   matrix matrix\_A \= {};  
   matrix matrix\_B \= {};  
     
   matrix\_A.Identity(3); // Crea una matriz identidad de 3x3   
   matrix\_B.Ones(3, 3);     // Crea una matriz de 3x3 llena de unos   
     
   // Multiplicación matricial paralela acelerada por hardware \[52, 54\]  
   matrix matrix\_C \= matrix\_A.MatMul(matrix\_B); \[52, 54\]  
     
   PrintFormat("Filas de la Matriz C: %d | Columnas: %d", matrix\_C.Rows(), matrix\_C.Cols()); \[23, 52\]  
}

## **8\. Divergencias críticas y trampas semánticas con C++**

Esta sección recopila los "gotchas" de desarrollo y las diferencias conceptuales más severas entre MQL5 y C++ que provocan errores de compilación o de ejecución a los ingenieros de sistemas tradicionales:

1. **Inexistencia de punteros físicos a variables primitivas**: En C++, se puede tomar la dirección de cualquier variable primitiva en la pila usando el operador de dirección & (ej. int\* p \= \&x;). En MQL5, **el operador & solo es válido en las firmas de parámetros de funciones para indicar pasaje por referencia**.31 No se permite almacenar direcciones de variables primitivas ni realizar desreferenciación directa de tipos de datos básicos en el heap.2  
2. **Aritmética de punteros totalmente prohibida**: No existe la manipulación física de punteros de memoria.2 Declaraciones como ptr++ o ptr \= ptr \+ 2 generarán errores fatales de compilación.2  
3. **Inexistencia de múltiples unidades de compilación**: En C++, un proyecto compuesto por múltiples archivos .cpp se compila de manera separada y se une mediante un linker. En MQL5, **la compilación es estrictamente monolítica**.1 El compilador genera un binario único .ex5 a partir de un único archivo fuente .mq5 principal.39 El ámbito de visibilidad de las variables globales definidas en el archivo .mq5 se extiende de forma implícita a todos los archivos de cabecera .mqh incluidos en el proyecto 40, rompiendo la modularización de encapsulado clásica.  
4. **No hay soporte de Standard Template Library (STL)**: No se dispone de clases como std::vector, std::map, std::string ni algoritmos genéricos de la biblioteca estándar de C++. El desarrollador debe implementar manualmente estas colecciones o apoyarse en la biblioteca de estructuras de datos estándar de MetaTrader 5\.33  
5. **Diferencias en firmas de destructores y especificador virtual**: En C++, es de vital importancia definir destructores base con la firma virtual \~CBase(); para evitar fugas de memoria en la jerarquía. En MQL5, **el compilador prohíbe el uso de la palabra clave virtual en la firma de destructores de clases**.13 El terminal cliente resuelve dinámicamente la destrucción de subclases de manera interna gracias a que todos los objetos creados por herencia integran obligatoriamente la tabla VMT.2  
6. **Sintaxis única de acceso a miembros a través de punteros**: MQL5 omite el operador de punteros flecha \-\> de C++. El acceso a los miembros de datos de un objeto se realiza utilizando el punto convencional . directamente sobre el descriptor lógico de la clase.  
7. **Incompatibilidad del especificador const con punteros**: MQL5 carece de un sistema completo para diferenciar firmas constantes en punteros (ej. diferenciar const Class\* de Class\* const). Intentar forzar conversiones de tipo complejas sobre punteros constantes heredados fallará de manera silenciosa o detendrá el proceso del compilador.  
8. **Comportamiento del indexado de series temporales (AS\_SERIES)**: En MQL5, un array dinámico que almacena cotizaciones históricas se puede configurar en modo invertido de serie temporal utilizando ArraySetAsSeries(array, true).18 Al activar esta propiedad, **el índice ![][image3] pasa a representar el elemento más reciente en el tiempo (el presente)**, mientras que el índice más alto representa el más antiguo (el pasado).18 Si se pasa este array invertido a funciones de cálculo aritmético estándar que esperan un ordenamiento de memoria lineal contiguo estándar, se generarán inconsistencias lógicas en los cálculos.  
9. **Limitaciones de la directiva typedef**: En C++, typedef define alias arbitrarios para cualquier tipo de datos estructurado complejo. En MQL5, **typedef está severamente restringido y solo es permitido para declarar tipos punteros a funciones**. Cualquier otro alias léxico estructurado debe gestionarse mediante directivas \#define.

Fragmento de código  
//+------------------------------------------------------------------+  
//| EJEMPLO COMPILABLE 8: GOTCHAS Y TRAMPAS SEMÁNTICAS MQL5 VS C++   |  
//+------------------------------------------------------------------+  
\#property strict

// Variable con visibilidad global compartida en la unidad monolítica   
int g\_monolithic\_shared\_var \= 100;

class GotchaBase  
{  
public:  
   int m\_id;  
   GotchaBase(int id) : m\_id(id) {}  
     
   // IMPORTANTE: 'virtual \~GotchaBase()' no se permite en MQL5   
   \~GotchaBase() { Print("GotchaBase Destruido"); }   
};

void OnStart()  
{  
   // GOTCHA 1: El uso de punteros lógicos (handles) sin operador flecha   
   GotchaBase\* ptr\_obj \= new GotchaBase(777);   
     
   if(CheckPointer(ptr\_obj)\!= POINTER\_INVALID)   
   {  
      // En C++ esto se escribiría obligatoriamente como: ptr\_obj-\>m\_id  
      // En MQL5 se utiliza de forma exclusiva el punto '.'   
      int active\_id \= ptr\_obj.m\_id;   
      PrintFormat("ID recuperado mediante descriptor lógico: %d", active\_id);   
        
      delete ptr\_obj;   
   }  
     
   // GOTCHA 2: Comportamiento y trampa del índice AS\_SERIES   
   double rates\_store;  
   ArrayResize(rates\_store, 5); \[15\]  
   rates\_store \= 1.1000; // Pasado lejano  
   rates\_store \= 1.2000;  
   rates\_store \= 1.3000;  
   rates\_store \= 1.4000;  
   rates\_store \= 1.5000; // Presente (más reciente)  
     
   // Activamos el mapeo inverso de serie temporal de precios   
   ArraySetAsSeries(rates\_store, true); \[29\]  
     
   // La trampa: El índice 0 ahora apunta al elemento indexado al final originalmente (1.5000)   
   PrintFormat("rates\_store invertido (Presente): %.4f", rates\_store);   
}

## **9\. Conclusión**

El lenguaje de programación MQL5 es un entorno fuertemente estructurado diseñado para operar de forma segura bajo una máquina de ejecución Just-In-Time.1  
Para los desarrolladores senior de C++, Java o Python, el éxito en la implementación de software en este ecosistema consiste en abandonar paradigmas flexibles como la aritmética libre de punteros de memoria, la herencia múltiple descontrolada y el control de flujos basado en excepciones estructuradas.2 Al operar con MQL5, es mandatorio adoptar un diseño arquitectónico basado estrictamente en el aislamiento del Sandbox, la validación estática de tipos, el predimensionamiento riguroso de búferes con parámetros de reserva lógica, y el control imperativo defensivo post-llamada a través de la API global de errores del sistema.35

#### **Fuentes citadas**

1. Introduction to MQL5 and development environment \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/intro](https://www.mql5.com/en/book/intro)  
2. how similar is C++ verses MQL5? \- MetaTrader 4 \- General \- MQL5 ..., acceso: junio 28, 2026, [https://www.mql5.com/en/forum/210326](https://www.mql5.com/en/forum/210326)  
3. Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types](https://www.mql5.com/en/docs/basis/types)  
4. Integer Types \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/integer](https://www.mql5.com/en/docs/basis/types/integer)  
5. Char, Short, Int and Long Types \- Integer Types \- Data Types \- Language Basics \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/integer/integertypes](https://www.mql5.com/en/docs/basis/types/integer/integertypes)  
6. Character Constants \- Integer Types \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/integer/symbolconstants](https://www.mql5.com/en/docs/basis/types/integer/symbolconstants)  
7. Datetime Type \- Integer Types \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/integer/datetime](https://www.mql5.com/en/docs/basis/types/integer/datetime)  
8. Color Type \- Integer Types \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/integer/color](https://www.mql5.com/en/docs/basis/types/integer/color)  
9. Typecasting \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/casting](https://www.mql5.com/en/docs/basis/types/casting)  
10. Ternary Operator ?: / Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/operators/ternary](https://www.mql5.com/en/docs/basis/operators/ternary)  
11. How significant is the correlation between MQL5 syntax/structure & that of C++?, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/268989](https://www.mql5.com/en/forum/268989)  
12. Structures, Classes and Interfaces \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/classes](https://www.mql5.com/en/docs/basis/types/classes)  
13. Compilation Errors \- Codes of Errors and Warnings \- Constants, Enumerations and Structures \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/errorswarnings/errorscompile](https://www.mql5.com/en/docs/constants/errorswarnings/errorscompile)  
14. Dynamic Array Object \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/dynamic\_array](https://www.mql5.com/en/docs/basis/types/dynamic_array)  
15. Dynamic arrays \- Common APIs \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/common/arrays/arrays\_dynamic](https://www.mql5.com/en/book/common/arrays/arrays_dynamic)  
16. Data Structures \- Constants, Enumerations and Structures \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/structures](https://www.mql5.com/en/docs/constants/structures)  
17. MqlDateTime \- Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/structures/mqldatetime](https://www.mql5.com/en/docs/constants/structures/mqldatetime)  
18. CopySeries \- Timeseries and Indicators Access \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/copyseries](https://www.mql5.com/en/docs/series/copyseries)  
19. The Trade Request Structure (MqlTradeRequest) \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/structures/mqltraderequest](https://www.mql5.com/en/docs/constants/structures/mqltraderequest)  
20. The Structure of a Trade Request Result (MqlTradeResult) \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/structures/mqltraderesult](https://www.mql5.com/en/docs/constants/structures/mqltraderesult)  
21. CustomTicksAdd \- Custom Symbols \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customsymbols/customticksadd](https://www.mql5.com/en/docs/customsymbols/customticksadd)  
22. List of MQL5 Functions, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/function\_indices](https://www.mql5.com/en/docs/function_indices)  
23. Common Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/common](https://www.mql5.com/en/docs/common)  
24. Inheritance \- Object-Oriented Programming \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/oop/inheritance](https://www.mql5.com/en/docs/basis/oop/inheritance)  
25. Operation Overloading \- Functions \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/function/operationoverload](https://www.mql5.com/en/docs/basis/function/operationoverload)  
26. Function templates \- Object-Oriented Programming \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/oop/templates](https://www.mql5.com/en/docs/basis/oop/templates)  
27. Class templates \- Object-Oriented Programming \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/oop/class\_templates](https://www.mql5.com/en/docs/basis/oop/class_templates)  
28. Variables \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/variables](https://www.mql5.com/en/docs/basis/variables)  
29. Checking Object Pointer / Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/namedconstants/enum\_pointer\_type](https://www.mql5.com/en/docs/constants/namedconstants/enum_pointer_type)  
30. Object Pointers \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/object\_pointers](https://www.mql5.com/en/docs/basis/types/object_pointers)  
31. CheckPointer \- Common Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/common/checkpointer](https://www.mql5.com/en/docs/common/checkpointer)  
32. FreeMode(bool) \- CList \- Data Collections \- Standard Library \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/standardlibrary/datastructures/clist/clistfreemode2](https://www.mql5.com/en/docs/standardlibrary/datastructures/clist/clistfreemode2)  
33. GetPointer \- Common Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/common/getpointer](https://www.mql5.com/en/docs/common/getpointer)  
34. Discussion on ArrayResize function behavior, memory allocation, and performance optimization in MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/393227/page263](https://www.mql5.com/en/forum/393227/page263)  
35. ArrayFree \- Array Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/array/arrayfree](https://www.mql5.com/en/docs/array/arrayfree)  
36. Possible Solutions to Runtime Error: 4025 \- Backtesting Software \- MQL4 and MetaTrader 4 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/376990](https://www.mql5.com/en/forum/376990)  
37. CopyTicks \- Initialization \- Matrix and Vector Methods \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/matrix/matrix\_initialization/matrix\_copyticks](https://www.mql5.com/en/docs/matrix/matrix_initialization/matrix_copyticks)  
38. Program Properties (\#property) \- Preprocessor \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/preprosessor/compilation](https://www.mql5.com/en/docs/basis/preprosessor/compilation)  
39. Preprocessor \- Programming fundamentals \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/basis/preprocessor](https://www.mql5.com/en/book/basis/preprocessor)  
40. GetLastError \- Checkup \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/check/getlasterror](https://www.mql5.com/en/docs/check/getlasterror)  
41. \_LastError \- Predefined Variables \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/predefined/\_lasterror](https://www.mql5.com/en/docs/predefined/_lasterror)  
42. Runtime Errors \- Codes of Errors and Warnings \- Constants, Enumerations and Structures \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/errorswarnings/errorcodes](https://www.mql5.com/en/docs/constants/errorswarnings/errorcodes)  
43. ResetLastError \- Common Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/common/resetlasterror](https://www.mql5.com/en/docs/common/resetlasterror)  
44. List of MQL5 Constants, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constant\_indices](https://www.mql5.com/en/docs/constant_indices)  
45. ChartIndicatorAdd \- Chart Operations \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/chart\_operations/chartindicatoradd](https://www.mql5.com/en/docs/chart_operations/chartindicatoradd)  
46. File Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/files](https://www.mql5.com/en/docs/files)  
47. FileOpen \- File Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/files/fileopen](https://www.mql5.com/en/docs/files/fileopen)  
48. FileIsExist \- File Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/files/fileisexist](https://www.mql5.com/en/docs/files/fileisexist)  
49. FileDelete \- File Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/files/filedelete](https://www.mql5.com/en/docs/files/filedelete)  
50. Matrices and vectors \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/matrix\_vector](https://www.mql5.com/en/docs/basis/types/matrix_vector)  
51. Matrix and Vector Types \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/matrix/matrix\_types](https://www.mql5.com/en/docs/matrix/matrix_types)  
52. Passing Parameters \- Functions \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/function/parameterpass](https://www.mql5.com/en/docs/basis/function/parameterpass)  
53. CopyTicksRange \- Timeseries and Indicators Access \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/copyticksrange](https://www.mql5.com/en/docs/series/copyticksrange)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAAWCAYAAABdTLWOAAABZElEQVR4Xu2UO0sEQRCEWzAQBBHEzEegIAZmIhgYmRlooIK5lwhG+heMNNXIUPwR/gIRzMTIQPEBgiAaCD5ArWJmvN5m9nZu9yLZD4rdru6drRtuVqSm5n9zbg3FCHQD/UAXUF+m22Qd+hY3d2h6pTkTt2BQjGXoVNXX4maXlEd2oE1VL0j+mqXYkvwF6a9GPDtva/JkjSoUhbQ9vpzepK/7fd31N+F4NnUlWoXcgNaM9yFuXv83w4+Z93WvrztGq5AxYru7rfwHf+0o7YQ8EDc7YRvgWJpBqZXQGICmExVbmKSG5Ls4N2Mb4Ara8/cnYnZ7FFpM1Jx/xpISkoeCM8O2ARrQi/GGpHjNtkgJyT4PQ4Af7jHVY23J25RSFIV8h7qNd6nuX6F9VQfGrVGFXXEhB20D3Er2MGgFuKOse5RH3kxdik/oEbqH7vyVH+ojNWODxUKSWe99iQvH+6nMRE1NTRq/c6hri8w43mwAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAZCAYAAADJ9/UkAAABSUlEQVR4Xu2UsS5EQRSGT4hKK1HoRIUX0EkUOpUEiYYKi5CIN9BRegGRSFBoRHgEolSq2GJXQikRwf+buXvHb2btbmu+5Mve+c+ZOdmbmzHLZMy24LKGAVfwE77ARakR1k7hEpyHc3AWznh/cQTfzG2kKz/LDVjr8c88lOt6Wf6mOCPmddAXJTX8Ap5Jdm6ufyrIPuAYHIZDcNDLvj9JDX83V5sOshGf1fy6C+6V5QbPsFfDGKnhA/BAsnFz/beSh2zDVQ1TpIbHuDTXP6oFD7+Pll53AZsrGkboNtd7o4WAe7igYTN44JqGEV6t+esmbf1rwg3rGgp38FhD4dA6HL6hYQAvkB3JHmRNeE5Hwzc19PDL1duvH+5LRtoe3mduw64WwISVB6qTQV9By8NP4BN8NPcK+cuLg1dugQ4M5eWiMK9qmMlk/hdfLt9f6x1cRksAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAApElEQVR4XmNgGJpAHl0AHZwA4qtA7AbEj4H4AIosFMwF4r9oYv+BuBRNDKvgDKg4HEhDBTyRBYEgByoOBwlQAVNkQSCIgIqrwgQqoQL6MAEoCIaKw22qggqgKwyCioejCxjDBKAgDCoON8AOKmAJE4CCWKg4yLNgwA4VAJmADGBOQgEggUloYtug4igAm24QH+R+DLCcARKNIBqkqABVehRQAwAA4fYow14SzbMAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAWCAYAAAAxSueLAAABd0lEQVR4Xu2UTStFURSGl68IJQMjHwMmZswMmKH8AKNbjM0kIwOlDPwAZazkB1BElAkyVlJioswUEx8hvO/Zex9rr7uvW2bqPPV073rXOnufzt3nihT8Z0bgPfyCZ7A2bmc8winYDtvgJHyIJkS24BrsgzVwAO7BwTCw6gcCz+I27VUZYWbtiiZEjlUvuKkHGAzpwGfUZivibmzU9AJHcA5uwHnTkxapvHAqq8ahuMdXkWU4bLK/bnYgVTZLwYU/E9kVvICn8APWRxMi+3AWvsF1cdfM6AHLubihZpMza1T1rs8023BJ1U3iZsZUlsODwmaHbSToFze7aBuG1E+SvT/27jV1pua7yPlLlTWo74GyzcKFGh7fwLW4Ph9LoNVnfLdIj6938glH2Wb2MBCd3cInVZMJcYuUfM0/Adbj+YSDGQ9TBk9O2N0a6IY3qiav8MVkvEb/1S34LHsinb5IaRea9vmd/zyJ2xnciDf/Lj/r8HEXFPzON0GzcO7AQcZZAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAWCAYAAAASEbZeAAAAW0lEQVR4XmNgGBqgBIgz0QVBYDkQ/wLi/1CchSqNCQaromx0QXQAUpSLLogOQIry0AXRAUhRAbogOgApKkQXRAYiDBBFPegSILAaiF8D8RMgfgylXzJAomroAgBDrhlwfTmIpwAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEQAAAAWCAYAAAB5VTpOAAAClElEQVR4Xu2XzYuPURTHj3dFFGUhL3nLiCGSsmDG1GQjFhI2MllZ2bGY1ciKFAslFiTlX7CwUBaatWQsBiEbCeVdzJyvc8/Mued3fr95nuc3ZWqeT32b53zP/d23597n3iGqqamp+f+cZf1ljbBu56kxVrFekZR5wlqUZYtxlfWSdYZ1gnWcdYx1NMnTz/qTtN/lwBLWO5I+vWAtztPVeM7aY+KvJA1YDrMemxiDQplDxisCOo3fNZPlN+tmep5H8sLmj6dpLslkKDOosY5K+M7g7SG+ZzzER0ysXtkOoHwPawtrA2tt0i/KB/uB9d7EWFn47S7jfTLPCuptGzSEVaGcS95l40WDR4fhbXJ+K/CWPZdYp0y8hqRebFHLVhejzGnnbXPxpPCZpDEsQQUNY69bfpKUq/ItUfANGHYetqZOPrZFr8lZPpKUe2C8aNW0xUWSRjp9IiBaNWWJfq/1Yst2szanGNvGMiv5KkzGgaxEGyxjXWE9Yr1lLc3TDVwj6cRGnyhBH8lH1qMDHDAevjPwVhgPLE++6qkmMICdBTXRIC6QVL7XJxJoC3n7gasC6jjpTRofnAeePVVwDH9Pz13kfreadbCg7BEbocdX1CnNrfSJkqwnqWehT1Dztr0flXntjbLspvht+8YVeAtMjNNhnYmLcoPi+sEgxTnbJ1wBojJtgxsnKn7o/GhCfrBmO29szyZwNDY7FSx6K47ooDgH71Z63p7iSWcHyY3QcoekMXtVxlLUSfKyRF7EROW+se6bGFd4Xx7xeef5uBK6/L6Q/M+A531ZicZJaDYh11nPSC5XrdB2WvGGpAxusVhRM/P0P/TONJT+3s3TUwPcZeZ4czqDN1qTwF7v8uZ0BveLmqnEKAVwxJOy8/dcAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADUAAAAWCAYAAABg3tToAAACf0lEQVR4Xu2XS6iNURTHVx4heQ+IlDxGXmVgZEAGJN088xiga8LICF3GJvcqIUUkpDtASLhdGRgqCUkpKXUpz8gzb///WXufb33r7O+ec7gGp86v/p27/mvt9e1vn32+/V2RJk2a/C9mQ2+g39BNaGQ+XeaaaM1bqNXlamGU6Pjd0CZoPbQWWhM0qFypTIKei465lE/JcugDtB3aKFmvElugAzEAp0WbzDEeoTcw/L0uxC+zdE1sEB1XpAFZqRyGvpv4PNRt4uNSOZ4qkQsKvC7ooonJFdGaFuf3xlnRVeXOmAZNgSZDF0QXKrJQ0nN6Z+JX0GJopuR7lXgq6QbW+xHiVcabHrwXxqvGF2+AidBD57HvI+eNc7GfM1nqjcgu0QFLjDcBOmViMl+07rbz68VPbnjwDoZ4kWTbvhpfvUGWiTbc7xMJuL9ZO8Mn6uAutMB5W0X7tkHnoKHQDeibqUnxUXRBcuwV3fM/Rfd0b/QXvfAtn6iD2MNzRCq3P2F8z3mRqaLzLoRbjQ0u+4SBv41/3XZckCfeBB2i1+90PiftbzTyGTrhTU9qpSIPoDPe/AvYv92bok9H5jY7/33wU9C3z4DSChy1hmQ3Nc/53ON7nNfj4loYL9qfj2TPCNEcf1uWT8H38NClPzgaK4Phi6PHfR/ZIZUXGgsdMvEQaJuJi9gn2p/nVQrmjiU8P09yRxI+Dft6Mit4V40XD8OU+MiNRG+u8VLwXGJd+bB08BXMT5Rx6gGWvNnR0K+QeB0+7eoTfyNW/UzdCugZdNJ4KXgGcSy/2SL46saax+FzdT5d5r4kbqqvGQbt9GajU+1bajjGQNe92ej4/4ea9AV/ACCmtgcvQp3EAAAAAElFTkSuQmCC>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADUAAAAWCAYAAABg3tToAAACmUlEQVR4Xu2WW4hOURTHl/s9TZKaMG+iXJ6MPCjFg+IJLxQpKZKUkhcMpVBmPLg9eJLUeJNcSlIKeRkzEiJSCvHgllsI//+31j6zznJ8853Bw1ffr/6dvf5rnf3ts7999tkiDRo0+J+MgR5DP6FbIUfeQqugJmgstBx6k6uojafQEmgUNB5aD33NVSjLoC+i4zkHDcynK3RD86Ch0ERou0+uEb15iMVt0LssqzAfxY7KEvugOChPJ7TWxfdE60Y6b7B5XtnkcLZoDE+GxZSH8V7oKLQg5MrAfjqgg9CMkEvE359l8QvnkQfQEWg/1OwTsQPiZyQRa/pLLf18g364eI7ofV3OI1dDnMHiO9aeK/puFVHLYGqhP/1cEr1vQvALH2qaaPEp6Lboy3vYvAi9h9Bd6Ab0XXRdl4X9cNO5Lrp84rsb2SB6z8qYEN3QOI7z0CvoCc0VUrz8+Nd/Dh5rhrn4gnllife8LvASfPe4832ApoYc4e7oqfSz2BrP8zm5Yn41+COs2RETJeGWzn64Nf+JhaI1W2MiwF1TWkSLT+Zzctb82c4b5NqE3w3W3A9+WeaL9nMs+BHW9DXRu1KDhad7/Qpco/SnWPzIYr/tjzbvmvP6gss6DowfYnp7LOaHnfG6rEJJDzUgxJ4DqcEEB+3pMT/BU8BHF5NFojX+BR4BbXZxhPXPgrfP/MkWH7L4U1ahxIdgmycKz83UmC6/PzHj3S6eJHqE8vAlLdpMqNbgJ3j0ORM81vslnFaAh6cLejudx4ff4uJ0wsjYZEY6+/HkEFktvTPNK7fkyFLR/ImYcLSL3v/Srsfz6QozRXP8CHPi2N6Yq1Auiube27XaKvkr+PHeFs16p9q/VJeMgy5Hs97xJ44G/4pf57K+8lBBrhAAAAAASUVORK5CYII=>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIEAAAAWCAYAAADnw/+rAAAEkElEQVR4Xu2ZXahVRRTHlx8pimUohIRpKOhDhRh+JCLZQwhhKoqkBHkr1CI08EFRMsgeihCRHiTtKRAKVAQFLfHNQBCRosJ8EVP70JQyP1LLdP2bWeess87aX3Pv5V4v+weLs+e/Zu/Ze2btmdnrENXU1NTU1NTUdB0fsv3D9i/bZ8aXwgUrZDCQ7a4VKWjvs73G9jLbEraXoj2m6lXlL7ZFVmRGsP1Cod3TbMNb3Q0OU6hzlW2Z8VXlUwrXusk20fgsH7N9Z8XIISukcIXt6Xg8ksKNeQNTxDfUPLfs+beove6YqGUZ/CmspHC+DYJBFAJA6Eeh3mSlAdzrgHj8IIU6Z5vu0uAaOHd5LD8Sy1kMpeD3ggAv7jArVmU6hbcWDyVMpdDoCaVVYR/lP5SwgUIn2rpvsW2hMAgT2MazjWNbx7Zd1avK7+QHwZ+mDJ5ku6PK71I4d6PSJCirgnP2q/K3UXtAaZr/yA+CNWxvGi0JLANo4Hujpz4gKBMEeBsQALupve5XpgywbNywYgVkoL0ggGY7c1LUhadiea7SUvroVQrnYLbRPG7KwmZqvpQ2CDDznjJaMrvYHjJaygMKZYLg7/jrBYEH9iqpvMLWEY+9IPgj6ljvBQTNLFX2wDnYG1RBL3/o82nKZxnM9mM89oIAMyl07HO6nBkULo7gSKEoCFaxLYjHZYJgG9t7VqyA7iQvCGSNFkMA6Dfegk0j9lEpM5O0gQF9gpp9jQ2vBeu94AUBwD0U9V8SuCjWoVSKguCiOi4TBEX+PLDf0VOvFwTgUWoNhB9a3Q2wJ9hBYSZDcFZFrv+c0jqi1l9p77DNVuWsIACN/sGufkpJy/sc2UOtG6IU8oLAbsKKggBrYp4/jxfYVhvNC4I51FyenqXmQGHDlofUq4J3jnyNfB7LCIafmu7/8YJgSNQbn7Nj2eaVtKy1Dp9QdpBSyAqCpdRcm4WiIIDvmBVLIgOr8YLAa9/7arFgh68HrwxeEABo1+Ox/Gq8IMBs/bzROsUzbGeM5t1sGbKC4AO2I8ZkoyRlC3z4gknBtnWcwvVOxjJYHDUP6OgXgJ243YBhykYdvXYXcZv89qBJrsLeN0yCBMczYz3vOsmMIn/qs43gW7kMWUHgIVk6j/kUfG9bRwTTKAaiLMg54Hp6JkAuIqt9reMYhsSNsDNqXygNU3TW/YI3qL29h6O2zOga+O1MYK+TjKRtPTuq6u2N2gGlZfE1hbr4xCkCu+ysh/mEgg+pY4/LFPxrrSMDvEGov8Lo0DYZDWW8/cI5to9UGUg/eVrepx/861UZad+ifRjOOW80vLg605mM5K890zeK3Lpk3LLAGvwbhZtFp/3MdontdV0pspXCzl3q/kphadDgjUV7ktK2IKGDQLCbKA/kAnA/aAttoqyRYMR3OX7xllsks4cEDX7xrJaFFNrJ+/8Fs8k1CssI1vW8XAOWAAy03DfG4EXl/5Lyx6RbQGf1Ng5aoYdBCh4p7j4J1lT8o9ebQBp2tBV7mLxZ4L6nMwmk7sKbknsS5Gt0+rnPYf/0qGmnzGa4pqbruQelF3L6bT3CDwAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHMAAAAWCAYAAADzeqMPAAAEZ0lEQVR4Xu2ZSahVRxCGS19UNIo4reIQREWMGxFRMQE3WbgQFQkqKqgLpzgjLlREiBASjYiiBAU3Ci4URBGHQAQVnBBRIyYhJO8Z42zE5DkPifXf6n63bt0+4+PpXZwPfu7p6uo+fbr69HAuUUFBQUFBQUFWPmU9YP3POstqXZmdmeWsedYYAe7ZLWDbx5rLmsaawprMmuSUl82sn6zR8QPJff9lfWbyPFtIfN6w1pu8rExlvSCp70uTZ/mAxM8C21esWd6ABm5ryiZ6SuLUV9nSsIf1kqQsNL8yOwjKRAUzSueVXxY6kJQPBfMVq6NKX2PtUmnwjPWxSvv25OEO65xKYwCNVGmLD7qmt7NVtAMXw31C2WzhLKBsUjC7sq6T+Npg/kfycINY/UgGFtScNqHOUDCXUXgW0fdq69KNyrbf2eYoWxpOUmXdE1x6hbJpVrL+pOpnx9u8kTWENQCGDykcuJAtC2mCCZ/B7lcHE1P8dyrteUjS3jxsYA2jcDAvsX41NmCfH2k9KxxxtrHKlgaUmW5sCEiIOpJAYsmx7Tlm0iUw544ytpYO5k7WQAoHMwRG7QJrTEk71i/uOhRMjHzYMdX5vcJ21o9NHmHy9NHXVH7eVpQ8EDC1g1AwU4OCmJbyEhdMrE0X3HWaYLahZjwIyXroCQUT+H0CdJp1qDK7ioMkvp1tRgJ3ScotJNnY9WI9J7mnBT7j3XXuYF4hKYgNQ15QPmqHpgdJmmD+zpppjSlZzRqt0lHBBD6Y0GsK7+hHkGwYf2ZdJFlLs+DrP6FseENhm6hs4J66zhVMbIRQqIfNyIgffZZvWUNVOk0wMz+EA8HABksTCmZ7Z8dbhlkDxw7f6XEcJ/HpbjNi8PWWNiwBu+eRugZJwcSeoIIuJAWwxjQX1LPI2DCKMaI1ScHcTfEPEccTa6BwMDFTfG5sW0l8vzB2DQalDUIS9RT21/XgTD2jnFUiKZgVeRjF1tmes7KAupYYW3/WKaPfSHzPuLQla2dp7L0g1IUg49pv+qLqf8w66q6x/sOvUzm7RNb2fUNhf10PNkm23f6c6dOWijpDmx1rG8P6xNiiQOVLrTHAbBLfqDczqbOwy8XXkbSgLvtmRtV/g2STAnw71jblyvk31L41Jq3x62NPY4ftD2PT3KLq+3jGkcrTX22sPL4RURVqsIbAr2oeD7CKxNeuIZ64e2IaR16jzYgB/n8Z22WSztKgPfq+i0m+2miukvj0UTb/IeGwslmw1NxWacwQKFOnbJZ/KLofvieX95G7CMmfcTwHWA3GptnLuk/SWRjV+MVWHIPFgvX5byr73iRpsAXtQF4U9SQ7zyQwtSJgvl1opz7jYTrFvRrcrw0uWEeSh7L4xcyFo4UGX7V8fhw4msEHZ1v8oj9CbCLpQ99PGASYcjXYBSfdL0je76ItSa4HaWFCA7PmqLWOw857hzW+ZzBF4x+RmgZ/EWU5U70LcCasNezGsSbB0aLWwCG/1sBmsaAgP28BdttoQSJ1xdIAAAAASUVORK5CYII=>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHMAAAAWCAYAAADzeqMPAAAEn0lEQVR4Xu2ZacimUxjHL/u+jC37MMwghUjI8lGJwSCmxBcf5sNMM0lIQqH4QmQpkTVSkhSmiIgPlpI1ss1kCZFI9vX85pzrea/7/5xnee93au4P96+u3vv6n+uc59zn3Gd9zXp6enp6enrmwvxk/6k4JSck+95y/leTbdxMHnCT5Zg/kx0oaTXOsvZ1OjrZl5bzXyVpymrLcT8lmydp6NT7omTnJ1ua7LxiR4W4aXjYcnm/Jbte0iJPWo77INmmkgY/JrvAhus6gMxtGu62ZHcG/1fL5SwIGqDdJf5pwa/Rtk7eaM49yb4LvrOz5bhjin9Y8SNeh5qdEeImQfwu5fnw4v8zk7yOHYt+cPH3KP7mg4hMrMMQzyb7xUYkToA83hhRi2W9Iz6cU9Ei39hwOdOwr+U8S0RHO7uiXRJ8Gjf+3qHJnrM8Ag9KdoDlj/TkZG+HuElcnuwta85Yl1r+rZuDVnvf92y404m5wZqDaB17Wx7WPk3Ohm2sXgHV1Iftinas6LA42cVWzzeJOyzn2VN0NKZR54GiKYwO54pkOwTfqeUbB0sPeW4XXd+P54+CD740RdQf4AltOhOuS3a8aLVK1spGe1TFxO/l76h841hjOU/sFNCyor+X5ZE3DazD26s4ga2TPW7NkbmFNeswvzwzgiNXF92nXqi2CT+wT3lu25k1KOdf8bXs/Yv2ruhrbWbRr+WbxH2W89RGZizLfd6bNji9+IeEGOXcZC+p2BJGPb+3PGj4OjJ9BolLhMe97wKL/wuD5PXXmb4+8jU6NICWzXyPxlrtnJjsmuBrB0yDb2rYCUe0LPeJd+4v2ihI20TFllDWDxVN10cGBTprrIPPyG4IkfXRmWyEKGNXTbCs31ieN0r2StGeH0SY/RWeQTtgWp6yZr7Pix819eGkoi0THdh5a3xbPrbc3grTPb+xe/E58r1YND70KhwR4hwMc+1Mzjzkb3wxAos5I5F11ned15Y0ptsty7NTa/Bp4djwoeWOZa3SstSHI4v2tOiAHpeOtnBsGkyPFTZL9liyr5Kdmuxey78dz5uN2YFD8sti/nI8cy6bDd5YkYfEV06xnMcrpvXROq0ocW2hnEfE1zpz0aBxDjq70rmw0vIxMKJ1UF6zZswnxdcPv0Ht5YBG57w1jtoXG7ULLZcdRy2H+D+CX2NUnS6z+s2IQx4+WOeIokXYRat2ZtH2E90P80+IHmHXOQ6m8NoHHkfpZzZcJ/xbg8+SEfcZVWoNx9pW0yNczXmMmnNl8b0D+Djw9WZD0XKArxvtZ9EjpMeG48O6JfgOcfFYxYaEywqFKzxiH9SEAp1M+jOaUPC1sGYc/h2u+eL7shzq+7Pz/lS0AW9afoEvivH8RkjnQmFt8CPjKknFIpwd2eDQYH8n26qZ3IAR+7XN1Olby+uts8ZyGaPwRmCjwV8uIGpwP8zukbtO4pjCauxmOX2VJhR2sjzTaMM7Xo+aHRfiOL+isX+hXozUGj7Tsa7OmtdV6ACjGm5DEm+YOkvXGo61924VNzCLLP9XpdOw+/Lb/q6gB+suUNsEdo6FKnSAbVXoAGwWe3ra8z9VFI/CIDeTigAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAWCAYAAABHcFUAAAABWElEQVR4Xu2UPS8EURSGzyYaEiLR6ESloRGfhUYiodFQ+QGrohXxAyj8AKKxhWoJIXQSKo1IJH6ARBSEhIgofO17cs9w9o1isrOzW5gneZJz37lz5+zeuSPyz5mH7/CQ8hP4AI8oT519OGb1N5y2+hQuWL0G36yuCdpIRKurl+Cq1dtSPi8xKxK25gMW6NqchIftwluYL7/8g87p4bBSnmGv1W0SFve/eJPGj7DbjQfgOjx2WSIG4R1sdlm/hCYubLxs44gDCS82MyVV2j7dNl3oinL/b426WtmDr1afw06rGyXMy9k4EUXYQhlvoa9v4IzLx62esHEqDEtYXJuN0C19kfCN2nJ5H7yHG/ALNrlrVUUb0gckRk+Ndh3HLrvnL3bgJ4eV0gEnYzpi9zCz8InDejIErylL7aWNQzu85FDq2FSD/B5/9szNqyl6lLmZyEU3LyMjgykBK/hYeqMU3DoAAAAASUVORK5CYII=>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADYAAAAWCAYAAACL6W/rAAABOklEQVR4Xu2VTStFURSGV4Ri4KOUYqQYmVEGTPwA95cYM1AmZgyVkZm/YqCIMlIyZYKRro98ve8963SX15ncLp2zc556Omu/q1t71W5ds5oWY/AR3sDZkG95fg5HQp4Ew/De63X46fUKPPN6IuTJ8A5nwrnfv1Pw2us5q+Bgy/DOsosdw57v7VbO53cJT6SXcwp3NCyTPbgfzk3LBpkOGc9rXs/D29Aju/AB9kpeKrz0YkEWn5U+MT3nMB/SsAx4CR2CaFbUJ9twQ/LNcC4VXm5JMh3sytrLg98Xr5/hkdeEv8kXSyXhBT8k47o/gG8h64NPnnPY1dCrHBeWDTaojZThEuFQ49r4ZRY6sGtGLRtqQBt/QKMDu4J/yLr5DuWcJLooSFGWFK/WXu9qskzaz2FyucZrampq/g9fsu9TukfhTxMAAAAASUVORK5CYII=>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADYAAAAWCAYAAACL6W/rAAABMUlEQVR4Xu2Vv0pCYRjGXxoKbAiDJjchb6DAoaYuoCtx7gYavADBqU1oafEKnAMnm4oIBEEXa6rE6I/P43cOvr4eB7Hw++j7wY9zvvdZfNTzHpHIlH34CvuwZDJyBqt26Dt78Dm5v4A/KkvhLLhiX/BQnbfVPXmCTfGw2CkcivvWb+HWfDyd8+93D9smO4F58bBYDdbV+V1ckaKa8VxJ7o/gQGXXydW7YvzQ5YyZfo7sM5WeO2rmVbFdWSxB7CwrJy3lG+zCmyTbOJfinhONLfYos+XB61hlKQ/i0S+2DJb6NjOu+yv4aeZkJC5/gT2TecOduGI5G4QMlwhLHdjglzlewbXhu4ildmzwB5yv4FrwhWw3X8Ocg8QuCpI1C4oPma13a7AUZLFMKld4JBKJ/B8myZVUysOueVUAAAAASUVORK5CYII=>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEsAAAAaCAYAAAD/nKG4AAADRUlEQVR4Xu2YS6hNYRTHlzchz0geoYQBMRPqJo+U8ghRSpGkKCkDr1JiamLAkIk8MhIDZeAREkoGKEw8MiCP8n6uf99a566zzvrO3e69TpvOr1b3W/+19j7fY+/1ffsSNWnyLzHbCyVlkhfayzy2odLuwnaQbRfbkEpGzEdK+Zbxzi8Lt9imePFPec12TNrv2X6y/TK2TWKey2wtxsd99Jqygr719WIRBlK6WGcb7QWtYdogWjT4cRTrYyjWywLG98GLRcCglkr7Cds9E1P0KRvu9Ddsy5wGhlG5JwugfyO9WI+XbG+lPZXSDXztAXg9EVvp9NyEDKZ8rCygdl31Yo6xlAY0QPyzbKMr0WpQr5A702jrRYsYRPnYOrbnlBYAT2DEDLbjbFvFP0Hp6da+eg6wbTc++onrtxjNs5ryfazhHRVPvkC1uTcpDToimqyeoi002ie2Q8YH2FnPSHsTpWt6UKoxGzXJcJLSbo28K5TelDkSg/ZA2hG+j1mQWDRZa5bX0LmIaLK+sd13WndKeSPE3y++BT5emRzf5a+OB/dUbouWo16sCiRiwEVA7t5A06OGx09WH/GXGE2B/lDap8W3wMcTmGOa/EUeJtsCTWtyBOK9vRihK9EWeyjOg3bUi4KfrLXizzeaYvuhr5MegruKv0j8HNilkefPTtA2O82CeH8vRhSZLNQK5Oip3vKZ7ZIXBT9ZWH34KO4e349X4uNYgr+rTCzHYaodC4q71zxtxSs8ppT8yAcEnahZPiDcZXvqRUFX2h5D4GPH9UDHJxWYwHbExIqCe6Ameg0LCm7YgKHwZOkjDkNNmCh6L0rbLvR+okVgZ8r92GRKMftELhbNPvbXqLYeIecOpc3jPKXdMnekUXDNvkDbSWnBokVdTvn+h2A7x4ropKnNtUl1iH7sC9sLSh3EoRffisooan3NogFiJ8Pu5vujE5gD8W5O2yH6M6crWKjrXvyboDNR0W4vuF+LFyl9lkQL0xFwP5SahoHCXfT4UQQMAB/2EZ05WajDX73YCPDK6Vmno6ygNClrjIZPH5QKfPJ0Fj+o+vDaUPDjnQm+O0+xnWPb7WId5SLbdC82Gv0eKzv2nwFNmjRp8l/xG4DZ44K3hgwNAAAAAElFTkSuQmCC>