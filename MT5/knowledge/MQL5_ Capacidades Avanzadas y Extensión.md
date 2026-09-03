# **Ingeniería de Software Cuantitativa y Extensibilidad en MQL5: Arquitectura de Sistemas de Alta Disponibilidad y Computación de Alto Rendimiento**

## **Computación Heterogénea y GPU con OpenCL en MQL5**

La necesidad de procesar grandes volúmenes de datos financieros en tiempo real y ejecutar optimizaciones matemáticas complejas ha impulsado la integración de tecnologías de computación heterogénea dentro de las plataformas de trading.1 MQL5 aborda esta exigencia mediante una API nativa para interactuar directamente con la especificación OpenCL (Open Computing Language), permitiendo descargar tareas computacionales masivas desde la CPU hacia la GPU u otros aceleradores de hardware dedicados.1  
Esta paralelización a nivel de hardware resulta especialmente ventajosa para algoritmos que pueden subdividirse en múltiples hilos de ejecución independientes, como el entrenamiento y ejecución de redes neuronales, la transformada rápida de Fourier (FFT), el filtrado por ondículas (wavelets) o la resolución de sistemas de ecuaciones de grandes dimensiones.1

### **La API Integrada de OpenCL en MQL5**

La interacción con el entorno OpenCL en MQL5 se gestiona mediante un conjunto preciso de funciones del sistema que abstraen el ciclo de vida del cómputo heterogéneo 1:

* **CLContextCreate**: Inicializa el entorno de ejecución (contexto) y detecta los dispositivos compatibles.1 Permite definir si se usará la GPU de forma exclusiva mediante la bandera CL\_USE\_GPU\_ONLY o si se requiere soporte explícito para cálculos de doble precisión con CL\_USE\_GPU\_DOUBLE\_ONLY.5  
* **CLProgramCreate**: Compila el código fuente del kernel OpenCL en tiempo de ejecución para la arquitectura específica del hardware objetivo, devolviendo un identificador del programa compilado.1  
* **CLKernelCreate**: Registra un punto de entrada o función específica dentro del programa compilado (identificada por el calificador \_\_kernel o kernel en el código OpenCL) para su ejecución paralela.1  
* **CLBufferCreate**: Asigna bloques de memoria física en el dispositivo acelerador (GPU).1 Estos búferes se configuran con banderas de acceso como CL\_MEM\_READ\_WRITE para permitir la bidireccionalidad de datos.1  
* **CLBufferWrite y CLBufferRead**: Transfieren datos bidireccionalmente entre el espacio de memoria del host (MQL5 en la CPU) y la memoria del dispositivo (OpenCL en la GPU).1  
* **CLSetKernelArg y CLSetKernelArgMem**: Vinculan variables escalares o punteros de memoria del búfer a los parámetros formales definidos en la firma del kernel.1  
* **CLExecute**: Lanza la ejecución del kernel en un espacio de trabajo indexado, definiendo dimensiones globales y locales para mapear la paralelización a los núcleos de la GPU.1  
* **Liberación de Recursos**: Al finalizar el procesamiento, es obligatorio liberar todos los descriptores para evitar fugas de memoria en la GPU mediante las funciones CLBufferFree, CLKernelFree, CLProgramFree y CLContextFree.1

### **Gestión de Precisión y Limitaciones del Soporte de Hardware**

La compatibilidad de tipos de datos entre MQL5 y OpenCL exige un riguroso control por parte del desarrollador. MQL5 trabaja de forma predeterminada con datos de precisión doble (double), pero muchas GPUs comerciales limitan o desactivan el soporte nativo de punto flotante de 64 bits para optimizar la eficiencia energética y el rendimiento en precisión simple (float).4 Intentar ejecutar cálculos en double en un hardware sin soporte físico o sin la habilitación explícita del driver provocará el fallo crítico de compilación en tiempo de ejecución con el código de error 5105\.4 Para mitigar esto, es obligatorio incluir la directiva de habilitación de la extensión correspondiente en la cabecera del código del kernel 4:

Fragmento de código  
\#pragma OPENCL EXTENSION cl\_khr\_fp64 : enable

Si el hardware subyacente carece por completo de unidades de cómputo fp64, la ejecución fallará inevitablemente, lo que obliga a diseñar arquitecturas híbridas capaces de realizar un *fallback* a precisión simple (float) utilizando buffers mapeados de tipo float.4 La clase estándar de MQL5 COpenCL incluye métodos como SupportDouble para verificar de forma dinámica la compatibilidad de doble precisión en el dispositivo anfitrión.4  
En lo referente a las limitaciones de plataforma, MetaTrader 5 soporta oficialmente la especificación OpenCL versión 1.2.3 Las implementaciones que dependen de características avanzadas de OpenCL 2.x o 3.x no son compatibles directamente a través de la API nativa de MQL5.  
Asimismo, el soporte en entornos macOS (especialmente sobre arquitecturas Apple Silicon M1/M2/M3) presenta restricciones severas. Debido a que MetaTrader 5 se ejecuta habitualmente bajo capas de emulación como Wine en estos sistemas, y dado que Apple deprecio formalmente OpenCL en favor de su API Metal, la plataforma no suele detectar la GPU integrada de Apple Silicon.4 En consecuencia, el sistema realiza de manera transparente un *fallback* de ejecución utilizando la CPU para emular el entorno OpenCL, lo cual anula los beneficios de velocidad esperados de la paralelización por hardware.1

### **Benchmarks de Rendimiento y Casos de Uso Críticos**

El impacto de OpenCL en el rendimiento computacional sigue una escala no lineal correlacionada directamente con el tamaño de los conjuntos de datos. Para operaciones algebraicas masivas, como la multiplicación de matrices de tamaño ![][image1] donde ![][image2], la GPU supera exponencialmente a la CPU debido a que la complejidad algorítmica del producto de matrices es de orden ![][image3].6  
El cálculo de cada elemento individual de la matriz resultante se ejecuta de forma completamente aislada e independiente.6 En una CPU tradicional de 8 núcleos con ejecución secuencial o multi-hilo limitada, el tiempo de proceso crece de manera prohibitiva.3 En cambio, una GPU equipada con miles de núcleos de procesamiento paralelo ejecuta estas sumas de productos simultáneamente, logrando tasas de aceleración (*speed-up*) de entre ![][image4] y ![][image5] en comparación con las funciones nativas de la CPU.3

| Dimensión de Matriz (N×N) | Tiempo CPU Monohilo (ms) | Tiempo CPU Multihilo / MatMul (ms) | Tiempo OpenCL GPU (ms) | Factor de Aceleración (GPU vs CPU) |
| :---- | :---- | :---- | :---- | :---- |
| **![][image6]** | 180 | 25 | 12 | ![][image7] |
| ![][image8] | 1,450 | 180 | 35 | ![][image9] |
| ![][image10] | 42,300 | 4,800 | 290 | ![][image11] |

Los casos de uso prácticos de esta tecnología en el trading algorítmico automatizado abarcan:

1. **Optimización Masiva de Parámetros**: Ejecución simultánea de miles de simulaciones de Montecarlo o reajustes periódicos de carteras mediante algoritmos genéticos.1  
2. **Cálculos Matriciales para Machine Learning**: Procesamiento rápido de las fases de propagación hacia adelante (*forward pass*) y retropropagación (*backpropagation*) de modelos de aprendizaje automático integrados directamente en el terminal, evitando la latencia de comunicación con servicios externos.1

### **Código Funcional MQL5: Multiplicación de Matrices con OpenCL**

El siguiente script de MQL5 demuestra la inicialización de OpenCL, la compilación de un kernel en línea para multiplicar dos matrices bidimensionales en precisión simple (float), la transferencia de memoria hacia el dispositivo, la ejecución paralela y la lectura final de los resultados 6:

Fragmento de código  
\#property copyright "Algorithmic Systems Architect"  
\#property version   "1.00"  
\#property script\_show\_inputs

\#define MATRIX\_M 1024  // Filas de la Matriz A  
\#define MATRIX\_K 512   // Columnas de A y Filas de B  
\#define MATRIX\_N 1024  // Columnas de la Matriz B

// Código fuente del Kernel OpenCL escrito en C99 estándar   
const string OpenCLKernelSource \=   
   "\_\_kernel void MatrixMulKernel(\_\_global const float\* A,       \\r\\n"  
   "                              \_\_global const float\* B,       \\r\\n"  
   "                              \_\_global float\* C,             \\r\\n"  
   "                              const int M,                   \\r\\n"  
   "                              const int K,                   \\r\\n"  
   "                              const int N)                   \\r\\n"  
   "{                                                            \\r\\n"  
   "   int row \= get\_global\_id(0);                               \\r\\n"  
   "   int col \= get\_global\_id(1);                               \\r\\n"  
   "   if(row \< M && col \< N)                                    \\r\\n"  
   "   {                                                         \\r\\n"  
   "      float sum \= 0.0f;                                      \\r\\n"  
   "      for(int i \= 0; i \< K; i++)                             \\r\\n"  
   "      {                                                      \\r\\n"  
   "         sum \+= A\[row \* K \+ i\] \* B\[i \* N \+ col\];             \\r\\n"  
   "      }                                                      \\r\\n"  
   "      C\[row \* N \+ col\] \= sum;                                \\r\\n"  
   "   }                                                         \\r\\n"  
   "}                                                            \\r\\n";

void OnStart()  
{  
   Print("Iniciando computación matricial paralela vía OpenCL...");  
     
   // Matrices de datos representadas en arreglos unidimensionales aplanados para OpenCL \[7\]  
   float h\_A, h\_B, h\_C;  
   ArrayResize(h\_A, MATRIX\_M \* MATRIX\_K);  
   ArrayResize(h\_B, MATRIX\_K \* MATRIX\_N);  
   ArrayResize(h\_C, MATRIX\_M \* MATRIX\_N);  
     
   // Inicialización de matrices con datos simulados \[7\]  
   for(int i \= 0; i \< MATRIX\_M \* MATRIX\_K; i++) h\_A\[i\] \= (float)MathRand() / 32767.0f;  
   for(int i \= 0; i \< MATRIX\_K \* MATRIX\_N; i++) h\_B\[i\] \= (float)MathRand() / 32767.0f;  
   ArrayInitialize(h\_C, 0.0f);  
     
   // Creación del contexto OpenCL enfocado en la GPU \[1, 6\]  
   int clContext \= CLContextCreate(CL\_USE\_GPU\_ONLY);  
   if(clContext \== INVALID\_HANDLE)  
   {  
      Print("Error: No se pudo crear el contexto OpenCL en la GPU. Error local: ", GetLastError());  
      return;  
   }  
     
   // Compilación del código fuente del kernel   
   string buildLog \= "";  
   int clProgram \= CLProgramCreate(clContext, OpenCLKernelSource, buildLog);  
   if(clProgram \== INVALID\_HANDLE)  
   {  
      Print("Error de compilación OpenCL. Logs de compilador: \\n", buildLog);  
      CLContextFree(clContext);  
      return;  
   }  
     
   // Registro del Kernel de computación   
   int clKernel \= CLKernelCreate(clProgram, "MatrixMulKernel");  
   if(clKernel \== INVALID\_HANDLE)  
   {  
      Print("Error: No se pudo instanciar el kernel 'MatrixMulKernel'. Código: ", GetLastError());  
      CLProgramFree(clProgram);  
      CLContextFree(clContext);  
      return;  
   }  
     
   // Asignación de memoria física en el dispositivo de cómputo (GPU buffers) \[1, 6\]  
   int bufA \= CLBufferCreate(clContext, MATRIX\_M \* MATRIX\_K \* sizeof(float), CL\_MEM\_READ\_WRITE);  
   int bufB \= CLBufferCreate(clContext, MATRIX\_K \* MATRIX\_N \* sizeof(float), CL\_MEM\_READ\_WRITE);  
   int bufC \= CLBufferCreate(clContext, MATRIX\_M \* MATRIX\_N \* sizeof(float), CL\_MEM\_READ\_WRITE);  
     
   if(bufA \== INVALID\_HANDLE || bufB \== INVALID\_HANDLE || bufC \== INVALID\_HANDLE)  
   {  
      Print("Error crítico al inicializar búferes en GPU.");  
      CLBufferFree(bufA); CLBufferFree(bufB); CLBufferFree(bufC);  
      CLKernelFree(clKernel); CLProgramFree(clProgram); CLContextFree(clContext);  
      return;  
   }  
     
   // Escritura de datos desde la RAM de la CPU a la VRAM de la GPU \[1, 6\]  
   CLBufferWrite(bufA, h\_A);  
   CLBufferWrite(bufB, h\_B);  
   CLBufferWrite(bufC, h\_C);  
     
   // Vinculación de argumentos del Kernel \[1, 6, 7\]  
   CLSetKernelArgMem(clKernel, 0, bufA);  
   CLSetKernelArgMem(clKernel, 1, bufB);  
   CLSetKernelArgMem(clKernel, 2, bufC);  
   CLSetKernelArg(clKernel, 3, MATRIX\_M);  
   CLSetKernelArg(clKernel, 4, MATRIX\_K);  
   CLSetKernelArg(clKernel, 5, MATRIX\_N);  
     
   // Configuración de las dimensiones del espacio de trabajo de ejecución (2D Grid) \[6, 7\]  
   uint offsets \= {0, 0};  
   uint workSizes \= {MATRIX\_M, MATRIX\_N};  
     
   uint startTick \= GetTickCount();  
     
   // Ejecución del cómputo paralelo   
   if(\!CLExecute(clKernel, 2, offsets, workSizes))  
   {  
      Print("Fallo crítico en la ejecución del Kernel OpenCL. Error: ", GetLastError());  
   }  
   else  
   {  
      // Lectura de los resultados desde la GPU hacia la CPU \[1, 9\]  
      CLBufferRead(bufC, h\_C);  
      uint executionTime \= GetTickCount() \- startTick;  
      PrintFormat("Multiplicación de matrices \[%dx%d\] exitosa. Tiempo de cómputo GPU: %u ms.",   
                  MATRIX\_M, MATRIX\_N, executionTime);  
      PrintFormat("Resultado de validación de primer elemento: C \= %f", h\_C);  
   }  
     
   // Liberación de todos los recursos del entorno OpenCL   
   CLBufferFree(bufA);  
   CLBufferFree(bufB);  
   CLBufferFree(bufC);  
   CLKernelFree(clKernel);  
   CLProgramFree(clProgram);  
   CLContextFree(clContext);  
}

## **Interoperabilidad Nativa mediante Importación de DLLs**

La flexibilidad de MQL5 se extiende de forma sustancial mediante la capacidad de importar funciones externas compiladas en librerías dinámicas (.dll).10 Esta característica permite integrar capacidades ausentes de forma nativa en la sandbox de MetaTrader 5, tales como el acceso directo a APIs del sistema operativo Windows, algoritmos criptográficos avanzados o la intercomunicación directa con procesos concurrentes en el host.11

### **Sintaxis de Importación y la Directiva \#import**

El mecanismo para enlazar funciones externas requiere el uso de la directiva \#import.12 Al declarar una función externa, el desarrollador especifica la firma de la función, forzando al compilador de MQL5 a generar los puntos de entrada correspondientes 13:

Fragmento de código  
\#import "CryptographicEngine.dll"  
   int EncryptBuffer(const uchar \&inputBuffer, int inputSize, uchar \&outputBuffer);  
   void GenerateKeyPair(string \&publicKey, string \&privateKey);  
\#import

### **Marshaling de Tipos de Datos y Alineación de Memoria**

El proceso de transferir datos entre MQL5 (entorno gestionado y seguro) y C/C++ (entorno nativo sin gestión automática de memoria) se conoce como *marshaling*. Un error de correspondencia en el tamaño físico de los tipos de datos o en la estructura del alineamiento de memoria provocará de manera inmediata la corrupción del flujo de ejecución y, por ende, el colapso (*crash*) fatal de MetaTrader 5\.13  
A continuación se presenta una matriz detallada de conversión de tipos compatibles entre MQL5 y arquitecturas nativas de C/C++ (64 bits):

| Tipo de Dato MQL5 | Tipo Nativo en C/C++ (64-bit) | Mecanismo de Pasaje de Parámetros | Notas Críticas de Marshaling |
| :---- | :---- | :---- | :---- |
| int | int o int32\_t | Por Valor / Por Referencia (&) | Ocupa exactamente 4 bytes en ambas plataformas. |
| long | \_\_int64 o int64\_t | Por Valor / Por Referencia (&) | Ocupa exactamente 8 bytes.15 |
| double | double | Por Valor / Por Referencia (&) | Ocupa exactamente 8 bytes (formato estándar IEEE 754). |
| string | const wchar\_t\* (Input) / wchar\_t\* (Output) | Solo de lectura (Por Valor) o puntero a búfer mutable.13 | MQL5 utiliza de forma predeterminada cadenas UTF-16 Unicode.12 |
| struct | struct nativa | Obligatoriamente Por Referencia (&) | Requiere coincidencia exacta de campos y empaquetado de estructura en el compilador C++.15 |
| array (e.g., double) | double\* o tipo base apuntado | Obligatoriamente Por Referencia (&) 14 | Los arrays de MQL5 se pasan como punteros continuos al primer elemento. No son asSeries.13 |

### **Cadenas de Texto y Estructuras de Datos Complejas**

Las cadenas de caracteres en MQL5 representan uno de los mayores desafíos para el desarrollo nativo.12 MQL5 gestiona internamente las cadenas de texto a través de buffers dinámicos de caracteres Unicode UTF-16 (wchar\_t en C++ de 64 bits), a diferencia de las cadenas ANSI de un solo byte utilizadas de forma predeterminada en el antiguo MQL4.12 Al pasar un objeto de tipo string a una DLL:

1. **Lectura (Parámetro por Valor)**: La DLL recibe directamente un puntero constante de tipo const wchar\_t\*.13 Es seguro leer esta información, pero bajo ninguna circunstancia se debe intentar modificar el contenido direccionado por este puntero, dado que pertenece al bloque de memoria interno gestionado por MetaTrader 5\.  
2. **Escritura / Modificación**: No se pueden reasignar dinámicamente punteros de strings desde C++ para devolver nuevas cadenas de caracteres al terminal, ya que esto rompería la gestión de asignación de memoria de MetaTrader y provocaría fugas de memoria severas (*memory leaks*) o desbordamientos.12 Para escribir datos de texto desde C++, la mejor práctica consiste en pasar un array nativo de tipo uchar o wchar\_t preasignado en tamaño desde MQL5, poblarlo en el lado de C++ mediante funciones de copia de memoria de bajo nivel como memcpy o wcscpy, y posteriormente reconstruir la cadena en MQL5 utilizando las funciones nativas CharArrayToString o ShortArrayToString.12

Alternativamente, es posible representar cadenas mediante la estructura interna MqlStr propia de la plataforma, que debe declararse con alineamiento estricto a un byte en C++ para que coincida con la disposición de memoria de MQL5 13:

C++  
\#**pragma** pack(push, 1\)  
struct MqlStr\_mt5  
{  
    int len;            // Longitud del buffer asignado para la cadena (4 bytes)  
    wchar\_t\* string;    // Dirección de memoria del buffer Unicode UTF-16 (8 bytes en 64-bit)  
    int reserved;       // Campo reservado de control (4 bytes)  
};  
\#**pragma** pack(pop)

Al pasar un arreglo de estructuras MqlStr por referencia, es posible modificar directamente el contenido de los buffers asignados por el terminal siempre que se respete de forma estricta el límite físico de caracteres indicado en el campo len.13  
Por otro lado, cuando se transmiten estructuras personalizadas a una DLL, es vital coordinar el alineamiento de memoria (*alignment*). Por defecto, el compilador de MQL5 almacena los elementos de una estructura de forma secuencial y compacta, es decir, sin ningún relleno o alineación artificial (empaquetado estricto a 1 byte).16 Sin embargo, la mayoría de los compiladores modernos de C/C++ aplican de forma estándar un empaquetado optimizado para el procesador (normalmente alineando los datos a palabras de 4 u 8 bytes).15 Para asegurar que la estructura en C++ coincida exactamente bit a bit con la de MQL5, se debe forzar explícitamente la directiva de empaquetado de estructura en el código de C++ mediante las directivas \#pragma pack 13:

C++  
\#**pragma** pack(push, 1\)  
struct RateInfo  
{  
    \_\_int64 ctm;          // 8 bytes (Unix timestamp)  
    double  open;         // 8 bytes  
    double  low;          // 8 bytes  
    double  high;         // 8 bytes  
    double  close;        // 8 bytes  
    unsigned \_\_int64 vol; // 8 bytes  
};  
\#**pragma** pack(pop)

### **Seguridad y Entorno de Ejecución (Sandbox)**

Por razones estrictas de seguridad de la infraestructura y protección del usuario final, MetaTrader 5 ejecuta todos los scripts e indicadores dentro de una sandbox controlada.10 El acceso a la API externa de DLLs está deshabilitado de forma predeterminada en el terminal.10 Para permitir la ejecución de estas funciones importadas, el usuario debe marcar explícitamente la opción **"Allow DLL imports"** en los ajustes generales del terminal (Tools \> Options \> Expert Advisors) o en la ventana de configuración específica de entrada de cada Expert Advisor al momento de su inicialización.  
Habilitar esta bandera otorga al programa privilegios del nivel del sistema operativo. Un binario DLL malicioso o comprometido de un proveedor externo tiene acceso irrestricto al sistema de archivos local, a conexiones de red arbitrarias no rastreables y a la ejecución de procesos del sistema, anulando por completo las garantías de seguridad informática de MetaTrader.

### **Diagnóstico de Fallas Críticas (Crashes)**

El principal riesgo operativo de integrar código de bajo nivel en plataformas de trading financiero es el potencial de provocar un desbordamiento de búfer o una violación de acceso a memoria (*segmentation fault*). Dado que MQL5 se ejecuta en el mismo proceso del espacio de usuario que la terminal principal (terminal64.exe), cualquier excepción no controlada arrojada dentro de la DLL (como una desreferenciación de un puntero nulo o un desbordamiento al escribir en un arreglo que superó su límite asignado) arrastrará consigo al proceso completo, cerrando instantáneamente el terminal sin previo aviso ni logs de diagnóstico en los registros de Expert Advisors.13  
Para diagnosticar estos fallos se recomiendan las siguientes prácticas de ingeniería:

1. **Fijar el Debugger al Proceso de MetaTrader**: Configurar el entorno de desarrollo en C++ para adjuntar el depurador (*Attach to Process*) directamente a la instancia activa de terminal64.exe.13 De este modo, si se produce una violación de acceso en la DLL, el depurador detendrá la ejecución exactamente en la instrucción ensambladora causante del fallo de memoria.  
2. **Protección mediante Bloques de Manejo de Excepciones**: Envolver todas las operaciones expuestas en la API de la DLL dentro de bloques estructurados de captura de excepciones (try-catch nativo de C++ o mecanismos SEH de Windows) para interceptar cualquier falla y evitar que se propague de manera destructiva hacia el núcleo de MetaTrader 5\.13

## **Arquitectura de Comunicaciones de Red: WebRequest y Sockets de Bajo Nivel**

La intercomunicación eficiente con sistemas e infraestructuras externas a la red interna del broker es una piedra angular en el diseño de plataformas de trading cuantitativo de nivel empresarial.10 MQL5 ofrece dos mecanismos bien diferenciados para satisfacer estos requerimientos: funciones HTTP integradas de alto nivel y sockets de transporte de bajo nivel.10

### **Interacciones HTTP de Alto Nivel mediante WebRequest**

La función WebRequest proporciona una interfaz síncrona optimizada para el protocolo HTTP/HTTPS, diseñada para consumir de manera directa APIs REST, interactuar con servidores web intermedios y enviar telemetría de trading.10  
Existen dos firmas para WebRequest. La versión simplificada gestiona cabeceras predeterminadas limitadas a cookies e identificadores de origen (*referrer*).19 La versión extendida otorga un control total sobre el cuerpo y los encabezados del protocolo 19:

Fragmento de código  
int WebRequest(  
   const string      method,           // Método HTTP (GET, POST, HEAD, etc.)   
   const string      url,              // URL completa del servicio externo   
   const string      headers,          // Cabeceras HTTP personalizadas separadas por \\r\\n   
   int               timeout,          // Tiempo de espera máximo en milisegundos   
   const char        \&data,          // Cuerpo de la solicitud estructurado en arreglo binario   
   char              \&result,        // Arreglo binario destinado a almacenar la respuesta   
   string            \&response\_headers // Cabeceras de respuesta devueltas por el servidor   
);

#### **Restricciones de Seguridad, Ámbito y Bloqueo**

Para evitar el uso malicioso del protocolo y la fuga no controlada de datos de cuentas reales, la terminal MetaTrader 5 impone estrictas capas de control sobre WebRequest 10:

1. **Whitelisting Manual de Dominios**: Cualquier URL que deba ser contactada mediante WebRequest tiene que agregarse explícitamente en el menú de opciones de la plataforma, dentro de la pestaña **Expert Advisors** (Tools \> Options \> Expert Advisors).10 Intentar realizar peticiones a dominios ausentes en este listado retornará de manera automática el error 5200 (ERR\_WEBREQUEST\_INVALID\_ADDRESS) sin llegar a abrir la conexión de red.19  
2. **Restricciones de Hilos y Ámbito**: WebRequest es una función estrictamente **bloqueante (síncrona)**.19 Detiene por completo el hilo de ejecución actual hasta que el servidor web responda o expire el intervalo fijado en el parámetro timeout.19 Debido a este comportamiento síncrono, su ejecución está **estrictamente prohibida en indicadores personalizados**.19 Los indicadores de un mismo símbolo gráfico comparten un único hilo de ejecución de la terminal.20 Bloquear este hilo detendría por completo la actualización de los gráficos de precios y el procesamiento de nuevos ticks en todo el terminal.19  
3. **Gestión de Cookies por el Terminal**: El terminal almacena automáticamente las cookies devueltas en la cabecera Set-Cookie de las respuestas del servidor. En solicitudes posteriores al mismo dominio, el motor de WebRequest las inyecta de forma transparente en la cabecera Cookie: del mensaje saliente, manteniendo la sesión de usuario activa de manera compartida entre diferentes programas que utilicen el servicio.19  
4. **Entorno del Strategy Tester**: La función no tiene validez y se encuentra completamente inhabilitada dentro del Probador de Estrategias para evitar sesgos o filtraciones de información futura (*look-ahead bias*) durante las simulaciones históricas.19

### **Comunicaciones TCP de Bajo Nivel mediante Sockets**

Para escenarios de alta frecuencia, integraciones con brokers institucionales mediante protocolos propietarios (o estándares industriales como FIX/FAST) y streaming bidireccional de baja latencia, el protocolo HTTP resulta ineficiente debido a la sobrecarga de sus cabeceras. En su lugar, MQL5 expone un wrapper completo sobre la capa de transporte TCP (Transmission Control Protocol) del sistema operativo mediante las funciones Socket\* 10:

* **SocketCreate**: Instancia un descriptor de socket del sistema operativo.10 Un programa puede abrir hasta 128 sockets simultáneos.18  
* **SocketConnect**: Establece la conexión de red TCP bidireccional con la IP o dominio y puerto especificado con un tiempo de espera de control.18  
* **SocketSend**: Transmite un arreglo de bytes crudos (uchar) sobre el flujo activo.10  
* **SocketRead**: Operación bloqueante que recupera un volumen de bytes definidos desde la cola del búfer del socket, suspendiendo el hilo de ejecución hasta leer el tamaño solicitado o llegar a un timeout.10  
* **SocketIsReadable**: Devuelve inmediatamente la cantidad de bytes que están actualmente listos y depositados en el búfer de entrada del sistema operativo para ser recuperados por SocketRead, evitando llamadas bloqueantes innecesarias cuando no hay datos entrantes.10

#### **Implementación de un Protocolo de Comunicación Personalizado**

El diseño de comunicaciones sobre sockets TCP puros requiere que el desarrollador defina e el de control que el protocolo HTTP proporciona de manera integrada:

1. **Handshake a Nivel de Aplicación**: Fase de negociación inicial inmediatamente posterior al establecimiento de la conexión TCP donde las partes validan credenciales criptográficas, firmas digitales o definen el tamaño de payload máximo permitido.  
2. **Mensajes Estructurados y Framing**: TCP es un protocolo basado en flujos continuos de bytes (*stream-oriented*), no en paquetes delimitados. El receptor no tiene forma de saber dónde empieza o termina un mensaje lógico. Es indispensable diseñar un mecanismo de enmarcado (*framing*). Un enfoque óptimo consiste en utilizar un encabezado de tamaño fijo (ej. 4 bytes para codificar un entero de 32 bits que declare la longitud exacta del payload que sigue a continuación) o delimitar los mensajes utilizando secuencias específicas de caracteres de escape (como \\r\\n o delimitadores nulos \\0).  
3. **Mecanismos de Heartbeat (Keep-Alive)**: Los firewalls de red e intermediarios tienden a desconectar silenciosamente conexiones TCP inactivas. Se requiere enviar periódicamente paquetes pequeños de control para mantener activa la sesión física y detectar desconexiones silenciosas en el lado del cliente de forma proactiva.

#### **Protocolo de Seguridad TLS mediante SocketTLS**

La seguridad en el envío de datos de transacciones financieras requiere cifrado de extremo a extremo. MQL5 proporciona integración nativa de TLS (Transport Layer Security) para cifrar los canales TCP.10 El flujo de trabajo seguro se inicia conectando el socket mediante SocketConnect a un puerto estándar seguro (usualmente el puerto 443 para HTTPS).18  
Una vez establecida la conexión de transporte física, se debe llamar inmediatamente a la función **SocketTlsHandshake** para iniciar la negociación del protocolo seguro, pactar las claves simétricas de cifrado de sesión y validar la autenticidad del certificado del servidor mediante la infraestructura de clave pública (PKI) del sistema operativo.23 Una vez completada esta fase, los envíos y lecturas cifradas se gestionan mediante las llamadas especializadas **SocketTlsSend** y las variantes de lectura **SocketTlsRead** y **SocketTlsReadAvailable**.24 SocketTlsReadAvailable resulta idónea por su naturaleza no bloqueante, ya que recupera únicamente los datos ya desencriptados y disponibles en la cola del búfer del socket, retornando inmediatamente un valor de cero si la cola está momentáneamente vacía, lo que evita suspender innecesariamente el hilo de procesamiento principal.24

### **Código Funcional MQL5: WebRequest HTTP POST REST API**

El siguiente ejemplo demuestra cómo empaquetar un payload en formato JSON, configurar cabeceras personalizadas para una solicitud tipo POST segura y procesar la respuesta binaria de un servicio web compatible con el formato JSON 19:

Fragmento de código  
\#property copyright "Algorithmic Systems Architect"  
\#property version   "1.00"  
\#property script\_show\_inputs

input string ServerEndpoint \= "https://httpbin.org/post";  
input int    RequestTimeout \= 5000; // Timeout de red en milisegundos

void OnStart()  
{  
   // Estructura del cuerpo de la petición en formato JSON  
   string jsonPayload \= "{\\"magic\_number\\": 998877, \\"strategy\\": \\"Mean Reversion\\", \\"metric\\": \\"Sharpe Ratio\\"}";  
     
   // Conversión del string UTF-16 nativo a un arreglo binario codificado en UTF-8  
   char postData;  
   ArrayResize(postData, StringLen(jsonPayload));  
   int convertedBytes \= StringToCharArray(jsonPayload, postData, 0, WHOLE\_ARRAY, CP\_UTF8) \- 1; // Excluir null terminador  
     
   // Definición de cabeceras HTTP avanzadas para indicarle al servidor que procese JSON   
   string requestHeaders \= "Content-Type: application/json\\r\\n" \+  
                           "Accept: application/json\\r\\n" \+  
                           "User-Agent: MetaTrader/5.00 (MQL5 Quantitative Architecture)\\r\\n";  
     
   char responseBuffer;  
   string responseHeaders \= "";  
   ResetLastError();  
     
   Print("Enviando petición HTTP POST a: ", ServerEndpoint);  
     
   // Invocación síncrona de WebRequest (versión avanzada de 7 parámetros)   
   int httpResponseCode \= WebRequest(  
      "POST",  
      ServerEndpoint,  
      requestHeaders,  
      RequestTimeout,  
      postData,  
      responseBuffer,  
      responseHeaders  
   );  
     
   // Procesamiento de la respuesta del servidor  
   if(httpResponseCode \== \-1)  
   {  
      int errorCode \= \_LastError;  
      PrintFormat("Fallo del sistema al invocar WebRequest. Código de Error MQL5: %d", errorCode);  
        
      // Clasificación técnica del error para facilitar diagnósticos   
      switch(errorCode)  
      {  
         case 5200: Print("Diagnóstico: URL inválida o no presente en la whitelist del terminal."); break;  
         case 5201: Print("Diagnóstico: Error crítico de conexión al servidor de destino."); break;  
         case 5202: Print("Diagnóstico: El servidor superó el tiempo máximo de respuesta (Timeout)."); break;  
         default:   Print("Diagnóstico: Error interno de comunicaciones de red."); break;  
      }  
   }  
   else  
   {  
      PrintFormat("Servidor web respondió exitosamente. Código HTTP de Retorno: %d", httpResponseCode);  
        
      if(ArraySize(responseBuffer) \> 0\)  
      {  
         // Deserialización del búfer binario de respuesta codificado en UTF-8  
         string responseString \= CharArrayToString(responseBuffer, 0, WHOLE\_ARRAY, CP\_UTF8);  
         Print("Cuerpo de Respuesta JSON Recibido del Servidor:\\n", responseString);  
      }  
      else  
      {  
         Print("Advertencia: La petición finalizó correctamente pero el cuerpo de respuesta está vacío.");  
      }  
   }  
}

## **Persistencia y Sincronización Avanzada con SQLite Embebido**

El almacenamiento de datos históricos es vital para el desarrollo de estrategias de trading automáticas. El uso tradicional de archivos estructurados de texto plano (formatos .csv o .txt) resulta altamente ineficiente cuando las estrategias escalan en complejidad.25 Los accesos secuenciales obligan a reescribir archivos completos de varios megabytes para actualizar una sola línea, lo que genera sobrecarga de Entrada/Salida (I/O) en disco y fallos de bloqueo en accesos concurrentes de múltiples Expert Advisors concurrentes.25  
Para superar estas limitaciones, MQL5 incluye un motor de base de datos relacional embebido **SQLite** que se ejecuta de forma nativa directamente en el núcleo físico de la terminal, sin requerir configuraciones de administración de red ni servidores externos de base de datos.25

### **Diseño de un Esquema de Base de Datos Relacional para Trading**

Un diseño robusto de base de datos para operaciones cuantitativas debe estructurarse de manera modular y normalizada. La división lógica de las entidades garantiza la integridad referencial y simplifica la optimización de las consultas relacionales mediante índices balanceados.27  
El esquema de persistencia se divide en tres dominios físicos:

1. **DEALS**: Historial contable de transacciones físicas completadas.27  
2. **SIGNALS**: Bitácora de señales de trading generadas por los modelos matemáticos cuantitativos.27  
3. **EVENTS**: Registro de noticias macroeconómicas y fallas internas del sistema.27

### **Optimización de Inserción Masiva mediante Transacciones e Índices**

SQLite, por defecto, opera en un modo de confirmación automática (*auto-commit*).26 Esto significa que cada comando de inserción de datos individual se ejecuta de manera independiente en su propia transacción física, lo cual obliga a abrir y cerrar un flujo físico de escritura en disco duro por cada fila procesada.26 Este comportamiento limita la velocidad de escritura a una media de entre 50 y 100 inserciones por segundo.  
Para lograr optimizaciones de rendimiento de orden industrial, es imperativo agrupar las inserciones masivas dentro de un único bloque transaccional explícito utilizando las funciones **DatabaseTransactionBegin** y **DatabaseTransactionCommit**.27 La implementación correcta de este bloque reduce drásticamente los cuellos de botella de latencia física. La inserción de miles de registros puede llegar a completarse hasta **3500 veces más rápido** utilizando transacciones agrupadas en comparación con inserciones individuales directas.27

| Tipo de Ejecución | Volumen de Registros | Tiempo de Ejecución (ms) | Tiempo Promedio por Registro (ms) | Factor de Aceleración |
| :---- | :---- | :---- | :---- | :---- |
| Sin Transacciones (Auto-Commit) | 1,000 | 12,450 | 12.450 | Base (![][image12]) |
| Con Transacción Agrupada | 25,000 | 88 | 0.0035 | ![][image13] |

### **Código Funcional MQL5: Gestión de Base de Datos SQLite Transaccional**

El siguiente script crea un esquema relacional estructurado para un diario de trading integrado de tres tablas independientes, aplica inserción por lotes bajo transacciones explícitas de control, verifica la presencia de las tablas utilizando DatabaseTableExists y lee los datos utilizando el método optimizado DatabaseReadBind 26:

Fragmento de código  
\#property copyright "Algorithmic Systems Architect"  
\#property version   "1.00"  
\#property script\_show\_inputs

input string DBFilename \= "QuantitativeTradingJournal.sqlite";

void OnStart()  
{  
   Print("Inicializando base de datos SQLite embebida...");  
     
   // Inicialización y creación de la base de datos   
   int dbHandle \= DatabaseOpen(DBFilename, DATABASE\_OPEN\_READWRITE | DATABASE\_OPEN\_CREATE);  
   if(dbHandle \== INVALID\_HANDLE)  
   {  
      Print("Error fatal al inicializar base de datos: ", GetLastError());  
      return;  
   }  
     
   // Creación de las tres tablas recomendadas por el esquema relacional   
   string sqlDealsTable \=   
      "CREATE TABLE IF NOT EXISTS DEALS("  
      "  id INTEGER PRIMARY KEY AUTOINCREMENT,"  
      "  deal\_ticket INTEGER UNIQUE,"  
      "  order\_ticket INTEGER,"  
      "  symbol TEXT NOT NULL,"  
      "  type INTEGER,"  
      "  direction INTEGER,"  
      "  volume REAL,"  
      "  price\_open REAL,"  
      "  price\_close REAL,"  
      "  profit REAL,"  
      "  swap REAL,"  
      "  commission REAL,"  
      "  sl REAL,"  
      "  tp REAL,"  
      "  magic INTEGER,"  
      "  comment TEXT,"  
      "  time INTEGER,"  
      "  time\_msc INTEGER,"  
      "  reason INTEGER"  
      ");";

   string sqlSignalsTable \=   
      "CREATE TABLE IF NOT EXISTS SIGNALS("  
      "  id INTEGER PRIMARY KEY AUTOINCREMENT,"  
      "  symbol TEXT NOT NULL,"  
      "  signal\_type TEXT,"  
      "  price REAL,"  
      "  stop\_loss REAL,"  
      "  take\_profit REAL,"  
      "  strength REAL,"  
      "  source TEXT,"  
      "  notes TEXT,"  
      "  time INTEGER"  
      ");";

   string sqlEventsTable \=   
      "CREATE TABLE IF NOT EXISTS EVENTS("  
      "  id INTEGER PRIMARY KEY AUTOINCREMENT,"  
      "  event\_type TEXT,"  
      "  symbol TEXT,"  
      "  description TEXT,"  
      "  importance INTEGER,"  
      "  time INTEGER,"  
      "  actual REAL,"  
      "  previous REAL,"  
      "  forecast REAL"  
      ");";

   // Ejecución de esquemas de definición de datos   
   if(\!DatabaseExecute(dbHandle, sqlDealsTable) ||   
     \!DatabaseExecute(dbHandle, sqlSignalsTable) ||   
     \!DatabaseExecute(dbHandle, sqlEventsTable))  
   {  
      Print("Error crítico en la definición de las tablas: ", GetLastError());  
      DatabaseClose(dbHandle);  
      return;  
   }  
     
   // Verificación explícita de existencia de tablas mediante DatabaseTableExists   
   if(DatabaseTableExists(dbHandle, "DEALS"))  
   {  
      Print("Confirmado: Tabla 'DEALS' de auditoría contable existe en el esquema.");  
   }  
     
   // Creación de índices sobre columnas de búsqueda en consultas cuantitativas   
   DatabaseExecute(dbHandle, "CREATE INDEX IF NOT EXISTS idx\_deals\_magic ON DEALS(magic);");  
   DatabaseExecute(dbHandle, "CREATE INDEX IF NOT EXISTS idx\_deals\_time ON DEALS(time);");  
   DatabaseExecute(dbHandle, "CREATE INDEX IF NOT EXISTS idx\_signals\_time ON SIGNALS(time);");

   // Simulación de inserción masiva acelerada mediante transacciones explícitas   
   uint startTick \= GetTickCount();  
     
   // Apertura del bloque transaccional   
   if(DatabaseTransactionBegin(dbHandle))  
   {  
      bool operationSuccess \= true;  
      int recordsToInsert \= 1000;  
        
      for(int i \= 0; i \< recordsToInsert; i++)  
      {  
         int dealTicket \= 500000 \+ i;  
         int orderTicket \= 200000 \+ i;  
         double profit \= (double)(MathRand() % 1000\) \- 500.0;  
         double openPrice \= 1.0850 \+ (i \* 0.0001);  
         int magic \= 777123;  
           
         string insertQuery \= StringFormat(  
            "INSERT INTO DEALS (deal\_ticket, order\_ticket, symbol, type, direction, volume, price\_open, price\_close, profit, swap, commission, sl, tp, magic, comment, time, time\_msc, reason) "  
            "VALUES (%d, %d, 'EURUSD', %d, 0, 0.1, %f, %f, %f, 0.0, \-1.2, 0.0, 0.0, %d, 'MQL5 Advanced DB Test', %d, %d, 3);",  
            dealTicket, orderTicket, (i % 2), openPrice, openPrice \+ 0.0050, profit, magic, TimeCurrent(), TimeCurrent() \* 1000  
         );  
           
         if(\!DatabaseExecute(dbHandle, insertQuery))  
         {  
            PrintFormat("Error al insertar registro indexado %d. Abortando lote.", i);  
            operationSuccess \= false;  
            break;  
         }  
      }  
        
      // Cierre del lote: si todo fue exitoso consolidar en disco, de lo contrario revertir   
      if(operationSuccess)  
      {  
         DatabaseTransactionCommit(dbHandle); // Consolidación física atómica   
         uint elapsed \= GetTickCount() \- startTick;  
         PrintFormat("Inserción masiva de %d registros completada con éxito en %u ms.", recordsToInsert, elapsed);  
      }  
      else  
      {  
         DatabaseTransactionRollback(dbHandle); // Reversión total por fallo   
         Print("Fallo crítico detectado. Se ha ejecutado Rollback de la transacción completa.");  
      }  
   }  
     
   // Consulta de prueba utilizando cursores indexados para evitar lecturas de disco ineficientes   
   string selectQuery \= "SELECT deal\_ticket, price\_open, profit FROM DEALS WHERE magic \= 777123 LIMIT 5;";  
   int requestHandle \= DatabasePrepare(dbHandle, selectQuery);  
     
   if(requestHandle\!= INVALID\_HANDLE)  
   {  
      Print("Lectura de base de datos exitosa. Resultados:");  
        
      // Estructura para el mapeo de registros mediante DatabaseReadBind  
      struct LocalDealResult  
      {  
         int dealTicket;  
         double priceOpen;  
         double profit;  
      } result;  
        
      // Lectura progresiva utilizando DatabaseReadBind para mapeo directo \[25, 27\]  
      while(DatabaseRead(dbHandle, requestHandle))  
      {  
         if(DatabaseReadBind(requestHandle, result))  
         {  
            PrintFormat("-\> Deal Ticket: %d | Price Open: %f | Profit: %.2f USD",   
                        result.dealTicket, result.priceOpen, result.profit);  
         }  
      }  
      DatabaseFinalize(requestHandle); // Liberar descriptor de consulta  
   }  
   else  
   {  
      Print("Error al preparar la consulta de selección. Código: ", GetLastError());  
   }  
     
   // Cierre físico de la sesión de base de datos   
   DatabaseClose(dbHandle);  
}

## **Servicios en MQL5 (MQL5 Services) para Procesamiento en Segundo Plano**

La suite de MetaTrader 5 tradicionalmente se basaba de forma exclusiva en la interacción de gráficos activos, lo que obligaba a los Expert Advisors a ejecutarse necesariamente enlazados a la ventana visual de un activo financiero específico para responder a sus flujos de ticks o temporizadores.20 Para romper esta dependencia de la interfaz de usuario e implementar tareas del lado del servidor o de administración de la infraestructura, MetaTrader 5 incluye un tipo de programa llamado **Service** (Servicio).28

### **Arquitectura de un Servicio, Inicio y Ciclo de Vida**

Un servicio en MQL5 es un programa de un único hilo de ejecución que opera en segundo plano y que prescinde completamente de un entorno de gráfico o representación visual para su despliegue.20 El inicio del servicio se parametriza en el código mediante la inclusión de la directiva de compilación \#property service.29 Tras la compilación correcta del archivo ejecutable, el servicio se registra formalmente en el panel del Navegador del terminal, desde donde se pueden crear una o más instancias independientes configuradas con parámetros específicos.  
El ciclo de vida del servicio es controlado de forma directa por el hilo principal del terminal. El único punto de entrada de la ejecución es la función **OnStart**.30 El servicio arranca automáticamente de forma simultánea con el inicio físico del terminal de MetaTrader 5, garantizando que sus tareas comiencen sin mediar intervención del operador.  
Una vez iniciado, el servicio persiste activo ejecutando sus algoritmos dentro de un bucle de control controlado de forma estricta por la función preventiva de salida \!IsStopped().29 El servicio permanece activo de forma indefinida incluso a lo largo del cambio de perfiles, cierre de gráficos, apertura de nuevas cuentas reales o reinicios temporales, deteniéndose de forma exclusiva cuando el terminal es apagado o si el operador detiene manualmente la instancia de servicio desde el Navegador.28

### **Diferencias Operativas Críticas frente a los Expert Advisors**

Las diferencias arquitectónicas entre un servicio y un EA determinan sus casos de uso específicos en el desarrollo de software cuantitativo:

* **Punto de Entrada Principal**: El servicio depende exclusivamente de OnStart para su ciclo de ejecución 30, mientras que el EA se cimenta en la arquitectura de eventos estructurados de mercado (OnInit, OnDeinit, OnTick, OnTimer, OnTradeTransaction).31  
* **Dependencia Gráfica**: El servicio opera de manera totalmente agnóstica a la existencia de charts, lo que impide el uso de variables contextuales como \_Symbol o \_Period.28 Un EA requiere asignación obligatoria a un gráfico para ejecutarse.28  
* **Gestión de Eventos y Cola de Entrada**: Los servicios carecen de cola de eventos del terminal; no reciben notificaciones de fluctuación de precios de mercado (NewTick) ni de acciones de usuario sobre gráficos (ChartEvent).20 Toda su lógica debe operar bajo esquemas de monitoreo cíclico (*polling*) mediante bucles optimizados.29  
* **Persistencia Operativa**: Una vez lanzado, el servicio persiste a lo largo de todas las sesiones de trabajo del terminal, restaurándose automáticamente por el núcleo al iniciar el sistema.28 Los EAs se eliminan si el gráfico es destruido o si se altera drásticamente la configuración de perfiles del terminal.28

### **Patrones de Diseño Recomendados para Servicios**

Debido a su persistencia en segundo plano y a su naturaleza de ejecución en hilos independientes, los servicios son ideales para implementar los siguientes patrones arquitectónicos:

1. **Proxy de Comunicaciones y Servidores de Escucha (Gateway)**: Se puede diseñar un servicio que actúe como un servidor local abriendo un puerto mediante sockets TCP de bajo nivel y manteniendo un ciclo de aceptación bloqueante de conexiones concurrentes (blocking accept loop), actuando como pasarela (como el patrón de diseño RiskGateServer que gestiona de manera centralizada hasta 32 conexiones simultáneas provenientes de diferentes EAs activos en distintos gráficos de la plataforma).32  
2. **Monitoreo del Sistema y Recolección Periódica de Datos**: Recolección de telemetría de red, uso de recursos del sistema, salud de los hilos de los asesores expertos y volcado automático de métricas hacia sistemas externos para su posterior análisis.29

### **Código Funcional MQL5: Servicio de Monitoreo de Recursos y Estado**

El siguiente código implementa un servicio persistente que se inicia de manera automática con la terminal, comprueba de manera continua el estado de conexión con el servidor del broker y monitoriza el uso de margen de la cuenta de trading, registrando eventos de alerta en tiempo real en un archivo común 29:

Fragmento de código  
\#property copyright "Algorithmic Systems Architect"  
\#property version   "1.00"  
\#property service   // Registro explícito del programa como Servicio de background 

input uint   MonitorIntervalMs \= 5000;       // Intervalo de escaneo y diagnóstico  
input double MarginWarningRatio \= 200.0;     // Nivel de Margin Level (%) para alertas  
input string LogFilename         \= "InfrastructureMonitor.log";

void OnStart()  
{  
   Print("Servicio de Monitoreo de Infraestructura iniciado exitosamente.");  
     
   // Bucle principal infinito que garantiza la persistencia del servicio   
   while(\!IsStopped())  
   {  
      bool isConnected \= (bool)TerminalInfoInteger(TERMINAL\_CONNECTED);  
      long accountLogin \= AccountInfoInteger(ACCOUNT\_LOGIN);  
        
      // Apertura del archivo de registro en la carpeta común para el acceso multi-proceso  
      int fileHandle \= FileOpen(LogFilename, FILE\_WRITE | FILE\_READ | FILE\_TXT | FILE\_COMMON);  
        
      if(fileHandle\!= INVALID\_HANDLE)  
      {  
         FileSeek(fileHandle, 0, SEEK\_END); // Mover cursor al final para añadir registro  
         string timestamp \= TimeToString(TimeLocal(), TIME\_DATE | TIME\_MINUTES | TIME\_SECONDS);  
           
         if(\!isConnected)  
         {  
            string alertMsg \= StringFormat("\[%s\] Alerta: Terminal desconectada de los servidores del Broker.", timestamp);  
            FileWriteString(fileHandle, alertMsg \+ "\\r\\n");  
            Print(alertMsg);  
         }  
         else  
         {  
            double marginLevel \= AccountInfoDouble(ACCOUNT\_MARGIN\_LEVEL);  
              
            if(marginLevel \> 0 && marginLevel \< MarginWarningRatio)  
            {  
               string alertMsg \= StringFormat("\[%s\] Cuenta %d \- Nivel de Margen bajo: %.2f%% (Límite: %.2f%%)",   
                                              timestamp, accountLogin, marginLevel, MarginWarningRatio);  
               FileWriteString(fileHandle, alertMsg \+ "\\r\\n");  
               Print(alertMsg);  
            }  
            else  
            {  
               int pingTime \= (int)TerminalInfoInteger(TERMINAL\_PING\_LAST);  
               string logMsg \= StringFormat("\[%s\]\[INFO\] Operación normal. Cuenta: %d | Latencia: %d ms | Margin Level: %.2f%%",   
                                            timestamp, accountLogin, pingTime, marginLevel);  
               FileWriteString(fileHandle, logMsg \+ "\\r\\n");  
            }  
         }  
         FileClose(fileHandle);  
      }  
      else  
      {  
         Print("Error al intentar escribir en el archivo común de logs. Código: ", GetLastError());  
      }  
        
      Sleep(MonitorIntervalMs); // Pausa para liberar ciclos de CPU al sistema operativo   
   }  
     
   Print("Servicio de Monitoreo de Infraestructura detenido.");  
}

## **Análisis Crítico de la Standard Library de MQL5**

La suite MetaTrader 5 incluye una extensa biblioteca de clases orientada a objetos conocida como la **Standard Library (Librería Estándar)**. Esta colección proporciona wrappers que abstraen gran parte de las complejidades operativas del lenguaje.

### **Estructura de Clases e Infraestructura de UI**

La Standard Library se segmenta en varios dominios funcionales clave:

1. **Clases de Negociación (Trading)**: Abstraen la complejidad de la estructuración interna de órdenes asíncronas de mercado. Destacan CTrade para envío de órdenes, CPositionInfo para consulta y selección de posiciones activas, y clases accesorias como COrderInfo, CDealInfo, CAccountInfo y CSymbolInfo.34  
2. **Clases de Indicadores Técnicos**: Instancian, actualizan y liberan de forma automática la memoria asociada con indicadores integrados en el terminal (como CiMA para medias móviles, CiRSI para índice de fuerza relativa y CiMACD para divergencia de convergencia de medias móviles).35  
3. **Clases de Interfaz de Usuario (UI)**: Proporcionan una jerarquía para la construcción de cuadros de diálogo y paneles de trading visuales embebidos en el gráfico financiero (CAppDialog, CPanel, CButton, CLabel, CEdit, CListView).  
4. **Estructuras de Datos Genéricas**: Clases como CList proporcionan implementaciones nativas de estructuras complejas como listas doblemente enlazadas donde cada nodo posee referencias bidireccionales, facilitando la gestión estructurada de colas de ejecución o secuencias dinámicas de objetos.35

### **El Framework Modular CExpert**

En el nivel más alto de abstracción, MetaQuotes provee el framework **CExpert**, diseñado para ensamblar de manera automática arquitecturas modulares de trading algorítmico.36 Este framework se integra de forma directa con el **MQL5 Wizard** (Asistente del editor de código), lo que permite estructurar un EA modular combinando tres subsistemas independientes 36:

* **Mecanismo de Señales (CExpertSignal)**: Genera niveles teóricos de entrada y salida basados en condiciones lógicas o patrones técnicos.  
* **Mecanismo de Gestión Monetaria (CExpertMoney)**: Define el tamaño dinámico de la posición o volumen según las reglas de control de riesgo.  
* **Mecanismo de Trailing Stop (CExpertTrailing)**: Ajusta dinámicamente el Stop Loss para proteger las utilidades generadas a lo largo de la vida del trade.

### **Evaluación Crítica: ¿Adoptar CExpert o Desarrollar un Framework Propietario?**

A pesar de las ventajas teóricas que ofrece el framework CExpert en términos de prototipado rápido y estandarización visual 37, un análisis de ingeniería cuantitativa revela deficiencias de diseño severas que desaconsejan su uso en entornos de producción profesional o de trading de alta frecuencia:

* **Netting vs Hedging y Gestión de Posición Única**: El diseño subyacente de CExpert y clases de soporte como CPositionInfo fue optimizado originalmente para cuentas de tipo *Netting*.34 El framework presenta carencias críticas y limitaciones para gestionar de forma nativa múltiples posiciones concurrentes bajo entornos *Hedging* de forma robusta.34 No existe un soporte nativo maduro para administrar grupos de posiciones asociadas bajo una misma lógica de cobertura de manera aislada.34  
* **Soporte Incompleto o Inconcluso en la Librería**: Un examen detallado del código fuente de CExpert revela áreas de la API que quedaron inconclusas o no implementadas activamente por MetaQuotes.34 Por ejemplo, miembros declarados como m\_max\_orders (destinados teóricamente a limitar el número máximo de órdenes pendientes permitidas de forma concurrente) no se utilizan en ninguna sección de la lógica interna de ejecución o de envío de transacciones del framework, lo que expone su estado incompleto.34  
* **Obsolescencia de Eventos**: El diseño de CExpert sigue atado a flujos de control antiguos como el evento básico OnTrade(), en lugar de modernizarse para procesar de manera atómica el flujo detallado de la estructura transaccional provisto por el manejador avanzado OnTradeTransaction().34

**Veredicto de Ingeniería Cuantitativa**: Para proyectos profesionales de nivel empresarial, la mejor práctica consiste en **diseñar y escribir un framework propietario estructurado desde cero**.34 Es preferible implementar clases de envoltura personalizadas (como un gestor experto modular CMyExpert) que aprovechen únicamente los componentes más básicos, eficientes y probados de la Standard Library (tales como CTrade para envíos transaccionales y CList para la gestión de nodos de memoria).34 Esto permite cimentar la arquitectura sobre el manejador moderno de transacciones OnTradeTransaction(), garantizando soporte nativo total para modelos de cobertura multidireccional (*hedging*), eliminando sobrecarga de llamadas virtuales innecesarias y asegurando un control absoluto sobre el flujo de ejecución.34

## **Creación de Instrumentos Sintéticos mediante Custom Symbols**

El análisis cuantitativo avanzado de activos altamente correlacionados requiere evaluar cotizaciones ausentes en la oferta estándar que proporciona el servidor del broker de trading habitual. MQL5 resuelve esta necesidad mediante la funcionalidad de **Custom Symbols** (Símbolos Personalizados), que permite crear, configurar e inyectar datos de forma completamente programática a instrumentos financieros sintéticos personalizados.38

### **Creación Programática mediante CustomSymbolCreate**

La inicialización de un símbolo personalizado se realiza mediante la función CustomSymbolCreate 38:

Fragmento de código  
bool CustomSymbolCreate(  
   const string symbol\_name,   // Nombre del activo sintético (ej. "SYN\_EURUSD") \[38\]  
   const string symbol\_path,   // Grupo o jerarquía en Market Watch (ej. "Quantitative\\\\Sinteticos") \[38\]  
   const string symbol\_origin  // Símbolo de origen para copiar propiedades base \[38\]  
);

Posteriormente, se deben configurar los parámetros regulatorios y físicos del activo, como el valor del punto flotante, el número de dígitos decimales de precisión, los márgenes de apalancamiento permitidos y el tamaño del contrato financiero, utilizando funciones nativas como CustomSymbolSetInteger, CustomSymbolSetDouble y CustomSymbolSetString.39

### **Inyección de Datos: Actualización de Barras y Ticks**

Una vez creado el símbolo personalizado, se requiere suministrarle un flujo de datos históricos estructurado para permitir su visualización en gráficos o su ejecución analítica dentro del Strategy Tester.39 El sistema de MetaTrader 5 permite actualizar la información mediante dos mecanismos:

1. **Datos Históricos de Barras de Minuto (M1)**: La actualización de la estructura clásica de velas de precios OHLC (Open, High, Low, Close) se ejecuta mediante la función **CustomRatesUpdate** o la variante de reemplazo absoluto de intervalos temporales **CustomRatesReplace**.39 Las estructuras pasadas a través del arreglo de tipo MqlRates deben alinearse de forma exacta a marcas de tiempo consecutivas del timeframe M1.40  
2. **Datos Históricos de Ticks de Alta Precisión**: Para simulaciones realistas que tomen en cuenta la volatilidad instantánea del spread del bid y ask, se utiliza la función **CustomTicksAdd** o **CustomTicksReplace**.39 CustomTicksAdd transmite ticks directamente a la ventana de Market Watch (desde donde la terminal los consolida de forma diferida en la base de datos de ticks), requiriendo que el símbolo personalizado esté seleccionado activamente en dicha ventana para procesar el flujo.42 Si se transmiten bloques masivos de más de 256 ticks en una sola llamada, la función optimiza automáticamente el uso de recursos escribiendo la porción mayoritaria directamente en los archivos físicos de la base de datos de ticks (como lo hace CustomTicksReplace), y enviando únicamente las últimas 128 transacciones instantáneas a Market Watch.42

#### **Reglas de Procesamiento de Marcas de Tiempo en Ticks**

La estructura MqlTick expone dos campos temporales que deben rellenarse con precisión milimétrica 42: time (segundos desde el 01.01.1970) y time\_msc (milisegundos desde la misma época).42 Al inyectar datos con CustomTicksAdd, el motor procesa estos campos bajo tres reglas jerárquicas estrictas 42:

* **Regla de Precisión de Milisegundos (time\_msc\!= 0\)**: Se utiliza el valor de time\_msc para calcular de forma matemática el valor correspondiente en segundos mediante división entera, forzando la asignación: time \= time\_msc / 1000\.42  
* **Regla de Fallback de Segundos (time\_msc \== 0 y time\!= 0\)**: La precisión de milisegundos se extrapola multiplicando el valor en segundos, forzando la asignación: time\_msc \= time \* 1000\.42  
* **Regla de Tiempo del Servidor (time\_msc \== 0 y time \== 0\)**: El motor de la terminal asigna la hora actual del servidor comercial al milisegundo en el momento exacto de la llamada a la función.42

Para que un tick sea válido, debe contener valores de cotización superiores a cero y asociarse con banderas descriptivas específicas de la naturaleza del cambio 42: TICK\_FLAG\_BID para cambios en el precio de venta, TICK\_FLAG\_ASK para cambios en el precio de compra, TICK\_FLAG\_LAST para transacciones ejecutadas o TICK\_FLAG\_VOLUME para alteraciones en el volumen transaccionado.42

### **Casos de Uso Estratégicos de Activos Sintéticos**

* **Índices Personalizados de Divisas Ponderadas (Baskets)**: Modelado de un activo que represente la fortaleza de una divisa frente a una canasta ponderada de contrapartes.  
* **Trading de Spreads de Correlación Cruzada (Pairs Trading)**: Creación de un activo que represente el diferencial o spread instantáneo de arbitraje estadístico de reversión a la media entre dos activos altamente correlacionados (como EURUSD y GBPUSD), permitiendo evaluar y probar la estrategia directamente sobre el gráfico sintético resultante.  
* **Importación de Activos de Fuentes de Datos Externas**: Traer feeds históricos reales de criptomonedas directamente desde exchanges, o activos de renta variable no provistos por el broker para ejecutar análisis cuantitativos exhaustivos en el Strategy Tester.39

### **Código Funcional MQL5: Creación de Custom Symbol e Importación**

El siguiente script crea un símbolo sintético en el terminal, configura sus propiedades financieras físicas y le inyecta un lote de barras históricas M1 generadas mediante simulación matemática 38:

Fragmento de código  
\#property copyright "Algorithmic Systems Architect"  
\#property version   "1.00"  
\#property script\_show\_inputs

\#define SYNTHETIC\_NAME "SYN\_EURUSD"  
\#define SYNTHETIC\_GROUP "Quantitative\\\\Sinteticos"

void OnStart()  
{  
   Print("Creando símbolo sintético programático...");  
     
   // Eliminar instancia preexistente si existiera para garantizar una inicialización limpia  
   ResetLastError();  
   if(SymbolInfoInteger(SYNTHETIC\_NAME, SYMBOL\_EXIST))  
   {  
      SymbolSelect(SYNTHETIC\_NAME, false);  
      if(CustomSymbolDelete(SYNTHETIC\_NAME))  
      {  
         Print("Símbolo personalizado previo eliminado para resetear historial.");  
      }  
   }  
     
   // Creación del Custom Symbol copiando propiedades iniciales de EURUSD estándar \[38\]  
   if(\!CustomSymbolCreate(SYNTHETIC\_NAME, SYNTHETIC\_GROUP, "EURUSD"))  
   {  
      Print("Error crítico al crear el símbolo sintético personalizado. Error: ", GetLastError());  
      return;  
   }  
     
   // Configuración avanzada de las propiedades financieras del Custom Symbol   
   CustomSymbolSetString(SYNTHETIC\_NAME, SYMBOL\_DESCRIPTION, "Sintético Cuantitativo de Prueba");  
   CustomSymbolSetInteger(SYNTHETIC\_NAME, SYMBOL\_DIGITS, 5);  
   CustomSymbolSetDouble(SYNTHETIC\_NAME, SYMBOL\_VOLUME\_MIN, 0.01);  
   CustomSymbolSetDouble(SYNTHETIC\_NAME, SYMBOL\_VOLUME\_MAX, 100.0);  
   CustomSymbolSetDouble(SYNTHETIC\_NAME, SYMBOL\_VOLUME\_STEP, 0.01);  
     
   // Mostrar el símbolo en la tabla activa de Market Watch  
   SymbolSelect(SYNTHETIC\_NAME, true);  
     
   // Preparación del lote de barras históricas M1 artificiales  
   int totalBars \= 500;  
   MqlRates rates;  
   ArrayResize(rates, totalBars);  
     
   datetime startTime \= TimeCurrent() \- (totalBars \* 60); // Iniciar barra de tiempo 500 minutos atrás  
   double simulatedPrice \= 1.0850;  
     
   for(int i \= 0; i \< totalBars; i++)  
   {  
      double variation \= ((double)MathRand() / 32767.0 \- 0.5) \* 0.0010;  
      double open \= simulatedPrice;  
      double close \= simulatedPrice \+ variation;  
      double high \= MathMax(open, close) \+ 0.0002;  
      double low \= MathMin(open, close) \- 0.0002;  
        
      rates\[i\].time \= startTime \+ (i \* 60); // Alineación a intervalos de M1   
      rates\[i\].open \= open;  
      rates\[i\].high \= high;  
      rates\[i\].low \= low;  
      rates\[i\].close \= close;  
      rates\[i\].tick\_volume \= 100;  
      rates\[i\].spread \= 15;  
      rates\[i\].real\_volume \= 0;  
        
      simulatedPrice \= close;  
   }  
     
   // Inyección física del lote de barras generadas en el historial del símbolo \[39, 40\]  
   int updatedBars \= CustomRatesUpdate(SYNTHETIC\_NAME, rates);  
   if(updatedBars \> 0\)  
   {  
      PrintFormat("Historial inyectado con éxito en el activo '%s'. Velas M1 añadidas: %d",   
                  SYNTHETIC\_NAME, updatedBars);  
   }  
   else  
   {  
      Print("Error crítico al intentar inyectar los datos de barras M1. Código: ", GetLastError());  
   }  
}

## **Cómputo Científico Avanzado: Matrices y Vectores en MQL5 Moderno**

En builds recientes, MetaTrader 5 ha incorporado soporte nativo para los tipos de datos integrados de **matrices (matrix) y vectores (vector)**, diseñados específicamente para implementar computación matemática, simulación científica avanzada y machine learning directamente en la terminal sin requerir librerías externas ni recurrir a bucles de cálculo ineficientes de MQL5.43

### **Estructura de Tipos, Inicialización y Métodos Integrados**

Los tipos se segmentan según su precisión y componentes matemáticos 43:

* **matrix y vector**: Elementos estándar representados en precisión doble de punto flotante de 64 bits (double).43  
* **matrixf y vectorf**: Elementos de precisión simple de 32 bits (float).43  
* **matrixc y vectorc**: Soporte avanzado de números complejos.43

La API nativa para estos objetos incluye métodos de inicialización que permiten generar con una sola línea de código arreglos predefinidos que típicamente requerirían de bucles anidados manuales:

Fragmento de código  
matrix A \= matrix::Identity(5, 5); // Matriz Identidad de 5x5   
matrix B \= matrix::Zeros(3, 4);    // Matriz de ceros de 3x4   
matrix C \= matrix::Full(2, 3, 3.14); // Matriz inicializada con pi en cada elemento 

La biblioteca incluye una colección de métodos de álgebra lineal de orden superior, abarcando productos punto, inversiones de matrices, determinantes y descomposiciones complejas, los cuales se ejecutan de manera directa en el núcleo de la plataforma utilizando rutinas optimizadas de bajo nivel 43:

* **Multiplicación Matricial**: Ejecutada mediante el método nativo .MatMul o el producto punto .Dot.6  
* **Inversión de Matrices**: Calculada eficientemente a través de la llamada .Inv.44  
* **Descomposiciones Matriciales Científicas**: Soporte directo para descomposición en valores singulares .SVD, factorización de Cholesky .Cholesky (fundamental para simulaciones de Montecarlo correlacionadas) y descomposición QR .QR.44

### **Comparativa Técnica frente a NumPy de Python**

La API integrada de matrices y vectores de MQL5 ha sido modelada deliberadamente a partir de las firmas y comportamientos de la popular librería científica **NumPy** de Python, facilitando de forma directa la traducción de algoritmos cuantitativos avanzados de un entorno a otro.43

| Operación Algorítmica | Sintaxis en Python (NumPy) | Sintaxis Equivalente en MQL5 | Compatibilidad e Impacto de Rendimiento |
| :---- | :---- | :---- | :---- |
| **Cambio de Dimensiones** | A.reshape((rows, cols)) | A.Reshape(rows, cols) 44 | Cambia las dimensiones dinámicamente sin duplicar la memoria.44 |
| **Media Aritmética** | A.mean(axis=0) | A.Mean(0) 44 | Cálculo optimizado de la media en un eje específico (Axis 0 o 1).44 |
| **Suma sobre Eje** | A.sum(axis=1) | A.Sum(1) 44 | Procesamiento de la suma acumulada de manera eficiente.44 |
| **Inversión Matricial** | np.linalg.inv(A) | A.Inv() 44 | Invierte la matriz en el mismo bloque de memoria asignado.44 |
| **Descomposición SVD** | U, S, V \= np.linalg.svd(A) | A.SVD(U, V, S) 44 | Computación directa en MQL5 sin necesidad de enlazar DLLs de Python.44 |

### **Limitaciones del Cómputo Matricial en MQL5 Moderno**

A pesar de las ventajas, existen importantes diferencias y limitaciones técnicas con respecto a la flexibilidad que ofrece la librería nativa de Python 44:

1. **Ausencia de Conversión de Tipos (Type Casting Implícito)**: Mientras que Python/NumPy gestiona automáticamente la coerción de tipos, el compilador de MQL5 rechaza cualquier mezcla de tipos de precisión.44 No existe cast automático entre un objeto matrix (double) y matrixf (float); cualquier intento de operación cruzada provocará un error de compilación inmediato.44  
2. **Falta de Tratamiento de Vectores como Sub-Matrices**: MQL5 mantiene una separación categórica estricta a nivel del compilador entre los tipos de datos vector (arreglo unidimensional) y matrix (arreglo bidimensional).44 La plataforma no aplica herencia de clases orientada a objetos entre ambos ni convierte de forma automática un vector a una matriz de columna o fila unitaria. Si un método del sistema espera una estructura de tipo matrix, rechazaría de inmediato un argumento de tipo vector.44  
3. **Restricciones de Correlación y Convolución**: Las operaciones de procesamiento de señales sobre vectores como .CorrCoef (coeficiente de correlación de Pearson) 44, .Correlate (correlación cruzada) 44 y .Convolve (convolución discreta lineal) 44 se comportan con un alto rendimiento matemático pero carecen de la flexibilidad de difusión (*broadcasting*) automática de ejes múltiples de NumPy, obligando al desarrollador a ajustar las dimensiones de sus matrices con precisión de forma manual antes de cada cómputo.

## **Conclusiones e Implicaciones de Ingeniería Cuantitativa**

El desarrollo de software financiero de nivel institucional sobre MetaTrader 5 exige trascender el paradigma básico de codificación centrado en gráficos y asimilar las capacidades avanzadas de extensibilidad y comunicación de la plataforma:

1. **Computación GPU mediante OpenCL**: Representa la solución óptima para procesar cálculos de optimización estadística no lineales o evaluar modelos matemáticos de gran escala.1 Al programar kernels OpenCL, es vital estructurar mecanismos de mitigación de errores para hardware de usuario final sin soporte nativo fp64, asegurando flujos lógicos con *fallbacks* controlados a precisión simple o cómputo multihilo en CPU.4  
2. **Extensibilidad Nativa con DLLs**: Ofrece un canal de integración inestimable para acceder a librerías de bajo nivel y APIs operativas complejas.10 Sin embargo, debido al potencial destructivo de fallos de memoria que colapsan la terminal de trading completa, las DLLs deben empaquetarse de manera preventiva bajo alineaciones estrictas de un solo byte (\#pragma pack(1)) y gestionarse mediante aislamiento estricto de excepciones de bajo nivel.13  
3. **Comunicaciones Robustas de Red**: El uso síncrono y bloqueante de WebRequest debe restringirse para la recolección estática de datos iniciales en Expert Advisors o scripts de gestión, estando totalmente proscrito en indicadores.19 Para sincronizaciones de datos de alta frecuencia y flujos bidireccionales en tiempo real, se debe optar por sockets TCP seguros y encriptados bajo protocolos estructurados de control de frames y latencia, aislando la lógica en un hilo de procesamiento en segundo plano.10  
4. **Persistencia Avanzada mediante SQLite**: El motor nativo de SQLite reemplaza con creces las ineficiencias críticas de persistencia basadas en archivos de texto.25 El uso de índices lógicos balanceados y transacciones en lote proporciona las bases para diseñar diarios de trading históricos de alta velocidad y sincronizar estados entre múltiples robots financieros activos.8  
5. **Servicios en Segundo Plano (Services)**: Proporcionan una arquitectura de software sin precedentes en la suite de MetaQuotes para diseñar monitores operativos independientes de gráficos y proxies de comunicación que se ejecutan de manera integrada en el terminal desde su encendido inicial.28  
6. **Símbolos Sintéticos e Instrumentos Sintéticos**: La flexibilidad que otorga la creación programática de activos personalizados permite estructurar simulaciones históricas complejas que facilitan el backtesting de estrategias algorítmicas avanzadas (como spread trading o portfolios ponderados) con la máxima precisión de ticks.39  
7. **Estructuras Matriciales y de Vectores**: Permiten un desarrollo cuantitativo ágil que minimiza los tiempos de codificación y asimila la lógica del ecosistema NumPy de Python directo en MQL5.43 La velocidad computacional nativa y la cercanía sintáctica de estos tipos los convierten en el estándar idóneo para el modelado de álgebra lineal en el terminal.43

#### **Fuentes citadas**

1. Built-in support for parallel computing: OpenCL \- Advanced language tools \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/ko/book/advanced/opencl](https://www.mql5.com/ko/book/advanced/opencl)  
2. OpenCL: Parallel computations in MQL5 \- MetaTrader 5 features for algorithmic trading, acceso: junio 28, 2026, [https://www.mql5.com/en/neurobook/index/algotrading/opencl](https://www.mql5.com/en/neurobook/index/algotrading/opencl)  
3. Understand and efficiently use OpenCL API by recreating built-in support as DLL on Linux (Part 1): Motivation and validation \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/12108](https://www.mql5.com/en/articles/12108)  
4. Working with OpenCL \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/opencl](https://www.mql5.com/en/docs/opencl)  
5. OpenCL is dead within the Mql5 ecostytem or in general, but there are no standards for an open library that, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/446275/page2](https://www.mql5.com/en/forum/446275/page2)  
6. CLBufferWrite \- Working with OpenCL \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/opencl/clbufferwrite](https://www.mql5.com/en/docs/opencl/clbufferwrite)  
7. CLProgramCreate \- Working with OpenCL \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/opencl/clprogramcreate](https://www.mql5.com/en/docs/opencl/clprogramcreate)  
8. Developing a multi-currency Expert Advisor (Part 22): Starting the transition to hot swapping of settings \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/16452](https://www.mql5.com/en/articles/16452)  
9. Network Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/network](https://www.mql5.com/en/docs/network)  
10. Exposing C\# code to MQL5 using unmanaged exports \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/249](https://www.mql5.com/en/articles/249)  
11. Passing string to c\# dll and get string \- Indices \- MQL4 and MetaTrader 4 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/150219](https://www.mql5.com/en/forum/150219)  
12. Passing a string to a DLL Function \- MT5 \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/220214](https://www.mql5.com/en/forum/220214)  
13. Passing a String/String Array reference to C++ or how to write a result handle for mysql \- Day Trading \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/220373](https://www.mql5.com/en/forum/220373)  
14. DLL access to all bars, need help\! \- Price Chart \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/185690](https://www.mql5.com/en/forum/185690)  
15. Structures, Classes and Interfaces \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/classes](https://www.mql5.com/en/docs/basis/types/classes)  
16. Returning a char\* string from a DLL in MT4 eats memory \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/125111](https://www.mql5.com/en/forum/125111)  
17. Establishing and breaking a network socket connection \- Advanced language tools \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/network/network\_socket\_create\_connect](https://www.mql5.com/en/book/advanced/network/network_socket_create_connect)  
18. Data exchange with a web server via HTTP/HTTPS \- Advanced ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/network/network\_http](https://www.mql5.com/en/book/advanced/network/network_http)  
19. Program Running \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/runtime/running](https://www.mql5.com/en/docs/runtime/running)  
20. SocketIsConnected \- Network Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/network/socketisconnected](https://www.mql5.com/en/docs/network/socketisconnected)  
21. SocketCreate \- Network Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/network/socketcreate](https://www.mql5.com/en/docs/network/socketcreate)  
22. SocketTlsHandshake \- Network Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/network/sockettlshandshake](https://www.mql5.com/en/docs/network/sockettlshandshake)  
23. Reading and writing data over a secure socket connection ... \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/network/network\_socket\_tls\_send\_read](https://www.mql5.com/en/book/advanced/network/network_socket_tls_send_read)  
24. Simplifying Databases in MQL5 (Part 1): Introduction to Databases and SQL \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/19285](https://www.mql5.com/en/articles/19285)  
25. Implementing Practical Modules from Other Languages in MQL5 (Part 01): Building the SQLite3 Library, Inspired by Python, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/18640](https://www.mql5.com/en/articles/18640)  
26. Algorithmic Trading Without the Routine: Quick Trade Analysis in ..., acceso: junio 28, 2026, [https://www.mql5.com/en/articles/22009](https://www.mql5.com/en/articles/22009)  
27. Scripts and services \- Creating application programs \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/script\_service](https://www.mql5.com/en/book/applications/script_service)  
28. Services \- Creating application programs \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/script\_service/services](https://www.mql5.com/en/book/applications/script_service/services)  
29. OnStart \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/onstart](https://www.mql5.com/en/docs/event_handlers/onstart)  
30. Overview of event handling functions \- Creating application programs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/runtime/runtime\_events\_overview](https://www.mql5.com/en/book/applications/runtime/runtime_events_overview)  
31. RiskGate: Centralized Risk Management for Multiple EAs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/21720](https://www.mql5.com/en/articles/21720)  
32. Event-Driven Architecture in MQL5: How to Turn an Expert Advisor into a Full-Fledged Trading System, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/22383](https://www.mql5.com/en/articles/22383)  
33. CPositionInfo: How does SelectByMagic work if there are multiple positions with the same magic number? \- How to Join Forex \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/322694](https://www.mql5.com/en/forum/322694)  
34. MQL5 Cookbook: Implementing an Associative Array or a Dictionary for Quick Data Access, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/1334](https://www.mql5.com/en/articles/1334)  
35. The MQL5 Standard Library Explorer (Part 5): Multiple Signal Expert \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/20289](https://www.mql5.com/en/articles/20289)  
36. The MQL5 Standard Library Explorer (Part 4): Custom Signal Library \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/20266](https://www.mql5.com/en/articles/20266)  
37. CustomSymbolCreate \- Custom Symbols \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customsymbols/customsymbolcreate](https://www.mql5.com/en/docs/customsymbols/customsymbolcreate)  
38. Custom Symbols \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customsymbols](https://www.mql5.com/en/docs/customsymbols)  
39. CustomRatesUpdate \- Custom Symbols \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customsymbols/customratesupdate](https://www.mql5.com/en/docs/customsymbols/customratesupdate)  
40. CustomRatesReplace \- Custom Symbols \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customsymbols/customratesreplace](https://www.mql5.com/en/docs/customsymbols/customratesreplace)  
41. CustomTicksAdd \- Custom Symbols \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customsymbols/customticksadd](https://www.mql5.com/en/docs/customsymbols/customticksadd)  
42. Matrices and vectors \- Data Types \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/types/matrix\_vector](https://www.mql5.com/en/docs/basis/types/matrix_vector)  
43. Types of matrices and vectors \- Common APIs \- MQL5 Programming ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/common/matrices/matrices\_types](https://www.mql5.com/en/book/common/matrices/matrices_types)  
44. Correlate \- Products \- Matrix and Vector Methods \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/matrix/matrix\_products/matrix\_correlate](https://www.mql5.com/en/docs/matrix/matrix_products/matrix_correlate)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEIAAAAaCAYAAAADiYpyAAACPElEQVR4Xu2WPU8XQRDGRxITI0giMbGRngjY2NDQmUDUlobCytAhJFQUhNhoIS0fgArExAb9AFoYGjo7Y4xRIUbeUVBQcB52h5sb7mUXkn+1v+TJ7c1ztzc3ezd3RIlEIhHOJOsn68hrKW+f4jNlx+K8sbzdEH6w/lGWh+UNZR60krer0SeWcYs1Qe6Y28ZrNKOst+RyGTeegGJF85WyJ6OML6x3VH1Mo1jz27LF62Y9s8E67rIesl5R8aTgpd+WXbiMQRswXGRdscEAJIf3ftypPDDHajWxWhb9Fu970U22sIb9GP4L5dVxnbVlg55m1r4NBnCBteDHmAM57WT2MUX3UYuchPce4xvKA7/9to+cf1N5IWA+vHYa3MCBiYXyiPI96pBcXiiQcKa5v6kxJnyg9kfIJQ3w5Jyp0kw765cfY76/yotF+oPQTy4veUo6WE8yOwys8pDax4Qzal+/BrH9wSLFOE8RQFEOOrfnlC1eMNIfBEyGrwNY1gY5b97EYmgj98juWSOCJtZrG2SmyeWHpl9UqFrsSVLZXlaXit/zcdudQ5EigGusXeXFgIbeY4Meyf2PNUL4bvZXyU32wcTxx2mLFspVOt28UAzpGTFs24DiE7kcH1ujCnTYj+R+mTWzVHzDUu1Y8C2Xr44FxbBfkyrukMvhsjU8eOrgX7JGGVOsTXLdF99f3bzuswbUPlZNjsVqYGXLfmmLwK9wFfiZQkHqQME2WOt+/DRvnxBT2EQikUgkEonEefgPXw6PfZWt0IMAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHcAAAAaCAYAAACNU8MOAAAD1UlEQVR4Xu2YSejNURTHjymJJElEscDCPJUFsiAyLER2sjImWfxXZFpYEBZkSDKVKGSIKNOCEsqCnUTmUuZ55n7/516/8zvv93vv3t97/i/cT53ePd9z37m/4Y4/okgkEolEIvVgpbF3xn5au54Ol3Cfkrr4X0M67MUuY28pybMnFWW+UxKHjU2Hm4xBxp4TX8MVYx3S4d9sMPaFuO4oFXP0MnaVONc5FZP45ApCPsg8BhpbTlxnmIoVoVKbF4gfiA9Hjb001lUHqmC+sU3C30d8rUOFBl4bWy38j8bWCB+MofR9Dla+wydXMI8oGcF5PDR2mcrX8aWZsdPELwX5pqXDjRRpZyvxqB+iAwXI6nhaw4yi63TM0OAvUBpGJ2YDh2+uICYZm23sJOUnOmJ/9c0VZbGx4bacl/ObFgJwM8xkHQgAHV5fl75WvCBdB0CbacudrY9fyRmrO3xyBeN6D9bPrOTtjC2yZcQPiVhRsJ44XhHnbS+0PsbWCr8oc4hzz9OBAiwlzoXB4ID/VfgO6DdteYX1NbsprfvkCsY1gHUU5e4iBj7Z3wnE8b4iVhR5U1hX4d8S2n7iTlUrphC3sUwHPJlK/P+NSof2RmkAOtZLcMz6mi1U+nIr5QrmsSgj0SzhY/psa8sY4VkXGQrW2xNKQ159o7UGGyTk7a8DFVhPPFthLde7duR7oTQg7+eiKEvQUaB3s75PriAwGucKH0n2Cl9OwYUbUcj1VmrIvc76WH9qxSri3OOVHgpeAvJgb+KAj2VFA/2HLWMWynpum4n1ltb3yRWE3K0BJMKuGDyRAeLYQaUVIat3Atd5+lH6OFCU7cSbsgE6UAW6g6P8WfgO6LdtOW/N3UnhuYLQjbqLH03p6Qu7Tvfgq0W36ThLHLtrrI2KhYCRhfNiFx0IBNPwDqW55+M+LuiX7YC2zZZHWr/SbtknVxBPlf+MOJnuKfhyldWwZCJVfvmYgs5r0dKc8m/Qh2vG7lF1HcMxnbKvxWktrI9zta6DPQW0VkKDr8/y+K4gZzHfXBXBn+4Qf06UHKDSBkDWjUrcRZSrgweCzoNPcHl8oGR3HsIl4muoJbiX1sLHFzpop4QGoMlOjU6md70YpfLc7p5XT6EBn1xlwe4PCzfOmvjGKxvFkWGG8N9TUheN4By2RMQlx4lHThZYqzFVIg/yYcrLAt9yF2qxTuDrEDYyeOBuRsPxRdODOIYZ6QGlTx+SG8TP8zBx/XHpcCO+ueoCelrkH6XctPwnwYbP17C2RwLButJJi03EiACr9dr8X9BbC5FIJBKJRCKRyF/FL+M1QuKHiPcZAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAAaCAYAAADrCT9ZAAACsklEQVR4Xu2XOYsVQRSFr7viCg4ayICCqCBuYOQoIi6BkSsYi5gYiIGJCE5gIoI/QcbEQAQDQcENXHAZTMRIUBNRRNzFBfd7rFvzbh+reD39pp+DvA8OVJ1bXVvX0i3SYVgyQ/VJ9V61n2LDgpVstMhP1ShL/1JtczGwgPKVWKfqsvQI1THVAdX0gRJp8CZQfih5oRpjaQx4r4uBu6pF5A2KV6oTlsYywgyjoah9FmOuqVazaRxXfZBGHX2FaOCHFNtZWwzLXAn9SYHyE9lsxjQJD8bZQnpDIyy7zIOYOZL2GT+gFFckDIzplTChG8mPoJ8f2WwGOrHJ0o9V910sEt/2TPLfqDaTx2Cpn1edkVDHlmL4D7mJiCB+mk0DsVls5niuemvpxRIeTu1FLHXEtpPfrKMAe2+5pXNv+Tvlx6keuPwdST8HsJdvsJlitoRKplr+rKp7IFoE+xdlVzhvp3nNwNkQweTimSnOm6c64vJglRTr/qq64PKeHVKuH/JOShaU0BiX7Vc9JS+Ffw77FHn/9k6qJrl85Jzqkuq26h7FGO5bktzyShH3MHvXyWOwPbByPNwu11uFUnWgEDpdBpQ9lPDiNZbD71/v4dmjlsdybRXUN55Nhmc6x0FJl4PXxybxmg0jtr1QdZhiVUBdk9lkygwYXzooE7++PF9UV9kkcvVflBDDNTiBYlXItVPgkYSCDzlgxMH2cMDAQfKETcdo1WU2jZFSbsLLUqoe3+hn1XzzcQfi5ISfOj0juyXfED76X0q4P3Pg+xurpFW2Sr4ffzFW9U0aA4/i79kcqYZOSbjycP/i3sW3coolqj1sVuCm6habdYEBr2ezzaAP8a+qdpZK+autDnC+DMW1NiieSRj4vwDbBYdj28nt0zrBDbCMzXayho2a8T8yHTp0+I/5DV93sJiW03mzAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAZCAYAAAC2JufVAAABTElEQVR4Xu2VvS4FURSFt59INKLxAhqiFdFSeQMvoFEiUQhyC1Q6nUQiEo1HELVGg0R4Cg2JaPysdc8czqzsc4dkFJLzJSs3+zv7nNmZmdwxKxT+hlXkDJmq6knkFFn56vhmG3lCXpAlWWuVXeRDcl3rCNwjF0l9h1wmdat0kAPkBNlCBurLXUYsDKvQjapsAw4yr1K4sfxQR+JmpfbgK9KTTWseKj5WxfODyLu4FO132UD2LDQfV7+HtQ7/4iTnh8z3nnNZQ87FcfOO1N6BOU90sFzfj9GLaR3J+UgcjOmTtZ54zW/WzlD91tzjwg2PjksPepY6QvegsiIORPg34+3PwuZ1x6WHLEodoZtWaeHua/+vBuMnYyyp5yxsnkgcoVtO6v3KeeR8evca4eOLd4cZry93GbawdoXcIq/mv48LKgTumVFZKBQK/4VP1UxhXvjMZPIAAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAZCAYAAAChBHccAAAB10lEQVR4Xu2VPUgcURSFrxqIRUCEYKOChYWlfQoLLWwNphFiH/9QMAEL04mIP0EwIY1ZCJIUURCUFGIliWhpIYrERk0hQmKhKCLoubz71jcns47ZZCvng4/Ze+5l35uZnVmRlJSUfviCQ+MYPoflsAy2wt+RCUctXIdXcJl6/53P8ELcYmpHtJ3F90OrIhMiDZZ76qkuKEmbH4bvYCP1PDrDd04vzBplBSFp87dRIW5GjyFLljMtHBDPOEjiXzb/WuJnMhKfz8EuDo1ROMJhEkmb34GbcBVewgdBf95mmLcSnysL8CVl43CCsjuhi3RyaGjvYVB/tcyzQrVnUlxeyQ1jEb6yz7pxnc8LXaSbwxzUiZsftPqT1cyUuDy8S4yegJ68vgzyRhfp4dAoobpY3PyW1bl+89MSn4dk4LbcXIi80EV6OQQ/xPVKg+yRZd+sfmL1Xd82Ht34G/s8AweC3l+hi/RxCPbgKWXN4ubbgkzrp0GtnMBflHk+yM3GPXoC/BAn8ljc4mPcANVwl7JzeEaZXmV9C3mKxH1nTZB53sMhDo2PEn8R/+ALPIIHcN+Oh+L+GUPaxW3kpx2/R9tZNsTdpVlxc03Rdhb+J2ZyPXspKSkpKfeAazESeVrYgKSsAAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFcAAAAZCAYAAABEmrJwAAADO0lEQVR4Xu2YS+hNQRzHf8KCJOSZPJJXshCRUJ5F2VnYyIYFNvKWvBYohUIoeaUkYmFh47EihZJHQigprxR5v1+/r5m5/9/53jnnnkvuxnzq253fd2bOPJozM+eKJBKJRKLRLFQdVQ3y8UDVIdWCSokmVqveqD6oZlNeoK/qkuqn6izlNYpXqnWqHqoWqpGqK5kSTRwT19dbqtaUF5ileqr6ptpIeYWsF/dwq6uZEg40fsbEN1UXTAzGiqsfGEJxo+DxQFhElpbe7+nj5j7uVinhOK56YmIsvJcmLmStarvqoGqVuEaYthKfJHjtKJ5nYvBFdZG8fw36sULcmOZQXuC86hF5m6V6nIix+tmbQl4UTOh4NolrUt0ogLfXpzv7GL+W096vxRI2iC5sFIDXtxbo0y7yRnk/sJXiALz7bMZYKbUnFw/LayT4a0zackDiPjNG3FYTo7/qMZsFfGWDCFsAFpall/en+RhvXazvefNRBV6fDeIKh4nYnSmR/zDrnzBpy06J+zEmqu6SN0DcYVIPn8W1+1p1RFz7WJWBcBYsMh7o5P3lPi4z7kLQwCnyUBGnrY1jD7P+OZO2bBPnd+eMHCap7vk0JvaZySsLbjSTTTxCXB86+HiCj+dXSjjae3+Pj8uMu264MscB6x82acsOcT4fCkWECX7OGX8B+oBJB9hmEPN1s6P3w8IqM+5CmrGhfJf6Jzdvz90ncb+IoeJW7APOKAmuWYztK8aMNLZEC+7F8Gf4GAdjrO9581EFCr2IeLbyW4oD8G779Ggf/+ltIYCJDXssXudSp7Jhprj2lpLPY0I677YQ7rq418f6Du8HmzHKdGQ6xQF4wygOJ23gnZS/dGNi7YUdYIL5kCsCX1PoB+/x8Oxz8HbeMDFYJtlxdqU4AG8xmzHwKYtTMjBOXGUcJhZ4c028yXsWrFJ7xwyvX2/j5TFY9ZBNz3DVHTYL4H6djHi4+rGHGB9UFqxQ3DgCU6W6XiHYFlAhqE82+zetxOVdVl1XfZL4fo289+I+G1Eeh1MZtrBB9GOjgHAw4SqG348S72tYqfhvBXfa/dnsCsjDqsdXHcq3yWYnEolEIpFIJBL/B78ACAoDJvLrNPMAAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADUAAAAZCAYAAACRiGY9AAAB/klEQVR4Xu2WzUtUYRTGj5ooIkRgRODHyopoIYEtwpW6cCdIK0X3FkmJFEKtXLipTYs2QVuR9v4DfmzahZpYIn5V6kI3ooSR5+m8d3rv470zd2QmCN4fPIz3d86d1zPz3ntHJBAIlJsxzTBLx6FmUHNFc1nzQHMQ68jPB81vzbKmjmolZ0rzU2xB5GG8nCOq+2mMdSRTLdbb7I6r3PH1XEeZKTTUpOatpotq+ZjVbJN7JfZ+/4RCQ10EnIcPwue+8wy2fz6uschCqYeKttoL8i3O95Hv0CySi7ih2WGZhUJDrWqWNAuaU82lWMd52sTOGyV/1fnn5AG2Ntbxuan5Ti4zWOgRSwdqNd7xjHP56BTrGSGPOyj8O/IR3Zov7m8M9MOrFQ0WeswyhVti/S+54IEtg54n5BucnyDvEw22x4ViSfpUI3B9+FSK9X8m71Mh1jNOvsn5AfI+d8W+oXUuFEvSpwq+itVqPVfv3JznkkBP2t0v7VmFgaJr6J7Y+hcGCz1lqWxqjsj1iPX3ew5D8zX5S/OJ3DOxc5PAQN/IYTC+eWQi2ud4MDLYLmvkTjTH5HA+cttzuE3zADh+Qw7c0WywdLRrVlimgd9k+2JP/S33uiv208lnSOyfwbMCr/Px8h96NR9Zyt9vZlrsfd/HyzlesyBaWQQCgUAg8D9xBrOFezPiyYoyAAAAAElFTkSuQmCC>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGsAAAAZCAYAAAA2VdDGAAADaElEQVR4Xu2YSehPURTHDyE2QqYyhgWxUMqGkkgWFrJgY6dkiJCdSP0tFBZkWCArLEiGIuOCZCiFTCUpU2Sex3C+7r1/5513z+/d91e/UvdTp/853/Pu/b3zzn3v3fcnymQymUzm/2U523wtClayvWP7xDZH5QLD2C6x/WI7pXKSDWzf2F6yjVe5ZtON3PlapNa0g9wxD9gGqlxgItsdcsftVrlK9pK7aBgMW1BMt3KL7aSIb7CdFzGYQMWiR6s48JZtjYg/s60VcTPoRe6ihrpj5wlSa/rJNkXEOGaqiMEycscF5lF8riSsZnWl+KTQsCplrO9MLISLIp5E5bl6RLRm0qhZKTW1UHn8tIiGeEREa9NCtZp1lco/DKDh1ge9fYy/khNeD4S7WANtthYV7dm6a1ExVwsJWM1KrQk+njwa6AO8P93Hmq8U1yuxmmUVI/VVwpfsonJh30UcgH5dixE+sPXRoucxufdLXaz66tQUe5dB3+T9Mz7W3Ke4XgkGtbVZB4Uv2ULlwrBJ0UDHuysFbHD6Ke0J23ClpWLVV6emwyIOQD/m/Tc+1tykuF4JBi3UItnFSP2s8CUbyenh4sJ/9TfdivUbFrJhaJR+F9TB+u2UmvBohn+gcIQD+l3hx+a6RnG9EgxapEWyf0jqe4Qv2UxO7+Bj+FhlGuhyp5QCGoZGjdKJmlj11akJd6EG+jnv4zxjc2FXHdMrwaDFWiS7GKlbz/edVNTh46WqgR5WYSq4Q9F465smFau+OjUdF3EA+nbvW++sexTXK8GgJVpk3lN8Qmi3vT/Oxyk7J2uubVpsABoV3lFoWH+Rq4t1TnVqsnaDs7y/wseaf9oNLtUiM5PiE0Ibo+IZIgbYvcl31FYqz9XOax2VbiEbFUDD9KYjFatZIKUmNEqPHxvREOObUmtHlFZJT3ID1+uEBzl8cQfWeU2CFfdDxKEJg4UGoI0U8WWK7xBjvGAbqkXPa7a+WkygUbNSagof9Z2FhqfRFRGDp+S26gGcK8alLlLax/ac7RHbQ//3GbmPV0kXchPjwmIH84XciWuQ+8i2n9zxk4vpPwwilztN7l8++D5KoRNVP+5Wa6EBuBvx4kfdMPixzU9KTdCQO0Ru0VwoplvBYsP1PUru+CHFdCaTyWQymUwmk8lkmsFvKFFEvy+AQAYAAAAASUVORK5CYII=>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADUAAAAZCAYAAACRiGY9AAABhklEQVR4Xu2WvS9EQRTFb0KhV2iIQnxEVBIqHT2tTi86lX9AJdFK/AkUKolCo5SoFIJEfH9ExEcQGs7NzNhxvDfvzdonkcwvOdmZc+e+m7P7dt+KJBKJv6AT+mDToxl6ZzMC7Q9dvxJ0YNbQPanVsupleZPf9UezAT1LeOijhOsh5qATqb8/mnZoDbqV8NB6QzWJCbQi+f2zbBBtbBThBlUV6tW+hkKNQLtsWnqgczZDrEIddl1FqBlowq5DoZRRaJ+8XuiSvCCt0Ka3ryLUjbcuCqWMQQd2rYGuvFopeECjQ93TvkwoxQXz35BSLEF95DUy1CQ0RV7ZUINiPqEjLhSxDm2RdKBK18u1o1/EhJqXn9d3zym3z0IDue/QMHTo1erChcojFKoFmmaTuJD8fkUD6RkfDcY/HlEUhXqR/Lrr7eeCx4Pk9w9Ax2xahsT8q4liR8w9fGql622v/iTmlnB1fWbcQV3emXH53uOzCF1DZ2L69Vp6K/os0J7pZiORSCQSif/EJ9XjfvWGFbqXAAAAAElFTkSuQmCC>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGsAAAAZCAYAAAA2VdDGAAADvklEQVR4Xu2YWciOQRTHj30p6wXKGi7IGuWGkkiSC1HcKBdK3Lq0pbiQ5YIsZcmNrUi2yHpBspRC1iRli7LvO+f/zZzvO+95Zt533q+8peZXp3fO/8wzz5xnZp6Z5yXKZDKZTOb/YxjbK7Y/bJfYOpaG61nC9p7tM9scExP6s10m19ZpE9OsZftO7r5jTKyWoI/o6we22SYmpOa0jVydR2y9TEwYx3aXXL1dJlaReWzrlb+TXEMjlAZus51S/k22C8oHY8ldKww3vvCObYXyv7CtVH6t+MbWzJfbUcOD1qTm9JttovJRZ5LywQJy9QQ8+1BbUVDZXmC19sYXoOlVCH++8gFWD1arMJ6KbXUOaP+apeTuibeFYPMWrVJOy6l43ZSABn9gQEueqE8o3KjWrhlfgIalD7p4H7+ak14XkGisrVlWNDRl62RFw1wrRBhC7p54qILNOzUnlPHmsUDv6ctTvW/B6g7pSSwkd/FkpdkkBK3LTLXsoGJiP5QvQL9hxQAf2bpa0fOU3P7SWNAH7F1CNTmF9jLossWc9b7lIYX1isjorzM6tFCDWj+oypqNVEwMhxQLdOxdKeCA091oz9gGGC2VDuT2UbSrqSanw8oXoB/35bfet9yisF6WNWz72H6R21c0KYN1TpU1GHjo8nBRft0Qrid2jxh6wDBQdi9IBXvWFnITZZOJpeSEVzPKB0pqOKDfV+VQW9cprCeBDuDio0qL3Ujru1VZs4Gc3tz7KGOWWaDrk1IKGDAM1GAbaCQ2z2pywiq0QD/vy+hnqC2cqkN6MrbT1he0Hnu/b6diW9hULdBlFqaCFYqBj33TVMsRcv3Y4/1qcjqhfAH6Vl+O7VkPKKwHwWtPGhRkEORjFZtuqEFod3x5tPdTTk6xtjZbsQwYKNmjMGA9VCwFnHDt3rmYXD/kAFRNTrHT4ExfXuR9S/JpcDqFH55o8sE4w/sWaCONP035AKc3vUdhX7BtNfFaC6PH0AMlYMDsoaMckmNbpckfAnuVlpITBsrmNCqgwcc3pdWwopNA5VbKH+q1Y0oD0PDFLaz2mgYz7qfyZRD6KA1AG6T8K1Sc5TFesvWzoucNWzcrRnjMtspoMoCalJzko7610vA2uqp88JzcUV1AX3Fd6iStuxE2dlyEB4FfHE0tbcjF8GBxgvlKruMWxD6x7SdXf0JpuI7e5GJnyP29g++jFFpS5dfdMiuUQU5i9/wvHmaIlJygIXaI3KS5WBquB8/4BbnFgPp9S8OZTCaTyWQymUwmk6kFfwE+/1ze5S/lhwAAAABJRU5ErkJggg==>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD8AAAAZCAYAAACGqvb0AAACTElEQVR4Xu2WT0hVQRjFvwIjyIWBUFC0sBADI7chrqpNtKtNmwgStf+Kbdq5cGdLadNGiGjRqiBQClrkSty7aOkfkKQ00qBC+w4zX2/ueXPfnSfYxvnB4d05882bd+bNnXtFMpnMfuex6g6bJXxXXSPvjeqZ6rTqgOq8alrVExY14LZqW7Wjek59e8Ir1S9xE0J3i91RBsXVcvhZ74d6WagoZ1x1P2hfETf+v5Ea/ovEw39UjaheqEapr4pYUMxzg829IiX8uv+Mhf8gbrs3S5u47+OxX1W3yDuoOkoeM8BGClXhb0rtx8TCv5f6AKnYbXLRt4/4dowfqmNsepZVZ9hMoSo8DjkjFn5G9UjcGTIlrmYoLGgAbhNbAAQoC25sqU6Qt6LqIi8ZTHiPTc+qFP/VWPi3qrGgfVhc3aXAawQOR1sA6Hqxu45wARD8bNDXNJjwAZviTt6H5MXCx7AgVXxWTfhr7CAb1/2vIg4WAMGr6irBZBwS/GRD4uFbqA1SwvdL7SA1TkraWByKGHuKO5oFEw2zqXwizYurXfBtgMnhvfNtIyUA+vGCw/RJ47EIbvc4FgALtmswEZ7TVXRK/T/f4b3LgQfg/SEPt9ahoL2hmgzaBk7tsvBhcAMLwIdgEu3iJnrKHRF6xdXy8xQensPGE+/h4DPwqsu7Aa/DXAc2fR+zJnEffFMdZ7OM1+LepJZUi/4TJzseVzHw5XgUWS3aBoJj3G+pBWwN+o051VXyLoirx1iExvW5QoUDO6Zqe4+xkclkMplMZv/wF7rgnGPF+uDgAAAAAElFTkSuQmCC>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAA2UlEQVR4Xu2UPw4BQRjF5xCO4hJKWh2J+BNCouEAKvdQkBCFRqEQ4gpqGnEDDe/LzibjmdmZYiUk80t+WXmveMl+skpF/pEhbHGYFzP4gE9t+73+Dj8z1OWAKHLgwjc0UMmrtlGGOw5d+IaEEVxSVoF7yjKRoQ6HFsZwpX/LyMHogpAh3x1SZOwIT1yEIEM9Dh3U4RluuAhBhvocWpCR9CZNuDa6IGRI/llZ1NTn4WUsvZmXgkqGplwYVOGWQ00DLjg0mcM7vMKLft5U8lliJhwQJQ4ikUg+vAC9piwlvwvjEwAAAABJRU5ErkJggg==>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEIAAAAZCAYAAACFHfjcAAACaklEQVR4Xu2XTahNURiGP4SBicRIGYiIUGZEHZQiRZG/TMwkAxTlpwy4ZeAnSpKBlIkYUFKMUEoSMZGiJAYKMTFQft63tdb17fdsZ61zOnegs596One/37f3Xnu1ztnrmjU0NDSUsQB+hr/hIzixWi5iD7wK58Tj2fAK3D3cEXgH18AJcArcAX9UOsI4rsfaNrgFboaboiMCb3bWHXPwHMhCl5VwzMJ53meVjoD20HGVjva697Hr6yvpBrksxxELE3oZHoZjquVheN1T8DScJ7XEL7jIwuqaAadHux1TV7y39hv0MhF8+GUa1pC77mh4UkPwxcLXSZmvgbBTg1IOWhjsai1kOGT9mYg69sNdGkZewcUaRu7BtRqWsM7CQM9ooYADcMjC+Zfi54VKR4D5V/jQwkN8q5bbGGv5yXsNW5Ldh+slK+IEvAZ/whVSK2EvvCMZH+BoTebhktfM8wZu17AG9qUV+QBudLWemGphYLe00AMlvzV8a7FnqRYiufM9nIwncKsWeqXkAZRRGlhYXbnrtCz0nJecpFd5KU8tTMZKLZTAwV6ULE3EEsk7wX5uyjTzD8LXoj4YN1fMuA9R9PxOcBI2xL9fwOWuloU/JnU3S5nfC6yCc92xwv59NZm/Nv/+4I7J8ZhPk5zo+f/CT0KCk9GSrCO80Xh3zPcys9su47LPDeq7hS1zomWhf5bLOPE33DFhz0vJErl7Eu40uarqeG5drOpJ9nfJfoqf5yodgZvwrYZC+n8lyd2gws0Sax/jp34tPazrClJaGgj61uoLI7bP/9/ILdOB4C6crOEgMlODhoaGhkHgDw3hpxLK1LAuAAAAAElFTkSuQmCC>