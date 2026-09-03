# **Diseño e Implementación de Arquitecturas Híbridas de Alto Rendimiento: Integración Profesional de MetaTrader 5, Python y Servicios Cloud para Trading Algorítmico**

## **Arquitecturas de Referencia para Sistemas de Trading**

El diseño de un sistema de trading algorítmico profesional exige una definición rigurosa de la topología de red, los límites físicos de hardware y los flujos de datos para garantizar que las estrategias operen dentro de sus límites teóricos de latencia y riesgo. A continuación, se detallan tres arquitecturas de referencia para diferentes escalas de operación.

### **Arquitectura Simple (Monolítica Local / Retail)**

Este modelo se fundamenta en la co-locación de todos los componentes en un único sistema operativo Windows, ya sea un hardware físico local o un Servidor Privado Virtual (VPS) básico con recursos compartidos.1 El flujo de datos es local y síncrono.

\+-------------------------------------------------------------------------+  
|                        WINDOWS HOST (LOCAL / VPS)                       |  
|                                                                         |  
|  \+---------------------------+              \+------------------------+  |  
|  |     METATRADER 5          |  Loopback    |     PYTHON PROCESS     |  |  
|  | (Terminal & Execution Engine)| \<---------\> | (Strategy & Local ETL) |  |  
|  \+---------------------------+  (127.0.0.1)  \+------------------------+  |  
|                ^                                         |              |  
|                |                                         v              |  
|                | (TCP/IP WAN)                       \+----------+        |  
|                v                                    |  SQLite  |        |  
|       \+------------------+                          \+----------+        |  
|       |  Broker Server   |                                              |  
|       \+------------------+                                              |  
\+-------------------------------------------------------------------------+

* **Componentes**: Una única instancia del terminal MetaTrader 5 (MT5), un entorno de ejecución Python (versiones 3.8 a 3.10) 2 y una base de datos local ligera SQLite para almacenamiento de configuraciones y datos históricos de soporte.4  
* **Flujo de Datos**: Las cotizaciones de mercado en tiempo real ingresan desde el servidor del broker al terminal MT5. El script de Python las extrae mediante la API oficial de MetaQuotes o a través de un puente de comunicación interproceso local en el bucle de retorno (*loopback* 127.0.0.1).5 Python procesa la lógica de la estrategia, toma la decisión de ejecución y envía la orden de vuelta al terminal de manera síncrona. Finalmente, el terminal procesa la transacción hacia la pasarela del broker.  
* **Latencias**: Al operar dentro del mismo bus de memoria y del bucle de red interna, la latencia de comunicación entre procesos oscila entre ![][image1] y ![][image2].6 La latencia total de ejecución (el viaje completo del mensaje hasta el broker) está supeditada al ping de red de la WAN hacia el servidor de corretaje, oscilando típicamente entre ![][image3] y ![][image4] si el VPS está ubicado en el mismo centro de datos del broker.7  
* **Costos**: El costo operativo de esta infraestructura es mínimo, situándose en un rango de ![][image5] (en hardware local) a un rango de ![][image6] a ![][image7] por un VPS Windows Server básico con especificaciones de bajo perfil (2 vCPUs y 4 GB de RAM).2

### **Arquitectura Intermedia (Híbrida VPS / Wine-Docker)**

Este diseño desacopla el análisis estadístico avanzado de la ejecución de órdenes mercantiles, permitiendo desplegar la lógica predictiva en entornos Linux nativos, mientras que la ejecución se mantiene en contenedores de MetaTrader virtualizados.8

\+------------------------------------+         \+------------------------------------+  
|         LINUX VPS (DOCKER)         |         |         ANALYTICS ENGINE           |  
|                                    |         |                                    |  
|  \+------------------------------+  |         |  \+------------------------------+  |  
|  |     WINE CONTAINER POD       |  |         |  |        PYTHON PROCESS        |  |  
|  |                              |  |         |  | (ML/DL Models & PyTorch Host)|  |  
|  |  \+------------------------+  |  |         |  \+------------------------------+  |  
|  |  |   METATRADER 5 (Wine)  |  |  |         |                 |                  |  
|  |  \+------------------------+  |  |  TCP    |                 v                  |  
|  |               ^              |  |\<-------\>|  \+------------------------------+  |  
|  |               | (RPyC Port   |  | (8001 / |  |      POSTGRESQL DATABASE     |  |  
|  |  \+------------------------+  |  |  1234\)  |  \+------------------------------+  |  
|  |  | RPyC Classic Server    |  |  |         |                                    |  
|  |  \+------------------------+  |  |         \+------------------------------------+  
|  \+------------------------------+  |                                               
\+------------------------------------+                                             

* **Componentes**: Un servidor Linux VPS que aloja un contenedor Docker basado en imágenes optimizadas como msjpq/wine-vnc:bionic o gmag11/metatrader5\_vnc.8 El contenedor inicializa un prefijo de emulación Wine configurado de forma headless a través de un servidor virtual de pantalla Xvfb e interactuable vía un cliente VNC en el puerto 3000 o 8080\.8 Dentro del prefijo Wine, se despliega el terminal MT5 junto con un servidor de llamadas a procedimientos remotos como RPyC (*Remote Python Call*) ejecutándose en los puertos estándar 1234 o 8001\.8  
* **Flujo de Datos**: El terminal de MT5 en Wine extrae datos en tiempo real y los expone mediante el servidor rpyc\_classic.exe.8 El motor analítico de Python, que corre en un contenedor Linux independiente, interactúa remotamente con las funciones nativas de MT5 a través de la librería mt5linux en el host.10 Al generarse una señal, la orden se ejecuta de forma asíncrona mediante comandos RPC dirigidos al contenedor virtualizado.  
* **Latencias**: La capa de emulación del sistema operativo y la traducción de sockets de red internos dentro del host Linux añaden una sobrecarga, ubicando la latencia de comunicación interna entre procesos en un rango de ![][image3] a ![][image4].7 Si el motor analítico se encuentra en una máquina física distinta dentro del mismo centro de datos, la latencia de red incrementa el viaje completo de datos a un rango de ![][image8] a ![][image9].7  
* **Costos**: Los costos de mantenimiento de este entorno oscilan entre ![][image10] y ![][image11], dependiendo de la escala del VPS Linux requerido para dar soporte a los entornos emulados (requisito mínimo de 4 vCPUs y 8 GB de RAM) y al almacenamiento relacional concomitante como PostgreSQL.8

### **Arquitectura Avanzada (Enterprise Event-Driven Cloud)**

Orientada a instituciones financieras y empresas de corretaje propietarias (*prop firms*) que administran cientos de cuentas de trading simultáneamente y requieren una alta tolerancia a fallos, procesamiento paralelo asíncrono y almacenamiento a gran escala.9

\+-----------------------------------------------------------------------------------------------------+  
|                                      KUBERNETES / K3S CLUSTER                                       |  
|                                                                                                     |  
|   \+---------------------+      \+-------------------------+      \+-------------------------------+   |  
|   |    MT5 EXECUTION    |      |      MESSAGE BROKER     |      |       INFERENCE ENGINE        |   |  
|   |    PODS (x10-x100)  |      |   (Apache Kafka / RMQ)  |      |         (Python Pods)         |   |  
|   |                     |      |                         |      |                               |   |  
|   |     |====\> | \- tick\_stream\_topic     |====\> | \- Feature Store Read (Feast)  |   |  
|   | | \<====| \- order\_execution\_topic | \<====| \- Deep Learning Model Predict |   |  
|   \+---------------------+      \+-------------------------+      \+-------------------------------+   |  
|                                                                                 |                   |  
|                                                \+--------------------------------+                   |  
|                                                v                                                    |  
|                               \+---------------------------------+                                   |  
|                               |       DATA & ML PIPELINE        |                                   |  
|                               |                                 |                                   |  
|                               | \- Redis (Active P\&L & Margins)  |                                   |  
|                               | \- TimescaleDB (Ticks & Candles) |                                   |  
|                               | \- MLflow Registry & Airflow     |                                   |  
|                               \+---------------------------------+                                   |  
\+-----------------------------------------------------------------------------------------------------+

* **Componentes**: Un clúster de Kubernetes (o la distribución ligera K3s) distribuido en zonas de disponibilidad múltiple de AWS o Google Cloud.8 Aloja múltiples Pods de ejecución de MT5 aislados 8; un clúster distribuido de mensajería asíncrona de alto rendimiento como Apache Kafka para la publicación de eventos de mercado y ordenamiento de ejecuciones 9; una base de datos de series temporales TimescaleDB para datos históricos masivos 14; una caché distribuida en memoria Redis para persistencia de estados de cuenta calientes y verificación de límites de pérdida diaria y drawdown en tiempo real 12; y servidores de orquestación analítica como MLflow para registro de modelos y Feast como Feature Store centralizado.8  
* **Flujo de Datos**: Los Pods de MT5 capturan cotizaciones por milisegundos y las inyectan en paralelo al topic tick\_stream de Kafka.9 Diversos microservicios independientes se suscriben al flujo: el motor de ingesta de TimescaleDB guarda las series temporales, mientras que los modelos de aprendizaje profundo en PyTorch procesan las señales basándose en las características suministradas por Feast.15 Al generarse una señal de trading, esta se envía al topic de Kafka order\_execution. El Pod de ejecución correspondiente a la cuenta específica consume la señal y procesa la orden a través de su API nativa de MT5.  
* **Latencias**: Al priorizar el desacoplamiento masivo, la resiliencia de red y la escalabilidad horizontal por encima de la velocidad pura, la latencia interna introducida por las colas de mensajes y los ruteos de red de Kubernetes eleva el tiempo total de procesamiento interno a un rango de ![][image4] a ![][image12].7 Esto es apto para estrategias intradiarias y swing trading, pero inadecuado para arbitraje de latencia ultra-baja (HFT).7  
* **Costos**: Los presupuestos de infraestructura para esta arquitectura empresarial e institucional se sitúan entre ![][image13] y más de ![][image14], dependiendo del número de instancias de cómputo con aceleración GPU/CPU para entrenamiento de modelos, el tráfico de datos y la redundancia requerida en la nube.

## **Análisis Comparativo de Bridges de Comunicación MT5 ↔ Python**

Para coordinar la lógica de Python y las capacidades operativas de MT5, es fundamental analizar las distintas alternativas de comunicación inter-proceso (IPC) e inter-red.5

| Bridge | Latencia Interna | Confiabilidad / Resiliencia | Complejidad de Implementación | Dependencia de DLLs | Caso de Uso Recomendado |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **API Oficial (MetaTrader5)** | **![][image1]** (Windows nativo) 7 | **Alta**. Mantenido oficialmente por MetaQuotes.9 | **Baja**. Integración directa a través de pip install MetaTrader5.11 | No expone DLLs externas de terceros directamente; encapsula funciones nativas del terminal.11 | Sistemas de trading mono-cuenta desplegados localmente en sistemas operativos Windows.1 |
| **ZeroMQ (ZMQ)** | **![][image1]** (TCP/IPC local) 20 | **Alta**. Arquitectura robusta sin broker intermediario que gestiona automáticamente las reconexiones.13 | **Alta**. Requiere programar sockets en MQL5 y controladores avanzados en Python.20 | **Sí**. Requiere importar libsodium.dll y libzmq.dll en el directorio de librerías de MT5.21 | Sistemas distribuidos de alto volumen de datos cruzados y ejecución multi-terminal.1 |
| **WebSockets** | **![][image15]** 22 | **Media-Alta**. Sujeto a pérdidas de red, requiere lógica manual de latido (*heartbeat*) y reconexiones.22 | **Alta**. MQL5 nativo requiere llamadas complejas a SocketCreate y frameworks asíncronos.23 | No estrictamente necesario si se utilizan las funciones de red nativas de MQL5.24 | Streaming de datos en tiempo real directo desde MT5 hacia dashboards web o microservicios asíncronos.23 |
| **REST API** | **![][image16]** 22 | **Media**. Vulnerable a bloqueos por timeouts HTTP y límites de tasa (*rate limiting*) del servidor de red.27 | **Baja**. Protocolo estándar Request-Response fácil de programar.22 | **No**. Utiliza el sandbox HTTP estándar a través de la función nativa WebRequest de MQL5.28 | Backfill histórico de datos y ejecución de órdenes de baja velocidad (marcos temporales superiores).7 |
| **Named Pipes** | **![][image1]** 30 | **Alta**. Muy estable en entornos dedicados locales sin sobrecarga de red.1 | **Alta**. Exige la manipulación directa de la API de Windows dentro de MQL5.31 | **Sí**. Requiere importar librerías del sistema operativo (kernel32.dll).31 | Co-locación de sistemas en Windows de muy baja latencia que rechazan el uso de protocolos de red TCP.1 |
| **Shared Files** | **![][image17]** (con SSD/RAM Disk) 30 | **Media**. Puede generar conflictos de bloqueo de lectura/escritura de archivos (*race conditions*). | **Media**. Implementación sencilla mediante el uso compartido del directorio común de MT5.30 | **No**. Solución completamente sandbox sin DLLs externas que funciona en múltiples plataformas.30 | Integraciones básicas locales donde las políticas de seguridad de MT5 prohíben estrictamente el uso de DLLs.1 |

La implementación de Named Pipes a través de la carga directa de la librería dinámica de Windows kernel32.dll (CreateNamedPipeW, ConnectNamedPipe, ReadFile, WriteFile, CreateFileW) destaca por su velocidad en arquitecturas Windows locales.31 No obstante, presenta riesgos críticos de bloqueo: si se configura en modo de lectura/escritura síncrono clásico, el terminal de MetaTrader se colgará de forma indefinida en espera de una respuesta por parte del hilo externo de Python, perdiendo ticks y congelando la gestión de órdenes en momentos de volatilidad extrema de mercado.34 Por ello, se vuelve un requisito mandatorio el desarrollo estructurado bajo llamadas asíncronas utilizando la estructura de control OVERLAPPED nativa de la API de Windows, lo que incrementa notablemente la complejidad del código MQL5.33

### **Código de Ejemplo: ZeroMQ Bridge en Python (PUB/SUB y REQ/REP)**

Esta clase en Python gestiona una conexión bidireccional asíncrona robusta con MetaTrader 5 utilizando la librería de sockets de alto rendimiento ZeroMQ.20

Python  
import zmq  
import json  
import threading  
import time

class MT5ZeroMQBridge:  
    def \_\_init\_\_(self, req\_port: int \= 5555, sub\_port: int \= 5556, host: str \= "127.0.0.1"):  
        self.context \= zmq.Context()  
        self.host \= host  
          
        \# Socket REQ/REP para el envío de comandos (Ejecución de órdenes)  
        self.req\_socket \= self.context.socket(zmq.REQ)  
        self.req\_socket.connect(f"tcp://{self.host}:{req\_port}")  
        self.req\_lock \= threading.Lock()  
          
        \# Socket SUB para recibir cotizaciones en tiempo real  
        self.sub\_socket \= self.context.socket(zmq.SUB)  
        self.sub\_socket.connect(f"tcp://{self.host}:{sub\_port}")  
        self.sub\_socket.setsockopt\_string(zmq.SUBSCRIBE, "")  \# Suscribirse a todos los símbolos  
          
        self.running \= False  
        self.tick\_thread \= None

    def start\_market\_data\_stream((self, callback\_func)):  
        """Inicia el hilo de escucha asíncrona para cotizaciones de mercado."""  
        self.running \= True  
        self.tick\_thread \= threading.Thread(target=self.\_listen\_ticks, args=(callback\_func,), daemon=True)  
        self.tick\_thread.start()

    def \_listen\_ticks(self, callback\_func):  
        while self.running:  
            try:  
                \# Lectura no bloqueante para evitar colgar el hilo si no hay ticks  
                if self.sub\_socket.poll(timeout=1000, flags=zmq.POLLIN):  
                    message \= self.sub\_socket.recv\_string()  
                    data \= json.loads(message)  
                    callback\_func(data)  
            except zmq.ZMQError as e:  
                print(f" Error en canal de cotizaciones: {e}")  
                time.sleep(1)

    def send\_order(self, action: str, symbol: str, order\_type: int, lots: float, sl: float \= 0.0, tp: float \= 0.0) \-\> dict:  
        """Envía de forma segura un comando de ejecución de orden al bridge del lado de MT5."""  
        payload \= {  
            "\_action": action,      \# OPEN, CLOSE, MODIFY   
            "\_symbol": symbol,  
            "\_type": order\_type,    \# 0 \= Buy, 1 \= Sell   
            "\_lots": lots,  
            "\_SL": sl,  
            "\_TP": tp,  
            "\_magic": 987654,  
            "\_ticket": 0  
        }  
          
        \# Sincronización del socket REQ/REP para evitar condiciones de carrera multi-hilo  
        with self.req\_lock:  
            try:  
                self.req\_socket.send\_string(json.dumps(payload))  
                  
                \# Monitoreo de respuesta con poller para evitar bloqueos indefinidos si MT5 se cuelga  
                poller \= zmq.Poller()  
                poller.register(self.req\_socket, zmq.POLLIN)  
                if poller.poll(timeout=5000):  \# Timeout de 5 segundos  
                    response\_str \= self.req\_socket.recv\_string()  
                    return json.loads(response\_str)  
                else:  
                    self.req\_socket.close()  \# Reiniciar socket en caso de fallo crítico  
                    self.req\_socket \= self.context.socket(zmq.REQ)  
                    self.req\_socket.connect(f"tcp://{self.host}:5555")  
                    return {"\_response": "ERROR", "\_comment": "Timeout de comunicación en pasarela de ejecución"}  
            except zmq.ZMQError as e:  
                return {"\_response": "ERROR", "\_comment": f"Fallo físico en transporte de red: {e}"}

    def close(self):  
        self.running \= False  
        if self.tick\_thread:  
            self.tick\_thread.join()  
        self.req\_socket.close()  
        self.sub\_socket.close()  
        self.context.term()

### **Código de Ejemplo: Integración de Envío por Archivo Común en MQL5**

Este indicador de MetaTrader utiliza el directorio común (FILE\_COMMON) compartido globalmente por el sistema de archivos del terminal (\\Terminal\\Common\\Files).30 Esto elimina la necesidad de habilitar el uso de DLLs externas de terceros en el terminal y garantiza la portabilidad del código.30

Fragmento de código  
//+------------------------------------------------------------------+  
//|                                              SafeFileBridge.mq5  |  
//|                        Copyright 2026, Quant Systems Architect  |  
//+------------------------------------------------------------------+  
\#property copyright "Copyright 2026"  
\#property version   "1.00"  
\#property indicator\_chart\_window

// Entrada del indicador  
input string InpFileName \= "live\_ticks.csv"; // Nombre del archivo común

int file\_handle \= INVALID\_HANDLE;  
datetime last\_write\_time \= 0;

//+------------------------------------------------------------------+  
//| Custom indicator initialization function                         |  
//+------------------------------------------------------------------+  
int OnInit()  
{  
   // Creación e inicialización del archivo compartido de lectura común  
   // FILE\_COMMON sitúa el archivo en Terminal/Common/Files   
   file\_handle \= FileOpen(InpFileName, FILE\_WRITE|FILE\_CSV|FILE\_COMMON|FILE\_SHARE\_READ|FILE\_ANSI, ",");  
   if(file\_handle \== INVALID\_HANDLE)  
   {  
      Print("Fallo al inicializar el archivo compartido. Código de error: ", GetLastError());  
      return(INIT\_FAILED);  
   }  
     
   // Escribir cabecera del archivo de ticks  
   FileWrite(file\_handle, "timestamp", "symbol", "bid", "ask", "volume");  
   FileFlush(file\_handle);  
     
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
   MqlTick last\_tick;  
   if(SymbolInfoTick(Symbol(), last\_tick))  
   {  
      // Validar que no estemos repitiendo ticks en la misma unidad de milisegundo  
      if(last\_tick.time\_msc\!= last\_write\_time)  
      {  
         // Escribir estructura de tick formateada de forma segura para Python  
         FileWrite(file\_handle,   
                   IntegerToString(last\_tick.time\_msc),   
                   Symbol(),   
                   DoubleToString(last\_tick.bid, \_Digits),   
                   DoubleToString(last\_tick.ask, \_Digits),   
                   IntegerToString(last\_tick.volume));  
           
         // Forzar el volcado físico del buffer en disco duro o unidad RAM Virtualizada  
         FileFlush(file\_handle);  
         last\_write\_time \= (datetime)last\_tick.time\_msc;  
      }  
   }  
   return(rates\_total);  
}

//+------------------------------------------------------------------+  
//| Indicator deinitialization function                              |  
//+------------------------------------------------------------------+  
void OnDeinit(const int reason)  
{  
   if(file\_handle\!= INVALID\_HANDLE)  
   {  
      FileClose(file\_handle);  
   }  
}

## **Almacenamiento de Datos de Trading**

El diseño de un repositorio de almacenamiento para trading exige segmentar las bases de datos de acuerdo con su velocidad de escritura masiva simultánea, latencia en lecturas analíticas y capacidad de compresión volumétrica.4

| Base de Datos | Tipo | Rendimiento de Escritura (Ticks) | Latencia de Lectura (Consultas de Análisis) | Complejidad de Escalabilidad | Caso de Uso Principal |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **SQLite** | Relacional local basado en archivos. | Bajo (![][image18] bajo ACID estándar). | Baja en volúmenes pequeños, inaceptable para conjuntos masivos. | Muy Alta (Incompatible con entornos distribuidos). | Caching local de señales, almacenamiento de configuraciones del bot y prototipos rápidos.4 |
| **PostgreSQL** | Relacional clásico. | Medio (![][image19] sin optimizaciones). | Media-Alta (Requiere índices balanceados complejos para series de tiempo). | Media (Soporta la replicación maestro-esclavo y particionamiento manual). | Almacenamiento de perfiles de usuario, balance de cuentas, estados de órdenes e información estática.12 |
| **TimescaleDB** | Series temporales relacionales (extensión de Postgres). | Muy Alto (![][image20] con particiones nativas).15 | Muy Baja (Optimizado mediante *Hypertables* y agregaciones de tiempo continuas).14 | Baja (Mantiene el ecosistema Postgres clásico y la sintaxis SQL estándar).4 | Almacenamiento masivo de flujos históricos de ticks en crudo y análisis de velas de múltiples horizontes temporales.4 |
| **InfluxDB** | NoSQL de series temporales puro. | Extremo (![][image21]). | Baja en el horizonte temporal caliente inmediato, degradada en horizontes fríos. | Alta (La integración de metadatos relacionales es deficiente). | Métricas de telemetría de red, curvas de patrimonio continuo en tiempo real (*equity*) y logs del sistema.12 |
| **BigQuery** | Data Warehouse serverless en la nube. | Bajo para streaming de milisegundos, optimizado para cargas por lotes (*batch*). | Alta para consultas operativas puntuales, extremadamente rápida para agregaciones de petabytes. | Ninguna (Escalabilidad completamente autogestionada por Google Cloud). | Backtesting pesado de portfolios multiactivo de varios años y entrenamiento offline de modelos predictivos. |
| **Firebase / Firestore** | Base de datos NoSQL de documentos en tiempo real. | Bajo-Medio. | Muy Baja para actualizaciones de interfaz gracias a la sincronización activa de sockets de datos. | Media-Baja (Los costos escalan rápidamente con el número de lecturas/escrituras). | Sincronización en vivo del estado inmediato de posiciones abiertas del bot con dashboards web de visualización cliente. |

### **Esquemas de Datos Recomendados (TimescaleDB)**

A continuación, se define el esquema físico de base de datos optimizado para el almacenamiento histórico de ticks, diseñando vistas materializadas de agregación continua para construir velas de 1 minuto y de forma dinámica a intervalos mayores.14

SQL  
\-- Habilitar la extensión espacial y de series temporales de TimescaleDB  
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

\-- 1\. Tabla para ticks de mercado financieros  
CREATE TABLE tick\_data (  
    time TIMESTAMPTZ NOT NULL,  
    symbol VARCHAR(12) NOT NULL,  
    bid NUMERIC(12, 5) NOT NULL,  
    ask NUMERIC(12, 5) NOT NULL,  
    volume DOUBLE PRECISION NOT NULL  
);

\-- Convertir la tabla en un Hypertable optimizado para series temporales  
\-- Particionado automático de datos por marcas de tiempo en bruto \[14, 37\]  
SELECT create\_hypertable('tick\_data', 'time');

\-- Crear índices balanceados compuestos para acelerar búsquedas  
CREATE INDEX idx\_symbol\_time ON tick\_data (symbol, time DESC);

\-- 2\. Materialized View de Agregación Continua para generar velas de un minuto  
\-- Este modelo calcula de manera incremental y materializa en disco los datos reduciendo la carga de CPU \[4, 37\]  
CREATE MATERIALIZED VIEW ohlcv\_1m\_cagg  
WITH (timescaledb.continuous, timescaledb.materialized\_only \= false) AS  
SELECT   
    time\_bucket('1 minute', time) AS bucket, \-- Agrupación temporal en intervalos de 60 segundos \[14, 38\]  
    symbol,  
    FIRST((bid \+ ask) / 2, time) AS open\_price, \-- Determinación del precio de apertura por marca de tiempo \[14, 38\]  
    MAX(ask) AS high\_price,  
    MIN(bid) AS low\_price,  
    LAST((bid \+ ask) / 2, time) AS close\_price, \-- Determinación del precio de cierre \[14, 38\]  
    SUM(volume) AS total\_volume  
FROM tick\_data  
GROUP BY bucket, symbol;

\-- 3\. Configuración de la política de actualización en segundo plano  
\-- Garantiza que las modificaciones tardías por latencia de red se reconcilien \[4, 37\]  
SELECT add\_continuous\_aggregate\_policy('ohlcv\_1m\_cagg',  
    start\_offset \=\> INTERVAL '2 hours', \-- Ventana hacia atrás para recalcular posibles desconexiones \[37\]  
    end\_offset \=\> INTERVAL '1 minute',    \-- Retraso en caliente mínimo \[37\]  
    schedule\_interval \=\> INTERVAL '1 minute'); \-- Frecuencia física de corrida del motor \[37\]

## **Pipeline de Aprendizaje Automático (ML) Aplicado**

Un pipeline robusto de Machine Learning para trading debe neutralizar los riesgos de fuga de datos en el tiempo (*data leakage*), el sesgo de entorno de entrenamiento frente a producción (*training-serving skew*) y la rápida obsolescencia de modelos por cambio de régimen del mercado.16

\+-------------------------------------------------------------------------------------------------------+  
|                                      PIPELINE DE MACHINE LEARNING                                     |  
|                                                                                                       |  
|  \+--------------------+     \+------------------------+     \+--------------------+     \+-------------+  |  
|  |     ETL ENGINE     |     |   FEAST FEATURE STORE  |     |   TRAINING ENGINE  |     |  DRIFT DET. |  |  
|  |                    |     |                        |     |                    |     |             |  |  
|  | \- Timescale Pull   |===\> | \- Offline (Parquet)    |===\> | \- PyTorch / XGBoost|===\> | \- KS-Test   |  |  
|  | \- Strict UTC Align |     | \- Online (Redis / DB)  |     | \- MLflow Registry  |     | \- PSI Calc  |  |  
|  \+--------------------+     \+------------------------+     \+--------------------+     \+-------------+  |  
|           ^                             ^                                                    |         |  
|           |                             \+----------------- (Automated Re-train Trigger) \<----+         |  
|           |                                                                                            |  
|           \+--------------------------- (Real-time Features Push) \<-------------------------------------+  |  
\+-------------------------------------------------------------------------------------------------------+

### **Ingesta y ETL (Extracción, Transformación, Carga)**

El flujo se inicia con la consulta incremental de series temporales de la base de datos.15 Es crítico estructurar las transformaciones de datos para evitar desalineaciones horarias debidas al desfase del servidor del broker, forzando la conversión explícita a marcas de tiempo con hora universal coordinada (UTC) pura antes de procesar los datos de entrada.27

### **Feature Store (Feast)**

El Feature Store actúa como una pasarela unificada de datos estructurados entre las fases de entrenamiento y de inferencia.16

* **Evitar el Training-Serving Skew**: Almacena las características transformadas en bruto empleando una definición unificada, asegurando que las funciones para normalizar precios consuman exactamente la misma base de código lógica y física en producción y en entrenamiento.16 Feast utiliza un modelo de empuje (*push model*) de datos hacia el almacén en caliente (*online store*) para minimizar la latencia de recuperación durante la inferencia en producción.17  
* **Puntos de Unión en el Tiempo (Point-in-Time Joins)**: Feast calcula uniones históricas temporales exactas, asegurando que no exista fuga de información en los modelos de entrenamiento mediante la eliminación de cualquier actualización de datos ocurrida después de la marca de tiempo de la decisión teórica analizada.16  
* **Motores Online y Offline**: El almacén secundario (*offline store*) utiliza formatos de compresión masiva como Parquet, BigQuery o Snowflake para entrenamiento estadístico pesado.17 El almacén de baja latencia (*online store*) se despliega sobre memorias en caché caliente en memoria como Redis o bases de datos de alto rendimiento como PostgreSQL para servir vectores en milisegundos.17

### **Entrenamiento y Re-entrenamiento Automático**

Los scripts de entrenamiento generan modelos optimizados basados en XGBoost, PyTorch u ONNX.16 El ciclo de entrenamiento se registra de manera centralizada en un servidor MLflow.8 El re-entrenamiento automatizado es coordinado por planificadores de tareas como Apache Airflow.17 Se dispara de forma determinista mediante dos eventos específicos:

1. **Calendario Estático**: Ejecución semanal o mensual programada para incorporar la última ventana de datos consolidados para actualizar la sensibilidad de los parámetros.  
2. **Disparador Dinámico**: Ejecución bajo demanda gatillada inmediatamente al detectarse un declive pronunciado de la precisión de validación o un incremento preocupante en el error de predicción del modelo en producción.

### **Detección de Deriva (Drift Detection)**

Para monitorear la salud de los modelos estadísticos en entornos reales caracterizados por cambios continuos en la dinámica del precio, se implementan procesos automatizados de evaluación de deriva distribuidos en dos categorías:

* **Deriva de Características (Data Drift / Covariate Shift)**: Se ejecuta de manera continua sobre las características de entrada mediante pruebas estadísticas no paramétricas como la prueba de Kolmogorov-Smirnov (KS-Test) o el Índice de Estabilidad de Población (PSI). Un valor de ![][image22] para una característica clave (por ejemplo, un indicador de volatilidad media de 14 períodos) indica que la distribución actual se ha desviado significativamente de los datos utilizados en el entrenamiento, lo que invalida las predicciones operativas del modelo.  
* **Deriva de Concepto (Concept Drift)**: Ocurre cuando la relación matemática subyacente entre las características de entrada y la variable objetivo cambia. Se detecta analizando si los retornos reales del sistema divergen de los retornos esperados calculados durante las fases de optimización previas al despliegue.

### **Código de Ejemplo: Configuración de Feature Store (Feast)**

Este código define un entorno Feast básico en Python para registrar características técnicas de mercado utilizando la extensión PostgreSQL.39

Python  
\# Archivo de definición: feature\_definition.py  
from datetime import timedelta  
from feast import (  
    Entity,  
    Field,  
    FeatureView,  
    ValueType,  
)  
from feast.infra.offline\_stores.contrib.postgres\_offline\_store.postgres\_source import PostgreSQLSource  
from feast.types import Float32, String

\# 1\. Definición de la entidad principal: El Símbolo Financiero  
symbol\_entity \= Entity(  
    name="symbol",   
    join\_keys=\["symbol"\],   
    value\_type=ValueType.STRING,   
    description="Símbolo del activo negociado (e.g. EURUSD)" \[39\]  
)

\# 2\. Origen de datos offline utilizando la base de datos relacional PostgreSQL   
indicator\_source \= PostgreSQLSource(  
    name="timescaledb\_features\_source",  
    query="SELECT time AS event\_timestamp, symbol, macd\_value, rsi\_value FROM technical\_features\_table",  
    timestamp\_field="event\_timestamp",  
    created\_timestamp\_column="created\_at"  
)

\# 3\. Vista de características para el almacenamiento de baja latencia \[17, 39\]  
technical\_indicators\_view \= FeatureView(  
    name="technical\_indicators",  
    entities=\[symbol\_entity\],  
    ttl=timedelta(days=2),  \# Tiempo límite de vida útil de la característica para consultas online  
    schema=\[  
        Field(name="macd\_value", dtype=Float32),  
        Field(name="rsi\_value", dtype=Float32),  
    \],  
    online=True,  \# Habilitar persistencia de baja latencia en el almacén en caliente (Redis) \[40\]  
    source=indicator\_source,  
    tags={"category": "quantitative\_indicators"}  
)

## **Visualización de Telemetría y Dashboards de Trading**

La supervisión operativa requiere interfaces de visualización que muestren el rendimiento de los modelos, la velocidad de ejecución de las órdenes y la exposición agregada de riesgo.12

| Plataforma | Latencia de Actualización | Velocidad de Desarrollo | Capacidad de Personalización | Audiencia Objetivo |
| :---- | :---- | :---- | :---- | :---- |
| **Streamlit** | Media (![][image23] basada en sockets del framework).43 | Muy Rápida (100% Python sin necesidad de programar en HTML/JS).44 | Media (Limitada por la disposición estándar de sus componentes interactivos).45 | Analistas cuantitativos, investigadores y desarrollo de prototipos interactivos.44 |
| **Grafana** | Muy Baja (Optimizado para streaming en milisegundos de bases de series temporales).36 | Rápida (Diseño interactivo visual sin código mediante plantillas preestablecidas).36 | Alta (Ecosistema robusto de paneles especializados para Big Data y series temporales).36 | Ingenieros de infraestructura (SREs), DevOps y gestores de control de riesgo operativo en tiempo real.12 |
| **React** | Baja en Milisegundos (Utilizando WebSockets y procesamiento en el navegador cliente). | Lenta (Requiere desarrollo completo de arquitectura frontend y backend). | Extrema (Soporte absoluto para componentes a medida adaptados para mesas de trading corporativas). | Clientes finales, brokers retail de marca blanca y terminales propietarios profesionales. |
| **Looker Studio** | Alta (Actualización estática programada por horas o sobre demanda lenta). | Rápida (Ecosistema de arrastrar y soltar completamente integrado con Google Cloud). | Baja (Estructuras de informes tradicionales). | Directivos, gestores de fondos de inversión que evalúan el rendimiento consolidado de las carteras. |

### **Métricas Clave de Trading y Fórmulas Matemáticas**

Un dashboard profesional debe calcular dinámicamente indicadores clave de rendimiento (KPIs) de manera unificada empleando formulaciones estándar:

* **Sharpe Ratio (![][image24])**: Mide el rendimiento excedente esperado por unidad de riesgo total en la cartera.  
  ![][image25]  
  Donde ![][image26] representa el retorno del portafolio, ![][image27] es la tasa libre de riesgo y ![][image28] es la desviación estándar de los retornos de la cartera.  
* **Sortino Ratio (![][image29])**: Variante del Sharpe Ratio que penaliza únicamente las desviaciones de volatilidad que se encuentran por debajo del rendimiento mínimo aceptado.  
  ![][image30]  
  Donde ![][image31] es la desviación estándar ponderada de los retornos que resultan exclusivamente negativos (*Downside Deviation*).  
* **Drawdown Máximo (![][image32])**: Representa la mayor caída observada desde un pico máximo hasta el valle mínimo de la curva de equidad antes de que se registre un nuevo pico.  
  ![][image33]  
  Donde ![][image34] es el valor del pico histórico alcanzado de la curva de patrimonio y ![][image35] es el valor actual neto de la cuenta.  
* **Factor de Beneficio (Profit Factor \- ![][image36])**: Relación entre las ganancias brutas consolidadas y las pérdidas brutas registradas por las estrategias.  
  ![][image37]  
* **Latencia de Ejecución**: Lapso de tiempo transcurrido desde que el algoritmo publica una señal de ejecución de compra/venta hasta el momento preciso en que la transacción es confirmada de regreso por el broker.  
* **Deslizamiento de Ejecución (Slippage)**: Diferencia en puntos o precio neto entre la cotización solicitada por el modelo predictivo y el precio final de llenado registrado por el broker.

## **Sistema de Notificaciones, Alertas y Escalabilidad**

La resiliencia operativa depende de un sistema integrado de mensajería asíncrona capaz de enrutar advertencias e incidentes críticos de manera jerárquica.12

### **Proceso de Configuración del Bot de Telegram**

Para desplegar un canal de alerta instantáneo en Telegram, se deben ejecutar de manera estricta los siguientes pasos:

1. **Creación**: Acceder a Telegram y buscar la cuenta oficial @BotFather.48 Enviar el comando /newbot, definir un nombre para el bot y asignarle un nombre de usuario único que obligatoriamente finalice en "bot".48 Copiar la clave token generada.48  
2. **Configuración de Privacidad**: Enviar el comando /setprivacy al BotFather, seleccionar el bot creado y definir la opción en DISABLE para permitir que lea mensajes dentro de grupos de operaciones si es requerido.48 Configurar /setjoingroups en ENABLE.48  
3. **Obtención del Chat ID**: Iniciar una conversación con el bot y enviar un mensaje de texto aleatorio.48 En un navegador web, invocar la API del bot mediante la URL: https://api.telegram.org/bot\<TU\_TOKEN\_AQUÍ\>/getUpdates.48 Localizar el bloque de respuesta JSON: "chat":{"id":123456789} para identificar el Chat ID numérico privado.48  
4. **Lista Blanca en MetaTrader 5**: Abrir el terminal de MT5, navegar a *Herramientas* ![][image38] *Opciones* ![][image38] *Expert Advisors*, marcar la casilla *Permitir WebRequest para las siguientes URL* y registrar de forma explícita la dirección: https://api.telegram.org.28

### **Matriz de Escalación de Alertas**

| Severidad de Alerta | Criterio de Activación | Canal de Envío Primario | Tiempo Límite de Respuesta (SLA) | Acción del Operador / Respuesta del Sistema |
| :---- | :---- | :---- | :---- | :---- |
| **Nivel 1: Informativo** | Confirmación normal de llenado de órdenes en el mercado.28 | Canal de Telegram dedicado (\#logs-ejecucion).28 | No requiere intervención activa. | Ninguna. Registro pasivo del payload completo en la base de datos PostgreSQL de auditoría.12 |
| **Nivel 2: Advertencia (Warning)** | Pérdida máxima de capital diario alcanzado en el terminal del 5% o caída de margen de cobertura por debajo del 300%.48 | Alerta por Telegram de alta prioridad con etiqueta directa a operadores.48 | ![][image39] antes de la desactivación preventiva. | La API de riesgo externa altera inmediatamente los parámetros operativos del bot reduciendo el tamaño máximo permitido de lotes por posición.12 |
| **Nivel 3: Crítico** | Pérdida máxima permitida de la cuenta alcanzada en la mesa del 10% 48, o pérdida temporal de conexión del broker superior a 60 segundos durante horario activo de mercado. | PagerDuty (Mensaje de texto sms \+ llamada telefónica automatizada) y alertas auditivas locales de la terminal. | ![][image40] de respuesta humana. | Desconexión inmediata de los motores predictivos de Python. Envío masivo asíncrono de órdenes automáticas de liquidación total y de protección absoluta para cerrar posiciones abiertas de emergencia.12 |
| **Nivel 4: Catastrófico** | Caída física de la base de datos de producción TimescaleDB o falla crítica del sistema de orquestación en la nube (Falla del clúster de Kubernetes).51 | PagerDuty (Notificación masiva continua a todo el personal técnico de guardia en la mesa). | ![][image41] (Escalación en bucle permanente hasta confirmación humana). | Los bots ejecutores locales de MT5 asumen control offline defensivo autónomo de emergencia utilizando el modo desconectado. Ninguna nueva orden se emite hacia el mercado. Las posiciones abiertas activas pasan a monitorearse mediante stops rígidos locales preestablecidos administrados directamente en el servidor central de corretaje. |

### **Código de Ejemplo: Helper MQL5 para Alertas via WebRequest**

En MQL5, la función WebRequest es asíncrona pero bloquea los hilos si se ejecuta incorrectamente. Se resalta que **las alertas directas mediante WebRequest no pueden ejecutarse dentro de Indicadores MQL5** debido a limitaciones estrictas del entorno de aislamiento de indicadores del terminal; es obligatorio implementarlas de manera centralizada en un **Expert Advisor (EA)** o en un **Servicio en segundo plano**.29

Fragmento de código  
//+------------------------------------------------------------------+  
//|                                             TelegramNotifier.mqh |  
//|                        Copyright 2026, Quant Systems Architect  |  
//+------------------------------------------------------------------+  
\#property copyright "Copyright 2026"  
\#property link      "https://api.telegram.org"  
\#property strict

class CTelegramNotifier  
{  
private:  
    string m\_bot\_token;  
    string m\_chat\_id;

public:  
    CTelegramNotifier(const string bot\_token, const string chat\_id)  
    {  
        m\_bot\_token \= bot\_token;  
        m\_chat\_id \= chat\_id;  
    }

    bool SendAlert(const string message)  
    {  
        // El terminal requiere que https://api.telegram.org esté añadido explícitamente   
        // en Herramientas \-\> Opciones \-\> Expert Advisors \-\> Permitir WebRequest   
          
        string url \= "https://api.telegram.org/bot" \+ m\_bot\_token \+ "/sendMessage";  
          
        // Creación del payload en JSON codificado de manera segura para la API de Telegram  
        string payload \= "{\\"chat\_id\\":\\"" \+ m\_chat\_id \+ "\\",\\"text\\":\\"" \+ message \+ "\\",\\"parse\_mode\\":\\"HTML\\"}";  
          
        char post\_data;  
        StringToCharArray(payload, post\_data, 0, WHOLE\_ARRAY, CP\_UTF8);  
          
        string headers \= "Content-Type: application/json\\r\\n";  
        char result\_data;  
        string result\_headers;  
          
        // Ejecución de la solicitud HTTP POST de forma directa al servidor de Telegram  
        int http\_status \= WebRequest("POST", url, headers, 10000, post\_data, result\_data, result\_headers);  
          
        if(http\_status \== 200\)  
        {  
            return true;  
        }  
        else  
        {  
            Print(" Fallo al despachar alerta. Código HTTP: ", http\_status, ". Error del sistema: ", GetLastError());  
            return false;  
        }  
    }  
};

## **Seguridad, Resiliencia y Recuperación ante Desastres**

Un entorno de trading profesional asume que cualquier recurso físico (red, servidores, APIs de brokers) fallará inevitablemente en momentos de alta volatilidad operativa.2

### **Protección de Credenciales y Control de Accesos**

* **Encriptación de Credenciales**: Está prohibido incluir claves de API o contraseñas del broker en el código fuente. Se deben almacenar como secretos cifrados expuestos de forma controlada mediante herramientas de inyección en contenedores como AWS Secrets Manager o HashiCorp Vault.12  
* **Aislamiento de Red**: Toda comunicación saliente o entrante debe restringirse estrictamente mediante firewalls basados en listas blancas de direcciones IP corporativas específicas.12 Las redes del clúster de Kubernetes se aíslan en subredes privadas que rechazan tráfico WAN no autenticado.

### **Patrón Circuit Breaker y Reintento Resiliente**

La comunicación directa con brokers e infraestructura distribuida externa es inherentemente poco confiable.2 Para proteger al ecosistema de una degradación catastrófica por fallas en cascada se emplean técnicas de mitigación activa:

        \+----------------------------------------+  
        |                CLOSED                  | \<----+ (Success Rate Restored)  
        |          (Normal Operation)            |      |  
        \+----------------------------------------+      |  
            |                                |          |  
            | (Failure Threshold Exceeded)   |          |  
            v                                v          |  
        \+----------------------------------------+      |  
        |                  OPEN                  |      |  
        |       (Immediate Fast-Fail)            |      |  
        \+----------------------------------------+      |  
            |                                           |  
            | (Cooldown Period Ends)                    |  
            v                                           |  
        \+----------------------------------------+      |  
        |               HALF-OPEN                | \-----+  
        |         (Controlled Trials)            |  
        \+----------------------------------------+

* **State Machine**: El circuito opera por defecto en estado *Closed* (paso libre). Si el porcentaje de errores críticos de red supera un umbral parametrizado en una ventana temporal estrecha (e.g., 5 caídas consecutivas), el disyuntor cambia al estado *Open*.51 En este estado, cualquier llamada algorítmica posterior de lectura o escritura falla de forma inmediata de manera local sin intentar establecer contacto con el servicio caído, previniendo la congestión y sobrecarga.51 Después de un tiempo de enfriamiento, el disyuntor transiciona a *Half-Open* (semi-abierto), permitiendo un número de llamadas de prueba controladas. Si se completan con éxito, se cierra el circuito restableciendo la operación normal; de lo contrario, regresa de forma instantánea a *Open*.  
* **Backoff Exponencial con Jitter**: Al reintentar llamadas caídas, se evita saturar los endpoints mediante un tiempo de espera de retraso incremental calculado mediante:  
  ![][image42]  
  El *Jitter* aleatorio desincroniza las solicitudes re-enviadas concurrentemente por múltiples servicios algorítmicos evitando el "efecto rebaño" (*thundering herd*) contra los servidores del broker.2

### **Failover y Disaster Recovery (DR)**

* **Topologías Hot-Standby (Active-Passive)**: Se ejecutan de manera concurrente dos terminales idénticos de MT5 ubicados en diferentes centros de datos y proveedores de la nube (AWS y GCP). El nodo principal opera de forma activa enviando órdenes comerciales, mientras que el nodo pasivo corre en modo de solo lectura recopilando telemetrías y sincronizando datos.22 Un hilo de verificación cruzada (*heartbeat*) autónomo determina la salud de los procesos; si el nodo primario pierde conexión por más de un tiempo parametrizado, el nodo secundario asume el rol de ejecutor principal de manera automática.22  
* **Aseguramiento de Idempotencia**: En caso de reinicio por caída crítica del sistema, se deben reconciliar las órdenes abiertas comparándolas con la base de datos distribuida Redis. Cada orden despachada por Python debe portar un identificador de idempotencia único asignado al *Magic Number* o dentro del campo de comentario de la transacción en MT5 para evitar que el bot duplique posiciones de forma indeseada al reconectarse.12

### **Código de Ejemplo: Circuit Breaker y Reintento Resiliente en Python**

Este código implementa una estructura de protección asíncrona robusta que integra el patrón Circuit Breaker clásico con lógica de reintento exponencial y *Jitter* para el despacho de transacciones financieras.2

Python  
import time  
import random  
import math

class CircuitBreakerOpenException(Exception):  
    """Excepción de seguridad arrojada de inmediato si el disyuntor se encuentra en estado abierto."""  
    pass

class SafeTradeExecutor:  
    def \_\_init\_\_(self, failure\_threshold: int \= 5, recovery\_timeout: float \= 30.0):  
        self.failure\_threshold \= failure\_threshold  
        self.recovery\_timeout \= recovery\_timeout  
        self.state \= "CLOSED"  \# CLOSED, OPEN, HALF-OPEN \[13\]  
        self.failure\_count \= 0  
        self.last\_failure\_time \= 0.0

    def \_on\_failure(self):  
        self.failure\_count \+= 1  
        self.last\_failure\_time \= time.time()  
        print(f" Fallo registrado ({self.failure\_count}/{self.failure\_threshold})")  
        if self.failure\_count \>= self.failure\_threshold:  
            self.state \= "OPEN"  
            print(f" Circuito cambiado a estado OPEN. Bloqueo activo.")

    def \_on\_success(self):  
        self.failure\_count \= 0  
        self.state \= "CLOSED"

    def execute\_with\_resilience(self, trade\_func, \*args, \*\*kwargs):  
        """Envuelve la ejecución comercial con el patrón disyuntor y reintento con Jitter."""  
        current\_time \= time.time()  
          
        \# Validar si el disyuntor ha finalizado su periodo de enfriamiento en modo OPEN  
        if self.state \== "OPEN":  
            if current\_time \- self.last\_failure\_time \> self.recovery\_timeout:  
                self.state \= "HALF-OPEN"  
                print(" Entrando en modo HALF-OPEN para probar el canal...")  
            else:  
                raise CircuitBreakerOpenException("Circuito OPEN. Petición abortada localmente.")

        max\_attempts \= 3  
        base\_delay \= 1.0  \# Segundo base de retraso para el backoff exponencial   
          
        for attempt in range(max\_attempts):  
            try:  
                \# Intento de llamada a la función comercial real (e.g. Enviar orden a MT5)  
                result \= trade\_func(\*args, \*\*kwargs)  
                  
                \# En trading, respuestas de error lógicas del broker deben considerarse fallas críticas  
                if result.get("\_response") \== "ERROR":  
                    raise RuntimeWarning(f"Error lógico devuelto del broker: {result.get('\_comment')}")  
                  
                self.\_on\_success()  
                return result  
                  
            except Exception as e:  
                print(f" Intento {attempt \+ 1} fallido debido a: {e}")  
                  
                if attempt \== max\_attempts \- 1:  
                    \# Agotar los intentos locales de llamada activa  
                    self.\_on\_failure()  
                    raise e  
                  
                \# Cálculo de espera exponencial con factor Jitter para desincronizar peticiones   
                delay \= (base\_delay \* math.pow(2, attempt)) \+ random.uniform(0.1, 0.5)  
                print(f" Esperando {delay:.2f} segundos antes de reintentar...")  
                time.sleep(delay)

## **Conclusiones**

La construcción de un sistema híbrido profesional que integre MetaTrader 5 con Python y servicios cloud requiere descartar la visión monolítica y retail de la plataforma, adoptando principios de ingeniería de sistemas de alto volumen y resiliencia de nivel institucional.12  
La selección de la arquitectura y la tecnología debe basarse en un equilibrio pragmático entre latencia, confiabilidad y costos. El terminal de MetaTrader 5 debe ser aislado físicamente mediante contenedores Wine-Docker estables si se opera en la nube.8 La selección del bridge de comunicación interproceso debe responder estrictamente a la topología física elegida, donde el uso de archivos compartidos FILE\_COMMON ofrece una alternativa limpia y sin DLLs para aislar la ejecución local 30, mientras que ZeroMQ proporciona la flexibilidad asíncrona robusta necesaria para sistemas altamente distribuidos.20  
Para el almacenamiento masivo de cotizaciones y procesamiento analítico, el uso de las hypertables y las políticas de agregación continua de TimescaleDB representa el estándar tecnológico óptimo para mitigar la latencia en bases de datos relacionales.14 Asimismo, la integración del Feature Store Feast y el control estricto de derivas conceptuales y de características blindan al sistema frente a la degradación de los modelos predictivos.16 Por último, el despliegue de sistemas de alerta jerarquizados y de disyuntores lógicos asgura la continuidad operativa del capital de la firma incluso durante las condiciones de mayor volatilidad y duress de los mercados globales.13

#### **Fuentes citadas**

1. Efficient Communication Between Multiple MT5 Instances and Python for Low-Latency Data Analysis \- エキスパートアドバイザーと自動取引 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/ja/forum/483092](https://www.mql5.com/ja/forum/483092)  
2. How to Build a Crypto Trading Bot in Python — Step-by-Step Guide with Source Code, acceso: junio 28, 2026, [https://dev.to/matrixtrak/how-to-build-a-crypto-trading-bot-in-python-step-by-step-guide-with-source-code-ik9](https://dev.to/matrixtrak/how-to-build-a-crypto-trading-bot-in-python-step-by-step-guide-with-source-code-ik9)  
3. A guide to successfully install MT5 and MetaTrader5 package for Python on Linux. \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/457940](https://www.mql5.com/en/forum/457940)  
4. TimescaleDB Basics for Trading Algorithms \- Untitled Publication, acceso: junio 28, 2026, [https://siddharthqs.com/introduction-to-timescaledb-for-algorithmic-trading](https://siddharthqs.com/introduction-to-timescaledb-for-algorithmic-trading)  
5. MetaTrader 5 and Python integration: receiving and sending data \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/5691](https://www.mql5.com/en/articles/5691)  
6. MQL5 SocketConnect fails with error 4014 connecting to local TCP server \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/79786669/mql5-socketconnect-fails-with-error-4014-connecting-to-local-tcp-server](https://stackoverflow.com/questions/79786669/mql5-socketconnect-fails-with-error-4014-connecting-to-local-tcp-server)  
7. Automating TradingView Alerts with a VPS and Webhooks: Architecture, Security, and Broker Integration Guide, acceso: junio 28, 2026, [https://www.vpsforextrader.com/blog/what-is-tradingview-and-how-to-use-it/](https://www.vpsforextrader.com/blog/what-is-tradingview-and-how-to-use-it/)  
8. Use MT5 in Linux with Docker and Python | by Asc686f61 | Medium, acceso: junio 28, 2026, [https://medium.com/@asc686f61/use-mt5-in-linux-with-docker-and-python-f8a9859d65b1](https://medium.com/@asc686f61/use-mt5-in-linux-with-docker-and-python-f8a9859d65b1)  
9. Is sending trades through the API on MT5, DXtrade, or Tradelocker a practical option, or are there significant limitations to be aware of? : r/algotrading \- Reddit, acceso: junio 28, 2026, [https://www.reddit.com/r/algotrading/comments/1nw86ge/is\_sending\_trades\_through\_the\_api\_on\_mt5\_dxtrade/](https://www.reddit.com/r/algotrading/comments/1nw86ge/is_sending_trades_through_the_api_on_mt5_dxtrade/)  
10. gmag11/MetaTrader5-Docker: Docker image that runs Metatrader 5 with VNC web server, acceso: junio 28, 2026, [https://github.com/gmag11/MetaTrader5-Docker](https://github.com/gmag11/MetaTrader5-Docker)  
11. mt5linux \- PyPI, acceso: junio 28, 2026, [https://pypi.org/project/mt5linux/](https://pypi.org/project/mt5linux/)  
12. MT5 Manager API: Build a Custom Prop Firm Backend \- Softices, acceso: junio 28, 2026, [https://softices.com/blogs/mt5-manager-api-prop-firm-backend](https://softices.com/blogs/mt5-manager-api-prop-firm-backend)  
13. Retries and circuit breakers as failure policies in Python \- Reddit, acceso: junio 28, 2026, [https://www.reddit.com/r/Python/comments/1qqh7yb/retries\_and\_circuit\_breakers\_as\_failure\_policies/](https://www.reddit.com/r/Python/comments/1qqh7yb/retries_and_circuit_breakers_as_failure_policies/)  
14. Analyze financial tick data | Tiger Data Docs, acceso: junio 28, 2026, [https://www.tigerdata.com/docs/build/examples/analyze-financial-tick-data](https://www.tigerdata.com/docs/build/examples/analyze-financial-tick-data)  
15. Scaling Real-Time Tick-by-Tick Charting with TimescaleDB | by ansu jain \- Medium, acceso: junio 28, 2026, [https://medium.com/@ansujain/scaling-real-time-tick-by-tick-charting-with-timescaledb-7d29dd9034e6](https://medium.com/@ansujain/scaling-real-time-tick-by-tick-charting-with-timescaledb-7d29dd9034e6)  
16. Feast Joins the PyTorch Ecosystem: Bridging Feature Stores and Deep Learning, acceso: junio 28, 2026, [https://pytorch.org/blog/feast-joins-the-pytorch-ecosystem/](https://pytorch.org/blog/feast-joins-the-pytorch-ecosystem/)  
17. Introduction | Feast: the Open Source Feature Store, acceso: junio 28, 2026, [https://docs.feast.dev/](https://docs.feast.dev/)  
18. Why MQL Remains the Undisputed Leader for Algorithmic Trading Development | by Naveen Sanjula | Medium, acceso: junio 28, 2026, [https://medium.com/@naveensanjula/why-mql-remains-the-undisputed-leader-for-algorithmic-trading-development-468d464621b3](https://medium.com/@naveensanjula/why-mql-remains-the-undisputed-leader-for-algorithmic-trading-development-468d464621b3)  
19. Manual Mql4 Del Metaeditor | PDF | Array Data Structure \- Scribd, acceso: junio 28, 2026, [https://www.scribd.com/document/502851091/Manual-Mql4-Del-Metaeditor](https://www.scribd.com/document/502851091/Manual-Mql4-Del-Metaeditor)  
20. DarwinexLabs/tools/dwx\_zeromq\_connector/v2.0.1/README.md at master · darwinex ... \- GitHub, acceso: junio 28, 2026, [https://github.com/darwinex/DarwinexLabs/blob/master/tools/dwx\_zeromq\_connector/v2.0.1/README.md](https://github.com/darwinex/DarwinexLabs/blob/master/tools/dwx_zeromq_connector/v2.0.1/README.md)  
21. GitHub \- darwinex/dwx-zeromq-connector: Wrapper library for algorithmic trading in Python 3, providing DMA/STP access to Darwinex liquidity via a ZeroMQ-enabled MetaTrader Bridge EA., acceso: junio 28, 2026, [https://github.com/darwinex/dwx-zeromq-connector](https://github.com/darwinex/dwx-zeromq-connector)  
22. Real‑Time Forex Data with Python: WebSocket & REST API Integration — Complete Code Tutorial | by San Si wu \- Medium, acceso: junio 28, 2026, [https://medium.com/@wutainfofu/real-time-forex-data-with-python-websocket-rest-api-integration-complete-code-tutorial-240432e3992d](https://medium.com/@wutainfofu/real-time-forex-data-with-python-websocket-rest-api-integration-complete-code-tutorial-240432e3992d)  
23. polyclick/metatrader5-websocket-tickers: A solution for streaming real-time ticker updates from MetaTrader 5 over WebSockets to any server. \- GitHub, acceso: junio 28, 2026, [https://github.com/polyclick/metatrader5-websocket-tickers](https://github.com/polyclick/metatrader5-websocket-tickers)  
24. SocketConnect \- Network Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/network/socketconnect](https://www.mql5.com/en/docs/network/socketconnect)  
25. anyone have a simple example of websocket worked \- MT5 \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/497177](https://www.mql5.com/en/forum/497177)  
26. mainpclab/metatrader5-websocket-tickers: A solution for streaming real-time ticker updates from MetaTrader 5 over WebSockets to any server. \- GitHub, acceso: junio 28, 2026, [https://github.com/mainpclab/metatrader5-websocket-tickers](https://github.com/mainpclab/metatrader5-websocket-tickers)  
27. The Ultimate MT5 Data Bridge: Hybrid REST & WebSocket TraderMade Plugin, acceso: junio 28, 2026, [https://tradermade.com/tutorials/MT5-tradermade-plugin](https://tradermade.com/tutorials/MT5-tradermade-plugin)  
28. MT4 Telegram Trade Notifier (Bot API) — Deal Alerts \- expert for MetaTrader 4 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/code/68617](https://www.mql5.com/en/code/68617)  
29. Send alert on Telegram from MT5 Indicator \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/491715](https://www.mql5.com/en/forum/491715)  
30. How to use DLLs to exchange values between MQL4 programs? \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/44213422/how-to-use-dlls-to-exchange-values-between-mql4-programs](https://stackoverflow.com/questions/44213422/how-to-use-dlls-to-exchange-values-between-mql4-programs)  
31. Named Pipes Client in MQL4 and Server in C++ \- Free Trading Signals \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/132704](https://www.mql5.com/en/forum/132704)  
32. Using named pipes \- Pips \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/365812](https://www.mql5.com/en/forum/365812)  
33. Correct signature in mt5 for kernel32 import \- MT5 \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/336002](https://www.mql5.com/en/forum/336002)  
34. Named Pipe communication between two terminals \- Pips \- MQL4 and MetaTrader 4 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/153978](https://www.mql5.com/en/forum/153978)  
35. dwx-zeromq-connector/v2.0.1/python/api/DWX\_ZeroMQ\_Connector\_v2\_0\_1\_RC8.py at ... \- GitHub, acceso: junio 28, 2026, [https://github.com/darwinex/dwx-zeromq-connector/blob/master/v2.0.1/python/api/DWX\_ZeroMQ\_Connector\_v2\_0\_1\_RC8.py](https://github.com/darwinex/dwx-zeromq-connector/blob/master/v2.0.1/python/api/DWX_ZeroMQ_Connector_v2_0_1_RC8.py)  
36. Best Footprint Trading Software: 2026 Comparison \- WifiTalents, acceso: junio 28, 2026, [https://wifitalents.com/best/footprint-trading-software/](https://wifitalents.com/best/footprint-trading-software/)  
37. TimescaleDB Tutorial: Real-Time Market Data to OHLC Candles Pipeline \- TraderMade, acceso: junio 28, 2026, [https://tradermade.com/tutorials/6-steps-fx-stock-ticks-ohlc-timescaledb](https://tradermade.com/tutorials/6-steps-fx-stock-ticks-ohlc-timescaledb)  
38. Create financial-focused OHLC aggregation · Issue \#445 · timescale/timescaledb-toolkit, acceso: junio 28, 2026, [https://github.com/timescale/timescaledb-toolkit/issues/445](https://github.com/timescale/timescaledb-toolkit/issues/445)  
39. Using Feast in a Trading System: From Indicators to Feature Store | by Asc686f61 | Medium, acceso: junio 28, 2026, [https://medium.com/@asc686f61/using-feast-in-a-trading-system-from-indicators-to-feature-store-037e9cc74dba](https://medium.com/@asc686f61/using-feast-in-a-trading-system-from-indicators-to-feature-store-037e9cc74dba)  
40. Low-Latency Machine Learning Feature Store with GridGain and Feast, acceso: junio 28, 2026, [https://www.gridgain.com/docs/tutorials/vector/feast](https://www.gridgain.com/docs/tutorials/vector/feast)  
41. mql5-api · GitHub Topics, acceso: junio 28, 2026, [https://github.com/topics/mql5-api?o=desc\&s=updated](https://github.com/topics/mql5-api?o=desc&s=updated)  
42. How to Install Grafana on Ubuntu: Complete Setup & Configuration Guide \- AlexHost, acceso: junio 28, 2026, [https://alexhost.com/faq/installing-grafana-on-ubuntu/](https://alexhost.com/faq/installing-grafana-on-ubuntu/)  
43. Building a Real-Time Forex Dashboard with Streamlit and WebSocket | by Nikhil Adithyan | Data Science Collective | Medium, acceso: junio 28, 2026, [https://medium.com/data-science-collective/building-a-real-time-forex-dashboard-with-streamlit-and-websocket-56a14a985f42](https://medium.com/data-science-collective/building-a-real-time-forex-dashboard-with-streamlit-and-websocket-56a14a985f42)  
44. Sharing my stock market data dashboard built with Streamlit and yFinance \- Reddit, acceso: junio 28, 2026, [https://www.reddit.com/r/StreamlitOfficial/comments/1ir5k30/sharing\_my\_stock\_market\_data\_dashboard\_built\_with/](https://www.reddit.com/r/StreamlitOfficial/comments/1ir5k30/sharing_my_stock_market_data_dashboard_built_with/)  
45. praneethsattavaram/Stock\_Trading\_App: Stock Trading Using Streamlit in Python \- GitHub, acceso: junio 28, 2026, [https://github.com/praneethsattavaram/Stock\_Trading\_App](https://github.com/praneethsattavaram/Stock_Trading_App)  
46. Build a Real Time Stock Price Dashboard in Python (with Streamlit) \- YouTube, acceso: junio 28, 2026, [https://www.youtube.com/watch?v=n0rqiQSt8Gc](https://www.youtube.com/watch?v=n0rqiQSt8Gc)  
47. Live Stock Dashboard with Peer Analysis — Built with Streamlit (python), acceso: junio 28, 2026, [https://discuss.streamlit.io/t/live-stock-dashboard-with-peer-analysis-built-with-streamlit-python/120077](https://discuss.streamlit.io/t/live-stock-dashboard-with-peer-analysis-built-with-streamlit-python/120077)  
48. MT5 to Telegram Professional Library \- library for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/code/63587](https://www.mql5.com/en/code/63587)  
49. Telegram Alerts for MT5 | Free Download Trading Utility for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/market/product/58067](https://www.mql5.com/en/market/product/58067)  
50. MT5 to Telegram \- Professional Trading Notifications Library \- library for MetaTrader 5, acceso: junio 28, 2026, [https://www.mql5.com/en/code/63585](https://www.mql5.com/en/code/63585)  
51. The Circuit Breaker Pattern | Aerospike Documentation, acceso: junio 28, 2026, [https://aerospike.com/docs/develop/tutorials/circuit-breaker/](https://aerospike.com/docs/develop/tutorials/circuit-breaker/)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADcAAAAWCAYAAABkKwTVAAAAjUlEQVR4Xu3UIQ7CQBhE4UIRJSE1JJheoHfhHNyp4RagOQEhwWEbBKKmCQIFgreiZnzF/pkveWZH7maLwszM5rHXgwiO9KVWh5xd6E07HXK1ogc9aS1btmoa6EZL2bLV0IfOOkSQPokfdTpEMt3gSYdINvSiKy1kC6OkO/VUyRZKeqojbXWI5KAHZmbJHxiIEiAmnChMAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAAZCAYAAACsGgdbAAABl0lEQVR4Xu2UvStGURzHD0omWcisRDaDRamHWQZhUgYLJi8ZRBmQScnGIiWy2eQ/8BiYsKgnIXnPQBm8fL+d33k699fxeJ7tDudTn+79fc/v3nM698WYSCSdTMA92CJ1M9yG4/mOFLAIf5SniY4UMA/X4BacgxXJ4XTAhXXqMG3MmtIX2QGn4DqsgeVwGK7Caq9vDO7AjJc5GuABPIMj8Cg5nGQGLhn7Lm7KkZMXYhCeGNvbBTck75GsHuYkq5VsRWrSDS+8mh8te/5kEh6qjBcsqCwE+64CmZ7wU2WPcNerib7mX0IThWDPUCA7V9mb5I5lqV/hNKz0xoKU6QB8meIXORDIjlX2JLkPn57bDLqfHE7ChudApm8agj29gSyrsgfJHXXeeZWx/2WO8yMMwkFuuc6KXWRfINM7yXfQvx/PuTgfZu0qy/Nh7BfoyBh7QZOXheAk7BtVObNLlb1L7uB5zqtdVhA+brd7lP+wQnCn7uA1vDV2Ef3wXrIb+CK9fB9ZM+djbzN2jlY50m/YKP2RSCQSKYFfmwt0vCWgNfwAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAAZCAYAAACsGgdbAAABj0lEQVR4Xu2UzytEURTHTxaIEgtSdsrGzkLKj5K1LISVsrDBVv4CCyullGKr2NrJf4AFpbBRk5D8iCwQC5xv91ydOXPmMauZxf3Ut3n3c89978ybe4cokahc+jmPnG/OPqcqf7r8rHLW1PiNQrPtypUdNNTjOKQiqCe/Ic+VlUVOn3F/NTnAmeescxop7OFpzgqnQdXNcbY4g8pFsJ12OaecGQpnoSTQ4JeViknOEYW6Ic6G+BFxrZycuGZxyzIGw5xzNe6k7JdSwAmFBXV2wgF1l46zD/ww7oGzrcbArikKDhCK8e3/A2qnHHdm3Iv4yJKMnzkLnGo1l0kThYU1diID1E847tC4+B+s2RMXs5M/XQg2vr3Jphl7YM2o4w6MuxcfaVHXtZxjCvM4hEXxDonnLLjxmOPsm8Qe1E3iGs1p4HqN++WT8l+7ThZ4CGpmjYe7MO5VfATXOTWOzqWNChuLeVd1FrypW84V54ZCE+OcO3HXnCepxX7EGB4/ezeF+3fJJ4JfrUPqE4lEIlECP+hWeJC1nWP6AAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAZCAYAAACclhZ6AAAB6klEQVR4Xu2Wv0tcQRSFrzESCyUExCqWohAQtJeIWqRJIQhCwBBMmiiKAYsgCBb+aKwttEkXRAsrC7EJifkPJKIGFo2KiBgIRgmBeA4z69535+muKLKB+eBjvWfuzM64771dkUgkclOG4Fsben7CbvgIPoSd8DjRUQR8hH/gP29vcviC7Lj2caKjyMh3mEk4DdvMWFGS7zD/Fbd9mFdwAi74+gmchc+zDaAOzsBxlWlG4Tb8AJvE3asFke8wG3ANfoV/4f1ER8iY5O6vDKyEJb7egZ/gU9/Lv+0/jDXnZOED57IHVAAn99nQw7EHql7yWT5+iOsrV9k7n/WojDBrMLWmUa55mH4bXkK9uP4RO2DISLgpbshmhFmLqekibFZ5QXDigA09paa+J67/m8ktWxJu/E1KRpi1qrraZ9oKNX4lbB60oeQ2pC8VLsrsi8rS2JRw469TMmIPoy/rdnHj/PIuCDbzerbwaXJismfi+l+Y3JKRcONXfTL6O8z+wuiQ9HkBVeIap+wAqIHfTXYGT02WxqGEGxj2WZnKsp90l8pY16r6Pfys6oB5cW/Ipw4fl3w9EPcTR/NS3OK7/nU1OZzKkeTW5Zq8VH6JW4PZPlyG63DPZxz7zclgRdzNz/ejcz6PRCKRSOROOQfKPItESY0t0gAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEQAAAAZCAYAAACIA4ibAAACmElEQVR4Xu2Xy8tOURTGl9tAJBNSZl+hUERRiqkvE1JuM5eJS/kH3JMB6ssfYKyMlIEBAxmYGFFCBspt5H7JJYr12Hu9Z53n3fvs84oM7F+tzt7Ps84++6xz2mcfkUplVHaw8D+zQeOHxjY2/jGbNE5qrHbaEtf+40yWUIiJeDwVj3N8UuSIxnuNTxp7yEvxSsJYFl807jv/AfnfnLciauMasyVcG/0X0jy0VRpvo27xTuO1xufY/6ixLOb34rvGytjGAIZvg3sa11z/rsZN1+/CJpsD3pSENp+0mVHnt3hL1E+TDnZL8A6ykSNVhJekz6K+AQ1Pr0SfgnjWJjQDDyJXkBOkG8clXeAkPtEmcUnCm2Pcdp4H2nkWE4xakM1RW0g6wM3nCnKUdE9pDgMscW88psgNltOZUh5706KG2EheCivIYTYcpTkMmCdNMgKL0YJWRn6wnM6U8lLeVWnPC3GxldFgBTnEhsMW311spMCCdkfaF8e6YeRuKKczpbyct12Gi5LK7VOQhxJyjrHRBU7wb4zXUxPJ6Uwpr8szFkvzlLHGefoUBJ985Kxng3mssTO2bWJLXdv01KRzOlPKYw/Xn0qakRqrT0FS5yVB0lPX9rrxgfoGNL/RylGaDHv7pXlIzBUZzi8tqpMk+E/YSOF3h3ahMdcGW6lvQLNNXRePJH0+wI74OmkHNN6QZjyTsPv0lD67OCd3/SHOaVyIbZxknzzeA0DDp9k4G7W+IJffphlRZ1AQ6JdJxyYQul/wwb6onyEdW3boCN4Jd4K/XGzEcCLemLlt+xfTJfi3JHyRsEjhVRyFGxLGsAXuedsegIJgTuukuaGv8bjI5a1xvgXuA+PjnwsPYPkg+zfAgJVKpVKpVCp/m59huvWxeq+HVQAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAABL0lEQVR4Xu2TsUoDQRCGRyNoZbQQBbUM2Au+QDqxFI2CZcA3EAtLSScIYu8TSECsrQRLCxtbSw3aWSjq/zOzOjt3nkErIR987OzMz1423In8ZzZi468sw3e4Hge/YVj0sANb922d8iHwBLfgJKzDVfiYJRyvcNFqHpbwddpH57KEo+ygh9An3HfgMWyGWQGGZ11NTkVv4IkPqSRdZdvW76iaFZiR/H96ho0soXB2C2/gpehNRrJEoAavJT98PEtob9Ttz633Iwz5X17FgmhmLw4IB/eu9v3EGrxz+wQzvdgkHKy42vd9TSdcj28Me0eu98kLHLM6HdSFZ1aTE7jk9uRQNM8vssCQ6PDCVl6z7PN7g22rN0Wzra9xOdNSvGJkB17BXdE3pi/mY2PAgP75AKErUwKlrpkGAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHsAAAAZCAYAAAAR+1EuAAAE2UlEQVR4Xu2ZachtUxjHH+M1p2umJNfwwZD4YkhuxjKGi5C6mX00RCEkREqEL4RIQqYPbjIVSsiUUGTo4CKzMmW2ftZ63vPs/1l7n/O6XTne/aunvdf/efY6a++111rPXsesp6dnbnCsCj2drKTCtHBgsj+THaOOKWB+squTnRK088L58uD+ZCuq+F+HBtPJ15Tj5eW4QQwqPGbZ902yE8XnbJXsBctxT4ivxpPJfrQc7/Z1I6Lpw64Lvm+TvWK5vfsn+zjZVSXO+TLZH0XDvi/ad0G7dCZ6MmL9U8NvyXYp5/EG9GYor1LOme4pfz50/81eRXd2knIXn1mOXVsdhU2TvS7a9ZZfFIW42u96xyqrWdZ5iSdh22QXqjgN1DqYtz7qjyR7KJRhieWYQ4NG+YxQhl+SPS9aDe/sNdRRYH18SjTi7xbNqXVqW2c7+F5SscJAhWmBG9wsnMODlke8wzm+RUHbrmh0EmxYyhwjPvWPwzubUVaDzmbKj3R1Xk3viodXLfvXVYfwswrTgj+A08uxBi/DHaIttBz/cilfVMrKbVbXFe9sXyoUOvtx0T60fM17ydYUX41xnX28Zf8t6giQwB4u2uJkVyS7r5QZCDcnO8QDLE/9N1nOido4J9knyW5UR2LPZM9azoeOTvZO0z0ZG9vwIWA/Jdu6EVHnUcvx25cy03ztQdLwmq58at2dvbLl31Qtth37wdrbP66zPcfoivlVhcRlNrxuYDnvWKGUP0r2tOV8BjjX+ucV7YRS3r2U/VnwpXFnOYfjbLSOiWHUvGbNh7ZOI6IJ8cS8GLRniqaQOaP7UtEGWTRx3HgNblw7G3iob1uz7djZMajgvjZIAsfFvKtCYanl6+IydGbR9MsFbcdQJsnkJY2wdH5Rzok/LfhcWyaoII70Nhj9Pn07d1n9mhss64zCLj6wHNc2HZO4PaxihQusvf1turOrZT9JZQ2maj4tawxstG6SVdUAbaGUb0+2UTCfOeG5cj6w0U6fFTzkxeXcK2dqrjUS3kx2r4rWvmaz/tV0hRFD3HrqKKyf7B7RmN5qHGW5rt1EH9fZvsfAC1Oj61pvf+TkigZoe5dzXh7KTNP7Vszx+t0uDr6J4ULWFT+PukICogmGX7uH5Wv+aTZ+q+W4HdRROMhGO6GrXnzsCqrWdQ3rcZt/dctfKW2QMOm1J1U0QPPO9nJck5VNwjm7hexv1OodS0w4vIItw7lzro1+QzPdxMyRa44IZWC3SnfEaniS8oA6Cl+pYDl+cxUL+HTp6OpsRhG+U9VRYAlpyydgYKN1d43sfaT8eyg7g3Jsq2PWe/PXWl5vgQpIhDhuMxORG+YPSu2AEMcojt/nnpFuEbQuWBOJXyA6n306qsHboOson2Ke3EQ8PsL9st2KzqdXG3qdwu9pzPlFi18YaxUt/gfBoEG7Mmg8V79nfJqc6m9NDNufvnHCSNep2B9SzfTPALJ6MkumfPxx3ZmEnW1YN7MCxyMbEUP8hr2z2Ozg+MZMREbbzCgiCaOddNJZw9AqvPiXqBhg1llqeUljv4B7Zt+dLww0PisZCG9Z/o5Gwxe3eldN9r4N20gm71DeL/ho97iNn7H4w+tpQif0zBGmdnu0Z3bwFXCYij3/T8gbeuYIB6vQ09PT09PzL/MXx1ySD/S6S4EAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAZCAYAAACclhZ6AAAByUlEQVR4Xu2WzytFQRTHj4VQyEL+A1kohbUIWwsltsLCj4iykFIW2PAXYGEnsbDGRrKxooRi8fIzSURJNpxvM9c778ybi0h3MZ/69t75zJl77/Tm3neJAoHAbxnl9GkpmOA8cV443WosESxz3jjvNv2Zw58ccTZFfcjZFXXi8C2mmMyYBq5Ey6TgW8w++RezqGVS8C0m2oIan4/o5Mxw1mxdyVngtEQNTAVnnjMtnGSSc85Z4tRw2uRgHH+9mClK96Q4RZwcW19wtjn1thff9bFQY07EA8U/oDLA5AEtyX/RPi+5JNOTL9yIdV3CAbgqVUuq6YeLGdSS/Bft85IUuT24IO0AXIOqkXVOnfDfAhOHtCT/Rfu85Izcnp4sDsA1irrMOplCMR4Lmoe1ZJ7Jf/JjLRWn5M7FH652QC8mT3xvJjP+KFwsaMZ+1rST/+S1WipS5M6N+2WaRI0bXtJK2ec5lJJpnNMDFoz1inrWuq+4I7dv3Lpc4bB94DqEQ10u6jHOjqgdVsmcEE8dPC7xeUvmFUdSQObge5wDziuZx2wc95Q+Lo6JrYIte2XdDWeDc8K5tg5jePcDW2RufpwXWbE+EAgEAoF/5QOx6ZKZSOQcWgAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAZCAYAAACclhZ6AAACFklEQVR4Xu2WzUtVQRjG36ywRZG5cGMto0AwbK0k5UIEoUgIgkTURS7bRRC4UNu4MchFbly0CV20CBfRJrTwH4iiEi5+hZQoRB+LPnyeOzPe97xnyquLuML84Ie+zztnnHPPzPGKJBKJvXIOrsM/cB7WZNtFNuENeAIeh11wIzOiArgJ76v6kbibOq8ywsx6MjOiAggLKye7B8fhJdOrGJYlvvBYtu+4I27hHSbfy830wBE47esGOAE7wwBwBj6EwyrTDMJFOClu6/OslsVlcYsesw1x+Tv4Gr6CP+GhzIg8Q1J6ygV4DB7w9RJ8AS/4sfzdfmCseU2AL5wBVf+VUTgFf0n8THDialXP+GwnwjY+orJbPutVGWHWaGpNk5R5M4F6cZM8tQ3DWXHj7tqGoSD5RXFBNiPMWk1Nn8AWle+KMInmoKmrxI15Y3LLB8nP1R/JCLOLqq7zmfao6ufgtuKh1IQLm30dFqS3CidlNqeyGO8lv/C+SEbszeht3Sauz3/eUa5KaeGakIWnwbfJ11K7SLu4MddNbilIfv5/PRl9Xu03jCsSv24bNvUnwAPIjAc8cAouqJr8gN9NFuOT5BcQXv+HVRae9DWVsT6t6ttwVtU5auFvcRd+9j8fZEY4usX1VvzPl9l2FH7f49uMr+E1cVvli7g5mH2Ez+BbuOoz9r7xYvBc3OHn36OPfZ5IJBKJxH9lC36AmPavcPCgAAAAAElFTkSuQmCC>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAZCAYAAADJ9/UkAAABpUlEQVR4Xu2VvytGYRTHj1+rzY+ySFgYlNFAUcpgkHqzycQ/YLRZRTFKGQxSLBKZTCSDwR8gE4mFFIrne88595577nMHA4Pup74953zPed7nvs9z3+clqsiY8cZfMRH0FVTzhd+knnjRFRmXZWyxTcIJce05aM7VlO6gC+K+U1cr8Bk0KDEmKDbWvEliHA/yh6ycMCy+MuDyArEFH51/FHRgcnBI3DNpPOQLJgfvQefOS8GEDhODfeIdURCjNm28PvHuJW+VHKNFjyoKCtC8jDHwcNvOGyHuv5J8SXLPFsX9hHbKHgB6C+rJdcQ5Ju7vlxzHEltkg+J+SkPQNeUfojnXkQf96Lk03pl4njViX4+2FDTZnSgDu6PbrexQfM46sd/oC+A2aFZinYytjH0QuAna9SaVn/kmxf0EFO5MbH3PHvElZNG5Q8RzfvS2f5hYm7pMrCxS8TfcRvxCKZgzZXLwEvTkvJRV4vMCmIxbDGNv2kE0Kl5M46YP39LeD3XEPZ3GK4DrUi8S7ITfOr+gFf4bLPjVvBIfEepj+XI5aK6oqPg/fAPHeYKtHnicIwAAAABJRU5ErkJggg==>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHsAAAAZCAYAAAAR+1EuAAAE30lEQVR4Xu2Zach1UxTHl3mWzFMyU4ZEyZC8md4yJISQejP7aCiFTCFSInwh3kiGMn3wwVgooUTiAxm6eJFZmTLbv/Zez1nnf/c59z5Eruf8anXO/q919j377LPPXntfs4GBgYXBCSoM9LKCCrPCocn+SHa8OmaAdZNdl+z0oF0Qzv8JHky2vIr/dbhhOvn6cryqHDeIQYGLkv1WbLH4YNtkL1mu4ynx1Xg62Q+W492+akW0fdiNwfdNslcs3+8hyT5Kdm2Jc75I9nvRsO+K9m3QrpiLno5Y/8zwa7I9ynlsQK0xvyS7rZyvYvkBrtq4bX9rX7eblPv41HLsWuoobJrsddFusvyiKMTVftc7VqEN6F+ro4Mdkl2s4ixQ62Deen0oXyb7PJQZXcTsGTTKZ4cy/JzsRdFqeGevro4C8+MzohF/n2iO3j90dbaD72UVK4xUmBVo4GbhHB62POKdrYpvi6DBruF8Q8sxHCNPFH0S3tnxSxGhs/nkR/o6r6b3xcOrlv3rqEP4SYVZwR/AWeVY4wVrfCsnOzj4nEusfv1Sq+uKd/ZK6ijQ2U+K9oHla95Ntob4akzq7JMs+29XR4AE9ijRliS7OtkDpbyT5enuCA+w/Om/1XJO1MX5yT5Odos6Evsle95yPnRcsrfb7unY2JqHgP2YbLtWROO7N9kiy42hHBOlR4qmcOM1XfnE+jt7xWSPV7R479j3Nn7/zqTO9hyjL4a8RbnSmutGlvOO5Ur5w2TPWs5ngHOtn/wH7eRS3qeU/Vmw0ri7nMOJNl7H1DBqXrP2Q1s7+F27PGhbF23zUn6ulBWf232q6IIsmjgaXoOGa2cDD/Uta987dl4MKrivC5LASTHvqFBYZvm6OA2dU7RTggZocQokyeQljTCNeo5E/JnB59rfggriSI96rXI0PjtwTykrN1vWGYV9vG85rutzTOL2qIoVWBr23W9Nd/ay7CeprMGnmqVljZGN102yqhqgLZLynck2CsaL7df6NDqy8U6fFzzkJeXcK985nLveddOud83ZzH81XWHEELeeOgrrJ7tfND5vNY61XNfeone1w/E9Bl6YGn3X+v1HTqtogHZAOeflocxn+qCKOV6/26XBNzVcyLzi51F3fJNEiQ9v33L+V7PxOyzH7aKOwmE23gl99eJjV1C1vmuYj7v8q1lepXRBwqTXnlrRAM0728txTlY2CefsFn5m9XonEhMOr8DnY2dHKTtoS6V8dCgDu1W6I1bDk5SH1FFgna8Qr8tBB59OHWi1dgCjCN8Z6igwhXTlEzCy8br7RvaBUmZHUhmVY1cd896bv8HyfAtUQCLEcfu5iAxJxGOh7HNjhFEc1+eekW4ZtD6YE4nfRvS7bHxUg3eezqMsxeIGkFPrbNrLdis6S68u9DqF39OYC4sWVxhrFi3+B8EcjXZN0BZb02Z8mpzqb00N/3bRSVTASNdPscPnnhgSGLZKa38EkNWTWbLmJDbOO9OwuzWdwleB4zGtiAZvsHcWmx0c35iLyHh9bowi2sB90knnNqFVePEvUzHAV2eZ5efDfgFtZt+dFQYay0oGwpuWE1o0fHGrl/2L96y5RzJ5hzJ7G+7jvidt/EzEH95AGzphYIEws9ujA/ODVcCRKg78PyFvGFggHK7CwMDAwMDAv8yfXpWTXUupGOgAAAAASUVORK5CYII=>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAZCAYAAACclhZ6AAACJUlEQVR4Xu2WzatOURTGH1+Rj2TgjsjIV6QoAwNdXQZKBkqJohsmBgZmUkLh/gO6g2uidAfKQIqBpORjKJLIR735TBKSj4HwPK19rnXW3l5F6R3sXz29Zz1rnX3Wfs/Z+xygUqn8CzOoJ9QP6lbIiffUdmoWNZPaTL1rVfQIg7BJTErxIerDWNZQPmpOq6IHmA1rbIrzmmY9ioeoYWptyPUMpcanhljEmp5ETd5Nx6tga6fE30xmkDpOnU3xEuoktbEpIAupEeqY8zyHqafUKWoFbK0WWQxrcpS6Q02jTiQvIu8hdY+6SX2jJrYqco7i153vwP6ocSl+Rl2l+lOtjuN1Ffs/VxvOHhe32IryY/ad+hI81Ux28cXk/YnnsDq/Jvclb6fzhLxlIfYsR5fJbICd8DL4V5LfjUWwmoMxEeggH0sNRU/IWxNi6Ry12vlF5sGKTwf/fPJXOm+COxbjYTX3gx95jLzx3QVPyBtwcV/yvKa7fIYKzgTvQvIXpLhpyD8qGlTedeeVeIS88V0FT8TJ+Md6HSyvl/dvUYGa9dxOfoN2k08uFuthNduCH+kgb7zbnfHvsPiFsQnl88ZYirxA8REXz4V96ni+It8kSrxBPv6B5DVfHKK501ucp3i+i/dT11xcZC/sxObbTG/6yA5Y7kX6vdFOF3kL2820Db+GPSofYWPIe0Vdoh7ANiF5yn3WyeQybPHrelJcDpVKpVKp/Bd+ApiFnFyiadj+AAAAAElFTkSuQmCC>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAAZCAYAAACsGgdbAAACIElEQVR4Xu2VP0hXURTHT0bgIA5BKQQGRS0JCa4NgoXQ4CRE0CBNNkUIQVtDgovikq1S2CBCJYR/KlycjAaDpqaKhiT7t4gl6vn+7j297z3v/n5OgsP7wJd37vece3/nvft794lUHBzXvXHYuKraVV3zicNAk4TmxuN1JF5PcFFkSULup+qmy4EXqknVWdUR1UXVgqqLiyJjqr+qDdUllyuxreqOMRowOLbxsRjjb4HxepGusRJ91nRSEfitekDjTdUojUvkGvvu/HnVcxqDlxJq+slbVt1RPVENk8/0SvkBHM94CUieohg8k/CEDcTIDZB3IXrfyHstYZsbgS3ONQTvhjcN25aheM2Bm3jsvB4J9e/IeyX7N4k5/7wpwX/vTaNdikYh/D/OJRV5FiXUdzrvtoSnNRXzuHkG3h/nAfvtuhxVrUnabGtSkYJ61Lx1/pzqPo2bJdRdJg/jHzQ27Hf3BUX8ZOuBO+ZtboRfC/EvGhvwd7xpfFINxtgWwxbWa/KDasabETuimFyTWzQ24H/0poHkF4rZ98xKOOwZm9shYQ6OJibXZG5teI+8afCbZpPPUGzcVd1yXpvqYYxtzpUiXQMeH2f4Ivm1cSLAy+1EjQnV0xhbIa7n/1cUB3BOfVSHMT6zxr3o4QVi4OGcNVYl/8Yn4DNnBzae7Mk0XWqMxU0hxvGDNSzfQnnjtITcG9Vn1dc03RhMrKioqKgI7AEog6oABjDJOgAAAABJRU5ErkJggg==>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJkAAAAZCAYAAAAi7IxiAAAFiUlEQVR4Xu2Zach1UxTHl3kIZZbpvebxg8gQ6f1AklCmpHx4S8qQEBnK8JiSMYQPxqSUeUqGSJFMKRIJH17zkHme2b/2Xu+z7v/uc+cPLudXq3v2f6+z797nrLNHs5aWlpb/Ikeo0PKvYScVZpH9kv2d7HDNaOlhUbKzkm1a0islW3lJ7vRZNtmdKs4SS1sOrivL70Xld+3oFKDBv6k4Ii9a/o+Pky2UPGdzm/d7UvIiN1n2eT/ZxpKnrJLsK8v+bj9YLsP5TvJ/CnlHF23XZBsluyrZ98n+SrZu8bkn2Y/FD/sj2dfJvkn2Z9FeTbZi8R+Gu5Itr+IswUPwrpgH4MRreKtobuPAg/o9pC+3XNZzQYOFRXd2kLTDy90npPHZN6Sb2May7yuaEaj9H9oyom1XdA8y542i08sptJe89TWjgVpdZorYAL/+QvSIf+njQK9Bjxn5zHJ5awaN9LEhDfSeL4T0BdZbj/0rWg0Pspc0I6DlnF3RHD6cpiBbSnTHe9RBMCTT1pmGhm4QruF+yz1cjUmCjPuwOBQfXzSfc6xT0vxGnii6w/WbIe2gM5T1w4MsBq2ibbymaEwvlOusOciaWN1y/lOaIbyrwiziL/6Y8juISYJsx2SXiTZnubwrSvqcklZutd4gq83V0AmIfniQ6TAd0Tr4PdgekldjUJCBl9ePOL2Ag5OdkeyWkl4h2cnJzk22nDslTrPsw9y2xi6WP9JHLM8xI3xIzFM/SHZhslO7s0dnPZtvLPZzsi26PLqZJMhq+LDBw4IHSlqht4g61w+FtIP+qIrCVjZ6kMF71v2sMP1onGkEGQGlq31e+EeW7yP/hKJfXLQFyZ4u2tZFO7CkndcsT1McfG4u18w5Y500PTYUxB/Hh7dal8c80wwyVoOUdX3QnimacrVlnaHdV8T3dXlk0N9RUeAjwu95zQjU6gBnWvdzwuIK1JlGkP2qQoHeift0WwONxZBqfMjOoUWLHBQ0n75EHpT0RFB47NlqTDPIKMe7feeOoivXWtbZQgGu6fUU9GdVFDax7PeyZgRqdVB2tzx3xfdEyZtGkLEtU6Nj+b4FoqPFD9a1+B+eZg4ZDY3V/xrBh2nHoG2hoWAIWFSuvTLbh2tlWkHG/tIpKlrznIzuXB/W4yHtoN+oorChZb/XNSOgdThA0hF8mWZEJg2y85Jtq2LB66+LI7RLK5o+N2zvijlHBj+MPb6JoBAmeH4d9RrTCLK3rfel3V5+mVTXHuAoq0udx9TA70sVA9pGNkQ7ojm++RoZFGQc4ZF/kmYU+t3LlIF8ep0I2iUVTZ9bv7J9buycb9l/TvSRiKsX/3P2Zpoq0i/I2HjUYUN5ONluoh1WzKF8JrUR9tji3IIA03qwYlKtCR/mauxlebUWudvyCUQNynlMtEFBRl7TyQnDFqu+JjqW719LdLRBPZmf6CgsDtirpN2sXiPM1/nIx4ajEeZBwJ+zDOZ3yyUe3TDJrVUSvEG87Bq+oVmzuDNOg+I+HRua+HSC5nOHeDzDENxvFz/Cfdx/r+h8YLptAAQZ/voSdy66stiyrmeaxxV9segR6lQ7KXA4oaEMtlUiaLdVNK0fCwrdB+XIC+as1/9T6x5Ox4Ku279sHrAOVcAL/MTy0IqxjKZn2Sz40Puga0OdGFRqCl8PwxBngeTXGolGHqsfzgf7rRabYOimDNrHb1NvRZCxKj3K5uvMi2E1t2rw82HdjXyeKXM26khPHv1r1J6H84vlM1/eAb8EDIsiAgHtw2TfWt6Q/jxonOJEbrD5OsZpx1yyQyzf6/mc2U6Nfo0bFh7g6Sq2DE3H8pDW0oemXqxlOGqLmZYAE8faUU/L8DQtBloKuvxtGY09rXdV3dIyVTguamlpaWlpafl/8Q9x/9u/aXZpSwAAAABJRU5ErkJggg==>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEwAAAAWCAYAAABqgnq6AAAAxklEQVR4Xu3VPQ4BURQF4CtarQ1oiERnATRKa0GiEBIFNqBTiURjCVZhJVqdcG7mjbg386c0c77kZDJ33mtO5s2IEBH9vylyQbrhvoOckclnBRlb5OVyMyvIWCN75ISskLp9TJ6WNPRDSrcUFvaTBbKT6Nt1DNeDWUHGDLm6mZa2cTPKEP8ts/SQfsE0wp5SqPkBPCW/sBEyLphm2FMKWsw9YZZXWGVpMfOEGQtL8RB7ZAYSldX+mpGjRzJ+qzQt+5iIiKhi3jabKddyoM+xAAAAAElFTkSuQmCC>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF4AAAAWCAYAAABJ2StvAAABKUlEQVR4Xu3XsS5EQRgF4F9UGtF4Ac2K1j4AL6D0ApotkSiEjQKVTieRiETjEUSt0SARnkJDIhrh/Dt3mHtyJ+YiCnu+5GTzn5nqv5u7WTMREfnvVpBTZKaap5ETZPnjxqc+8og8I0t0Ji3tIG+Uq9qN4A45T+Zb5CKZpaUtZB85RjaR0frxwLiFB8K8m+BSyviy57kk15Zf/CGXUmbDvl58fAWxXC8F1pFdCws8qj4PajfyC871UmAVOaPOl7lNc9OCc718Ey+U5yjXp7otMlRGuIBX+73FL7TIUPHFPTR06UKfaI68u+dSyvjy1hq6dNGLNEfezXIpZfzv/2Qyz1lYaCfpnHe9ZN6rOvkBf9XEb7lnqn48MGbh7BK5QV6s+fdBRERE5G+9A6jtVgVE30bAAAAAAElFTkSuQmCC>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFYAAAAWCAYAAABaDmubAAABCklEQVR4Xu3WMU4CURAG4EEjvZWFR9AOKyuChYkFlRbGjo4LeAOO4AUoCQUNMcoRiCUnsDAaE0saCczk7cbhL9j31mbZ/F/yJ7x/CAkT9gURIiLaV6+ateZH04MZlWQLPcpe32fnr78xlfGsmUA3lbDcLvSU4FfCEm9dd5Z1n66jRKeaIXRtCYt9g57+6UXCYs9xUHcfEr645RtmqINFgUMJnzvHQd3NNDfufClhEceuy91pGlgWWEr8FXCRkMqzxaIDCct9cF1Ts3LnGAvNCMsd7F9DbCqvhYVjj29+RVjssY411gyge4czJXrU9KE70TxBRwmuZPtX7nPt3keJcJk+dncTERFR1WwA2mY8XeHHmJUAAAAASUVORK5CYII=>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAAAWCAYAAAAIAZSVAAAAlUlEQVR4Xu3WPQ5BQQBF4eenIBGNRGMD9mId9iR2QW0FItFpRaHQSBQqCucVmtuozZwvOc3cfmaaRpIkSZJ+WeSB6rCmF81zUNl29KBpDipXn050oWFsKtiYbnSgbmwq2IyetM1BdWg/dm9a5aC6fG+CTQ6qy4iutKdObKpIj450pkFsqkz7LNxpkoPqsswDSZIk/ZcPI/cSINIe99MAAAAASUVORK5CYII=>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIkAAAAWCAYAAAD0FL9fAAAAk0lEQVR4Xu3WPQ5BQQBF4eenIBGNRGMD9mId9iR2QW0FItFpRaHQSBQqCucVU7hq1ZwvOc3cfmaaRpIkSZJqtcgDqVjTi+Y5SDt60DQH1a1PJ7rQMDZVbkw3OlA3NlVuRk/a5iAV7Wf0TascpFRulE0OUhrRlfbUiU360qMjnWkQm/SjfYLuNMlBSss8kCRJkv7tA+Y1EiC0mP9eAAAAAElFTkSuQmCC>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIkAAAAWCAYAAAD0FL9fAAAAlUlEQVR4Xu3YsQ1BURxG8UshDCCxgkKrVNjCDNZgDDEGAyg1BhA2kGhJOM+L4n0WEM4vOc392lv9S5EkSZKkXzLOByl16Ew7ajUnqalNBzpRLzbpw4auNMhBSmu60ygHKS3pQZMcpLd5qT/JLAdpUerPMc1BWtGNhjlIW7pQPwf9t+qAtqcjdWOTXqqzvJdWSZIkfa0nYmsR1ju1zxwAAAAASUVORK5CYII=>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJIAAAAWCAYAAAArWsVAAAAAoUlEQVR4Xu3ZoQ3CQACF4QNB2gFIWKECW1nRLZiBNWAM0jFgACSGAUjZgARLE3hNFc9wvVQg/i/5zT176i4EAAAAAMD/K/0ASLFQd3VWs+8JGG+urqpVuW1AkqN6qpUPQIpGdWrtA5Bir96q8gEYYxuGi7TxAYixC8MFqn0AYhzUSxU+ADFO6qGWPgC/9I+QF3VTmW1AtP6LhBdtAAAAYEIftmkR1qAplfEAAAAASUVORK5CYII=>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGEAAAAZCAYAAAAhd0APAAADWElEQVR4Xu2YWahOURTHFzImSRlKKcOLoXgzPF0hvBjixSNJxowplLyYElGGvMmQkgdDZrnJ8CIPCsn4QGahZA7r/+2171l3nX3O+c53r1u0f/Xvfvu/1j53n7PO2XufQxSJRCL/DXWsLawJypumfkeq4DnrG+u36DvrLeuj8rY2ZCd0JRebyerAWizty6w9krOA9VV8ffz1Em9pRrPukRvHIRMr4jy5fu9Zs0wMHGftZvVntWINZZ1lDdNJRfiLZOlMzn9hfHhTjQfg+yJ4lou/zfgtyTLWL9WeS+HzDYG8tvJ7hrRfJ+EKV8XXKlvozCKAz+RiA6XdRtohdlK6CIvI5W82fhYjrNEM6PFrb5PxLGdYx4x3ilzfScqrZy1lHSB309VEXhHuk4vtkHY3ac9pyEjoTukiYFpC/kbjZzGRXP58G6iRKRQ+Nz8N5/GTXM505Q0W75XyLpKbhppEXhF8TN9J3qvmQiEHuWXXgpHk+lX7BGVxicLn9oTCvqY3a7/x6sj1u6m8C/QXi9CDnI8Ba9aKr3WlUUbCPKqtCB4sdljgD9tAlXyg8LndobBfxDly/YYYD5sTbDz2SRzrTin8hXwn8gOHVqs8zXBKFwLCmqFpahE8mAYxtms2UIAfl+UWhf08/Hp4w/gnWOtUGztG5I1VXiFZA60WPLYPyB3D7qRqnY6yaM96xLpL6YKHwDY8dG63Kezn8YUaT0N5lL6mZTp0YQ2wphBa7HwRNhi/VjD3Xie3MHYysRBZawIKGfKzwPR1xJqC38JqylzTCmU6DCI374VYSenjLBSvaDtYRDvWQ3IvXKGTzmINpccEQjdMFkcp/SQ/lb99yB0HW1dNmWtaoUwHv0ULcZDSMf82jc8btYC1AG/x9TZQAvx/HMd6J42HgllwY2Fd0/Rk7ZLf/cgda1wSrgAPW9yq8UXoaAMBfBEwp1rgjzIe3g/g40WmDNgV4W4t2y/ES2q8w+tFbkz6iVoint7/jxEvpPEqD+3Wqr1KPCzQhWChwQCfkXu8sIjhu1EeKMJeVl9KBvRJ/k5WeStYbyg5Nv6ivV3lhMD3FnxiaK41xIOnCRf4NLmx4g62PKbw+1BI+qLjN7anP1Qcn3z+WWZbIxKJRCKRSCQSibQYfwA2ZQ9SteixgQAAAABJRU5ErkJggg==>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGcAAAAWCAYAAADdP4KdAAABdElEQVR4Xu2XPy9EURDFj9BoRCEajcIHkNApNGqFwhfQ+BNCol1fgEZCR3QUFGpUEgkqEuED0IhE4V9EJMzk3pXZyX3Ju15EseeXnLyZM2+3OJO7+x5ACCGE/B+LoilvGmqiJ9GbaMLN6vSJzkRfoiM3I5nsiD4QwlRNN45/uBYdmv5KdGJ6ZRjhO+r0u55UoGg5HUiHrF6n6/3J08WfOo/8gqLlXKB4ORux7o69Xi0H0ScVKVpO/SfPY/0lU1u2kPZJJlWWs29qyzrSPslEQ5zxJsot59jUllUEv8cPSB4a4qw3UW4526a2rCH4bX5gGMxQ06IhznkT5ZZT9J+zibRvGc1Qa/xM06EhzntTeEY6YPVuYj0Uez6t/REa4oI3hXGkA1ZvwPVjpldeRI/OI5l0IYS74gcRnU2afjl6Fj0ln6ZvQbin13gkg13Rg+hOdBuv9whv9pZ2hKDPRZeid4TwPTp7Fe0h3D/SOCaEEEIIIaX4BjYkc1JOJ6nyAAAAAElFTkSuQmCC>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAaCAYAAACkVDyJAAABUUlEQVR4Xu2UvS8FQRTFD4mK6F40StFTirxKS+P/EAWJoBN5hWiFaDbRSfgLtBqJQkQjSokofGsQH/fmzpiZ83YWiWjsLzl5b845O3ffy84CNX/IoGhDNB55M9H3X6NL9CbaFPWKmqJ30aLoIeopF6JnWK66F91F67NQzaPFUTZh/jybwgAsa3GAMDhLgXxBff31jP4TmnVzILzAsgYHnqo7qvK/yjo48PjCKgcVaP+JTWEYlu1xELOCMNRrPWmk9ME6S+Tr06z+AvmlTKF96GnSCKzB8gOnE7e+jEs/YQxhaBm5TL1jNplJNhxbKN9UUV/PIZO7kU8mRNNsOmZRfnE/zF/mAN8YeCjaZdPxivIHp4BtyudvxPmVA32hh/wdtL/OPLlNh5BmejzmQmycizpFt7Dijfssoo7nEfa+vBJdu/VR0gD2Yddvwzo1NTX/mQ9aB2vnUbTClgAAAABJRU5ErkJggg==>

[image25]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABECAYAAAA89WlXAAACRklEQVR4Xu3du4oUQRQG4AYDwQuYaSzGYmAkJr6CgiZG+gIb+BQimCh4QRYRL+iKmZGZoCCaKIgIIuLmRgsG3k4x1UzNYVxdcbd72e+Dn65zqh7gMH2ZrgMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgbd5HPkU+R5ZryvpjewgAgGHdyo3wNTcAABjO/VRfjCykHgAAA1pK9d1UAwAwsIf1+jNyLXKv2QMAYAT6ga13J9UAAAzsQaqP1OuZmS4AAIOZ98za0RoAAAZ2KnI7cjJyumYlcrw9BACwFZUH/A9HXnaTgan3rO6VfIl8r+udzRkAANZZGcBWq8u/DJTBrZXPAACwjvLwNa/eMacHAMAG6W95ns0bVR7OSl2eMQMAYIPs66ZDWx7O9tbei8iHuv6d3d3kf0Db3IwsRm5Erk+PAgDwr/JA9i7ytKlfR6429f/SDox/EwCALeNQqvMwVOr2jdBSP2nq1vbI+T8EAIA1uNDNDmgHusnt0d62bv4Ad6mufdoDAGCdParXhciryJ5mbzWXIydyEwAAAAAAAAAAADa5K51PeAAAjFYZzvY3awAARqS8qbrU1N8iu5oaAICB5V/Ucg0AwMBWmvXByOOmPtdNBziDHADAgH50k4HsWN4Iz+vVwAYAMFL982xvZ7oAAIzGcuRNbgIAMA6LuQEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwOb0C/M4bEFR8O/dAAAAAElFTkSuQmCC>

[image26]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAaCAYAAACtv5zzAAABKklEQVR4Xu2TsUpDQRREx8pGCxvLIKS1sPALgqRLbfwJf8AfsLBMoVb5h1RC2iRqFQhRYiUIVkoUBREVM5e7T28um2LzXpEiBwZ2Z5bZZd8+YMmicUK9Ur9BH9Qz9WW8rWxxHrIyTxvql32QipR0vEkq0GzogxTq0JI9H5BzaNZ0fhI3iF+PMOvqkoiV7FDf1L3z50LK5eVcU33qM3irdtG8ZPcvH9NyG/zcjBAvOob6mz5IJXb/wjvUX/FBKlLS9SZmbzyA/u016NO9nEodR9ASWezxG8h434w3wrhF7YbxHw3qjRpDX88L9TO1AtiGFj1CT7xuMrvxE3Vo5rk5oHpmLputmXlu7vB/4ip1YbJCkBOfUVfUqcsKIfayCkH+Bzn5A1Vy2ZIFYwLKfk9SHJaOKQAAAABJRU5ErkJggg==>

[image27]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAaCAYAAABCfffNAAABKUlEQVR4Xu2UsUoDYRCERwQlSMAm1kJaC/MKIdiFtL6BpQ9gYZvC0ipVHkGs0yZFqqQwYpcqnagoiBjRWfYO78b/ApdcwCIfTDOzt8v9//IDG/47V9QL9R3pnXqkPhPeYVy8KnFDpQf3qxosgzXqq0nq8OxOg7ycwhs1NCAdeNYVPzcThI/KyDrG3IQaHVNzair+0tgA26ghNaI+Im83WZTBFrWtphLfh11wkvvIX0SFuqG+NFAeEG7WhvsHGiSwjatRZxooofsw3uC+HUcWoe+CWOFATWQPN5r4zU2X6TjNBbzIPlJ0iA7cD3gprqlX6gm+Vc/4e3lH8CYz+HtWTsc4p27FK5wx1VKzaBYeVVGsdcgJ/CWw925t2B/Y4uxoUCR7VEnNDSvxA8o1TUAIJDBcAAAAAElFTkSuQmCC>

[image28]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAaCAYAAAC3g3x9AAAAyUlEQVR4XmNgGAWjYHACfiB2B2IvNEwykAfi/3hwOkIpYcDLANFUgCT2Coj/IfFJAiDDNqCJpUDFSQag8MGmcQUDdnGCYAcDdo0gsQ/ogsSAZQyYBopAxfjQxKcA8RMgFgTiy0D8DoiFUFQAgTADqoFMUH40khgMVAPxPCBeA+UzAvF7hDQC2DAgksdNBogLcAGQGh4oWxfKpwggG7AOiHci8UkGUgyoBlLsulkMkDC8BMQvGSDhTRHAFvNkA3sGiIH66BKjgLoAABrlMJfg+404AAAAAElFTkSuQmCC>

[image29]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAaCAYAAABCfffNAAABJUlEQVR4XmNgGAVUAmpAPBOIfZHESpDYFAFWIP4HxLOBmA+I7YD4PxDXAPFnJHUUAZCBNuiCDBDxKnRBcsACBohh2ABIHORLigHIIHyWUAXALOlFl6Am6GZAWATDM1BUUAnkMWBadAtFBZWBCwPueJrEABHfCcTTgHgfEP8FYnZkReggGF0AChYzYLcEBNDFQZahi8GBHxAXoAtCQSkDdo2GDJjiV4D4NZoYHJwF4nXoglAACgJskb8BiI8i8VWB+CcQMyKJoQBYuPOgia9lwF2UgNTvYoCoeQPEE1GlMcETIGYC4g8MEM3vofQCJDXoAD2o0PkUA2MGTEPR+RSDHUB8HImvxYCwxBRJnGzwnQEST1+B+D6S+G8GSHG0GUlsFIwCGgMAtatLQtPHaNYAAAAASUVORK5CYII=>

[image30]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABCCAYAAADqrIpKAAACOklEQVR4Xu3dy2oUURAG4KOiCYigLsS1ARVviD6LLlzHF3DlBcW1ryAi4gv4BO4VXblVUMxCEMFsRCFe6tA9zJkyCSPB6YZ8H/x0V1U/QNHT010KAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPN7G/kQ+RhZ61PP3zfXAAAwsJXIrdTbSDUAAAM6E7nb1Mcie5oaAICBnYvc689PRE41MwAARuB86Ra236Vb1k7PjgEAGNpkYasORk42MwAARuBsmX2GbX9/PNT0AAAYUP0Z9E7qLaUaAICBXI9cKd0dtquR1dI9y3atvQgAYDery9GByKfImzQDAGBgdVnbrgYAYGB5QVtPNQAAA6sLW82RPAAAYBwulunSlu+2zeNC5GnKk8jjyKPIw+mlAADsVF7YvjXnebZT7ZI4bwAAdpXD5e+Pq+elqK3zbKK+kuPHNvk+vRQAgH/xqswuYV8j+5q6Wos8i3xJfQAAFuBBf7wdedEOejdK903PaqMdAAAwDpv9HHq06QEAMCLLkfu5CQAAAACMxLsy+/qO+u9SAABGYrNn5QAAGIm6oLWvEtlqYduqDwDAf5YXsVxPPM8NAAAWo13Q6nNsx5u6ehn5HFlKfQAAFqgubb8ie1P/Z3+sX1sAAGCEJnff6vFmOwAAYBwuRV5H1iOX0wwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACD7A0NhYQfE2Nx0AAAAAElFTkSuQmCC>

[image31]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAaCAYAAAC3g3x9AAAAzElEQVR4XmNgGAWjYHACfiB2B2IvNEwykAfi/3hwOkIpYcDLANFUgCT2Coj/IfFJAiDDNqCJpUDF8YGZDFjUgMIHQxAIVjBgF0cHGGp2YBNkgIh9QBdEAxlAvA9dcBkDpoEiUDE+NHEQ0AbiB0D8DIhfALE9iiwQCDOgGsgE5UcjicGAFBD/ReKjOwQObBgQyeMmEAuiSsMByLAYJD5OA4kFyAaAUsFBJD5ZANnA90DsDMTXkcRIBkZA/AaIbwGxKRDfBmJjFBWjYAQAAHvsMgzWT5jhAAAAAElFTkSuQmCC>

[image32]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAaCAYAAAANIPQdAAACPUlEQVR4Xu2WPeiIURTGHzEQJYsMJiOyWJQUgxSKhIVMUgZJLAZhUJJZScKkKJPJxCKLTRYp8pUQ+f6M8zj3/N/znv+9933/gzLcX53e957nuff9uve+B2g0Gv8zRyU+SvxOcbcvT+IxOi/7HezLf3kh8Qud773EG4lPLrdzwt1ni8RbdL7vqf1O4mfKvZKYYR2mgg3KKLFM4gjUszxokd1Q39ooCHuh2oEoOGr38gxlrcpTdF+0xBOJ26h7jAeo+16irlP7FpMO6jdjssZ66Ju/jvKFr6Vj7Q17hnynoPrcKAgLoNrxKDiGxp/EnXTk+sp1nCOxL51Tv+q0EvTdiknHSahncxSEM1BtZhQcU35IM3Od8Xyh08jXdFwH1Rc7Lcd2qG91yHvuQT2LooBxDzDG04ML2WDHXa69X2J2OucXHzPwfQz7ajfJvL3YHJxZ9HAHHwW/zh7XZudLru2nZu3GPGN81HMbi63HYyHvOQf1bIpCCVuPBjtzFyXPvQDVroRcDvpq6/E81LMiCsJZqPZP1qNvM1ZJLHX5DSm/xOVy8CdP35ooJGZB9RtRSAw9wAWoPj8KNfi/8ryGDsL/nIeVUO3ixiOUfdORH9tDPTeNCash6lujUGKaxENomea5jPxNDr1hI+fj17uY8of6Uo+VUM+JTN7KSdsEBzkNrQVZT36A1oTGRoltrs1607ysQX9IHHa68RndAzK489HLXZK1JsctsQNdXWrBNuvWL9CpPW/C3Wg0Go1GozHEH8QQvXN9mTtJAAAAAElFTkSuQmCC>

[image33]: <data:image/png;base64,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>

[image34]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAaCAYAAAAue6XIAAABvElEQVR4Xu2WzStFQRjG3y1lIclGSZGdiIWFlIVEKR8baxv+ARErZWVFFuxkJSI7yVayVaSUP8DKR/K1wfs0d65znzPnzpzbuYrur55u88wz77znnjmdI1Lh7zDBRgAdbPwGO6peNgP5YsPHqupJzELoTXVP3l4+Xciw6oTNFDSrHtgMwTbGNInxXU258ml5UY2w6QMbn7OZw3UhC6oL8kqhVeK1izIpZsEgTyhV4m4W4x7ySgW1qtlM4lrizVgOxcyNkp+Ut/SLufghMWcbvwOq+mgoB2qtsJmE658D2BD+GvnY3JUHaNDWc+n0J5oHz8MHm0nYQo9ins733PhSVRfJWZbE3WyNmBqWTtVmZJwEMq56Mex5neKJImyLu3gbja9U3eS5mBN3vRg3EhiMsCVha0IyYFYCs/YIpGFe/GtwfHwZy4YEZhG6ZdPDmPiLH4g/YzlWvbLJLIopOM0TAfgawfw+mwkgi9e+k3XVs5gnH98BeOV9FiT8YIMuNiNgvoXNBJCtZTNLjlRnbJZAo/jvUiZksQnu7jib5WBZtctmChpUd2yWE7w+29kMJIs7k5oZNgLoY6NChf/AN45ecxlzD8EGAAAAAElFTkSuQmCC>

[image35]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAaCAYAAADFTB7LAAAB2UlEQVR4Xu2WzStEURjGX/lKlrJRkp0dUcRGJElIrFiQrXwl8R/IRinWdiwspCwI+QNYKWUls7CzkgXy+T7Ovc3puefcOyajWcyvnjrze99zzr3umTtECuQfjSw8jLD4D5o1Ryw9jGq2WSZxovnKMEyp5p1lAheacZaZ4LsIUCPu2oemhWUAHqdrDvB5L8ViJl1xwYIXrXQ4mwfx11OaTZZxLIlZbIj8gjXmza41x+Rs0H/AMmBAouvF8ijRCf2aCetzmzUG6O8hVy5mHoL6cjDGWWV4v1jQjLRrusQsnLSAq96kWdSciqljjLgI90skPH93mlXNluY+cD7COT7izl8I6lMsXayIae4jf2uNqzRF1ud6ib8A1PZZEuhZY+niSaKb4czg7IS8WmNQJ9E5IbgR1JJ+XdCzztIFGn2bgWrNOUvxz5kRf80GPXMsmTIxjZdcsEC9hKX4L4LPH94QLtDTwZLZENPI7z8wLKbGjzcEtU6WYjy+ZGBeM2bVbHw3+MOemN/QT0k/Yjvwb5pnMa8OFynNIUulQtLrTlItpFcSLvAvaJXsN7nRzLLMBfhLNbDMgGxv7NfUal5YJnAm0XduThnU7LD00K3ZZfkf8D8NPqZZFCiQj3wDHeJ9ofqmEIYAAAAASUVORK5CYII=>

[image36]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAaCAYAAABLlle3AAABIUlEQVR4Xu2UPUoEQRCFX2ogrIiRwUbeQBDMjEwNjWVBNPAAegEjUQy8g4mJgRiaeABhRfAEgn/4C4paZXVLzdvpmelU+oPHdL16VM8/UPjv7IoeRd9Bb6I78g7/0sCm89vUSirYh/mn5KfyygbSvQoaOmczULeB1p/keZp6vyzDhixyQxjD6Kazod52njLh1mduXcsQo1cSOYL1lpx3HLxx582LBq6eduta+EoiCzB/j3zOT1HdiTjkQXQveg/1hWjS5SIxz+pMfJ4r3EgwB8vvkH9DdSNXyDvLE1i+57wZ0ZqrW8m9Nbn5WnTANZsNaP6DzRy2YENWuZFAPxvNH3CjC/uiJ9ibqv/ZF9FXJVFlXfQMy9+G46vo0ocKhUIhmx+tfWD2uHxpgwAAAABJRU5ErkJggg==>

[image37]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABICAYAAABLN6ksAAAIFUlEQVR4Xu3daayt1xgA4NWaWlQjKkrFGLMqIUEVNcVY0kaL8KOJmmmQhoREjeGH8YdIxBQkEkNSif6gopeYh5S0FA0aWrSqLTUUNazX962cdd7z7X32vr373HO7nyd5s9d61/rO/s65P+6bb1irFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIDd7kY1Dq5xeI2bpTEAAPaxu9c4qcYpNZ5d4zlzorlPjf+O7V92+d3onjlxgLhxTgAA6y2Kr/vlZOeDZaNAa14/fub8bvLPnKiOyokJP+riBzW+XeOTm2Ys72Nl+b/VsvMBgBuwx5XFioPLx8/Tutx7uvZuc0jXfnSNt47tv3f5WU4uW/8m/6pxesotY7dfjQQAdrk/la0FSvaU8bO/SnV0195NPpX6+Xf7T+pnUwVbmMot6oKcWMD1+T4A4AYoioPP5+SKvKTGJ8b2mWXjluyJNd4/tpt71/htjed1uSfUeFiNY8f+g2s8aGN4S6GzXT+bV7D9ouu/o8bZXT+8pmw93xC3WJu71fh1jRfXeGaXz6bOAQBYYweVnS0Q4rvu3LXjKl8/lttxK/bnXf69NX46tvN5L9vPZhVsF5eN/NQ5Pqlr5/PtC7a3de0oXmeZOgcAYM29vcZVObkifTFyWRneVG2mCpUjy9Z89D+QcmFq3rx+Nqtgu7ZsLthuN8Y1NW7aJo3y+fYFW+TPKluPuUPqL/K8HQDApJfmxAz/zolOX8z8pmw8Ixf6sVntEC89RO7WKZ/nbdfPZhVskTusa2fvrnFF159VsDXn1bh6bH+jHxhNfQcAsOa+mRPX07yCox+7tMbTun4bi/XfWvtRY7u9UHCrGvcd2/l75vUfWYZlNpo8N0wVbOfXOKfr9+NtAeHI3XFs5/Ptb4/GmndNzIlnBz/d5Zp8DgDAmrsuJ5K7jJ9n1vhLl59nVsERt0Djqtofy3Dl6ZIyFG3HdWNXjnNjLbT4ObcpwzNkLxvH4pifjXN+X4bj3zj2p743cp8tw7xe7se8FvE3+WuNCzfN2BDnEfOe2uXasf35frUM5/uHcU68IBFz+rdVZ50zALCD4j/fu47tm4z9Jq7KRP+IGofWuG0Zrsj0bySuUqwxtp12ezO2plq0kFh03r5285yY44k5sZ/EbeZ427V3fOoDACuWi5djysZiqg8pW8fDm3JiBb6WE8lzy3Butx/78bxYu+13RhmWsegj3+7bXy7KiRm+nBO7xBtyAgBYrXiTMBcvP65xwtiOJS1iC6SmFUftityqxHNj7RbedtHEbcUHdv1ZHlqG46Iw3R9imZL75+QBIvYSvVdOAgCr9ZOy+S3AW5TNRVC029uHUcgBALDDoiCLDcQ/WoaV/NtbhU2Mx1WVeHatL+T2pXzFTBzYAQDsY/P+g40tlvrxeOMRAIAddKcyv2CLZSO+m5Nz/GObePrGVAAAFnF5jd/lZCeKuXgpYadEQRcbjj+rDG90xuK0U9HvPPCFMixU+5EyPMgfG5fHGmp7I2777oSDc+IA0l46AQDW1Oll/hW/KHT+VjbmPKPGizaG/7+obZj3M+bZbhmRKQ/IiW2cnRNlWD9uO7GIb4vvl2HnhzM3zVjexWXv/lZTxzw2JwCAG67Y5H2qIMja7dU29zFtoAyr98fbr8vam4JtkXNtYqmSw7t+f+wiPyfmfD3lflXjcym3jEW+d0q+0qZgA4A1E0XEvM3Ze7E9VGgL/YYfdu1l7E3BtoxcHPX919X4UNefEvO/kpNl689dxt4em49TsAHAGoqC4OU5uWKtYIvvjoirSOeN7RDbZEUh2W5rtm27mnZcHBNv1Maiw71+7qmpH8/s5SIoi/Gp3Q8if2rX/1YZzrM9fxif3yvDZu/9HqGh/84/13hhys2S5yjYAGANrXLdt1n6K2zx3YeM7VeN/X5sqp3788benPonpv6UGD8nJ8uQP7dr9/nwirJRZMaG7/H8W9PmfKYst89pPlcFGwCsqe+UrYXBKuWCrYkXG9qt1zBVFE3189gFXfuksnn8lNSfMq9gi2f4YoHjaPfRRDEWW4xFrr/yl883It+afXiNo1Mun6uCDQDWVNzC20mzCrbnl6F4bHKR05s31t+OjB0l+vF4hu3Crj8l5s+6JTrVbq6u8a6xfVwZbn02bX57GSLexI3c8WN/lvw9CjYAWEOxy0K7JbmIXEBksSn8VWXzGm7ZrILtBWVYSqOZVyAtOpb7V3bt95Wtz7+FmH/uRK6/+tX/zI9P5KLgiwWRW6597hk/m1gyJVxUtl5xC/l3UbABwJqJdcmenJNJFHTLOqgsVrDFwruxpttlNU6ucWmNS2p8qcYV41gsOvz4MR/zQixCHGNREF0ztvuFiXORc2gZXg6ItdVe2eWPKcMaab04tkW8/BA//8ObZmxo8+IWabhllwtxfLwwEVfe2u+5p8Y7xzl5d4t83iHnFGwAsGa+mBPJI2ocObZboXDa+PnaiWgWLdhW5dVlKNIWEUXVbpGLs3BY6ivYAGCNXJsTyfllawERuw0ssltAFGwn5GRn1QVbyOc+yxE5sR+dkfpTz9Ep2ABgTcRD+f2tv1lxXTtg1O8dGs9/5WiiYGvPZk3ZkxNrLv49zkq5o8r0VcLjcwIAoLfIVatjy/BgfxR3b0ljTLtHTgAALCsKtXy7DgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACglP8BsVlwhBQQJtIAAAAASUVORK5CYII=>

[image38]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAAAU0lEQVR4XmNgGAWjYFCAvegC1AD/0AWoAWyAuAxdkBrgHBCbowsiAxMy8S0g3sdAZfAXiBnRBSkB/9EFKAUTgJgdXZBS8BtdgBrAAF1gFIwCGgIAYTgLotElupAAAAAASUVORK5CYII=>

[image39]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGkAAAAWCAYAAADD9rIuAAAAlElEQVR4Xu3WLQpCQQBF4edPUBCLYHED7sV1uCdxF5pdgQg2qxgMFsFg0uB5wXI3MAPvfHDK3DzDNI0kSZK6bZUHqseWPrTMQeUd6EXzHFTWkC50o3FsKmxKDzpRPzYVtqA37XNQPdrPwJc2Oag+/xu1y0H1mdCdjtSLTZUZ0JmuNIpNFWqfwCfNclB91nkgSZK64QfBpBIg2YJBCwAAAABJRU5ErkJggg==>

[image40]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAAAWCAYAAAA/45nkAAAAkklEQVR4Xu3VLQpCQQBF4edPUBCLYHED7sV1uCdxF5pdgQg2qxgMFsFg0uB5wXKThpl0Pjhlbp6ZppEkSdJvFnmgOtb0onkOKmtHD5rmoHL6dKILDWNTQWO60YG6samgGT1pm4PqaD/WN61yUF3fm7DJQXWN6Ep76sSminp0pDMNYlNl7bN0p0kOqmuZB5Ik6X8f/1cSICEFFtkAAAAASUVORK5CYII=>

[image41]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFkAAAAWCAYAAACrBTAWAAAAkklEQVR4Xu3VKwqCQQBFYV9BQSyCxQ24F9fhnsRdaHYFItisYjBYBINJg+cPlltnRITzwSlz6zDTakmSJP3aPA9Uz4qeNMtB5bZ0p0kOKtOjI51pEJsKjehKe+rEpkJTetAmB9XTfGYvWuag+j43ep2D6hvShXbUjk2VdelAJ+rHpi9onpAbjXNQfYs8kCTpX7wBL2MSIFhI6GYAAAAASUVORK5CYII=>

[image42]: <data:image/png;base64,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>