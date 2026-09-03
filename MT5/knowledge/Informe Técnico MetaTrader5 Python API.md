# **Arquitectura de Integración y Especificación Técnica Exhaustiva de la API MetaTrader 5 para Python**

El diseño de sistemas de trading algorítmico de nivel institucional exige una infraestructura de baja latencia, alta concurrencia y un control de riesgos robusto.1 Para los desarrolladores que operan bajo entornos macOS, el despliegue del paquete oficial de Python MetaTrader5 (distribuido a través de PyPI) plantea un desafío de compatibilidad estructural, dado que esta biblioteca está compilada exclusivamente como una biblioteca de enlace dinámico (DLL) para arquitecturas de 64 bits de Windows.3 La solución de ingeniería estándar consiste en desacoplar la ejecución en una arquitectura puente: un cliente ligero en macOS que se comunica por red (mediante protocolos gRPC, REST o WebSockets) con un servidor de pasarela (Gateway) en un Servidor Virtual Privado (VPS) con Windows, el cual aloja la terminal de MetaTrader 5 y un servicio Python para interactuar de forma local por medio de canales de comunicación interproceso (IPC).1 El presente informe detalla exhaustivamente el funcionamiento de la API, sus limitaciones físicas y los patrones de integración avanzados necesarios para construir un sistema de producción robusto.5

## **1\. Inicialización, Conexión y Gestión de Sesión**

La conectividad entre el intérprete de Python y la terminal de MetaTrader 5 se gestiona mediante un canal IPC sincrónico mapeado en memoria.4 El ciclo de vida de esta sesión se gobierna a través de funciones críticas que administran el arranque, la autenticación y la monitorización de la terminal.8

### **Parámetros de la Función mt5.initialize()**

La función mt5.initialize() es el único punto de entrada para iniciar la comunicación IPC.2 Su comportamiento varía drásticamente según los argumentos proporcionados:

| Parámetro | Tipo | Requerido | Descripción Técnica y Comportamiento por Defecto |
| :---- | :---- | :---- | :---- |
| path | str | No | Ruta absoluta al ejecutable metatrader.exe o metatrader64.exe.8 Si se omite, la API busca en el registro de Windows la última instalación activa de la terminal.8 |
| login | int | No | Número identificador de la cuenta de trading.4 Si se omite, la terminal se conecta por defecto a la última cuenta guardada localmente.8 |
| password | str | No | Contraseña de la cuenta de trading.4 Si se omite, se aplica la contraseña almacenada en la base de datos local de la terminal.8 |
| server | str | No | Nombre del servidor de trading asignado por el bróker.4 Si no se especifica, se utiliza el servidor asociado a la última cuenta activa.8 |
| timeout | int | No | Tiempo máximo de espera en milisegundos para establecer el canal IPC con la terminal.8 Por defecto es 60000 (60 segundos).8 |
| portable | bool | No | Flag para forzar el lanzamiento de la terminal en modo portable.8 Si es True, la terminal almacena sus datos en su propia carpeta de instalación y no en el directorio AppData de Windows.8 |

### **Comportamiento del Sistema ante Fallos y Secuencias de Recuperación**

El proceso de inicialización no lanza excepciones nativas de Python ante fallos de conexión o autenticación.6 En su lugar, devuelve un valor booleano False y almacena el código del fallo internamente, el cual debe ser consultado mediante mt5.last\_error().7

* **Terminal no iniciada**: Si el proceso de la terminal no está en ejecución y no se especifica una ruta válida en path, mt5.initialize() devuelve False.8 El código de error devuelto es \-10003 (RES\_E\_INTERNAL\_FAIL\_CONNECT / RES\_E\_INTERNAL\_FAIL\_INIT), indicando que la capa de transporte IPC no detectó un canal activo.7  
* **Credenciales incorrectas**: Si la terminal arranca pero los parámetros de autenticación son rechazados por el servidor de trading del bróker, mt5.login() o la inicialización con credenciales devuelven False.9 El código de error es \-6 (RES\_E\_AUTH\_FAILED), impidiendo recibir cotizaciones reales o enviar órdenes de trading.7  
* **Manejo de reconexiones**: La pérdida de conexión física a internet o la desconexión del servidor del bróker se detecta evaluando periódicamente el campo connected de mt5.terminal\_info().11 Si este valor es False, se debe ejecutar un desmontaje limpio mediante mt5.shutdown(), aplicar una espera exponencial (*exponential backoff*) e intentar nuevamente la secuencia de inicialización.8

### **Métodos de Inspección de Sesión y Cuenta**

La API ofrece funciones complementarias para auditar el estado del software y las variables financieras de la cuenta 2:

* **mt5.shutdown()**: Finaliza la conexión IPC con la terminal, cierra los sockets internos de transporte y libera los recursos de memoria mapeada en el VPS.8  
* **mt5.login(login, password, server, timeout)**: Permite alternar de forma dinámica entre cuentas de trading dentro de una misma sesión activa sin necesidad de reiniciar la terminal física ni reinstanciar la conexión IPC.9  
* **mt5.version()**: Retorna una tupla con el formato (build\_number, compilation\_date) (por ejemplo, (500, 3003, '22 Jul 2021')) que representa la versión de compilación de la terminal de MT5 conectada.11  
* **mt5.terminal\_info()**: Retorna una estructura namedtuple que contiene los parámetros de configuración y estado del software, incluyendo propiedades críticas como trade\_allowed (si la terminal admite trading automático) o tradeapi\_disabled (si el bróker o el terminal ha bloqueado las transacciones vía Python).11  
* **mt5.account\_info()**: Devuelve la estructura financiera de la cuenta de trading en un objeto namedtuple.14

Para facilitar la monitorización de la cuenta, las propiedades del objeto retornado por mt5.account\_info() se detallan en la siguiente tabla de variables financieras 14:

| Propiedad | Tipo | Descripción y Relevancia en Control de Riesgos |
| :---- | :---- | :---- |
| login | int | Número identificador único de la cuenta de trading.14 |
| trade\_mode | int | Modo de trading: 0 para Demo, 1 para Real, 2 para Competición.13 |
| leverage | int | Apalancamiento máximo configurado en la cuenta (e.g., 100 para 1:100).1 |
| limit\_orders | int | Número máximo de órdenes pendientes activas permitidas simultáneamente.14 |
| margin\_so\_mode | int | Modo de Stop Out: 0 basado en porcentaje de margen, 1 basado en valor monetario bruto.14 |
| trade\_allowed | bool | Indica si la cuenta de trading tiene permisos de ejecución aprobados en el servidor.14 |
| trade\_expert | bool | Indica si el servidor permite la ejecución comercial mediante asesores expertos o API.14 |
| margin\_mode | int | Modo de margen: 0 para cobertura (hedging), 1 para compensación (netting), 2 para retail hedging.13 |
| currency\_digits | int | Número de decimales para mostrar el balance y patrimonio de la cuenta.14 |
| fifo\_close | bool | Flag que determina si la cuenta exige la regla FIFO (First-In, First-Out) para cerrar posiciones.14 |
| balance | float | Saldo neto de la cuenta antes de considerar las pérdidas y ganancias flotantes.1 |
| credit | float | Crédito comercial provisto por el bróker (fondos de bonificación).14 |
| profit | float | Beneficio o pérdida flotante acumulado por la totalidad de las posiciones abiertas.14 |
| equity | float | Patrimonio neto en tiempo real de la cuenta (![][image1]).1 |
| margin | float | Margen retenido por el bróker como garantía para mantener las posiciones abiertas.1 El margen libre se calcula mediante la fórmula: ![][image2], donde ![][image3] es el margen libre, ![][image4] es el patrimonio (equity), y ![][image5] es el margen retenido.14 |
| margin\_free | float | Fondos disponibles en la cuenta para abrir nuevas posiciones o realizar retiros.14 |
| margin\_level | float | Nivel de margen porcentual (![][image6]).14 |
| margin\_so\_call | float | Umbral de llamada de margen (*Margin Call*) en el cual el bróker advierte insuficiencia de fondos.14 |
| margin\_so\_so | float | Umbral de Stop Out en el cual el bróker liquida posiciones de forma automática.14 |
| currency | str | Divisa base de la cuenta de trading (e.g., "USD", "EUR").14 |

## **2\. Información de Símbolos e Instrumentos**

El control preciso de los activos y la recopilación de sus especificaciones técnicas de mercado es vital para evitar errores de redondear de forma inválida los precios o volúmenes enviados al servidor.17

### **Métodos de Consulta y Filtrado Avanzado**

* **mt5.symbols\_total()**: Retorna un valor entero que representa el total de símbolos disponibles en la terminal, incluyendo activos ocultos y símbolos personalizados creados por el usuario.19  
* **mt5.symbols\_get(group)**: Obtiene una tupla que contiene objetos SymbolInfo.18 Acepta el parámetro opcional group para realizar filtrado de cadenas complejo.18 Se pueden separar múltiples patrones por coma, usar asteriscos (\*) como comodines de coincidencia y signos de exclamación (\!) para exclusión secuencial.18 Por ejemplo, un filtro definido como group="\*,\!\*USD\*,\!\*EUR\*" selecciona inicialmente todos los símbolos de la terminal, excluye a continuación todos los que contienen la subcadena "USD" y finalmente excluye aquellos que contienen "EUR".18  
* **mt5.symbol\_select(symbol, enable)**: Añade (enable=True) o remueve (enable=False) un símbolo de la ventana "MarketWatch" del terminal.20 Esto es un requisito obligatorio, ya que si un símbolo no está seleccionado de forma activa en el MarketWatch, las cotizaciones en tiempo real no se actualizarán en la caché de la terminal local y las llamadas a la API de ticks devolverán valores nulos o desactualizados.17  
* **mt5.symbol\_info\_tick(symbol)**: Retorna un objeto Tick con la última cotización instantánea almacenada en la terminal local.20 Proporciona acceso rápido a los campos time (segundos), time\_msc (milisegundos), bid, ask, last, volume y volume\_real sin necesidad de realizar solicitudes de red directas al servidor.17  
* **mt5.symbol\_info(symbol)**: Devuelve las especificaciones del contrato de un activo en un objeto namedtuple.18

A continuación se presenta un mapeo exhaustivo de las propiedades de la estructura SymbolInfo devuelta por la API 18:

| Propiedad | Tipo | Clasificación | Descripción Técnica e Importancia Operativa |
| :---- | :---- | :---- | :---- |
| name | str | String | Nombre técnico del instrumento financiero (e.g., "EURUSD").18 |
| currency\_base | str | String | Divisa base del activo (e.g., "EUR" en EURUSD).18 |
| currency\_profit | str | String | Divisa en la que se liquidan los beneficios o pérdidas (e.g., "USD").18 |
| currency\_margin | str | String | Divisa utilizada para calcular el margen requerido (e.g., "EUR").18 |
| description | str | String | Nombre descriptivo oficial del instrumento.18 |
| custom | bool | Booleano | Flag que indica si es un símbolo personalizado configurado por el usuario.18 |
| select | bool | Booleano | Indica si el activo está seleccionado actualmente en el MarketWatch.18 |
| visible | bool | Booleano | Determina si el símbolo es visible en la interfaz del terminal.18 |
| digits | int | Entero | Número de posiciones decimales permitidas para cotizar el precio.18 |
| spread | int | Entero | Spread instantáneo medido en puntos.18 |
| spread\_float | bool | Booleano | Indica si el diferencial de spread es variable (flotante) o fijo.18 |
| point | float | Float | Tamaño mínimo del punto de variación de precio (![][image7]).16 |
| trade\_mode | int | Entero | Modo operativo del mercado: 0 desactivado, 1 solo posiciones cortas, 2 solo posiciones largas, 3 solo cierre de posiciones, 4 trading totalmente habilitado.18 |
| trade\_calc\_mode | int | Entero | Modelo de cálculo de margen y rentabilidad (e.g., Forex, Futuros, CFDs, Acciones).18 |
| trade\_exemode | int | Entero | Modo de ejecución de órdenes: 0 instantánea, 1 por petición, 2 por mercado, 3 de bolsa.18 |
| trade\_stops\_level | int | Entero | Distancia mínima admisible en puntos desde el precio actual para colocar SL o TP.18 Si se colocan a menor distancia, el servidor rechaza la orden.18 |
| trade\_freeze\_level | int | Entero | Rango de precios en puntos donde no se permite modificar órdenes pendientes cercanas al precio spot.18 |
| volume\_min | float | Float | Tamaño mínimo permitido de lote para abrir una transacción (e.g., 0.01 lotes).18 |
| volume\_max | float | Float | Tamaño máximo de lote permitido para una única transacción comercial.18 |
| volume\_step | float | Float | Incremento mínimo aplicable para modificar el tamaño del lote de una orden.18 |
| trade\_contract\_size | float | Float | Tamaño nominal de un lote estándar (e.g., 100000.0 unidades para divisas).18 |
| trade\_tick\_size | float | Float | Variación mínima admisible en la cotización del precio (paso mínimo del tick).18 |
| trade\_tick\_value | float | Float | Valor monetario del paso mínimo del tick en la divisa de la cuenta.18 |
| swap\_mode | int | Entero | Método utilizado para calcular el cobro de swap por mantener la posición nocturna.18 |
| swap\_long | float | Float | Tasa de swap aplicable a posiciones largas (compras) mantenidas durante el rollover.18 |
| swap\_short | float | Float | Tasa de swap aplicable a posiciones cortas (ventas) mantenidas durante el rollover.18 |
| swap\_rollover3days | int | Entero | Día de la semana en el cual se liquida el swap triple (normalmente el miércoles).18 |

## **3\. Datos Históricos OHLCV (Series Temporales)**

La API proporciona tres funciones optimizadas para la extracción masiva de series temporales, las cuales retornan arrays estructurados de NumPy que representan las barras históricas del gráfico.23

### **Comparativa Funcional de los Métodos de Extracción**

* **mt5.copy\_rates\_from(symbol, timeframe, date\_from, count)**: Extrae exactamente la cantidad de barras indicada por count a partir de una fecha de inicio determinada por date\_from (tipo datetime o timestamp entero), moviéndose cronológicamente hacia atrás en el pasado.24 Solo devuelve barras con tiempo de apertura menor o igual a la fecha especificada.24  
* **mt5.copy\_rates\_from\_pos(symbol, timeframe, start\_pos, count)**: Recupera count barras utilizando una indexación ordinal basada en la distancia con el momento actual.25 El índice 0 representa la barra que se está formando en tiempo real, el índice 1 representa la última vela finalizada y el conteo avanza consecutivamente hacia el pasado.25 Es ideal para procesos cíclicos de análisis técnico continuo en tiempo real.26  
* **mt5.copy\_rates\_range(symbol, timeframe, date\_from, date\_to)**: Obtiene la totalidad de las barras completadas cuyo tiempo de apertura se sitúe estrictamente dentro del intervalo temporal cerrado ![][image8].23

### **Constantes de Temporalidad (Timeframes)**

La resolución temporal requerida para las barras se especifica utilizando las siguientes constantes del módulo 24:

| Constante API | Valor Entero | Constante API | Valor Entero | Constante API | Valor Entero |
| :---- | :---- | :---- | :---- | :---- | :---- |
| mt5.TIMEFRAME\_M1 | 1 | mt5.TIMEFRAME\_M15 | 15 | mt5.TIMEFRAME\_H4 | 16388 |
| mt5.TIMEFRAME\_M2 | 2 | mt5.TIMEFRAME\_M20 | 20 | mt5.TIMEFRAME\_H6 | 16390 |
| mt5.TIMEFRAME\_M3 | 3 | mt5.TIMEFRAME\_M30 | 30 | mt5.TIMEFRAME\_H8 | 16392 |
| mt5.TIMEFRAME\_M4 | 4 | mt5.TIMEFRAME\_H1 | 16385 | mt5.TIMEFRAME\_H12 | 16396 |
| mt5.TIMEFRAME\_M5 | 5 | mt5.TIMEFRAME\_H2 | 16386 | mt5.TIMEFRAME\_D1 | 16401 |
| mt5.TIMEFRAME\_M6 | 6 | mt5.TIMEFRAME\_H3 | 16387 | mt5.TIMEFRAME\_W1 | 32769 |
| mt5.TIMEFRAME\_M10 | 10 |  |  | mt5.TIMEFRAME\_MN1 | 49153 |
| mt5.TIMEFRAME\_M12 | 12 |  |  |  |  |

### **Estructura de Retorno y Formateo a Pandas**

El array de NumPy retornado contiene las siguientes columnas estructuradas de bajo nivel en formato binario bin-packed 23:  
![][image9]

* **time**: Entero de 64 bits que representa la marca de tiempo de apertura de la barra expresada en segundos epoch Unix.23  
* **open / high / low / close**: Precios flotantes de precisión doble que detallan el recorrido del precio en el periodo.23  
* **tick\_volume**: Número total de ticks de cotización que alteraron el precio dentro de la duración de la barra.23  
* **spread**: Spread mínimo medido en puntos registrado durante la barra.23  
* **real\_volume**: Volumen comercial real transaccionado en bolsa de valores (utilizado en activos centralizados).23

### **Gestión Estricta de Horas y Zonas Horarias**

La terminal de MetaTrader almacena de forma inalterable los tiempos de apertura de barras y ticks según la hora del servidor del bróker, la cual suele estar configurada en GMT+2 o GMT+3 para alinearse con el cierre de Nueva York.23 No obstante, al realizar la comunicación por canal IPC, la API de Python requiere que toda marca de tiempo enviada en objetos datetime de Python esté explícitamente parametrizada en la zona horaria UTC pura (por ejemplo, instanciando con tzinfo=timezone.utc o mediante pytz.timezone("Etc/UTC")).23 De omitirse esto, Python interpretará el objeto datetime utilizando la zona horaria del sistema operativo local (macOS del cliente o VPS Windows), lo que provocará desajustes de horas en la recuperación de barras históricas.23 Al transformar el array a un DataFrame de Pandas, se debe forzar el parseo especificando la unidad y la zona horaria 23:

Python  
import pandas as pd  
rates \= mt5.copy\_rates\_from\_pos("EURUSD", mt5.TIMEFRAME\_M5, 0, 1000)  
df \= pd.DataFrame(rates)  
df\['time'\] \= pd.to\_datetime(df\['time'\], unit='s', utc=True)

## **4\. Flujo de Datos de Ticks**

Para algoritmos HFT, scalping de microestructura o la monitorización de flujos de spread instantáneos, la recuperación de ticks transaccionales individuales se realiza mediante llamadas directas a la base de datos de la terminal.28

### **Métodos de Recuperación y Parámetros**

* **mt5.copy\_ticks\_from(symbol, date\_from, count, flags)**: Obtiene count ticks moviéndose cronológicamente hacia adelante en el tiempo a partir de la marca temporal de origen determinada por date\_from.29  
* **mt5.copy\_ticks\_range(symbol, date\_from, date\_to, flags)**: Extrae todos los ticks comprendidos dentro de la ventana de tiempo especificada entre date\_from y date\_to.30

### **Banderas de Control de Consulta (Flags)**

El parámetro flags define qué subconjunto de eventos de precios debe filtrar la API antes de transferir los datos por el canal IPC 29:

* **mt5.COPY\_TICKS\_ALL**: Retorna el registro completo de todos los ticks sin aplicar filtros.29 Contiene tanto cambios de cotización (bid/ask) como transacciones reales de volumen.29  
* **mt5.COPY\_TICKS\_INFO**: Limita la respuesta del servidor y retorna únicamente aquellos ticks en los que se registró una alteración en las cotizaciones de compra y venta (bid o ask), ignorando transacciones de volumen.29  
* **mt5.COPY\_TICKS\_TRADE**: Devuelve de manera selectiva los ticks que registran transacciones reales de compra o venta en bolsa, modificando los campos last y volume.29

### **Campos Retornados y Análisis de Variación mediante TICK\_FLAG\_\***

Cada tick devuelto se almacena en una fila de un array NumPy estruturado con los campos: time (segundos), bid (precio de demanda), ask (precio de oferta), last (último precio operado en bolsa), volume (volumen entero de transacción), time\_msc (marca de tiempo exacta en milisegundos), flags (máscara de bits de variación) y volume\_real (volumen de precisión flotante).20  
El campo flags contiene una máscara binaria compuesta por la suma de constantes lógicas de bit.28 Evaluar estos bits mediante el operador binario AND (&) en Python permite saber con absoluta exactitud qué cambió en cada tick con respecto al tick predecesor 29:

| Constante Flag de Bit | Valor Binario | Descripción Técnica del Cambio de Estado |
| :---- | :---- | :---- |
| mt5.TICK\_FLAG\_BID | 2 | Se ha registrado una modificación en el precio Bid (precio de venta).20 |
| mt5.TICK\_FLAG\_ASK | 4 | Se ha registrado una modificación en el precio Ask (precio de compra).29 |
| mt5.TICK\_FLAG\_LAST | 8 | Se ha modificado el precio de la última transacción real negociada (last).29 |
| mt5.TICK\_FLAG\_VOLUME | 16 | Se ha modificado el volumen de negociación de la última transacción real.29 |
| mt5.TICK\_FLAG\_BUY | 32 | El tick fue iniciado por una transacción de compra de mercado.29 |
| mt5.TICK\_FLAG\_SELL | 64 | El tick fue iniciado por una transacción de venta de mercado.29 |

### **Límites de Memoria y Paginación**

La terminal de MetaTrader 5 almacena de forma local el histórico bruto de ticks comprimido en archivos de disco en el VPS.23 Solicitar rangos excesivamente grandes en una sola llamada (por ejemplo, más de ![][image10] de ticks) obligará a la terminal a descompilar datos masivos de disco y, potencialmente, a realizar descargas síncronas de red desde el servidor del bróker.3 Esto bloqueará el canal IPC y congelará el hilo de ejecución de Python.4 Para evitar desbordamientos de memoria RAM en el VPS o caídas por timeout, se debe diseñar un algoritmo de paginación de datos dividiendo la consulta en intervalos diarios o limitando las llamadas a bloques máximos de ![][image11] ticks de forma secuencial.

## **5\. Profundidad de Mercado (DOM / Order Book)**

El libro de órdenes, conocido como Depth of Market (DOM), proporciona una vista interna sobre la liquidez disponible por encima y por debajo del precio actual del mercado de CFDs o futuros.32

### **Suscripción y Polling al DOM**

Debido a que la API de Python opera de forma sincrónica y no admite devoluciones de llamada directas (*asynchronous callbacks*) para capturar eventos de red de la terminal (como el evento de MQL5 OnBookEvent), el desarrollador debe estructurar un patrón de suscripción y polling activo en bucle supervisado 34:

1. **mt5.market\_book\_add(symbol)**: Registra la terminal local a la recepción del flujo de red de la profundidad de mercado para el activo especificado.35 Si es exitosa, devuelve True.34 Esta función eleva de forma interna el contador de suscripción del gráfico de ese símbolo en la terminal.34  
2. **mt5.market\_book\_get(symbol)**: Recupera de forma síncrona el contenido instantáneo del libro de órdenes.34 Devuelve una tupla de objetos BookInfo.34 En caso de no haber suscripción activa o si el bróker no soporta DOM, retorna None.34  
3. **mt5.market\_book\_release(symbol)**: Cancela la suscripción al flujo de red del DOM de la terminal local, liberando recursos y ancho de banda en el canal de comunicación del VPS.34

### **Estructura BookInfo e Interpretación de Datos**

Cada nivel de precios dentro de la tupla devuelta por mt5.market\_book\_get() está representado por un objeto BookInfo con cuatro atributos 34:

* **price**: El nivel de precio absoluto correspondiente al lote de órdenes límite.34  
* **volume**: El volumen total acumulado en ese precio expresado como número entero en lotes.34  
* **volume\_dbl** (mapeado como volume\_real en MQL5): El volumen exacto con precisión flotante decimal.34  
* **type**: El tipo de orden presente en ese nivel específico, mapeado con constantes numéricas del módulo.34

La interpretación del campo type rige la disposición de la orden dentro de la matriz de profundidad para reconstruir de forma gráfica el libro 34:

| Valor Entero | Constante API de Python | Significado Comercial | Posición en la Estructura de Datos |
| :---- | :---- | :---- | :---- |
| 1 | mt5.BOOK\_TYPE\_SELL | Oferta límite de venta activa (Asks/Offers).34 | Se sitúa en la mitad superior de la matriz. Ordenada de mayor a menor precio.34 |
| 2 | mt5.BOOK\_TYPE\_BUY | Demanda límite de compra activa (Bids).34 | Se sitúa en la mitad inferior de la matriz. Ordenada de mayor a menor precio.34 |
| 3 | mt5.BOOK\_TYPE\_SELL\_MARKET | Orden entrante de venta a mercado.34 | Golpea de manera inmediata contra el mejor Bid de compra disponible.34 |
| 4 | mt5.BOOK\_TYPE\_BUY\_MARKET | Orden entrante de compra a mercado.34 | Golpea de manera inmediata contra el mejor Ask de venta disponible.34 |

### **Suministro de DOM Real en el Mercado Forex**

Debido a que el mercado cambiario (Forex) opera de manera descentralizada y extrabursátil (Over-The-Counter), la mayoría de los brókers minoristas estructurados bajo el modelo de creación de mercado (*Market Maker*) carecen de un libro de órdenes consolidado real.34 Para estos brókers, llamar a mt5.market\_book\_get() devolverá un array simulado o simplemente fallará devolviendo None.34 El acceso a un DOM real, con profundidades dinámicas en las puntas de liquidez y volúmenes reales, está restringido de manera estricta a brókers que ofrezcan cuentas de ejecución directa en redes de comunicación electrónica institucionales (ECN, como LMAX, Pepperstone o IC Markets) o mediante la cotización de futuros centralizados de divisas (CME) operados desde cuentas compensadas.34

## **6\. Envío y Gestión de Órdenes (Operaciones Comerciales)**

La operativa comercial mediante la API requiere un nivel absoluto de control sintáctico para garantizar la correcta estructuración de las solicitudes antes de ser enviadas al bróker.37

### **Validación Comercial Previa: mt5.order\_check()**

Toda transacción comercial debe someterse a una validación síncrona local mediante la función mt5.order\_check(request\_dict) antes de ser transmitida físicamente al servidor.16 Esta función comprueba que los tipos de datos del diccionario sean correctos, verifica los niveles de precios de SL/TP, evalúa la validez del volumen y realiza el cálculo matemático de margen requerido para asegurar que el capital disponible en la cuenta de trading sea suficiente, evitando así rechazos directos del servidor.16

### **La Estructura TradeRequest en Python**

La API interactúa comercialmente mediante el paso de un diccionario de Python que simula la estructura nativa MqlTradeRequest de MQL5.37 Los campos que admite este diccionario son 37:

Python  
request \= {  
    "action": int,             \# Identificador de la acción (TRADE\_ACTION\_\*) \[obligatorio\]  
    "magic": int,              \# Magic Number identificador del bot   
    "order": int,              \# Ticket de la orden pendiente a modificar o cancelar   
    "symbol": str,             \# Nombre del activo financiero (e.g., "EURUSD")   
    "volume": float,           \# Volumen comercial expresado en número de lotes   
    "price": float,            \# Precio de ejecución límite o stop   
    "stoplimit": float,        \# Precio de activación para órdenes Stop-Limit   
    "sl": float,               \# Nivel de precio del Stop Loss   
    "tp": float,               \# Nivel de precio del Take Profit   
    "deviation": int,          \# Desviación máxima permitida respecto al precio de envío (en puntos)   
    "type": int,               \# Dirección de la orden (ORDER\_TYPE\_\*)   
    "type\_filling": int,       \# Política de llenado de la orden (ORDER\_FILLING\_\*)   
    "type\_time": int,          \# Tipo de vigencia temporal de la orden (ORDER\_TIME\_\*)   
    "expiration": int,         \# Fecha de expiración de la orden en formato timestamp de segundos   
    "comment": str,            \# Comentario descriptivo para control interno de logs   
    "position": int,           \# Ticket único de la posición comercial a modificar o cerrar   
    "position\_by": int         \# Ticket de la posición opuesta a compensar en modo "Close By"   
}

La política de llenado de la orden (type\_filling) define cómo debe interactuar la orden con la liquidez del bróker 16:

* **mt5.ORDER\_FILLING\_FOK** (Fill or Kill): La orden exige que todo el volumen solicitado sea ejecutado inmediatamente y al mismo precio.16 Si no hay suficiente volumen disponible en el mercado, se cancela completamente.16  
* **mt5.ORDER\_FILLING\_IOC** (Immediate or Cancel): Permite la ejecución parcial instantánea de la orden comercial.16 El volumen que no pueda ser llenado de forma inmediata en el libro se elimina del mercado.16  
* **mt5.ORDER\_FILLING\_RETURN**: Permite la ejecución parcial de la orden.16 El volumen residual restante no ejecutado se mantiene en el libro en forma de orden pendiente.16

### **Resultado del Envío Comercial: OrderSendResult**

Al enviar la orden física mediante mt5.order\_send(request\_dict), la API devuelve una estructura OrderSendResult con los campos del estado de la transacción en el servidor 37:

* **retcode**: Código de respuesta del servidor de trading.37 Un valor de 10009 (mt5.TRADE\_RETCODE\_DONE) es el único que confirma una transacción completada con éxito.37  
* **order**: Número de ticket único asignado a la orden colocada en el sistema.37  
* **deal**: Número de ticket único de la transacción de liquidación comercial ejecutada (*Deal*).37  
* **volume**: El volumen real de lotes comerciales liquidados con éxito por el servidor.37  
* **price**: El precio exacto al que fue ejecutada y pactada la transacción por la mesa de dinero.37  
* **bid / ask**: Cotización vigente al momento exacto en que el servidor procesó el envío.37  
* **comment**: Texto descriptivo devuelto por el bróker sobre el resultado (e.g., "Request executed").37

### **Patrones de Configuración de Diccionarios de Órdenes**

A continuación se detallan de manera precisa las configuraciones necesarias de los diccionarios de solicitud para cada una de las operaciones avanzadas del sistema comercial 16:

#### **Patrón 1: Orden de Mercado (Compra Inmediata)**

Utiliza la acción de transacción directa con ejecución inmediata 16:

Python  
market\_buy\_request \= {  
    "action": mt5.TRADE\_ACTION\_DEAL,  
    "symbol": "EURUSD",  
    "volume": 0.1,  
    "type": mt5.ORDER\_TYPE\_BUY,  
    "price": mt5.symbol\_info\_tick("EURUSD").ask,  
    "deviation": 10,  
    "magic": 10001,  
    "comment": "Market Buy Python",  
    "type\_time": mt5.ORDER\_TIME\_GTC,  
    "type\_filling": mt5.ORDER\_FILLING\_IOC  
}

#### **Patrón 2: Orden Pendiente (Buy Limit por debajo del mercado)**

Inserta una orden pasiva de compra en el libro de órdenes a la espera de que el precio retroceda a un nivel determinado 38:

Python  
pending\_limit\_request \= {  
    "action": mt5.TRADE\_ACTION\_PENDING,  
    "symbol": "EURUSD",  
    "volume": 0.1,  
    "price": 1.08500,  \# Precio límite por debajo de la cotización actual  
    "type": mt5.ORDER\_TYPE\_BUY\_LIMIT,  
    "magic": 10002,  
    "comment": "Buy Limit Python",  
    "type\_time": mt5.ORDER\_TIME\_GTC,  
    "type\_filling": mt5.ORDER\_FILLING\_RETURN  
}

#### **Patrón 3: Modificación de Stop Loss y Take Profit de una Posición**

Aplica la acción de reajuste de protección de riesgo vinculándola estrictamente al ticket único de la posición 38:

Python  
modify\_sltp\_request \= {  
    "action": mt5.TRADE\_ACTION\_SLTP,  
    "symbol": "EURUSD",  
    "position": 548297723,  \# Ticket de la posición abierta previamente  
    "sl": 1.08200,          \# Nuevo nivel de Stop Loss  
    "tp": 1.09500,          \# Nuevo nivel de Take Profit  
    "magic": 10001  
}

#### **Patrón 4: Cierre Total de una Posición de Mercado**

Para liquidar una posición de compra en mercado, se debe enviar una orden de mercado opuesta (venta) especificando el volumen completo y el identificador de la posición para compensar y liberar el margen 37:

Python  
close\_full\_request \= {  
    "action": mt5.TRADE\_ACTION\_DEAL,  
    "symbol": "EURUSD",  
    "volume": 0.1,  \# Volumen completo de la posición abierta  
    "type": mt5.ORDER\_TYPE\_SELL,  \# Opuesto a la posición original  
    "position": 548297723,  \# Ticket de la posición que se desea cerrar  
    "price": mt5.symbol\_info\_tick("EURUSD").bid,  
    "deviation": 10,  
    "magic": 10001,  
    "comment": "Full Close Python",  
    "type\_time": mt5.ORDER\_TIME\_GTC,  
    "type\_filling": mt5.ORDER\_FILLING\_IOC  
}

#### **Patrón 5: Cierre Parcial de una Posición**

Sigue la misma lógica que el cierre completo, pero el volumen indicado en la transacción es menor al volumen actual de la posición.37 La terminal cierra el volumen especificado y reabre de manera automática el volumen remanente asignándole un nuevo ID de ticket 37:

Python  
close\_partial\_request \= {  
    "action": mt5.TRADE\_ACTION\_DEAL,  
    "symbol": "EURUSD",  
    "volume": 0.04,  \# Se cierran 0.04 lotes de una posición original de 0.1  
    "type": mt5.ORDER\_TYPE\_SELL,  
    "position": 548297723,  
    "price": mt5.symbol\_info\_tick("EURUSD").bid,  
    "deviation": 10,  
    "magic": 10001,  
    "comment": "Partial Close Python",  
    "type\_time": mt5.ORDER\_TIME\_GTC,  
    "type\_filling": mt5.ORDER\_FILLING\_IOC  
}

#### **Patrón 6: Cierre por Posición Opuesta (Close By)**

En cuentas con modo de cobertura (*hedging*), si existen dos posiciones abiertas en direcciones opuestas sobre el mismo activo, este patrón permite cerrarlas de manera simultánea ahorrando costes de spread y comisiones de doble ejecución 37:

Python  
close\_by\_request \= {  
    "action": mt5.TRADE\_ACTION\_CLOSE\_BY,  
    "symbol": "EURUSD",  
    "position": 548297723,     \# Ticket de la posición larga (Buy)  
    "position\_by": 548297854,  \# Ticket de la posición corta (Sell)  
    "magic": 10001  
}

## **7\. Consulta e Inspección de Posiciones y Órdenes**

La API proporciona un grupo de ocho funciones de consulta que permiten extraer y auditar el estado comercial actual y el histórico de la cuenta de trading en el servidor.5  
A continuación se catalogan exhaustivamente estas funciones, detallando sus filtros de consulta admisibles y los campos de retorno estructurales 39:

| Función de Consulta | Filtros Soportados | Descripción y Campos Estructurales Retornados |
| :---- | :---- | :---- |
| mt5.positions\_total() | Ninguno | Retorna el conteo total numérico (entero) de posiciones actualmente abiertas en mercado.5 |
| mt5.positions\_get() | symbol, group, ticket 42 | Obtiene la lista de posiciones abiertas que coinciden con los filtros.42 Si no hay filtros, retorna todas las posiciones de la cuenta.42 Los objetos retornados contienen campos clave como: ticket, time (epoch segundos), type (compra/venta), magic, volume, price\_open (precio de entrada), sl, tp, price\_current (precio de valoración flotante), swap, profit y comment.42 |
| mt5.orders\_total() | Ninguno | Retorna un entero con la cantidad de órdenes pendientes activas (órdenes de límite y stop no ejecutadas en el libro).5 |
| mt5.orders\_get() | symbol, group, ticket 41 | Recupera el listado detallado de órdenes pendientes activas.41 Estructura similar a la de posiciones, incluyendo campos críticos como: ticket, time\_setup (fecha de colocación), type, price\_open, sl, tp y price\_stoplimit.41 |
| mt5.history\_orders\_total() | date\_from, date\_to 5 | Retorna el número de órdenes canceladas, ejecutadas o expiradas almacenadas en el histórico del bróker dentro del rango temporal.5 |
| mt5.history\_orders\_get() | date\_from, date\_to, group, ticket, position 39 | Extrae las órdenes del histórico.39 Sostiene filtros avanzados como position, que permite aislar de forma unívoca todas las órdenes de entrada, stop y salida asociadas a una posición específica.39 Los campos retornados incluyen: ticket, time\_setup, time\_done (fecha de finalización), type, state (estado de orden cancelada, completada o rechazada), price\_open, sl y tp.39 |
| mt5.history\_deals\_total() | date\_from, date\_to 5 | Retorna el número total de transacciones financieras reales (*Deals*) procesadas y liquidadas en la cuenta de trading en el periodo.5 |
| mt5.history\_deals\_get() | date\_from, date\_to, group, ticket, position 40 | Obtiene las transacciones de liquidación reales (*Deals*).40 Campos críticos del objeto devuelto: ticket (ID del Deal), order (ticket de la orden origen), time, time\_msc, type (compra/venta de liquidación), entry (0 para entrada (In), 1 para salida (Out), 2 para inversión de sentido (In/Out)), position\_id (ticket de la posición asociada), volume, price, profit, commission y comment.40 |

## **8\. Tratamiento de Errores e Inestabilidades**

Para evitar que el bot de trading sufra caídas catastróficas, se debe diseñar un sistema defensivo capaz de gestionar de forma diferenciada los errores locales del módulo de Python y los rechazos del servidor del bróker.6

### **Códigos de Fallo del Runtime (mt5.last\_error())**

El valor de error almacenado internamente tras una llamada fallida a las funciones de la API de Python se evalúa consultando las siguientes constantes numéricas mapeadas 7:

| Constante Error | Valor de Error | Explicación Técnica del Origen del Fallo |
| :---- | :---- | :---- |
| mt5.RES\_S\_OK | 1 | Operación completada con éxito. Sin fallos.7 |
| mt5.RES\_E\_FAIL | \-1 | Fallo común indeterminado en el intérprete o el canal.7 |
| mt5.RES\_E\_INVALID\_PARAMS | \-2 | Argumentos inválidos o tipos de datos incompatibles pasados a la función.7 |
| mt5.RES\_E\_NO\_MEMORY | \-3 | Fallo de asignación de memoria RAM en el sistema operativo local.7 |
| mt5.RES\_E\_NOT\_FOUND | \-4 | El histórico de datos solicitado no existe en la base de datos.7 |
| mt5.RES\_E\_INVALID\_VERSION | \-5 | Incompatibilidad física entre la biblioteca de Python y la terminal.7 |
| mt5.RES\_E\_AUTH\_FAILED | \-6 | Fallo de autenticación. Credenciales o servidores de red inválidos.7 |
| mt5.RES\_E\_UNSUPPORTED | \-7 | El terminal no admite el método de API seleccionado.7 |
| mt5.RES\_E\_AUTO\_TRADING\_DISABLED | \-8 | Algorithmic trading deshabilitado en los menús de la terminal.7 |
| mt5.RES\_E\_INTERNAL\_FAIL | \-10000 | Error crítico de comunicación interna general en los sockets IPC.7 |
| mt5.RES\_E\_INTERNAL\_FAIL\_SEND | \-10001 | Error físico al transmitir paquetes de datos por el socket IPC.7 |
| mt5.RES\_E\_INTERNAL\_FAIL\_RECEIVE | \-10002 | Error al leer los buffers devueltos por la terminal en el socket IPC.7 |
| mt5.RES\_E\_INTERNAL\_FAIL\_INIT | \-10003 | Fallo estructural al inicializar los hilos de red IPC.7 |
| mt5.RES\_E\_INTERNAL\_FAIL\_CONNECT | \-10003 | No se pudo establecer comunicación con la terminal MetaTrader 5\.7 |
| mt5.RES\_E\_INTERNAL\_FAIL\_TIMEOUT | \-10005 | El terminal no respondió dentro del límite de tiempo configurado.7 |

### **Diferenciación: Errores de API vs Errores de Servidor de Trading**

Es de suma importancia separar conceptualmente estos dos tipos de fallos en el diseño de la arquitectura del bot:

* **Errores locales de la API de Python**: Son devueltos por mt5.last\_error().7 Representan problemas de comunicación entre el proceso local de Python y el proceso de la terminal local en el VPS Windows.7 No tienen relación con el bróker o el mercado.7 Se solucionan de forma interna reiniciando el puente IPC de red.8  
* **Errores de Ejecución Comercial del Servidor**: Son devueltos exclusivamente en el campo retcode dentro de las estructuras de respuesta OrderCheckResult y OrderSendResult.37 Representan el rechazo de la orden por parte del servidor del bróker debido a inconsistencias de mercado.37 Los códigos comunes son, por ejemplo, 10004 (Requote/Recotización) 45, 10014 (Volumen de lote inválido), 10018 (Mercado cerrado) o 10027 (Autotrading deshabilitado por el terminal del cliente).45

## **9\. Rendimiento, Concurrencia y Límites Físicos**

El diseño de un sistema transaccional robusto exige conocer las fronteras de transferencia del canal IPC del módulo síncrono para optimizar el rendimiento del VPS.4

### **Cuellos de Botella y Restricciones de Concurrencia**

La mayor limitación del paquete oficial de Python MetaTrader5 es que todas sus funciones son de naturaleza **estrictamente síncrona y bloqueante**.4 Cada vez que se solicita la copia de rates históricos, ticks o el envío de órdenes, el hilo primario de ejecución del intérprete de Python se congela por completo a la espera de que el canal de bajo nivel IPC complete la transferencia con la terminal de Windows.4 Debido al Global Interpreter Lock (GIL) de Python, si este módulo se integra directamente en frameworks asíncronos como FastAPI, aiomql o event loops de asyncio, bloqueará toda la aplicación, degradando su capacidad para recibir peticiones externas del cliente macOS.4

* **Mitigación mediante Threading**: Para evitar la congelación de la pasarela, toda llamada síncrona de MT5 debe delegarse a un pool de hilos del sistema utilizando ejecutores asíncronos en segundo plano 4:  
  Python  
  import asyncio  
  import MetaTrader5 as mt5

  async def copy\_rates\_threadsafe(symbol, timeframe, count):  
      loop \= asyncio.get\_running\_loop()  
      \# Offload the blocking IPC call to an OS thread executor  
      rates \= await loop.run\_in\_executor(None, mt5.copy\_rates\_from\_pos, symbol, timeframe, 0, count)  
      return rates

### **Benchmarks de Velocidad de Ejecución**

Bajo un VPS Windows Server estándar optimizado (e.g., 2 vCPUs Xeon de 2.5 GHz, 4 GB RAM, almacenamiento SSD y latencia física de red con el bróker ![][image12] ms), los tiempos típicos de respuesta de la API de MT5 se detallan en la siguiente tabla de latencia medida 31:

| Operación de la API de Python | Tamaño del Bloque de Datos | Tiempo Promedio de Respuesta |
| :---- | :---- | :---- |
| mt5.symbol\_info\_tick() | Único tick en caché local | ![][image13] |
| mt5.order\_check() | Diccionario TradeRequest de prueba | ![][image14] |
| mt5.order\_send() | Ejecución de mercado (tiempo local pre-red) | ![][image15] |
| mt5.copy\_rates\_from\_pos() | ![][image16] barras (datos en caché de terminal) | ![][image17] |
| mt5.copy\_ticks\_range() | ![][image18] ticks (datos en disco del terminal) | ![][image19] |

## **10\. Integración Avanzada con el Ecosistema Python**

La pasarela (Gateway) de conexión en el VPS debe envolver la API de MetaTrader 5 dentro de estructuras orientadas a objetos, permitiendo la manipulación avanzada de datos de forma limpia.4

### **Manejo de Series Temporales y Timestamps con Pandas**

Al reconstruir series históricas en Pandas, la marca de tiempo epoch devuelta en segundos debe convertirse asegurando que el índice del DataFrame mantenga la localización de zona horaria correcta para evitar sesgos temporales en análisis cuantitativos 23:

Python  
import pandas as pd  
import pytz

def rates\_to\_dataframe(raw\_rates) \-\> pd.DataFrame:  
    df \= pd.DataFrame(raw\_rates)  
    \# Convertir a datetime de Pandas aplicando localización UTC estricta  
    df\['time'\] \= pd.to\_datetime(df\['time'\], unit='s', utc=True)  
    df.set\_index('time', inplace=True)  
    return df

### **Visualización Gráfica y Monitorización de Operaciones**

La monitorización y visualización del mercado se pueden realizar de manera eficiente utilizando bibliotecas de trazado de gráficos como Matplotlib o Plotly.5 Esto permite graficar las series OHLCV históricas e superponer las líneas de precio promedio de entrada, Stop Loss y Take Profit calculadas por el bot en el VPS para enviarlas en forma de imagen comprimida al cliente macOS.5

### **Planificación de Tareas (Scheduling) con Polling Supervisado**

En ausencia de un flujo de sockets bidireccional puro controlado por eventos, se debe implementar una biblioteca de planificación de alto rendimiento como APScheduler o schedule para ejecutar bucles de polling periódicos que auditen el estado de la conexión comercial, actualicen las variables del libro de órdenes o busquen el cierre de posiciones flotantes cada determinado lapso de milisegundos.17

## **Código de Producción de la Pasarela Comercial (VPS Gateway)**

La siguiente clase de Python representa un módulo de producción altamente robusto, completamente tipado, encapsulado mediante clases de datos (dataclasses) y diseñado para ejecutarse de forma continua dentro de la pasarela del VPS Windows. Contiene la totalidad de los patrones avanzados de ejecución comercial (órdenes de mercado, pendientes, modificaciones, cierres totales, parciales y compensaciones "Close By") y provee conversión directa a Pandas con formateo de fechas e integración con sistemas de monitorización periódica.6

Python  
"""  
Módulo de Infraestructura de Ejecución Comercial y Análisis Técnico para MetaTrader 5\.  
Diseñado para operar de forma continua en un VPS Windows expuesto por canal seguro a macOS.  
"""

import logging  
from datetime import datetime, timezone  
from dataclasses import dataclass  
from typing import Optional, Dict, List, Tuple, Any, Union  
import MetaTrader5 as mt5  
import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt

\# Configuración central del sistema de registros y trazabilidad  
logging.basicConfig(  
    level=logging.INFO,  
    format\="%(asctime)s \[%(levelname)s\] (%(filename)s:%(lineno)d) \- %(message)s"  
)  
logger \= logging.getLogger("MT5AdvancedGateway")

@dataclass(frozen=True)  
class ActivePosition:  
    """Representación inmutable de una posición activa en mercado."""  
    ticket: int  
    symbol: str  
    volume: float  
    position\_type: int  
    price\_open: float  
    sl: float  
    tp: float  
    profit: float  
    magic: int  
    comment: str

class MT5GatewayError(Exception):  
    """Excepción base para fallos del sistema de la pasarela."""  
    pass

class MT5AdvancedGateway:  
    """  
    Controlador maestro de conexión y ejecución transaccional sobre MetaTrader 5\.  
    Gestiona el ciclo de vida IPC, extracción de datos y comandos comerciales.  
    """

    def \_\_init\_\_(self,   
                 path: Optional\[str\] \= None,   
                 login: Optional\[int\] \= None,   
                 password: Optional\[str\] \= None,   
                 server: Optional\[str\] \= None,   
                 timeout: int \= 60000,   
                 portable: bool \= False) \-\> None:  
        """Inicializa la configuración física del Gateway local del VPS."""  
        self.path: Optional\[str\] \= path  
        self.login: Optional\[int\] \= login  
        self.password: Optional\[str\] \= password  
        self.server: Optional\[str\] \= server  
        self.timeout: int \= timeout  
        self.portable: bool \= portable  
        self.\_connected: bool \= False

    def conectar(self) \-\> bool:  
        """Establece e inicializa el canal de comunicación IPC síncrono con el terminal."""  
        logger.info("Estableciendo enlace de red local e inicializando buffers IPC...")  
          
        \# Parámetros obligatorios estructurados para inicialización condicional  
        init\_args: Dict\[str, Any\] \= {"timeout": self.timeout, "portable": self.portable}  
        if self.path:  
            init\_args\["path"\] \= self.path  
        if self.login:  
            init\_args\["login"\] \= self.login  
        if self.password:  
            init\_args\["password"\] \= self.password  
        if self.server:  
            init\_args\["server"\] \= self.server

        \# Invocar la llamada IPC de inicialización síncrona  
        if not mt5.initialize(\*\*init\_args):  
            err\_code, err\_desc \= mt5.last\_error()  
            msg \= f"No se pudo inicializar la conexión con el terminal MT5: {err\_code} \- {err\_desc}"  
            logger.critical(msg)  
            raise MT5GatewayError(msg)

        logger.info("Pasarela IPC con el terminal MT5 establecida correctamente en el VPS Windows.")  
        self.\_connected \= True  
        return True

    def verificar\_enlace(self) \-\> bool:  
        """Audita el estado físico de la pasarela y la conexión de red del terminal."""  
        if not self.\_connected:  
            return False  
          
        t\_info \= mt5.terminal\_info()  
        if t\_info is None or not t\_info.connected:  
            logger.warning("Conexión perdida con el terminal MT5 o terminal desconectada del bróker.")  
            return False  
        return True

    def desconectar(self) \-\> None:  
        """Desmonta el puente IPC y libera de forma segura los descriptores de sockets."""  
        if self.\_connected:  
            mt5.shutdown()  
            self.\_connected \= False  
            logger.info("Pasarela de MT5 desconectada y recursos liberados en el VPS Windows.")

    def obtener\_ohlcv(self, symbol: str, timeframe: int, count: int) \-\> pd.DataFrame:  
        """  
        Extrae barras históricas OHLCV y las convierte en un DataFrame estructurado con zona horaria UTC.  
        """  
        if not self.verificar\_enlace():  
            raise MT5GatewayError("La pasarela IPC o el terminal MT5 no están disponibles para la solicitud.")

        \# Sincronizar de forma previa la presencia del activo en el MarketWatch  
        if not mt5.symbol\_select(symbol, True):  
            \_, err\_desc \= mt5.last\_error()  
            raise MT5GatewayError(f"No se pudo seleccionar el activo {symbol} en MarketWatch: {err\_desc}")

        raw\_bars \= mt5.copy\_rates\_from\_pos(symbol, timeframe, 0, count)  
        if raw\_bars is None or len(raw\_bars) \== 0:  
            err\_code, err\_desc \= mt5.last\_error()  
            raise MT5GatewayError(f"Fallo al copiar barras de {symbol}: {err\_code} \- {err\_desc}")

        df \= pd.DataFrame(raw\_bars)  
        df\['time'\] \= pd.to\_datetime(df\['time'\], unit='s', utc=True)  
        df.set\_index('time', inplace=True)  
        return df

    def enviar\_orden(self, request: Dict\[str, Any\]) \-\> Dict\[str, Any\]:  
        """  
        Valida síncronamente y transmite una solicitud comercial al servidor de trading del bróker.  
        """  
        if not self.verificar\_enlace():  
            raise MT5GatewayError("Pérdida de comunicación de red: Transacción comercial suspendida.")

        \# Validación previa requerida antes del envío físico  
        check\_result \= mt5.order\_check(request)  
        if check\_result is None:  
            \_, err\_desc \= mt5.last\_error()  
            raise MT5GatewayError(f"Error de consistencia en order\_check: {err\_desc}")  
              
        if check\_result.retcode\!= 0:  
            raise MT5GatewayError(  
                f"La solicitud falló la comprobación pre-trade local. Código: {check\_result.retcode}. "  
                f"Comentario: {check\_result.comment}. Margen Requerido: {check\_result.margin}"  
            )

        \# Transmisión real de la orden al servidor  
        send\_result \= mt5.order\_send(request)  
        if send\_result is None:  
            err\_code, err\_desc \= mt5.last\_error()  
            raise MT5GatewayError(f"Error crítico en el canal de red de order\_send: {err\_code} \- {err\_desc}")

        result\_dict \= send\_result.\_asdict()  
        if send\_result.retcode\!= mt5.TRADE\_RETCODE\_DONE:  
            raise MT5GatewayError(  
                f"La orden fue rechazada por el servidor del bróker. Código: {send\_result.retcode}. "  
                f"Comentario: {send\_result.comment}"  
            )

        logger.info(f"Orden ejecutada con éxito en el servidor. Ticket generado: {send\_result.order}")  
        return result\_dict

    def ejecutar\_market\_order(self,   
                              symbol: str,   
                              order\_type: int,   
                              volume: float,   
                              sl\_points: Optional\[int\] \= None,   
                              tp\_points: Optional\[int\] \= None,   
                              magic: int \= 20002) \-\> Dict\[str, Any\]:  
        """Patrón Avanzado 1: Transacción inmediata por ejecución de mercado."""  
        sym\_info \= mt5.symbol\_info(symbol)  
        tick \= mt5.symbol\_info\_tick(symbol)  
        if sym\_info is None or tick is None:  
            raise MT5GatewayError(f"Imposible recuperar cotizaciones en tiempo real para {symbol}")

        if order\_type \== mt5.ORDER\_TYPE\_BUY:  
            price \= tick.ask  
            sl \= price \- (sl\_points \* sym\_info.point) if sl\_points else 0.0  
            tp \= price \+ (tp\_points \* sym\_info.point) if tp\_points else 0.0  
        elif order\_type \== mt5.ORDER\_TYPE\_SELL:  
            price \= tick.bid  
            sl \= price \+ (sl\_points \* sym\_info.point) if sl\_points else 0.0  
            tp \= price \- (tp\_points \* sym\_info.point) if tp\_points else 0.0  
        else:  
            raise ValueError("El tipo de orden debe ser ORDER\_TYPE\_BUY u ORDER\_TYPE\_SELL.")

        request \= {  
            "action": mt5.TRADE\_ACTION\_DEAL,  
            "symbol": symbol,  
            "volume": float(volume),  
            "type": order\_type,  
            "price": float(price),  
            "sl": float(round(sl, sym\_info.digits)) if sl \> 0 else 0.0,  
            "tp": float(round(tp, sym\_info.digits)) if tp \> 0 else 0.0,  
            "deviation": 10,  
            "magic": int(magic),  
            "comment": "Market Order Python",  
            "type\_time": mt5.ORDER\_TIME\_GTC,  
            "type\_filling": mt5.ORDER\_FILLING\_IOC  
        }  
        return self.enviar\_orden(request)

    def colocar\_orden\_pendiente(self,   
                                symbol: str,   
                                pending\_type: int,   
                                volume: float,   
                                target\_price: float,   
                                sl\_price: float \= 0.0,   
                                tp\_price: float \= 0.0,   
                                magic: int \= 20003) \-\> Dict\[str, Any\]:  
        """Patrón Avanzado 2: Inserción de orden límite o stop en el libro."""  
        sym\_info \= mt5.symbol\_info(symbol)  
        if sym\_info is None:  
            raise MT5GatewayError(f"No se encontró el activo {symbol} en el servidor.")

        request \= {  
            "action": mt5.TRADE\_ACTION\_PENDING,  
            "symbol": symbol,  
            "volume": float(volume),  
            "price": float(round(target\_price, sym\_info.digits)),  
            "type": pending\_type,  
            "sl": float(round(sl\_price, sym\_info.digits)) if sl\_price \> 0 else 0.0,  
            "tp": float(round(tp\_price, sym\_info.digits)) if tp\_price \> 0 else 0.0,  
            "magic": int(magic),  
            "comment": "Pending Order Python",  
            "type\_time": mt5.ORDER\_TIME\_GTC,  
            "type\_filling": mt5.ORDER\_FILLING\_RETURN  
        }  
        return self.enviar\_orden(request)

    def modificar\_sltp\_posicion(self, ticket: int, new\_sl: float, new\_tp: float) \-\> Dict\[str, Any\]:  
        """Patrón Avanzado 3: Modificación física de los stops de protección de una posición activa."""  
        positions \= mt5.positions\_get(ticket=ticket)  
        if positions is None or len(positions) \== 0:  
            raise MT5GatewayError(f"No se detectó la posición activa asociada al ticket \#{ticket}")

        pos \= positions  
        sym\_info \= mt5.symbol\_info(pos.symbol)  
        if sym\_info is None:  
            raise MT5GatewayError(f"Símbolo {pos.symbol} no disponible en el sistema.")

        request \= {  
            "action": mt5.TRADE\_ACTION\_SLTP,  
            "symbol": pos.symbol,  
            "position": int(ticket),  
            "sl": float(round(new\_sl, sym\_info.digits)) if new\_sl \> 0 else 0.0,  
            "tp": float(round(new\_tp, sym\_info.digits)) if new\_tp \> 0 else 0.0,  
            "magic": int(pos.magic)  
        }  
        return self.enviar\_orden(request)

    def cerrar\_posicion\_completa(self, ticket: int) \-\> Dict\[str, Any\]:  
        """Patrón Avanzado 4: Liquidación y cierre absoluto de una posición abierta."""  
        positions \= mt5.positions\_get(ticket=ticket)  
        if positions is None or len(positions) \== 0:  
            raise MT5GatewayError(f"La posición especificada con ticket \#{ticket} no se encuentra activa.")

        pos \= positions  
        symbol \= pos.symbol  
        volume \= pos.volume  
        pos\_type \= pos.type

        tick \= mt5.symbol\_info\_tick(symbol)  
        if tick is None:  
            raise MT5GatewayError(f"No se pudo recuperar la cotización actual para liquidar posición en {symbol}.")

        \# Invertir el sentido operativo para la orden de salida  
        close\_type \= mt5.ORDER\_TYPE\_SELL if pos\_type \== mt5.POSITION\_TYPE\_BUY else mt5.ORDER\_TYPE\_BUY  
        price \= tick.bid if close\_type \== mt5.ORDER\_TYPE\_SELL else tick.ask

        request \= {  
            "action": mt5.TRADE\_ACTION\_DEAL,  
            "symbol": symbol,  
            "volume": float(volume),  
            "type": close\_type,  
            "position": int(ticket),  \# Campo crítico para ligar la compensación  
            "price": float(price),  
            "deviation": 15,  
            "magic": int(pos.magic),  
            "comment": "Cierre Total Pasarela",  
            "type\_time": mt5.ORDER\_TIME\_GTC,  
            "type\_filling": mt5.ORDER\_FILLING\_IOC  
        }  
        return self.enviar\_orden(request)

    def cerrar\_posicion\_parcial(self, ticket: int, volume\_to\_close: float) \-\> Dict\[str, Any\]:  
        """Patrón Avanzado 5: Cierre parcial del volumen flotante de una posición abierta."""  
        positions \= mt5.positions\_get(ticket=ticket)  
        if positions is None or len(positions) \== 0:  
            raise MT5GatewayError(f"Posición \#{ticket} no encontrada.")

        pos \= positions  
        if volume\_to\_close \>= pos.volume:  
            raise ValueError(f"El volumen de cierre ({volume\_to\_close}) debe ser menor al volumen de la posición ({pos.volume}).")

        tick \= mt5.symbol\_info\_tick(pos.symbol)  
        if tick is None:  
            raise MT5GatewayError(f"Cotización en tiempo real no disponible para {pos.symbol}")

        close\_type \= mt5.ORDER\_TYPE\_SELL if pos.type \== mt5.POSITION\_TYPE\_BUY else mt5.ORDER\_TYPE\_BUY  
        price \= tick.bid if close\_type \== mt5.ORDER\_TYPE\_SELL else tick.ask

        request \= {  
            "action": mt5.TRADE\_ACTION\_DEAL,  
            "symbol": pos.symbol,  
            "volume": float(volume\_to\_close),  
            "type": close\_type,  
            "position": int(ticket),  
            "price": float(price),  
            "deviation": 15,  
            "magic": int(pos.magic),  
            "comment": "Cierre Parcial Python",  
            "type\_time": mt5.ORDER\_TIME\_GTC,  
            "type\_filling": mt5.ORDER\_FILLING\_IOC  
        }  
        return self.enviar\_orden(request)

    def compensar\_posiciones\_close\_by(self, ticket\_larga: int, ticket\_corta: int) \-\> Dict\[str, Any\]:  
        """Patrón Avanzado 6: Cierre simultáneo de dos posiciones opuestas en cuentas de cobertura."""  
        positions\_larga \= mt5.positions\_get(ticket=ticket\_larga)  
        positions\_corta \= mt5.positions\_get(ticket=ticket\_corta)

        if not positions\_larga or not positions\_corta:  
            raise MT5GatewayError("Una o ambas posiciones para compensación Close By no se encuentran disponibles.")

        pos\_l \= positions\_larga  
        pos\_c \= positions\_corta

        if pos\_l.symbol\!= pos\_c.symbol:  
            raise ValueError("Las posiciones para Close By deben pertenecer al mismo instrumento financiero.")

        request \= {  
            "action": mt5.TRADE\_ACTION\_CLOSE\_BY,  
            "symbol": pos\_l.symbol,  
            "position": int(ticket\_larga),  
            "position\_by": int(ticket\_corta),  
            "magic": int(pos\_l.magic)  
        }  
        return self.enviar\_orden(request)

    def graficar\_y\_guardar\_ohlcv(self, symbol: str, timeframe: int, count: int, file\_path: str) \-\> None:  
        """Extrae la serie de precios, grafica las velas de cierre y las exporta a disco en formato PNG."""  
        df \= self.obtener\_ohlcv(symbol, timeframe, count)  
          
        plt.figure(figsize=(12, 6))  
        plt.plot(df.index, df\['close'\], label=f"Precio Cierre {symbol}", color="blue", linewidth=1.5)  
        plt.title(f"Monitor de Precios Históricos \- {symbol}", fontsize=14)  
        plt.xlabel("Línea Temporal (UTC)", fontsize=10)  
        plt.ylabel("Cotización", fontsize=10)  
        plt.grid(True, linestyle="--", alpha=0.5)  
        plt.legend(loc="upper left")  
          
        \# Guardar gráfico en disco para que pueda ser recuperado de forma remota por macOS  
        plt.savefig(file\_path, dpi=150, bbox\_inches='tight')  
        plt.close()  
        logger.info(f"Gráfico técnico generado y almacenado con éxito en: {file\_path}")

\# Demostración del flujo de control transaccional del módulo Gateway  
if \_\_name\_\_ \== "\_\_main\_\_":  
    \# Inicialización de la pasarela comercial (usando credenciales Demo del bróker)  
    \# En producción bajo VPS, estos datos de inicio de sesión deben provenir de variables de entorno protegidas.  
    gateway \= MT5AdvancedGateway(login=25115284, server="MetaQuotes-Demo")  
      
    try:  
        \# Paso 1: Conexión física IPC con el terminal local de MT5  
        gateway.conectar()

        \# Paso 2: Consulta e inspección técnica de barras históricas  
        df\_datos \= gateway.obtener\_ohlcv("EURUSD", mt5.TIMEFRAME\_M5, count=100)  
        print("\\n=== SERIE HISTÓRICA OHLCV RECUPERADA EN PANDAS \===")  
        print(df\_datos.tail(5))

        \# Paso 3: Trazado gráfico de soporte visual  
        gateway.graficar\_y\_guardar\_ohlcv("EURUSD", mt5.TIMEFRAME\_M5, count=50, file\_path="eurusd\_vps\_monitor.png")

        \# Paso 4: Envío de orden de mercado inmediata (Compra)  
        print("\\n=== EJECUTANDO COMPRA A MERCADO DE PRUEBA \===")  
        res\_compra \= gateway.ejecutar\_market\_order(  
            symbol="EURUSD",  
            order\_type=mt5.ORDER\_TYPE\_BUY,  
            volume=0.10,  
            sl\_points=200,  \# 20.0 pips de Stop Loss  
            tp\_points=400   \# 40.0 pips de Take Profit  
        )  
        ticket\_generado \= res\_compra\["order"\]

        \# Paso 5: Modificación síncrona en caliente de los stops protectores de la posición abierta  
        print("\\n=== REAJUSTANDO PROTECCIONES EN CALIENTE \===")  
        \# Se asume un nuevo cálculo de Stop Loss un poco más ajustado  
        info\_pos \= mt5.positions\_get(ticket=ticket\_generado)  
        gateway.modificar\_sltp\_posicion(  
            ticket=ticket\_generado,   
            new\_sl=info\_pos.price\_open \- 0.00100,  \# Reducir Stop Loss a 10 pips  
            new\_tp=info\_pos.price\_open \+ 0.00500   \# Ampliar Take Profit a 50 pips  
        )

        \# Paso 6: Cierre parcial de la posición flotante (cerrando el 40% de la posición)  
        print("\\n=== EJECUTANDO CIERRE PARCIAL COMERCIAL \===")  
        gateway.cerrar\_posicion\_parcial(ticket=ticket\_generado, volume\_to\_close=0.04)

        \# Paso 7: Cierre absoluto del volumen restante remanente en mercado  
        print("\\n=== LIQUIDANDO VOLUMEN FLOTANTE RESTANTE \===")  
        gateway.cerrar\_posicion\_completa(ticket=ticket\_generado)

    except Exception as error\_ejecucion:  
        logger.exception(f"Fallo en el pipeline comercial de la pasarela: {error\_ejecucion}")  
    finally:  
        \# Desconectar el Gateway y cerrar el socket de red IPC de forma limpia  
        gateway.desconectar()

#### **Fuentes citadas**

1. Integrating MetaTrader 5 API in Python : A Practical Example | by Ullasraj \- Medium, acceso: junio 28, 2026, [https://medium.com/@ullasraj1998/integrating-metatrader-5-api-in-python-a-practical-example-3996524f1ea0](https://medium.com/@ullasraj1998/integrating-metatrader-5-api-in-python-a-practical-example-3996524f1ea0)  
2. MetaTrader 5 Python Integration \- Grokipedia, acceso: junio 28, 2026, [https://grokipedia.com/page/MetaTrader\_5\_Python\_Integration](https://grokipedia.com/page/MetaTrader_5_Python_Integration)  
3. metatrader5 \- PyPI, acceso: junio 28, 2026, [https://pypi.org/project/metatrader5/](https://pypi.org/project/metatrader5/)  
4. AIOMQL-The Complete Guide to Building Algorithmic Trading Bots with Python & MetaTrader 5 \- DEV Community, acceso: junio 28, 2026, [https://dev.to/akaichinga/aiomql-the-complete-guide-to-building-algorithmic-trading-bots-with-python-metatrader-5-3bgh](https://dev.to/akaichinga/aiomql-the-complete-guide-to-building-algorithmic-trading-bots-with-python-metatrader-5-3bgh)  
5. Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5](https://www.mql5.com/en/docs/python_metatrader5)  
6. Automated Trading with MetaTrader5: Order Management and Market Data Collection, acceso: junio 28, 2026, [https://dev.to/vital7777/automated-trading-with-metatrader5-order-management-and-market-data-collection-4pb8](https://dev.to/vital7777/automated-trading-with-metatrader5-order-management-and-market-data-collection-4pb8)  
7. last\_error \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5lasterror\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5lasterror_py)  
8. initialize \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5initialize\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5initialize_py)  
9. login \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5login\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5login_py)  
10. What's new in MetaTrader 5 \- Page 4, acceso: junio 28, 2026, [https://www.metatrader5.com/en/releasenotes/terminal/page4](https://www.metatrader5.com/en/releasenotes/terminal/page4)  
11. terminal\_info \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5terminalinfo\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5terminalinfo_py)  
12. shutdown \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5shutdown\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5shutdown_py)  
13. how to use Python in Metatrader \- page 86 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/393357/page86](https://www.mql5.com/en/forum/393357/page86)  
14. account\_info \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5accountinfo\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5accountinfo_py)  
15. Getting information about a trading account \- Advanced language tools \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/python/python\_account\_info](https://www.mql5.com/en/book/advanced/python/python_account_info)  
16. order\_check \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5ordercheck\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5ordercheck_py)  
17. MT5 | Place a trade programmatically with python \- GitHub Gist, acceso: junio 28, 2026, [https://gist.github.com/pawiromitchel/e9a52de7ed65486b0770cd4acd3d8a66](https://gist.github.com/pawiromitchel/e9a52de7ed65486b0770cd4acd3d8a66)  
18. symbols\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5symbolsget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5symbolsget_py)  
19. symbols\_total \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5symbolstotal\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5symbolstotal_py)  
20. symbol\_info\_tick \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5symbolinfotick\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5symbolinfotick_py)  
21. symbol\_select \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5symbolselect\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5symbolselect_py)  
22. symbol\_info \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5symbolinfo\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5symbolinfo_py)  
23. copy\_rates\_range \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5copyratesrange\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesrange_py)  
24. copy\_rates\_from \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5copyratesfrom\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesfrom_py)  
25. copy\_rates\_from\_pos \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5copyratesfrompos\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesfrompos_py)  
26. Python MT5 bot : r/mltraders \- Reddit, acceso: junio 28, 2026, [https://www.reddit.com/r/mltraders/comments/1fl8gkb/python\_mt5\_bot/](https://www.reddit.com/r/mltraders/comments/1fl8gkb/python_mt5_bot/)  
27. 原生Python支持| 知行合一 \- MT5, acceso: junio 28, 2026, [http://mt5.me/mq5\_programming\_for\_traders/advanced\_language\_tools/native\_python\_support.html](http://mt5.me/mq5_programming_for_traders/advanced_language_tools/native_python_support.html)  
28. Reading tick history \- Advanced language tools \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/python/python\_copyticks](https://www.mql5.com/en/book/advanced/python/python_copyticks)  
29. copy\_ticks\_from \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5copyticksfrom\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5copyticksfrom_py)  
30. copy\_ticks\_range \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5copyticksrange\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5copyticksrange_py)  
31. MetaTrader 5 System Requirements for Windows \- Defcofx, acceso: junio 28, 2026, [https://www.defcofx.com/metatrader-5-system-requirements-windows/](https://www.defcofx.com/metatrader-5-system-requirements-windows/)  
32. MetaTrader 5 build 2815: Access to the Depth of Market from Python, revamped Debugger, and Profiler improvements \- Release Notes, acceso: junio 28, 2026, [https://www.metatrader5.com/en/releasenotes/terminal/2186](https://www.metatrader5.com/en/releasenotes/terminal/2186)  
33. MetaTrader 5 Build 2815: Task Manager, data access via Python API and other updates, acceso: junio 28, 2026, [https://www.metatrader5.com/en/news/2187](https://www.metatrader5.com/en/news/2187)  
34. Subscribing to order book changes \- Advanced language tools ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/python/python\_marketbook](https://www.mql5.com/en/book/advanced/python/python_marketbook)  
35. market\_book\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5marketbookget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5marketbookget_py)  
36. market\_book\_add \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5marketbookadd\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5marketbookadd_py)  
37. Checking and sending a trade order \- Advanced language tools ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/python/python\_ordercheck\_ordersend](https://www.mql5.com/en/book/advanced/python/python_ordercheck_ordersend)  
38. Code for 7 Indispensable Functions for your MetaTrader 5 Python Trading Bot. \- GitHub Gist, acceso: junio 28, 2026, [https://gist.github.com/jimtin/0f6e9041c9c494dd479c8d81a473b2f0](https://gist.github.com/jimtin/0f6e9041c9c494dd479c8d81a473b2f0)  
39. history\_orders\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5historyordersget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5historyordersget_py)  
40. history\_deals\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5historydealsget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5historydealsget_py)  
41. orders\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5ordersget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5ordersget_py)  
42. positions\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5positionsget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5positionsget_py)  
43. How to get the final Stop Loss price on a closed trade using MetaTrader for Python?, acceso: junio 28, 2026, [https://stackoverflow.com/questions/73982018/how-to-get-the-final-stop-loss-price-on-a-closed-trade-using-metatrader-for-pyth](https://stackoverflow.com/questions/73982018/how-to-get-the-final-stop-loss-price-on-a-closed-trade-using-metatrader-for-pyth)  
44. Error checking: last\_error \- Advanced language tools \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/advanced/python/python\_last\_error](https://www.mql5.com/en/book/advanced/python/python_last_error)  
45. order\_send failed, retcode=10027 \- MetaTrader 5 \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/376255](https://www.mql5.com/en/forum/376255)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAPQAAAAWCAYAAAD3o7F3AAAGBklEQVR4Xu2bV6hkRRCGy5xzDigmREUU1AdFBXNO+GgGUQyYFRWfzCgqYlaUNaILigEFfdBVQR9ERDGnK4ZV14A5p/rsrp3a2p5z5oyyM/duf1Dc6b/6hDnd1aHOXJFKpVKpVCqVSqVSqYw5S6ptGcXKaJip9qva39l+U/tS7VunXTG79rzjLEnXHmceVPslimPIF2p/Sa89f1D7Su0btT+zdsPs2t2gv9h5K2NEv0ZZWpL+aXQMyAIyXGf5Q9J1d4iOMcKe2aLRMab0a+N9JenvRseAvC/l81ZGSL/Ghp8k+TaJjgE4QIYLaNggCmPIylEYY5rauMnXxusy/LHjxm5q20RxMtLUoG9L8l0dHQPwvQwf0JX/l6Y2bvK18YoMf+y4safMBwFtPj9DL6x2mdo7ajPUNnY+4x5Jxz2mtnc242hJxzNILKV2nfQe5OZqJ6tdr7ZZ1pgJj1O7Kv+FPdTudnXgILXpaic5LXKmpC3EtWqLOJ3tAfd1udo1WdtW0jWOzGVjZ7Uz1G4JunGU2idqt6utGnyjol8bryFJnxUdknIZz6u9pHZo8Bkvy9znbesf/drzXrW9rFJgGbW71D5Xe1zKq6NL1SYkteEwsP2Y0gFNZ0TnIXnQPsyfCQrKT/bcspPaaVl/Ln/GDB44PvZtT6s9kMtAw76QyztmbX1JwYN2s/SuTaOiEaS/SxocFswaSR/PmllfL5et3iG5zF74yqy9JSlxRJ3Fs0bHNY5R+yjrHs6Bxkhv/Cy9AWKUcF8YWxmMAfqirN3m6hmWSDO+k5RAjZQCmnJT/2hrTwZ4z7FZt7YjsP0118nlLXLZ+l5X9pMpFtB0YsuAmnauq2egP+rKJ2QtgtZvyW3nh7Ukjc4efBbQXovXsYy8T06dkzVP6V42zTqBa5Su8VBBW7egMai8ETRmK+oxEzZxZ4Mx00+TFHi3SgqGDf89anDse7G6wHZX21/SgENA+WcArGJITno4nuM8/QJ60P4RdWtPY7FcvtBprN58HT4/68qmMVF0YcoF9LAcLOXj0WIQGW3XxFcK6ImgsQSL5zk1aMz6lJdzmoF+UyjH891X0FYJ2hK5TCIwgs6sP0pK38swH9+hH6tLqnNK0EsBHWnqHxNBi+15Yy6zJSph7cAsvpoz8je8luvH1gVjZj+ioGOTiqbGLrG82o+SlmXnS9rzlo5Ho0FKtF0TXymgyap6Ps6658SgMbNR9ntmA51Zypfj+eISD1YM2uG5TKY0UjrnvKbpHthC4IuDzmtZ5/kxe/GZwdJTCugu/aOtPQnM0rEGeQ/87Pd3DbaLqxdhdRLtArXTCzo2qWhq7IjtV/wPTrbPWgSNJSJsJHPuLduuia8U0GRVPaW97PFBY1ahbHswD/p7oRzPx7I3aisEjV9LUSYhFimdM0ISqYv5ZOAgNN0Diajo5zM/MvKg+VwIxIDu2j/a2pMcTOlYg4QbfgL7vzJfLrnp/LHugU6LneKO/JmEhR/p2q6JrxTQrwYtjugQ92ws1ygz+nosKLdzWum+SjP0SgWN8iNBA/RSLmJeUvpexoQk39m5fFguk7zy2DOc5jRyBv68XftHW3vaj5sYpD0kOa0/4Y8zPfDKtQtTLqCb9lAGrxqoy5LTsONjJ+czSTYg6UWCyPtiwxuWLeY1ggeNEdxjCTwPyzy0hZx2SdY8s2TuX0iV7uuJgmYzw7JOo4Oh8YrFYIbxS/pRUfpeMF2Szt7VsFdZJBeNN7NGxn6G0+OM2rV/DNKeT2XNP2uy7gYDP37fXy7OehcmfUDT0T6TNCryYGdKyjK2wWsFayQbBekY/LZ5baskvRkQ4x2hQZDznpZr0pHud75nJN0TPjKtH0h60NRD415tkOCv3TvBydKOPZedm+MfznVhK5nzt+skUgw6C7975jiMzwxAdDC7Bvd1nqRsNuc2zVYhwPdnqWrXYHAZJXYfZuxruX/anu/2oqT37RFLJGJkuwnGfXKZFRDY88d4XvZPGm39o0t7GrZtwqgTIRH2tfTqcK9dmfQBXalUetSArlQqlUqlUqlUKpVKZT7gH0vURuaKCt6iAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHAAAAAXCAYAAADTEcupAAACYElEQVR4Xu2YO2gUURSGTxQiGiMSSWdIYSGoCEGjIAhamOAzithaBa2CRSqLsKUoVipYRHwWggEVERttfTQBDSSNpAhqQFCQPESiif6Hcy9z9mRmd1K4O3e5H/zsveefWc7ZO/exQxSJRCKRSIQpQXPQX6fRcnsZU5Rcy/cNltuFweeYRw1BnoJ2QkMk1+wyXhHZQ5LrdWs4XkPvbTBUPlMyE7P4BL2hytcUieckubZZw3EQumaDIXIE6qek4DQeu89qs7RIpOV6CFrl2geg04kVLu/cJ+9ntmBmPTTg2uyPKK/IcK6LJvZLtduh1aofLH7QeF/j9mblMb7oXhJ/m/KKSjdJrk+gvdBh6KWLNRxfVJsLPKv6F6AW1+aZWu0HaKJ8T3Ur9CBD96F70B3oNnQLGpbbcvOCJNdL0BXoruvz9zUUPKvOqT4XyT+eRy+XaXuKhpekp7R82aoHabnehDpU/5Rqp7EJ2p1TW909Ncfvfx4umk+bzLQ2SLxHJqYZh7qg89aoA5zrbxN7ptq8Uoypfhqd0Imc2u/uqTn2KfVPLie0Q8WPuvh2FbPY76rEGpKlbSXKyz6SXC5bQ/GW5HAWPF9N/xtJ8R9NnN/QZA3QcUoGnlUqt2vOK5I8NljDsYWyawkGXkImSV6NaR5SenF+cLLYSJX9WpKV6zqSAxJ7J40XFFehH9B3aBb6o7xj0BnVn6fk2hmSfeWi8j18WtV7TD34SXKAWqLyFYHFMfYWSN44RQwfoD4bjIRD2pIVCYg4gIHSQ/KXYMIakTDgmXcDarZGJAz4PelaG4z8P/4BD0moMPjDjDAAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAXCAYAAAAV1F8QAAABYUlEQVR4Xu2Uu0oDQRSGjwQUMYWNnU9gRBBrWwUvWNmmEq3EwspC8gKWvoCVoCAiPoPYWFhoIxaiCQgGghcQVMz/MzPs2ZO9GMgWQj742Jnzz57M7IYV6fPfqMF3+Ou9iscdPEi0lvdtx+N8ws00jSm4K27NjMn+zJNEJ0vjEV5I9ppMFuAaPJf0Jif+mnfqTC79lc87qUkZbvox82OVdUVozufO8bjKyKe/zovLJ1TWFXU1ZqOqmm/BET/myZNOrBmAJVsk3OW6mrPRgZrrx5T3fsbgKfyxAQnvJ8BG/HeRhg7EZUemprmB03DDBsTuMOx6Fk6q+qKvV1TNYnvFeDbzF3E33Jk6vxhpjZYl2iCt6ZAv7V7cJ0VzKMkN897PqCTke7AFm/ANfqtsCa6q+YdEa1/hF9xReYD/zjNbLIJruGKLRdDx2Iqi8B+ag0Pw1ga9hifZh4M26DX8Dg7bImkDBSJZssDiK8QAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAYCAYAAADKx8xXAAAAyUlEQVR4XmNgGHkgEoi3EIlRACsQiwPxfygWA2IeIOYGYlEgNgfiR1A5rAAk8Q9dEAlg1WjCAJHoR5dAAlg1gtwPkhBAEmMB4nlI/E9IbDiA+Q8ZXAZieTQxDADTiI7xAjMGiKJOJDE9qBheUM4AUeSBJn4XiS0MxIxIfDD4zIBpOihuvZD4P5HYcEDIP6BEsA9dkI0Bouk0ugQSAMmDogYFTIBK+KFLAEEAA0QOxZmrgPgPAySJoUcBCIPEfwPxdyA2gOoZBTQBANYqOzBlHQPpAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAXCAYAAAD+4+QTAAABPElEQVR4XmNgGAWDHdQD8Rcg/g/FZ1GlMcBDBoRakL5iVGn8AKYRhHEBPSCuZYCoMUaTIwo8YUD4CBd4DMTHGPCrwQm8gDgFiLcw4DZgHZQm5Fuc4ASUBoUvNgN4gDgXygbJr0aSIxrADAaFM4gtgyQHAj+gtDsDRF4LSY5o8BSJDTIkDomfD8TcUDbIx9h8ShCAXJeGxAcZshCJjxw0FMcHDIAMAaUiEHiGLMEAkVuFJkYUQHcZzLW2QKyDJO4NFddGEiMavETjv2GAGHYbTRxUEqA7CATOAfEnIM4D4gVAHIMsyQjEdxkgxQQyWM6A3TBs8ZEKpUHioGR+A4j7YZI9QPwBiN8C8Wcg/gOTAAIfIA5F4n9lQKgFufg3EFciyYMAuuVUB6CUuQ1dkNoAlMfM0QWpDWgeVCMAAADOC1PQdFGg/QAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJ8AAAAaCAYAAACpZo6LAAAFQ0lEQVR4Xu2beahtcxTHF+8ZQigyRkT+MWSe+QehJPyBkogSIkQyv1dPkjGEkuGah0y9QjJlTIkMkblb5oyZZ9bHby133XX2ue+ee87Z555z96dWZ//W2vt39j37u/f+rfX7XZGG6XK02nNq/6jdp3a72r1qv5uvW/5WWy07GxoiVUL7NDtmwGOpjRgbGiYRxXekfR4afL2iSuQNc5woiqon3upS9rlfijh/MT8+P3Y72/7V2o9Yey+15W3b7U61pUObfSH219AHllXbNDsHDBf8HLVLbTsyL/l2Se24vY1MiA/elSI+J/cN0fd52B5avlT7XibupDz2WCHE3A622OnW7gc/yey8u+P5XB+2z1O7UFrPt534tpbJ4ntdliy+N9ROs+0TY2DYieLaJMVgN7Vrku9PKfsT6wc3SvVFGCRV58Orcku1RdIabye+bdV+C+3XpFp8NwffquY/K/hGAv6ole0z/4CAIBdmp7JRdvQQxF51LoOk6nx+sM+lpFVg7cR3g5Sb12n35ItPR8D/TvINPf7HXmXbr4YYIL4FyddvrpTqiz0IrpOJG7PKnA3VvlN7Vm2rFNte7TO1l6U8KYn9IeWp97Xat1ISFqCG+LbautZ2eO2ukXydsKTXNTdM7cQf6S9r7xB8iO/c0N5c7SQpTydPCtiHscwWUgbUDLiBP4i+dlLbw3wOPyZZ49XJD1fI7BHfTOnV+fN7wweTvJ1zipQMuooD1Z7KzjqIP9Jy1o4+hEWW5+yt9pKUfXY3365ql5nvZ7UjzM/sAD6SCJIU8O843No7W3sZa8Owi28fKefPjdgt9MPT0n/rbjhT7YHkO0jK03og5Iu8wHwfWhvxVQ10o/gcXiW5v9xGnIgxwhiI7NuZrvgOUbu1jd2iNqZ2k5RxFhkq/Q4b89VWys4u4Fo+aNsI7/kQq52qi8xgF/++UsTHHZOpEt/+5l/R2hRJn5gI/wdxMrk1gz1qfme64usnfP+wWKcgwBfUXsyBuqk6+VhZ70R8gJ+JeGCMQTnC2VhK/Da1PSvMmQ3iG2UYDpE5P5wDddPuIh8nJUZNqhPxMX7wPqv6dvFNxXTFh2Av6sDOL4fNaRCej/GOVVscYrUz1UWmBEC8E/HxyiW2UIqAM8TIqjPjYftamfq8GmbGUdKaXCBAHwPWir8GD8iBQJX4mHvFv1/yO8TaiYcxHjGmpBwy6LND+25pf3ydnKD2pJRziYVg5y4pMRKcWJ7qlnnS+7//MGmdQnWOkVJfrA2SCupsH6l9ovbj5PD/UDagRuQ8I2Vym+MonI6HmHOy2nvZGUC8ZNMu0tg/hdqPzb6Q0tcgWUtK6chXqUQult6LxHk6O7rkguxIkFw2zDIQX9WTaDP7zP6Ghp7h4ntTynIqZ9w+s/iodR4vZdqM4jswbGG/RWoPSXnTAAV3luM/LiXzJCEiGYvDFr6fbeqgrOljKX+3sx0NQwIXf759RqExToUsvlhAjzFqa75YwLNuEi8WJQD7+lSat531U5uiPOP1hhEH0TFGBQTA5D5z204WHzXSS9TeSrEz1O4IbSC+QdiOMxnx2HVSG4HvGNoNIwri80L55VIWdsZyRRQFCyjiPwBl8Y2FNiBiEqv3pSQvkXisVwgcFgE34psDsLRpldCe6gn1ipS5ZPAkZW1rU0pivjnSrsIAsd/1UpvjWJDRMMIwL/2N2T3mo8QEFGcpC30lpRhPARd4kjFvyizNmJT/0UB43g8JhnOqFFG5eYzFF/TLE45XLv2TwDDbxHf6GkBfutbQ0DEsJo2wRpKVOiPNvzYTsAeMODO0AAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAWCAYAAAB+F+RbAAACFUlEQVR4Xu2Xu0scURTGTxRBESRIOv8GsbCQlGIbrMR6QQsfKCoGLLQXFQQbGxurFCpYKBY2glioiA8ksXMhURQJBAWfJPF83jPumbN7d90Hiwvzg4+957t3Z+63d+7MLFFEUalnXbJ2lPdftdPx1nHvilYKh91U7XTYcf9M/S75QuGwuZL1Sg+zuq2pGGNds25ZHaYvG76yvrM2WBOUCHtHbtIVUoMH1hJrizXD+mXGVUo70Df3NZpnjbOWxX8BnY9iQD1BhwGTW1f1MbkJZAsu21NVd1Lyng3C4pyfpY1z9Ukb2B/FrqyusThJ+MLWUPLBALyP0i4j94v7hNUEN6wRaYMY+cP+JtcPtlkt0gaZwsbFQ9DacJfDF/aAkg8G4M1ZMwNPrFFVx1i7qtYhGlhHrD3W2usIhy8sLl9QzfrA6ld9IXxh4af6gs9PRxvrTNXTrH1V6xArqm3xhb2Xz/OgQ3khihEW4JKOk7tMh8gdA6uHmxG8PzIO+zU4hz6XHQcWWSesOqlXWVesC0pshRA4WK81yR/K5xeKv6ZuZ80aL2cwcX3HC/CF8vmFAqvSLO1ycqsZ3BDzBhPHhrb4Qvn8QtNE/r2bM5j4gDXJPS5ShYL3w5qlAiY/aE1ye8UXttGapcAncpOfsh0C+rpUPSleSbFA7haNd86f8om/XXiF1FSRC4e3nUNyzy48tCMiIiIi8uEZg2anUSzM8NAAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,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>

[image9]: <data:image/png;base64,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>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFoAAAAZCAYAAACxZDnAAAADh0lEQVR4Xu2YS6hOURTHFxFihKTkkRhISQYkIpGIAfIYIGUgj8hFBpQBBgYU8hggE89IHkWeAwbeA0LyiLzl/cr7sf93r/V966yzzz3nux/13ev8anXX+q+99nfOPvvsvc8lysnJycmpSyxwNsOKJdDc2TFnv51ddNYgmi6wytk3Z6+c9Tc5oYuz8+T7OmFypTDI2U3y/Ww3Oc1m8m0eOOtgcsJUZ0+d/XC2wuRS2Un+pvEjsJnRdGbaka9vxnErjhsWWnjeOVuu4s8Uv+iB5GuFnibOyjxnv1Q8ncL9oM1QFaPNMBWDvc6eqHibs9cqLolyBvqTs91Gu+Tsi4oHU/xGWwY0xPbNwmQ4Z7Q00E+3gKYf7DLWNCMDGuJGAc0+kEyUM9CoHW+0RawL8uZYoE1ivw3H+KuRJSkroyjc/itFdfg3VCxAb8/+ao4t0O5YMQu1HegB5GvtejuFdcxaAP97MV0A+lX2l3Bs2UphPYlTFG5/j+IDHdoDoK9lv6YJEtJTQVFtBnou+dpeRh/Heh+O4b8vpgtAx1oN9nNsWU9hPYm3FG5/neIDfVDFAvQjyg/1laSngqJZVszAUvK1PYw+mvWJHMMPbSD6gk8rX7OGvI5NNwtJg3CFijo2avj7iukC0G8rP9RXkp4KimZbMQPTyNfidKAZyzo2QQAfM80CXU4HOzi2rCOv2w0pCZwQQv1co6gOH2+RBfoZ5Yf6StJTQdEcK2ZA1ui+Rp/MusxC+NiMLNBl9iSt0VsorCeRtEbfpfhAH1WxAH0T+zg3h/oqa6Cx3pZKE/K1aaeOpAuDtpH9fhyXe+pYTOH2pZw6JrB/nGMLNH1OzwwKq6zIDHfW3YoK1MouLRxmXdhgYoCvR2iNlYZ4jIrBR4qv7wup5qUE/ciJR2uHVIxBttfU22htTSxAm2/FNFqTL1xpE1QcjNCPCXb2gtCAQdMP7ALFTyKYvXhdBfn9TkrDEgftg9Isz8gf5wQZMP1Q5YOpqdLQ52UVA8zcXSoeQfH7rZE9zl44e+TsIf99Tv7sqDng7L7RLPic/8l/cRGhZagj+dxJ8v9XeBxNF8DpAF+b+PRF+yHRdDUYRP1AQrwkfz/ydnWOpqtB38jhHt84OxtNF8CY3CK/SaJ9i2j674HZV2mUNKvqCpV2U9iE5WRQb8C6iXW8ksAyVe/oaoUK4J+tkTk5OTk5/wd/AHo8IeErZ8FmAAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEcAAAAZCAYAAABjNDOYAAACgElEQVR4Xu2Yy6tPURTHv0QxkYSUSDIxopSJgZRkYCAD/gAGHhEyExMTxYQYISMMSB5FHhmQPEpRXiUp5BEhr5CwvvY6t3XWXfv8NgaU/anVXeuz9l6/32/fc8/5dYFKpVL5u6yTWOalYYPEW4mPEotdr2GSxBWJ7xJnXe9XKJ2zG2nNQ4nxrtcwS+Iu0rp9rtfJAYkvSBsZy9vtPm5LnDH1TYmLpiYzkWY0THV1KaVzvknMMTXXzDU1WYu0rmEp4lk9yR3OMMQD6Ya72l95PPjLzvWiZM4m9H9P8wLHenLgNjvXk9zhXEf/FyV0vKzJaK3503JafSmlc5jzavbQj9N8vtaez4h9J7nDoY+GWb/R5Ja9iH2O0jnMo3sR/XbNz2nteYDYd/Inh3PE5JadiH2O0jnMj5m6gf6k5m+09txC7DvhhhVeouxwzpvcsg3Jj/WNDCVzBmp+uLUiQX/P5NGsG4h9J9yw0kvkX8T6/Sa37EDyg3wjQ+kc5rzKPPQXNH+itYdP2sh3wg2rvETZ4eTuFXsQ+xylc5ifMnUD/S7Nc/ec+4h9J9yw2kvhHeJhdHc0n6F1r6dML0rnMM89rRZpvl5rz28/rdZ4KSxEPIxumqsXmJq8l3jl3BKJUc5ZSubwYPx7mh441iMCd9y5TkYibdrqGwp7/HbZsEWdhb/dr6YegLRmgnFT1Pm9lpI5/MB0Q4zjFX7N1OQZ0qO7YQzSvsHGZTko8ULiscQj/fkc6RupZSjS0KtId/tPSG/aw94HiUNI62e32z/hDL5mFyVz6Ng7KvFa4lK73cdLpM90Amn9xHb738NeGRVH812k4niK+E+ygvz/XSqVSuW/5Ae4SfBgPUsISgAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAZCAYAAABQDyyRAAABFUlEQVR4Xu2SP0tCURjGTyaoEEkELuru92gJWp0C2/oYzX0Dib6FDk6O6iBBUwlihEJDS+UQCgX1vJwr3PNw//8ZhPODH3Kf5+B9z6tKWSz58QU78ARWYRt+Gidy5s/DhnEiIRcc+CAvvIVdeEZdIu7hD2xx4YMMkAlDuIY1LkJINUARPsMlrFAXFRlgDp/gBP4q/b2BHMN3+AAL1MVFBii5ngdO5kkdfsM+Fxki/x0Z4IYLQUpZ0R0XKTikZ9moDDCj3GC3iR4XMVko/bKyKztyspEr80UOv8EpPKAuCiulL+LmXOkBLikPRNb4CF+VeZswmvCFsi3cUBYL+Vk+4CkXPlwpfWPZpHyOzTo51xxYLJa95h9ItzcL5Hvk5wAAAABJRU5ErkJggg==>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALUAAAAZCAYAAAB3jW88AAAFcUlEQVR4Xu2aZ4glRRRGrzmyKibMETGxZgwYFvGPigoKCoogGFAUEwYElTWAiAGziOKuCXVFUVQU/bGKCAbMGQXBjDmhYr5nqmre7fuquvvN7ujubB34mK6vqlO96uq6t0ekUqlUKpVKpVKpLMicp/pR9YvqaFfXh/1U93rTcJfqH9Wvqotd3VTnPgn3/rZqeVfXxiGq3yTs+4hq8Wb1GK+o9lAtrVpXda7q+0aLRRQ6+0lTflP1rCmXOEv1k4ROR3Oa1eNQt1rc3iaW/xpUT1mWknCv68fyErG81niLMvdIc3LhN2Jf+1AsGT2r3039Iss0CZ3hwVvZmy2UBvXZqlelOcucKaH9lcabijyj+sR5l0u+vz1pkCbSZPC58eA91fWqS1Vru7qFji1U63kzw2LecDDgcp2Md4s3WygN6uck1F3nfP+jTUW4vxuct1v0u/hD9bcp7yxhv5eMB0+78kLJhhJujhtm/cv2cbaBYTnVjt50lAZXyS9RGtS8Lu+X5ky9jHQf/wjVBaq7Y5kH+ArVkeMtwpKG2R6fV7HnFNUHEs6/reqqZvWkkpYarHEtG0T/YOd38YSE/dZ0/qiDmknuGNVlqmujt6vqTtXuqZGEdTpxkL/+BP3+qeoa1b4S7mvC2Kc3MVfCk02gYCEo66I0uEp+idKgznGOhPYn+goDgWu6Btb7G0f/Swn3eonq+OgxqGln30rfqbY25eelPZCd3/AQcU2nO3/16LMs68sJEvY53FcoL6v+VD0qoW8+bFYPQUDJgOR4LF2+kTDhLBs9AtIvZDBIv42+JVdm5TBheCpyrCoh+EoDAdknr0Rq6yn5JWhLlN8H2tJZXTB70HZL420XvduNB3gnu7LPNPyXg3pvGb4mWCX6Nzu/BAOQgfazanNXB2RHLBy7T/Yj9/s+FL1Njccsbttt5cpwmszjoO5D7lVcIndzUPJL0JbXfBfvq772ZoHZMnwNdB7eGs7Hm+nKaK5qf+O3wVKtr7rYTML5T3U+Syb8i5zfxT4S9iPIboOsCe1W8BWO3O/LQ++9NIlY0r63qaa7uglDpJsO3DU77ukNR+7moOSXoO0D3nSwRnvLmy0QqPprYBbB87Mw3oWmTDqNpVq6D8RAa+PAEdQFSyHOyVLLQmyAT8wwKn1+k5kS2hzmfE/uWOnNaGEJh2djoh2ilzTP6VmyCfYpv0nCgXOBB+s21lBtpDyzB+8db7ZA+we9aeA1TLBjyZ3Xwivat9kkel2DeprZTukwf6zJhvOVsh9tueqVJLQ51vnpHlLskLunlDJkZm8jt+8dGY+lH14a1Jzbxi5HSah/yngjw0XneEPCwc9QHSThA8q7jRZ5DpXhGwE8nsgEgURbYEd71mQ5eFvQYZ6uWXu2DF9b20xtH3a/H8sV7002zGCvO48PVv46dlJtb8pkJWhDdsviByLbfFG0pBRqF/5YkJup0xqabA7spXp8UD3G1dIvKVGkbeZldpol4esTaZu+cNEpkwCke/zNpU6wQVuCa6Iu9xVyHRns60UGo42HZfg60ky3kfPxbnTlA0x5F+kXnM5PCNT99VMmDeY9225FVwa+LuKdbzwGv82uEEvRZpbxSvhzQkobWlLAm1KJM2LZrtkfk9FjhEmHfDYX+oLqNQkRtf9ow+z/ovNOkhD0ka/8WMLXM9JB9qklMEwd6EVkXYIInuNxXI5Jp3Fdn0WPv8xkLFGoT+f/gZ2Vj2TwKk739n+QZmaCMD5h39qsHoMvgsgyXcJ+pC/pT7Zzb0oGFHX83w5/yc23wcT3lYT+QmzzMPj+Jj/NedNvS3+TJp0hYTJinKS+7ZqcKpVKpVKpVCqVSqVSqVQqlUqlUlkg+Rfkk6Y6eSevZQAAAABJRU5ErkJggg==>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALUAAAAZCAYAAAB3jW88AAAFZElEQVR4Xu2aV4glRRSGjxHjIsYXwxoQDJgVFcMqKmbBB30QQVBEUAwoBlAY9UHEgAEVE44JE4quOTGKignFhBkUE645gIr5fFt19p4+t7rvvY7O7jr1wc/0+au6uru6uvp03RGpVCqVSqVSqVQqCzJnqH5Q/aQ6PJR1sbjqNdVfqjmqdZrFc/lVdbxqNdXSqt1UH/oK04C9VbdFs4N7VJer1lUtotpU9ZBqM18pc42k/v9ItWYom7a8qXrUxW+onnFxF79J6nTje9URLgY6PGqXRo3/JyerfpTeNd/eLO7kaenvs5sbNRJ/qvZwMfX2dPG0ZIakjojgrRDNwGzVBtGU/vaIxyTNKAc3i6YNow7qCdUJqhtVJ4Yy42zp7+t9C95CA4NpjWgW8LNoiVek3Al4DMIuqHNr8DhebC/G05FRB/VjMvje0SZv2Qj+MGNjgWGmpJPmtUP+y/aRvoKD/HWraAbYvzTo2nzPI5LqvO+8lyXl555B7ZQ4RHWm6pYcc5MuUB06r4bIyqoLs09uHzlO0rndKSkXvahZPKWMOqhJB4cZ1Az+CP4l0czQJunheapLs7ed6ibVDlZJ2VFSunO68zz0+6eSjrOXaq1m8WgwmCMTknLb1YP/c4hLtA3eNj9i9dA7ktKMCGXcJDrhgRzz0dgFD4a1y772AfqFpGs9R3VU9hjU1POD4FvVxi5+Xkb7UPu34fxGGdQPS3oo+cgel7S/Xa+BRwoYwX8wmpklJQ1Iu19fqxZVLZW9+1SfS2+QfpN9TykupaFDw1NRYiXVH9IbCMg/eW1Y3UibH7HOMNEJEXzrJOADapi2mT2ot6HzNs/eDc4DvGNDvIyLYX4P6jui2QGDdczF1s+sHAEDkfiueTV64L8XzUDp/rLigree85jFfb2NQgzk/pMa1MNQehW3Ubo4aPM9a0uqwww5M28jlgYHQb3HoxkYl/5zoPPwVg0+3liI0YRqH+d3Qao2rEaFcyENmgzxnrB9t4sN/KeiGYhtAQ999GwS8di+16s2CWX/mHOl1/Cgp3+naARKFwdtvody8lrPk9lfxXlLuG1jmPZt/dXDLIIXZ2G8s1zMMUnV7DhofVdeYv8RNCocvzSrtjFMn7FNmhLBvzqagdgW2JvRQwqHx5vB2DJ7JjKESfGcpKUc40pJDR/oPOMUSTlUF7aOGsF7K5oOBm1pP8A/NW9fm+Ote8VzwSM37oIbE4/BjxF4gwb1DLfNDxd2A+YXHLs0q5bgBxTq3x/8eA1st61+DFo6jW0By4fRI/XDs0HNW9l/uxwmqfwJ543M+dHIvC6p8ZNUB0j6AeXtRo0yB0n/hQAeT6RBTne0i6G0H+DbRyu5L0+y74jlJdW5ynklxqX/GF0ztX/Y436kK9GbSjg2OWsJHvgtXMxHMfV3dx7g/e5iBnS8pm0KXgnqxHqlmdpy6MVyvLOkXzY9F8twixKtdM28zE7XSbpYlm2GhZP2X9Ys98SLs07wH23kzizreXg1M/sbPOHxgj+Q/vZL3Cv99bbPHvm8B++KEO/n4m2l/BE7FXDPOJ+2X2mtb6PnX/mnZY/JxVix4NH3L7m4jdIxbYnWs2v2bLVqVo6XtQqSVlr8hLJAwHo2J/qC6lXVL9K/Rsrs/2Lw4F1J+7I8ZG1E+LCibE7++3GzuMh3qk8k1WWJiU7jvD7LHn9ZpydFoRyP+vxMD/wfBG81u3ml8/qvOUb1laSlTDs/zjU+5JdleRjQLOeRotk1LNeokWA1hDLeAixjPtss7oOJ70tJ54PYZmEh9jfr05ynnTv9TfuzJC2nMk7svIgrlUqlUqlUKpVKpVKpVCqVSqVSWej4G9cPpXERNFqsAAAAAElFTkSuQmCC>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALUAAAAZCAYAAAB3jW88AAAFFElEQVR4Xu2aV6gsRRCGy4jxCirqgzliwKyoGC4iYhYUURBBVAwoiij6oILhQcWAERFFrwmzmDDDFURM+CAGTJgT5gDmVJ/ddba2tmd21uWu5x77g5+z9XdP6qnp7uk5IpVKpVKpVCqVSmW6s7Dq12h2ZA/V7dF0HKb6VPW76rxQNpNZVfWe6i/Vy6pZfaXtrKf6QdK2L6oW6i+e4lpJdT6QdLyK8rqkRjF15RTpNTq6o794irtUn7j4ZtXXLp6p7K96xsXvSmqnfZ3XBMnpt11a0rbLOA/+VO3qYurs5uL/Pd/LaEntaUtqyhgFojfTG59rPKDgdWnjUp3jVG+4+BwZrLdXwZtvWF+1SjQLLBCNFuZFUl8i5X3ivR3NGUYpgb/IHvevDepsFrwTJE1lDOq85mIDv0tuTBtWl3TSDDs/5t9H+gqOxVVbRrOFeZHUzNFL+yzdcM/BqrNUt+aYm3SR6pCpGiLLqy7OfhwJgCTgwblbtamkB2ySHKM6KHi/SLruYXNra58rgue3I37CxQb+ZdHM0MkdobpAdXn2tpU0JdzeKik7qG5Rne48D+3+saTj7K5arb94NEjmyFzVb6qVg/9TiIcxL5K6KXmbfOMM6dV5XLVm9j+XdK3nqo7OHklNPT8qfaPayMXPSfuL7KQYdt3GitKri/5QrdNXI/n3Bw/wH45mZlFJCUkdpjJfqRZULZa9B1WfSS9JefeJ51uKh408rfBUlFhO0oX7hvBPXhfGTeo7oym9c4k0+R56D+ps4DyGZLwbnQd4x4d4CRfDf53UV0o6L1Y1ukAP6u/nfa6MRMS7x3kG/lvRDJTan/3jre08OwdjwxDDiTJmUnehNBR3YdykZpiPlBoPmnzPHBmsQ+PhrRB8vDNDjOaq9nR+G0zVumpU6HQ4n61jQQMM++/n30dJ73qum6qR4ntdbOA/Fc1Aqf156KNnnYjHtr1BtXEo+9ecL70dl3pHz47RaGHcpC71GqxLl/ZZatSIrb966EXwYi+Md7aLF5E0VbPjoHVdeYl9RtAoMC3i+F1f3liPjtcN9g5l8PtRFxv410QzUGp/Gxk9TOHwGBmMLbJnYoYwFs9KWsoxrpa04/2cZ5wqaQ7VlXGTutRrMB8u7ROv9H7g4cbEbdfK3rCknuV+byLlmzgpOO6SLj5c0nU0wTTlw2hm/DXwu2n148BoBkrtcVPBY+qHZ0nNA+rfXQ6VVP6k80bmwmhk+FrFzk+WtLj/iqSPKqPQltS8SBwbTQfb+TmfsZKU94l3UjQDc2Rw27ae2j/scTumK9GbBD/L4HTw1RBvpdrcxcxRm87V+yR0rMf0JnolqBPrlXpqm0Pb18ydVI/0iv/hUhl9UaKPtp6X3ul6SRfLss2oxOHNY43gX9oMzomyp2NBhh75Nhczx206jucBGay3XfbWCD7eVSHe28XbyOS/YvLZ2totytPk+S+F8JD0X+OykurR4Rh84eWT+jBKx3ys4O2cPVZjYHaO/cjDSovvUKYFNAT/l8GQh1h/JAH8EEnv/4KLgS9cX0qqz3YfSVoOKj21rFe/KekFhkZZqr94gG8l7Y/9sk8ajV6Pz+14/OUhZIpCuR3/OzaWlFCManbzns/+JImJ7OVhuoE8JKqtZr2T/57WVyOxi6QyRkmWMf2n9RJ0fHwAsnvNb0aS2N68qHIf7d7S3ux/tqTl1Jekdy3ElUqlUqlUKpVKpVKpVCqVSqVSqcx3/A2hGKGbnrkELgAAAABJRU5ErkJggg==>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAZCAYAAABzVH1EAAACUElEQVR4Xu2WT0hVQRTGT5lEuKts48KIwiiIcBNSZGKblkm5sWgXuLOgRX9IsAI3LZRKWoQEkQgtchMUtWmlFkRt24TQ0qjQ/phW5+ucmXvucZ5ec/Xk/uDjzfnOmbnz5s3MfUQlJSVFOMcaZe3ReDfrAasnVhSnjvWM9Yf1irUun47cZM2xplmHXC6wkzVBMtZzl0tynaTY6k2uohgNJH03abxF4/WxQvhC8szAd1a/iUErSd/Afhcn6WUNsu6zrrBq8unCzJL8spbXrB8mbqfFE9qc8BB3Ow+/4LjzcmDybd78D/DwTuddUj+AyfhJA3intL1NY3xawpatyGVa/Rc5TPIQv9/PqI9VB2j/ytIR+O+0fVVjzzCl/chF1g2SolB8N1exPLgY0K/Z+SfVP6Ax2l+zdAQ+zgp4rLHnNqX9yHnWU+ehwzXnLUUfSZ99zj+ufpfGaH/K0hH4YZIvTdsyQOLjUimMHbgIZ0nqcbtYTqiPQw7Q/pylI/B/a/uhxp5bJP4Gnwik7voFSg9WiXBGWpx/Wv2wimj/zNIR+O+1XemM3KO0H0ESLybvLdnJsZGkfrlbq9K48Ia0fVDjFd9aSF5IeL7TMdZe51lQj/eR5Yn6gTsuBtgR8GqNh7jDxGCG0ucr8o1Vb+IjJAM1GS88zE/C4lcfpCYEzy7IJC2+ybD68yYOz99uvCTYWmGi0I58+h9jrA/edIyQnC98YpzU/7VGktwL1hTrYz4deUvyb+ERSf3RfHp1YPXWBH7rVCXYt1u9WY3s8kZJSUl18Be3lqVxYDINfQAAAABJRU5ErkJggg==>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALUAAAAZCAYAAAB3jW88AAAFcklEQVR4Xu2aV6geRRTHj73ig12wxELAKHbFniBB7II+5CHEBBUVBEUU9EEh6oOKBQsiomJsqFiwYiyQxDxoNIoN+4u9YceC/fyYOfc7e77Z7+79Qq65l/nBn7vz39n9dmfPzJydvSKVSqVSqVQqlUplovCT6sRoFthT9ZxqL9Xqqh1U16oe8ZUyJ6u+UP2lujzsm8ysqXpD9a/qK0lt1JVTVL9IOnZh2Oe5VVKdj1Xbhn0V5XRJDdQlqGdKquv1daNG4kHV5658t+o7V57M/KlazZV/VJ3qym28opqbt9eQXvuuM1Ij8Y/qcFemzhGuXFG+ke5BPV31pKSR4hLVhs3dI3A+RqzoTfbGf0y1czQl3fsgmPXoDH7U3UDScX8479LseY4peBMGGmubaBbwo8Ro/JD/dg3qg1UXRzNAOlJqZLwPoznJ4B7vCx7Po9QeHjq7jcye6LH9tisb+F1iY5VhiqSLZtr5NW+f5is41lPtE80WTlLNy9tdg/ogGT2oGVniw4H4gCKzJZ373lzmIV2tmjNSQ2RT1TXZjzMBnC2p4zyk2kNSBxtPnpH+zvuq6iJXbuM21fbBi23GNu80Efzro5mhU5H+XKm6IXsHSEoJGaSMQ1T3qC50nod2/0zS7xyp2q65e2wQzJFFkqarrYP/WygPgpdDo2tQ0xjcOPUJPjrZ840a/Q/CaPMNHrzVeVZ6L1jk7NzrZaozskdQU8/PSt+rdnXlZar7XXm8sHtA76nmN/Z2Z31J5/jEeZRJcSL4T0Uzs7akgLTr+VZSurNu9p5QfSm9IOXdJz6nUrmUZnWGXlFiE9Xf0mxE3/MGwVu5DwiO7RLUrHp8FDyOXRrKsRGgzfcwelBnmvNYccG703mAd1YoEwie/yOoLVhMw74g26xsEIiUH3aegf9BNAOl9n80ezs5j4HL19sllOEcWcGg7kJpKm7jKGkGA3DRXYK6BL3c33Sp8aDN9yyQ/jo0Ht7mwcebH8pokepo5w+CVK2rukD6wDUwYEzJ28jPil0gjeI4VkE8eKXlU3w/sJQotT+dPno2iHjs2DtUu4V9Q3OF9E78QNgXOTQagVKKwnmHDerFko7fIpdZl46NAqVGjdj6q4dRBC+OwniswBhrSUrV7HfQVLe/xHFjUBf4TfJ+z5Lsbxb8NvaWcsoJnOfpaEryb4lmoNT+NjN6SOHwmBkMrsm3KxnCCvGipKUc42ZJJz7Becb5knKoQdCjvZZLOt87uTyIUsPY8Uy7QD4c6wBe28MyeDDx2B2zN1pQb+S2d5fyta5MCNq238O/IJoF6BBx0Ik5ddvqx6xoBkrtcVfBI/XDs6Bm1vGp6jxJ+xc7b8xcFY3Mm5JOfp7qeNVbqncbNbrBaMZ54khNkJ4ZPOrFmSKudmwZygbeudEMLJD+YweN1L6zx+NIV6K3smn7PXz/Ur+vpPcTD6kGL7sRf04COv7GfgWvBHVivdJIbTm0pT7Tpf/r5nXS3/nGxKCRl9Hpdkk32+WrVQmW6biJuExojeBf2l6TVN/YSlKduc4DRmS/XkuOGxuvxOPSX+/A7JWWu24K5WNdeX8Z/iVtWMidWdbzkLr8HLxSgJkX5We3jbNnsyJwbr5GjkbpN20J0nNY9iydnJHLfAwyWGnxA8oqBSMDa49McZ/mssHo/7IrGzZa2Ag9s7l7BPa/LymloV7b10eDD0FcA9fCyyeN9rukz+14/GVFgBSF/XbNfIYG/g+CWc0e3kvZH2+4Z36f5bO267gxy2CN3geyV8yhaW98Vi54Xi80d/fBwMdXY9oLsc3CQmxv1qcZfS0eaG/OP0PScurr0rsmypVKpVKpVCqVSqVSqVQqlUqlUqlMOP4DyTyuLwxO4IEAAAAASUVORK5CYII=>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD0AAAAZCAYAAACCXybJAAACjklEQVR4Xu2WS8hOQRjHH7f4FiRiIx9JERulbChEsrCyYGNnw8qlJOGzQClZkEtCUlJKwkZuG5JLySWxsFOW7p/79fm/zwzP/M/M8Uqfxdv51b93/v95zpyZ98w5jUhDQ0MnskZ1UjUl+Mmq46rVvyp+s1n1RvVetZz6/oZdqs+q56pZ1BeZqLql+qG6TH2ew2I1T1Xd1Fdkm9hFXneTCuOR6pLzD1XXnW+X12L3jHxQ7XAezBabR2Qa+ch31QLnUbPQ+SJbVHtUx1SbVAPS7hbDJH9TZMM5rGGeVMcZkcngV1KGnXHT+a1SvW5RJsuChc7lkLgn+cGQYXu1CyZeGmdZaI8OHr+eiyGPoI3dxyAfyyGzUf68aAxUmmwuL4HaLxyK5Q9Cuyd45qhUF51715Fj59ayQbVdrDgOfDCpKC+ulJdALT6EDHK82+BM8Mw+qS76nPMR5Oc5ZNaqLlCGC/HOeJ+bSCkvgdoXHEo6zlXX9uwWy8eo+of26aTCQP6Ew3bgxbCPlPISqH3FoViOLzE4ETyzVywfGDza2BUM8mscMv04UL5J3y36E4dieXw6pXf6iFTnxDsUID/EIYMiHBI48zd4Sz6C7DGHNfC4EWQHQntm8P/y9V7KIYOidZnM32AJ+Qiy6c53qVY5z+yX6jjYacgGuQx+sfOgV9LvARbMY83IZFlwpBzl/ByxCye5DCBb4fzOkHnin4Wbl0D/VOdvS/WLjqf61fn4x4x3WTzUDHEZduQd52vB9o4Thiak3S3wFNGHSd5XfZTq9wBP55nY6a7EOLFxroidl1GfA/d4pzolVj8/7W6BDH1nVS9VN9Lu/8dQ1XoOO526p9yRjJT80bCjGcxBQ0NDQ1/yEz5n0u5kVWxbAAAAAElFTkSuQmCC>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALUAAAAZCAYAAAB3jW88AAAFVUlEQVR4Xu2aZ4hkRRDHyxzxgxnMAcWsKKJiOERFMYFf/CCiiIgoKqIiisIZwCwmFFFwTagYMGKEVRQMICgGTHiHGXPAgLl+dNdNTU2/MKt3t7fXPyh2+t/13vR0V/frrrcilUqlUqlUKpVKZbqztNrvUcw8pHa92iZqS6htp/aE2vbeqYVj1D5X+1Pt4lA3k1lDbY7aP2rvqW02XD2POyX5/Kp2Yajr4mZJ136ktn6oW2x5R1KnmJV4QYZ9MAaiD/epfebKd6h968ozlR3UJl35WEn9dpLTAG31/JnFgvJfg+pW/lbbz5W5dn9XXuz5UZqDmsE5Ve12tdNCXRfck6dA1GZ65/8m6Xeu4LS4cJyp9prakk47Q5LPlU4rcYGMjtdBBW2RYQu19aJYgK1CX9qC+hkZ717GVVK+J9oHUZxh3C2jvz0G9Uu5fJ3TIPqVoP7tKErS+8TGtGFDSY3msfNL/nycd3CwQuwUxRbagvppmVpQs0cv3bNr0I5QO0/trlxmkK5QO3KeR3pks5qhxycBnCJp4twvae/PBFuY7CbpN1/qtBUltc+v1MtJd/8A9Sw2EfRrophhDNkGXaZ2bdZ2lbQl3N2clD0kbS/PcZqHfv9U0vccoLbBcPV4EMyRSbU/1NYNOoeOcWgL6iclBQlBOiHJ73jv0EDT4DTpxrky8GFCbZz1LyX91otk8P0ENX5+0n2ntrUrv6x2jysvaHaW1MbnYkWBsyT5nhgrAvg8HEVJ+uNRzCwrKSDxeVftG0kTavmsPar2hQyClLNPHKdSmZ3DlGFWlFhN0uHCAgHzM68PbUFN5812ZeuEfZxWwtoSadI9rB74bOk0Dl9otzkN0E4OZVZBz8IKalZFziK06ahQVwK/roM0gYjfA7FCkv5+FAOl/ifDhbap01jFvd9WoQyctf5TUPeh9CjuQ1tQlyh1TKTJp0n3TMioD52HtmbQ0WaHMjapdqDT22Cr1temwjKS2jQ36B6C8esoNsC9HoyiJP35KAZK/c+kj5otIh679la1bUPdlLlEBje+N9RF9oxCC21BzYBESh0TIS9d8ulzreVfPawiaHEVRjvflWkvWzX7HqwpR2wcMoZNFWvL5rFC0h72rSi2wH3YFkbQb4pioNT/9mT0sIVD83v+HbNm1jf92AinZVI5xo2SbnyY0wzSReyh+tIU1CT00R8LeqljIuyHSz5opfOBh4GJ1/LyB60rqFdxny33G+81v/lZ7ZWg2SSPBzC2Tk8Frau91DdlPw6PYqDUH7ZF8rD1Q7Og5tzizy5HS6p/1mljc3kUMm9IuvnpaoeqvSnppco4NAU1hzT0fYOOxiB5eLHgJ9LaUr4nWle+e0JGr21bqf1kj9exXYna/IQzTilwTPN7UJ6mBFQkrtpnhzIBHe9vB9IuSm0rrdS2h14ql/eS9CbZc7WMn5QYom3lZXW6RdKPJW0zLpYiLIHuH0F2QufAaJA2K3UWKzI5W4M9bvQp8YiM+llabKOgo90Qyge78i7Sffj6v4ntZHzQ5jhtnayVjAyPQTYH7QSnrZo1PwY/qb3qyk3Yd3h4UkRt76ytlcuzcnklc5CUafELyrSAjuD/Mj7ORv6RAOBRbxDQpPNIp1mHrOzqDR63vNWKcC3/+8ABpulaz/dqn0hqDykmOo03dLxuR+Mvk5AtCvVo+P/AxZL+D4KnmrU1bgMWBKxurGB8/9z8N6baOBhaG6OReTC2UfvQlQ2yT/iSuSDwXxyuHoGJ9ZUMxprPJBZif7M9ou3EgvU3958labK9LoN2+slXqVQqlUqlUqlUKpVKpVKpVCqVyiLDv2SsqwK24ww2AAAAAElFTkSuQmCC>