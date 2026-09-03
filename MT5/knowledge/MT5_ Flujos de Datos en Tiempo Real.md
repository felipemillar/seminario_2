# **Arquitectura de Flujos de Datos de Mercado en Tiempo Real en MetaTrader 5 y Python**

La implementación de flujos de datos de mercado de ultra baja latencia es uno de los mayores desafíos de ingeniería de software en el desarrollo de infraestructura para el trading cuantitativo y la microestructura de mercado.1 MetaTrader 5 se ha consolidado como un puente fundamental hacia múltiples proveedores de liquidez. Sin embargo, su diseño interno monofilar y orientado a eventos requiere el desarrollo de arquitecturas de integración híbridas para interactuar de forma eficiente con motores de análisis cuantitativo basados en Python o Rust.3 Este informe examina detalladamente el modelo de eventos nativo de MetaTrader 5, las diferencias estructurales entre tipos de datos, el acceso al libro de órdenes y los patrones de comunicación interproceso óptimos para construir tuberías de datos de alta velocidad y tolerancia a fallos.2

## **Modelo de Eventos de MetaTrader 5 para Datos en Tiempo Real**

El subsistema de ejecución de MetaTrader 5 opera bajo un paradigma estrictamente monofilar para cada programa MQL5, ya sea un Expert Advisor (EA), un indicador o un servicio.4 Esto significa que todos los eventos dirigidos a un hilo específico se procesan de manera secuencial y cronológica. La comprensión profunda de cómo se encolan, procesan o descartan estos eventos es crítica para evitar la degradación del rendimiento de ejecución durante periodos de estrés de mercado.1

| Evento MQL5 | Tipo de Datos Recibidos | Frecuencia de Activación | Garantía de Entrega | Comportamiento del Probador de Estrategias |
| :---- | :---- | :---- | :---- | :---- |
| OnTick() | Ninguno directamente; requiere llamar a SymbolInfoTick(). | Con cada cambio en Bid, Ask, Last o volumen del símbolo del gráfico.4 | No garantizada. Si el hilo está ocupado, el evento se descarta. | Simulado minuciosamente basándose en el historial de ticks reales o generados.9 |
| OnBookEvent() | Nombre del símbolo afectado (const string \&symbol). | Con cada actualización en cualquier nivel de la profundidad de mercado (DOM). | Acumulativa. Los eventos se colocan en una cola persistente de hasta \~1,000 elementos.5 | No simulado de manera fidedigna en la mayoría de agentes locales o en la nube.7 |
| OnTimer() | Ninguno.10 | Intervalo fijo configurado mediante EventSetMillisecondTimer().10 | No garantizada. Si un evento previo de temporizador está en cola, el nuevo se descarta.10 | Simulado y supeditado a la llegada efectiva de ticks del símbolo principal evaluado.7 |

### **Comportamiento del Evento OnTick y Descarte de Ticks**

El evento OnTick() constituye el núcleo de la mayoría de los Expert Advisors y se activa de manera exclusiva para el símbolo del gráfico al cual está acoplado el programa MQL5. Es crucial destacar que MetaTrader 5 no garantiza la llamada a OnTick() para cada tick individual que llega al terminal.12 Cuando el mercado experimenta una alta tasa de actualización y el hilo de ejecución del EA se encuentra ocupado computando lógica matemática o ejecutando llamadas síncronas de red, los nuevos eventos de tick entrantes no se acumulan en la cola, sino que son inmediatamente descartados por el terminal.4  
En consecuencia, el evento OnTick() no representa un flujo continuo completo, sino simplemente una notificación de cambio de estado.12 Para recuperar los ticks intermedios que se perdieron mientras el hilo principal estaba bloqueado, es necesario implementar rutinas explícitas de sincronización de datos basadas en la API de recuperación de historial.13

### **Dinámica de Cola y Suscripciones en OnBookEvent**

La profundidad de mercado o Level 2 se gestiona a través del controlador OnBookEvent(). Para que un EA o indicador comience a recibir estas notificaciones, debe suscribirse de forma explícita mediante la función MarketBookAdd().5 A diferencia de OnTick(), el terminal de MetaTrader 5 utiliza un contador de suscripciones por gráfico, lo que requiere un emparejamiento estricto entre llamadas de adición y liberación (MarketBookRelease()) al desinicializar el programa para evitar fugas de suscripción en segundo plano.  
Los eventos del DOM se encolan en una cola con capacidad aproximada para 1,000 elementos y no se descartan de forma inmediata si el hilo está ocupado.5 No obstante, si el EA monitoriza múltiples instrumentos (como en estrategias multicurrency de hasta 28 pares), el volumen masivo de actualizaciones del DOM desbordará rápidamente la cola monofilar del terminal.7 Esto da lugar a un retraso de procesamiento acumulativo que degrada significativamente la latencia operativa del sistema de trading.7

### **El Temporizador OnTimer y su Comportamiento Divergente**

El evento OnTimer() proporciona una base de tiempo controlada para tareas secundarias y latidos de control (heartbeats).4 Aunque la API permite configurar resoluciones en milisegundos mediante EventSetMillisecondTimer(), las limitaciones del programador de hilos del sistema operativo Windows impiden que el temporizador real posea una precisión inferior a los 10-16 milisegundos en condiciones normales.10  
En producción en tiempo real, el temporizador se rige por el reloj de hardware local.7 Sin embargo, en el Probador de Estrategias (Strategy Tester), este comportamiento cambia por completo: el temporizador se simula de manera virtual y se vincula de forma directa a la marca temporal de los ticks históricos del símbolo bajo prueba.7 Si existen brechas de datos o periodos de inactividad de mercado donde no se registran ticks durante varios minutos, el temporizador virtual se detiene por completo.7 Esta divergencia inhabilita el uso de lógica basada en tiempo absoluto para la gestión de cierres forzados u optimizaciones multicurrency que dependan de un paso del tiempo constante durante simulaciones históricas de agentes de optimización en la nube o granjas locales.7

## **Análisis Microestructural: Datos de Ticks vs. OHLCV**

El diseño de la base de datos de un sistema algorítmico de alta frecuencia debe justificar rigurosamente la elección entre el uso de ticks individuales o barras agregadas en formato OHLCV (Open, High, Low, Close, Volume).2

| Dimensión | Datos de Ticks Individuales | Barras Agregadas (OHLCV) |
| :---- | :---- | :---- |
| **Granularidad Temporal** | Precisión de milisegundos (time\_msc).8 | Intervalos de tiempo fijos (M1, M5, H1).17 |
| **Volumen de Datos** | Alto (![][image1] por activo).7 | Muy bajo (1,440 barras por día en gráficos M1).17 |
| **Atributos Clave** | Flags de dirección de transacción, Bid, Ask, Last.8 | Precios ponderados y volumen consolidado.17 |
| **Esfuerzo de Red** | Transmisión continua asíncrona de alta carga.20 | Solicitud discreta mediante transacciones síncronas.19 |
| **Estrategias Destino** | Scalping, Market Making, Order Flow, Arbitraje.1 | Reversión a la media, Swing Trading, Machine Learning.21 |

### **Justificación Cuantitativa de Datos de Ticks**

El uso de datos de ticks individuales es indispensable para el desarrollo de estrategias cuantitativas enfocadas en la microestructura del mercado por tres razones fundamentales:  
Primero, los ticks preservan la asimetría temporal del diferencial entre el precio de compra y venta (Bid-Ask Spread). Las barras OHLCV ocultan por completo los micro-picos de volatilidad intrabarra donde ocurren las ejecuciones de las órdenes y donde la volatilidad del spread puede desencadenar deslizamientos de precio (slippage) destructivos para modelos de scalping de alta frecuencia.1  
Segundo, la identificación de flujos de órdenes agresivos requiere el análisis de las transacciones ejecutadas en tiempo real. Esto se logra evaluando los indicadores binarios TICK\_FLAG\_BUY (transacción iniciada por el comprador al precio Ask) y TICK\_FLAG\_SELL (transacción iniciada por el vendedor al precio Bid) presentes únicamente en la estructura de ticks reales, datos imposibles de reconstruir a partir de barras consolidadas.8  
Tercero, permite modelar de forma precisa la liquidez transaccional histórica. Las simulaciones robustas del deslizamiento de las órdenes exigen conocer la profundidad de la liquidez en el momento exacto de la ejecución de cada tick, evitando la sobreoptimización común asociada a las pruebas basadas en la interpolación lineal de barras en el probador de estrategias.9

### **Impacto en Almacenamiento, Memoria y Entrada/Salida (I/O)**

La manipulación de series de ticks impone requisitos exigentes sobre la infraestructura de almacenamiento físico. El volumen generado por una cartera moderada de 20 activos puede alcanzar decenas de millones de registros semanales.2  
Durante la fase de backtesting y optimización, la velocidad de carga de estos archivos históricos se convierte en el principal cuello de botella computacional. La implementación de almacenamiento basado en discos NVMe de alta velocidad (lectura secuencial de ![][image2]) reduce hasta en un ![][image3] el tiempo de preparación de los agentes de simulación frente a configuraciones tradicionales SATA SSD, acelerando directamente el ciclo de investigación y desarrollo cuantitativo.

## **Acceso y Sincronización del Libro de Órdenes (DOM)**

La profundidad de mercado (Level 2\) permite conocer la intención de negociación de los participantes del mercado antes de que sus órdenes se ejecuten.16 En MetaTrader 5, esta información se extrae mediante estructuras de datos especializadas.16

### **Implementación Técnica de Acceso en MQL5 y Python**

La estructura base utilizada en MQL5 para capturar los niveles del libro de órdenes se denomina MqlBookInfo.16 Esta contiene tres campos esenciales: type (identificador del tipo de orden del DOM, por ejemplo, BOOK\_TYPE\_BUY\_LIMIT o BOOK\_TYPE\_SELL\_LIMIT), price (nivel de precio de la cotización) y volume (tamaño de la orden expresado en lotes o contratos).16  
En la integración con Python, el paquete oficial de MetaTrader 5 ofrece las funciones homólogas market\_book\_add(), market\_book\_get() y market\_book\_release().23 La llamada a market\_book\_get(symbol) devuelve una tupla de objetos de tipo BookInfo, cuyos atributos replican la estructura binaria de MQL5 y pueden convertirse inmediatamente a estructuras de datos nativas de análisis.23

Python  
\# Extracción y procesamiento estructurado del DOM en Python  
import MetaTrader5 as mt5  
import pandas as pd

def capturar\_estado\_dom(symbol):  
    \# Solicitud del estado actual de la profundidad de mercado  
    items \= mt5.market\_book\_get(symbol)  
    if items is None:  
        error\_code \= mt5.last\_error()  
        raise RuntimeError(f"Error al leer DOM para {symbol}. Código: {error\_code}")  
      
    \# Conversión eficiente a DataFrame para análisis de desequilibrios  
    dom\_list \= \[item.\_asdict() for item in items\]  
    df\_dom \= pd.DataFrame(dom\_list)  
      
    \# Separación y ordenamiento de Ask (ventas) y Bid (compras)  
    asks \= df\_dom\[df\_dom\['type'\] \== mt5.BOOK\_TYPE\_SELL\].sort\_values(by='price', ascending=True)  
    bids \= df\_dom\[df\_dom\['type'\] \== mt5.BOOK\_TYPE\_BUY\].sort\_values(by='price', ascending=False)  
      
    return asks, bids

### **Análisis de Compatibilidad y Restricciones de Brokers**

A pesar de que las APIs de MetaTrader 5 exponen estas funciones de profundidad de mercado, su viabilidad operativa está supeditada estrictamente a la infraestructura tecnológica y al modelo de ejecución del broker utilizado.25  
En los mercados de divisas minoristas de carácter Over-The-Counter (OTC), la mayoría de los brokers de Forex operan sin un libro de órdenes centralizado.25 Para estos brokers, el terminal reporta la propiedad SYMBOL\_TICKS\_BOOKDEPTH \= 0, lo que significa que la llamada a MarketBookAdd() fallará de inmediato retornando false e indicando en el registro de errores el código 4901 (ERR\_BOOKS\_CANNOT\_ADD).25 En tales circunstancias, cualquier llamada subsiguiente a MarketBookGet() devolverá el código de error 4903 (ERR\_BOOKS\_CANNOT\_GET).25  
Incluso si el broker habilita una interfaz gráfica visual de profundidad de mercado (DOM), esta suele ser puramente sintética, construida de manera artificial espaciando niveles de precios ficticios en torno a la cotización de los mejores Bid y Ask, lo que carece de valor predictivo para el análisis microestructural del flujo de órdenes real.24 Las estrategias cuantitativas basadas en volumen y DOM real deben operar exclusivamente a través de brokers que ofrezcan acceso a mercados de futuros centralizados o que provean puentes ECN directos de grado institucional donde la profundidad refleje liquidez de mercado verídica.3

## **Arquitecturas de Streaming Interproceso (Python ↔ MetaTrader 5\)**

La integración bidireccional entre MetaTrader 5 y Python requiere el diseño de un puente de comunicación interproceso (IPC) optimizado para baja latencia.26 Dado que la biblioteca oficial de Python para MT5 opera exclusivamente bajo un modelo síncrono de petición-respuesta (polling), no es adecuada para capturar flujos de ticks en milisegundos en tiempo real.6

### **Diagrama Conceptual de la Arquitectura de Integración (Descripción Textual)**

La arquitectura de baja latencia se estructura en tres capas jerárquicas locales ejecutadas sobre el mismo servidor físico Windows para eliminar retardos de red:

1. **Capa Transaccional y de Captura (Terminal MetaTrader 5):** Un Expert Advisor escrito en MQL5 se ejecuta de manera continua acoplado a un gráfico de alta liquidez.4 Este EA intercepta de manera asíncrona los eventos de ticks reales (OnTick()) y variaciones del libro de órdenes (OnBookEvent()).4 En lugar de procesar los datos localmente, los delega de inmediato a un cliente o servidor de baja latencia integrado directamente en el EA.3  
2. **Capa de Comunicación de Ultra Baja Latencia (IPC):** Un canal de memoria compartida mapeada (Memory-Mapped File) o una tubería nombrada duplex (\\\\.\\pipe\\MQL5) conecta el espacio de memoria del proceso del terminal MT5 con el proceso del intérprete de Python.26 Esta capa transmite los bytes binarios crudos sin serializar, evitando por completo la sobrecarga de la pila de red TCP/IP y el consumo de CPU asociado al procesamiento de texto.1  
3. **Capa Analítica de Ejecución (Python Processing Core):** Un script de Python asíncrono actúa como consumidor permanente, leyendo el flujo binario del canal de comunicación, cargando los datos en estructuras vectorizadas y evaluando modelos matemáticos en tiempo real para retornar órdenes de trading transaccionales de vuelta al EA.20

### **Comparativa de Patrones de Comunicación**

| Patrón de Streaming | Latencia Promedio | Consumo de CPU | Escalabilidad Multicurrency | Fiabilidad Operativa | Limitaciones del Enfoque |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **API Polling (Oficial)** | **![][image4]** | Alto (debido a consultas continuas) | Muy Baja | Media | No es orientado a eventos; omite ticks intermedios de alta velocidad.28 |
| **ZeroMQ (Sockets TCP)** | **![][image5]** | Moderado | Excelente (mediante PUB/SUB) | Muy Alta | Mayor sobrecarga debido al protocolo de control TCP de la pila local.3 |
| **Tuberías Nombradas (Named Pipes)** | **![][image6]** | Bajo | Alta (mediante canales dedicados) | Alta | Limitado de manera estricta a entornos del sistema operativo Windows.26 |
| **Memoria Compartida (Shared Memory)** | **![][image7]** | Mínimo | Complejo | Media-Baja (riesgo de corrupción de memoria) | Requiere el desarrollo de DLLs nativas en C++ y control estricto de exclusión mutua.26 |

### **Ejemplo Práctico: Implementación de Named Pipes Duplex**

El uso de Named Pipes en Windows ofrece un balance óptimo entre facilidad de desarrollo nativo en MQL5 y mínima latencia local.26 A continuación, se detalla la implementación de un EA cliente en MQL5 y un servidor de lectura asíncrono en Python utilizando la API nativa de Windows.30

Fragmento de código  
//+------------------------------------------------------------------+  
//| MQL5: EA Cliente de Named Pipe para Streaming de Ticks           |  
//+------------------------------------------------------------------+  
\#property property\_strict

// Importación de funciones nativas de la API de Windows para control de archivos  
\#import "kernel32.dll"  
   int CreateFileW(string lpFileName, uint dwDesiredAccess, uint dwShareMode, uint lpSecurityAttributes, uint dwCreationDisposition, uint dwFlagsAndAttributes, int hTemplateFile);  
   int WriteFile(int hFile, uchar \&lpBuffer, uint nNumberOfBytesToWrite, uint \&lpNumberOfBytesWritten, int lpOverlapped);  
   int CloseHandle(int hObject);  
\#import

\#define GENERIC\_WRITE          0x40000000  
\#define OPEN\_EXISTING          3  
\#define FILE\_ATTRIBUTE\_NORMAL  0x00000080  
\#define INVALID\_HANDLE\_VALUE   \-1

int pipe\_handle \= INVALID\_HANDLE\_VALUE;  
string pipe\_name \= "\\\\\\\\.\\\\pipe\\\\MT5\_TickStream";

int OnInit()  
{  
   // Apertura del canal Named Pipe creado previamente por el servidor de Python  
   pipe\_handle \= CreateFileW(pipe\_name, GENERIC\_WRITE, 0, 0, OPEN\_EXISTING, FILE\_ATTRIBUTE\_NORMAL, 0);  
   if(pipe\_handle \== INVALID\_HANDLE\_VALUE)  
   {  
      Print("Error crítico al conectar con la Named Pipe de Python. Error: ", GetLastError());  
      return(INIT\_FAILED);  
   }  
   return(INIT\_SUCCEEDED);  
}

void OnTick()  
{  
   if(pipe\_handle \== INVALID\_HANDLE\_VALUE) return;  
     
   MqlTick tick;  
   if(SymbolInfoTick(\_Symbol, tick))  
   {  
      // Serialización binaria directa de la estructura MqlTick (64 bytes de tamaño estructurado)  
      uchar buffer;  
      StructToToBytes(tick, buffer);  
        
      uint bytes\_written \= 0;  
      WriteFile(pipe\_handle, buffer, 64, bytes\_written, 0);  
   }  
}

void OnDeinit(const int reason)  
{  
   if(pipe\_handle\!= INVALID\_HANDLE\_VALUE)  
   {  
      CloseHandle(pipe\_handle);  
   }  
}

// Helper para mapear memoria de la estructura a array de bytes  
void StructToToBytes(const MqlTick \&tick, uchar \&bytes)  
{  
   // Copiado de estructura directa usando funciones nativas de casteo  
   struct MqlTickBytes { uchar data; } s\_bytes;  
   s\_bytes \= (MqlTickBytes)tick;  
   ArrayCopy(bytes, s\_bytes.data);  
}

El script de Python correspondiente debe actuar como el servidor de la tubería encargándose de inicializar el recurso de Windows y de leer continuamente los bloques binarios que envía el EA 30:

Python  
\# Python: Servidor Named Pipe para Ingesta de Ticks de MT5  
import win32pipe  
import win32file  
import struct  
import time

def inicializar\_pipe\_server():  
    pipe\_path \= r'\\\\.\\pipe\\MT5\_TickStream'  
      
    \# Creación del Named Pipe en modo dúplex y transmisión por mensaje binario directo  
    pipe \= win32pipe.CreateNamedPipe(  
        pipe\_path,  
        win32pipe.PIPE\_ACCESS\_DUPLEX,  
        win32pipe.PIPE\_TYPE\_MESSAGE | win32pipe.PIPE\_READMODE\_MESSAGE | win32pipe.PIPE\_WAIT,  
        1, 65536, 65536, 0, None  
    )  
      
    print("Servidor de Tubería iniciado. Esperando conexión del Expert Advisor en MT5...")  
    win32pipe.ConnectNamedPipe(pipe, None)  
    print("¡EA conectado de manera exitosa\!")  
      
    \# Formato de desempaquetado binario MqlTick (64 bytes en total)  
    \# \<QdddQqI4xd \-\> Little-endian, datetime(Q), bid(d), ask(d), last(d), volume(Q), time\_msc(q), flags(I), padding(4x), volume\_real(d)  
    mql\_tick\_format \= "\<QdddQqI4xd"  
      
    try:  
        while True:  
            \# Lectura del bloque de datos binario crudo del buffer del pipe  
            err, data \= win32file.ReadFile(pipe, 64)  
            if err \== 0 and len(data) \== 64:  
                unpacked \= struct.unpack(mql\_tick\_format, data)  
                  
                time\_sec \= unpacked  
                bid \= unpacked  
                ask \= unpacked  
                last \= unpacked  
                volume \= unpacked  
                time\_msc \= unpacked  
                flags \= unpacked  
                volume\_real \= unpacked  
                  
                print(f"Tick Recibido \- Bid: {bid} | Ask: {ask} | MSC: {time\_msc}")  
    except Exception as e:  
        print(f"Conexión interrumpida de forma inesperada: {e}")  
    finally:  
        win32pipe.DisconnectNamedPipe(pipe)  
        win32file.CloseHandle(pipe)

if \_\_name\_\_ \== "\_\_main\_\_":  
    inicializar\_pipe\_server()

## **Pipelines de Procesamiento de Ultra Baja Latencia**

La rentabilidad de un sistema de trading automatizado de alta frecuencia se define por su capacidad para procesar información y emitir juicios de ejecución en ventanas temporales de microsegundos.1 Esto exige eliminar cualquier origen de retardo computacional evitable dentro del flujo analítico.1

### **Evitación de Retardo por Serialización**

El principal cuello de botella de rendimiento en la comunicación de procesos reside en la conversión de estructuras de memoria interna a formatos de texto plano como JSON o XML. Durante momentos de alta volatilidad macroeconómica, la tasa de ticks puede exceder de forma sostenida los 500 ticks por segundo por símbolo.1 Convertir estos datos a cadenas JSON mediante el EA de MQL5 y procesarlos en Python mediante json.loads() consume hasta el ![][image8] del ciclo útil de la CPU en operaciones inútiles de parseo de cadenas, generando retrasos severos conocidos como hinchamiento de buffer (*buffer bloat*).  
La transmisión debe realizarse enviando de manera directa el bloque de memoria binaria de la estructura nativa MqlTick.35 Esto permite que el receptor en Python acceda a los valores primitivos de punto flotante de forma instantánea a través de desplazamientos de puntero en la memoria (offsets), reduciendo el tiempo de desempaquetado de milisegundos a nanosegundos.35

### **Estructuración de Buffers Circulares Contiguos**

Los cálculos vectorizados sobre bibliotecas como NumPy o SciPy imponen un requisito fundamental: los datos deben estar almacenados en bloques de memoria físicamente contiguos.38 No obstante, los flujos continuos de datos en tiempo real implican la inserción infinita de nuevos elementos.20 Usar listas estándar en Python y aplicarles métodos como append() o rebanados constantes fuerza al intérprete a copiar y realojar arreglos completos en memoria, lo que representa una operación de complejidad algorítmica ![][image9] inadmisible para baja latencia.38  
Para solventar esta limitación, se implementa el patrón de Buffer Circular basado en arreglos NumPy pre-asignados de tamaño fijo ![][image10].38 El puntero de escritura avanza secuencialmente mediante aritmética modular:  
![][image11]  
Para permitir la extracción de ventanas históricas contiguas sin incurrir en duplicaciones de memoria, se adopta el patrón de solapamiento extendido de tamaño ![][image12] (donde ![][image13] es el tamaño máximo de la ventana de análisis histórica).38 Al realizar una escritura que intersecta el límite de la capacidad física, el dato se copia de forma dual tanto en la posición indexada correspondiente de la primera mitad del buffer como en la posición correspondiente del bloque de extensión final.38 Esto garantiza que siempre exista una vista contigua de tamaño ![][image13] accesible directamente a través de referencias de memoria (views) de NumPy para cálculos vectorizados inmediatos.38

### **Pipeline de Ingesta y Feature Engineering Vectorizado**

A continuación se presenta un diseño robusto de pipeline que integra un buffer circular de NumPy optimizado para el pre-cálculo asíncrono de características de trading en tiempo real:

Python  
import numpy as np

class LowLatencyFeaturePipeline:  
    def \_\_init\_\_(self, window\_size=50, buffer\_capacity=1000):  
        self.window\_size \= window\_size  
        self.capacity \= buffer\_capacity  
          
        \# Reservamos memoria extendida para garantizar accesos contiguos lineales de tamaño window\_size  
        self.total\_size \= self.capacity \+ self.window\_size  
        self.price\_buffer \= np.zeros(self.total\_size, dtype=np.float64)  
        self.volume\_buffer \= np.zeros(self.total\_size, dtype=np.uint64)  
          
        self.write\_index \= 0  
        self.ticks\_seen \= 0  
          
    def registrar\_tick(self, price, volume):  
        idx \= self.write\_index  
          
        \# Escritura dual primaria en el buffer circular estándar  
        self.price\_buffer\[idx\] \= price  
        self.volume\_buffer\[idx\] \= volume  
          
        \# Escritura espejo de solapamiento si estamos dentro del rango de extensión final  
        if idx \< self.window\_size:  
            self.price\_buffer\[self.capacity \+ idx\] \= price  
            self.volume\_buffer\[self.capacity \+ idx\] \= volume  
              
        self.write\_index \= (idx \+ 1) % self.capacity  
        self.ticks\_seen \+= 1  
          
        \# Retorna una vista de memoria contigua de los últimos ticks requeridos  
        return self.\_obtener\_ventana\_reciente()

    def \_obtener\_ventana\_reciente(self):  
        if self.ticks\_seen \< self.window\_size:  
            return None  
              
        idx \= self.write\_index  
        \# Determinación de los índices de la ventana de memoria contigua  
        if idx \>= self.window\_size:  
            start \= idx \- self.window\_size  
            end \= idx  
            return self.price\_buffer\[start:end\], self.volume\_buffer\[start:end\]  
        else:  
            \# Aprovechamiento del solapamiento espejo del final del buffer  
            start \= self.capacity \- (self.window\_size \- idx)  
            end \= self.capacity \+ idx  
            return self.price\_buffer\[start:end\], self.volume\_buffer\[start:end\]

    def calcular\_micro\_features(self, windows):  
        if windows is None:  
            return None  
              
        prices, volumes \= windows  
          
        \# Cálculo vectorizado optimizado a nivel C nativo mediante NumPy  
        mid\_prices \= prices  
        price\_velocity \= np.diff(mid\_prices)  
        price\_acceleration \= np.diff(price\_velocity)  
          
        \# Medida de la volatilidad realizada localmente  
        local\_volatility \= np.std(prices)  
        vwap \= np.sum(prices \* volumes) / np.sum(volumes) if np.sum(volumes) \> 0 else prices\[-1\]  
          
        return {  
            "volatility": local\_volatility,  
            "vwap": vwap,  
            "momentum": price\_velocity\[-1\] if len(price\_velocity) \> 0 else 0.0,  
            "acceleration": price\_acceleration\[-1\] if len(price\_acceleration) \> 0 else 0.0  
        }

## **Tolerancia a Fallos, Gaps y Reconciliación de Datos**

En un entorno de producción en tiempo real, las desconexiones temporales por microcortes de red, fallos del servidor del broker o sobrecargas de procesamiento local son inevitables.9 Un sistema de trading algorítmico maduro debe poseer mecanismos para garantizar la coherencia absoluta de los datos históricos en sus bases de datos asíncronas.13

### **Algoritmo de Sincronización Determinista Libre de Gaps**

El método de control de flujo basado de forma exclusiva en el evento OnTick() presenta graves deficiencias debido a que el terminal omite cotizaciones cuando el hilo está congestionado.4 Para solucionar este vacío temporal, se debe emplear un algoritmo de sincronización robusto aprovechando el búfer persistente del terminal de MetaTrader 5 mediante la función CopyTicks().13  
Dado que CopyTicks() puede sincronizar directamente la base de datos de ticks local del terminal con la del servidor de corretaje, se puede programar una verificación secuencial que se ejecute de manera dual tanto al recibir un tick aislado como al cumplirse un intervalo fijo del temporizador OnTimer().14  
Este flujo lógico se estructura bajo la siguiente secuencia operativa 13:

1. **Persistencia del Estado Temporal:** El sistema almacena localmente una variable estática que registra la marca temporal exacta, expresada en milisegundos (time\_msc), del último tick procesado con éxito.13  
2. **Consulta no Bloqueante con Margen:** Al dispararse un nuevo evento, el EA realiza una llamada a CopyTicks(), especificando como punto de partida la marca temporal del último tick registrado más un milisegundo adicional (![][image14]).13  
3. **Manejo de Bloqueos en MQL5:** Es crítico conocer que el comportamiento de CopyTicks() varía según el tipo de programa MQL5.13 En indicadores (que comparten un hilo de ejecución común por símbolo), la función retorna inmediatamente los datos disponibles en la memoria caché e inicia un proceso asíncrono de descarga en segundo plano para evitar congelar la interfaz de usuario.13 Por el contrario, en Expert Advisors y scripts (que operan en hilos independientes), la función bloqueará la ejecución del EA hasta por 45 segundos mientras espera la sincronización completa del historial desde el servidor remoto, procediendo por tiempo límite en caso de que este expire.12  
4. **Tratamiento del Problema del Mismo Milisegundo:** En mercados altamente líquidos, es sumamente habitual recibir múltiples ticks distintos que comparten exactamente el mismo milisegundo de registro.13 Al sumar arbitrariamente ![][image15] milisegundo al punto de partida para evitar duplicaciones de ticks ya leídos, el algoritmo estándar omitirá de forma irreparable aquellos ticks subsiguientes que compartían esa idéntica estampa temporal de origen.13 Para mitigar este vacío, la rutina de reconciliación cuantitativa debe almacenar el número absoluto de ticks duplicados en el milisegundo de frontera.13 En la siguiente llamada, se solicita el historial desde el tiempo de inicio exacto de frontera (sin sumarle ![][image15]) y se descarta programáticamente en Python el número de elementos iniciales correspondiente al conteo de duplicados previos, garantizando una ingesta libre de omisiones de datos.13

### **Heartbeats, Timeouts y Mecanismo de Reconexión**

Para prevenir situaciones donde una desconexión silenciosa de la Named Pipe o del socket de red deje al motor analítico de Python operando con datos fantasmas, es obligatorio implementar un esquema robusto de latidos de control (Heartbeats):

* **Ping/Pong de Verificación Activa:** El EA utiliza su evento OnTimer() para enviar un mensaje simplificado de control de conectividad (por ejemplo, {"MSG": "PING"}) a través del canal IPC en intervalos fijos de un segundo.15  
* **Controles de Timeout asíncronos:** El consumidor en Python ejecuta un temporizador asíncrono que monitorea constantemente el canal de lectura.40 Si transcurren más de cinco segundos sin recibir ninguna estructura binaria de tick ni ningún mensaje de tipo PING, el proceso declara formalmente un estado de desconexión.19  
* **Bucle de Reconexión y Backfill:** Al detectar la desconexión, Python procede a cerrar los descriptores de archivo de la Named Pipe local, entra en un bucle repetitivo de reintento de conexión cada dos segundos y bloquea temporalmente el envío de cualquier orden transaccional al mercado.17 Al reestablecer el canal de comunicación, el script de Python lee el valor del último timestamp de tick almacenado en su archivo de estado persistente (history\_tracker.json) y solicita al EA un reenvío histórico masivo de todo el bloque de cotizaciones omitido durante el periodo de caída, asegurando una reincorporación libre de inconsistencias analíticas antes de reanudar el cálculo en tiempo real.17

## **Benchmarking y Optimización del Rendimiento**

Para validar la idoneidad técnica de un diseño de infraestructura frente a otras opciones de la industria, es imperativo establecer métricas claras de latencia y tasas de transferencia computacional bajo condiciones de estrés.1

### **Métricas de Latencia en Diferentes Entornos**

La velocidad a la que viaja una señal de mercado desde la pasarela del broker hasta el motor de decisión algorítmico varía sustancialmente en función de la arquitectura física de despliegue utilizada.1

| Infraestructura de Despliegue | Latencia de Red al Broker | Latencia de Procesamiento IPC | Latencia de Ejecución Total | Viabilidad en Trading de Alta Frecuencia (HFT) |
| :---- | :---- | :---- | :---- | :---- |
| **PC de Escritorio Local (Conexión Hogar)** | **![][image16]** | **![][image17]** | **![][image18]** | Inviable (alto deslizamiento y retrasos de cola).1 |
| **AWS / GCP Cloud (Zonas Generales)** | **![][image19]** | **![][image20]** | **![][image21]** | Media-Baja (adecuado para algoritmos de baja frecuencia).41 |
| **VPS Co-localizado Dedicado (Centros LD4/NY4)** | **![][image22]** | **![][image23]** | **![][image24]** | Crítica (óptimo para scalping, arbitraje e intradía).1 |

### **Rendimiento de Procesamiento en Python**

El intérprete nativo de Python (CPython) puede procesar flujos de entrada en tiempo real de aproximadamente 5,000 a 15,000 ticks individuales por segundo en un único hilo de ejecución, siempre y cuando no se utilicen formatos de texto para la transmisión y la lógica matemática sea puramente aritmética elemental. No obstante, este límite de capacidad decae críticamente si se comenten dos errores estructurales comunes en el diseño de sistemas financieros:  
El primero es la presencia de latencia de serialización de texto. Utilizar un mapeo textual JSON y deserializar mediante la función nativa json.loads() introduce un retardo constante de entre ![][image25] por bloque de datos. Esto provoca un colapso en la tasa de procesamiento máximo, reduciendo la capacidad del sistema a un máximo de solo 150-200 ticks por segundo, provocando la pérdida o el retraso masivo de ticks durante eventos de volatilidad macroeconómica extrema.  
El segundo es la interferencia de lógicas de procesamiento bloqueantes.42 Por ejemplo, en integraciones de Expert Advisors modernos donde se consulta de forma directa a APIs externas de inteligencia artificial o de modelos de lenguaje durante la ejecución síncrona del EA, los hilos principales sufren una saturación severa.42 El tiempo de respuesta de estas APIs externas (que suele variar entre 1 y 5 tokens por segundo, requiriendo de 40 a 120 segundos para completar un análisis de texto completo) bloquea de manera irreversible el terminal, congelando la renderización visual de gráficos e introduciendo retrasos desastrosos en el envío de las solicitudes de orden (OrderSend).42  
Para mitigar estas restricciones, el pipeline debe utilizar de forma rigurosa la compilación estática a través de herramientas como Cython o el compilador Just-In-Time (JIT) de Numba.39 Al encapsular las rutinas matemáticas complejas en extensiones de lenguaje C optimizadas y delegar las tareas pesadas de red y de toma de decisiones lentas a hilos o procesos de ejecución paralelos secundarios, la velocidad útil de procesamiento de ticks en Python puede superar cómodamente los ![][image26], garantizando la escalabilidad absoluta del sistema para carteras multicurrency complejas.39

### **Conclusiones y Recomendaciones de Ingeniería**

1. **Separación de Responsabilidades:** Se debe consolidar a MetaTrader 5 únicamente como una pasarela de captura de datos de mercado y de ejecución de órdenes de bajo nivel.41 Cualquier cálculo analítico pesado, estimación estadística o evaluación de modelos predictivos de aprendizaje automático debe ser ejecutado asíncronamente en el espacio de proceso de Python, evitando saturar el hilo principal del EA para prevenir la omisión de cotizaciones clave.  
2. **Adopción de Flujo Binario IPC Local:** Se debe descartar por completo el uso de formatos estructurados de texto como JSON o REST APIs locales para la transmisión de ticks de mercado en tiempo real. Se recomienda el diseño de canales de comunicación directa basados en Named Pipes o Memoria Compartida que transmitan de forma nativa los 64 bytes de la estructura binaria de MqlTick, logrando desempaquetados de ultra baja latencia en Python mediante el uso de la biblioteca nativa struct.26  
3. **Monitoreo de Latencia de Extremo a Extremo:** Es mandatorio instrumentar las tuberías de procesamiento con trazadores de tiempo integrados para cuantificar constantemente la latencia acumulada en cada etapa del sistema.34 El desvío de los relojes locales con respecto a la referencia de tiempo maestro UTC debe ser monitorizado de forma estricta mediante servicios NTP, asegurando la validez analítica y la vigencia temporal de los precios cotizados utilizados por los algoritmos predictivos.34

#### **Fuentes citadas**

1. Reducing Tick-to-Trade Latency: Architecting Real-Time Forex ..., acceso: junio 28, 2026, [https://www.reddit.com/r/algotrading/comments/1sk5tye/reducing\_ticktotrade\_latency\_architecting/](https://www.reddit.com/r/algotrading/comments/1sk5tye/reducing_ticktotrade_latency_architecting/)  
2. The Trap of Parallel Processing in MT5: VPS Architecture Design for Multi-Symbol EAs｜AI MQL合同会社 \- note, acceso: junio 28, 2026, [https://note.com/aimql/n/n09c761773248?hl=en](https://note.com/aimql/n/n09c761773248?hl=en)  
3. SUM3API: Using Rust, ZeroMQ, and MetaQuotes Language (MQL5) API Combination to Extract, Communicate, and Externally Project Financial Data from MetaTrader 5 (MT5) \- ResearchGate, acceso: junio 28, 2026, [https://www.researchgate.net/publication/401883214\_SUM3API\_Using\_Rust\_ZeroMQ\_and\_MetaQuotes\_Language\_MQL5\_API\_Combination\_to\_Extract\_Communicate\_and\_Externally\_Project\_Financial\_Data\_from\_MetaTrader\_5\_MT5](https://www.researchgate.net/publication/401883214_SUM3API_Using_Rust_ZeroMQ_and_MetaQuotes_Language_MQL5_API_Combination_to_Extract_Communicate_and_Externally_Project_Financial_Data_from_MetaTrader_5_MT5)  
4. Expert Advisors main event: OnTick \- Trading automation \- MQL5 ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_ontick](https://www.mql5.com/en/book/automation/experts/experts_ontick)  
5. OnBookEvent \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/onbookevent](https://www.mql5.com/en/docs/event_handlers/onbookevent)  
6. Socket between MetaTrader 5 and Python \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/77792625/socket-between-metatrader-5-and-python](https://stackoverflow.com/questions/77792625/socket-between-metatrader-5-and-python)  
7. Multicurrency EA. What to use: OnTimer, OnChartEvent, OnTick, OnFakeindicator? \- page 3 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/502737/page3](https://www.mql5.com/en/forum/502737/page3)  
8. The Structure for Returning Current Prices (MqlTick) \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/structures/mqltick](https://www.mql5.com/en/docs/constants/structures/mqltick)  
9. Generating ticks in tester \- Trading automation \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/tester/tester\_ticks](https://www.mql5.com/en/book/automation/tester/tester_ticks)  
10. OnTimer \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/ontimer](https://www.mql5.com/en/docs/event_handlers/ontimer)  
11. Event Handling Functions \- Functions \- Language Basics \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/basis/function/events](https://www.mql5.com/en/docs/basis/function/events)  
12. CopyTicks \- Initialization \- Matrix and Vector Methods \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/matrix/matrix\_initialization/matrix\_copyticks](https://www.mql5.com/en/docs/matrix/matrix_initialization/matrix_copyticks)  
13. Working with real tick arrays in MqlTick structures \- Creating ... \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/applications/timeseries/timeseries\_ticks\_mqltick](https://www.mql5.com/en/book/applications/timeseries/timeseries_ticks_mqltick)  
14. CopyTicks \- Timeseries and Indicators Access \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/series/copyticks](https://www.mql5.com/en/docs/series/copyticks)  
15. Never miss Ticks \- Trailing Stop \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/439507](https://www.mql5.com/en/forum/439507)  
16. MarketBookGet \- Market Info \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/marketinformation/marketbookget](https://www.mql5.com/en/docs/marketinformation/marketbookget)  
17. The Ultimate MT5 Data Bridge: Hybrid REST & WebSocket TraderMade Plugin, acceso: junio 28, 2026, [https://tradermade.com/tutorials/MT5-tradermade-plugin](https://tradermade.com/tutorials/MT5-tradermade-plugin)  
18. Adding, replacing, and removing ticks \- Advanced language tools \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/custom\_symbols/custom\_symbols\_ticks](https://www.mql5.com/en/book/advanced/custom_symbols/custom_symbols_ticks)  
19. Python \- MTsocketAPI for MT5, acceso: junio 28, 2026, [https://www.mtsocketapi.com/mt5/for\_developers/Python/](https://www.mtsocketapi.com/mt5/for_developers/Python/)  
20. Stop Living in the Past: Building Your Real-Time Trading Engine with Python and ZeroMQ, acceso: junio 28, 2026, [https://medium.com/@lashapor/stop-living-in-the-past-building-your-real-time-trading-engine-with-python-and-zeromq-d2675f7b6c92](https://medium.com/@lashapor/stop-living-in-the-past-building-your-real-time-trading-engine-with-python-and-zeromq-d2675f7b6c92)  
21. How to interactive with MT5 with python | by Asc686f61 | Medium, acceso: junio 28, 2026, [https://medium.com/@asc686f61/how-to-interactive-with-mt5-with-python-99053eedd067](https://medium.com/@asc686f61/how-to-interactive-with-mt5-with-python-99053eedd067)  
22. CustomTicksAdd \- Custom Symbols \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/customsymbols/customticksadd](https://www.mql5.com/en/docs/customsymbols/customticksadd)  
23. market\_book\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5marketbookget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5marketbookget_py)  
24. What's new in MetaTrader 5 \- Page 4 \- MetaQuotes, acceso: junio 28, 2026, [https://www.metaquotes.net/en/metatrader5/news/page4](https://www.metaquotes.net/en/metatrader5/news/page4)  
25. MarketBookAdd returns 4901 and SYMBOL\_TICKS\_BOOKDEPTH is 0, but manual DOM window opens on MT5 \- Trade FX \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/510727](https://www.mql5.com/en/forum/510727)  
26. Efficient Communication Between Multiple MT5 Instances and Python for Low-Latency Data Analysis \- エキスパートアドバイザーと自動取引 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/ja/forum/483092](https://www.mql5.com/ja/forum/483092)  
27. Speed of named pipe vs tcp/ip vs shared memory \- EA Forum \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/170320](https://www.mql5.com/en/forum/170320)  
28. Connection of MATLAB and MetaTrader 4 or 5 via ZeroMQ \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/tr/job/122531](https://www.mql5.com/tr/job/122531)  
29. run two Expert Advisors and communicate between them (message passing between them both) \- Expert Advisor \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/289798](https://www.mql5.com/en/forum/289798)  
30. Named Pipes Communication between Python Server and Python Client on Window | by Pei Seng Tan | DataDrivenInvestor, acceso: junio 28, 2026, [https://medium.datadriveninvestor.com/named-pipes-communication-between-python-server-and-python-client-on-window-8cdf64504801](https://medium.datadriveninvestor.com/named-pipes-communication-between-python-server-and-python-client-on-window-8cdf64504801)  
31. Interaction between MQL5 (or C++) and C\# via Named Pipes \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/18160777/interaction-between-mql5-or-c-and-c-sharp-via-named-pipes](https://stackoverflow.com/questions/18160777/interaction-between-mql5-or-c-and-c-sharp-via-named-pipes)  
32. Python and Windows Named Pipes \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/48542644/python-and-windows-named-pipes](https://stackoverflow.com/questions/48542644/python-and-windows-named-pipes)  
33. Why you need to synchronize every tick in the world? \- General \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/393733/page2963](https://www.mql5.com/en/forum/393733/page2963)  
34. How to Monitor Stock Market Data Feed Latency from Exchange to Trading Platform, acceso: junio 28, 2026, [https://oneuptime.com/blog/post/2026-02-06-monitor-stock-market-data-feed-latency-opentelemetry/view](https://oneuptime.com/blog/post/2026-02-06-monitor-stock-market-data-feed-latency-opentelemetry/view)  
35. Python struct.pack and struct.unpack for Binary Data \- DigitalOcean, acceso: junio 28, 2026, [https://www.digitalocean.com/community/tutorials/python-struct-pack-unpack](https://www.digitalocean.com/community/tutorials/python-struct-pack-unpack)  
36. Sending Binary Data — PyMOTW 3 \- Python 3 Module of the Week, acceso: junio 28, 2026, [https://pymotw.com/3/socket/binary.html](https://pymotw.com/3/socket/binary.html)  
37. struct — Interpret bytes as packed binary data — Python 3.14.6 documentation, acceso: junio 28, 2026, [https://docs.python.org/3/library/struct.html](https://docs.python.org/3/library/struct.html)  
38. ring buffer with numpy/ctypes \- python \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/8908998/ring-buffer-with-numpy-ctypes](https://stackoverflow.com/questions/8908998/ring-buffer-with-numpy-ctypes)  
39. Implementing a C-level Ringbuffer in Python \- HangukQuant Research, acceso: junio 28, 2026, [https://www.research.hangukquant.com/p/implementing-a-c-level-ringbuffer](https://www.research.hangukquant.com/p/implementing-a-c-level-ringbuffer)  
40. how to stream realtime data in Python socket \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/23320918/how-to-stream-realtime-data-in-python-socket](https://stackoverflow.com/questions/23320918/how-to-stream-realtime-data-in-python-socket)  
41. How to Build Your Own Trade Copier Using the MetaTrader API \- NYCServers Blog, acceso: junio 28, 2026, [https://newyorkcityservers.com/blog/how-to-build-your-own-trade-copier-using-the-metatrader-api](https://newyorkcityservers.com/blog/how-to-build-your-own-trade-copier-using-the-metatrader-api)  
42. AI-Assisted Trading on VPS: From API Costs to RAM Budgets by Tier, acceso: junio 28, 2026, [https://www.vpsforextrader.com/blog/ai-trading-co-pilot/](https://www.vpsforextrader.com/blog/ai-trading-co-pilot/)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIEAAAAZCAYAAAAWlU1+AAAEoklEQVR4Xu2ZSchcRRDHyw2joIiaoIga0KDiRTwkccEENxSXgxeJeBRRQTx4UC8hYiKiKCguB7eoKCiSuBw00VwiuEEQRQVRTHDf933vX6qLr6ame+bNzBvyJb4fFPP6X91v6a7Xr7pHpKOjo6Nj+2T3KHT8//g8CrOZx5L9m+z3ZFcF3yjcnOyPZF8nOzH4jMOTvSJ6veeDz3OPaJ0Pkh0SfCW4JvXNBnGszNT7J9lXWf8yl833k+h5v0v2d9buynWbQNvWOU30Ri6LjgngfHuHMgM5Kt8nW+nKvya7wZVhifQO0DGhbDAQp7sydc5w5Ro7J3tUtP4twef5RmYGu0QtkM4W1d+LjgIXS/1FaIUTRG/mpugYkZNEz7PBad9m7QinDeMU6e+0fQsa5UuDRsC97MrXSX876/xhEAT3Sn0QjSdkvCCAQT5PkzqtsEB0Cn8kOhqyq+jN3ui0X7LmZ4dhMJClh0a7MB/Py2V+PeuzbnD8tisb6AdHMWBBwExJ/QN63Vu5JtluMv0geDUK02Z/0Td4Y3SMQdOH9FD/zyiK6m/k4+W5HLlf+oOglCug3xbFgAUBUP8t5zPsWuMEwYGi+hfRESBvmBvFxDLR/nhOdBaeSqDMSbZZ9E3aJfiGwazwpmjn7BR8w6BjfoiiqE5uAEzBpY69Q/qD4ClXNtCfiWLAB8GH0n+9PZNdno+bBMFh2Y5Ktipr97l6NUrn5ZN3kSvfKVNcPTDdks0+Gx0DuEA0ermp0gAMg4cm2YpYZwKzVKlzbhXVDxIdRI7X9NRQ0N+NYoD2Nkh8KmnDsxl+hmkSBCdnI0k9VzSgWa1wnRrkQhaIHs4X86zWg4AL8G1+IDpG5DPRGx5lNqA+gRdBp7OBvKXU6beL6sxEwDGzRgT9hSgGGJzVruyvD5+44yZBUMJ8e0RH5kUp993Pou1eE/0stIpl+NdHx5hcKXq+T6NjANQnQY2g29tbywksmzc4XufKBvrdUQwQBA+68mrRdgzKkmRHOt+4QcDSD9870ZGptYMfZebc2Dm97tEhmjjRJHsGdNhfQWNtO6gTStTqo9nmii1rJ1kdnB/FAEHwkCsz+LRjdmTjxzNuEJwpdf/xya6IYsYnivOlvqJqBIkNjflGTYo9zFKnkbyg+amTqa/2cECSEx/IBoDlmEH5PFcGBsfnEwRAPNfCglaCIHg4aLbT54MDxg2CzaK+q6NDynmRUTpfSRvKCtEtz7ZYK/3fWQaFm/N/flinMBg18B/tyix/4oqBt97PPBYo851mm0ysdAym0U2uXONp0cH132ubMeN32oIg6lALAtteryV07JrWoJ3fUd0na7MCMnFuZkv+JQOO/37x9n4sg5POQ0Xbs/tIBk39Eq+LJkmPi9Y/tde9FTR8T4ruf7zU6y7C/v9HoktDkttrne99d7xFdBCtLjOefSps8M0IFPY/6BMSXwLxuFw3Qq6wNIqO35JdIjPn5vqWDG837CWT/bm0o+NXIVOFtfRZDW1xbtMWg2aBjint/pVge3hRQ2OXqy32k/JWbofCH3mMzQ5NzBE6epk1CV7HtmPQqqmjo6Ojo6NN/gMvbnfgHmqoSwAAAABJRU5ErkJggg==>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAZCAYAAABdEVzWAAAB8UlEQVR4Xu2UvytGURjHHz9CEZGFmJSIQhksMkgUkmJRbAazTVksDAYGFqu/QDJhQtko8iMMQgaFwY9EPF/nnPd9znPv+3rf4S3D/dS3e57v89x7n3vOPYco4v/Qr40QmrWRSRpY7/b6yWr10zHOWYPaDKOMdcf6Zl2xSvz0L0+sUVYpmfwQ69GrMPfX2DHq3lhfrElWF2vF1tzbmqTkkWnKkUXm5hbhAXhaVV6F8RLFFfaKGU0JzISmkcyXSvCSWdYyq1PlQDklbwxMUYpLCHDzhPKarC/RcRi6Rsa5lOISOvCf4AGbwsMstosY6JeG8cEasWPM6rjKpUUO+f8NmurzKgzIYTcds/bI7DrMggZ1q6wH4c2wBkScMpXkN4eXa+Dni3jDen+hN1c965W1LbxQuslsa9BB8eYOYxXh1JGpm9YJBWbWUUzxjylknYhcgLCvvqagjyWXZJOpSfbwOVaviPHcNRFfiLHHMAUbcMBvs2M8AHFBPE1F1tsRngS1N8pD/ZKIF8TYA4dossYc+NIXEYMeMjVuF2r0OQh0Y4tiHADF2DUSxAcirmZdihjgBHf/pmaewg/hfda6iBMupeOZTIOn9ortrhkjk7u1110/HQNLmOiF2NVuJfDzH4lcxjnThqKWzGG7pRMRERERafID4oN/QibfNZAAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJgAAAAXCAYAAAD3JIYsAAAFZ0lEQVR4Xu2aaahuUxjHH+M1u+ZkTEQpxAdkuLdQhsicjEkZQny6RYZCEcnMF/KByBgJGbtXZpJZpjqmQubhmof1a63nfZ/97PXuvfbh3POe0/7Vc/Z6/mvttfde81rvEenp6enp6enp6ZlOdg32VbB/gj0fbOlqdDErB3tUYj4vBVuqGj3g8mC/B/ta4rNzbB7sBYl5Pe7iZgr7BrvDi4nvgh0TbI1gqwc7NNi3lRTlnBvsh2CLg53g4pTS8iypm05cE+x64/OSvMRmRithA4n3rZj8tZLvG+v3wS4y/i/BLjE+zJN4r7Kd88eZBcF+lPi+2J3V6AEab23DSooy3g72mPHfDPaM8aG0PEvqpjM8aMeMlnuBJn6Wem99Odivxt9D6vmumdHwT3EavYrRdSbR1sAulti5KZfJsJrUyw7Q5jq/rTxL66YTTGm5xpTT2iD94U47O+kKH5XLF+3oFF43+VwtOvXOJHjfpgb2X3lV8vmg3ZjCpeVZUjeT4sJguzitawPbXWJ6P2cfl3R6AhD+Yxg9AP31FD4v+Z6bJa/vHOxILwa2dP5uEqcO1iF0hPer0TWWDXapxHQLpZ5fCbzvVDawUfVk9dLyLKkbC0srzzpSXxJlIdO/vdjAmRLv2d7phyVdp2DCLEY96Mz3cF/yPddJXkd7zmlsMGzay4LdanwaZC4vC/Efp/ByyX9yGF0E9zQ1sPeCvRXs2WB/SmzUXSCP3HdYvbQ8CbfVjbJK0pkBLWinO60GrZWEK/mIBi6QeM82Tj8o6Ucln/A3w+gBtkCeMmHLVRJ1NhMWtP0z2gPOP8n4qjVB/IPGPzVpXSD9XV5MEDfH+A8lrQu23CyTKU/CbXWj0GG9tnbSdATb2sQNYKQhEUNdF06UeB+7Ewtbb3RdxBJme+5B1xHztuR7rpWo215+QNI8aDsZnxEObULqDa2UQyT/rCZIf48XR7CVxPQcOZRC+tw7Wb20PEvqRvkrmYXNSu45AziPIYHtVaXoGoz1kIVzHnTbS34bRg9A1zXRqDXDTVLXc4vcIzIafCDDgsfOr0bXYBfGzpjCZYQ+Q/L5NkH6e72YWMb59HzSv+P0JvRbPFYvLU/CbXVjNc7LvOan0gH6cZZbnN8EjZL723aRTQVyQwqz4cBv2/UAPo3M8m7SLeubMBuOL6WexrKx1AuRDUzTPTlIzxrIo419BaPpuuZpo7Wh520eNG2opeVJeFReWjeg55sMSBY0e4ZWOWT3QyB4bR8ZMa8meMDVTvPritwwyougsZBW8A82Pvwk9TWC/yjVXjRhe7Wg+VFE+VDq9xxoNB83CtLd70WJmwdGR8veEtPbHTFlc47xPXTo3Lug7eD8tvIsrRvq2KfTQ/ZVU5iF/jyN1POPnCn6IJ+xxY9WkPswNNtQaQx+90LvYlel6PM3NZquib4w2qKknRVsPRlWDtojmshoo7hCYrwer4B+v/bgNpaXmM6fqsNGEhuxhQNpP8Xwcw15LHC6hfiTjZ9bgJeUJ5TUDQOPT6dlAxyuw3z+aMvLmf9YeuKE0zy3S1z8cSUPji88m0iMe0JiT/6sGj3gNYm9/G6J6fesRssbSV+crjyXHqQjAZWj4O+Vrhj52pPuHLqNxzhOAI4caAhNP+mcJvF3Xb7rk2CfBvtc6uV5rMS8Scc11xC3lfgdH/kIAz/NcT+NgTLj/XK/AbeVJ5TUDfGvpCumR0QTydc6n5+undCpZxzgY7S3zHYe9sI0oaM3P85PCWQ+LvAu/vxrNnK8NI+YS5IrZQrbAPM4h2njwH4yhR86ZjC9jgssQ3I/J/0vbOGFaYT1C/+W0rNkYQ2XW7v19PT0zDL+BfZK9hgb6ogDAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAG0AAAAXCAYAAAABQcHxAAAEYUlEQVR4Xu2ZWch2UxTHlymzzJniI5IbmQqZLlDKkPErJIUMuaDcSBnigkhmpcgFmXIhZZbMM5kiU+TCnHnKvH/PXut5/2ed/byOoTy8z69W717/tc85++xnD+vs12zGjBkzZsz4/7FzsU+L/VbsyWJLdsNjTi/2VbHvih2dYsGmxZ6yeq/7U2zaWbrYS1bb/lGxTbrhMUcV+6DYz8XOS7FgxWL3Wr3XM8WW6Ib/HpcVu1J8fhAelBv8arH7xH+l2GPiw25Wrw22Sv6085N1O/fLYseID7cWe1/864t9Jj6sb/W9l3d/DfcnTYY/DTfbvqFpZ6+S/ABt1eSfID78aHX2Tju3F9sii9Z/b3xmZNb2Ev/bYjeLD88W+yFpfwmmcP6BIGsvJD9Au9rLa7vPXyWWiGmHNt6UNGadtv3i5AdobyV/sfhwmuv/COcU2ylp+UfLfqD6GVJWrrW2vp7VZ2e2S/4uVpdh9kk64s1uuAez4Hyr9R4stnknOpkYXNr5z1vdxwNWjda7aD/s6mXyBOVI11dPOu29KmmwQ/LZru5KWgdu/mvy/6ixt0lZucLaOh3ARq5cYN26+OwZwWHWvpdC/D0vL+P+A3PheYn3wV4vdlYnOqwfTvbyNnPhEYe4nreix11X9k7aPsVeE79HZE8riDaksQ9LWbnEqs7mrKBdmDQGyhfiU+c48UObD+J3iH+ia0NYzubeCcsJxpB+ONvLW86FRxzg+uFJR3suaS+7HnxS7EbxOzAKqLxW0oc09gYpK5db1XXzJnlB0yQG0E4V/wnX3rX+jzeUg6zdrszGVuuxjy3yMsYnTjCkH471MpmzcrDruycdbd+Gdrf457r2uWgjVvPAsjlgwxo7aU+7xvp6a0Nfx7X8fPaYeA52Zjfcg4FA9sasZdSfZP1ntaDOmkl7yPUYxCznrXtpP8SetuNceMQRruuKs79rGTTuo9zj+hi+H/LF10n5a+vHAS3WWpIZ/CHZIx2qeyawGed660qZDfxj69dRNrQa12WXhGC+a4AfZVId9Jj9fKe26qHF+zDo8Idkjy82tEMbWu7TEbkDQTUakG8EaNsm/0Dx4Rtr7w2PNrRITOLZk565VBadt61/jY7mHFMmxdA38HKsBhm0U5J/qfhwp+sKftbIekMjGQJ89tsxkca2TME/Xvyc6QGzSjPC+M5ZJBpLUL4/KTo+SwDXxPFXaEp+pnKR1bim1fGsOJWYBHsX7Vf2s7rKKAwo/Z7LmR60ZhV+HtC5H3ge/vfux36K9o6Xx8ctLYsLA45k0J+2Oq35um+dpxFjT+G4h/p7dMOjYzP0D/0vtlmxjbysPzr+nlKP++bkJROfGNgbrt1itb0xYyZBfa5jhMe7tmCgU/cRq/VW6oZHkO394n+pw6eAEgkSx4HRXk5VYnnF4tiL8tb+91+BkcrLLHTi0+o/AQ3N32cLEfohf59NJXHwvHIOLEBiOZx6OAfk/1QLHY7Xcs4wY8aMqeF3QBCMotl2YfQAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAG0AAAAXCAYAAAABQcHxAAAEMklEQVR4Xu2YWahOURTHlylkSEimkMibTIVMDyhlyFxIRBkzxYMUigcyZH5Q5EXmBy9mSeaxTJEpQsYyz5n2/9tr3W+d9e3vu8e96n7XPb9anb3+a59p7332XmcTJSQkJCQk/L/McTbZior5zt47++xsvIkJLZydd/bb2VETK01UJP8OIcY5e+bsh7OlJiZUc3aY/DUuOisXDReP7c6+k784bEo0XMBNZ0eUf8PZaeWDHhR90TbGL018o/Cz73H2VPlbnb1WPmhE/tyq7Ndhv3xBjX9Itk6rSeEXgFbL+PZLxYA4Z7R8Z56zR5T9nfEVWq2P8j8526l8cMnZV6P9E7J12hXK/gKbuFyPfRw1MkWUFiqQ7zB8Ufa5Vwc0AO2e8YcrH2AghM4tNtk6DXrohlpfoMqaLRTWGzpbbEVHB+N3Iz8NY51EQ9yNhjPAV7CMfL3jzlpFooXzhY+hTpNlxKLboTuXu6bDKcawXtvoeN6NRgOdjN/c2QGjpShOp+1VZc0GCutoACzkmuUUrQsfa4YwksLX0iCOLwVUYv9YOpyTac4GcjnUaXHaYSaX26XDKYax3tHoZ1jX9DVaP2e3lB8BFadakeI97AlV1qwhr2Nx1kBbabRfzt4qH3UmKl+0XCC+T/l4n8LOEV6qclE7bRGXW6fDKQaxPsro0C4b7TrrwivyCWMQVMRos8R52G2qrFlPXteLN5IXaDqJAdDmKv8saw8ps/PiMoTCz2XRgwUUtdMmcBmZs2Yo6z2NDq1/QDuo/CWsvVFaAQhMtyLFe9hsa9pmytRDC3p91iobHQu83Ae2MBrOAAMB2Ru+Woz6GZR5L8sIZ2ONFuo0TOdWA7odZE3rnA6nGM26nnEwFWe7Hq6jOcR6BhAxJ1s+UPgEaDLXdmE/TvaIBoVpsBjbeg1UGQs4pi9bR9OEfFxPu0gIcp0DMJJPGpP/NPEB/lND14Im74NBBz9O9ng1oGEAWc22aQRUnmVF8g9gLwSgtTf+YOWDj5T584l6pwKaJCbSANnuibQ8xH3KPEePZhvLBX6gbX2ZDSzQZht/rfLBftY18K2GrFe023yEX4XLEeqSD66wAQaxScq3mR7AV6UzQmzdoE4zpcl99LlI0eFjCsA5sv0lmsbeU7OKfFyn1XIv2ZWIyzsK18eA2qF8m+mB0FcF3w5o2w4D2JffDmwZAmgPuJxiN/ns5Imzx3x8QT4l12BLBidfIP9Z4+8+tJ+GGNYUWRN6RcO0jvXnfIS1dNaUy7rT4fdW9XBdm7xY5BcDdoe1XeSft7FUygHWW7y/tAf2GDFVatA2uDamTdynejScAtneTz6ijl12JEHCdqA8L3ZVZHqFybYXym35WCJgpOJlyjrXqAQ74W/Bg9r/s7II2sH+n+UlsvFcwwbKIDId5j3YB8R6UdbB9pokGwkJCXnHH/uSeZgRpFpGAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADcAAAAXCAYAAACvd9dwAAAAjklEQVR4Xu3UIQ7CQBhE4VIqaNJgmmB6Ae7CObhT01uA5gSkCa62QSAwJAhUEX0VmPGI/TNf8syO3M1mmZmZ/cdBDyLoaKK9Dim70Jt2OqSqoIHuVMqWrC09qadctmQ19KGzDhEsn8SXWh0i+d3gSYdIKnrQlVayhbGmG420kS2U5am+qNYhkqMemJmFNwO/CRIgax4VwAAAAABJRU5ErkJggg==>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAZCAYAAABdEVzWAAAB3ElEQVR4Xu2VvStHURjHH5GXlLcsrEqJQgwWGSQDkoHBKsVsUxaTYmAwMfoLZPOyGZgo78kgyaC8FRLxfDvn/H7Pfe45ugYy3E99u+f7fc6559zf/Z1ziVL+D3068NCkg9+knvVqr++s1mg5wxlrQIc+KljXrE/WBas0Ws4wxXpkPbNGVA1gfI1tl7NeWB+sCVYXa8n2ubF9viWfzKIcOWQGN4sMHLHWhT9gbQsPMC7kq+wVv2gi7nXANJB5UkcJxScFyMpsu9J6ifaTlPAVAgweV1mjzR17yjuQLSsvkT6PEr5Cxx2ZG2yIDL9iu/Co60mBzt9Yw7bdyRpVtR+RS9kJICyqN9IjvgCHL4dfYd2KbJrVL3xiqim6uMNo2bsAEMolenPVkdnVWyLz0k1mW4MOyk62n+kRXkAol+A8c8hNVMw6FrUYvhtfUjQPLSCUO2ZYPcLjvqvCn4t2hEEK3xh5m20/Wa9BFnrqQtaVytB/Ufh50Y6AQ9Q3IZD5kPIOZC06tMhz0KEXtiDaMdAZu0YCj7NLgn5jws/azMccmeNCs8NaEz74Kh0PZCY5sVdsd00RmdoumY2BTws+Xxq8wtCEBZR9GPz58Vn7M051oKglc9hu6kJKSkrKD/kCEAKGlz5m75wAAAAASUVORK5CYII=>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAaCAYAAAAaAmTUAAACS0lEQVR4Xu2WvWsVQRTFj5qIJijYmEYNKWzFzqigGCEKYiOWkmAh2GgjMf4JYmUh6P8giJBGUkUb0wgigqhgISJR4xd+a0i8J3c2b97JvJ3Vt7Hx/eDw3px75w47Mzs7QIf/h2E12mSnGn9Lv+ma6Yppo8RSnDZdULMGFtT4Ey7DC4yE9jbTa9P3pYzlbDW9VDNiFl6zkPIMzfHHUWzA9D5qV2I1vNBtDQTmTPNqBthvnZrCTdM9eO5uiZEu0yM1A19MR9Usg4NwhloxBM85KP4e0w/xUrDv2vD7U2LkjOmImoHtSK9okhfIJxcrd138X6j2rnwMv3wQ1uFKxMxIW2GfHjWV/fDEKfGVTfC8D+LTWy+essN0LvzfC+9zpxFeJDeZjF9SU+HMMjG350/A8+5H3obg5bhhWhO12Uf73ZW2MokK2zlVOMUTeB6P4IIDwcuhOReDV6wWa+a+UfxMaJ0mNqP6w6TyTia8FMX7EhPXexUHWjCOzFhceiZ804BwHJ6nx/Zo8MvgV3xMTeMhvG/Vk4o1snmpGVda5Qwi7cdMYPnJRXrhfblqehikuIr8WIvFypKew+PdGkDjhCujLM6PMON893LcMn1VMwULPlDTeAM/7cpgX34MU5yFx1dpIHAY5Q8bwzxetSpR3J+m4e8Q/+9qykjDvOJUKuC2+mR6F8QZPdSU0eCtGi3gONwJK8p502c1a2YLqq9g23Cg1EteF7w1H1NzpeDef6pmTfQhf2+rHd6bTqlZA/9seymjarTJPjU6dOhQD78BqRyWmBpJICMAAAAASUVORK5CYII=>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAAA3klEQVR4XmNgGAWUgnlA/BmI/0PxAhRZCPjLgJAHYWdUaUyArBgb2AfEKuiC2AAjEG8H4vUMEMOCUKXBAJclGCAfiE2gbFyu+4MugAu8RWJ/YIAYxockpgbEnUh8vADZJaBwAfFvIoktA2IeJD5OAAqvzWhi6F7F5m2sADm8kMVABnRD+b+Q5PCCd+gCUABznTYQt6DJ4QS4vLCbASJ3D4g50eSwAhYg3osuCAVMDJhhhxMwA/EbID6JLoEEvgHxD3RBdLAKiD8yQNIXKF2B8h42oA/E2eiCo2AUDGkAAM4NNN65dbHtAAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,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>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD8AAAAaCAYAAAAAPoRaAAABz0lEQVR4Xu2XOy8FQRTHj0ckBFFoiBIFEY34AqLQKNTiCyiIz6Agaq2oJCgIBYlHJyGhFCRCoVB4xDue4Zyc2Th7srt3d+beWzC/5J/s/P/3zpyZnbm7F8Dj8fxnZlCPqG+j2VDKfMFvTuoJx0XhCsI1PKAGRD6i8nOR5UR+MYptVLM2i8w6cH1NOkCqgLMWHeSiBLWGWgLuQK5oQNyipGFHG5bE3Zw+1KE200Jbpstcxw3wqY0M7GrDkqjaVlFjysvEjbi+Ax6gVnitqEnRzsq+NixoA65rWnjPqEbRtkKuJp1rap8Ibw5VLdpZOdCGBfPAddWjGsy13gWZofNOW0eiO3YdJB+TD2oaRa2gNk17UH4oK/K8S486njLtd5ElUQncl9ZRhBcoLcHke027THjW3GrDEHTcjhpXWRx1qP4InUZ4gdLQAVzLhPJfjU/jWhG3chvA2RnwHXXBddsvA9dSo/xu49PiZqYctaVNQynkYVsZXCefVEdSFgudmWvUng4EL8BbyxWXyVdA8gSPgbNFHcSxgLoHfr7Tc53e3aPoRA1r0wLbyT8B10d10v+PD9SQyN9Ql6gL4Bvp8iJWMGwn/yeg3w+Px+PxeDyF5wfiqYDaoZzSCQAAAABJRU5ErkJggg==>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAAA1UlEQVR4XmNgGAWUgtlA/AmI/yPhVygqGBi+IMmBsDeqNCaAKcQGmoD4PLogLsDIADHoFroEEFwGYl90QXwgmwFiWDiSGBMQ/wNiLiQxosBLBlQvGgLxUyQ+SQA5vKZB2ccQ0qQBkOYLDBAXakH5uCIDL4CF1x8ksSVQsXwkMaLAawbsriDLdbg0vWWAiCuiS+ACzAwQDafRJYBAlQEi9x5dAhfoZ4BoCEWXgAKYqwXRJZDBMgZIfnwHxV8ZIAkUBmQYIC4CpbXHDBC195DkR8EoGLoAALqKPUMnIoY7AAAAAElFTkSuQmCC>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHgAAAAZCAYAAAD6zOotAAADNElEQVR4Xu2YW6hNURSGB7mGolwevIkIKfJELiFKyAMpRUIuJUV4oCi5PfCg8ECRUnJ5QCGKkkRRXtyK2LlLolzLdfzmmO2xx5lnm3ud09lOja/+zhz/WHOuufdYZ62xNpHjOI7jOP8rPVm/WWNtwmlxulOoRSHOWUPYTWHRSzbhtAi9WE8p1CCqENUmDrWGUxNnrVGQwgVuSwUnOlnUtcB9WD8oTJwqmiy59qwlrJ2szeKBBaxtrJMSD2EdYE2PBzADWftZW5VnWcN6ydprExkMYq1k7WGNEW826yCrbzyImc86zpqrvEg/1nnWXdYy1o3K9F/msJ6z7lHYbxHqWuDVrMMUJmIMrZBcNwqFQ+6yeGCLeFCJwnFtJH7GusIaJ8dibDfVUbx5Eo+SGBdULlj/DIV5S1lXxR8gHtb8RGFfncW7JceAaaz7Kh5MDff5nSqLjvxNFedS1wIDXPnVJiKnCwxwVcPvpLxV4i1UHoA3TMVfWJ9VDHAXeWu8HFIfOuVdMB7OdVTFQOfvmBgg3mW8HFplgUvia5YnPABvvIlx18DjIcoWIBfMOZTw7Fqnjbdd4vestawOKgeQ+2a8fzGyEV1LeBB6n1pIfa4sihT4kfiaxQkPwJsg4/4SH2FNSqhWsNa+hGf3gX7BevGiijqlcohrfTWc0YjwaLAehEdVLaQ+VxazqHLidTUGqQI/FF+zKOEBXeAYo8DNAdbCu7r17D7QaGmvtxrjMXObQh4/JgCM0U80B3W/Rc+kyom4bWlSBS6Jr6n2HzzRxD9VHClZIwOshU7aenYfJ4yHse4foofmDHyU2KIbs1zqXuB2FCaOlvirygHkbPeIJsWebL14uhvuKh5eNyJ45sLbobwprA0qzgXrHEt4dm+2m8f4iYqjF+khcezOwQhqeLfIoe4FBhupvEAX8fBMRCHRMeN9NXa+78TDLeyNHIcr/oV4r1gXWQ8ozIOHHLrnCJqax1Q+JzrwWkA3+5rC2tjLBwo/62G/0YtdOe5Icb+Yg/dZnHO4/IV+UXjFsuifCdeZXC5NLTA+W/weIYzhtUo2UfkLrabWRFML7DiO4ziO4ziO4zQPfwBGyBle0RPuDAAAAABJRU5ErkJggg==>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAAf0lEQVR4XmNgGAUjDZxBF6AmOAnE/5EwyYAViEvRBfGAIgYyLeJgoJNFPAx0soiXYShbZIIF2wPxJCziIIwNEGWRHxYcDsQLsIiDMDZAlEXYAE2CDhsYtBZ1MUAsEkWXIASItegXEL8A4idA/BhKvwbixciK8AFiLRoFo2CkAwAtOCUn2On9ZQAAAABJRU5ErkJggg==>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJEAAAAWCAYAAADAbX5DAAAFLklEQVR4Xu2ZV6glRRCGy7gmzD4YFyOLgoo+iGIAFRRB1DU8mFYUs5gwo3hREUFFFAOY9kURE7iuiBFXRBADmFDBhwUD5pyz/W113a3z355zjsoVdpkP6t7pv2v6zPR011T3mPX09PT09PT09GS2K/ZFsb+KvVBszcHqSS4p9m2xH4sdJ3WjuN+8/beKrSJ1SwvLF/tVxQR99oN5PzwmdZlrzdvhmewqdcNYtdgT5u2/VGyZwerp46RiN6TyXeYXsUPSgIf/ZCq/Wez5VO5iBfP2Nqnl5Wp5/UmPJZ93zO8prMUrxebU4+gDbMakh/NNsStS+adiV6VyFxuat7dyLa9Ty8tOekwjrRtXbXUpB2hdUSt4rtgHol1j7faWdIjSrfviQf5miycSEDXwzZFrr6pl1m5oLYhw94r2crGfRZsWeMB6kTqIXpVygHa7igI+N4u2S9WXNroG0b42tU9BNQaU+gDakSoK+Bwm2kVV/9+JH94vaXqzQZceRNi+WPSZVZ8terBusZOLXVf/wz7F7i62TTgVDip2X7HTkxYw+xng75u/Hs4ZrG5yarGnir1d7HypG4euQQR3FNtUNO0/jolYCvrrKiZ2N/fR/GlO1YlmLWaZ992NxXar2qHF7jR/PQZHm/fz4Unr5EDzH71edL3ZoEsPtjevP1v09are9aA2K3abuc+txd6rOoML7VzzzuaVwGBB+7r6QAzernKLhTbow6tg1DnKsEGksLjAl0EeUKYNBZ3cqIszzX00j2VAoO8kerBHsYfNfU40Tz1gy6rxxvjePEEn10KjX4KN0vEiyFNYQf1h/m7OcHKrc7r0YE/zeo0Ua1WdgTKMVvsknmgrJu3CqgVEFD1vnpSVB23qOZSvFG0Y/2QQscJVX8pfigatfshcZl6/rehEavQjRFda7be0x0VjvDSJLP+RpLUahC492Mq8npmSiYhyuegKPgtF+6TqmbNEi2QUY+WZE9pxiYH+kFYMYdxBdIa5HxEyg5YjaoD+p4qJE8x9iPyZQ6quQUHBZ25D03thImaNFKMTbUDLQZceEAapJ1JkNq76ODOErYVMayFwWkMjEY3rw1oPR4k9FjqLJDWOx2WcQbSjdQ8Izv1FRXP9XRUTkRPtLPpRVc/5TQt8dPET/ZZ5oKEtgteXvlaigUjUvqtlBY0kdBitC4zV2ai9Inw0oSSH0Gs5RTTde4lwPyF6hnp9uGjkDOMyahARgTW30ZyodT7aLSomuF98/u3qDJ9x8mCS66ytwZ+Dq6jOoUW4jVmpoDGzgpXM85EMg1QHwnnWbk/Bh03NTCsSaQ50abELUhleM480LSIyHis62vxix5gn+6MYNojoy69UtEF/JpueH9GcTdtgA/N8J4MPr+7Mo1UfBT6s0FTTc+OrQ/BMHCDmmUtyhsYFZNDY3Q6urlomfnjrpBHNWn56wy3wyzMVeC1pexFpYtBP1HLm42J7i5bBP3+KmFu1N8zbWy3VddFKloPoG7VW9MvbGC/a1BVbnJtpRR3Ks0VrgZ9uVLZ+41nRFsQBSSg3QuXn9f9NUZmIJR43xaxmJ1S/zRxg/s1GicjDhbKhxj7EMPY3T6AZQEQeviEB/ymjf2o+QHnVfli1j8xfPxPmURaf6IzjbThbFPvdFvszEYg+HOvrWOEa+G2uAeN6WGVtXuvJ/aJdNVY8mZlVf9p8a4O2FKJsK+G/xzzy8582dEGj8I2OyRX9zARl++WzpHEMRNHoe85h321Brevp6enp6enp6enp+S/8DdQhxfCjd0Y7AAAAAElFTkSuQmCC>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH8AAAAWCAYAAADpRkOBAAAESUlEQVR4Xu2ZW6hWRRTHV1fCEDUVETPDB4N68UURkR7sQRAiiiykAo2gu6iVGgRJ9RCUKFEJRkFEd4iIHoKQtF6yiCjChwyELkSZkVZkd9fvrJnj2uubmfMpJXTaP1h8Z/6z9uw9ay57zT4iPT09PT09Pf9X7lS7OYoNflC7X2222ulqi9Q+6HiMH8aKzRa139QOqi0JdWPxstrfanvVJoS6f5XnxR6am2O3dKub5Gu8ret4/LcZNjaH1B5w5V/UHnTlGmeItXteKp+WyjNHPU4irQ6WwP9utafVbgx1441abC4Rq/OcU9BKvKP2ZdAeluGu/cepdbDGH1EYx9Rik3eGCNq1UQzg83jQFif9pFPrYI3fozAEV6vdo/ZMKk9Wu1dtzaiHbYf3qT2W6iMr1T5We1PtYrX3utUDsBIfVftc7Q21qd3qoajFBr0UB3SesUbe4omFZ07Srwh6ZppY7rE1/cIytWfVLspOyuVqL0k3rpmJUYBaB2v8KjZAvPNeELuemdtik9oRMV/ei2ybwECiLRcbKLgyaSSUmXfVbnBlVs43rlyCNp5Lf09K5c2jtcNRiw364SiK6bz7a8wX81kf9OlJ3xj0zFy1J8R8dohNaGBSoN0lNhnPVjs1aSTmmXOl8lw43hrFBnSaWZdZKNYGK60Fg4dfzJ7RPitor4TyBa4Mwww+Qcnk7Pp4qMUG/fsoiumteywVq48rc0rSGeAWpfZZhGhnOo2czPvR9xjjEXC6PYrHCW2UVoJnlQw+OKBdVdB2ufLPSftQbPs/EU4kqarFBt2vrAz6X1F0zBPzWRv0vII5QrfAZ3/QWASxX5y+vMZijT4jIMaZ2IJ3c4Q2io07SIRKPmhs+1F7O2g/Jj3bpd3qAdgp/hTb7lgJT0r5/i1qsUHn9RdB3xdFxyliPjyPh1cc+jVBj+DDdwEPJ4fYr9sK2kOhPAJOcSbWuE7M32+nkAekBR0r+aCNNfi8EzPnSz3bzlwmVs9vhiSrdU2JWmxq/UXbHsUAPrVsf6yzPj4xofwi6R7yFK+R8xTBqfaRZoXaDFe+Xsx/ltMA7dOgRVbJ4EMCWmnwOQ/7cqSkZUqDs81psa5GLTYMXmwjr2q/M54lgzkDu1EcwA0y2F4JfD4JWmnlc0+vvSX2JbZDftfwPozkzsSGY/n1glbiDjE/n5hMSNpqp0HsJGX/NY2jYOue5Aaxnmw4a8N8q2jFBqjzxyyOnjHvyfG70Gl8Bo7PRvmRoJXAj5XuIfeI7XFkRuNoCbvEZftkfwfEZg2N8UviwHbqeVXs+7YnByVnmTTKRGnxk9pXYvf6Wm232kfpbzTqSOp4rfAc+ZlyRs0x8SY5Fkzq+L9CizwpMY6UsEftO2lfO2xs5oi1vVPs6EUfIrx23o+iHFvpL4q1+1S3egDyGx8X/pcA/Obn/FZsYpEb+Vi/Jjb4C+ySnp6enp6enp6ecctRldFeTMDg5dAAAAAASUVORK5CYII=>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJEAAAAWCAYAAADAbX5DAAAE/0lEQVR4Xu2ZV6glRRCGyxzBjJjBAKJgehHjPigIgph9MK0oZhEFxfCgVxHxwbgmUHFfFDOYUVG86osYQFdRwYfFhDnnbH23urBO3Z45c1xX8NIfFGf67+qemZqZmuo5Io1Go9FoNBqNyPZqn6v9qfa82pqj3SMsr/ZLFnvYUe1JtZ3UllXbXO1qtfuj0xxhXGwOVvtJLM4Pi8WjxhVi83BNdk99faym9oTY/C+qLTPavfQ4SW1BaN8mdhBc9MhbRXcbyt4yOg77ZMTj/8+Q2NypdlxovyHmu2rQ4Gu1S0L7R7XLQruLjcTmW6W01yntrhv1X6V24jXN+Ua6+2rMU3tE7Ra1i9VWH+2eU/TFJseU7E/7w6DtVbTI2hWtxvdqdyXtJbHMt9R5X2YfZD7hSF+gapCOL8riHKUvNr+q/RHaO4v5vhw0XmG18WhHZjGBz2FJO7/o/zm+431zR6EvUDV2k8lvonXVTla7qvzCPmq3q23rTsqBanernR40hzRO9ntP7PVw1mh3lVPF6rc31c5JfUOYJDZeu6wfNNrcbBn0RVkM7Cnmk+un+UUnm9XYWix216ntUbRD1W4Vez06R4vF+fCgdXKA2E6vyR2BSQIFu4hdfMbcofaD2rMjHrOh+L5ZbMxNau8WnZsL7WyxYFNIcrOgfVV8YLmidbVrLJZRH14F48ZkhsaGBwO/fFHQmCODTm3UxRliPrmO5YZAJ+vVmKf2oJjPiWrPFX2rou2q9p1YgU6thUZcnI3D9gyXq92j9rvYu7mLoYFyOLF3ksZ4P+A+8Mv7ovBEWzFo5xXNIaPkcQ+kduY+mT2G9qVJ62NIbK4UW5lxccgEEcZ+kTSoxSFCrUn/dkknU6MfkfRMbf6a9njSuF+qeJXPidYYEqhxfCTD5sBncdI+LnrkzKR5MYotUNs09A1lLbHxk3yKmCQ2vmolqzq0Y0Z10GM9lTlBzGeHpB9S9L6kAPgsrGj5XHgQo0aJ0UltAmeSQHUxLTZHrAdq4MNSOFJbCJxW0ShE/Tyw2sXJeJ1CsChSfXsok8Ymx5ntn0PbQX87iwGviSgdIkcVPdY3NfC5oaLlc7m3os3A64v6I+IT5EINljRQ4PXGyknP4LMoaRTKeb5TkrZS2AZP91NJj9Cfn3Y0aoahdMVmDTH9+KR7bPyjYC1WgHZjFgOcLz7/dHWGT66Da8dCcR01zmvmC2rN2TUK0kxXoICbgnokgm9+d3YtZTP4vJ60WibKNdCFaueGNrwqlmlqbCI2/tikoz2kdoxYsT+OrthcK6azqIjk2JMN8nhuMLQVgrahWL0TwYdXd+TRoo8DH1ZoWctjuY5Re9o3EOOTS3GGxgHUIBB5csd3vE3QXhFb5jsbiPnMD1oX+JF5IryW8v490/hNP1XaEeow6pAu8H8stBcW7TWx+YZ8JO2KDWOzztdrtAuSjhY/Y7wgs1dsHudILevQPihpNfDLHypr+3gmadO+QRFKGqfzs/J7vXcGvhX7uspFxT4QW0lsEXz2F/vPJuOf+D0D9V1M2E+sgGY/ZB7+QwJ+aaPz1wmvW46LY0Hj+Hj9TIllWXw8GPlVktlS7Tf5258HgezDdq4XMkNi4w8nnyZYrrOdszZsJtb3lNinDebKkGVrBT+fUChP+GUOlv598B8dD5fHmQd0PbVPg8Y2fFna6Izhu9t06Ws0Go1Go9FoNBpLwl/U+rLfcEOgWAAAAABJRU5ErkJggg==>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIgAAAAWCAYAAAAb1tRhAAAEy0lEQVR4Xu2ZR4htRRCGyywqiqKiYECfiGGhbtWVAcWAGHBhQoRnzllQHAPqwoQLBRUdDJjBgGICF4aFujGDKA/MATMGzPVNdc3UrdPnnPcejjyG/uDn3v67+k6fc6rTGZFGo9FoNBqNFYNzVSdls/C96mjV+qr1VIepvpuIGOYh1T+qd1VrpbqFxo+qQ5P3mOpm1SLVSqqdVE+rdo5BAxyn+lz1p+qaVDev3Kf6XezhoZMnq2fx+qjNJiLqrCYWu0Upr1LKm85GLCxOELu+nCAvFT/q3omIfh5WfRbK96i+DeX/jbEEuVpsFOyZ6oZ4UfVJ8q4V+72FyNdST5AXVGep7ladk+rG4PdWrXj7Jm/eGUuQ5YF2JFVk1+IvNFiGoZYgz4stLcvKjVK/V3gfZHO++a8TxJeTi5O/ZfEPSb6zodhe6IbyCfuITck7epBysOpB1enBc1ZW3a76WHWl2P5qjFPEHuR7qgtS3RjHqI4t32sJ8pwsX4L48p/Bq/nOkarLxLYQsLnqOrF9pMN9vr74eYaqMpYg76veUb0itlka+1E2YLQ7O/kbFb/vIWytuk0s5lbVR8XngvDOU/2hWlssEfB89IInZl+5xhKZjHk9lcdgY+rUEuQZ1RliD3xaLObEGNBDXyL0+c4lMhdDcnJP4Suxe8d2wf8+CUJcTODqAYQgRlEN6tYI5aeKN8QeYjF5hHMSwicJhqjdhB+Kt3rwLiqewzXkdpwihnhEum0oX5W8Gl/K5M2lXU6Qx1VTobymWNxewatRuwfQ50fYzBKzQ/B2Kd5dwQO8+Jyqv415WjZ72E4snkztY1uxmDOT7zPBFcnPELMkeTyM3Hk2f9HboJTRTTJ3gloWPIkfzRWJ/aQ7AGiXE6SG93GIvpg+PzIt3Zjti7dx8vGmUrkDZr5Yh2k64lM763UfjCpiGOER1kN81skhiOG9SYQTUe78qRXvqOK54hLUx7Niscw2h4fvQ/yaDbF2OUE47me8b0OwlNdilqYte7Acs03x8rsovMtDudbfmaA82oHdMnVMi846xeN8PwQxfaeYsXchxLyZPDad+aLZN0UvLoXAhVM/lfwI9X9XPJaGITjGR/nehYFDGZjB8J4sZQcvX0uG/UMtptbfjO/jIouKN5Yg64bvsxDEdJ1hk/hz8jiDE39E8EigvIf5S7oP+XzpdrwGMW8nrzaD5D3HpaoLQxneEJshaviMxtvKCN4TYqcT3+SN4ctqnEFoi7d38ACPGSLCEh/3V5tI93oBb+x9yrR02w7NIHHJz+1m9wW8xMpwAz9M3m/SnV5pj+KmaPfiRSizNxiDOGaMCEtF/j2fIXwZnCrlyBcyvCEknlffzp3Fe0vs95gxl4bdxNodn3w8lmXHN9ZxVvZTX+47M8X9oby/dGNqkNw5zmfvrZKPd0sqz8D/SHj7x8jkYfDJRpDjWIRzPo0+LZ8vT1bPcJDqtWzK3IzxgNjv3jFZ3eFAsT54f74pPp/eT45rJN9PYn3C438VflpgBBPjN3yxDMPI8vUekeQ+8vMS2QdHQ+8L/YxHRZKDa+eI6X+jlnSvqg7IplhbXjOwbPW1jTCQ/F4xOJgdGNS8ssfj8xexZYh67zOnRGDVaDQajUaj0Wg0Viz+Bbtfh4GHrSADAAAAAElFTkSuQmCC>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHYAAAAWCAYAAAAVU2hLAAADi0lEQVR4Xu2YWchNURTHFxlChgxRUvIiL5ISSkreRIYMCblKxnwZy1QkDx48SHiRBwlJpEiiZHgwRkR5IDKLRMg8rP+397533fWtc+45Ot/3cNu/+nfv/q91ztln73P2cIgikUgkEok0N51YZ1l/WTdYrarDqWxj/WT9Yu1XsXpiNWuxNmswhvWAXLseVLFmpy+5C3fw5R6+3LqckcxH1lD/PxwH1QuHWT+ocl9LqsOprGT9EeVF1MJt84V1RHk3Wd+UpxnOesPqLLxh5Cp/S3j1Qt6ORf4gw8MI1yLgYtOVt977aaCCyLmn/Hp7awN5OnYS2W3wnWy/cEaTu9Ao5c/1fnfla46yuiivVsfOYG1kHfDlbqxNrIZyBlFb1hbWbh/XzGTdZZ0jdw/Xq8NNwH3sYj1lnSE3beQlT8eeJ7sNHpPtB4pqG1pO7kJhngxM8z6G2zyMJHccOjyJteSGeeThrR/rfXQSvHHkOgFM9V4/XwZXWfNFeQ+5KSENnOOQ/9/VlzeXo9nI07EfyO7A+2T7gcLaBj2P4GARBJO9P0v5tcAxcsGQBC6OXL3KhPfQ8I6r8kBRBlk6do0o48FLa2AL5C/VZgLItc5/h2xfUkjbLPCFISIIwtMQnpgsHGP91mYCJbJvEJ6e7+FdEGUs9uDdJj/s/Afbyb5+Gshfps0EXpJ9fqxHLF9SIjsnT9uU51gMoZI53sdWKAsLyQ0/WZlNyZXHcKO9S8r75P2gCdXhJuApxkP3lbWOtY/s66eBfDnXpZE0xz4i25cU0TbUnlxQPwlZVsWBEawnyqt1LIZ4KydL5XuJ//2pss9MYiK5OH4DWKCkHWOBfKxJsrCB7PNnWRUX1TaNwZ3SYE57X4IFVW/l9SE3b2j0sZoS2TlJlb+syhrLCyCm4zuEp2NJIG+FNj0YotspD/l6VwHvpPI0JbLrlLttrLcT5SmijE+MuoHaCE/risizWEUuTzZGR+/NEx6AJ/fKKG8VZSz5df0lmIt1HJ9Ag4dPobXoSS4fc7MG6xPdNuA1ue1NAC8BcrBdSaPItmn8dIY5CL8IWkPOCXLfSwN7qXJDWpjHkvjMesF6xnrFukjurcd/eIhhEYB5HqtdeM9Z73Ewue1A+DwHIYaHLI1TVMnH1gFcY72j9GOxen5L7hqhHqgThn8J9tHjlQdwfuSHEXBAdbgJRbVNJBKJRCKRSCQr/wBFdkY2KeB/fAAAAABJRU5ErkJggg==>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIgAAAAWCAYAAAAb1tRhAAAEvElEQVR4Xu2ZR6glRRSGj1lUFAPiQsWEY9joxoW6G0ExIGJAzDiYA4qKuhCvARWMKGbBQUyYMICYFoIJ1I0ZDDwxB8yY4/mmqpxz/1vdfWfgyfioDw59z1+n+lVVV1ed6mfWaDQajUajsWxwuttxKma+dTvUbW23tdz2c/tmLKKbjd3ed/vb7TW3NcdK5x7fu+2rYmYTt88sjcXD40W9HOn2qdsfbpdI2axyl9tvlhqMHT9e/C+lPNqGYxF1GKgXgj9jqe7eQZtLHGOpf7UJcoPb78F/wO3x4Hdxn9snwb/d7evg/2cMTZCL3a5zmy9lfVBv/4qGzUW+tPoEYcy0z/iszEMQt2JF2020WWdogiwNtclQBnFr0f/vlIddmyBo74i2gfg1rrLJ8QO0d1WcbWZjgpDTHCjar5bu15WLrGep3pX5Cru63eG2bQly9nG7x+3koBWWd7vF7UO3Cy3lV0Oc4PaU21tuZ0rZEIe5HZF/6wShn2jXZJ++rLS4uJey/Su1Fy9ysNt5llII2Mjtckt5ZIFxviLrukJVGZogb7u94fa8pWRpqptWGOrcZm43W4q5ye2DrNMhtDMs7eWrW5oIaHGpXiFrXX6NGRuPeVn8IUhMC9SLE4RJjna2pXyCdj9t6eEP0TVWXXrhHFsc86SlMYUvLI0d6cKxWWOCELdc9qF6ACGIt6gGZasE/9GsLSnXWqo3Twsq1Abhu6ytHDQGPsbRB633kPjK/TZZB/8i0Wp8buODS704QW7MWu3+r4im1OpBlx4hmSVmm6Btn7XbggZocSWu3hvxJBU72MpSPDN1Wta1VGcHLeiA2BnReBja+FNFWyf72NWWjtlLCsd56j+oBcLuNrnFUS9OkEuzdmfQ4M+s91H6oXTpkYU2GUPeh7a+6Ggj8SdA1M4WWKYjZWlnv54G3jDi2Qunhfg3Rfso65ETK9ohWSs2zWnhCUuxrDYHhN99/KyCpXpxghyetQVBA7YlbbfCVl6LKf3qgxxMY7bI2mqio50f/GqORNApKlrKlilbNWhrZO3ZoPVBLHtvgcHaPPg1qPOqaCSd2mnypqjFrRDoOOUj0SOU/1XRhj5mPSNWchdeHHzgwyKafoT8Met9kD/UYmrtVUoeF2HM0YYmSPUAQRDLtUKSSGcinMGJPyhoTKBaDvOLTSa0JLtDcP/XRautIJpznOt2VvCBvZ4VogarGvX5WhlBe8TS6aQkeUNsaale7ZjLG62a9oUtPuZXHIU1BtBOU1FYaJN1+1aQC8Qfo5wQLtMCSwP4nmg8dF1eS4djUsTkKrraEMSwYkTYKrRuWSHKNjjKfoTP27uIFiH+seDfmjX+NTCytGJOw06W6h0tOpNP24Q/P/jbZU3jWCnuDv4eNhlTg8mtcTtmbVPR0a4XfxH3WvpwxZvJw+BKIqhHMM75VPo4X58bL14En89fEq10uGZd7GWpDaU9X2Wda2knx7Wd3X6w1CY0/lfBljCy9AYTU/7WUdYPb1bZ7zEmOasGv/l6PA0cDUtbaKceFUmYuR8vG1f9wgwvuu2poqXnwWcGti3qDk1YXqQyVrwcrA681HyyR+P6k6VtiPLSZk6JUD4tNBqNRqPRaDQayw7/AGY4juMmd48KAAAAAElFTkSuQmCC>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHYAAAAWCAYAAAAVU2hLAAADIElEQVR4Xu2YS8hNURTHF3mEAXlkIGVmJhl4JRMDJRJ5JOQjeUaEQoowMDCQMDOQ8kjJQBITj4lnIiMZeSSRPPOO9f/22veus+4++57zle9ct/2rf/eu/1rnnn3XvneffQ5RIpFIJBKJf80A1hXWH9ZdVo9sOpf3rH2skaxerIms+5mK9mEra601I1TemxHkJrSfxEMk7lmryAd1VpszFf83p1k/qP7d1mXTUWxfur03X1hnjXeP9c14ITDYHawTrNUm1250ZWIr7Q0GsMB4O8Vvxi9rtDFlJ7bS3kwlN+Apxl8m/mDjW35aowALWbtYJyUexNrN2lirIOrN2ss6KnnLItYj1lVy3+FONt0AvscR1jPWZXKXm7KUndgqe0ObyA14XDZH88WfYHzLd3In+MA6Q+6YyZmKRraTW+ZRe4A1TXxMErwZ5CYBzBMPGxDPLdZKFR9jvVZxCHzGKXk/UOI9tWwxyk5spb3BzCM5RiXBHPEXG9/ykTVdxePJHdfsn46To87uMuE9DXjnTTxaxaDIxG5T8TnxyoD69daMUGlvVkkwViWB/zX4X0wZcBy+VIwOCjcWnr3ew7umYmz24D0gWXa6wEEKnz8G6jdYsyTd1ZvaNXaSSoKl4uNWKAbWewuOCw1Ms4TCNfCw3FjvhvE+ie81K5tuAL/i36yv5Haqxyl8/hio19e6ZlTZG+pLLml/CUV2xX7y9RIHigweS3yopsjgh6n3o6h+n5nHbHJ5vHqwQYkdEwL12JMUoRV605k8rA3mkvgabKiGq3gFuRr7r4b3xHiWDmr8fJA3+JsmtoQ8T6iZh5Rnc3mgLu8BA5boPipuid6E/p2I56oYjxhDDbLxxYAXYgu5Ot2M/uItVx6A99jE+1WMLX/snLgW2zxuRbxX5H5zKLl6XJst2J+0am86H53hGoRXJENLzgVyz0s1/gtjS49XXMOaPWf+zHrJes56xbrOeijv4SGHTQCWM+x24b1gvcPB5G4H1lC9mcjhWWwM31QItw7gNustxY/F7vkNuXP4cWBMWP41uI+eabwqe5NIJBKJRCKRKMpfMXk8Z9pKZlEAAAAASUVORK5CYII=>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH8AAAAWCAYAAADpRkOBAAAESElEQVR4Xu2ZWahNURjHP2TKPIUMRSKUDJlFojzJ7AVdmTKHyJxLknggDx5QHiRTypAh5F7kBQ9mEp1rHqIMmcfvf9da+fZ31trnOte95dq/+t9zvv/61tl7r7X3WmuvS5SQkJCQkJDwv1GNdYL1k3WRVS5aHEt/1m0ydXeqMtCJdYrVmVWe1ZK1kXVAJpUBlrPesj6wJqqyOBqwUmTa7w6rdbS4ZGlC5sBVbVzPxuioTMxj/RDxVDJ1JQOtJ/UikvHvc5N1UsTXWedFHAIPRp6IJ5Fpn1nCK1Hes/Yo7xLrk/J84ETbery1Iu7HOsLaxlrFqi7KygI1Kf2GB/Bqa1OBNpYPHnAPSKmAA41W3hLrxzGU/DmfKer3Ya0UcVnjMvnbAR5u+Dh2U3rdUuv8vmQOhA6S5Fi/rvIlp8l/kimK+r3pzzu/Pmsaa4P9BIPIrCnauyRmGGsva7bwHJi20PgPWatZ86PFXmaQWZ/cYi1UZSFCnRXy4+hFps46XSD4G21TA3/mkDkYFmOSUdbvrnzJa/Jf3A2K+j3JnBi8XWQWRGdFuQ8sCreSqbOF9cD6uHB4C1hfySxU0cnwcD6OCtYLxT5SFM3B1JepDgh1csgP0Y1M/hldoChu2zRlfcQXzMEo7CAKAe4a+GOULwld3BWK+rix7osYoPyc8nz4jvHGepWEt9h6DjzBut5BFWv2U3odxGuUp/GdIwj5PtazdpDJz1FlIXy/X5S22ce6iy9TbEFHUQhGWn+A8iVPKP3gACtdny95RplzAHJSyntufclc5WG6co2zidVclBWVOmTqZ3ol9XUCCPlxVCRTp0D5PrJtG0wRhbGb8zE0S8ZZH6+BIUJz/j3y+5J8MjkNla9BDl6jJI+sL5np8cZaz0kOfSHcXgdGCSyC3fc43O9rQn4mXL02ukBRnLbBSEOVbUE2q/2l5M/Rq31fI7j5tIryNci5qjws4PTvTVcerkviprdc5UtQLvcsnHdIeZp3lH4+AB4WjnHgNfuC8r6RqbtM+Zps26aW+F5YgKFRctT6EiwC9ZOKHP1GAO+wijHPSL5YPxPIwTQi8d3deo5fwVokYoC1CJ5sH83I1J+gfHct48kstHy4EUIDr4uIcaPjPB1uM03XdZ7eP9Fk2zZ5rB4u8D3liIeLGNu9vhPF3J0ScSMyOZi7HHgPxuueozGZnBzhhUAe7maJ7y3DPdlY1YNcG0twrthtDIH84yLebr1rZH4vbnMKedjddGBY1cd37ddOeS1E7DaMUsILkW3b5JNd7TvwCvbdfiIRr4AaLHx878ovySw03Gjhe0IwN6HMPfFxnQAGk/lNXBzu5lfWxydi+Ngixv4Eht3H1ntKZpjOZY2wOa7RJ1M8rej3kOs6CdeC75tFng/s0CEPQzhGGOzc6f+PDCHzfxMJOgQdgboF9vOYTPBQ3LbJZ3U1VRISEhISEhISEsosvwB614Ep2sp3owAAAABJRU5ErkJggg==>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH8AAAAWCAYAAADpRkOBAAAEJUlEQVR4Xu2ZWahNURjHPzMhmZIMmV5QQpnFA+UJGV8QyZAhUWQouYa8eCDFA0oeZEpxDUnKxZspLplSN1OGIkPm8fvftVb3299Ze5+z90E51q/+9+z1X9/aw1prr2FfokAgEAgEAv8bjVmnWT9Zl1i1otmxvGatZ3Vg1WUNZF2JRBD1YZ1h9WXVZnVhbWEdkUElAurgizbzgDKVZOr+OZn6+Wu0I3PhRjbd0qbRUPlAnNaSSATRSJHn9CIS8e9zh6LPl4avFH3Z3rBmifQf5T3rgPIusz4pzwcedCVrD2uuynMMZ51g7WKtYzWJZpcUbyld45ezumuT0p2jKHChycpbZf18fNOGh6GstdosUdI2PmL3Kw+jQJpzZGYYmQuhgSTTrd9C+RoMWfkYQukbvxVrHmuz/QWjWHtZPV0QM451kLVIeA5MWxhtHrE2sJZGs70sILM+uc1arvIKIW3ju3XWfeFdZa0Wac3vqJum+LOYzMWxGJNMsv4A5Ws+s7aRmafQg1FmcCSCaBCZG0PePtYH1vlIRC5Y9OwkU2YH66H18eDwlpHpeFioopHhYfHpqGO9uLSPKorGYOrLV0aTtvEB4p3ussoiubkUWzftWR9xgDkYmb1EJkCvgT9F+Ro8LHqdoz+ZcnLEQMd6INIAMReU58NVigQdDV594WHdIePwButyR1Vac5hyyyC9UXlJZGn8hlTznNCraHYsWevmENmRZo7N6C0ywUTrj1B+IaAcKiGJZ5R74z4QU6U8bId0WewwpIfO5ypnK6ujyCuU5mTKp9mSpm38zmTiMc93sseF1B/IWjd4WavTbs7H0CyZZn1sA5Oopw2qeYAkKsjEtFG+BjG3lPfY+pKFHm+q9Zzk0BeHm4MxSmAR7I4LJW3jIxbDteSc9VsrX1NM3WzCnwY2I8tq33UQzDESV9lxaeDmUwx5SSCmUnlYwOnzzVcenkviprcy5UuQ/8PjlSsviTSNj8aNi4W/QpuKrHXTTBxXZ2BolJy0vgSLQPmmziQTo0cHePdUGvOMBF/B9Pl9IOam8ny9W8/xayi38q6TebN94AslyuOZJPCOsWZQYV/ekhofHR33KYmLhY+FWRJZ6+YsmS+x1fjecqTHi7Tbe/riJMc93jUy2z1HWzIx04UXB+LQmyUYvvU13JuNVT0os2kJ1hn42hgH4k+J9G7r3SBzvkI+TmEno6/rcPXXQ3joLLpDjmG9U56PrHVTQXa178AW7Lv9RSC2gBosfPRe2W0v3CoTJ/X9XwBzE/LdG5/UCGA0mcULHg69+aX18Ys0fHwixvcJVNQT6z0lM0yXsSbYGFfpsymZbmQ+WslGwtuO4+0izgfuAdfGPUC4H6zau4qYsWT+b6LBKIlrYJuH34vR7ByKrZsKVj9TJBAIBAKBQCBQsvwCtmBuaiUdqn8AAAAASUVORK5CYII=>

[image25]: <data:image/png;base64,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>

[image26]: <data:image/png;base64,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>