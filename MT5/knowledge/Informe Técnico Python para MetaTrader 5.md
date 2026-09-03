# **Análisis Técnico de la API Oficial de MetaTrader 5 para Python: Arquitectura, Gestión de Datos y Ejecución Transaccional**

La integración de algoritmos de negociación cuantitativa con plataformas de corretaje requiere interfaces de comunicación estables, eficientes y de baja latencia.1 La librería oficial de Python para MetaTrader 5 (el paquete MetaTrader5, también conocido como mt5) actúa como un puente de integración nativo que permite el control programático del terminal de trading.1 Este informe técnico analiza la arquitectura de la API, detalla los protocolos de extracción de datos históricos y en tiempo real, expone las especificaciones de la gestión de órdenes y posiciones, y presenta patrones de diseño avanzados para construir sistemas de trading algorítmico robustos y tolerantes a fallos.

## **1\. Setup, conexión e infraestructura multiterminal**

La API oficial de Python para MetaTrader 5 no es un cliente de red independiente que se conecta a los servidores del broker de forma directa; en su lugar, actúa como un cliente de comunicación interprocesos (IPC).1

### **Mecanismo de comunicación y requisitos del sistema**

La librería se comunica con el terminal de escritorio de MetaTrader 5 a través de tuberías nombradas (Named Pipes), un mecanismo de comunicación de baja latencia integrado en el kernel del sistema operativo Windows.3 Por este motivo, el uso de Windows es obligatorio para la ejecución nativa de la librería, y el terminal físico de MetaTrader 5 debe estar instalado y en ejecución en la misma máquina que aloja el proceso de Python.1  
La instalación básica del paquete se realiza a través de pip y es compatible con versiones de CPython desde la 3.6 hasta la 3.14 1:

Bash  
pip install MetaTrader5  
pip install \--upgrade MetaTrader5

### **Inicialización y autenticación en la cuenta de trading**

La inicialización del canal de comunicación se gestiona a través de la función mt5.initialize(), la cual admite diversos parámetros opcionales para automatizar la apertura del terminal y la autenticación de la cuenta 4:

| Parámetro | Tipo | Descripción |
| :---- | :---- | :---- |
| path | str | Ruta absoluta al ejecutable del terminal (terminal64.exe). Si es omitido, la API localiza el terminal en el registro de Windows.4 |
| login | int | Número identificador de la cuenta de trading (opcional).4 |
| password | str | Contraseña asociada a la cuenta de trading (opcional).4 |
| server | str | Nombre del servidor del broker de destino.4 |
| timeout | int | Límite de tiempo en milisegundos para establecer la conexión con el terminal (por defecto, 60 000 ms).4 |
| portable | bool | Indicador para ejecutar el terminal en modo portable, aislando la base de datos.4 |

La llamada a mt5.login() se puede realizar de forma independiente si ya se ha inicializado el terminal.1 Esta función autentica al cliente contra el servidor del broker, validando las credenciales transmitidas.1

### **Arquitectura de múltiples instancias concurrentes**

La limitación fundamental de la API nativa de Python es que el módulo MetaTrader5 solo puede enlazarse a una única Named Pipe activa por proceso, impidiendo la comunicación directa con múltiples terminales desde un único hilo de ejecución.3 Para gestionar múltiples brokers o cuentas concurrentes, se debe estructurar una arquitectura de procesos aislados 6:

1. **Aislamiento en modo portable**: Cada instancia de MetaTrader 5 debe estar instalada en directorios físicos separados y ejecutarse utilizando el parámetro portable=True.4 Esto fuerza al terminal a almacenar sus configuraciones, bases de datos y archivos de conexión dentro de su propia carpeta de instalación, evitando colisiones en la carpeta compartida de datos de usuario de Windows.6  
2. **Procesos distribuidos o microservicios**: El desarrollador debe orquestar procesos independientes de Python (utilizando la librería estándar multiprocessing o contenedores individuales), donde cada proceso inicializa una Named Pipe exclusiva apuntando a un ejecutable específico del terminal 6:

Python  
import multiprocessing  
import MetaTrader5 as mt5

def instanciar\_bot\_trading(ruta\_exe: str, cuenta: int, password: str, servidor: str):  
    \# Inicialización aislada dentro del proceso secundario  
    if not mt5.initialize(path=ruta\_exe, login=cuenta, password=password, server=servidor, portable=True):  
        print(f"Error al inicializar la cuenta {cuenta}: {mt5.last\_error()}")  
        return  
    \# Flujo operativo del bot...  
    mt5.shutdown()

## **2\. Extracción de datos históricos (Rates y Ticks)**

La obtención de series temporales históricas de precios es una de las mayores fortalezas de la API de Python, al retornar los datos directamente como arrays estructurados de NumPy, lo que minimiza la latencia de conversión y maximiza el rendimiento analítico.2

### **Funciones de obtención de barras históricas (Rates)**

Existen tres funciones principales para descargar datosOHLCV, las cuales varían según la referencia temporal o posicional utilizada para definir el rango de consulta 8:

* **copy\_rates\_from(symbol, timeframe, date\_from, count)**: Solicita un número específico de barras (count) hacia el pasado a partir de una fecha de inicio determinada (date\_from).9 Las barras se devuelven en orden cronológico, y la fecha de apertura de la última barra del array será menor o igual a la fecha especificada en date\_from.9  
* **copy\_rates\_from\_pos(symbol, timeframe, start\_pos, count)**: Recupera un número de barras (count) utilizando índices relativos de posición.10 El índice 0 representa la vela actual en desarrollo, y los índices positivos se desplazan hacia el pasado histórico.10  
* **copy\_rates\_range(symbol, timeframe, date\_from, date\_to)**: Extrae todas las velas completadas o en desarrollo comprendidas estrictamente dentro del intervalo de fechas cerrado definido por date\_from y date\_to.11

### **Marcos de tiempo (Timeframes) disponibles**

Los timeframes se definen mediante constantes de la librería 9:

| Constante de Timeframe | Intervalo | Constante de Timeframe | Intervalo |
| :---- | :---- | :---- | :---- |
| mt5.TIMEFRAME\_M1 | 1 Minuto | mt5.TIMEFRAME\_H1 | 1 Hora |
| mt5.TIMEFRAME\_M2 | 2 Minutos | mt5.TIMEFRAME\_H2 | 2 Horas |
| mt5.TIMEFRAME\_M3 | 3 Minutos | mt5.TIMEFRAME\_H3 | 3 Horas |
| mt5.TIMEFRAME\_M4 | 4 Minutos | mt5.TIMEFRAME\_H4 | 4 Horas |
| mt5.TIMEFRAME\_M5 | 5 Minutos | mt5.TIMEFRAME\_H6 | 6 Horas |
| mt5.TIMEFRAME\_M6 | 6 Minutos | mt5.TIMEFRAME\_H8 | 8 Horas |
| mt5.TIMEFRAME\_M10 | 10 Minutos | mt5.TIMEFRAME\_H12 | 12 Horas |
| mt5.TIMEFRAME\_M12 | 12 Minutos | mt5.TIMEFRAME\_D1 | 1 Día |
| mt5.TIMEFRAME\_M15 | 15 Minutos | mt5.TIMEFRAME\_W1 | 1 Semana |
| mt5.TIMEFRAME\_M20 | 20 Minutos | mt5.TIMEFRAME\_MN1 | 1 Mes |
| mt5.TIMEFRAME\_M30 | 30 Minutos |  |  |

Los datos de rates se retornan como un array estructurado de NumPy que contiene las columnas: time (timestamp Unix en segundos) 11, open, high, low, close, tick\_volume, spread (en puntos) y real\_volume.9

### **Funciones de obtención de ticks históricos**

Para el análisis de la microestructura del mercado o el desarrollo de estrategias de alta frecuencia, la librería provee acceso al flujo transaccional de ticks 8:

* **copy\_ticks\_from(symbol, date\_from, count, flags)**: Obtiene una cantidad fija de ticks (count) a partir de la fecha especificada (date\_from) moviéndose cronológicamente hacia adelante.12  
* **copy\_ticks\_range(symbol, date\_from, date\_to, flags)**: Recupera el conjunto completo de ticks ocurridos en el intervalo de tiempo definido por date\_from y date\_to.8

Los tipos de ticks solicitados se filtran mediante el parámetro flags usando máscaras de bits de la enumeración COPY\_TICKS 12:

| Constante de Filtro | Tipo de Ticks Retornados |
| :---- | :---- |
| mt5.COPY\_TICKS\_ALL | Retorna la totalidad de los ticks generados por el broker.12 |
| mt5.COPY\_TICKS\_INFO | Retorna únicamente ticks con cambios en las cotizaciones Bid y/o Ask.12 |
| mt5.COPY\_TICKS\_TRADE | Retorna únicamente ticks con cambios de precio Last y volumen transaccionado.12 |

El array estructurado de ticks de NumPy resultante contiene las columnas: time (Unix epoch en segundos) 12, bid, ask, last 12, volume 12, time\_msc (marca temporal con precisión de milisegundos), y flags (máscara de bits que describe la causa del tick, p. ej., mt5.TICK\_FLAG\_BID, mt5.TICK\_FLAG\_ASK, mt5.TICK\_FLAG\_BUY, mt5.TICK\_FLAG\_SELL).12

### **Tratamiento de zonas horarias**

El terminal de MetaTrader 5 opera de forma interna y almacena los datos históricos utilizando el huso horario del servidor del broker (habitualmente UTC+2 o UTC+3, sincronizado con la apertura del mercado de Nueva York).11 Sin embargo, la API de Python procesa las marcas de tiempo en el estándar de Tiempo Universal Coordinado (UTC) sin desfases.11  
Para evitar desfases en las consultas históricas, es indispensable instanciar los filtros temporales de Python usando marcas horarias en UTC de forma explícita, aplicando librerías de gestión de husos horarios como pytz o el módulo nativo zoneinfo 11:

Python  
import pytz  
from datetime import datetime  
import pandas as pd  
import MetaTrader5 as mt5

def obtener\_datos\_ohlcv(simbolo: str, timeframe: int, limite\_barras: int) \-\> pd.DataFrame:  
    if not mt5.initialize():  
        raise RuntimeError(f"Fallo de conexión: {mt5.last\_error()}")  
          
    \# Establecer huso horario UTC de forma explícita  
    zona\_utc \= pytz.timezone("Etc/UTC")  
    fecha\_referencia \= datetime.now(zona\_utc)  
      
    \# Obtener rates desde una fecha específica UTC  
    rates \= mt5.copy\_rates\_from(simbolo, timeframe, fecha\_referencia, limite\_barras)  
    mt5.shutdown()  
      
    if rates is None or len(rates) \== 0:  
        return pd.DataFrame()  
          
    \# Transformación del structured array de NumPy a un DataFrame de Pandas  
    df \= pd.DataFrame(rates)  
    df\['time'\] \= pd.to\_datetime(df\['time'\], unit='s', utc=True)  
    df.set\_index('time', inplace=True)  
    return df

## **3\. Información de mercado en tiempo real**

La monitorización del mercado requiere consultar la cotización activa, las propiedades estáticas del activo y las intenciones de liquidez del libro de órdenes (DOM).1

### **Consulta de propiedades del instrumento y cotización instantánea**

Antes de realizar consultas sobre un activo, este debe estar visible en el terminal de MetaTrader 5\.13 La función mt5.symbol\_select(symbol, True) añade explícitamente el instrumento a la ventana "MarketWatch" (Observación del Mercado), habilitando la sincronización de su flujo de precios.13

* **mt5.symbol\_info(symbol)**: Recupera las propiedades físicas y financieras del instrumento financiero en forma de una estructura nombrada (namedtuple).14 Esta información permite calcular el margen necesario, el valor del tick y el spread dinámico en tiempo real.14  
* **mt5.symbol\_info\_tick(symbol)**: Retorna un registro instantáneo con la cotización más reciente del mercado (Bid, Ask, Last, marcas de tiempo y volumen del tick) de forma directa y de bajo costo transaccional.13

### **Profundidad de mercado (Depth of Market / DOM / Level 2\)**

El Order Book de un activo representa la liquidez agregada del mercado de un broker a diferentes niveles de precios.15 El flujo de consultas para procesar esta matriz de datos se estructura en tres etapas 15:

1. **Suscripción (mt5.market\_book\_add(symbol))**: Indica al terminal que active la escucha de red para eventos de cambio en el DOM del activo.15  
2. **Extracción (mt5.market\_book\_get(symbol))**: Retorna una tupla de objetos de tipo BookInfo que representan los niveles de precios de compra (Bid) y venta (Ask) activos.15 Cada nivel incluye campos como type (tipo de orden del DOM mapeado a ENUM\_BOOK\_TYPE), price (precio del nivel) y volume o volume\_dbl (volumen acumulado en lotes).15  
3. **Liberación (mt5.market\_book\_release(symbol))**: Cancela la suscripción al libro del instrumento para optimizar el rendimiento de la red y el procesamiento del procesador en el terminal local.15

### **Fórmulas financieras clave expresadas en LaTeX**

La toma de decisiones en tiempo real se apoya en cálculos métricos sobre los datos recuperados:

* **Cálculo del Spread Nominal (![][image1])**:

![][image2]

* **Cálculo del Valor del Tick (![][image3])**:

![][image4]

| Función | Tipo de Retorno | Propósito y Usabilidad |
| :---- | :---- | :---- |
| symbol\_info(symbol) | namedtuple | Acceso a propiedades operativas del activo (apalancamiento, tick size, volumen mínimo de trading).14 |
| symbol\_info\_tick(symbol) | namedtuple | Consulta de la cotización rápida instantánea sin latencia de almacenamiento histórico.13 |
| market\_book\_get(symbol) | tuple de BookInfo | Extracción de los niveles de oferta y demanda del libro de órdenes (DOM Level 2).15 |

## **4\. Gestión de órdenes y posiciones**

La automatización de la operativa requiere la colocación de órdenes a mercado y pendientes, el control de límites de parada y el análisis histórico de la cuenta de trading.8

### **Estructura de la solicitud de negociación (MqlTradeRequest)**

Cualquier operación que altere el estado financiero de la cuenta se realiza transmitiendo un diccionario de Python estructurado de acuerdo con la definición de la clase nativa MqlTradeRequest de MQL5.17 La API procesa el diccionario y lo reenvía al servidor del broker mediante las funciones mt5.order\_check() o mt5.order\_send().17  
A continuación se detallan los parámetros de la estructura de solicitud de trading:

Python  
solicitud \= {  
    "action": int,          \# Tipo de operación de trading (TRADE\_REQUEST\_ACTIONS)  
    "magic": int,           \# Identificador único del bot de trading (Magic Number)  
    "order": int,           \# Ticket de la orden (para modificaciones de órdenes pendientes)  
    "symbol": str,          \# Símbolo del activo financiero  
    "volume": float,        \# Volumen solicitado en lotes  
    "price": float,         \# Precio de ejecución (requerido para órdenes limitadas)  
    "stoplimit": float,     \# Precio de la orden limit al dispararse un stop  
    "sl": float,            \# Nivel de precio del Stop Loss  
    "tp": float,            \# Nivel de precio del Take Profit  
    "deviation": int,       \# Desviación máxima del precio en puntos de cotización  
    "type": int,            \# Tipo de orden a colocar (ORDER\_TYPE)  
    "type\_filling": int,    \# Modo de llenado (ORDER\_TYPE\_FILLING)  
    "type\_time": int,       \# Tipo de expiración temporal de la orden  
    "expiration": int,      \# Fecha de expiración (para órdenes con tiempo específico)  
    "comment": str,         \# Comentario textual asociado a la transacción  
    "position": int,        \# Ticket de la posición (requerido para modificaciones/cierres)  
    "position\_by": int      \# Ticket de la posición opuesta (para cierres cruzados)  
}

### **Tipos de solicitudes de negociación (TRADE\_REQUEST\_ACTIONS)**

* mt5.TRADE\_ACTION\_DEAL: Coloca una orden para ejecución inmediata en el mercado (operaciones de compra o venta directa).19  
* mt5.TRADE\_ACTION\_PENDING: Registra una orden pendiente condicionada a un precio objetivo futuro (órdenes tipo Limit o Stop).19  
* mt5.TRADE\_ACTION\_SLTP: Modifica los parámetros de Stop Loss y Take Profit de una posición activa.19  
* mt5.TRADE\_ACTION\_MODIFY: Modifica los parámetros de precio, stops o expiración de una orden pendiente activa en el libro.19  
* mt5.TRADE\_ACTION\_REMOVE: Cancela y elimina una orden pendiente del mercado.19  
* mt5.TRADE\_ACTION\_CLOSE\_BY: Ejecuta un cierre neto compensado de dos posiciones abiertas de signo opuesto sobre el mismo símbolo (sistema de cobertura o Hedging).19

### **Políticas de llenado de órdenes (Filling Modes)**

Las políticas de llenado regulan el comportamiento del broker cuando la liquidez inmediata del libro no permite completar el volumen total solicitado en una transacción 19:

* **ORDER\_FILLING\_FOK (Fill or Kill)**: Exige la ejecución del volumen total solicitado.19 Si el volumen no puede ser cubierto en su totalidad por los precios del libro de órdenes, la solicitud es rechazada y cancelada por completo.19  
* **ORDER\_FILLING\_IOC (Immediate or Cancel)**: Permite una ejecución parcial de la orden.19 El broker ejecuta la máxima cantidad de volumen disponible en los niveles de precio actuales y cancela automáticamente el volumen remanente.19  
* **ORDER\_FILLING\_RETURN**: Utilizado habitualmente en mercados bursátiles centralizados. En caso de una ejecución parcial, el volumen remanente se mantiene en el mercado estructurado como una orden pendiente activa.19

### **Diferencias arquitectónicas entre órdenes, posiciones e historial de deals**

Para evitar errores de desarrollo comunes, es crucial diferenciar entre las tres estructuras que representan el estado de las transacciones en MetaTrader 5 22:

1. **Órdenes Activas (orders\_get)**: Representan solicitudes pendientes en el libro que aún no han sido ejecutadas ni rechazadas.25 No afectan el balance de la cuenta, sino que reservan margen potencial.  
2. **Posiciones Abiertas (positions\_get)**: Representan compromisos financieros de mercado activos y vigentes.26 En cuentas con modo "Netting", solo puede existir una posición agregada por símbolo, mientras que en cuentas tipo "Hedging" coexisten múltiples posiciones individuales independientes.26  
3. **Deals Históricos (history\_deals\_get)**: Un "Deal" representa el hecho físico e irreversible de la transacción ejecutada en el mercado.22 Las órdenes actúan como intenciones, mientras que los deals representan los eventos de ejecución real que modifican directamente el balance de la cuenta.22 Una sola orden de gran volumen puede generar múltiples deals históricos debido a llenados parciales.

### **Gestión de filtros avanzados de búsqueda (group)**

Las funciones de consulta del estado de la cuenta (positions\_get(), orders\_get(), history\_orders\_get(), history\_deals\_get()) implementan el parámetro group para filtrar de manera eficiente por conjuntos de símbolos utilizando comodines y reglas de exclusión 23:

Python  
\# Recupera únicamente posiciones de pares de divisas que contengan el Dólar (USD)  
posiciones\_usd \= mt5.positions\_get(group="\*USD\*")

\# Recupera todas las posiciones excluyendo las que pertenezcan al Euro (EUR)  
posiciones\_sin\_eur \= mt5.positions\_get(group="\*,\!\*EUR\*")

El filtrado con el parámetro group evalúa las condiciones de izquierda a derecha secuencialmente.23 Por ello, se deben declarar en primer lugar los comodines de inclusión (\*) y, posteriormente, las reglas de exclusión negadas (\!).23

### **Tabla de códigos de retorno del servidor transaccional del broker (retcode)**

La estructura devuelta tras un chequeo o envío de orden contiene el código numérico retcode, el cual describe de manera precisa el resultado de la solicitud en el servidor del broker 17:

| Código retcode | Constante MQL5 | Descripción y Diagnóstico Técnico |
| :---- | :---- | :---- |
| 10009 | TRADE\_RETCODE\_DONE | **Éxito absoluto.** La solicitud de trading ha sido procesada y ejecutada en su totalidad.27 |
| 10008 | TRADE\_RETCODE\_PLACED | La orden pendiente ha sido colocada correctamente en el libro de órdenes del broker.27 |
| 10019 | TRADE\_RETCODE\_NO\_MONEY | **Rechazo por falta de margen.** La cuenta no dispone de suficiente dinero libre para cubrir la garantía de la orden.27 |
| 10004 | TRADE\_RETCODE\_REQUOTE | El precio del mercado ha variado durante el tránsito de la red. Se requiere re-cotización.27 |
| 10013 | TRADE\_RETCODE\_INVALID | Parámetros de la estructura de la solicitud erróneos o inconsistentes.27 |
| 10015 | TRADE\_RETCODE\_INVALID\_PRICE | El precio especificado en la orden no se ajusta a los límites permitidos de cotización.27 |
| 10016 | TRADE\_RETCODE\_INVALID\_STOPS | Los niveles de SL o TP violan la distancia mínima del Stop Level permitida por el broker.27 |
| 10018 | TRADE\_RETCODE\_MARKET\_CLOSED | La sesión del mercado para el activo consultado se encuentra actualmente inactiva o cerrada.27 |
| 10036 | TRADE\_RETCODE\_POSITION\_CLOSED | Intento de modificación o cierre de una posición que ya ha sido liquidada en el servidor.27 |

## **5\. Limitaciones técnicas conocidas de la API oficial**

El desarrollo de plataformas complejas en Python requiere contemplar limitaciones de infraestructura que diferencian este paquete de la programación nativa en MQL5.1

### **Entornos UNIX y problemas de emulación en macOS y Linux**

La API oficial de MetaTrader 5 depende de llamadas nativas de Windows a través de Named Pipes, impidiendo su compilación directa o importación en sistemas basados en Linux o macOS.3 El uso de emuladores como Wine introduce dificultades en el establecimiento del canal IPC 28:

1. **Inestabilidad del canal IPC**: La traducción de las tuberías nombradas de Windows en sockets locales de Unix a través de Wine es propensa a fallas de sincronización, provocando excepciones frecuentes de tipo "IPC Timeout" bajo flujos de datos masivos.28  
2. **Apple Silicon (M-Series ARM)**: En computadoras con arquitectura ARM, la emulación requiere la combinación de capas de traducción x86 (QEMU/Colima) y Wine, lo que penaliza significativamente la latencia transaccional y puede causar corrupción de memoria o cierres inesperados en entornos de alta velocidad.28  
3. **Persistencia en entornos de producción**: Para sistemas en vivo, se recomienda ejecutar el terminal sobre una infraestructura física o un servidor privado virtual (VPS) con Windows Server de manera nativa.28

### **Brechas operativas frente a MQL5 nativo**

* **Falta de callbacks para eventos en tiempo real (Push)**: A diferencia de los EAs de MQL5, que reaccionan inmediatamente a eventos del servidor mediante funciones integradas como OnTick() u OnCalculate(), la API de Python opera exclusivamente bajo un modelo pull o de sondeo activo (polling).3 Esto obliga a los desarrolladores a programar bucles infinitos con temporizadores para monitorizar precios, incrementando la latencia del sistema y el uso de recursos de CPU en comparación con el código nativo.3  
* **Control nulo del Strategy Tester**: La API de Python no proporciona mecanismos para controlar, lanzar u optimizar pruebas de backtesting en el Strategy Tester de forma programática y nativa.7  
* **Ausencia de capacidades gráficas**: Python no dispone de acceso a las funciones nativas para dibujar objetos en los gráficos, colocar indicadores o estructurar interfaces gráficas de usuario integradas directamente en las ventanas del terminal de MetaTrader 5\.

## **6\. Patrones de uso avanzado**

Para desplegar un sistema de negociación algorítmica de nivel profesional, el desarrollador debe abstraer el comportamiento básico de la API utilizando patrones que garanticen la seguridad transaccional, la resiliencia ante pérdidas de conexión y el procesamiento concurrente de datos.31

### **Integración de Pandas para procesamiento analítico de datos**

La API oficial está diseñada para integrarse directamente con estructuras de análisis cuantitativo. Dado que los métodos de obtención de rates históricos devuelven arrays estructurados de NumPy, la inicialización de DataFrames de Pandas se realiza de manera eficiente 11:

Python  
import pandas as pd  
import MetaTrader5 as mt5

def extraer\_ohlcv\_formateado(simbolo: str, timeframe: int, total\_velas: int) \-\> pd.DataFrame:  
    datos\_crudos \= mt5.copy\_rates\_from\_pos(simbolo, timeframe, 0, total\_velas)  
    if datos\_crudos is None or len(datos\_crudos) \== 0:  
        return pd.DataFrame()  
          
    df \= pd.DataFrame(datos\_crudos)  
    \# Conversión del timestamp entero en un índice datetime de Pandas  
    df\['time'\] \= pd.to\_datetime(df\['time'\], unit='s', utc=True)  
    df.set\_index('time', inplace=True)  
    return df

### **Ejecución de llamadas bloqueantes en arquitecturas asíncronas con asyncio**

Puesto que las funciones transaccionales de la librería oficial (order\_send(), copy\_rates\_range(), etc.) son síncronas y bloquean el hilo de ejecución hasta que reciben respuesta, su uso en arquitecturas asíncronas basadas en el bucle de eventos (asyncio) puede degradar el rendimiento del sistema.31  
Para evitar congelar el bucle de eventos de asyncio, se deben delegar las llamadas bloqueantes de MT5 a un ejecutor en hilos de fondo mediante la función asyncio.to\_thread 31:

Python  
import asyncio  
import logging  
import MetaTrader5 as mt5

class EjecutorTradingAsincrono:  
    """Manejador concurrente para llamadas bloqueantes de MetaTrader 5 en asyncio."""  
      
    async def obtener\_rates\_asincronos(self, simbolo: str, timeframe: int, barras: int):  
        \# Desviar la ejecución síncrona a un hilo secundario del pool  
        rates \= await asyncio.to\_thread(mt5.copy\_rates\_from\_pos, simbolo, timeframe, 0, barras)  
        if rates is None:  
            err\_code \= await asyncio.to\_thread(mt5.last\_error)  
            logging.error(f"Fallo al recuperar rates para {simbolo}: {err\_code}")  
            return  
        return rates

    async def enviar\_orden\_asincrona(self, solicitud\_dict: dict):  
        \# Envío y pre-validación sin bloquear el bucle de eventos principal  
        chequeo \= await asyncio.to\_thread(mt5.order\_check, solicitud\_dict)  
        if chequeo.retcode\!= mt5.TRADE\_RETCODE\_DONE:  
            logging.warning(f"Validación de orden fallida: {chequeo.comment}")  
            return None  
              
        resultado \= await asyncio.to\_thread(mt5.order\_send, solicitud\_dict)  
        return resultado

### **Clase contenedora (Wrapper) con auto-reconexión automática**

El siguiente código implementa un wrapper robusto bajo el paradigma de programación orientada a objetos, aislando el comportamiento de la API oficial tras una capa defensiva de reconexión automática y verificación de consistencia:

Python  
import time  
import logging  
import MetaTrader5 as mt5  
from typing import Optional, Dict, Any

class TerminalMT5Manager:  
    """Wrapper robusto de control y ejecución transaccional para MetaTrader 5."""  
      
    def \_\_init\_\_(self, login: int, password: str, server: str, path\_exe: str):  
        self.login \= login  
        self.password \= password  
        self.server \= server  
        self.path\_exe \= path\_exe  
        self.conectado \= False  
          
    def conectar(self) \-\> bool:  
        """Inicializa el terminal y autentica la cuenta de trading de manera segura."""  
        logging.info("Intentando establecer conexión con el terminal MT5...")  
          
        \# Intentar inicializar el terminal apuntando a su ruta ejecutable  
        if not mt5.initialize(path=self.path\_exe, timeout=15000):  
            logging.error(f"Error crítico en initialize(). Código de error: {mt5.last\_error()}")  
            return False  
              
        \# Autenticación explícita contra el servidor del broker  
        autorizado \= mt5.login(login=self.login, password=self.password, server=self.server)  
        if not autorizado:  
            logging.error(f"Fallo de login para la cuenta {self.login}. Código de error: {mt5.last\_error()}")  
            mt5.shutdown()  
            return False  
              
        self.conectado \= True  
        logging.info(f"Conexión exitosa. Cuenta: {self.login} | Servidor: {self.server}")  
        return True  
          
    def asegurar\_conexion(self) \-\> bool:  
        """Valida que el canal de comunicaciones con el terminal y el broker siga activo."""  
        if self.conectado:  
            info\_terminal \= mt5.terminal\_info()  
            if info\_terminal is not None and info\_terminal.connected:  
                return True  
            logging.warning("Pérdida de conectividad detectada. Iniciando reconexión en caliente...")  
              
        \# Algoritmo de reintentos con backoff exponencial básico  
        for intento in range(1, 4):  
            logging.info(f"Intento de restauración de conexión {intento}/3...")  
            if self.conectar():  
                return True  
            time.sleep(intento \* 2)  
              
        self.conectado \= False  
        return False  
          
    def colocar\_orden\_mercado(self, simbolo: str, tipo\_orden: int, lotes: float,   
                               puntos\_sl: int \= 0, puntos\_tp: int \= 0) \-\> Optional\]:  
        """Envía una orden a mercado tras asegurar la conexión y pre-validar los parámetros."""  
        if not self.asegurar\_conexion():  
            logging.error("Llamada transaccional abortada: Conexión inactiva.")  
            return None  
              
        \# Añadir símbolo a MarketWatch si no está activo  
        if not mt5.symbol\_select(simbolo, True):  
            logging.error(f"El símbolo {simbolo} no se puede seleccionar.")  
            return None  
              
        info\_simbolo \= mt5.symbol\_info(simbolo)  
        tick \= mt5.symbol\_info\_tick(simbolo)  
        if info\_simbolo is None or tick is None:  
            logging.error(f"Propiedades o tick actual de {simbolo} no disponibles.")  
            return None  
              
        point \= info\_simbolo.point  
        precio \= tick.ask if tipo\_orden \== mt5.ORDER\_TYPE\_BUY else tick.bid  
          
        \# Cálculo estricto de los niveles de salida de protección  
        sl \= precio \- (puntos\_sl \* point) if tipo\_orden \== mt5.ORDER\_TYPE\_BUY else precio \+ (puntos\_sl \* point)  
        tp \= precio \+ (puntos\_tp \* point) if tipo\_orden \== mt5.ORDER\_TYPE\_BUY else precio \- (puntos\_tp \* point)  
          
        sl \= sl if puntos\_sl \> 0 else 0.0  
        tp \= tp if puntos\_tp \> 0 else 0.0  
          
        \# Selección automática del filling mode soportado por el broker  
        if info\_simbolo.filling\_mode & mt5.SYMBOL\_FILLING\_FOK:  
            modo\_llenado \= mt5.ORDER\_FILLING\_FOK  
        elif info\_simbolo.filling\_mode & mt5.SYMBOL\_FILLING\_IOC:  
            modo\_llenado \= mt5.ORDER\_FILLING\_IOC  
        else:  
            modo\_llenado \= mt5.ORDER\_FILLING\_RETURN  
              
        solicitud \= {  
            "action": mt5.TRADE\_ACTION\_DEAL,  
            "symbol": simbolo,  
            "volume": lotes,  
            "type": tipo\_orden,  
            "price": precio,  
            "sl": sl,  
            "tp": tp,  
            "deviation": 10,  
            "magic": 123456,  
            "comment": "Orden automatizada Python Wrapper",  
            "type\_filling": modo\_llenado,  
            "type\_time": mt5.ORDER\_TIME\_GTC  
        }  
          
        \# Pre-chequeo defensivo  
        verificacion \= mt5.order\_check(solicitud)  
        if verificacion.retcode\!= mt5.TRADE\_RETCODE\_DONE:  
            logging.error(f"Orden inválida en pre-chequeo: {verificacion.comment} (Código: {verificacion.retcode})")  
            return None  
              
        \# Envío formal de la transacción al mercado  
        resultado \= mt5.order\_send(solicitud)  
        if resultado is None:  
            logging.critical("Error fatal: El terminal devolvió un objeto vacío tras order\_send().")  
            return None  
              
        if resultado.retcode\!= mt5.TRADE\_RETCODE\_DONE:  
            logging.error(f"Rechazo del servidor. Código: {resultado.retcode} | Motivo: {resultado.comment}")  
            return resultado.\_asdict()  
              
        logging.info(f"Transacción confirmada. Ticket: {resultado.order} | Precio Ejecución: {resultado.price}")  
        return resultado.\_asdict()  
          
    def liberar(self):  
        if self.conectado:  
            mt5.shutdown()  
            self.conectado \= False  
            logging.info("Recursos de MetaTrader 5 liberados.")

## **7\. Ecosistema de terceros y puentes de comunicación alternativos**

Cuando las limitaciones de la API oficial (como la falta de un entorno nativo asíncrono o la incompatibilidad multiplataforma de las Named Pipes de Windows) entran en conflicto con la arquitectura del sistema, se debe evaluar el uso de componentes de red alternativos desarrollados por la comunidad o proveedores de servicios especializados.3

### **Comparativa técnica detallada de alternativas de integración**

| Criterio | API Oficial MetaTrader5 | Conector DWX-ZeroMQ | Gateway Socket pymt5 | HTTP API Remota (mt5-httpapi) |
| :---- | :---- | :---- | :---- | :---- |
| **Protocolo de red** | Named Pipes nativas de Windows.3 | Sockets TCP ligeros con ZeroMQ.33 | Conexión por socket TCP directo en crudo.35 | Protocolo REST HTTP e interfaz Nginx.7 |
| **Compatibilidad Python** | Solo en sistemas Windows.3 | Multiplataforma (Linux, macOS, Windows).6 | Multiplataforma (Linux, macOS, Windows).35 | Multiplataforma y soporte de cliente HTTP.7 |
| **Modelo de Market Data** | Polling activo bajo demanda de datos.3 | Streaming push asíncrono nativo (PUB/SUB).33 | Streaming push asíncrono nativo sobre eventos.35 | Consulta asíncrona sobre HTTP.7 |
| **Complejidad operativa** | Baja. Integración instantánea por pip install.8 | Alta. Requiere inyectar librerías de enlace (.dll) y EAs en el terminal.36 | Media. Exige configurar un servicio o script receptor en el terminal.35 | Alta. Requiere dockerizar instancias de MT5 e integrar un servidor de Nginx.7 |
| **Latencia estimada** | Extremadamente baja (sub-milisegundo en local).1 | Baja (milisegundos sobre transporte de red local o remota).33 | Baja (latencia sobre red local o remota).35 | Media-Alta (debido al procesamiento y deserialización JSON HTTP).7 |

### **Conector DWX-ZeroMQ**

La arquitectura del conector DWX-ZeroMQ implementa una biblioteca de enlace de bajo nivel (libsodium.dll y libzmq.dll) instalada en el directorio de librerías de MetaTrader junto con un EA receptor en MQL.36 Esto convierte al terminal de MetaTrader en un servidor ZeroMQ de alto rendimiento que expone puertos TCP para la adquisición de datos de mercado y el envío de órdenes 33:

* **Idoneidad**: Es la alternativa preferida para separar la lógica analítica de la ejecución física.6 Permite ejecutar el algoritmo complejo en servidores dedicados de alto rendimiento en Linux (utilizando Tensorflow o PyTorch) mientras se envían las órdenes a través de una red local o remota hacia terminales MT5 remotos en Windows.6

### **Conector PyMT5**

pymt5 opera mediante un servidor de sockets que corre en un hilo de fondo del terminal de MetaTrader.35 Al invocar métodos de trading o suscripciones desde el script de Python, los datos se transmiten serializados directamente por red.35 Es una opción ágil y ligera para habilitar un flujo transaccional y de cotización en tiempo real sin requerir la inyección de librerías dinámicas (.dll) complejas de terceros en el terminal de corretaje.35

### **HTTP API Remota (mt5-httpapi)**

Diseñada para despliegues complejos a nivel de infraestructura corporativa, esta aproximación aloja los terminales físicos de MetaTrader 5 dentro de contenedores de Docker (ejecutados bajo Wine en máquinas virtuales Windows o Linux).7 Un servidor intermedio expone una API REST protegida por un proxy inverso de Nginx, permitiendo el control transaccional de múltiples cuentas de brokers independientes a través de simples llamadas HTTP de tipo POST y GET con payloads JSON.7

#### **Fuentes citadas**

1. MetaTrader 5 Python Integration \- Grokipedia, acceso: junio 28, 2026, [https://grokipedia.com/page/MetaTrader\_5\_Python\_Integration](https://grokipedia.com/page/MetaTrader_5_Python_Integration)  
2. metatrader5 \- PyPI, acceso: junio 28, 2026, [https://pypi.org/project/metatrader5/](https://pypi.org/project/metatrader5/)  
3. github.com/mukbeast4/go-mt5 v0.1.10 on Go \- Libraries.io \- security & maintenance data for open source software, acceso: junio 28, 2026, [https://libraries.io/go/github.com%2Fmukbeast4%2Fgo-mt5](https://libraries.io/go/github.com%2Fmukbeast4%2Fgo-mt5)  
4. initialize \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5initialize\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5initialize_py)  
5. Connecting a Python script to the terminal and account \- Advanced language tools \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/python/python\_init](https://www.mql5.com/en/book/advanced/python/python_init)  
6. BigMitchGit/mt5\_remote: MetaTrader5 with remote access using a client/server architecture, acceso: junio 28, 2026, [https://github.com/BigMitchGit/mt5\_remote](https://github.com/BigMitchGit/mt5_remote)  
7. GitHub \- psyb0t/mt5-httpapi: MetaTrader 5 in a real Windows VM (Docker \+ QEMU/KVM) with a REST API for programmatic trading AND server-side technical analysis. One POST \= OHLC bars enriched with RSI/MACD/Bollinger/ADX/VWAP/Ichimoku/Order Blocks/FVGs/divergences. Multi-broker, multi-account. No Wine bullshit, no janky workarounds., acceso: junio 28, 2026, [https://github.com/psyb0t/mt5-httpapi](https://github.com/psyb0t/mt5-httpapi)  
8. Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5](https://www.mql5.com/en/docs/python_metatrader5)  
9. copy\_rates\_from \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5copyratesfrom\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesfrom_py)  
10. copy\_rates\_from\_pos \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5copyratesfrompos\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesfrompos_py)  
11. copy\_rates\_range \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5copyratesrange\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesrange_py)  
12. copy\_ticks\_from \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5copyticksfrom\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5copyticksfrom_py)  
13. symbol\_info\_tick \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5symbolinfotick\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5symbolinfotick_py)  
14. symbol\_info \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5symbolinfo\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5symbolinfo_py)  
15. market\_book\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5marketbookget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5marketbookget_py)  
16. symbol\_select \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5symbolselect\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5symbolselect_py)  
17. order\_send \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5ordersend\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5ordersend_py)  
18. Checking and sending a trade order \- Advanced language tools \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/python/python\_ordercheck\_ordersend](https://www.mql5.com/en/book/advanced/python/python_ordercheck_ordersend)  
19. order\_check \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5ordercheck\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5ordercheck_py)  
20. Modify position from MetaTrader 5 Python Trading Bot \- Gist \- GitHub, acceso: junio 28, 2026, [https://gist.github.com/jimtin/f1653cd79275f8339939d874419da54e](https://gist.github.com/jimtin/f1653cd79275f8339939d874419da54e)  
21. Automated Trading with MetaTrader5: Order Management and Market Data Collection, acceso: junio 28, 2026, [https://dev.to/vital7777/automated-trading-with-metatrader5-order-management-and-market-data-collection-4pb8](https://dev.to/vital7777/automated-trading-with-metatrader5-order-management-and-market-data-collection-4pb8)  
22. history\_deals\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5historydealsget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5historydealsget_py)  
23. history\_orders\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5historyordersget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5historyordersget_py)  
24. Integrating MetaTrader 5 API in Python : A Practical Example | by Ullasraj \- Medium, acceso: junio 28, 2026, [https://medium.com/@ullasraj1998/integrating-metatrader-5-api-in-python-a-practical-example-3996524f1ea0](https://medium.com/@ullasraj1998/integrating-metatrader-5-api-in-python-a-practical-example-3996524f1ea0)  
25. orders\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5ordersget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5ordersget_py)  
26. positions\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5positionsget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5positionsget_py)  
27. Trade Server Return Codes \- Codes of Errors and Warnings \- Constants, Enumerations and Structures \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/errorswarnings/enum\_trade\_return\_codes](https://www.mql5.com/en/docs/constants/errorswarnings/enum_trade_return_codes)  
28. bahadirumutiscimen/silicon-metatrader5: MetaTrader 5 Solution for macOS Silicon M Series. Run MT5 seamlessly via Docker and perform algorithmic trading with Python. \- GitHub, acceso: junio 28, 2026, [https://github.com/bahadirumutiscimen/silicon-metatrader5](https://github.com/bahadirumutiscimen/silicon-metatrader5)  
29. MetaTrader 5 \+ Python on Apple Silicon Macs M\* Series | by bahadirumutiscimen \- Medium, acceso: junio 28, 2026, [https://medium.com/@bahadirumutiscimen/metatrader-5-python-on-apple-silicon-macs-m1-m2-m3-64d6fa2f7a49](https://medium.com/@bahadirumutiscimen/metatrader-5-python-on-apple-silicon-macs-m1-m2-m3-64d6fa2f7a49)  
30. Meta-Trader-MCP by shubhvisputek | Glama, acceso: junio 28, 2026, [https://glama.ai/mcp/servers/shubhvisputek/meta-trader-mcp](https://glama.ai/mcp/servers/shubhvisputek/meta-trader-mcp)  
31. AIOMQL-The Complete Guide to Building Algorithmic Trading Bots with Python & MetaTrader 5 \- DEV Community, acceso: junio 28, 2026, [https://dev.to/akaichinga/aiomql-the-complete-guide-to-building-algorithmic-trading-bots-with-python-metatrader-5-3bgh](https://dev.to/akaichinga/aiomql-the-complete-guide-to-building-algorithmic-trading-bots-with-python-metatrader-5-3bgh)  
32. How to pull data from MetaTrader 5 with Python | by Eduardo Bogosian | Medium, acceso: junio 28, 2026, [https://medium.com/@eduardo-bogosian/how-to-pull-data-from-metatrader-5-with-python-4889bd92f62d](https://medium.com/@eduardo-bogosian/how-to-pull-data-from-metatrader-5-with-python-4889bd92f62d)  
33. ZeroMQ to MetaTrader Connectivity \- Darwinex, acceso: junio 28, 2026, [https://www.darwinex.com/algorithmic-trading/zeromq-metatrader](https://www.darwinex.com/algorithmic-trading/zeromq-metatrader)  
34. DarwinexLabs/tools/dwx\_zeromq\_connector/v2.0.1/README.md at master · darwinex ... \- GitHub, acceso: junio 28, 2026, [https://github.com/darwinex/DarwinexLabs/blob/master/tools/dwx\_zeromq\_connector/v2.0.1/README.md](https://github.com/darwinex/DarwinexLabs/blob/master/tools/dwx_zeromq_connector/v2.0.1/README.md)  
35. devcartel/pymt5: Python API for interacting with DevCartel MetaTrader 5 gateway \- GitHub, acceso: junio 28, 2026, [https://github.com/devcartel/pymt5](https://github.com/devcartel/pymt5)  
36. GitHub \- darwinex/dwx-zeromq-connector: Wrapper library for algorithmic trading in Python 3, providing DMA/STP access to Darwinex liquidity via a ZeroMQ-enabled MetaTrader Bridge EA., acceso: junio 28, 2026, [https://github.com/darwinex/dwx-zeromq-connector](https://github.com/darwinex/dwx-zeromq-connector)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAaCAYAAACHD21cAAAArElEQVR4XmNgGBZADYhnArEvklgJEhsDsALxPyCeDcR8QGwHxP+BuAaIPyOpwwAgRTboggwQ8Sp0QRhYwABRgA2AxEGuwQpAkvg04gQwjb3oEoRANwNCMwzPQFGBB+QxYGq+haKCCODCgN/fYBCMLgAFixnwaPQD4gJ0QSgoZcCj8SwQr0MXhIK/DHgCCOYPHjTxtQwEktkTIGYC4g8MEAPeQ+kFSGpGwShAAACCHi2hbGnWVgAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAxCAYAAABnGvUlAAACTklEQVR4Xu3cS6hNYRQH8C+v5BFKSsrQwMRExJQYURIpUyVTUwYGjGVoYGhkZqaMyUgZmd0BeZREkbziW529u99Zzr1uzu7cq36/+re/tb7d3vvMVudVCgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8D/ZU3M1Nwe0puZAbi5gS24ssw01W3MTAGCWfjXrC6keyoey9OvGeTHgDa29//pUh1z3on8sNwEAZmVTzbrUe5DqIdwoCw9E2SwGtt6kXvakGNgAgGV0sCxtaJnGqe4Y97nTblSrap7VXG96cd7amqM1+2oON3vTyK/zUc2Rbn2u5lazF87XXCkGNgBgBYhBpk98l22Sub9kMf2gdLFZ936kOsQ58ZHl3pqHaW8a7euMnBnfHnu2vDawAQArwovy50A1hGvNOl8/6qc1u1NvY83JppftXyQLyffeXPOmqfv9E806vCoGNgBgmUz65WMeaoaws0lc/+74drnX9bd1dawfd8chTbpefict3K/52fRjYDve1AAAMxNDya6mjiFp6L/UyD9g2F7Gh6Tnzfpmd+z34/ttk4asf5Wvdbbmc1NPGt7C9zJ61w0AYOZe1lwqo+EksmN8e2rvy+hj1i9N723Xe9fVp8v8/UOcG/vxrtblMnrG193eNPp7RL7VfKy53ex/KqN7fe3q1WX+/HiWOB7q9gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAmLHfEpZ3JiWsozwAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAaCAYAAAAwspV7AAABh0lEQVR4Xu2Vuy9FQRDGhxCJQihURIhWp5QIHYWOiE5y/wE9iUehl0gUivs3aGgUChohKqIVj4hEPApE4vFNZjZ3TPa4cs+11fklX87sN2d35+zuOYeooKD+NECP0JfR/Y87hA+q5DlOQplkwhHnWziflFmSSeedH9iCBr353/STFLXtE6AVuvFmKrioJ2+Cd2+kJBxkSwlacF5SYkX5dnJ8UWdQp2kHWrwBLrwRYY1qeMhXqnTig79vcpbYwMveyCDW91d2STr16DVGB/TpzT8yBZ17sxqLJMVcQuMux4Tttds8Bh2QfOcs/F3bga6MdwrNaHwCPZtcJqMkkz34hIF/MbxagTI0QTJJ4AXq1pjHazNxI8kHekjbVWkiuZH/h1nEBnqDujTmlYjdw7B/CDX7RB7aKX6ebBE86bppByZJ3mZ+4Kyia2IF2tCYzwuzBG1Cw6a9qjEzAPWSbO+0eqGoW73mgreXD+ee8Xj1rqE54x2THPQ7qE89uzr8cEdU520sKCjIyzd62lw2Dt631QAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,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>