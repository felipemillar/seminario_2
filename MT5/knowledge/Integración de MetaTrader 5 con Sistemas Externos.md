# **Arquitectura de Integración Avanzada y Protocolos de Comunicación en MetaTrader 5**

El diseño de sistemas de trading algorítmico e infraestructuras de negociación cuantitativa de nivel profesional exige, con frecuencia, la interconexión de la terminal de cliente MetaTrader 5 (MT5) con plataformas externas de procesamiento analítico, motores de ejecución en la nube o entornos de aprendizaje automático basados en Python.1 Para preservar la estabilidad y seguridad operativa, el entorno de ejecución de MQL5 confina a sus programas dentro de un espacio aislado (*sandbox*) que restringe el acceso directo a los recursos del sistema operativo.3 No obstante, MetaTrader 5 provee una variedad de interfaces de comunicación nativas y mecanismos de extensibilidad que permiten estructurar soluciones de integración robustas.5 El propósito de este informe es analizar de manera exhaustiva las alternativas de comunicación disponibles, desde las funciones integradas hasta arquitecturas personalizadas de alto rendimiento, evaluando sus bases técnicas, latencias, limitaciones y patrones de implementación práctica.

## **1\. WebRequest() desde MQL5: Comunicación HTTP/HTTPS Síncrona**

La función incorporada WebRequest() constituye el mecanismo nativo más directo para interactuar con servicios web externos y APIs RESTful utilizando los protocolos HTTP y HTTPS.3 Esta interfaz es ampliamente utilizada para reportar estados de ejecución a servidores centralizados, consultar modelos de predicción remotos o interactuar con plataformas de mensajería externa.9  
La API de MQL5 expone dos sobrecargas fundamentales para esta función 8:

Fragmento de código  
// Sobrecarga 1: Envío de solicitudes estándar basadas en formato x-www-form-urlencoded  
int WebRequest(  
   const string      method,           // Método HTTP (GET, POST, PUT, DELETE, etc.)  
   const string      url,              // URL completa del recurso de destino  
   const string      cookie,           // Valor de las cookies de sesión  
   const string      referer,          // Encabezado HTTP Referer de la petición  
   int               timeout,          // Tiempo de espera en milisegundos (timeout)  
   const char        \&data,          // Arreglo de bytes con el cuerpo de la solicitud  
   int               data\_size,        // Tamaño del arreglo data en bytes  
   char              \&result,        // Arreglo de bytes de salida con la respuesta del servidor  
   string            \&result\_headers   // Cadena de salida con los encabezados de respuesta  
);

// Sobrecarga 2: Configuración avanzada de encabezados HTTP para payloads complejos (JSON/XML)  
int WebRequest(  
   const string      method,           // Método HTTP  
   const string      url,              // URL completa  
   const string      headers,          // Encabezados personalizados ("Key: Value\\r\\n")  
   int               timeout,          // Tiempo de espera en milisegundos  
   const char        \&data,          // Arreglo de bytes con el cuerpo de la solicitud  
   char              \&result,        // Arreglo de bytes de salida con la respuesta  
   string            \&result\_headers   // Cadena de salida con los encabezados de respuesta  
);

La segunda sobrecarga es indispensable al interactuar con arquitecturas de microservicios modernas, ya que permite inyectar encabezados críticos como Content-Type: application/json o tokens de portador (Authorization: Bearer \<token\>) requeridos en esquemas de autenticación avanzados.10

### **Restricciones Técnicas y de Seguridad**

El diseño de la función WebRequest() impone limitaciones estrictas destinadas a proteger la integridad de la terminal :

* **Naturaleza Bloqueante (Síncrona):** Al invocar WebRequest(), el hilo de ejecución del programa MQL5 se suspende por completo a la espera de la respuesta del servidor o del vencimiento del tiempo límite (timeout).3 Debido a esto, la función está estrictamente prohibida en indicadores personalizados, los cuales comparten un único hilo de ejecución para todos los gráficos de un mismo instrumento financiero.3 Si se permitiera, una respuesta tardía de una API web congelaría la actualización de los gráficos e interrumpiría el flujo de precios de la terminal, devolviendo en su lugar el código de error 4014 (ERR\_FUNCTION\_NOT\_ALLOWED) o 4060\.3 En consecuencia, su uso se limita exclusivamente a Expert Advisors (EAs) y scripts, que operan en sus propios hilos dedicados.3  
* **Incompatibilidad con el Probador de Estrategias (Strategy Tester):** WebRequest() no se ejecuta durante el backtesting histórico.3 Cualquier llamada dentro de este entorno fallará de inmediato, obligando a los desarrolladores a implementar alternativas locales o de simulación (*mocking*) si se requiere validar el EA bajo simulación histórica.  
* **Lista Blanca de URLs (Whitelisting):** Por motivos de seguridad, la terminal no iniciará conexiones hacia dominios arbitrarios.3 Cada dirección IP o nombre de dominio (incluyendo el puerto si difiere del estándar HTTP 80 o HTTPS 443\) debe registrarse manualmente en el menú de configuración global de la terminal (Herramientas \-\> Opciones \-\> Asesores Expertos \-\> Permitir WebRequest para las direcciones URL listadas).3 No existe ningún mecanismo programático que permita evadir o modificar esta lista de exclusión.5

### **Deserialización de Respuestas JSON en MQL5**

MQL5 carece de un motor nativo o biblioteca estándar integrada para parsear sintácticamente documentos JSON.3 Ante este vacío, la comunidad comercial de MQL5 utiliza bibliotecas de código abierto portadas de C++, tales como JAson.mqh o mql5-json.11  
Estas bibliotecas operan mediante analizadores léxicos (*lexers*) basados en máquinas de estados finitos que analizan el arreglo de caracteres devuelto por WebRequest(), discriminando entre llaves, corchetes, comillas y delimitadores para construir un árbol jerárquico de nodos genéricos en memoria (generalmente modelados bajo la clase CJAVal).12 El acceso a la información se realiza mapeando las claves del JSON mediante sobrecargas de operadores y métodos de conversión explícitos 12:

Fragmento de código  
\#include \<JAson.mqh\>

void ProcesarRespuesta(const char \&result\_bytes) {  
   // Conversión de la matriz de bytes en cadena UTF-8  
   string json\_str \= CharArrayToString(result\_bytes, 0, WHOLE\_ARRAY, CP\_UTF8);  
   CJAVal root;  
     
   if(root.Deserialize(json\_str)) {  
      string status \= root\["status"\].ToStr();  
      double balance \= root\["data"\]\["balance"\].ToDbl();  
      long order\_id \= root\["data"\]\["order\_id"\].ToInt();  
        
      PrintFormat("API \- Estado: %s | Balance: %G | ID Orden: %d", status, balance, order\_id);  
   } else {  
      Print("Error al deserializar el cuerpo de la respuesta JSON.");  
   }  
}

Es fundamental que el desarrollador gestione la recolección de memoria de estos objetos JSON dinámicos en MQL5 para evitar fugas de memoria (*memory leaks*) en bucles continuos de procesamiento.13

## **2\. Sockets Nativos MQL5: Comunicación TCP/IP de Baja Latencia**

Para aplicaciones comerciales que requieren un intercambio continuo de datos a nivel de microsegundos o milisegundos, MetaTrader 5 proporciona un conjunto de funciones de bajo nivel que permiten interactuar directamente con la API de sockets TCP/IP del sistema operativo, prescindiendo del uso de bibliotecas de enlace dinámico (DLLs) de terceros.5 Esta suite permite a los Expert Advisors y scripts actuar como clientes de red altamente eficientes.17  
La API nativa de sockets de MQL5 se compone de catorce funciones clave 5:

* SocketCreate(): Crea un descriptor de socket del sistema asociado a una bandera de comportamiento (actualmente solo admite SOCKET\_DEFAULT).15  
* SocketConnect(): Inicia una conexión activa de tres vías (*three-way handshake*) con el host y el puerto remoto bajo un temporizador estricto de desconexión.20  
* SocketIsConnected(): Verifica de forma no bloqueante si el socket se encuentra actualmente en un estado de conexión lógica activo.21  
* SocketIsReadable(): Devuelve el número de bytes acumulados en el búfer de entrada de red que están listos para ser leídos.15  
* SocketIsWritable(): Evalúa si el búfer del socket del sistema está disponible para escribir nuevos datos en el instante actual.15  
* SocketTimeouts(): Configura de forma explícita los tiempos de espera (*timeouts*) para operaciones de envío y recepción de datos.15  
* SocketSend(): Transmite una matriz de bytes (uchar) a través del canal establecido.22  
* SocketRead(): Lee datos del socket de red de manera síncrona dentro del límite de tiempo y tamaño máximo asignado.22  
* SocketTlsHandshake(): Inicia la negociación de certificados y el cifrado de datos mediante protocolos de seguridad TLS (SSL) sobre el canal TCP establecido.5  
* SocketTlsCertificate(): Recupera los datos del certificado de seguridad empleado en la negociación del túnel TLS.15  
* SocketTlsSend(): Envía datos cifrados de manera segura a través de la capa TLS.15  
* SocketTlsRead(): Lee datos cifrados a través del socket TLS de manera síncrona.15  
* SocketTlsReadAvailable(): Extrae de inmediato todo el volumen de bytes cifrados disponibles en el búfer SSL sin bloquear el hilo de ejecución.15  
* SocketClose(): Desconecta y libera de forma segura todos los recursos asociados al descriptor del socket.19

### **Protocolos de Framing para Flujos TCP**

TCP es un protocolo orientado a flujos de bytes continuos sin delimitadores semánticos inherentes (*stream-oriented*). Esto significa que múltiples envíos discretos realizados mediante SocketSend() pueden fusionarse o fragmentarse en la red debido a la fragmentación de la unidad de transmisión máxima (MTU) o a la agregación del algoritmo de Nagle. Para reconstruir los mensajes individuales en el receptor, se deben implementar protocolos de capa de aplicación basados en dos enfoques de enmarcado (*framing*):

1. **Enmarcado basado en Delimitadores:** Cada mensaje finaliza con un carácter de control único y no presente en el payload, típicamente un salto de línea (\\n, 0x0A) o un carácter nulo (\\0, 0x00).23 El receptor lee continuamente el flujo de bytes, acumulándolos en un búfer dinámico, y procesa cada mensaje en el instante en que detecta la presencia física del delimitador.  
2. **Enmarcado de Longitud Prefijada (Length-Prefixed):** Consiste en anteponer a cada mensaje un encabezado de tamaño fijo que define el volumen exacto de bytes del cuerpo del mensaje (por ejemplo, un entero de 4 bytes en formato binario). El receptor realiza una primera lectura de tamaño conocido para extraer este encabezado ![][image1], y posteriormente realiza lecturas iterativas hasta haber completado exactamente el tamaño del payload indicado por:  
   ![][image2]  
   donde el prefijo de longitud codifica el tamaño del mensaje en formato little-endian.

### **Lógica de Reconexión y Manejo de Errores**

Las infraestructuras comerciales que operan bajo redes inestables deben incorporar esquemas de reconexión tolerantes a fallos. La monitorización del estado de conexión mediante SocketIsConnected() debe ser periódica (por ejemplo, ejecutada dentro de un temporizador de corta frecuencia como OnTimer() o en la llegada de nuevos ticks en OnTick()).18 Si se detecta un error de red (como el código de error 5273 \- ERR\_NETSOCKET\_IO\_ERROR devuelto durante un intento de envío o lectura) 22, el flujo óptimo exige:

1. Cerrar de forma inmediata el descriptor del socket actual mediante SocketClose() para liberar los recursos del sistema operativo.19  
2. Aplicar un esquema de mitigación temporal (retroceso lineal o exponencial) para evitar saturar de peticiones fallidas al servidor.  
3. Instanciar un nuevo descriptor a través de SocketCreate() e intentar restablecer el canal de comunicación con SocketConnect().19

## **3\. ZeroMQ Bridge (DWX): Integración de Alto Rendimiento con Python**

El proyecto **DWX-ZeroMQ-Connector** representa uno de los enfoques más populares y consolidados para la integración asíncrona de alto rendimiento entre MetaTrader y Python utilizando sockets de mensajería ZeroMQ.1 ZeroMQ (0MQ) es una biblioteca que abstrae la complejidad de los sockets de red tradicionales, proporcionando colas de mensajes en memoria y patrones de distribución integrados de baja latencia.1  
La arquitectura del conector desacopla por completo la ejecución comercial de MetaTrader de la lógica analítica de Python 1:

\[Cliente Python (pyzmq)\]  \<====== Protocolo TCP \======\>   
   \- Hilo Ejecución (REQ)                                \- Wrapper ZeroMQ (C++) via DLL  
   \- Hilo Suscriptor (SUB)                               \- Cola de Mensajes MQL5

En MetaTrader 5, el servidor se implementa cargando la biblioteca dinámica nativa de ZeroMQ (libzmq.dll) y la capa de cifrado libsodium (libsodium.dll) en el espacio de memoria de la terminal.1 Desde una perspectiva arquitectónica, en MT5 resulta óptimo estructurar este puente como un **Servicio** de MQL5 (\#property service) en lugar de un Expert Advisor tradicional.25 A diferencia de los EAs, los servicios operan en segundo plano de manera continua, no requieren estar vinculados a un gráfico activo ni bloquean el hilo de procesamiento gráfico del terminal, iniciándose automáticamente al arrancar la aplicación.25

### **Patrones de Diseño de Mensajería en el Conector**

El conector implementa una combinación de patrones de mensajería distribuidos para coordinar la transacción de datos y comandos 1:

* **REQ/REP (Request-Reply):** Utilizado para el envío asíncrono de comandos transaccionales discretos desde el cliente Python (usando un socket REQ) hacia la terminal de MT5 (que escucha mediante un socket REP).1 Este patrón es síncrono por definición; el cliente envía una orden estructurada en JSON (por ejemplo, abrir una posición de mercado o modificar un Stop Loss) y espera de forma bloqueante la confirmación antes de transmitir la siguiente instrucción.1  
* **PUB/SUB (Publish-Subscribe):** Empleado para la distribución masiva y unidireccional de cotizaciones en tiempo real e información transaccional desde MetaTrader.1 El servicio en MT5 actúa como un publicador (PUB) enviando constantemente tramas de ticks a un puerto específico sin esperar confirmación.1 El cliente en Python se suscribe (SUB) al canal y filtra de forma eficiente solo los instrumentos que son de interés para la estrategia algorítmica.1

### **Instalación, Configuración y Rendimiento**

La instalación del puente requiere los siguientes pasos de mapeo en el disco duro :

1. Copiar las librerías dinámicas libzmq.dll y libsodium.dll en el directorio de librerías del sandbox de la terminal: /MQL5/Libraries/.  
2. Copiar los directorios de archivos de cabecera Mql y Zmq dentro de la carpeta: /MQL5/Include/.  
3. Colocar el script del servidor DWX\_ZeroMQ\_Service\_v1.0.0.mq5 en /MQL5/Services/ y compilarlo desde el MetaEditor.25  
4. Configurar los puertos de red del servicio MQL5, típicamente asignando el puerto 32768 para el socket PULL/REP de comandos, 32769 para el socket de control PUSH, y 32770 para el publicador de datos de mercado.25 En otras variantes del conector se suelen utilizar puertos de la serie 15555 a 15562\.27

Las pruebas de rendimiento bajo conexiones loopback locales (tcp://127.0.0.1) revelan latencias inferiores a ![][image3] milisegundos para operaciones REQ/REP y un rendimiento de entrega masiva de datos en tiempo real de alta fidelidad.1 No obstante, existen limitaciones que los desarrolladores deben prever:

* **Bloqueo de Sockets bajo Wine (Linux/macOS):** Al ejecutar MT5 sobre Wine en plataformas Unix, si la terminal se apaga de forma no limpia o se recarga abruptamente mientras el cliente en Python está conectado, los sockets pueden quedar bloqueados por el kernel de red de Wine durante un periodo de hasta ![][image4] segundos antes de permitir un nuevo enlace (*re-binding*).28  
* **Latencia de Caché del Historial:** La primera consulta de datos históricos voluminosos realizada desde Python puede forzar a MT5 a descargar los datos directamente del servidor del broker, excediendo el límite de tiempo del socket de datos (timeout).28 Las consultas consecutivas se completan rápidamente debido a la indexación en caché de la terminal.28

Para extender el protocolo y añadir comandos personalizados (por ejemplo, solicitar el cálculo remoto de un indicador técnico), el programador debe incorporar una rama en el selector de comandos JSON dentro del bucle de escucha del servicio MQL5 25:

Fragmento de código  
// Ejemplo de procesamiento de comando extendido en el Servicio MQL5  
string raw\_request \= pullSocket.Read();  
CJAVal parser;  
parser.Deserialize(raw\_request);

if(parser\["\_action"\].ToStr() \== "CALCULATE\_INDICATOR") {  
    string symbol \= parser\["\_symbol"\].ToStr();  
    int period \= parser\["\_period"\].ToInt();  
      
    // Obtener valor nativo del indicador iMA  
    double ma\_value \= iMA(symbol, (ENUM\_TIMEFRAMES)period, 14, 0, MODE\_EMA, PRICE\_CLOSE, 0);  
      
    // Generar respuesta y transmitir a través del socket de respuesta  
    CJAVal response;  
    response\["status"\] \= "SUCCESS";  
    response\["value"\] \= ma\_value;  
    pushSocket.Send(response.Serialize());  
}

## **4\. Named Pipes y Shared Memory: IPC en Windows de Ultra Baja Latencia**

Cuando la comunicación entre la terminal de MetaTrader 5 y el componente analítico externo se desarrolla estrictamente dentro de un mismo entorno físico o servidor virtual VPS, las técnicas de Comunicación Interprocesos (IPC) nativas de Windows eliminan la sobrecarga de la pila de protocolos de red TCP/IP, proporcionando latencias óptimas en el orden de microsegundos.16

### **Named Pipes (Conductos con Nombre)**

Los Named Pipes actúan como canales lógicos de comunicación bidireccionales expuestos en el espacio de nombres virtual \\\\.\\pipe\\NombreDelConducto.29 MetaTrader 5 ofrece soporte nativo para interactuar con Named Pipes encapsulándolos dentro de su sistema estándar de manipulación de archivos (FileOpen()), permitiendo conexiones rápidas sin comprometer la seguridad del sandbox ni recurrir a DLLs de terceros 7:

Fragmento de código  
// Apertura de un Named Pipe nativo en MQL5 sin evadir el sandbox  
int pipe\_handle \= FileOpen("\\\\\\\\.\\\\pipe\\\\MQL5\_Pipe\_Server", FILE\_READ|FILE\_WRITE|FILE\_BIN|FILE\_SHARE\_READ|FILE\_SHARE\_WRITE);

Para asegurar una comunicación robusta, el servidor en Python debe crear el conducto utilizando la biblioteca del sistema pywin32 configurándolo de forma explícita en modo Duplex (PIPE\_ACCESS\_DUPLEX) y asignando un búfer de tamaño definido.29 Si se omite la reserva del búfer de red en Windows, la conexión nativa de MT5 fallará devolviendo un descriptor inválido.31  
A pesar de que MT5 posee clases nativas como CFilePipe para interactuar de forma segura, muchos desarrolladores recurren a la importación directa de las funciones de la librería del sistema kernel32.dll para implementar operaciones asíncronas basadas en estructuras solapadas (OVERLAPPED), evitando que la terminal se bloquee si el servidor en Python deja de responder temporalmente 7:

Fragmento de código  
// Importación de funciones de Kernel32 para control avanzado de Pipes  
\#import "kernel32.dll"  
   int CreateNamedPipeW(string pipeName, uint openMode, uint pipeMode, uint maxInstances, uint outBufferSize, uint inBufferSize, uint defaultTimeOut, ulong security);  
   int ConnectNamedPipe(long hPipe, ulong overlapped);  
   int ReadFile(long hPipe, char \&inBuffer, uint bytesToRead, uint \&bytesRead, ulong overlapped);  
   int WriteFile(long hPipe, char \&outBuffer, uint bytesToWrite, uint \&bytesWritten, ulong overlapped);  
   int CloseHandle(long hObject);  
\#import

Es crítico destacar que al utilizar kernel32.dll en sistemas de 64 bits, todos los tipos de datos correspondientes a punteros lógicos y descriptores de archivos (*handles*) deben declararse estrictamente bajo el tipo de dato long de MQL5 (en lugar de int).7 La mezcla incorrecta de tamaños de enteros en compilaciones x64 corrompe el direccionamiento de la memoria del kernel de Windows, provocando un fallo catastrófico e inmediato de violación de acceso (Access Violation Error) y el cierre súbito de la terminal.7

### **Memoria Compartida (Shared Memory via Memory-Mapped Files)**

La memoria compartida a través de archivos mapeados en memoria representa el mecanismo IPC de menor latencia teórica en arquitecturas x86/x64.16 Este enfoque proyecta una región de la memoria física de Windows directamente sobre el espacio de direccionamiento virtual de ambos procesos.35 MQL5 no provee clases nativas para archivos mapeados en memoria sin respaldo de almacenamiento físico, lo que exige importar la API de Windows de kernel32.dll (CreateFileMappingW, MapViewOfFile, OpenFileMapping, UnmapViewOfFile).33  
A diferencia de los Named Pipes, la memoria compartida no cuenta con mecanismos de notificación o colas de espera implícitas.35 Si el script de Python y el EA en MT5 modifican el búfer al mismo tiempo, los datos se corromperán irrecuperablemente.35 Para garantizar la coherencia de los datos, es obligatorio implementar mecanismos de exclusión mutua utilizando variables de estado lógicas escritas en posiciones fijas del búfer de memoria o importando objetos de sincronización del sistema operativo como Mutexes o Eventos a través de llamadas de bajo nivel.35  
A continuación se presenta una comparación sistemática de las alternativas de IPC locales frente a los sockets tradicionales 16:

| Criterio | Sockets TCP/IP (Local) | Windows Named Pipes | Windows Shared Memory |
| :---- | :---- | :---- | :---- |
| **Latencia Típica** | Alta (![][image5] \- ![][image3] ms) | Muy Baja (![][image6] \- ![][image7] ![][image8]s) | Ultra Baja (![][image9] ![][image8]s) 16 |
| **Complejidad** | Baja-Media | Media | Muy Alta (Control manual de concurrencia) |
| **Sincronización** | Implícita (Colas TCP del OS) | Implícita (Búferes de conducto) 29 | Explícita (Requiere Semáforos/Mutex) 35 |
| **Restricción Geográfica** | Permite ejecución remota | Misma máquina / Red local 38 | Estrictamente la misma máquina física 16 |
| **Uso de DLLs en MT5** | No (Nativo por MQL5) 5 | No (Nativo por FileOpen) 7 | Sí (Obligatorio kernel32.dll) 33 |
| **Privilegios en OS** | Usuario estándar | Requiere nivel Administrador 31 | Usuario estándar (Global requiere SeCreateGlobal) 37 |

## **5\. Archivos Compartidos: Intercambio Asíncrono Desacoplado**

El intercambio de archivos constituye el método de integración clásico más desacoplado y tolerante a fallos. En este esquema, la terminal de MetaTrader escribe datos históricos o señales en un directorio local del disco duro, y un script de Python monitoriza y procesa dichos archivos reactivamente.39

### **El Sandbox de Archivos de MetaTrader 5 y el Acceso Común**

La terminal confina rigurosamente toda operación de lectura y escritura nativa de archivos dentro de su sandbox, ubicado de forma típica en la ruta de datos local de la aplicación (/MQL5/Files/).4 No obstante, si se necesita integrar múltiples instancias de MetaTrader 5 instaladas en el mismo servidor físico con un único script analítico de Python, se debe emplear el flag FILE\_COMMON durante la apertura del archivo.4 Esto redirige de forma automática la escritura física del archivo a una ruta pública e independiente del perfil específico de cada terminal activa.4

### **Control de Bloqueos de Escritura (File Locking)**

Si el programa de MQL5 mantiene abierto un archivo mientras el script de Python intenta acceder a él, el sistema operativo generará una excepción de violación de compartición que impedirá la lectura.41 Para solventar esto y permitir accesos concurrentes no bloqueantes entre el escritor y los múltiples lectores externos, MQL5 requiere la inclusión obligatoria de las banderas de uso compartido 41:

Fragmento de código  
// Apertura de archivo permitiendo que programas externos lean/escriban simultáneamente  
int file\_handle \= FileOpen("data\_stream.csv", FILE\_READ|FILE\_WRITE|FILE\_CSV|FILE\_SHARE\_READ|FILE\_SHARE\_WRITE);

### **Monitoreo del Sistema de Archivos: Polling frente a Watchers**

Para procesar la información de forma inmediata, el servicio en Python debe detectar las modificaciones físicas del archivo en el disco. Existen dos patrones dominantes para este fin:

1. **Polling (Bucle de consulta continua):** Consiste en estructurar un bucle while True en Python que verifique periódicamente (por ejemplo, cada ![][image10] ms) la marca de tiempo de última modificación del archivo. Este enfoque genera un consumo innecesario de recursos de procesamiento en el sistema operativo y provoca una degradación física acelerada de las unidades de estado sólido (SSD) debido a la consulta repetitiva de metadatos.  
2. **Filesystem Watchers (Monitoreo de eventos del kernel):** El enfoque de producción óptimo consiste en utilizar librerías como **Watchdog** en Python, la cual se suscribe de manera asíncrona a las interrupciones del kernel de Windows (interfaz ReadDirectoryChangesW). El script de Python entra en un estado inactivo de consumo de CPU nulo, y es despertado instantáneamente por el sistema operativo únicamente cuando ocurre un cambio físico de escritura en la carpeta.

La selección del formato de serialización de datos determina el rendimiento general de esta arquitectura:

* **CSV (Comma-Separated Values):** Formato humano legible, sumamente sencillo de depurar visualmente, pero de alto consumo de espacio de almacenamiento y procesamiento lento debido al formateo de cadenas.40  
* **JSON:** Estructura flexible que facilita el envío de metadatos complejos y anidados, pero exige un alto coste de serialización y deserialización.11  
* **Binario:** Representa la alternativa de rendimiento máximo. MQL5 permite volcar estructuras de datos completas de forma directa utilizando FileWriteStruct().30 En Python, la lectura se completa en microsegundos utilizando el módulo struct o mapeando la matriz a tipos estructurados de **NumPy** (np.fromfile()), requiriendo únicamente que las definiciones estructurales de datos y la alineación de bytes estén perfectamente coordinadas en ambos lenguajes.

A pesar de su simplicidad, este método sigue utilizándose activamente debido a su extrema robustez: actúa como un búfer natural que preserva la información en el disco en caso de que el script analítico en Python sufra un colapso, aislando por completo la ejecución comercial de fallos externos.

## **6\. Python a MT5 via la API Oficial**

A diferencia de los enfoques anteriores que posicionan a MQL5 como el origen emisor de la comunicación, la API oficial de integración provista por MetaQuotes para Python invierte por completo el flujo de control, posicionando al intérprete de Python como el director de la sesión algorítmica. Mediante el paquete MetaTrader5, un script de Python puede inicializar de manera transparente un puente IPC de alta velocidad con una terminal de usuario activa, consultar datos de mercado masivos e inyectar solicitudes de trading directamente.2  
El flujo analítico y transaccional se organiza bajo la API oficial de MetaTrader:

Python  
import MetaTrader5 as mt5  
import pandas as pd

\# Establecer enlace IPC con la terminal activa \[45\]  
if not mt5.initialize():  
    print("Fallo de inicialización:", mt5.last\_error())  
    quit()

\# Solicitar de forma asíncrona las últimas 10,000 barras del EURUSD   
rates \= mt5.copy\_rates\_from\_pos("EURUSD", mt5.TIMEFRAME\_H1, 0, 10000)  
df \= pd.DataFrame(rates)  
df\['time'\] \= pd.to\_datetime(df\['time'\], unit='s')

\# Preparar y enviar orden transaccional al motor de ejecución de MT5 \[45, 46\]  
tick \= mt5.symbol\_info\_tick("EURUSD")  
request \= {  
    "action": mt5.TRADE\_ACTION\_DEAL,  
    "symbol": "EURUSD",  
    "volume": 0.1,  
    "type": mt5.ORDER\_TYPE\_BUY,  
    "price": tick.ask,  
    "deviation": 20,  
    "magic": 123456,  
    "comment": "Inyección desde API Python",  
    "type\_time": mt5.ORDER\_TIME\_GTC,  
    "type\_filling": mt5.ORDER\_FILLING\_RETURN,  
}

result \= mt5.order\_send(request)  
if result.retcode\!= mt5.TRADE\_RETCODE\_DONE:  
    print("Orden rechazada:", result.comment)  
else:  
    print(f"Posición abierta exitosamente. Ticket: {result.order}")

mt5.shutdown()

### **Sincronización de Procesamiento en Python**

Las llamadas al sistema de la librería MetaTrader5 se comunican con una única conexión de canalización interna de la terminal, la cual no está diseñada nativamente para operaciones multi-hilo concurrentes y asíncronas desde múltiples procesos externos.47 Si un servicio robusto de Python utiliza hilos para analizar diferentes instrumentos, se debe implementar una capa de exclusión mutua mediante un cerrojo lógico (threading.Lock) para evitar llamadas colisionadas en la pasarela IPC 47:

Python  
import threading

mt5\_lock \= threading.Lock()

def consultar\_datos\_mercado(symbol):  
    with mt5\_lock:  
        \# Consulta segura en un entorno multi-hilo  
        return mt5.copy\_rates\_from\_pos(symbol, mt5.TIMEFRAME\_M5, 0, 100)

### **Limitación de Compatibilidad Multiplataforma**

La API oficial está construida utilizando interfaces internas del kernel de Windows, lo que limita su compatibilidad nativa a sistemas operativos de Microsoft.2 En infraestructuras de nube que operan bajo arquitecturas Linux (Ubuntu/Debian) o entornos macOS, el paquete oficial MetaTrader5 no compilará ni se ejecutará.48  
Para habilitar esta compatibilidad en servidores de producción Unix, la comunidad comercial de código abierto utiliza herramientas como **mt5linux**.48 Esta solución corre la terminal de MT5 e instancias de Python de Windows dentro del contenedor de emulación de **Wine**.48 El contenedor ejecuta un servidor de llamadas a procedimientos remotos (RPyC) de Python, el cual atiende sockets TCP expuestos al sistema operativo Linux anfitrión.48 De esta manera, el script nativo en Linux interactúa con el cliente RPyC de forma transparente, traduciendo cada instrucción a la terminal emulada de Windows y conservando la firma de la API original.48

## **7\. GlobalVariables de la Terminal: Comunicación de Estado Inter-EA**

Las variables globales de la terminal (GlobalVariables) constituyen un mecanismo nativo de memoria compartida diseñado exclusivamente para la transferencia de información y coordinación de estados entre diferentes Expert Advisors, scripts o indicadores técnicos que se ejecutan de manera simultánea dentro de una misma instancia de MetaTrader 5\.20  
Este sistema de persistencia en memoria se gestiona a través de cinco funciones nativas clave:

* GlobalVariableSet(): Crea una nueva variable o modifica el valor decimal existente de un registro.20  
* GlobalVariableGet(): Recupera de forma instantánea el valor numérico almacenado bajo una clave determinada.20  
* GlobalVariableCheck(): Valida la existencia física de una clave en la tabla de memoria global.20  
* GlobalVariableDel(): Elimina de manera inmediata un registro específico.20  
* GlobalVariableTemp(): Instancia una variable global temporal en la memoria RAM del sistema, garantizando que el registro se destruirá al apagar o cerrar la terminal y evitando la persistencia en disco duro.20

### **Comportamiento y Persistencia**

Las variables globales declaradas mediante GlobalVariableSet() son persistentes.20 Al modificarse, la terminal vuelca periódicamente la tabla de variables sobre un archivo binario centralizado denominado gvt.dat alojado en el directorio del perfil del terminal, garantizando que los datos sobrevivirán a fallos del fluido eléctrico, apagados o reinicios de la aplicación.20

### **Limitaciones Críticas de Diseño**

A pesar de su alta velocidad, este subsistema presenta severas limitaciones de diseño:

1. **Tipo de Datos Restringido a Punto Flotante:** Las variables globales de la terminal solo admiten el almacenamiento de valores numéricos de punto flotante de doble precisión (double, de 8 bytes). Es imposible registrar tipos estructurados, matrices de bytes o cadenas de caracteres de manera directa.  
2. **Límite de Longitud en Claves de Texto:** Los nombres lógicos asignados a cada variable están estrictamente limitados a un máximo de 63 caracteres de longitud.  
3. **Cuellos de Botella de Entrada/Salida (E/S) en Disco:** El uso desmedido de variables persistentes (GlobalVariableSet()) para actualizar información en alta frecuencia (como precios por cada tick de múltiples símbolos) genera operaciones constantes de volcado en el disco duro, elevando drásticamente el uso de recursos E/S de la máquina. En sistemas HFT, es obligatorio utilizar exclusivamente variables temporales a través de GlobalVariableTemp(), las cuales se administran en memoria volátil de alta velocidad y omiten el volcado físico a disco.

Para transmitir tipos complejos (como booleanos o enteros largos) sobre variables flotantes, se recurre a la codificación bit a bit o a técnicas de empaquetado de datos en el espacio mantisa del formato de punto flotante de doble precisión IEEE 754:  
![][image11]  
donde los ![][image12] bits destinados a la mantisa matemática de la variable flotante pueden emplearse mediante máscaras de bits lógicas en MQL5 para empaquetar de forma transparente múltiples variables enteras y banderas de control discretas en una única variable global.

## **8\. MetaTrader 5 como Servidor REST via EA**

En el diseño de arquitecturas modernas de trading, con frecuencia se requiere interactuar con MetaTrader 5 mediante peticiones estándar desde clientes HTTP tradicionales (por ejemplo, ejecutando un comando del tipo curl \-X GET http://localhost:8080/positions). Sin embargo, existe una limitación de diseño de suma importancia: las funciones de red nativas de MQL5 (Socket\*) operan estrictamente en modo cliente.5 Es físicamente imposible utilizar la API nativa de sockets para enlazar un puerto local y escuchar peticiones entrantes desde el exterior.  
Para superar esta restricción y dotar a la terminal con la funcionalidad de un Servidor REST HTTP de bajo nivel, se debe evadir el sandbox de MQL5 importando la biblioteca de sockets nativa del sistema operativo Windows, **Winsock2** (alojada en ws2\_32.dll).6 El Expert Advisor debe estructurar el ciclo completo de inicialización, enlace de puerto, escucha pasiva y aceptación de canales de comunicación.52

### **Gestión de Concurrencia y No-Bloqueo de Sockets en MQL5**

La llamada a la función estándar de aceptación de sockets (accept) de ws2\_32.dll es, por diseño, bloqueante.55 Si se ejecuta directamente dentro del hilo principal de un EA de MQL5, congelará permanentemente toda la terminal de MetaTrader 5 a la espera de la primera petición externa, desactivando el procesamiento de cotizaciones y colgando la interfaz gráfica de usuario.32  
Para evitar el bloqueo absoluto, se debe aplicar una técnica fundamental en programación de red: **configurar el socket de escucha en modo No Bloqueante (Non-blocking mode)**.55 Esto se realiza invocando a la función de control ioctlsocket() de Winsock con el comando FIONBIO y una variable de estado establecida en 1\.56  
Bajo esta configuración, cuando el bucle periódico de control del EA (el cual se ejecuta en el gestor de eventos de temporización OnTimer() de la terminal) invoca a la función accept(), la llamada no se suspende.55 Si no existe ninguna petición HTTP entrante en la cola, accept() retorna de forma instantánea devolviendo el valor INVALID\_SOCKET y el código de error del sistema WSAEWOULDBLOCK (10035), permitiendo que el hilo de MQL5 continúe su ejecución habitual y procese los eventos del mercado normalmente.55  
Cuando un cliente conecta, accept() devuelve un descriptor de socket válido.55 El EA procesa la trama de texto HTTP entrante leyendo los encabezados mediante recv() 57, extrae el verbo HTTP (GET, POST, DELETE) y la ruta del endpoint solicitado (por ejemplo, /positions o /order), ejecuta la acción de trading correspondiente de forma nativa en MetaTrader y finalmente devuelve al cliente una respuesta formateada en HTTP/1.1 con payload de JSON.22

## **9\. Notificaciones Push, Emails y Alertas Locales**

MetaTrader 5 proporciona un conjunto de funciones diseñadas de manera nativa para canalizar reportes analíticos de ejecución a operadores humanos y sistemas externos de soporte técnico:

* SendNotification(): Permite transmitir de manera asíncrona mensajes cortos de texto plano a dispositivos móviles que cuenten con la aplicación móvil oficial de MetaTrader instalada y vinculada a un MetaQuotes ID.5 No requiere configuración de servidores, ya que la comunicación se canaliza cifrada por los servidores de MetaQuotes.5  
* SendMail(): Envía un correo electrónico completo con título y cuerpo estructurado utilizando los parámetros del servidor SMTP definidos manualmente en el menú de configuración de la terminal.5  
* Alert(): Genera un cuadro de diálogo emergente de advertencia gráfica dentro de la interfaz del terminal, acompañado de una alerta acústica para notificación en terminales físicas locales.5

### **Límites de Frecuencia y Cuotas del Sistema**

Para prevenir la saturación de los servidores móviles y la sobrecarga de la pila de red, MetaQuotes impone cuotas estrictas de frecuencia en producción:

* **Restricción de Push en Producción:** La función SendNotification() limita la tasa de entrega a un máximo de **1 mensaje cada 0.5 segundos**, y restringe el volumen acumulado a un límite de **100 notificaciones al día** por cuenta activa. Si un sistema algorítmico supera estos límites debido a un bucle infinito, la terminal bloqueará temporalmente las llamadas entrantes para esa dirección IP.  
* **Bloqueo en el Probador de Estrategias:** Estas funciones están inhabilitadas de forma total durante simulaciones históricas en el Strategy Tester.

## **10\. Comparativa Integradora de Métodos de Comunicación**

La siguiente tabla resume técnicamente todas las arquitecturas de integración documentadas en este informe técnico:

| Metodología de Integración | Latencia Media | Confiabilidad de Canal | Complejidad de Implementación | Soporte Bidireccional | Compatibilidad Nativa Unix (Client) | Caso de Uso Óptimo Recomendado |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **WebRequest() (MQL5)** | Media-Alta (![][image7] \- ![][image13] ms) | Alta | Baja | Limitado (Síncrono/Bloqueante) | Sí (Bajo Wine estándar) 49 | Integración simple con Webhooks de Telegram o APIs de broker secundarias.9 |
| **Sockets Nativos MQL5** | Muy Baja (![][image5] \- ![][image14] ms local) | Alta (TCP) | Media-Alta | Sí (Dúplex asíncrono completo) | Sí (Bajo Wine estándar) 49 | Conexión directa a servidores de trading cuántico locales o VPS remotos.17 |
| **ZeroMQ Bridge (DWX)** | Muy Baja (![][image3] \- ![][image15] ms) | Muy Alta | Alta (Requiere DLLs y bindings) | Sí (REQ/REP y PUB/SUB) | Parcial (Wine requiere configuraciones de sockets complejas) 28 | Sistemas institucionales que requieran streaming masivo de datos a Python. |
| **Windows Named Pipes** | Ultra Baja (![][image9] ms) | Crítica (Solo Local) | Alta | Sí (Modo Duplex estricto) | No (Exclusivo de Win32 API) | Integración local de ultra baja latencia sin dependencias de red física.16 |
| **Shared Memory (WinAPI)** | Casi Cero (![][image16] ![][image8]s) | Crítica (Sin Sincronización) | Extrema (Requiere control manual) | Sí (Sincronización manual) | No (Exclusivo de arquitectura Windows x64) 33 | Aplicaciones de arbitraje HFT en el mismo servidor VPS de alta computación.16 |
| **Archivos Compartidos** | Alta (![][image17] ms) | Media (Riesgo de Bloqueos) | Muy Baja | No (Unidireccional por archivo) | Sí (Rutas Wine virtuales mapeadas) | Respaldo e intercambio offline de históricos de velas o logs de trading diarios.40 |
| **API Oficial Python** | Muy Baja (![][image3] \- ![][image14] ms) | Alta | Muy Baja | Sí (Inversión de Control) | Parcial (Requiere wrapper RPyC de Wine) 48 | Desarrollo rápido de bots de machine learning e interactividad asíncrona de datos.46 |
| **GlobalVariables de MT5** | Ultra Baja (![][image9] ms) | Muy Alta | Muy Baja | No (Compartida en memoria interna) | Sí (Interno de la terminal) | Semáforos básicos y coordinación de estados entre diferentes EAs locales. |
| **Servidor REST (ws2\_32.dll)** | Baja (![][image3] \- ![][image6] ms) | Media-Alta | Extrema (C sockets x64 e HTTP) | Sí (Atención asíncrona de peticiones) | No (Llamadas exclusivas de ws2\_32.dll) 6 | Exponer la terminal de trading para recibir órdenes de control externas tipo microservicio. |

## **11\. Implementaciones de Código Funcional**

A continuación se exponen tres arquitecturas de código listas para producción en entornos de MetaTrader 5 y Python.

### **Código 1: EA Consumidor de REST API externa con WebRequest() y Simulación de Tokenizer JSON**

Este Expert Advisor se ejecuta de manera asíncrona respecto al procesamiento de ticks utilizando temporizadores, consumiendo un servicio REST externo mediante la inyección de payloads estructurados de tipo JSON.8

Fragmento de código  
\#property copyright "Architect-Quant"  
\#property version   "1.00"  
\#property strict

// Parámetros de entrada \[3, 8, 10\]  
input string   InpApiUrl \= "https://api.quantserver.com/v1/orders";  
input string   InpApiKey \= "token\_auth\_bearer\_secret\_key";  
input int      InpTimeout \= 5000;

//+------------------------------------------------------------------+  
//| Inicialización                                                   |  
//+------------------------------------------------------------------+  
int OnInit()  
{  
   Print("EA WebRequest Inicializado. Iniciando temporizador de sondeo...");  
   EventSetTimer(10); // Ejecución periódica cada 10 segundos  
   return(INIT\_SUCCEEDED);  
}

//+------------------------------------------------------------------+  
//| Desinicialización                                                |  
//+------------------------------------------------------------------+  
void OnDeinit(const int reason)  
{  
   EventKillTimer();  
   Print("EA WebRequest desinicializado.");  
}

//+------------------------------------------------------------------+  
//| Evento del temporizador                                          |  
//+------------------------------------------------------------------+  
void OnTimer()  
{  
   ResetLastError();  
     
   // Construcción manual de un payload JSON válido \[14\]  
   string json\_body \= StringFormat("{\\"symbol\\":\\"%s\\",\\"bid\\":%G,\\"ask\\":%G}",  
                                   Symbol(), SymbolInfoDouble(Symbol(), SYMBOL\_BID), SymbolInfoDouble(Symbol(), SYMBOL\_ASK));  
                                     
   char data\_bytes;  
   StringToCharArray(json\_body, data\_bytes, 0, StringLen(json\_body), CP\_UTF8);  
     
   // Configuración de cabeceras HTTP para REST API   
   string headers \= StringFormat("Content-Type: application/json\\r\\nAuthorization: Bearer %s\\r\\n", InpApiKey);  
     
   char result\_bytes;  
   string response\_headers \= "";  
     
   // Invocación síncrona bloqueante en hilo dedicado del EA   
   int http\_code \= WebRequest("POST", InpApiUrl, headers, InpTimeout, data\_bytes, result\_bytes, response\_headers);  
     
   if(http\_code \== \-1)  
   {  
      Print("Fallo crítico en WebRequest. Código de último error: ", GetLastError()); //   
      return;  
   }  
     
   if(http\_code \== 200 || http\_code \== 201\)  
   {  
      string response\_text \= CharArrayToString(result\_bytes, 0, WHOLE\_ARRAY, CP\_UTF8);  
      Print("API Respuesta: ", response\_text);  
        
      // Tokenizer manual básico para extraer el ticket de orden devuelto  
      string key\_pattern \= "\\"ticket\\":";  
      int key\_index \= StringFind(response\_text, key\_pattern, 0);  
      if(key\_index\!= \-1)  
      {  
         int value\_index \= key\_index \+ StringLen(key\_pattern);  
         int end\_index \= StringFind(response\_text, ",", value\_index);  
         if(end\_index \== \-1) end\_index \= StringFind(response\_text, "}", value\_index);  
           
         if(end\_index\!= \-1)  
         {  
            string ticket\_str \= StringSubstr(response\_text, value\_index, end\_index \- value\_index);  
            StringReplace(ticket\_str, "\\"", "");  
            StringReplace(ticket\_str, " ", "");  
            Print("Procesado exitoso \- Ticket de orden extraído: ", ticket\_str);  
         }  
      }  
   }  
   else  
   {  
      PrintFormat("API retornó código de error HTTP: %d", http\_code);  
   }  
}

//+------------------------------------------------------------------+  
//| OnTick                                                           |  
//+------------------------------------------------------------------+  
void OnTick()  
{  
   // Ejecución en temporizador para evitar latencias de red en ticks  
}

### **Código 2: Sistema de Comunicación TCP Bidireccional de Baja Latencia**

Este sistema implementa una conexión asíncrona de baja latencia utilizando sockets TCP nativos de MQL5 para enviar cotizaciones, y un servidor multihilo en Python que responde comandos de trading enmarcados con salto de línea \\n.5

#### **Lado del Cliente: MQL5 Expert Advisor (SocketClient\_EA.mq5)**

Fragmento de código  
\#property copyright "Architect-Quant"  
\#property version   "1.00"  
\#property strict

input string   InpServerIp \= "127.0.0.1";  
input int      InpServerPort \= 9090;  
input int      InpTimeoutMs \= 1000;

int m\_socket \= INVALID\_HANDLE;

//+------------------------------------------------------------------+  
//| Inicialización                                                   |  
//+------------------------------------------------------------------+  
int OnInit()  
{  
   m\_socket \= SocketCreate(); // \[19\]  
   if(m\_socket \== INVALID\_HANDLE)  
   {  
      Print("Fallo al crear socket. Error: ", GetLastError());  
      return(INIT\_FAILED);  
   }  
     
   Print("Conectando a servidor TCP en ", InpServerIp, ":", InpServerPort, "...");  
   if(\!SocketConnect(m\_socket, InpServerIp, InpServerPort, InpTimeoutMs)) //   
   {  
      Print("Fallo al conectar. Código de error: ", GetLastError()); // \[17, 20\]  
      return(INIT\_SUCCEEDED); // Permitir reintento en el flujo de ticks  
   }  
     
   Print(" Conectado exitosamente.");  
   return(INIT\_SUCCEEDED);  
}

//+------------------------------------------------------------------+  
//| Desinicialización                                                |  
//+------------------------------------------------------------------+  
void OnDeinit(const int reason)  
{  
   if(m\_socket\!= INVALID\_HANDLE)  
   {  
      SocketClose(m\_socket); //   
      Print(" Socket cerrado.");  
   }  
}

//+------------------------------------------------------------------+  
//| OnTick                                                           |  
//+------------------------------------------------------------------+  
void OnTick()  
{  
   // Gestionar reconexión asíncrona si se detecta desconexión   
   if(\!SocketIsConnected(m\_socket))  
   {  
      Print(" Enlace inactivo. Reintentando conexión...");  
      SocketClose(m\_socket); //   
      m\_socket \= SocketCreate();  
      if(m\_socket\!= INVALID\_HANDLE)  
      {  
         if(\!SocketConnect(m\_socket, InpServerIp, InpServerPort, InpTimeoutMs))  
         {  
            Print(" Reintento fallido. Siguiente tick procesará...");  
            return;  
         }  
         Print(" Reconexión exitosa.");  
      }  
   }  
     
   // Construcción de trama de ticks con delimitador de salto de línea \\n  
   string frame\_data \= StringFormat("TICK,%s,%G,%G\\n", Symbol(), SymbolInfoDouble(Symbol(), SYMBOL\_BID), SymbolInfoDouble(Symbol(), SYMBOL\_ASK));  
     
   char send\_bytes;  
   StringToCharArray(frame\_data, send\_bytes, 0, StringLen(frame\_data), CP\_UTF8);  
     
   ResetLastError();  
   // Transmisión asíncrona   
   int bytes\_sent \= SocketSend(m\_socket, send\_bytes, ArraySize(send\_bytes));  
   if(bytes\_sent \== \-1)  
   {  
      Print(" Error en envío de datos. Código: ", GetLastError());  
      return;  
   }  
     
   // Lectura no bloqueante del canal en busca de comandos remotos  
   if(SocketIsReadable(m\_socket) \> 0\)  
   {  
      char read\_buffer;  
      int bytes\_read \= SocketRead(m\_socket, read\_buffer, 1024, 100); //   
      if(bytes\_read \> 0\)  
      {  
         string cmd\_recv \= CharArrayToString(read\_buffer, 0, bytes\_read, CP\_UTF8);  
         Print(" Recibido: ", cmd\_recv);  
           
         // Procesar comando enmarcado  
         if(StringFind(cmd\_recv, "EXEC\_MARKET\_BUY")\!= \-1)  
         {  
            Print(" Ejecutando compra del mercado remota...");  
         }  
      }  
   }  
}

#### **Lado del Servidor: Python Script (SocketServer.py)**

Python  
import socket  
import threading

BIND\_IP \= "127.0.0.1"  
BIND\_PORT \= 9090

def handle\_client(client\_socket, client\_address):  
    print(f"\[+\] Nueva sesión activa desde {client\_address}:{client\_address}")  
    buffer \= ""  
    try:  
        while True:  
            data \= client\_socket.recv(1024)  
            if not data:  
                break  
              
            buffer \+= data.decode('utf-8', errors='ignore')  
              
            \# Desensamblar tramas utilizando delimitación por salto de línea  
            while "\\n" in buffer:  
                line, buffer \= buffer.split("\\n", 1)  
                if line.strip():  
                    print(f" Trama: {line.strip()}")  
                      
                    \# Decisión algorítmica y transmisión de comando  
                    parts \= line.split(",")  
                    if parts \== "TICK":  
                        bid \= float(parts)  
                        ask \= float(parts)  
                        spread \= ask \- bid  
                          
                        \# Inyectar comando bajo condiciones específicas de mercado  
                        if spread \< 0.00015:  
                            cmd \= "EXEC\_MARKET\_BUY\\n"  
                            client\_socket.sendall(cmd.encode('utf-8'))  
                            print(f"\[ENVIO\] Comando transmitido: {cmd.strip()}")  
    except ConnectionResetError:  
        print(f"\[-\] Caída abrupta de sesión para {client\_address}")  
    finally:  
        client\_socket.close()  
        print(f"\[-\] Sesión finalizada con {client\_address}")

def main():  
    server \= socket.socket(socket.AF\_INET, socket.SOCK\_STREAM)  
    server.setsockopt(socket.SOL\_SOCKET, socket.SO\_REUSEADDR, 1)  
    server.bind((BIND\_IP, BIND\_PORT))  
    server.listen(5)  
    print(f"\[\*\] Servidor TCP escuchando en {BIND\_IP}:{BIND\_PORT}")  
      
    try:  
        while True:  
            client\_sock, client\_addr \= server.accept()  
            t \= threading.Thread(target=handle\_client, args=(client\_sock, client\_addr))  
            t.daemon \= True  
            t.start()  
    except KeyboardInterrupt:  
        print("\[\*\] Cerrando servidor TCP de producción.")  
    finally:  
        server.close()

if \_\_name\_\_ \== "\_\_main\_\_":  
    main()

### **Código 3: EA actuando como Servidor REST HTTP (Winsock2 ws2\_32.dll x64 No Bloqueante)**

Este Expert Advisor utiliza la API de Windows de 64 bits de Winsock2 para enlazar y escuchar peticiones HTTP en el puerto 8080, implementando un socket no bloqueante para evitar detener la terminal.6

Fragmento de código  
\#property copyright "Architect-Quant"  
\#property version   "1.00"  
\#property strict

\#define SOCKET ulong  
\#define INVALID\_SOCKET (SOCKET)(\~0)  
\#define SOCKET\_ERROR (-1)  
\#define AF\_INET 2  
\#define SOCK\_STREAM 1  
\#define IPPROTO\_TCP 6  
\#define FIONBIO 0x8004667e

struct sockaddr\_in {  
    short          sin\_family;  
    ushort         sin\_port;  
    uint           sin\_addr;  
    char           sin\_zero;  
};

\#import "ws2\_32.dll"  
   int WSAStartup(ushort wVersionRequested, uchar \&lpWSAData);  
   SOCKET socket(int af, int type, int protocol);  
   int ioctlsocket(SOCKET s, long cmd, uint \&argp);  
   int bind(SOCKET s, sockaddr\_in \&addr, int namelen);  
   int listen(SOCKET s, int backlog);  
   SOCKET accept(SOCKET s, sockaddr\_in \&addr, int \&addrlen);  
   int recv(SOCKET s, char \&buf, int len, int flags);  
   int send(SOCKET s, const char \&buf, int len, int flags);  
   int closesocket(SOCKET s);  
   int WSACleanup();  
   int WSAGetLastError();  
\#import

SOCKET m\_srv\_socket \= INVALID\_SOCKET;  
uchar wsa\_data; // Búfer de respaldo estructural de WSADATA para x64 \[51\]

//+------------------------------------------------------------------+  
//| Inicialización                                                   |  
//+------------------------------------------------------------------+  
int OnInit()  
{  
   // Arrancar sistema Winsock de Windows \[58, 59\]  
   int startup\_code \= WSAStartup(0x0202, wsa\_data);  
   if(startup\_code\!= 0\)  
   {  
      Print("Fallo en inicialización de Winsock. Error: ", startup\_code);  
      return(INIT\_FAILED);  
   }  
     
   // Crear descriptor de socket \[54, 60\]  
   m\_srv\_socket \= socket(AF\_INET, SOCK\_STREAM, IPPROTO\_TCP);  
   if(m\_srv\_socket \== INVALID\_SOCKET)  
   {  
      Print("Fallo al crear socket de escucha.");  
      WSACleanup();  
      return(INIT\_FAILED);  
   }  
     
   // Establecer comportamiento NO BLOQUEANTE para evitar colgar la terminal   
   uint non\_blocking\_arg \= 1;  
   if(ioctlsocket(m\_srv\_socket, FIONBIO, non\_blocking\_arg) \== SOCKET\_ERROR)  
   {  
      Print("Fallo de configuración no bloqueante.");  
      closesocket(m\_srv\_socket);  
      WSACleanup();  
      return(INIT\_FAILED);  
   }  
     
   // Enlazar socket al puerto local 8080 \[54, 56\]  
   sockaddr\_in server\_addr;  
   server\_addr.sin\_family \= AF\_INET;  
   server\_addr.sin\_port \= htons(8080); // Escucha en puerto 8080  
   server\_addr.sin\_addr \= 0;           // Escuchar en todas las IPs activas (INADDR\_ANY) \[61\]  
     
   for(int i \= 0; i \< 8; i++) server\_addr.sin\_zero\[i\] \= 0; // \[62\]  
     
   if(bind(m\_srv\_socket, server\_addr, sizeof(server\_addr)) \== SOCKET\_ERROR) \[54, 56\]  
   {  
      Print("Error en bind(). Puerto 8080 en uso? Error WSAGetLastError: ", WSAGetLastError());  
      closesocket(m\_srv\_socket);  
      WSACleanup();  
      return(INIT\_FAILED);  
   }  
     
   // Escuchar peticiones entrantes \[52\]  
   if(listen(m\_srv\_socket, 10\) \== SOCKET\_ERROR) \[52, 54\]  
   {  
      Print("Error en ejecución de listen().");  
      closesocket(m\_srv\_socket);  
      WSACleanup();  
      return(INIT\_FAILED);  
   }  
     
   Print("\[\*\] Servidor REST montado en MT5. Escuchando peticiones en puerto 8080...");  
   EventSetTimer(1); // Consultar sockets de forma periódica cada segundo  
   return(INIT\_SUCCEEDED);  
}

//+------------------------------------------------------------------+  
//| Desinicialización                                                |  
//+------------------------------------------------------------------+  
void OnDeinit(const int reason)  
{  
   EventKillTimer();  
   if(m\_srv\_socket\!= INVALID\_SOCKET)  
   {  
      closesocket(m\_srv\_socket);  
   }  
   WSACleanup(); // \[63\]  
   Print("Servidor REST cerrado y Winsock liberado.");  
}

//+------------------------------------------------------------------+  
//| Bucle periódico de aceptación de conexiones HTTP                 |  
//+------------------------------------------------------------------+  
void OnTimer()  
{  
   if(m\_srv\_socket \== INVALID\_SOCKET) return;  
     
   sockaddr\_in client\_addr;  
   int addr\_len \= sizeof(client\_addr);  
     
   // Intento de aceptación de cliente sin bloqueo de hilo   
   SOCKET client\_socket \= accept(m\_srv\_socket, client\_addr, addr\_len);  
     
   if(client\_socket \== INVALID\_SOCKET)  
   {  
      int err \= WSAGetLastError();  
      if(err \== 10035\) // WSAEWOULDBLOCK (Normal en modo no bloqueante)   
      {  
         return;  
      }  
      return;  
   }  
     
   // Leer solicitud HTTP entrante  
   char rcv\_bytes;  
   int bytes\_read \= recv(client\_socket, rcv\_bytes, 2048, 0);  
     
   if(bytes\_read \> 0\)  
   {  
      string request\_text \= CharArrayToString(rcv\_bytes, 0, bytes\_read, CP\_UTF8);  
      string response\_payload \= "";  
        
      // Enrutamiento de peticiones REST   
      if(StringFind(request\_text, "GET /positions")\!= \-1)  
      {  
         // Consultar y empaquetar posiciones de trading activas  
         int total \= PositionsTotal();  
         string positions\_json \= "  
         }  
         positions\_json \+= "\]";  
         response\_payload \= FormulateHttpResponse(200, "OK", positions\_json);  
      }  
      else if(StringFind(request\_str, "POST /order")\!= \-1)  
      {  
         // Simulación de inyección de órdenes externas de compra   
         string execution\_json \= "{\\"status\\":\\"EXECUTED\\",\\"ticket\\":85090920}";  
         response\_payload \= FormulateHttpResponse(201, "Created", execution\_json);  
      }  
      else if(StringFind(request\_str, "DELETE /order")\!= \-1)  
      {  
         // Simulación de cancelación de órdenes externas \[24\]  
         string cancel\_json \= "{\\"status\\":\\"CANCELLED\\",\\"ticket\\":85090920}";  
         response\_payload \= FormulateHttpResponse(200, "OK", cancel\_json);  
      }  
      else  
      {  
         // Error por defecto si no se encuentra la ruta asignada  
         string error\_json \= "{\\"error\\":\\"Endpoint no encontrado o no soportado\\"}";  
         response\_payload \= FormulateHttpResponse(404, "Not Found", error\_json);  
      }  
        
      // Enviar respuesta HTTP  
      char send\_bytes;  
      StringToCharArray(response\_payload, send\_bytes, 0, StringLen(response\_payload), CP\_UTF8);  
      send(client\_socket, send\_bytes, ArraySize(send\_bytes) \- 1, 0);  
   }  
     
   closesocket(client\_socket); // Cerrar conexión  
}

//+------------------------------------------------------------------+  
//| OnTick                                                           |  
//+------------------------------------------------------------------+  
void OnTick()  
{  
   // No bloqueante  
}

//+------------------------------------------------------------------+  
//| Formulación de respuesta HTTP/1.1 estándar con payload JSON     |  
//+------------------------------------------------------------------+  
string FormulateHttpResponse(int code, string text, string body)  
{  
   string formatted \= StringFormat("HTTP/1.1 %d %s\\r\\n"  
                                   "Server: MT5 REST Embedded\\r\\n"  
                                   "Content-Type: application/json; charset=utf-8\\r\\n"  
                                   "Content-Length: %d\\r\\n"  
                                   "Connection: close\\r\\n\\r\\n",   
                                   code, text, StringLen(body));  
   return (formatted \+ body);  
}

//+------------------------------------------------------------------+  
//| Conversión htons (Host to Network Short)                         |  
//+------------------------------------------------------------------+  
ushort htons(ushort hostshort)  
{  
   return (ushort)((hostshort \<\< 8\) | (hostshort \>\> 8));  
}

#### **Fuentes citadas**

1. GitHub \- darwinex/dwx-zeromq-connector: Wrapper library for algorithmic trading in Python 3, providing DMA/STP access to Darwinex liquidity via a ZeroMQ-enabled MetaTrader Bridge EA., acceso: junio 28, 2026, [https://github.com/darwinex/dwx-zeromq-connector](https://github.com/darwinex/dwx-zeromq-connector)  
2. Integration with Python and support for Market and Signals services in Wine (Linux/macOS) in MetaTrader 5 build 2085, acceso: junio 28, 2026, [https://www.metatrader5.com/en/news/2086](https://www.metatrader5.com/en/news/2086)  
3. How to read a JSON from a URL in MQL5? \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/36978198/how-to-read-a-json-from-a-url-in-mql5](https://stackoverflow.com/questions/36978198/how-to-read-a-json-from-a-url-in-mql5)  
4. FileOpen \- File Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/files/fileopen](https://www.mql5.com/en/docs/files/fileopen)  
5. Network Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/network](https://www.mql5.com/en/docs/network)  
6. Libraries: Working with sockets in MQL5 \- Expert Advisor, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/1760](https://www.mql5.com/en/forum/1760)  
7. MQL5 Asynchronous named pipes? \- Pips \- Expert Advisors and Automated Trading, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/94343](https://www.mql5.com/en/forum/94343)  
8. WebRequest \- Network Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/network/webrequest](https://www.mql5.com/en/docs/network/webrequest)  
9. Introduction to MQL5 (Part 27): Mastering API and WebRequest Function in MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/17774](https://www.mql5.com/en/articles/17774)  
10. WebRequest function \- Free Trading Signals \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/477201](https://www.mql5.com/en/forum/477201)  
11. how to write code that parse my json that I got with webrequest \- Trading Forex \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/450396](https://www.mql5.com/en/forum/450396)  
12. GitHub \- vivazzi/JAson: Creation a JSON object with data of different types and run serialization and deserialization of JSON data., acceso: junio 28, 2026, [https://github.com/vivazzi/JAson](https://github.com/vivazzi/JAson)  
13. xefino/mql5-json: JSON library allowing for the serialization to and deserialization from JSON \- GitHub, acceso: junio 28, 2026, [https://github.com/xefino/mql5-json](https://github.com/xefino/mql5-json)  
14. JSON Serialization and Deserialization (native MQL) \- library for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/code/13663](https://www.mql5.com/en/code/13663)  
15. Network Functions \- MQL5 features \- MQL4 Reference, acceso: junio 28, 2026, [https://docs.mql4.com/mql5\_language/mql5\_functions/mql5\_network](https://docs.mql4.com/mql5_language/mql5_functions/mql5_network)  
16. Efficient Communication Between Multiple MT5 Instances and Python for Low-Latency Data Analysis \- エキスパートアドバイザーと自動取引 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/ja/forum/483092](https://www.mql5.com/ja/forum/483092)  
17. MQL5 SocketConnect fails with error 4014 connecting to local TCP server \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/79786669/mql5-socketconnect-fails-with-error-4014-connecting-to-local-tcp-server](https://stackoverflow.com/questions/79786669/mql5-socketconnect-fails-with-error-4014-connecting-to-local-tcp-server)  
18. MetaTrader 5 and Python integration using socket \- Expert Advisor \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/331936](https://www.mql5.com/en/forum/331936)  
19. SocketCreate \- Network Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/network/socketcreate](https://www.mql5.com/en/docs/network/socketcreate)  
20. Establishing and breaking a network socket connection \- Advanced language tools \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/network/network\_socket\_create\_connect](https://www.mql5.com/en/book/advanced/network/network_socket_create_connect)  
21. SocketIsConnected \- Network Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/network/socketisconnected](https://www.mql5.com/en/docs/network/socketisconnected)  
22. Reading and writing data over an insecure socket connection \- Advanced language tools, acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/network/network\_socket\_send\_read](https://www.mql5.com/en/book/advanced/network/network_socket_send_read)  
23. dwx-zeromq-connector/v2.0.1/python/api/DWX\_ZeroMQ\_Connector\_v2\_0\_1\_RC8.py at ... \- GitHub, acceso: junio 28, 2026, [https://github.com/darwinex/dwx-zeromq-connector/blob/master/v2.0.1/python/api/DWX\_ZeroMQ\_Connector\_v2\_0\_1\_RC8.py](https://github.com/darwinex/dwx-zeromq-connector/blob/master/v2.0.1/python/api/DWX_ZeroMQ_Connector_v2_0_1_RC8.py)  
24. DarwinexLabs/tools/dwx\_zeromq\_connector/v2.0.1/README.md at master · darwinex ... \- GitHub, acceso: junio 28, 2026, [https://github.com/darwinex/DarwinexLabs/blob/master/tools/dwx\_zeromq\_connector/v2.0.1/README.md](https://github.com/darwinex/DarwinexLabs/blob/master/tools/dwx_zeromq_connector/v2.0.1/README.md)  
25. MQL5 support by artbert · Pull Request \#45 · darwinex/dwx-zeromq-connector \- GitHub, acceso: junio 28, 2026, [https://github.com/darwinex/dwx-zeromq-connector/pull/45/files](https://github.com/darwinex/dwx-zeromq-connector/pull/45/files)  
26. DWX\_ZeroMQ\_Server\_v2.0.1\_RC8.mq4 \- GitHub, acceso: junio 28, 2026, [https://github.com/darwinex/dwx-zeromq-connector/blob/master/v2.0.1/mql4/DWX\_ZeroMQ\_Server\_v2.0.1\_RC8.mq4](https://github.com/darwinex/dwx-zeromq-connector/blob/master/v2.0.1/mql4/DWX_ZeroMQ_Server_v2.0.1_RC8.mq4)  
27. parrondo/mql5-json-api \- GitHub, acceso: junio 28, 2026, [https://github.com/parrondo/mql5-json-api](https://github.com/parrondo/mql5-json-api)  
28. Gunther-Schulz/MQL5-JSON-API-2: Metaquotes MQL5 \- GitHub, acceso: junio 28, 2026, [https://github.com/Gunther-Schulz/MQL5-JSON-API-2](https://github.com/Gunther-Schulz/MQL5-JSON-API-2)  
29. Named Pipes Communication between Python Server and Python Client on Window | by Pei Seng Tan | DataDrivenInvestor, acceso: junio 28, 2026, [https://medium.datadriveninvestor.com/named-pipes-communication-between-python-server-and-python-client-on-window-8cdf64504801](https://medium.datadriveninvestor.com/named-pipes-communication-between-python-server-and-python-client-on-window-8cdf64504801)  
30. File Functions \- MQL5 features \- MQL4 Reference, acceso: junio 28, 2026, [https://docs.mql4.com/mql5\_language/mql5\_functions/mql5\_files](https://docs.mql4.com/mql5_language/mql5_functions/mql5_files)  
31. Interaction between MQL5 (or C++) and C\# via Named Pipes \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/18160777/interaction-between-mql5-or-c-and-c-sharp-via-named-pipes](https://stackoverflow.com/questions/18160777/interaction-between-mql5-or-c-and-c-sharp-via-named-pipes)  
32. Named Pipe communication between two terminals \- Pips \- MQL4 and MetaTrader 4 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/153978](https://www.mql5.com/en/forum/153978)  
33. Shared memory issue \- Factor Analysis \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/474103](https://www.mql5.com/en/forum/474103)  
34. Using named pipes \- Pips \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/365812](https://www.mql5.com/en/forum/365812)  
35. Shared Memory using CreateFileMapping \+ MapViewOfFile \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/30456993/shared-memory-using-createfilemapping-mapviewoffile](https://stackoverflow.com/questions/30456993/shared-memory-using-createfilemapping-mapviewoffile)  
36. MapViewOfFile function (memoryapi.h) \- Win32 apps \- Microsoft Learn, acceso: junio 28, 2026, [https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-mapviewoffile](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-mapviewoffile)  
37. Creating Named Shared Memory \- Win32 apps \- Microsoft Learn, acceso: junio 28, 2026, [https://learn.microsoft.com/en-us/windows/win32/memory/creating-named-shared-memory](https://learn.microsoft.com/en-us/windows/win32/memory/creating-named-shared-memory)  
38. Calling named pipes dll from MT5. How to? | Page 2 \- Forex Factory, acceso: junio 28, 2026, [https://www.forexfactory.com/thread/347503-calling-named-pipes-dll-from-mt5-how?page=2](https://www.forexfactory.com/thread/347503-calling-named-pipes-dll-from-mt5-how?page=2)  
39. how to write code that parse my json that I got with webrequest \- Trading Forex \- General \- MQL5 programming forum \- Page 5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/450396/page5](https://www.mql5.com/en/forum/450396/page5)  
40. Mastering API and WebRequest Function In MQL5 \- General, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/296230/page47](https://www.mql5.com/en/forum/296230/page47)  
41. Opening and closing files \- Common APIs \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/common/files/files\_open\_close](https://www.mql5.com/en/book/common/files/files_open_close)  
42. File Opening Flags / Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/io\_constants/fileflags](https://www.mql5.com/en/docs/constants/io_constants/fileflags)  
43. FileOpen locks the file for access by another programme \- Trading Signals \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/150408](https://www.mql5.com/en/forum/150408)  
44. Working with Python \- Developing programs \- MetaEditor Help \- MetaTrader 5, acceso: junio 28, 2026, [https://www.metatrader5.com/en/metaeditor/help/development/python](https://www.metatrader5.com/en/metaeditor/help/development/python)  
45. Automated Trading using MT5 and Python \- Quantra by QuantInsti, acceso: junio 28, 2026, [https://quantra.quantinsti.com/glossary/Automated-Trading-using-MT5-and-Python](https://quantra.quantinsti.com/glossary/Automated-Trading-using-MT5-and-Python)  
46. Automated Trading with MetaTrader5: Order Management and Market Data Collection, acceso: junio 28, 2026, [https://dev.to/vital7777/automated-trading-with-metatrader5-order-management-and-market-data-collection-4pb8](https://dev.to/vital7777/automated-trading-with-metatrader5-order-management-and-market-data-collection-4pb8)  
47. lucas-campagna/mt5linux: MetaTrader5 for linux users \- GitHub, acceso: junio 28, 2026, [https://github.com/lucas-campagna/mt5linux](https://github.com/lucas-campagna/mt5linux)  
48. Installation on Linux \- For Advanced Users \- Getting Started \- MetaTrader 5 Help, acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/start\_advanced/install\_linux](https://www.metatrader5.com/en/terminal/help/start_advanced/install_linux)  
49. Download MetaTrader 5 for macOS and Linux \- News, acceso: junio 28, 2026, [https://www.metatrader5.com/en/news/2329](https://www.metatrader5.com/en/news/2329)  
50. Discussion of article "Working with sockets in MQL, or How to become a signal provider" \- page 3 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/91815/page3](https://www.mql5.com/en/forum/91815/page3)  
51. listen function (winsock2.h) \- Win32 apps \- Microsoft Learn, acceso: junio 28, 2026, [https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-listen](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-listen)  
52. Relearning C Part 1 \- Windows TCP Server \- Alert Overload, acceso: junio 28, 2026, [https://alertoverload.com/posts/2024/10/relearning-c-part-1-windows-tcp-server/](https://alertoverload.com/posts/2024/10/relearning-c-part-1-windows-tcp-server/)  
53. Network Programming Part 1 using Winsock — Programming Sockets \- Medium, acceso: junio 28, 2026, [https://medium.com/@adityakumarbgs6/network-programming-part-1-using-winsock-programming-sockets-1978e4de94a2](https://medium.com/@adityakumarbgs6/network-programming-part-1-using-winsock-programming-sockets-1978e4de94a2)  
54. accept function (winsock2.h) \- Win32 apps \- Microsoft Learn, acceso: junio 28, 2026, [https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-accept](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-accept)  
55. bind function (winsock.h) \- Win32 apps | Microsoft Learn, acceso: junio 28, 2026, [https://learn.microsoft.com/en-us/windows/win32/api/winsock/nf-winsock-bind](https://learn.microsoft.com/en-us/windows/win32/api/winsock/nf-winsock-bind)  
56. Problem with calling socket communication functions via DLL \- Profitable Trading Strategies \- MQL4 and MetaTrader 4 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/110080](https://www.mql5.com/en/forum/110080)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAaCAYAAACHD21cAAAAk0lEQVR4XmNgGHlgHhB/AuL/SPgjEPchK8IHYJpIAowMEE1n0SUIgWwGiEYvdAlC4CUDGc4EAbL8BwIgTSfQBQkBQv5zQheAgdcM+J0JilOsAJ//aoDYEV0QBJgZIJouoksAgSwDbgMZ+hkgkoFo4jOg4hfQxBkWA/EvIP4LxP8YEM4FYRD/DxB/B2IZmIZRMAoYALcBKZyfMMC3AAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAzCAYAAAAq0lQuAAADcElEQVR4Xu3dO6gkRRQA0ApMRDRQhMVIAwNDzcVdFUEFRRYNBAUjAzdYUNTESEQxUAwEQURUTFZDY8XITBD8gGYigiuKP/D/qUt3szV3a+bNzJth3nueA5fputWvpqY36EtNT20pAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAUXKsxr81XswdrCSu4Ts5CQAcHX+X4YZ/Se6o3i5D36+5Y0Ni7J4fy9D3U40fxuOvZ85Y3m01/ijDGD/X+H48/q096QCYN8/H25MWuLJs798JANixu2p8XOPh3FGGImJeUbUJi8bOfdF+IOWWdU/pj/dayu3avHkua5VzAYBD5K8aj9T4LOW/LMOKz6mU36R5BcYd5fy+aF+YcsuKVcTTKRfjHU+5XZs3z2Wtci4AcIh8VeOyMnuzv3N83XYBMG/8XLj8U+OJpr2q/D7fleHr3oMmzzPaF6fcIvnvAYAj4urxtb3ZX9vJ9byR4vUar9Z4pcbLzXk9D9b4MCdH8b631Lipxv1lKNj2I8a7uQzjxVfAe32uXcnz/GS2e08H9XMBABsy3ex/GV9vbXKbFuNGQTJPft941mzKPd8cLyNWC/P58SzclPu8xvXl3Ofeld48o/1s076oxktNuyePAQAccu0vQ+NGf2nTjmfbHmraPVFMLIpFHqvxXk5WJ8v5Rcc3Kfd+c7yXWJ17NOXOlHPj5ddd6c0z5nRf0363Oe7Z9WcAALbgi+Y4bvZPpva29d4jclHMTa4bc61ewZbPmeT85Z1caHPT/nBZbDfyTMr15hei4L075RZ9HZvzvXnmdrZXPwBwyMQeZ7HX19mxPe1zdmMZCpPo+33MbUsuMOJXqbHSFPmIaN87c8agV7B9W+Oqpn17GYqmaawY98/SXzX8KCeqT3OiDHuiXZNyF9R4M+XCC2V2xTJEO/8ad5V5ttfrreZ4kq8nAMC+rVtg9Aq2dT2VE6Onc2JDPsiJJcWWJs817XjGMFv3egIAzLVOgRG7+ce2HLEC2Fr3l6TTylaey362EVnkhpxYQuxLN/2PFBGxApddUba/IgoA/A+dKEMBkp8LYzVxDXtf4QIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHDk/QcKp8r2Wg8g6QAAAABJRU5ErkJggg==>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAWCAYAAAASEbZeAAAAgUlEQVR4XmNgGNzABojfAPF/ID4BxEyo0gwMk4F4GhL/GwNEsRKSGFjAHFkAKgbCYMCNLgAFGGLNQGyNLMCARRE2AFLwD10QGVxigCjiQpeAAZAHQApE0SVgQJABooAdXQIGQIGH7tDFaHysjkQR+8WA8DI6BgNpLBIw/B2maEgCACOXKAO83OAoAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAABF0lEQVR4Xu2TsU4CQRCGJxKjICIFPAQdLfEReAILExJ63sDQyAsQQmXsLCwpCAWGgsRWMRA6WksTKTQkKP5zO6fj3G5Jd1/yJ/t/c7uXbO6IUvbNKbJCdsiTmcVcIWvkA2maWYIGucMOpbeR99+pY4mMVV8gj6r/o0zuwGPluHNiCqbHsCtaydgDmJzpM0o+w7C7sZLhwVzWNXJ3a/G9mPH6isg75AU5QXriNN7NFPAXgcE38qm67xnG6+siX42fiI/xbqaAz4q8NX4g/ly6dzOFfSSHxj2IP5J+L93CrmMl80zuDjVb5Ev1PLkDMsqdiQvCw76sW9IP/sYRU+RN9Q0FvlHNJbl//toOFFVkhHSRkpmlpOyDH+0CUjl+rWU1AAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAWCAYAAAASEbZeAAAAW0lEQVR4XmNgGBqgBIgz0QVBYDkQ/wLi/1CchSqNCQaromx0QXQAUpSLLogOQIry0AXRAUhRAbogOgApKkQXRAYiDBBFPegSILAaiF8D8RMgfgylXzJAomroAgBDrhlwfTmIpwAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAWCAYAAADNX8xBAAAAyElEQVR4Xu2TPQ5BURBGR6kRhZ3Yiw1o/ISQaK2AJegVlqDWqEjEWwCN6EhENHxz7/Vy7xfTCN07yYncM2YSBZGCbxjBNseIMbzAG2zSTObwAZ/BTjrO2cNl9N7BVfROsA5VxM8YbVWOinVoI/ahGUfFOvT+2YzVf3uoy1HsBau72OMo9oLVXexzFHvB6i4OOIKrfF7QlnFUdDDkCBpiH6pzrIXBlAcBnbWi9yS0nAU8wyM8hM+T+L9NTFn84hpu4R2Wkm8U/J8X+jZFsNrzBsMAAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAWCAYAAADNX8xBAAAA+ElEQVR4XmNgGAXEgkIgXgnEWlC+BhAvAeICuAoEqAXiT0D8DYiT0eQYWoD4Pxo+j6ICAq4B8W4k/hUgPorEZ6gH4klAvBCIa4CYGVkSCvgYIBagA5CYAIwD0uyIkMMKLjDgNmgOjFPNQNggmJfRAYp4JRC3QgXmQ+mZMEkoIMqgIiDeiZADA5BkMxqfoEHYALoCdD4MoIgzIknAwF8GMgwCMd4i5OBiyBo/o/FhACR2HZlTipCDiyFrDEPjwwBIzBjGASV3UYQcgwMDRIE6khgIgMQykPjdUDEUAPIazBUgrIQqDQacDBC5U0B8EYh/MGAP31FASwAAzZdQbwVsMJ0AAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAXCAYAAADduLXGAAAAjklEQVR4XmNgGAUDAeqBWAxNjBOKMcB/IHbHIrYWTYzBGyqBDkBixuiC56ASyCAMixgYgATPoondgIpjAJBgABaxI2hiDEFQCVY0cZCYF5QN9+RlqEQ2TAAI/kLFmIC4lwEp+ECCj6A0CD+Biu+A8ldB+WAAEvBBFsAFQJ7C6mNs4DQDCYqvA3EZuiB9AQDZziTfzpCf0QAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAWCAYAAADTlvzyAAAAiElEQVR4XmNgGAWjYDgCb3QBWoFZQPwbiDXQJagN9gDxRyAWQ5egJmAB4mtA/BCIOdHkqAr4gPglEJ8BYiY0OaoCaSD+CsSb0CVoBUAJ4Q8Qz0CXoDWA+XQjugStAQ8QPwXiU0DMiCZHU8AMxOeB+D4Qc6DJ0RyAgvkdEAujS9AapKILjIKRBQDRoRIgzQQd/AAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAZCAYAAADJ9/UkAAABSklEQVR4Xu2UvS4HURDFj0SjEYVoNAoPIFEqNJ5A4QU0PkJItLwAjYSO6Cgo1KgkElQkwgPQiEThKyISZjJ3Zfbce9nkX7q/5GRnzszO5O5uFigUgAXRJJuORdGT6E00TrWKftGZ6Et0RLWIHdEHrFk1VS//cC06dPmV6MTlyjBsRsUA5b+SW96J9BD1uijnJ6cHOyUvSW75BfLLN0LcE3K9eg6C/ye55dUrYby/5GLPFtJ+RCvL913sWUfaj9CmaTbRbPmxiz2rML+XC4w2zbCJZsu3XexZg/ntXGC0aZZNNFuee+ebSPsR2jTHpvCM9AD1bkI8FPKWvvZ5NoUxpAeoN0j5qMuVF9EjeRHdsJtXuBDQ2oTLl4Pn0VN+urwN1tPnvBq7ogfRneg2XO9hfyZPB2zQuehS9A4bzmjtVbQH6x+plwuFwn/hG6lpbbnBW51jAAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABMCAYAAADQpus6AAAJcklEQVR4Xu3decw21xjH8VNrq5a0al+irZbwT6lYiuYlVChqX5qI0j8UCUqkKPpa/qhSbRpEIkgX1NaKau0aqcQWQVFVS6md1tralfMz5+pzPdc7M/fMPTP35vtJrszMNXPP9t7vPec558xMSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALNxDY2JCe8VEdueYWEOvigkAAICx7MyxR0xO6Ptp+/a+UoZn57ily68jHRsAAMDofhMTE7s0xwdz3C/kz0/rX2CT/8QEAADAEMsoXNyqDE/McT2X/4YbX2f75Tg3JgEAAOZ1WUwsgBUSn5PjPmX89DI8tAzX3TIKwgAAYAOdFhML8pcytELNSWV8kwo5p8QEAADAPDapgLSKOL8AAGCQByYKFFPj/AIAgEFUmHh1TGJUOscPj0kAAICuqP2Z3kdz/DMmAQDAalulQtIi9+XKVG3vb3FGA9X8afnvxRkr6oqYKG6QFnue14Wet2cekeO7OW5cpndP1Tm7eZm+dY4/pe2PfwEA4P/CjrT4goTdBfq0OKPFovdxCptwDE2Oj4mO/DnZGXKzhgCw8Q6KiRVxz5gorp/j7jE5oY/HxEjen+PaMm4XHdUmfCZVNUhnlfwtcvy5zJef5nitmx7ThWk5F0ArtPVxTEykqvZlVWpcPhcTQd/jndfBOU5I1Xta/XnW8OVl+FuXl4+UnNh38MM5HlRyz8xxUY7dyny9nULfnb1zPKTkbH1vyfGSHE8o0238PjymDK9yOfHL3DXHU9w0AKw8/YidGXKXp9kXjSel4RcOXSD9Op4RpuehH+KmdehCMeu4xtK0D7PUfc7nbpKqfkwa+nlxeMcc9y/j983x/DIuddsYSutsW+9tU/v8eb0sVev9ZJzR0xT7Zj6b45xUbeO8MC96ZY7nxWSg9dwrJgfSHwDaN38e4nfquBxHlXGft3E//a8ytO+gzftFmP59Gcbn6Mn7anJN/DKPKkP/erRH5riNm1aB8UNuGgBW3jvSrj+IfwzTTeLn5lG3Dl8rNI+6dYr+ol5Uge3xMdFR3b4fkOOJZVwXGokX0xfm+EHamq+Lk71DUxfNd5ZxqdvGUFrnF2Iy6LrdvndBqrChdVsfpXl03bd5vNmNazuz3m06a180XzVcY1FNsL2DVX3B4nfL87k4HqfFjtWmv1OG5ltlaH0R/Tre6sZn8Z87ugytFlrU989YP8a64wOAlaYfrhu66diP5F05vp7jRiHvf/DUsfdHaftnX5yqv2LVHPJYl/fqfjRjTk0calYx++R4hZs+NsfZblqf3yPHGTlu5/IqRPkC2+GpuoDcweXG8OyY6CEeu7H8gTl+kqoaG50HNfvofZlqOvIXTdVcKP5QhqLzoc+28efZvCEmami7b4/JoOnYokfHRAd27NbRvI/9U1Vg0I0Jh4V5Y3ijG9c+nuym62hf4v81T+tQ83eb+EfXnmHa0/dfz9CTHWnr30k14Cr0aKj1KXSurKlRy6kWy/+B9e8cF5fxv6et76A+o23cLMe3y/xrSv6vZShqhtUNA3KXVH32AWW6idajm1DsmPUdPjVtNcPad8OO64IcX0pVbTwArBU1R9hfuK/3M1L1I/c2N+7/UvUX4Ne4ccurxsPGmy7WdXnlrAbBz/ePM/B9sW6fti/nx1WQsb5JvsD2u1RdPEQ/9irgRZe3RNuLuOPFso+68yFNeaPaNaO+QEN8zI13fR2S9u91MRnMOgZjfZD60IVe6++6DU+FWN01KKpxntI8+xdpHVYoaqOCjKiwpi4MXWjdKth3McaxAAB6UGd8+/Ft+xFWH7AXuWlb9osuJ8pbzVbb+qRuvnK6Nd/GzaFu+iiXF79cXKdN+wKbcmo2VKgJTsc2lrh90QvJ6+JufqFU/1lpyns7YmIAbc8K6l1o+RfEZNB2DP6cqGbWT9/JLddG/aO0jX/EGTP4/bI/PFQ7pH5/1g9KzcpabkeZbtPUB02f1/+1obSeX8dkAxXajozJFl+LCQDAatFF4MFp1wLEu9PWXV9qhlHzo7ELXbwQa1qdp228Td18y6nQ5+ero7VNP93lxS8X12nTKrBdGHJTGLLups825aeimrU+29SyL43JoOv65qlhM9pG38/XfXcucTmx2qquxxD9yo2rRngI7cOspm3RnZeqWVOTYxd2bLP62AEAlkjNYHUXI5+zvlLG5h2Rttcc1F0Am8T56k/zXjft578px6fK+ONc/pDUvk1b31NzfL6Mx2V8M+BQ34yJHuJ+mab8FNrOZRMtd1JMBl3X1bfAZfZL2787XdUdrwpsqnW1ZnMz6xhOyHF1yMU7Q58cpvvSPnw1JoO90vZmUCtwNvEd9P04AGAF1V2M1DSpvN2mb8v8MsfPUtV0JGo+0jx/sVKtgp79pf5ikRWybN26oFhn4+jSVC13j5C3z8dxdVLWnW+atibQh+X4eaqazaz/mT3GQJ2QV4H60ul8aT9jrcisC+5YnhsTaXZTp+g8vicmHfsu1B1bNE+BTTdG3DsmO9o3Vfv/iTgjbd2wIf5O2zNTdRw+TPwe23fTf0eH0Dr0LL6+9omJIu7frH8fAAA2xpiFwC53aS6bLvSXxeSc1G+tr3izzFBWsLKbcfQcry7qCrxj0749KyYBAEB/9oDQMfj+T6tKj3YYo/ZoHn23aw9kbaPHpqgm1vpKdq0hUz/QH8fkyLQP/nE1AABgAD2Taqi+D5FdFj2DbVZhZgp9t2lN++us7zEDAAD8z1SvnmpT1zeyiTrhd6khWwebcAwAAGBJFlmQ8E2UfcK/0WMd6c7PRZ5nAACwYVSQ8G/CwPh+mOPLMQkAANDVFTk+HZMYlQrFN41JAACArvTOVprrpsX5BQAAgy2jQLFbTNTYPSbW1FkxAQAA0NeBafEd+w+OiUAvk19GQXJsV8UEAADAvBZZODosJhoscp+msgnHAAAAVoTeM9ulmXKoI3LsXeL4HKeWOCXHyTl2Xrfk+hd2Tsuxf0wCAAAMsagCUtftdF1uVY3x1gwAAIBdXBsTE/hAjmNjMlAfNxXYDooz1sQ1MQEAAIDVsWdMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEv3X3qdM3WSO0WYAAAAAElFTkSuQmCC>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAABJ0lEQVR4Xu2SMUvDUBSFLxbBodDNRQfBpag/Qie3Ti5uontp3bSCgvoH3Jyk4mBxcRFR3EonkeIfcLeLiIhDRT039yV575DUSVzywUeTc08ur21ECv6KJuzAOXdfhWewkTRSbuE3fIHrNAs4ECv69oOGofm4u15194N0HLILj2Ab7sBSOI64hpeUXYktrlEeoYuWOCQ+xRaseNm8y569LKElvy+dgqeULYotfaA8YgseihVO3Odx0MjmRqy7wANlU6zgo+V9ynz0d9fOPQ9GEb8FeXxIzteOeYJrlA0le+mEWD7mZbPedURZrPROed5Js7I7DhQ9FaMP9yj7gntwW+w11D+3C+teJ2EDPsJpOAlf4VvQsCw+PTuT1kIq8BxewGWaFRT8Jz/vJke2BhbW9gAAAABJRU5ErkJggg==>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAWCAYAAAAxSueLAAABUUlEQVR4Xu2Tvy4GQRTFD40gEQoajYgHkCgUJBpPoPACGh6CRqkSfyqikKgUalQSCSpEeAlR+B8R3LMzs853v/lkW8n+kpO959y7M9ndWaDmPzNpujd9m85M7Y3tkkXTo+nVNOd6iRHTOcJax66HNdOmeC7EwWHJyK3pSPyN6VQ8mUK4NzHqfGHGNYiZDvU4n2DW6/yCePKB8LbQjeaFic8unU8w24r1QPS8KocxL1g2Tfz2Cvxm3ic0X5Ja2UE+L2Hzy/ncDZofSK1sIJ8XXCM0uySrstmJ1Moq8nlxUNjod3mVzfakVtaRyfti2OEbqLZZq2+2DZfzJ/aDu1I/oblPmN3FmoeM/s/TSPQwJDSbRevNxpyfEU+eTQ/J8KdLr8NLoZ8XvxIzhU/xKb4NYWaIZjCanN7CfElnzC9MV6Z3hMU87L2Y9hHmpxvbNTUZfgBAZXwtXd0kTQAAAABJRU5ErkJggg==>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAWCAYAAAASEbZeAAAAkUlEQVR4XmNgGLygEIhXArEWlK8BxEuAuACuAghagPg/Gj6PrAAE6oF4EhAvBOIaIGZGlYYAkIQjuiA6qGYgQlElELcyQNwyH0rPRFEBBEVAvBNNDKSwGU0MA8B8CQeMyBwo+MuApgjEeYssABXDUFSKLAAVQ1H0DYhFkfgODBAF6khiYACyDqYbhJVQpYcgAACKcyQv/8rJtgAAAABJRU5ErkJggg==>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAWCAYAAAASEbZeAAAAmElEQVR4XmNgGNxACIifAfF/IL4HxPyo0gwMbAwQBTDAyABRbIgkxvABmQMFOkD8F1kApCsTWQAI9KHicPAeKrAHSQxkui0Sn4GZAaIIhkEKfJAVwIAUA6rCq6jSDAzuQPwdyrZnQCi8CFcBFUAHjxiQxEOROWgAJG4BYoACDJ8iFE4TsgCUfwFNjOEjA0TxDSi9BFV6CAIAC+Mo1A4/jY4AAAAASUVORK5CYII=>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAWCAYAAABHcFUAAAAAjElEQVR4Xu3SMQrCQBRF0WgsIkgawSYbcC+uwz0Fd5HUrkAEO9tgYZFGSJFKC+8UNm8B87/wL5xmXjczRRFF0f900APLTnhjr4NFZ0zY6ZC7Fe54YC1b9mqMuGIpW/YazOh1sCx93g9aHTz0u7FOBw9t8MQFC9nMK3HDgEo2F6UnfWGrg4eOehBF3vsCk+4SIOvAuJMAAAAASUVORK5CYII=>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC4AAAAWCAYAAAC/kK73AAAAkUlEQVR4XmNgGAWjYBSMAloAM3SBoQLYgPgBEB8BYkZUqaEBmID4IhDfB2JONLkhA7YD8ScglkCXGCpgPhD/AWJddImhAlqB+D8Q26FLDHaQzQBxeCS6xGAFLQwQBzuhSwxWMBeIfwOxJrrEYAU7gPg9EIuiSwxGAKp0zgDxXSDmQJMb1ABU5Q/JGnMUjILhCgAtbRHWIqu+AAAAAABJRU5ErkJggg==>