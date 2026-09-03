# **Arquitectura Interna de MetaTrader 5: Guía de Referencia Técnica para Desarrolladores de Software**

La plataforma MetaTrader 5 (MT5) es un sistema de ejecución distribuido, diseñado específicamente para operar en mercados financieros con baja latencia y alta concurrencia.1 A diferencia de los entornos de desarrollo de propósito general, el runtime de MT5 impone un modelo híbrido donde coexisten la ejecución determinista en tiempo real y el procesamiento asíncrono guiado por eventos.3 Para un ingeniero de software, construir sistemas de trading algorítmico robustos (como Expert Advisors o pasarelas de integración de baja latencia) exige comprender a fondo la topología de red, el modelo de subprocesamiento (threading), el ciclo de vida de los eventos y el aislamiento de memoria que gobiernan la plataforma.5

## **1\. Modelo Cliente-Servidor e Infraestructura de Red**

La comunicación entre el terminal MetaTrader 5 y la infraestructura del broker se realiza mediante una arquitectura cliente-servidor propietaria, optimizada para mitigar la latencia de red y mantener un flujo continuo de cotizaciones e instrucciones de trading.5 La terminal establece conexiones TCP/IP directas hacia los puntos de acceso del broker, dividiendo el tráfico en canales especializados según el tipo de datos transmitidos.7

\+--------------------------------------------------------------------------+  
|                            Terminal MT5                                  |  
|                                                                          |  
|   \+-----------------------+                      \+-------------------+   |  
|   | Canal de Trading      |                      | Canal de Datos    |   |  
|   | (Baja Latencia / TCP) |                      | (Descarga / TCP)  |   |  
|   \+-----------+-----------+                      \+---------+---------+   |  
\+---------------|--------------------------------------------|-------------+  
                |                                            |  
                | SSL / TLS Encrypted (AES-256)       |  
                | Custom Protocol on Port 443 \[7, 9\] |  
                v                                            v  
\+--------------------------------------------------------------------------+  
|                         Servidores del Broker                            |  
|                                                                          |  
|   \+-----------------------+                      \+-------------------+   |  
|   | Servidor de Trading   |                      | Servidor Histórico|   |  
|   | (Motor de Ejecución)  |                      | (Bloques M1.hcc) |   |  
|   \+-----------------------+                      \+-------------------+   |  
\+--------------------------------------------------------------------------+

### **Canales de Comunicación y Flujo de Autenticación**

La terminal de MT5 interactúa de forma simultánea con dos entidades del lado del servidor, cada una con un puerto de red dedicado o lógicamente separado bajo un esquema de cifrado seguro.7 El establecimiento del canal TCP utiliza de forma nativa un cifrado simétrico robusto bajo el algoritmo AES-256, garantizando que el tráfico de datos de mercado y de trading no pueda ser interceptado o manipulado de forma maliciosa.7  
La autenticación estándar utiliza un esquema de desafío-respuesta (challenge-response) basado en la contraseña del usuario final.7 No obstante, los servidores de trading del broker pueden requerir de forma obligatoria un mecanismo de **Autenticación Extendida** basado en certificados SSL/TLS digitales 7:

1. El cliente inicia una conexión estándar con su número de cuenta y contraseña.7  
2. El servidor de trading valida las credenciales básicas y solicita a la terminal la generación de un par de claves criptográficas: una clave pública y una clave privada.7  
3. La clave pública se envía al servidor, el cual genera un certificado digital .pfx firmado digitalmente con su clave de autoridad para certificar que el acceso es lícito.7  
4. La terminal almacena este certificado localmente en la ruta física platform\_folder/config/certificates/.11  
5. Para transferir de forma segura este certificado a otros dispositivos, la terminal cifra el archivo utilizando una clave AES-256 robusta definida por el usuario (esta contraseña de cifrado jamás se envía al servidor).7 El servidor actúa únicamente como almacenamiento temporal de paso durante un límite máximo de una hora hasta que el dispositivo receptor (por ejemplo, una terminal móvil) solicita el certificado e introduce la contraseña de descifrado local para instalarlo.7

### **Diferencia entre el Servidor de Trading y el Servidor de Datos Históricos**

El comportamiento y el protocolo de datos varían sustancialmente entre los servidores asignados al cliente.7 El **Servidor de Trading** gestiona el estado transaccional en tiempo real, lo que incluye la transmisión instantánea del flujo de cotizaciones (ticks), la actualización del libro de órdenes y el procesamiento síncrono o asíncrono de solicitudes de compra y venta mediante funciones de la API como OrderSend u OrderSendAsync.1 Su prioridad es la mínima latencia y la consistencia transaccional.3  
Por otro lado, el **Servidor de Datos Históricos** es un motor de almacenamiento de bloques optimizado para transferencias masivas de datos históricos.8 Funciona bajo demanda: cuando un gráfico o un programa MQL5 solicita un intervalo histórico que no se encuentra en el caché del cliente, la terminal realiza una petición estructurada.8 El servidor histórico empaqueta los registros históricos en bloques comprimidos compuestos estrictamente por barras de un minuto (M1).8 La terminal recibe estos bloques, los descomprime y los indexa en su base de datos local.8

### **Comportamiento ante Pérdidas de Conexión**

Si la conexión TCP subyacente se interrumpe, el cliente de MT5 entra en un bucle automático de reconexión utilizando un algoritmo de retraso exponencial para evitar saturar el servidor del broker.1 Durante el periodo de desconexión, cualquier intento de enviar solicitudes de mercado síncronas generará de forma inmediata un código de error local en la API de MQL5. Al restablecerse el enlace, la terminal realiza un protocolo de sincronización rápido ("handshake de estado") donde descarga los datos históricos omitidos durante la desconexión y valida la consistencia de las posiciones abiertas y las órdenes pendientes locales frente a la base de datos transaccional maestra del servidor.3

| Parámetro / Protocolo | Servidor de Trading | Servidor de Datos Históricos |
| :---- | :---- | :---- |
| **Tipo de Transferencia** | Flujo continuo push en tiempo real.1 | Descarga masiva pull bajo demanda.8 |
| **Formato de los Datos** | Estructuras de ticks y estados transaccionales (MqlTick).5 | Bloques de barras M1 comprimidos binarios.8 |
| **Criptografía** | AES-256 con Autenticación Extendida Opcional SSL.7 | Cifrado de transporte de datos estándar de la plataforma.7 |
| **Impacto de Caída** | Rechazo inmediato de operaciones de trading locales.13 | Interrupción temporal de la reconstrucción de gráficos.8 |

## **2\. Arquitectura de Eventos (Event-Driven Model)**

El núcleo de MetaTrader 5 se basa estructuralmente en un bucle de eventos (event loop) que procesa de manera secuencial y determinista las señales provenientes del mercado, del temporizador del sistema y del entorno gráfico.4 Comprender la cola de eventos y sus prioridades es fundamental para evitar la pérdida de transacciones u operaciones lógicas críticas.3

                \+-----------------------------------------+  
                | Flujo de Entrada de Eventos             |  
                | (Ticks, Timers, Transactions, Graphics) |  
                \+--------------------+--------------------+  
                                     |  
                                     v  
                \+--------------------+--------------------+  
                |  Bucle de Despacho del Terminal (Core)  |  
                \+--------------------+--------------------+  
                                     |  
                                     |  (Filtro de Coalescencia:  
                                     |   ¿Ya existe el mismo tipo  
                                     |   de evento en cola?)   
                                     |  
                   \+-----------------+-----------------+  
                   |                                   |  
                   v (No)                              v (Sí)  
        \+----------+----------+               \+--------+--------+  
        | Insertar en la Cola |               | Descargar Evento|  
        | de MQL5 (Max Cap.)  |               | (Silencioso)    |  
        \+----------+----------+               \+-----------------+  
                   |  
                   v (Despacho Secuencial)  
        \+----------+----------+  
        | Manejadores MQL5    |  
        | (OnTick, OnTimer...)|  
        \+---------------------+

### **El Bucle de Eventos y Manejadores Predefinidos**

Cada gráfico visual de MT5 posee su propio hilo de despacho de eventos, y todos los programas MQL5 que se ejecutan en él se suscriben de forma pasiva a dicho canal de comunicación.4 El ciclo de vida de un programa se gestiona exclusivamente a través de manejadores de eventos predefinidos por la API del lenguaje 3:

* **OnInit()**: El punto de entrada de inicialización.3 Puede retornar un tipo entero (int) para definir códigos de error avanzados mediante la enumeración ENUM\_INIT\_RETCODE.3 Si retorna un valor distinto de cero, denota un fallo en la inicialización y genera automáticamente un evento de deinitialización con el código de error REASON\_INITFAILED.3  
* **OnDeinit(const int reason)**: Invocado inmediatamente antes de descargar un programa de la memoria, proporcionando el motivo exacto de la descarga (como cambio de parámetros, cambio de símbolo del gráfico o cierre de la terminal).3  
* **OnTick()**: El manejador maestro de cotizaciones para los Expert Advisors.4 Se activa con cada cambio de precio (bid/ask) del símbolo al que está adjunto el gráfico.3 No se ejecuta en indicadores ni scripts.4  
* **OnTimer()**: Se activa periódicamente de acuerdo con el temporizador del sistema configurado mediante la llamada EventSetTimer() o EventSetMillisecondTimer().5 Es ideal para realizar tareas de polling o de control temporal síncronas.18  
* **OnBookEvent(const string& symbol)**: Se activa de forma asíncrona ante cambios en la estructura de profundidad del mercado (DoM) tras realizar una suscripción explícita mediante MarketBookAdd.  
* **OnTradeTransaction(const MqlTradeTransaction& trans, const MqlTradeRequest& request, const MqlTradeResult& result)**: Exclusivo para Expert Advisors, este controlador procesa las respuestas del servidor de trading ante transacciones locales o externas asociadas a la cuenta del usuario.3  
* **OnChartEvent(const int id, const long& lparam, const double& dparam, const string& sparam)**: Permite capturar la interacción directa del usuario con el gráfico, incluyendo clics de ratón, pulsación de teclas e interactividad de objetos gráficos.3  
* **OnTester()**: Se ejecuta en los agentes de prueba de optimización genética del Strategy Tester para calcular un valor de optimización personalizado una vez concluido un ciclo completo de backtesting.20

### **Prioridades, Coalescencia y Garantías de Entrega**

La terminal de MT5 no garantiza el procesamiento en tiempo real de cada uno de los eventos si el hardware se encuentra saturado o si el programa MQL5 realiza bloqueos síncronos prolongados de CPU.4 El motor aplica un filtro estricto de **Coalescencia de Eventos** para evitar el desbordamiento de memoria 4:

* Si un evento de tipo NewTick (Tick de mercado) o Timer llega a la terminal y ya se encuentra un evento del mismo tipo en la cola de procesamiento del programa MQL5 (o el manejador anterior sigue en ejecución), el nuevo evento entrante se descarta de forma silenciosa.4 Por ende, no existe garantía alguna de que cada tick de mercado ejecute una iteración física de OnTick().4  
* El procesamiento de los eventos gráficos (OnChartEvent) opera bajo el mismo principio de coalescencia con el objetivo de mitigar las ráfagas masivas de eventos generadas, por ejemplo, al mover el cursor continuamente sobre el gráfico.4 Sin embargo, eventos críticos de control como pulsaciones físicas de teclas o transacciones de red se encolan con mayor prioridad de entrega.13

### **El Mecanismo Crítico de OnTradeTransaction**

El flujo transaccional de MetaTrader 5 destaca por ser asíncrono y multipartito.3 Enviar una única solicitud de mercado para abrir una posición (por ejemplo, mediante OrderSendAsync) genera una serie secuencial de transacciones que viajan de vuelta desde el servidor hacia la terminal 3:

1. Recepción y aceptación de la petición en el servidor (TRADE\_TRANSACTION\_REQUEST).13  
2. Creación formal de la orden de trading (TRADE\_TRANSACTION\_ORDER\_ADD).13  
3. Ejecución física de la orden y registro en la cuenta (TRADE\_TRANSACTION\_DEAL\_ADD).13  
4. Cierre y remoción de la orden activa para trasladarla al historial de transacciones (TRADE\_TRANSACTION\_HISTORY\_ADD).13

Cada uno de estos pasos dispara de forma individual el evento OnTradeTransaction.3 Sin embargo, la plataforma advierte formalmente de que **el orden de llegada de estas transacciones a la terminal no está garantizado de forma secuencial** debido a la naturaleza multi-hilo del servidor del broker.3  
La cola interna de transacciones posee un límite máximo estricto de **1024 elementos**.3 Si el desarrollador programa lógica ineficiente (como bucles complejos de análisis de datos o llamadas bloqueantes de red) dentro del cuerpo de OnTradeTransaction, el procesamiento se retrasará y las transacciones antiguas no procesadas en la cola de la terminal serán sobrescritas y perdidas de forma irreparable por los nuevos eventos transaccionales entrantes.3

| Parámetro del Evento | OnTick | OnTimer | OnTradeTransaction | OnChartEvent |
| :---- | :---- | :---- | :---- | :---- |
| **Garantía de Entrega** | No (Coalescencia activa).4 | No (Coalescencia activa).4 | Limitada (Max 1024 en cola).3 | No (Coalescencia para ratón).4 |
| **Hilos Permitidos** | Expert Advisors únicamente.18 | EAs e Indicadores.18 | Expert Advisors únicamente.13 | EAs e Indicadores.16 |
| **Acción ante Espera** | Descarte inmediato del tick entrante.4 | Retraso y descarte del pulso temporal.4 | Pérdida de eventos al superar 1024\.3 | Descarte de eventos de ratón intermedios.16 |

## **3\. Modelo de Ejecución de Programas y Concurrencia de Subprocesos (Threads)**

Para diseñar aplicaciones robustas en MT5, es fundamental comprender cómo se distribuyen los hilos de ejecución en el sistema operativo para cada tipo de programa MQL5.4 A diferencia de MT4, donde todo el procesamiento visual e indicativo compartía el hilo principal de la interfaz de usuario, MT5 introduce un modelo multihilo asimétrico y distribuido.4

\+-------------------------------------------------------------------------+  
|                         MetaTrader 5 Process                            |  
\+-------------------------------------------------------------------------+  
      | (Main GUI Thread) \- Windows Messages (WM\_PAINT, Input)   
      |  
      \+---\>  
      |           |---\> Procesamiento de Ticks y Sincronización   
      |           |---\> Indicador Custom A (EURUSD, M15)   
      |           \+---\> Indicador Custom B (EURUSD, H1)    
      |  
      \+---\>  
      |           |---\> Procesamiento de Ticks y Sincronización   
      |           \+---\> Indicador Custom C (GBPUSD, H4)    
      |  
      \+---\> (Isolated Thread)   
      |  
      \+---\> (Isolated Thread)   
      |  
      \+---\> (Isolated Background Thread) 

### **Hilos de Ejecución y Compartición de Memoria**

El sistema operativo de la máquina hosts asigna los recursos de CPU a los programas MQL5 bajo reglas específicas según su naturaleza funcional 4:

* **Expert Advisors (EAs)**: Cada EA en ejecución corre en su propio subproceso (thread) dedicado asignado de forma independiente por el sistema operativo.4 La sobrecarga de procesamiento de un EA en un gráfico no afecta la capacidad de ejecución de otro EA en otro gráfico.4  
* **Scripts**: Al igual que los EAs, cada script se ejecuta en un subproceso asignado e independiente de forma temporal.4 El hilo se destruye una vez finalizada la ejecución de su función principal OnStart.4  
* **Services (Servicios)**: Se ejecutan de manera asíncrona en hilos de segundo plano persistentes.4 Al no poseer representación gráfica, no requieren de un gráfico abierto en pantalla para operar y se inician directamente al arrancar la terminal.4  
* **Indicadores**: Los indicadores operan bajo un modelo de subprocesamiento compartido extremadamente restrictivo.4 **Todos los indicadores calculados sobre un mismo símbolo de mercado, independientemente de que estén alojados en gráficos con temporalidades distintas, comparten el mismo hilo de ejecución física asignado a dicho símbolo**.4

### **Restricciones de Concurrencia y el "Main Thread" de Símbolo**

Este diseño compartido para los indicadores impone restricciones drásticas para evitar que la interfaz de la plataforma se bloquee:

* El hilo compartido de un símbolo gestiona de forma secuencial la recepción de cotizaciones (ticks), la sincronización local del historial con el servidor y el cálculo de todos los indicadores activos para ese activo financiero.4  
* Si un desarrollador introduce un bucle de cálculo ineficiente o una rutina de procesamiento lenta en un indicador, el hilo de ejecución completo del símbolo se bloqueará.4 Como consecuencia directa, se detendrá el procesamiento de ticks de ese símbolo, se interrumpirá la actualización de los gráficos visuales y ningún otro indicador de ese instrumento podrá recalcular sus buffers.4  
* Para proteger este hilo común de latencias externas, la API de MQL5 bloquea de forma nativa la llamada de funciones de red síncronas como WebRequest dentro de cualquier indicador.6 Un intento de realizar una solicitud HTTP en un indicador provocará un error crítico de compilación o de ejecución.6

### **Estrategia de Arquitectura para Servicios de Red en Indicadores**

Cuando un desarrollador requiere conectar un indicador técnico a APIs de inteligencia artificial o de datos externos (por ejemplo, para extraer métricas macroeconómicas en tiempo real), debe implementar un diseño desacoplado utilizando un MQL5 Service 6:

1. Se despliega un programa de tipo **Service** en su propio hilo dedicado de fondo para que realice las llamadas de red síncronas bloqueantes (WebRequest) de manera continua.4  
2. Los datos obtenidos por el servicio se escriben en variables globales compartidas del terminal (GlobalVariableSet) o se envían de manera estructurada al indicador inyectando un evento personalizado en el gráfico mediante la función EventChartCustom.6  
3. El indicador intercepta el evento de forma asíncrona dentro de su manejador OnChartEvent y lee los datos pre-procesados de la memoria intermedia de forma instantánea sin bloquear el hilo de ejecución compartido del símbolo.6

### **Sincronización de Procesos Externos (DLLs)**

Cuando se integran algoritmos desarrollados en C++ o Rust mediante el uso de DLLs externas, el desarrollador se enfrenta a la naturaleza monohilo interna de MQL5 para cada programa.24 Para sincronizar datos con hilos concurrentes que operan en segundo plano dentro de la DLL, se deben implementar mecanismos clásicos de sincronización de sistemas como semáforos, bloqueos de exclusión mutua (Mutex) o colas de mensajes de memoria mapeada.24 El hilo único de MQL5 puede interactuar con el recurso protegido sin bloquear la terminal evaluando las primitivas de sincronización mediante polling no bloqueante en intervalos temporales controlados.24

| Tipo de Programa | Subproceso (Threading) | Comparte Memoria / Contexto | Capacidad de Trading | Capacidad de Red (WebRequest) |
| :---- | :---- | :---- | :---- | :---- |
| **Expert Advisor** | Dedicado por instancia.4 | Limitado a su propio espacio. | Sí.4 | Sí.5 |
| **Script** | Dedicado por instancia (Temporal).4 | Limitado a su propio espacio. | Sí.4 | Sí.6 |
| **Service** | Dedicado por servicio (Background).4 | Limitado a su propio espacio. | No | Sí.6 |
| **Indicator** | Compartido por símbolo de mercado.4 | Todos los indicadores de un símbolo.4 | No.4 | No (Bloqueado por Runtime).6 |

## **4\. Gestión de Datos Internos y Estructura del Sistema de Archivos**

Para garantizar el acceso rápido a los datos de mercado sin comprometer excesivamente los recursos físicos del host, MT5 almacena internamente la información en bases de datos de bajo nivel estructuradas en archivos de disco altamente optimizados.8

### **La Base de Datos de Ticks y Formatos de Almacenamiento**

A diferencia de los formatos tradicionales planos basados en texto, MT5 procesa los datos mediante archivos binarios propietarios comprimidos 8:

* **Archivos .hcc (Hydro-Compressed Charts)**: Contienen el historial binario comprimido de barras de un minuto (M1) de un símbolo de mercado.8 El almacenamiento se fragmenta de manera anual: cada archivo almacena un año calendario de barras M1 (por ejemplo, el archivo 2026.hcc almacena los minutos de 2026).8 Se localizan físicamente en la ruta:  
  terminal\_directory\\bases\\nombre\_servidor\\history\\nombre\_simbolo\\ 8  
  Estos archivos funcionan exclusivamente como bases de datos maestras internas y no están destinados al acceso directo por parte del programador o de aplicaciones de terceros.8  
* **Archivos .hc (History Cache)**: Cuando un gráfico visual o un programa MQL5 solicita datos históricos de una temporalidad específica (por ejemplo, velas de una hora H1), la terminal lee los minutos binarios del archivo .hcc de origen y compila las barras de H1 bajo demanda en caliente.8 Este resultado se almacena en disco bajo la extensión .hc dentro de la carpeta /Cache del símbolo respectivo.11 Para maximizar el rendimiento, estos archivos residen en la memoria RAM mientras el gráfico o el EA esté activo; si transcurre un largo período sin llamadas, la terminal libera la RAM de forma asíncrona y guarda el estado consolidado de vuelta en el archivo físico de disco.8  
* **Archivo ticks.dat**: Almacena el historial nativo y completo de ticks recibidos directamente del broker.11 Este archivo de bajo nivel registra cada transacción física de cambio de precio incluyendo la marca de tiempo exacta de nivel milisegundo y el volumen operado.5

### **Gestión de la Memoria RAM y el Límite de Velas**

El consumo de memoria RAM de la terminal durante la carga masiva de series de tiempo e indicadores depende directamente del parámetro de configuración "Max bars in charts" (máximo de barras en gráficos).8 Para calcular el límite teórico de uso de memoria física de un indicador con múltiples buffers de datos asignados a un gráfico, se puede aplicar la siguiente ecuación matemática estándar:  
![][image1]  
27  
Donde:

* ![][image2] representa el número físico de buffers asignados al indicador (definido mediante \#property indicator\_buffers).  
* ![][image3] representa el valor máximo de barras configurado en el terminal ("Max bars in charts").8  
* Cada valor en coma flotante de doble precisión (double) en un buffer MQL5 requiere un tamaño de almacenamiento estricto de 8 bytes en la arquitectura de 64 bits.27

Si este parámetro de configuración se define con un valor ilimitado en sistemas embebidos de bajo rendimiento o servidores virtuales con limitaciones de hardware, el terminal consumirá rápidamente el direccionamiento de memoria, degradando el rendimiento de caché de la CPU y provocando fallos de paginación.27

### **Estructura de Directorios Crítica para Automatización de Software**

Para automatizar despliegues continuos mediante scripts de administración de sistemas, la terminal organiza sus archivos dinámicos y de configuración bajo un directorio raíz de datos unificado.11 El desarrollador puede acceder a esta ruta física desde la terminal mediante el menú File \-\> Open Data Folder.11

Directorio de Datos del Terminal (Ruta física de datos modificables)   
├── bases/  
│   ├── Default/  
│   │   └── history/ (yyyy.hcc, ticks.dat, cache/\*.hc)   
│   └── Server\_BrokerName/ (Estructura de bases de datos de brokers específicos)   
│       ├── News/ (news.dat \- almacenamiento de boletines de noticias)   
│       ├── Symbols/ (selected-xxxxx.dat, symbols-xxxxx.dat)   
│       └── Trades/ (Información mensual consolidada de deals e historia)   
├── config/  
│   ├── certificates/ (\*.pfx \- Certificados SSL de acceso extendido)   
│   ├── accounts.dat (Base de datos binaria encriptada de cuentas de usuario)   
│   ├── common.ini (Ajustes de conexión, proxies y datos del terminal)   
│   └── terminal.ini (Configuraciones de la interfaz visual del usuario)   
├── Logs/ (Registros de actividad diaria del terminal y MetaEditor)   
├── MQL5/  
│   ├── Experts/ (Código fuente \*.mq5 y binarios compilados \*.ex5)   
│   ├── Files/ (Única subcarpeta local autorizada por el sandbox)   
│   ├── Services/ (MQL5 Services persistentes de fondo)   
│   └── Profiles/  
│       ├── Charts/ (Estructuras \*.chr de perfiles de gráficos abiertos)   
│       └── Templates/ (Plantillas de estilos gráficos \*.tpl)   
└── Tester/ (Carpeta raíz del Strategy Tester de optimización local)   
    ├── Agent-127.0.0.1-2000/ (Directorio de trabajo aislado del agente 1\) \[11, 31\]  
    └── Cache/ (XML caché de resultados históricos de optimizaciones pasadas) 

## **5\. Seguridad, Sandboxing e Importaciones de DLL**

El lenguaje MQL5 prioriza la seguridad física de la máquina host del usuario impidiendo que el código de terceros ejecute acciones maliciosas o acceda a recursos privados del disco del sistema operativo de manera no controlada.29

### **El Aislamiento de Archivos (Sandbox del Sistema de Archivos)**

Cualquier función estándar de E/S de archivos de MQL5 tiene estrictamente prohibido interactuar de manera directa con rutas absolutas o realizar escapes relativos del árbol de directorios fuera de las fronteras físicas del sandbox.30 Las únicas carpetas con autorización física de escritura y lectura son 30:

1. **Sandbox del Terminal Local**: Ubicado dentro de la ruta de datos del terminal específico bajo el subdirectorio MQL5\\Files\\.29 Durante las ejecuciones en el simulador de estrategias (Strategy Tester), la terminal redirige este sandbox para aislarlo en la carpeta del agente de pruebas correspondiente (testing\_agent\_directory\\MQL5\\Files\\).30 Al final de cada optimización, el agente limpia por completo el contenido de este directorio para evitar persistencias no deseadas entre ejecuciones.21  
2. **Sandbox del Servidor Común**: Si se pasa la bandera explícita FILE\_COMMON a la API de manipulación de archivos, el runtime de la terminal redirige la operación hacia el directorio de almacenamiento global compartido por todos los terminales instalados en la máquina, ubicado físicamente en:  
   C:\\Users\\\<nombre\_usuario\>\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\ 29

### **Escape del Sandbox para Integración de Datos**

Para sistemas de trading de nivel empresarial que exigen compartir archivos de log en tiempo real o bases de datos compartidas con aplicaciones externas que corren en el host, la restricción física del sandbox puede superarse de manera segura utilizando los siguientes métodos avanzados de administración de sistemas 29:

* **Enlaces de Cruce de Directorio de Windows (Junction Links)**: El administrador puede crear un enlace simbólico de tipo Junction utilizando la consola de comandos nativa de Windows (mklink /J).29 Se crea un enlace de carpeta virtual dentro de la carpeta segura MQL5\\Files\\Links que apunte físicamente a un directorio externo libre en el sistema operativo.29 Para el entorno sandbox de MT5, la carpeta virtual es lícita y permite operaciones de lectura y escritura normales, mientras que Windows redirige el flujo de datos fuera del sandbox en tiempo real.29  
* **Bypass mediante el Registro de Windows de la Limitación de Ruta**: Por defecto, Windows impone un límite de ruta física de archivo (MAX\_PATH) equivalente a 260 caracteres, lo que puede truncar operaciones de escritura con estructuras de carpetas profundas en MQL5.29 El desarrollador puede modificar la entrada del Registro de Windows correspondiente para aumentar el soporte del sistema de archivos a 32,767 caracteres.29

Ruta del registro para habilitar rutas de archivo largas en Windows 10/11:

"LongPathsEnabled"=dword:00000001 

### **Configuración del Permiso para DLLs Externas y Seguridad de Ejecución**

La terminal implementa dos capas de permisos obligatorios que el usuario de la máquina debe validar explícitamente en la interfaz de usuario para que se permita la interactividad del sistema 5:

* **Allow DLL Imports (Permitir importaciones de DLL)**: Deshabilitado por defecto.35 Si un programa MQL5 intenta realizar una importación y este parámetro se encuentra inactivo, la ejecución de la instrucción de código se abortará inmediatamente arrojando un error de protección de memoria.21 Este permiso puede activarse de forma global para todo el terminal (Tools \-\> Options \-\> Expert Advisors) o configurarse individualmente de manera exclusiva para un archivo compilado .ex5 específico al cargarlo sobre un gráfico.35  
* **Allow Algo Trading (Permitir Trading Algorítmico)**: Controla el permiso de llamadas directas hacia la API transaccional del broker. Si está desactivado, el runtime de MT5 bloquea de forma nativa la llamada física a funciones como OrderSend, desactivando la negociación automatizada de manera global.

## **6\. Ejecución Multi-Terminal y Conectividad Multi-Cuenta**

Debido a limitaciones arquitectónicas intrínsecas del diseño de MetaTrader 5, un único proceso de la terminal ejecutándose de forma nativa está restringido a mantener una única conexión activa con un solo broker y una sola cuenta de usuario al mismo tiempo.36 Gestionar de forma paralela estrategias complejas o sistemas multi-cuenta exige desplegar una infraestructura multi-instancia basada en el aislamiento físico.36

### **Configuración e Implementación del Modo Portable (/portable)**

La solución de ingeniería más limpia y eficiente para desplegar múltiples instancias concurrentes consiste en configurar cada binario ejecutable bajo el **Modo Portable** de la plataforma.12 Al iniciar la aplicación con este parámetro de comandos, la terminal ignora las rutas centralizadas de datos del sistema operativo y almacena de manera unificada toda su configuración, base de datos de historial y archivos MQL5 directamente en la subcarpeta física del directorio donde fue instalado el binario ejecutable.12  
Para configurar un entorno portátil multi-instancia automatizado:

1. Cree copias independientes del directorio de instalación original en rutas físicas fuera de los directorios de protección del sistema (por ejemplo, C:\\MT5\_Terminals\\Terminal\_01\\, C:\\MT5\_Terminals\\Terminal\_02\\).12  
2. Cree un acceso directo o un script bash de Windows para cada instancia que apunte a la terminal ejecutando el parámetro /portable 12:  
   "C:\\MT5\_Terminals\\Terminal\_01\\terminal64.exe" /portable 36  
3. Asegúrese de que el usuario del sistema operativo del servidor posea permisos de lectura y escritura habilitados de forma explícita para dichas carpetas.12 Si la carpeta reside en Program Files, se deben tener permisos de Administrador de Windows y el Control de Cuentas de Usuario (UAC) debe desactivarse por completo para evitar que Windows virtualice de forma oculta los archivos dinámicos del terminal.12

### **Límites Prácticos y Consumo de Hardware en Servidores Dedicados (VPS)**

Aunque la arquitectura del sistema operativo Windows y la terminal admiten teóricamente la ejecución de hasta un límite físico de 32 instancias simultáneas por cada sesión activa de usuario, las restricciones físicas de recursos como memoria RAM y ciclos de procesamiento de CPU limitan el número práctico de instancias estables a un rango común de entre 24 y 28 terminales activos.36  
La asignación óptima de recursos de memoria RAM física e infraestructura de cómputo para despliegues multi-terminal en servidores se rige bajo los siguientes patrones empíricos:

| Número de Instancias Concurrentes | CPU Cores Mínimos | Perfil de Almacenamiento | RAM Mínima Requerida |
| :---- | :---- | :---- | :---- |
| **Instancia Única Estándar** | 1 Core vCPU.28 | SSD Estándar | 2 \- 4 GB de RAM.36 |
| **Poco Concurrente (2 \- 3 terminales)** | 2 \- 4 Cores vCPU.28 | SSD NVMe rápido | 4 \- 6 GB de RAM.36 |
| **Escalamiento Medio (4 \- 6 terminales)** | 4 \- 8 Cores vCPU.28 | SSD NVMe empresarial.28 | 8 \- 12 GB de RAM.36 |
| **Optimización de Bots (7+ terminales)** | 8 \- 16+ Cores vCPU.28 | SSD NVMe de alta velocidad | 16 \- 64+ GB de RAM.27 |

## **7\. Ecosistema de Componentes de la Plataforma y Protocolo MetaTester**

El ecosistema de desarrollo y pruebas de MetaTrader 5 está integrado por cuatro componentes físicos de software independientes que colaboran estrechamente a través de protocolos y buses locales de alta velocidad para permitir el ciclo completo de desarrollo y optimización de robots.2

\+------------------------------------------------------------------------+  
|                      Entorno de Trabajo MT5                            |  
\+------------------------------------------------------------------------+  
       |  
       \+---\> \[ MetaEditor.exe \] (IDE, Compilador nativo MQL5) \[2, 11\]  
       |         |  (Comunicación local / Depuración en caliente)   
       |         v  
       \+---\> (Instancia visual del sistema)   
       |         |  
       |         \+---\> (Gestor local de servicios) \[9, 11\]  
       |                     |  
       |                     \+---\>\[31, 38\]  
       |                     |       | (Ports 2000, 2001, 2002 TCP Loopback)   
       |                     |  
       |                     \+---\>\[31, 38\]  
       |                     |       | (Ports personalizados TCP remotos) \[21, 31\]  
       |                     |  
       |                     \+---\> \[ MQL5 Cloud Network \]\[38, 39\]  
       |                             | (Outbound SSL Port 443 a Network Poolers) 

### **Protocolo de Red de los Agentes de Prueba (MetaTester)**

Durante la fase de optimización de parámetros, el gestor de la terminal de MT5 actúa como un orquestador de tareas distribuido.31 Los agentes de prueba locales se instalan por defecto como servicios del sistema y se asignan de acuerdo con la cantidad física de núcleos lógicos de la CPU.9  
El protocolo de red para coordinar la distribución de tareas de optimización se divide según la topología de los nodos:

* **Agentes Locales**: Cada proceso de pruebas de segundo plano abre de forma exclusiva un puerto TCP local en la máquina, configurado de manera predeterminada y consecutiva a partir del puerto base **2000** en adelante (ejemplo, 127.0.0.1:2000, 127.0.0.1:2001, 127.0.0.1:2002).31 La terminal se conecta localmente a estas direcciones para transferir las variables binarias del EA y recopilar los resultados transaccionales asíncronos calculados por el motor de simulación histórica.20  
* **Agentes Remotos**: Si se configuran equipos externos conectados en red local para que colaboren como nodos esclavos de procesamiento, se debe realizar un mapeo de puertos (Port-Forwarding) en los enrutadores y firewalls de la red local para redirigir las conexiones TCP entrantes enviadas por la terminal maestra hacia las IPs de los agentes remotos.31  
* **MQL5 Cloud Network**: Para participar y recibir tareas remuneradas de optimización genotípica global dentro de la red MQL5 Cloud, no es necesario configurar reglas de puertos entrantes complejos en los firewalls perimetrales de la máquina.9 Los agentes locales inician de forma proactiva conexiones puramente **salientes** cifradas bajo el protocolo seguro de capa de transporte SSL a través del puerto estándar **443** hacia el equilibrador de carga o task manager geográficamente más cercano de MetaQuotes.9

### **Requisitos Técnicos Obligatorios para la Participación en MQL5 Cloud**

Para evitar la ralentización general de los procesos de cálculo distribuido de la red, MetaQuotes impone reglas de filtrado automáticas para admitir nodos en su nube 39:

1. El procesador de la máquina debe soportar de forma nativa el conjunto de instrucciones avanzadas vectoriales AVX.40  
2. Los agentes no pueden ser ejecutados bajo ningún entorno virtualizado de sistema operativo (tales como hypervisores de tipo Hyper-V, VMware o VirtualBox).39  
3. El host debe poseer un mínimo absoluto de **768 MB** de memoria RAM física asignada a cada agente individual, y un mínimo total de **2048 MB (2 GB)** instalados en el sistema para poder conectarse y sincronizarse con la infraestructura global.39  
4. La partición física del almacenamiento debe mantener en todo momento un espacio libre de disco duro no inferior a **500 MB** para el caché histórico.39  
5. El nodo debe poseer un índice de rendimiento de procesamiento (PR \- Performance Rating) calculado por la terminal no inferior a **50**.39 Cualquier nodo que puntúe por debajo de un índice de **100** será descartado de forma automática de los procesos de optimización genética masivos para no comprometer el tiempo de entrega de los resultados calculados por generaciones.39

## **8\. Actualizaciones y Versionamiento**

MetaTrader 5 utiliza un sistema automatizado obligatorio de actualizaciones de software denominado **LiveUpdate**.21 Para un desarrollador de sistemas de trading, este mecanismo de despliegue silencioso es uno de los factores más críticos, ya que introduce el riesgo constante de interrupciones funcionales inesperadas (breaking changes) en el código de producción.21

### **El Mecanismo LiveUpdate y Builds de la Terminal**

Cada ciclo de actualización de la terminal incrementa el denominado **Build Number**, que actúa como el identificador único de versión del runtime y del compilador.1 Cuando la terminal se conecta al servidor del broker, valida si existe un Build Number superior disponible en la red de MetaQuotes y procede a descargar e instalar los nuevos parches binarios en segundo plano de manera silenciosa.21 No se proporciona ninguna opción nativa en la configuración gráfica o de archivos .ini para deshabilitar o pausar este bucle de actualizaciones de manera definitiva.

### **Cambios Rompedores Comunes (Breaking Changes) en Actualizaciones**

Las modificaciones introducidas por MetaQuotes en nuevas builds de la plataforma pueden generar fallos en cadena en sistemas algorítmicos existentes:

* **Incompatibilidad de Bytecode en Ejecutables .ex5**: Un compilador MQL5 actualizado en el MetaEditor puede introducir directivas internas de bytecode que la máquina virtual de una terminal con una build más antigua no puede interpretar, fallando de inmediato al cargar el EA. De forma inversa, actualizaciones profundas del runtime de la terminal pueden rechazar archivos compilados antiguos .ex5, exigiendo una recompilación inmediata del código fuente .mq5 original utilizando el compilador más reciente.21  
* **Depreciación Directa de Funciones de la API**: Funciones completas e históricas del lenguaje MQL5 pueden ser eliminadas de forma repentina del núcleo del compilador, como ocurrió con la depreciación total de la suite de funciones Signal\*, las cuales pasaron a retornar conjuntos de datos vacíos de forma permanente.40  
* **Modificaciones Funcionales de la Librería Estándar**: Cambios en la firma de métodos críticos de las clases base de la plataforma (ej. CTrade, COrderInfo) integradas en los archivos .mqh de inclusión común pueden romper la compilación y la ejecución lógica de los programas.20

### **Estrategias de Mitigación en Entornos de Producción Robustos**

Para evitar la paralización de sistemas automatizados que gestionan capital en tiempo real, los ingenieros de software deben adoptar las siguientes medidas defensivas de versionamiento y despliegue:

1. **Uso de Compilación Estática mediante Recursos Integrados**: Al compilar un Expert Advisor, se debe priorizar la inclusión directa de todas las imágenes de interfaz, bases de datos internas y DLLs dependientes de manera estática directamente dentro del ejecutable .ex5 utilizando la directiva \#resource.20 Esto encapsula todas las dependencias lógicas, permitiendo que el binario de trading opere sin depender de actualizaciones externas en la estructura de archivos local de la terminal.20  
2. **Infraestructura Portable Congelada**: No se deben realizar ejecuciones de trading de producción sobre instalaciones estándar del terminal alojadas en las rutas de sistema por defecto.12 Se debe desplegar la terminal estrictamente bajo el **Modo Portable** (/portable) y empaquetar toda la subcarpeta de instalación en sistemas de control de versiones o imágenes de contenedores.12 Esto permite "congelar" de forma absoluta tanto el build del binario ejecutable terminal64.exe como el de la máquina virtual interna de compilación de MQL5, garantizando la total consistencia operativa del entorno con independencia de los ciclos de actualización del broker o de MetaQuotes.12

| Estrategia de Mitigación | Objetivo de Robustez | Riesgo Asociado |
| :---- | :---- | :---- |
| **Modo Portable en Rutas Privadas** 12 | Aislar por completo los binarios estables del terminal e impedir la corrupción de archivos dinámicos.12 | Exige poseer privilegios explícitos de escritura en el directorio fuera de Program Files.12 |
| **Bloqueo de Puertos de LiveUpdate** 21 | Impedir que la terminal de trading establezca conexiones con servidores de descarga de MetaQuotes.21 | Puede retrasar la corrección de fallos críticos del motor transaccional de la plataforma.21 |
| **Inclusión de Dependencias por \#resource** 20 | Eliminar de forma permanente la dependencia de archivos auxiliares locales externos al ejecutable .ex5.20 | Incrementa el tamaño físico binario final del archivo compilado .ex5.20 |
| **Recompilación Periódica Automatizada** 21 | Asegurar la compatibilidad del bytecode del EA con el build actual del motor virtual del terminal.21 | Requiere acceso constante al código fuente original en los servidores de producción.21 |

#### **Fuentes citadas**

1. MetaTrader | MCP Servers \- Claude Code Marketplaces, acceso: junio 28, 2026, [https://claudemarketplaces.com/mcp/ariadng/metatrader-mcp-server](https://claudemarketplaces.com/mcp/ariadng/metatrader-mcp-server)  
2. Algorithmic (automated) trading in MetaTrader 5, acceso: junio 28, 2026, [https://www.metatrader5.com/en/automated-trading](https://www.metatrader5.com/en/automated-trading)  
3. Event Handling Functions \- Functions \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/function/events](https://www.mql5.com/en/docs/basis/function/events)  
4. Program Running \- MQL5 programs \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/runtime/running](https://www.mql5.com/en/docs/runtime/running)  
5. The Ultimate MT5 Data Bridge: Hybrid REST & WebSocket TraderMade Plugin, acceso: junio 28, 2026, [https://tradermade.com/tutorials/MT5-tradermade-plugin](https://tradermade.com/tutorials/MT5-tradermade-plugin)  
6. Communicating with an api/custom server using a HTTP request inside of .mq5 indicator code, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/432897](https://www.mql5.com/en/forum/432897)  
7. Extended Authentication \- For Advanced Users \- Getting Started \- MetaTrader 5 Help, acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/start\_advanced/extended\_authorization](https://www.metatrader5.com/en/terminal/help/start_advanced/extended_authorization)  
8. Organizing Data Access \- Timeseries and Indicators Access \- MQL5 ..., acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/timeseries\_access](https://www.mql5.com/en/docs/series/timeseries_access)  
9. Questions about how to set up MetaTester 5 Agents Manager \- MQL5 Cloud Network, acceso: junio 28, 2026, [https://cloud.mql5.com/en/faq/settings](https://cloud.mql5.com/en/faq/settings)  
10. Extended Authentication \- Accounts \- MetaTrader 5 for Android, acceso: junio 28, 2026, [https://www.metatrader5.com/en/mobile-trading/android/help/settings\_accounts/extended\_authorization](https://www.metatrader5.com/en/mobile-trading/android/help/settings_accounts/extended_authorization)  
11. Files and Folders \- For Advanced Users \- Getting Started ..., acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/start\_advanced/structure](https://www.metatrader5.com/en/terminal/help/start_advanced/structure)  
12. Platform Start \- For Advanced Users \- Getting Started \- MetaTrader 5 Help, acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/start\_advanced/start](https://www.metatrader5.com/en/terminal/help/start_advanced/start)  
13. OnTradeTransaction \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/ontradetransaction](https://www.mql5.com/en/docs/event_handlers/ontradetransaction)  
14. Organizing Data Access \- MQL4 Documentation, acceso: junio 28, 2026, [https://docs.mql4.com/series/timeseries\_access](https://docs.mql4.com/series/timeseries_access)  
15. Qoyyuum/mcp-metatrader5-server: A Model Context Protocol (MCP) server for interacting with the MetaTrader 5 trading platform. This server provides AI assistants with tools and resources to access market data, perform trading operations, and analyze trading history. · GitHub, acceso: junio 28, 2026, [https://github.com/Qoyyuum/mcp-metatrader5-server](https://github.com/Qoyyuum/mcp-metatrader5-server)  
16. Interactive events on charts \- Creating application programs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/events](https://www.mql5.com/en/book/applications/events)  
17. Once again, about multithreading \- Hanging Man \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/394900](https://www.mql5.com/en/forum/394900)  
18. Event Handling Functions \- Functions \- Language Basics \- MQL4 Reference, acceso: junio 28, 2026, [https://docs.mql4.com/basis/function/events](https://docs.mql4.com/basis/function/events)  
19. Overview of event handling functions \- Creating application programs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/runtime/runtime\_events\_overview](https://www.mql5.com/en/book/applications/runtime/runtime_events_overview)  
20. Mises à jour : MetaTrader 5 \- Page 12, acceso: junio 28, 2026, [https://www.metatrader5.com/fr/releasenotes/page12](https://www.metatrader5.com/fr/releasenotes/page12)  
21. What's new in MetaTrader 5 \- Page 9, acceso: junio 28, 2026, [https://www.metatrader5.com/en/releasenotes/terminal/page9](https://www.metatrader5.com/en/releasenotes/terminal/page9)  
22. Are object events possible (button press) in the EA strategy tester (visual tester)? \- page 2, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/497953/page2](https://www.mql5.com/en/forum/497953/page2)  
23. Program Running \- MQL4 Reference, acceso: junio 28, 2026, [https://docs.mql4.com/runtime/running](https://docs.mql4.com/runtime/running)  
24. Callback to MQ5 code from DLL \- Trading Signals, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/462273](https://www.mql5.com/en/forum/462273)  
25. User seeks help with multi-symbol EA in MQL5, synchronization, and preventing race conditions \- Expert Advisors and Automated Trading, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/479378/page2](https://www.mql5.com/en/forum/479378/page2)  
26. Technical aspects of timeseries organization and storage \- Creating application programs, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/timeseries/timeseries\_storage\_tech](https://www.mql5.com/en/book/applications/timeseries/timeseries_storage_tech)  
27. Which Trading Strategies Actually Fit on a 2 GB VPS? Resource Sizing for MetaTrader EAs, acceso: junio 28, 2026, [https://www.vpsforextrader.com/blog/algo-trading-strategies/](https://www.vpsforextrader.com/blog/algo-trading-strategies/)  
28. Set Up MT4/MT5 on a Windows VPS (Step-by-Step) \- HostStage, acceso: junio 28, 2026, [https://www.host-stage.net/case-study/forex/mt4-mt5-vps-setup-guide/](https://www.host-stage.net/case-study/forex/mt4-mt5-vps-setup-guide/)  
29. Working with files \- Common APIs \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/common/files](https://www.mql5.com/en/book/common/files)  
30. FileOpen \- File Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/files/fileopen](https://www.mql5.com/en/docs/files/fileopen)  
31. Ideology of the MetaTrader 5 trading strategy tester: Agents \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/378](https://www.mql5.com/en/forum/378)  
32. Error opening the file in a specific directory \- Symbols \- Trading Systems \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/15331](https://www.mql5.com/en/forum/15331)  
33. Writing and reading files in simplified mode \- Common APIs \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/common/files/files\_save\_load](https://www.mql5.com/en/book/common/files/files_save_load)  
34. Opus 4.7 (Anthropic) Usage Policy Violations \- Help \- Cursor \- Community Forum, acceso: junio 28, 2026, [https://forum.cursor.com/t/opus-4-7-anthropic-usage-policy-violations/159013](https://forum.cursor.com/t/opus-4-7-anthropic-usage-policy-violations/159013)  
35. MQL5 Programming Basics: Files \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/2720](https://www.mql5.com/en/articles/2720)  
36. How to Open Multiple MetaTrader 5 (MT5) Terminals on the Same VPS \- QuantVPS, acceso: junio 28, 2026, [https://www.quantvps.com/blog/how-to-open-multiple-mt5-terminals-on-same-vps](https://www.quantvps.com/blog/how-to-open-multiple-mt5-terminals-on-same-vps)  
37. BigMitchGit/mt5\_remote: MetaTrader5 with remote access using a client/server architecture, acceso: junio 28, 2026, [https://github.com/BigMitchGit/mt5\_remote](https://github.com/BigMitchGit/mt5_remote)  
38. Strategy Optimization \- Algorithmic Trading, Trading Robots \- MetaTrader 5 Help, acceso: junio 28, 2026, [https://www.metatrader5.com/en/terminal/help/algotrading/strategy\_optimization](https://www.metatrader5.com/en/terminal/help/algotrading/strategy_optimization)  
39. Hyper-V problems and minimum requirements for MQL5 Strategy Tester Agents\!, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/167515](https://www.mql5.com/en/forum/167515)  
40. What's new in MetaTrader 5 \- Page 2 \- MetaQuotes, acceso: junio 28, 2026, [https://www.metaquotes.net/en/metatrader5/news/page2](https://www.metaquotes.net/en/metatrader5/news/page2)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAAA3klEQVR4XmNgGAWUgnlA/BmI/0PxAhRZCPjLgJAHYWdUaUyArBgb2AfEKuiC2AAjEG8H4vUMEMOCUKXBAJclGCAfiE2gbFyu+4MugAu8RWJ/YIAYxockpgbEnUh8vADZJaBwAfFvIoktA2IeJD5OAAqvzWhi6F7F5m2sADm8kMVABnRD+b+Q5PCCd+gCUABznTYQt6DJ4QS4vLCbASJ3D4g50eSwAhYg3osuCAVMDJhhhxMwA/EbID6JLoEEvgHxD3RBdLAKiD8yQNIXKF2B8h42oA/E2eiCo2AUDGkAAM4NNN65dbHtAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAZCAYAAADXPsWXAAAAxklEQVR4XmNgGAWEQAsQfwTi/1D8HYjfA/EHIP4LFXsGV00AwAxBB1IMEPEv6BLYAEjhJnRBKMBlAQrwY4AoMkCXAAJBBoQ38YKzDLhtgrmCCV0CHcAUKkOxBhD3Q8VWIqnDC0CK9wGxCxA7Q+k4qPhWJHU4ASw8DNElgICdASJ3F10CHZxnwB0eIEBUzIAUfEYXhIIUBoj8UXQJZABLSOXoEkBgxACR+40uAQOgwDvJgHDqDSA+CMR7oTRMfAJMwygYBQMGAM+MOSX549GiAAAAAElFTkSuQmCC>