# **Arquitectura de Ejecución y Gestión de Riesgo Programática en MetaTrader 5**

## **El Modelo de Trading de MetaTrader 5: Órdenes, Transacciones y Posiciones**

El desarrollo de sistemas de trading algorítmico de grado institucional en la plataforma MetaTrader 5 exige un dominio absoluto de su modelo de ejecución asíncrono y estructurado en tres niveles independientes.1 A diferencia de la arquitectura heredada de MetaTrader 4, donde una orden y una posición eran tratadas de forma equivalente, MetaTrader 5 introduce una separación estricta entre la intención comercial, el registro de la ejecución física y el estado neto consolidado del inventario financiero.1

MqlTradeRequest ──\> Orden (Intención) ──\> Transacción/Deal (Ejecución) ──\> Posición (Inventario Neto)

La secuencia operativa se inicia cuando un programa MQL5 o un script de Python transmite una estructura MqlTradeRequest utilizando la función OrderSend().1 Esta solicitud es procesada y verificada por el servidor del broker, registrándose en el sistema como una **Orden**.1 Una orden representa exclusivamente una instrucción formal o una reserva de precio.1 Las órdenes pendientes (como límites ostops) no afectan el balance de la cuenta ni representan un compromiso financiero activo en el mercado.1 Para consultar las órdenes pendientes activas se utiliza la función OrdersTotal(), mientras que las órdenes históricas ya ejecutadas o canceladas deben ser extraídas del historial del servidor mediante HistorySelect() y HistoryOrderGetTicket().4  
Cuando las condiciones de liquidez del mercado permiten el emparejamiento de una orden, esta se ejecuta y genera una o varias **Transacciones (Deals)**.1 El deal constituye el registro histórico inmutable de la ejecución física de la orden, detallando el volumen específico y el precio transaccionado.1 Es de vital importancia comprender que una sola orden puede fragmentarse en múltiples deals si la liquidez en el libro de órdenes del broker es insuficiente para cubrir el lote solicitado en un único bloque de contrapartida.1  
La acumulación contable de estos deales da origen a la **Posición**.1 La posición representa el inventario financiero neto y activo de un instrumento específico en la cuenta.1 Mientras que el historial de órdenes y deales crece de manera indefinida con cada operación, la posición es un estado dinámico único por instrumento en cuentas netting, o un conjunto de posiciones con identificadores individuales en cuentas hedging.1 Un ticket de posición se asigna en el momento de su apertura inicial y normalmente coincide con el ticket de la orden que la originó, a menos que operaciones especiales del servidor (como la reapertura de posiciones durante el cobro de swaps) modifiquen este identificador.6 Para realizar un seguimiento retrospectivo preciso de la vida de una operación, el sistema debe utilizar el identificador único de posición (POSITION\_IDENTIFIER), el cual asocia de forma inmutable todos los deales y órdenes que afectaron a dicha posición a lo largo del tiempo.3

| Concepto Comercial | Naturaleza de la Entidad | Ciclo de Vida | Funciones de Acceso Clave |
| :---- | :---- | :---- | :---- |
| **Orden** 1 | Instrucción o solicitud formal enviada al broker para comprar o vender.1 | Temporal hasta su cancelación, expiración o ejecución total.1 | OrderGetInteger(), HistoryOrderGetTicket().4 |
| **Transacción (Deal)** 1 | Registro histórico de la ejecución física parcial o total de una orden.1 | Permanente e inmutable en la base de datos de la cuenta.1 | HistoryDealGetInteger(), HistoryDealGetDouble(). |
| **Posición** 1 | Estado del inventario financiero consolidado para un símbolo específico.1 | Activa en tiempo real; se modifica con deales subsecuentes.1 | PositionGetInteger(), PositionGetDouble(), positions\_get().6 |

### **Tipos de Órdenes y Mecanismos de Ejecución**

MetaTrader 5 admite ocho tipos de órdenes que permiten estructurar la entrada al mercado bajo diversos escenarios de precio 1:

* ORDER\_TYPE\_BUY / ORDER\_TYPE\_SELL: Órdenes de mercado de ejecución inmediata al precio bid/ask disponible en el libro de órdenes.3  
* ORDER\_TYPE\_BUY\_LIMIT / ORDER\_TYPE\_SELL\_LIMIT: Órdenes pendientes colocadas por debajo (compra) o por encima (venta) del precio actual, garantizando la ejecución al precio límite o mejor.  
* ORDER\_TYPE\_BUY\_STOP / ORDER\_TYPE\_SELL\_STOP: Órdenes pendientes de momentum que se activan cuando el precio cruza un umbral específico, transformándose en órdenes de mercado.7  
* ORDER\_TYPE\_BUY\_STOP\_LIMIT / ORDER\_TYPE\_SELL\_STOP\_LIMIT: Híbridos diseñados para mitigar el deslizamiento de precios (slippage). Cuando el precio alcanza el nivel de stop, se genera de manera automática una orden de tipo límite al nivel de precio preestablecido, evitando ejecuciones desfavorables en entornos de alta volatilidad.

### **Políticas de Ejecución de Volumen (Fill Policies)**

Las políticas de ejecución especifican las instrucciones de llenado de volumen cuando la contrapartida disponible en el libro de órdenes no coincide exactamente con el lote solicitado.9 Estas reglas se configuran en el campo type\_filling de la estructura MqlTradeRequest 9:

* ORDER\_FILLING\_FOK (Fill or Kill): Exige la ejecución inmediata y absoluta de todo el volumen solicitado.9 Si el mercado no dispone de la liquidez necesaria para cubrir la totalidad del lote al precio actual, la orden es rechazada y cancelada de inmediato por el servidor.9  
* ORDER\_FILLING\_IOC (Immediate or Cancel): Permite la ejecución parcial de la orden.9 El volumen disponible en el mercado se ejecuta al precio especificado y la fracción restante que no pudo ser emparejada se cancela de forma automática.9  
* ORDER\_FILLING\_RETURN: Utilizado principalmente en mercados centralizados de futuros y acciones, así como en órdenes pendientes.10 En caso de ejecución parcial, el volumen remanente permanece activo en el servidor como una orden vigente esperando contrapartida.9

La asignación correcta del tipo de llenado se realiza dinámicamente mediante la consulta de la propiedad SYMBOL\_FILLING\_MODE.9 Si un broker permite simultáneamente políticas FOK e IOC, la función estándar de la biblioteca de trading SetTypeFillingBySymbol establecerá por defecto el valor ORDER\_FILLING\_FOK para la orden correspondiente.12

### **Modos de Ejecución del Broker**

La plataforma interactúa diferencialmente con los servidores de ejecución dependiendo de la naturaleza del instrumento financiero y el modelo de negocio del broker, lo cual se recupera mediante el identificador SYMBOL\_TRADE\_EXEMODE 9:

1. **Ejecución Instantánea** (SYMBOL\_TRADE\_EXECUTION\_INSTANT): El terminal del cliente inserta el precio cotizado actual en la orden.9 Si el broker acepta dicho precio, la transacción se ejecuta.9 En caso contrario, el servidor devuelve un requote con los nuevos precios de compra y venta disponibles.9  
2. **Ejecución de Mercado** (SYMBOL\_TRADE\_EXECUTION\_MARKET): El terminal transmite la orden sin fijar un precio de referencia.9 El broker la ejecuta al precio vigente en sus servidores en el instante de la recepción, trasladando todo el riesgo de deslizamiento al algoritmo.9 En este modo de ejecución, la política ORDER\_FILLING\_RETURN está prohibida.10  
3. **Ejecución de Intercambio** (SYMBOL\_TRADE\_EXECUTION\_EXCHANGE): Diseñada para operar en bolsas organizadas de valores y futuros.9 Las operaciones se emparejan directamente contra el libro de órdenes central (Depth of Market) a los precios de compra y venta actuales de los creadores de mercado o contrapartidas directas.9  
4. **Ejecución bajo Solicitud** (SYMBOL\_TRADE\_EXECUTION\_REQUEST): El terminal debe solicitar previamente una cotización firme al servidor del broker antes de enviar la orden.9 La transacción se confirma únicamente si se transmite dentro de un intervalo temporal estricto tras la recepción de la cotización.9

| Modo de Ejecución | FOK Permitido | IOC Permitido | Return Permitido | Comportamiento del Precio ante Fluctuaciones |
| :---- | :---- | :---- | :---- | :---- |
| **Instant** 9 | Sí 10 | Sí 10 | Sí 10 | Genera requote si la desviación excede el límite.9 |
| **Market** 10 | Según Símbolo 10 | Según Símbolo 10 | No 10 | Ejecución garantizada al precio corriente del servidor.9 |
| **Exchange** 10 | Según Símbolo 10 | Según Símbolo 10 | Sí 10 | Emparejamiento directo contra el libro de órdenes.9 |
| **Request** 9 | Sí 10 | Sí 10 | Sí 10 | Requiere cotización firme antes de la transmisión.9 |

## **Implementación de Stop Loss y Take Profit**

La salida del mercado determina la esperanza matemática final de un sistema de trading algorítmico.14 Los niveles fijos de Stop Loss (SL) y Take Profit (TP) proveen una estructura de riesgo estática, pero carecen de la capacidad de adaptación ante los cambios en la volatilidad del mercado.14

### **Dynamic SL/TP, Cierre Parcial y Break-Even Automático**

El ajuste dinámico de stops requiere una infraestructura de código reactiva que evalúe de manera constante los datos del flujo de precios (tick stream).16 El break-even automático protege el capital de trabajo al mover el nivel de Stop Loss al precio de apertura de la posición (más un diferencial o offset para cubrir costos de transacción y comisiones) una vez que el precio de mercado ha avanzado una distancia favorable predeterminada.19  
Por su parte, el cierre parcial (partial close) permite reducir la exposición de la posición de forma escalonada.5 En una cuenta de tipo netting, el cierre parcial de un volumen ![][image1] se realiza enviando una orden inversa de mercado con volumen idéntico a ![][image1].1 En cuentas de tipo hedging, se requiere especificar el ticket de la posición activa en el campo position de la estructura de solicitud de transacción (MqlTradeRequest), asegurando así que la ejecución reduzca la posición objetivo en lugar de abrir una operación inversa independiente.1

### **Algoritmos de Trailing Stop de Alta Precisión**

Para implementar salidas basadas en volatilidad y estructura del precio, se recurre a tres metodologías matemáticas fundamentales:

#### **1\. Trailing Stop Basado en ATR (Average True Range)**

El uso de múltiplos del ATR permite que la distancia de protección se ensanche durante periodos de expansión de rango y se contraiga cuando el mercado entra en fases de compresión.17 El stop se calcula restando (para compras) o sumando (para ventas) un factor ![][image2] multiplicado por el valor actual del ATR (![][image3]) al precio de cierre.20 El principio de consistencia exige la implementación de un mecanismo de trinquete (ratchet), el cual impide que el nivel de stop se mueva en la dirección que incremente el riesgo asumido (el stop de una compra solo puede subir, jamás bajar).18  
![][image4]

#### **2\. Chandelier Exit**

Es una variante avanzada de los stop basados en volatilidad que ancla el cálculo al punto más alto (para compras) o más bajo (para ventas) alcanzado por el precio durante un periodo de observación retrospectivo de longitud ![][image5].20 Esto evita salidas prematuras durante correcciones severas de corto plazo dentro de una tendencia robusta.20  
![][image6]  
![][image7]

#### **3\. Parabolic SAR (Stop and Reverse)**

Es un indicador de seguimiento de tendencias cuyo diseño matemático acelera la velocidad de ajuste del stop a medida que la tendencia se extiende en el tiempo o se acelera en precio.14 Utiliza un factor de aceleración (![][image8]) que incrementa con cada nuevo extremo marcado en la tendencia actual, forzando al algoritmo de salida a capturar la mayor parte del recorrido antes de que ocurra una reversión violenta.14  
![][image9]  
Donde ![][image10] es el punto extremo (el máximo de la tendencia actual para compras, o el mínimo para ventas), y ![][image8] es el factor de aceleración que se incrementa en pasos de ![][image11] hasta alcanzar un límite máximo parametrizado de ![][image12].26

## **Position Sizing y Money Management**

La asignación de capital por operación constituye la barrera de contención contra el riesgo de ruina en sistemas algorítmicos.15 Los cálculos manuales del tamaño de lote son ineficientes y altamente propensos a errores debido a la fluctuación continua de los valores de tick en cuentas denominadas en divisas distintas a la moneda base del instrumento operado.15

### **Modelos de Position Sizing**

1. **Lote Fijo (Fixed Lot):** Consistencia matemática simple pero nula adaptación a las condiciones dinámicas de la cuenta o del mercado.15  
2. **Fraccionario Fijo (Fixed Fractional):** Arriesga un porcentaje estrictamente constante del capital neto de la cuenta por cada operación.27 Si el balance disminuye, el tamaño absoluto de las operaciones se contrae de forma proporcional, mitigando el riesgo de quiebra.15  
3. **Criterio de Kelly:** Determina la fracción óptima de capital a arriesgar para maximizar la tasa de crecimiento geométrico a largo plazo en función de la probabilidad de acierto del sistema (![][image13]) y la relación beneficio/riesgo promedio de las operaciones ganadoras frente a las perdedoras (![][image14]) 30:  
   ![][image15]  
   Para mitigar la alta volatilidad y los drawdowns profundos causados por errores de estimación en los parámetros históricos, se suele implementar el modelo de **Fraccionario de Kelly** (usualmente Half-Kelly, multiplicando ![][image16] por ![][image17]) para suavizar la varianza del balance sin sacrificar significativamente la tasa de crecimiento geométrico.32  
4. **f Óptima (Ralph Vince):** Generaliza el concepto de Kelly para distribuciones de retorno no binarias, buscando la fracción de capital que maximiza el crecimiento en función del peor resultado histórico obtenido.34 Al igual que Kelly, suele requerir factores de atenuación para evitar drawdowns catastróficos.34  
5. **Basado en Volatilidad (ATR Position Sizing):** Sincroniza el tamaño de la posición con la volatilidad intrínseca del activo bajo el postulado de que activos con mayor volatilidad requieren posiciones más pequeñas para mantener una equivalencia en el riesgo monetario asumido 15:  
   ![][image18]  
6. **Paridad de Riesgo (Risk Parity):** Diseñado para la asignación de portafolios multi-activo, donde la ponderación de cada instrumento se determina de forma que todos aporten de manera equitativa a la volatilidad total de la cartera, eliminando la dominancia de riesgo de activos altamente volátiles.35

### **Cálculo Preciso de Lotes y Validación de Margen**

Para realizar un cálculo robusto del tamaño de la posición, primero es imperativo determinar el valor real de cada punto de movimiento del precio del símbolo en la divisa base de la cuenta.27 Esto se realiza mediante la siguiente relación matemática 29:  
![][image19]  
Antes de proceder a enviar cualquier instrucción de ejecución al servidor, es de carácter obligatorio estimar el requisito de margen neto para asegurar que la cuenta dispone de suficiente margen libre.29 La función nativa de MT5 OrderCalcMargin() calcula este requisito simulando la transacción sin considerar las órdenes pendientes o posiciones abiertas en ese momento 29:  
![][image20]  
Este cálculo evita fallos de ejecución por insuficiencia de fondos, permitiendo que el módulo de riesgo valide de forma preventiva si la operación cumple con las políticas de apalancamiento y asignación de capital.29

## **Gestión de Riesgo a Nivel de Portfolio**

El control de riesgo de una cartera algorítmica exige trascender los límites de cada operación individual para observar la dinámica agregada del capital expuesto en el mercado.15

### **Correlación entre Instrumentos y Límites de Exposición**

La diversificación puede fallar si los activos bajo gestión presentan una alta correlación lineal en periodos de tensión financiera.35 El sistema debe computar periódicamente la correlación de los retornos diarios de los activos en cartera 35:  
![][image21]  
El módulo de riesgo del portafolio restringe la apertura de nuevas posiciones si la correlación agregada ponderada con las posiciones ya activas excede un límite de seguridad preestablecido (ej. ![][image22]). Asimismo, se imponen techos rígidos de exposición nocional agregada para evitar riesgos asimétricos:

* Exposición máxima por instrumento individual: ![][image23] del valor neto de liquidación (Equity).  
* Exposición máxima por sector de mercado o clase de activo: ![][image24] de la Equity.39  
* Exposición máxima por divisa base de cotización: ![][image25] de la Equity.

### **Umbrales de Drawdown y Circuit Breakers Automáticos**

Para evitar el escenario catastrófico de una racha de pérdidas consecutivas (losing streak) que afecte estructuralmente la cuenta de trading, se deben codificar de manera rígida límites de drawdown diario y semanal.40 El drawdown absoluto en tiempo real se calcula comparando el valor actual de la equidad en cuenta (![][image26]) frente al máximo valor histórico registrado de la misma (High-Water Mark, ![][image27]) 39:  
![][image28]  
El sistema incorpora un **Circuit Breaker Automático** de tres niveles progresivos:

1. **Nivel de Alerta (Drawdown Diario ![][image29]):** El sistema suspende la generación de nuevas señales de entrada por parte de los EAs, permitiendo únicamente que el algoritmo gestione las posiciones existentes para buscar salidas ordenadas o reducciones parciales de volumen.  
2. **Nivel de Restricción Comercial (Drawdown Diario ![][image30]):** Se cancelan de inmediato todas las órdenes pendientes en el servidor. El sistema suspende por completo la ejecución y entra en modo de solo lectura por un periodo mínimo de 24 horas.5  
3. **Kill Switch de Emergencia (Drawdown Diario ![][image31] o Semanal ![][image32]):** El módulo de riesgo asume el control absoluto del terminal.43 Cierra de inmediato todas las posiciones de mercado activas al precio disponible, elimina todas las órdenes pendientes y desactiva de forma global el autotrading en el terminal para evitar que los algoritmos vuelvan a interactuar con el mercado.5

## **Error Handling en la Ejecución de Órdenes**

La latencia, la falta de liquidez y la inestabilidad de la conexión con el servidor de trading introducen fricciones operativas que deterioran el rendimiento esperado de cualquier sistema cuantitativo si no son manejadas con estricto rigor algorítmico.13

### **Gestión de Fricciones del Mercado (Slippage, Requotes y Timeouts)**

El deslizamiento (slippage) debe modelarse dentro de las peticiones de envío configurando de manera estricta el campo deviation en la estructura MqlTradeRequest.13 Si la desviación de precio de mercado excede el umbral parametrizado, la orden debe rechazarse de inmediato en lugar de aceptar precios desfavorables.13  
Los timeouts deben ser gestionados mediante el uso de llamadas asíncronas controladas por temporizadores de precisión.45 Si el servidor no confirma la recepción o ejecución de una petición dentro del plazo previsto, el sistema debe iniciar un proceso de verificación del estado de las posiciones y órdenes activas antes de reintentar el envío de la orden, evitando la duplicación accidental de posiciones.5

### **Lógica Dinámica de Reintentos (Retry Logic) con Backoff Exponencial y Jitter**

Cuando una orden es rechazada por razones transitorias de mercado (p. ej., congestión del servidor o falta de cotización temporal), enviar reintentos inmediatos puede provocar bloqueos temporales por parte de los sistemas de protección contra spam del broker (TRADE\_RETCODE\_TOO\_MANY\_REQUESTS).5 El protocolo estándar de reintentos debe implementar un retraso exponencial (backoff) combinado con una variación aleatoria (jitter) para evitar la sincronización de reintentos con otros terminales de trading 46:  
![][image33]  
Donde ![][image34], ![][image35], y el reintento se limita a un máximo de 3 a 5 ciclos antes de reportar un fallo crítico del sistema y suspender la operación del símbolo.

### **Respuestas Sistémicas ante Códigos de Error Críticos**

La propiedad retcode de la estructura MqlTradeResult contiene la clave diagnóstica de la respuesta del servidor del broker.5 El algoritmo debe parsear este código de manera instantánea y ejecutar acciones correctivas automatizadas 1:

| Código de Error MT5 | Constante del Sistema | Diagnóstico de Causa | Acción Correctiva Algorítmica Requerida |
| :---- | :---- | :---- | :---- |
| **10004** 5 | TRADE\_RETCODE\_REQUOTE 48 | El precio ha cambiado durante el tránsito de la petición.9 | Solicitar ticks frescos mediante SymbolInfoTick(), actualizar la estructura de precios de la petición y volver a enviar.13 |
| **10014** | TRADE\_RETCODE\_INVALID\_VOLUME 13 | El volumen solicitado viola el lote mínimo, máximo o el paso de lote del broker.13 | Corregir el lote aplicando redondeo estricto al paso de lote (SYMBOL\_VOLUME\_STEP) y limitar dentro de los parámetros permitidos (SYMBOL\_VOLUME\_MIN/MAX).13 |
| **10016** 47 | TRADE\_RETCODE\_INVALID\_STOPS | Los de SL o TP violan el canal de congelación de precios del broker.46 | Consultar la propiedad de distancia mínima permitida (SYMBOL\_TRADE\_STOPS\_LEVEL) y reposicionar los stops fuera de esta zona.47 |
| **10019** 5 | TRADE\_RETCODE\_NO\_MONEY 5 | Margen libre insuficiente para abrir la posición con el volumen especificado.5 | Recalcular inmediatamente el tamaño del lote utilizando el margen libre actual de la cuenta, o cancelar de forma definitiva la transacción.13 |
| **10024** 5 | TRADE\_RETCODE\_TOO\_MANY\_REQUESTS 5 | Frecuencia de envío de peticiones excesivamente alta tolerada por el servidor del broker.5 | Suspender el envío de peticiones por un lapso mínimo de 5 a 10 segundos, revisar la lógica de bucles de los EAs y ralentizar los procesos de reintento.46 |
| **10030** 5 | TRADE\_RETCODE\_INVALID\_FILL 5 | El tipo de llenado de volumen solicitado no está soportado por el broker para el activo.46 | Consultar dinámicamente la propiedad de política de llenado permitida (SYMBOL\_FILLING\_MODE) y actualizar el campo de llenado de la orden.9 |

## **Risk Management en Código MQL5 y Python**

Las siguientes implementaciones de grado industrial han sido diseñadas bajo estrictos principios de robustez y modularidad de software.2

### **Implementación en MQL5: Clase de Control de Riesgo y Actuadores de Emergencia**

Este archivo de cabecera (CProgrammaticRiskManager.mqh) debe ser importado en la sección global del Expert Advisor para garantizar que ninguna orden se envíe al servidor de forma directa sin antes pasar por el filtro de validación de riesgo.

C++  
//+------------------------------------------------------------------+  
//|                      CProgrammaticRiskManager.mqh                 |  
//|                 Algorithmic Trading Architect (2026)             |  
//+------------------------------------------------------------------+  
\#property copyright "Algorithmic Trading Architect"  
\#property version   "1.00"  
\#property strict

\#**include** \<Trade\\Trade.mqh\>

class CProgrammaticRiskManager  
{  
private:  
   string            m\_symbol;  
   double            m\_maxDailyLossPct;  // Límite de pérdida diaria (ej. 5.0 para 5%)  
   double            m\_killSwitchPct;    // Límite absoluto para Kill Switch (ej. 7.0 para 7%)  
   ulong             m\_magicNumber;  
     
   double            m\_initialDailyEquity;  
   datetime          m\_lastEquityReset;  
   int               m\_logFileHandle;  
     
   CTrade            m\_trade;

   void              InitLogging();  
   void              WriteToLog(string message);  
     
public:  
                     CProgrammaticRiskManager(const string symbol, const ulong magic, const double maxDailyLoss, const double killSwitch);  
                    \~CProgrammaticRiskManager();  
                      
   void              DailyEquityReset();  
   bool              CheckMarginRequirements(ENUM\_ORDER\_TYPE orderType, double volume, double price);  
   double            CalculatePositionSize(double riskAmountPct, double slDistancePoints);  
   bool              EvaluateDrawdownCircuitBreaker();  
   bool              KillAllPositions();  
};

//+------------------------------------------------------------------+  
//| Constructor parametrizado                                        |  
//+------------------------------------------------------------------+  
CProgrammaticRiskManager::CProgrammaticRiskManager(const string symbol, const ulong magic, const double maxDailyLoss, const double killSwitch)  
   : m\_symbol(symbol),  
     m\_magicNumber(magic),  
     m\_maxDailyLossPct(maxDailyLoss),  
     m\_killSwitchPct(killSwitch)  
{  
   m\_trade.SetExpertMagicNumber(m\_magicNumber);  
   m\_trade.SetTypeFillingBySymbol(m\_symbol);  
   DailyEquityReset();  
   InitLogging();  
}

//+------------------------------------------------------------------+  
//| Destructor                                                       |  
//+------------------------------------------------------------------+  
CProgrammaticRiskManager::\~CProgrammaticRiskManager()  
{  
   if(m\_logFileHandle\!= INVALID\_HANDLE)  
   {  
      FileClose(m\_logFileHandle);  
   }  
}

//+------------------------------------------------------------------+  
//| Inicialización de Logging Corporativo                            |  
//+------------------------------------------------------------------+  
void CProgrammaticRiskManager::InitLogging()  
{  
   string fileName \= "RiskManager\_" \+ m\_symbol \+ "\_" \+ IntegerToString(m\_magicNumber) \+ ".log";  
   m\_logFileHandle \= FileOpen(fileName, FILE\_WRITE | FILE\_READ | FILE\_TXT | FILE\_SHARE\_READ);  
   if(m\_logFileHandle\!= INVALID\_HANDLE)  
   {  
      FileSeek(m\_logFileHandle, 0, SEEK\_END);  
      WriteToLog("SISTEMA DE GESTION DE RIESGO INICIALIZADO. Símbolo: " \+ m\_symbol);  
   }  
}

void CProgrammaticRiskManager::WriteToLog(string message)  
{  
   if(m\_logFileHandle\!= INVALID\_HANDLE)  
   {  
      string timeStr \= TimeToString(TimeCurrent(), TIME\_DATE | TIME\_SECONDS);  
      FileWrite(m\_logFileHandle, " " \+ message);  
      FileFlush(m\_logFileHandle);  
   }  
   Print(" " \+ message);  
}

//+------------------------------------------------------------------+  
//| Reseteo del capital diario para control de drawdown             |  
//+------------------------------------------------------------------+  
void CProgrammaticRiskManager::DailyEquityReset()  
{  
   m\_initialDailyEquity \= AccountInfoDouble(ACCOUNT\_EQUITY);  
   m\_lastEquityReset \= TimeCurrent();  
}

//+------------------------------------------------------------------+  
//| Verificación previa de suficiencia de margen                     |  
//+------------------------------------------------------------------+  
bool CProgrammaticRiskManager::CheckMarginRequirements(ENUM\_ORDER\_TYPE orderType, double volume, double price)  
{  
   double marginRequired \= 0.0;  
   ResetLastError();  
     
   if(\!OrderCalcMargin(orderType, m\_symbol, volume, price, marginRequired))  
   {  
      WriteToLog("Error al calcular el margen con OrderCalcMargin. Código: " \+ IntegerToString(GetLastError()));  
      return false;  
   }  
     
   double freeMargin \= AccountInfoDouble(ACCOUNT\_MARGIN\_FREE);  
     
   //--- Permitir la operación únicamente si tenemos un margen libre que supere el requisito más un 20% de seguridad  
   if(freeMargin \< (marginRequired \* 1.2))  
   {  
      WriteToLog(StringFormat("FALTA DE MARGEN: Requerido: %.2f, Disponible: %.2f (Buffer 1.2x No Satisfecho)", marginRequired, freeMargin));  
      return false;  
   }  
     
   return true;  
}

//+------------------------------------------------------------------+  
//| Cálculo dinámico de posición basado en puntos de SL              |  
//+------------------------------------------------------------------+  
double CProgrammaticRiskManager::CalculatePositionSize(double riskAmountPct, double slDistancePoints)  
{  
   if(slDistancePoints \<= 0)  
   {  
      WriteToLog("Error: Distancia de Stop Loss debe ser mayor que cero.");  
      return 0.0;  
   }

   double balance \= AccountInfoDouble(ACCOUNT\_BALANCE);  
   double riskMoney \= balance \* (riskAmountPct / 100.0);  
     
   double tickValue \= SymbolInfoDouble(m\_symbol, SYMBOL\_TRADE\_TICK\_VALUE);  
   double tickSize  \= SymbolInfoDouble(m\_symbol, SYMBOL\_TRADE\_TICK\_SIZE);  
   double point     \= SymbolInfoDouble(m\_symbol, SYMBOL\_POINT);  
     
   if(tickSize \== 0 || point \== 0) return 0.0;  
     
   double pointsInTick \= tickSize / point;  
   double pointValue \= tickValue / pointsInTick;  
     
   double rawLotSize \= riskMoney / (slDistancePoints \* pointValue);  
     
   double lotStep \= SymbolInfoDouble(m\_symbol, SYMBOL\_VOLUME\_STEP);  
   double minLot  \= SymbolInfoDouble(m\_symbol, SYMBOL\_VOLUME\_MIN);  
   double maxLot  \= SymbolInfoDouble(m\_symbol, SYMBOL\_VOLUME\_MAX);  
     
   double normalizedLot \= MathFloor(rawLotSize / lotStep) \* lotStep;  
     
   if(normalizedLot \< minLot)  
   {  
      WriteToLog(StringFormat("Lote calculado (%.4f) menor que el mínimo permitido (%.2f). Operación abortada.", rawLotSize, minLot));  
      return 0.0;  
   }  
   if(normalizedLot \> maxLot)  
   {  
      normalizedLot \= maxLot;  
      WriteToLog(StringFormat("Lote limitado al máximo del broker: %.2f", maxLot));  
   }  
     
   return normalizedLot;  
}

//+------------------------------------------------------------------+  
//| Monitoreo de pérdidas en tiempo real y activación de cortocircuitos|  
//+------------------------------------------------------------------+  
bool CProgrammaticRiskManager::EvaluateDrawdownCircuitBreaker()  
{  
   MqlDateTime currentStruct;  
   TimeToStruct(TimeCurrent(), currentStruct);  
   if(TimeCurrent() \- m\_lastEquityReset \>= 86400)  
   {  
      DailyEquityReset();  
      WriteToLog("Reset diario de referencia de capital ejecutado con éxito.");  
   }

   double currentEquity \= AccountInfoDouble(ACCOUNT\_EQUITY);  
   double currentLossPct \= ((m\_initialDailyEquity \- currentEquity) / m\_initialDailyEquity) \* 100.0;

   if(currentLossPct \>= m\_killSwitchPct)  
   {  
      WriteToLog(StringFormat("CRÍTICO: Umbral de Kill Switch superado (%.2f%%). Ejecutando liquidación de emergencia.", currentLossPct));  
      KillAllPositions();  
      ExpertRemove(); // Desactiva permanentemente el EA  
      return false;  
   }  
   else if(currentLossPct \>= m\_maxDailyLossPct)  
   {  
      WriteToLog(StringFormat("ADVERTENCIA: Drawdown diario (%.2f%%) supera el máximo diario. Operaciones bloqueadas.", currentLossPct));  
      return false; // Bloquea la entrada de nuevas posiciones  
   }

   return true; // Estado de riesgo dentro de los parámetros admisibles  
}

//+------------------------------------------------------------------+  
//| Kill Switch de Emergencia: Cierre absoluto de posiciones activas  |  
//+------------------------------------------------------------------+  
bool CProgrammaticRiskManager::KillAllPositions()  
{  
   bool allClosed \= true;  
   WriteToLog("INICIANDO PROCEDIMIENTO DE LIQUIDACIÓN ABSOLUTA EN MERCADO.");  
     
   for(int i \= PositionsTotal() \- 1; i \>= 0; i--)  
   {  
      ulong ticket \= PositionGetTicket(i);  
      if(ticket \<= 0) continue;  
        
      if(PositionSelectByTicket(ticket))  
      {  
         string posSymbol \= PositionGetString(POSITION\_SYMBOL);  
         long   posMagic  \= PositionGetInteger(POSITION\_MAGIC);  
           
         if(posSymbol \== m\_symbol && posMagic \== m\_magicNumber)  
         {  
            m\_trade.PositionClose(ticket);  
            if(m\_trade.ResultRetcode()\!= TRADE\_RETCODE\_DONE)  
            {  
               WriteToLog(StringFormat("Error al cerrar ticket %d: %s", ticket, m\_trade.ResultComment()));  
               allClosed \= false;  
            }  
            else  
            {  
               WriteToLog(StringFormat("Ticket %d cerrado con éxito en mercado.", ticket));  
            }  
         }  
      }  
   }  
   return allClosed;  
}

### **Implementación en Python: Módulo de Conexión de API de MT5, Monitor de Riesgo y Apagado**

Módulo escrito en Python (risk\_manager.py) diseñado para la integración asíncrona mediante sistemas de ejecución remota o para ser consumido en backtesting híbrido.2

Python  
"""  
risk\_manager.py  
Módulo de Gestión de Riesgo Programático y Controladores de Emergencia para MT5.  
Algorithmic Trading Architect (2026)  
"""

import sys  
import logging  
from datetime import datetime  
import MetaTrader5 as mt5

class ProgrammaticRiskManager:  
    def \_\_init\_\_(self, symbol: str, magic: int, max\_daily\_loss\_pct: float, kill\_switch\_pct: float):  
        self.symbol \= symbol  
        self.magic \= magic  
        self.max\_daily\_loss\_pct \= max\_daily\_loss\_pct  
        self.kill\_switch\_pct \= kill\_switch\_pct  
          
        self.initial\_daily\_equity \= 0.0  
        self.last\_equity\_reset \= datetime.now()  
          
        self.\_init\_logging()  
        self.\_initialize\_mt5()  
        self.daily\_equity\_reset()

    def \_\_del\_\_(self):  
        """  
        Destructor para garantizar que la conexión se libere correctamente al finalizar el proceso.  
        """  
        try:  
            mt5.shutdown()  
            self.logger.info("Conexión con MetaTrader 5 finalizada ordenadamente en destructor.")  
        except Exception as e:  
            pass

    def \_init\_logging(self):  
        log\_format \= '%(asctime)s \[%(levelname)s\] (%(filename)s:%(lineno)d) \- %(message)s'  
        logging.basicConfig(  
            level=logging.INFO,  
            format\=log\_format,  
            handlers=  
        )  
        self.logger \= logging.getLogger("RiskManager")  
        self.logger.info("Módulo Python de Gestión de Riesgo inicializado.")

    def \_initialize\_mt5(self):  
        if not mt5.initialize():  
            self.logger.critical(f"Fallo en la conexión del terminal MT5. Código de error: {mt5.last\_error()}")  
            raise ConnectionError("No se pudo inicializar la API de MetaTrader 5.")  
          
        if not mt5.symbol\_select(self.symbol, True):  
            self.logger.critical(f"Símbolo {self.symbol} no está disponible en la plataforma.")  
            mt5.shutdown()  
            raise ValueError(f"Símbolo {self.symbol} inaccesible en MarketWatch.")

    def daily\_equity\_reset(self):  
        account\_info \= mt5.account\_info()  
        if account\_info is None:  
            self.logger.error("No se pudo obtener información de la cuenta para resetear equidad.")  
            return  
        self.initial\_daily\_equity \= account\_info.equity  
        self.last\_equity\_reset \= datetime.now()  
        self.logger.info(f"Capital de referencia diaria reseteado a: {self.initial\_daily\_equity:.2f}")

    def check\_margin\_requirements(self, order\_type: int, volume: float, price: float) \-\> bool:  
        margin\_required \= mt5.order\_calc\_margin(order\_type, self.symbol, volume, price)  
        if margin\_required is None:  
            self.logger.error(f"Fallo al calcular margen usando order\_calc\_margin. Error: {mt5.last\_error()}")  
            return False  
              
        account\_info \= mt5.account\_info()  
        if account\_info is None:  
            self.logger.error("Error al obtener información de la cuenta para validar fondos.")  
            return False  
              
        free\_margin \= account\_info.margin\_free  
          
        if free\_margin \< (margin\_required \* 1.2):  
            self.logger.warning(  
                f"MARGEN INSUFICIENTE. Requerido simulado: {margin\_required:.2f}, Disponible libre: {free\_margin:.2f}"  
            )  
            return False  
              
        return True

    def calculate\_position\_size(self, risk\_amount\_pct: float, sl\_distance\_points: float) \-\> float:  
        if sl\_distance\_points \<= 0:  
            self.logger.error("La distancia del Stop Loss debe ser un número entero de puntos superior a cero.")  
            return 0.0

        account\_info \= mt5.account\_info()  
        if account\_info is None:  
            self.logger.error("No se pudo recuperar la información de la cuenta.")  
            return 0.0

        balance \= account\_info.balance  
        risk\_money \= balance \* (risk\_amount\_pct / 100.0)

        symbol\_info \= mt5.symbol\_info(self.symbol)  
        if symbol\_info is None:  
            self.logger.error(f"No se pudo extraer especificaciones para el símbolo: {self.symbol}")  
            return 0.0

        tick\_value \= symbol\_info.trade\_tick\_value  
        tick\_size \= symbol\_info.trade\_tick\_size  
        point \= symbol\_info.point

        if tick\_size \== 0 or point \== 0:  
            return 0.0

        points\_in\_tick \= tick\_size / point  
        point\_value \= tick\_value / points\_in\_tick

        raw\_lot\_size \= risk\_money / (sl\_distance\_points \* point\_value)

        lot\_step \= symbol\_info.volume\_step  
        min\_lot \= symbol\_info.volume\_min  
        max\_lot \= symbol\_info.volume\_max

        normalized\_lot \= (raw\_lot\_size // lot\_step) \* lot\_step  
        normalized\_lot \= round(normalized\_lot, 2)

        if normalized\_lot \< min\_lot:  
            self.logger.warning(  
                f"Lote calculado ({raw\_lot\_size:.4f}) es inferior al mínimo permitido ({min\_lot}). Operación bloqueada."  
            )  
            return 0.0  
        if normalized\_lot \> max\_lot:  
            normalized\_lot \= max\_lot  
            self.logger.info(f"Lote limitado al máximo institucional permitido: {max\_lot}")

        return normalized\_lot

    def evaluate\_drawdown\_circuit\_breaker(self) \-\> bool:  
        now \= datetime.now()  
        if (now \- self.last\_equity\_reset).total\_seconds() \>= 86400:  
            self.daily\_equity\_reset()

        account\_info \= mt5.account\_info()  
        if account\_info is None:  
            self.logger.error("Error crítico al leer datos de cuenta para el circuit breaker.")  
            return False

        current\_equity \= account\_info.equity  
        current\_loss\_pct \= ((self.initial\_daily\_equity \- current\_equity) / self.initial\_daily\_equity) \* 100.0

        if current\_loss\_pct \>= self.kill\_switch\_pct:  
            self.logger.critical(  
                f"CIRCUIT BREAKER DETECTADO: Drawdown diario crítico de {current\_loss\_pct:.2f}%. "  
                f"Umbral de Kill Switch ({self.kill\_switch\_pct}%) superado. Ejecutando liquidación."  
            )  
            self.kill\_all\_positions()  
            raise RuntimeError("Sistema finalizado de emergencia por violación crítica de riesgo.")  
              
        elif current\_loss\_pct \>= self.max\_daily\_loss\_pct:  
            self.logger.warning(  
                f"BLOQUEO OPERATIVO: Drawdown diario ({current\_loss\_pct:.2f}%) supera el límite diario. "  
                f"Se bloquea el flujo de nuevas órdenes."  
            )  
            return False

        return True

    def kill\_all\_positions(self) \-\> bool:  
        self.logger.info("EJECUTANDO KILL SWITCH: LIQUIDANDO CARTERA DE FORMA INCONDICIONAL.")  
        positions \= mt5.positions\_get(symbol=self.symbol)  
          
        if positions is None or len(positions) \== 0:  
            self.logger.info("No se detectaron posiciones activas de mercado en el símbolo.")  
            return True  
              
        success\_flag \= True  
          
        for pos in positions:  
            if pos.magic \== self.magic:  
                order\_type \= mt5.ORDER\_TYPE\_SELL if pos.type \== mt5.ORDER\_TYPE\_BUY else mt5.ORDER\_TYPE\_BUY  
                price \= mt5.symbol\_info\_tick(self.symbol).bid if order\_type \== mt5.ORDER\_TYPE\_SELL else mt5.symbol\_info\_tick(self.symbol).ask  
                  
                request \= {  
                    "action": mt5.TRADE\_ACTION\_DEAL,  
                    "symbol": self.symbol,  
                    "volume": pos.volume,  
                    "type": order\_type,  
                    "position": pos.ticket,  
                    "price": price,  
                    "deviation": 20,  
                    "magic": self.magic,  
                    "comment": "KILL SWITCH ACTUATOR",  
                    "type\_time": mt5.ORDER\_TIME\_GTC,  
                    "type\_filling": mt5.ORDER\_FILLING\_IOC,  
                }  
                  
                result \= mt5.order\_send(request)  
                if result.retcode\!= mt5.TRADE\_RETCODE\_DONE:  
                    self.logger.error(  
                        f"No se pudo cerrar la posición con ticket {pos.ticket}. Código de respuesta: {result.retcode}"  
                    )  
                    success\_flag \= False  
                else:  
                    self.logger.info(f"Posición con ticket {pos.ticket} liquidada correctamente.")  
                      
        return success\_flag

## **Consideraciones de Broker: Infraestructura y Regulación**

La parametrización de un módulo de control de riesgo no puede desvincularse de las especificidades contables y regulatorias bajo las cuales opera el servidor de ejecución del broker seleccionado.13

### **Cuentas Hedging frente a Cuentas Netting**

La diferencia de arquitectura radica en cómo se procesan múltiples transacciones paralelas sobre un mismo instrumento comercial 1:

* **Netting System (Modelo de Red de Posición):** Es el estándar de los mercados bursátiles tradicionales.1 Solo se permite **una posición abierta por símbolo** en un instante específico.1 Cualquier operación adicional en la misma dirección añade volumen y recalcula el precio medio de apertura mediante una media ponderada.1 Operaciones en dirección opuesta reducen directamente el volumen de la posición abierta, la cierran por completo, o la revierten si la orden contraria excede el volumen neto anterior.1 En este sistema, los stop loss de cada orden subsequente reemplazan a los niveles previamente establecidos para toda la posición consolidada, requiriendo un control estricto de los parámetros del envío.1  
* **Hedging System (Modelo de Cobertura de Posición):** Estándar de los brokers extrabursátiles (OTC).1 Admite la coexistencia de **múltiples posiciones paralelas e independientes sobre el mismo símbolo**, incluso en direcciones opuestas.1 Cada deal genera una posición única con su propio identificador y stop loss propio, sin verse afectada por transacciones subsecuentes.1

### **Regla FIFO (First-In, First-Out) y Restricciones de la NFA**

Para algoritmos que operen bajo la jurisdicción de la NFA (National Futures Association de los Estados Unidos) en cuentas de tipo Hedging, está estrictamente prohibido realizar transacciones compensatorias o cruzadas de cobertura.5 Asimismo, si se tienen varias posiciones abiertas del mismo símbolo, se exige de forma rigurosa que se cierren en estricto orden cronológico (la primera posición abierta debe ser obligatoriamente la primera en liquidarse).5 El incumplimiento de esta directiva provoca que el servidor de ejecución del broker rechace la transacción inmediatamente con el código de error TRADE\_RETCODE\_FIFO\_CLOSE.5

### **Ajustes Dinámicos de Margen ante Eventos Macroeconómicos**

Los brokers institucionales modifican de manera regular sus condiciones de apalancamiento para proteger su liquidez antes de la publicación de datos macroeconómicos de primer impacto (p. ej., nóminas no agrícolas, tasas de interés de la Fed) o ante cierres de mercado el fin de semana.13 Estas modificaciones deben ser interceptadas por el algoritmo mediante el monitoreo de los requisitos calculados por OrderCalcMargin() de forma constante antes de colocar órdenes, ya que el broker puede elevar el margen requerido hasta en un 500% en cuestión de segundos, reduciendo la capacidad de apertura de posiciones e incrementando la probabilidad de activar llamadas de margen (Margin Call) o ejecuciones forzadas (Stop Out).13

| Atributo Comercial | Netting System | Hedging System |
| :---- | :---- | :---- |
| **Límite de Posiciones** 1 | Máximo una única posición activa por símbolo.1 | Múltiples posiciones paralelas admitidas.1 |
| **Efecto de Orden Opuesta** 1 | Contrae, cierra o revierte la posición neta.1 | Abre una posición independiente en sentido opuesto.1 |
| **Cálculo del Margen** 1 | Estándar sobre el volumen neto consolidado. | Permite condiciones favorables de Margen Hedged.1 |
| **Herencia de SL/TP** 1 | La última orden modifica los stops de toda la posición.1 | Cada posición conserva sus propios stops definidos.1 |
| **Cierre de Posiciones** 1 | Requiere una transacción inversa de mercado.1 | Exige especificar el ticket exacto a liquidar.1 |

## **Conclusiones y Recomendaciones de Implementación**

La implementación exitosa de un sistema de trading algorítmico profesional en MetaTrader 5 requiere mitigar proactivamente las limitaciones de la plataforma mediante un diseño de software estrictamente defensivo:

### **Desacoplamiento Arquitectónico Estricto**

La lógica de generación de señales (Alfa) debe estar completamente separada de la capa de control de riesgo (Beta) y de la capa de persistencia y ejecución de órdenes (Gamma). La clase CProgrammaticRiskManager en MQL5 y el módulo homónimo en Python deben actuar como un cortafuegos (firewall) de control preventivo antes de canalizar cualquier orden comercial hacia los servidores del terminal.

### **Verificación Preventiva Sistemática**

Es un error crítico de programación confiar en los códigos de error del broker *después* de que una operación ha sido rechazada. Un algoritmo profesional debe validar preventivamente el tamaño del lote, verificar la suficiencia de margen mediante OrderCalcMargin(), comprobar la distancia mínima de congelación de stops (SYMBOL\_TRADE\_STOPS\_LEVEL) e inspeccionar el estado de conexión del servidor antes de transmitir una orden comercial.13

### **Latencia y Ubicación de Infraestructura (Colocación)**

El deslizamiento y los requotes son subproductos directos de la latencia física de red.13 Para algoritmos de alta frecuencia o sistemas intradiarios sensibles al precio, es altamente recomendable contratar servidores privados virtuales (VPS) colocados en el mismo centro de datos que aloja los servidores de ejecución del broker (típicamente Equinix LD4 en Londres o NY4 en Nueva York), minimizando el tiempo de tránsito y eliminando el desajuste de cotizaciones en tránsito.13

#### **Fuentes citadas**

1. Basic principles and concepts: order, deal, and position \- Trading ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_order\_deal\_position](https://www.mql5.com/en/book/automation/experts/experts_order_deal_position)  
2. MetaTrader 5 Python Integration \- Grokipedia, acceso: junio 28, 2026, [https://grokipedia.com/page/MetaTrader\_5\_Python\_Integration](https://grokipedia.com/page/MetaTrader_5_Python_Integration)  
3. difference between position history , deal history in MT5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/507395](https://www.mql5.com/en/forum/507395)  
4. what is the differnece between position and order? \- Commodity Channel Index, CCI \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/1046](https://www.mql5.com/en/forum/1046)  
5. Trade Server Return Codes \- Codes of Errors and Warnings \- Constants, Enumerations and Structures \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/errorswarnings/enum\_trade\_return\_codes](https://www.mql5.com/en/docs/constants/errorswarnings/enum_trade_return_codes)  
6. Position vs. Deal vs. Order \- Trading Positions \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/314300](https://www.mql5.com/en/forum/314300)  
7. The new concept of position, orders and deals is too confusing. Need some help\! \- MT5 \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/1778](https://www.mql5.com/en/forum/1778)  
8. positions\_get \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5positionsget\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5positionsget_py)  
9. Symbol trading conditions and order execution modes \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/symbols/symbols\_execution\_filling](https://www.mql5.com/en/book/automation/symbols/symbols_execution_filling)  
10. Order execution modes by price and volume \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_execution\_filling](https://www.mql5.com/en/book/automation/experts/experts_execution_filling)  
11. Order Properties \- Trade Constants \- Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties](https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties)  
12. SetTypeFillingBySymbol(const string) \- CTrade \- Trade Classes \- Standard Library \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/standardlibrary/tradeclasses/ctrade/ctradesettypefillingbysymbol](https://www.mql5.com/en/docs/standardlibrary/tradeclasses/ctrade/ctradesettypefillingbysymbol)  
13. MetaTrader Error Survival Guide 2026: Fix Trade Disabled & More \- NYCServers, acceso: junio 28, 2026, [https://newyorkcityservers.com/blog/metatrader-error-survival-guide-2025-fix-trade-disabled-more](https://newyorkcityservers.com/blog/metatrader-error-survival-guide-2025-fix-trade-disabled-more)  
14. The solution for intelligent exit condition? \- Trading Tools \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/508339](https://www.mql5.com/en/forum/508339)  
15. Risk Calculators and Position Sizing Tools for MT5 | For Traders, acceso: junio 28, 2026, [https://www.fortraders.com/blog/risk-calculators-position-sizing-tools-mt5](https://www.fortraders.com/blog/risk-calculators-position-sizing-tools-mt5)  
16. How to add Trailing Stop using Parabolic SAR \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/14782](https://www.mql5.com/en/articles/14782)  
17. Chandelier Exit Indicator for MT5 Download \[Free\] TradingFinder | Forex Factory, acceso: junio 28, 2026, [https://www.forexfactory.com/thread/1336289-chandelier-exit-indicator-for-mt5-download-free-tradingfinder](https://www.forexfactory.com/thread/1336289-chandelier-exit-indicator-for-mt5-download-free-tradingfinder)  
18. Trailing stop \- Trading automation \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_trailing\_stop](https://www.mql5.com/en/book/automation/experts/experts_trailing_stop)  
19. Chandelier Exit EA with Position Management | PDF | Computer Programming \- Scribd, acceso: junio 28, 2026, [https://www.scribd.com/document/931168670/Chandelier-Exit-EA](https://www.scribd.com/document/931168670/Chandelier-Exit-EA)  
20. Chandelier Exit Indicator: How the Adaptive Trailing Stop Works \- NetPicks, acceso: junio 28, 2026, [https://www.netpicks.com/chandelier-exit/](https://www.netpicks.com/chandelier-exit/)  
21. The ATR Trailing Stops Indicator: When and How to Use It for Effective Trading, acceso: junio 28, 2026, [https://strategyquant.com/blog/the-atr-trailing-stops-indicator-when-and-how-to-use-it-for-effective-trading/](https://strategyquant.com/blog/the-atr-trailing-stops-indicator-when-and-how-to-use-it-for-effective-trading/)  
22. ATR Trailing Stops \#724 \- facioquo stock-indicators-dotnet \- GitHub, acceso: junio 28, 2026, [https://github.com/DaveSkender/Stock.Indicators/discussions/724](https://github.com/DaveSkender/Stock.Indicators/discussions/724)  
23. ChandelierExit-EMA Dynamic Stop-Loss Trend-Following Strategy | by Sword Red | Medium, acceso: junio 28, 2026, [https://medium.com/@redsword\_23261/chandelierexit-ema-dynamic-stop-loss-trend-following-strategy-4ed49f313a28](https://medium.com/@redsword_23261/chandelierexit-ema-dynamic-stop-loss-trend-following-strategy-4ed49f313a28)  
24. Chandelier Exit \- indicator for MetaTrader 4 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/code/7249](https://www.mql5.com/en/code/7249)  
25. Chandelier exit \- indicator for MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/code/19875](https://www.mql5.com/en/code/19875)  
26. Parabolic SAR: Formula, Calculation, and Python Code \- QuantInsti Blog, acceso: junio 28, 2026, [https://blog.quantinsti.com/parabolic-sar/](https://blog.quantinsti.com/parabolic-sar/)  
27. How to calculate proper lot size ? \- Trading Strategies That Work \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/388742](https://www.mql5.com/en/forum/388742)  
28. Position Sizing and Risk Management in MQL5 \- Online Trading, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/232435](https://www.mql5.com/en/forum/232435)  
29. Margin calculation for a future order: OrderCalcMargin \- Trading ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_ordercalcmargin](https://www.mql5.com/en/book/automation/experts/experts_ordercalcmargin)  
30. Kelly criterion \- Wikipedia, acceso: junio 28, 2026, [https://en.wikipedia.org/wiki/Kelly\_criterion](https://en.wikipedia.org/wiki/Kelly_criterion)  
31. The Kelly Criterion — Hands-On Mathematical Optimization with AMPL in Python, acceso: junio 28, 2026, [https://ampl.com/mo-book/notebooks/06/kelly-criterion.html](https://ampl.com/mo-book/notebooks/06/kelly-criterion.html)  
32. Kelly Criterion Applications in Trading Systems \- QuantConnect.com, acceso: junio 28, 2026, [https://www.quantconnect.com/research/18312/kelly-criterion-applications-in-trading-systems/](https://www.quantconnect.com/research/18312/kelly-criterion-applications-in-trading-systems/)  
33. Using the Kelly Criterion in actual trading \- Forex Factory, acceso: junio 28, 2026, [https://www.forexfactory.com/thread/1144543-using-the-kelly-criterion-in-actual-trading](https://www.forexfactory.com/thread/1144543-using-the-kelly-criterion-in-actual-trading)  
34. The Kelly Criterion \- Money Management 101 \- Trading Practice \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/353748](https://www.mql5.com/en/forum/353748)  
35. Risk Parity Allocation with Python \- LuxAlgo, acceso: junio 28, 2026, [https://www.luxalgo.com/blog/risk-parity-allocation-with-python/](https://www.luxalgo.com/blog/risk-parity-allocation-with-python/)  
36. Building a Python-Based Risk Parity Portfolio for Trading | by SR \- Medium, acceso: junio 28, 2026, [https://medium.com/@deepml1818/building-a-python-based-risk-parity-portfolio-for-trading-40441ecdd84d](https://medium.com/@deepml1818/building-a-python-based-risk-parity-portfolio-for-trading-40441ecdd84d)  
37. Risk Parity Portfolio: Strategy, Example & Python Implementation \- QuantInsti Blog, acceso: junio 28, 2026, [https://blog.quantinsti.com/risk-parity-portfolio/](https://blog.quantinsti.com/risk-parity-portfolio/)  
38. OrderCalcMargin \- Trade Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/trading/ordercalcmargin](https://www.mql5.com/en/docs/trading/ordercalcmargin)  
39. Python for Real-Time Risk Monitoring in Algorithmic Trading | by SR \- Medium, acceso: junio 28, 2026, [https://medium.com/@deepml1818/python-for-real-time-risk-monitoring-in-algorithmic-trading-62a44ee9d921](https://medium.com/@deepml1818/python-for-real-time-risk-monitoring-in-algorithmic-trading-62a44ee9d921)  
40. Portfolio-Risk-Analysis-with-Python/Drawdown.ipynb at master \- GitHub, acceso: junio 28, 2026, [https://github.com/SharmaVidhiHaresh/Portfolio-Risk-Analysis-with-Python/blob/master/Drawdown.ipynb](https://github.com/SharmaVidhiHaresh/Portfolio-Risk-Analysis-with-Python/blob/master/Drawdown.ipynb)  
41. How to Build a Risk Parity Portfolio Using Python: Step-by-Step Guide | TraderVPS, acceso: junio 28, 2026, [https://www.tradervps.com/blog/how-to-build-a-risk-parity-portfolio-using-python-step-by-step-guide](https://www.tradervps.com/blog/how-to-build-a-risk-parity-portfolio-using-python-step-by-step-guide)  
42. Risk Management in Python: Control Drawdowns, Maximize Returns \- PyQuant News, acceso: junio 28, 2026, [https://www.pyquantnews.com/free-python-resources/risk-management-in-python-control-drawdowns-maximize-returns](https://www.pyquantnews.com/free-python-resources/risk-management-in-python-control-drawdowns-maximize-returns)  
43. Build a Remote Forex Risk Management System in Python \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/17410](https://www.mql5.com/en/articles/17410)  
44. Discussing the article: "Build a Remote Forex Risk Management System in Python" \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/503873](https://www.mql5.com/en/forum/503873)  
45. MetatraderTradeResponse \- MetaApi \- Powerful cloud forex trading API for MetaTrader, acceso: junio 28, 2026, [https://metaapi.cloud/docs/client/models/metatraderTradeResponse/](https://metaapi.cloud/docs/client/models/metatraderTradeResponse/)  
46. Fix Common MT5 EA Errors in AlgoWay Automation, acceso: junio 28, 2026, [https://algoway.trade/blog/algowaymt5-user-guide-for-metatrader-5-common-errors.html](https://algoway.trade/blog/algowaymt5-user-guide-for-metatrader-5-common-errors.html)  
47. Retcode=10016 when executing a trade in metatrader 5 \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/75952574/retcode-10016-when-executing-a-trade-in-metatrader-5](https://stackoverflow.com/questions/75952574/retcode-10016-when-executing-a-trade-in-metatrader-5)  
48. \[Python\] Constantly getting "TRADE\_RETCODE\_REQUOTE" error but can't see the problem w/my JSON would fail? \- MT5 \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/336952](https://www.mql5.com/en/forum/336952)  
49. order\_send() error in python algo trading \- MetaTrader 5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/440602](https://www.mql5.com/en/forum/440602)  
50. Automated Trading with MetaTrader5: Order Management and ..., acceso: junio 28, 2026, [https://dev.to/vital7777/automated-trading-with-metatrader5-order-management-and-market-data-collection-4pb8](https://dev.to/vital7777/automated-trading-with-metatrader5-order-management-and-market-data-collection-4pb8)  
51. Integrating MetaTrader 5 API in Python : A Practical Example | by Ullasraj \- Medium, acceso: junio 28, 2026, [https://medium.com/@ullasraj1998/integrating-metatrader-5-api-in-python-a-practical-example-3996524f1ea0](https://medium.com/@ullasraj1998/integrating-metatrader-5-api-in-python-a-practical-example-3996524f1ea0)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADoAAAAaCAYAAADmF08eAAACKElEQVR4Xu2Wz0sVURTHjyCCYZILV5U8MRJBAmvRogjdFSKuhRZS6EqkRbsEjaDQjVC20dIW/QH5AwssIahFgiUIooswfy5EKw1SErHv4dzLnHd6g/F8PByZD3x4937P/Hh37sydIYqJiTnq5MCfcF+5kbSFsEdBnduRZYBkENUm13A98jSSDOSeyT2D8JINo0gZyUBHbQGcgKs2jDI80E0bgj82iDp+sdHchm0mizypBmr7xwI70BlYrPrZZMEGITymNCZjm4KdeHH6oGrZ5r4NQjhJaQz0LclOJe43CnTCfhseRDvJAJfgDVNjyuEQbIJv4HtYr+p34Qich8Mq/wy3YCt8AW+qGr+fX8Nl178OP5K81zXv4HP4FI6rfBeeVf3/ooZkoD9swcGfijzbfHCPn/kW+Mq181TOF4XhfgGchd0u+w3PqHohyRdaHfzicmYOXnTtB3BM1dK683JJduTv3zB64SPV9yfSJ7xF8hho7B9qSJF5duBp186n5O0W4VXX5gsXdoxD42eGueD6/Kf0Cb9R8GeYZvr3i2sC9pjMo4/VB7+qvq7xBX+m+hlFn2gdFqXIfZufP2YFXnZtTwd8qPqVMOFyHtw1l1+hYLE5T8Gxq0i+2BLwl8syBs8cP5/fSW6vClV7QsEsvYSfVC3s9pokuRhrsNRlp0guzB2/Eck7dZrkLuFP1CmX15IsdP42zxi86nXZ8LhxjmRmePmPiYmJySh/ARLDgxTGjB1nAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAbCAYAAACqenW9AAAAo0lEQVR4XmNgGNrgKhD/AeL/QMyJJocV7GWAKCYKgBSSpHg6uiA2IMUAUSyBLoENzGJAdUIbED9FE4MDZPceAmI+IF6FJIYCQIJzgfgSELNCxeYB8T24CiiQZECYnIMmhwEiGCAKQREDovegSqOC6wyobgOxpyDxUQBI8hoafyWU/RFJHAxAkmFo/GwgZgTiY0jiDGJQSWTgBxX7gCY+CgYbAADqfCrdk3T3XwAAAABJRU5ErkJggg==>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAAAaCAYAAADi4p8jAAACF0lEQVR4Xu2Wv0tXURjGH9TUirZEqSXM1ZaQZidBI2pry79ACAeXJkuXZiUhWsRFHBx1F5EaJAWJhmgJF+0XFpmVvg/vOfbyes5Xv3q/w1fuBx6453nee84998e5BygpORf0iTa8eZ7YD/Lcxv/sJGrR0w5ZFu2EjOLxZ9Hf0N4TXT6srhEzyE/wk2jaeV+Qrk15kTgZDyfLrNkHRdEg+o78BHNezk9xHZqN+UAYhWYTPiiKLVET0hfdI3rkPN4Q1q06n/jzIy+g2SUfCO+h2aDzC6FbNBuO/+DoBXLh8TyG1t3zgfDAG4HUzYvQ59g1wQ7KFTR3EZavOFmdhfW7zuPNo7/k/MJ4Krpr2vPQAa8aL0Wlp5GiHVr/UfRatBba1fRxKn659nPooL3Ot8Rv9Y0PKhC/v4vO/xf8mvAOunJa/YQOOGTqPCPQmgEfVCD3tFaQ9s/MNWjnnlvQAV/6wBB/2NXA+t/eRH7iZybXKX+0x71+1V7UDWj9uPNJrq9F0bqoXzQHvTn8NI6lVbQJfRVTcHHhgKndBumE5h98UIEF6DlXfICjE9wWTZmsLRy/Eg2H4yyT0OWdnXCCfNUs3BfGnN8j/0t3QsY7GDPqG3SB4iKR4y20H27DKJ7j6x9CJ8INg51ol+iHafNaOky77uG++Ilpp17juoYTuhCO70Of8E2kt3l1iV1xG6Gv+jPjlZSUlJQUygHD46slRvzaGQAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAxCAYAAABnGvUlAAAHY0lEQVR4Xu3dd4gkRRTH8TJ7ZjFnFDNmMYCip4j5EBMm9B/Fw4wRQVERDBgwIBjRM2AWMXFGPDD7hxETiGdARcxZMdbPrue8fdc9M7szuzt3+/3AY6pe985MT89111RV96UEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEDaOCaA2dA+MQEA6M6VOf7J8XGO1cOyXtyeY3qOh3M8GZZheJbNsYyrf5WqffZjjvlcvlcn53gkVfvs8VS97pxs+VR9jopfS+7YHEeV3FklN56eTtV7GS11z31kjqsbYsccR+R4vcTLqfr3ve5/f9mdM2MCANDevjn2dnV/8J7LlXtRd0LA8PjP8HdXln5/vnel/j/nIHouxxchp+1Wg01uTIPRYJPR2h97pvrn/jTHpFLW8o/csvtd2f/tGqHezvMxAQBoTwfY1Vx9iitf4Mq96PYgjnpTc8zt6vHzXNyVd3HlkZooDba6bVwntRpsV6U5v8Gm51VcV5P35Q9c/WtXju9L9TNCron1aAIAunBHmvWga5TfvYRZKlW/vo93uVNz3JdjlRy3urxpen7ZOlXP5xsai+Z4P8dpOS4vuXNyvJVjs1IfFIek6sQu++dYqZQPy3FpKZuLcsxMVaPAbJNjqxybp+qz2CjHBm65xM/PTrLRcqm1z3Z2+QVTdcLd0OVOTFXDTL2r01xeOjXY1szxeRo6FKt9ptfYxOVOSNX34jaXGxRq5DZtozXYrkhDG2ztvqt+u0U9SPo+9MOKqfVetd8Wccu8v0P94lCvc15qDf96vtGlZdpGE5d5qs8fck3i3wIAOlCDwRoB/iAaD6j+hC+2fGlXtvw8oV4n5q3uTw5qPHzp6pu6cr8ckKqGpo9pqRoSuyHHAv+vWU/ve31XviUsk+NSNTdMjimP5vsce6VZT7gmfk5yfepun83MsYKrN62rsoa0pF2Dzee1zc+Wst9nck+OhUpZ2zdobs7xZkwGvsEWP4/zy2Pcbv1o+bmUNefQf3dHSq+tHwJ67hk53hmydCh7n/H91tF+Nu3W17K4nUbLNIdNDfjh9pi1e00AQAc6iNpVXPGAWlfXr32FXzYzx0uuHv9OvU8S8/5ko7C5WmpwWE6T4geN3w6V1evi60YNmBdDztTlTLtlEl/fa1f35ZtSq8FY12Czeru8Qg1cv0zR1CM0nnQxRdwWYz1o7RpsTdut76zlLKK4vN26ovxfMdlG0/NEWk+9n/qBonLTDxMta9dgM+pN/cHVO+n2fQIA0qwHTQ1DauhObNlaoW5U16/+hcMynbRecfX4d7rCUWI+1u8uObtSUUN7qi9RlmkujU6qamhoOHCkdkrVNjfFYq1Va/n3rbL1LFldvkutIdJty6Onqz0fiskifi4fhvqWrmzrvhDqJr5X81SOP0t5JA020Tw71Sen1rw63Yok/k2vdDXirjE5Ap3el75bZ5dyXLeuPjlVPU39HgJu+uzrDGddDb8b9ZLrO1hHz9VNg22PUO9kOOsCwISng6bmyBjN0TF2QLWrSDV/TQd2Y8tjgy0eiH3dTuox7+vXhJxfT8Oy1hjodkhntMVt9z1KdduqWyDIoeXRTpRap65xGLct1n1DT8t0da/1yDyTWj1Gakj+VsoS37fNPaprsL1aHpW3CyBOT9UcSPH7TMO7M1zdT1LvREOp/abv78ExmX2S442Q89utifjn1uRlanmM2y1+3V6Hg/Wcb5eyPa+G1+v43k2J79l7LCZS8/rKd9Ng0xC51fWjTHPoVNd3um64tOn1AAA1Hi2Pl+S41y8odouJVN0KZF5Xtwabcvu5fLcOiolUTfBeuZQ1x0ziJG7dauDOHH+UuhocdhKw3ixNqFYPmt5b3UlqLO2QY+1S9sOmnehE7G+xYhclqDFh+8/bPiZSdfuGSJ/Vqjm2iAu6cGBMpNZ+Em2rbOdytm9eK4/v5XiwlGXJHA+URzk8VXO3NLdOw+hqYGm+1HqpmiwvumhDNN9QDQO9Rl1DoC5n9P3TXLxueu2avquRLkLQv4te2b8B0UUe/l58g0j/Bqe7ul2gUPf5vxsTAIDRpZ63ugPyaFNjzdjr26O/mlS5ft5cdjw0XZDQi/HYZ+q1steNt5IQ38OmBpris1K3xq6oweYbM3H/R7qaF2NLN9c1l7myPBHqAIAxYL0aTSfL0VI3JGqPU2xBquZ89To0Nd5024/h9Mp1YvtLvaVjxe+jC3Nc65YZ9bCdFHJ2ixL1BhrrYTNx/3uTYgJjwm5xI/EKc82VBQBMANbg0HDot6k1RKsJ+PovlTQkZUOlcwoN7c7ONLSroUcNiarx+U2qrir8KbUa1BomO6WUtb7dwkIXbWg/i+b86W9F6/9SyhrytgtaMLiOjgkAANRo8xPDAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGDC+Bd0ns7PMcRF9wAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAbCAYAAABIpm7EAAAAiklEQVR4XmNgGAVDGnwH4k9AfBjKfwrEJ4D4PxCfhimCgTQgVgdiGwaIgn9IcspQMRTwB0pPZ4BIMiLJaUHFsAKQxC80sfVQcawAJHEMTewjVBwrAEl4YBGrRBMDg3AGTJNCkcSEgHgKkhzDZQZMDVuQxF4gS4AAKKQmo4mxMkA0gLAAmtwoGGoAAFUtI0LZEJOuAAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,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>

[image7]: <data:image/png;base64,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>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA0AAAAaCAYAAABsONZfAAAAkUlEQVR4XmNgGAVDFbgC8QYgzkOXwAZMgPg/EDtA+VVQPgxMQ2KDgS4DRIEQmjhIbDWU/RdZAgRAki/QBYHgHwNEzhyIo5ElHKAS7siCUPCIASKH7EwwAFmPIQgF1xggcpLoEg0MuDVdZMAtB5ZQRRO7B8RroXIg0IckBwagUAOFDsz9M5Dk7kPF4pHERsFwBQBRqyKsylFqowAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAxCAYAAABnGvUlAAAEbElEQVR4Xu3cOYhkRRgA4PK+b0EUBRVENBBBI0VRVAy8EDVfMNJE0MwLEVTESNFERUETwUAwMFCDVQMTTwwFDzzBG1YE7/rtLrv239c93bMz0zuz3wc//f6/unuqugZeUe91lwIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFvDvjUerXF0jTNTW7MjFzaRbTVOHx8f2tWb53JhizqqxvG5uCTbysbMyWO5AACb0b01Luryf7rj5sAyXA+vl0nbJePjI/5vXb6+33F8Qpc3Ub8vF6vDy+T1x9X4vsYLk+ZN57Px40E1riijscUi7pAa143zWLSHWMT3n10s6Kf9Dyxqo+dkrfoNAEuTT2Z/pzzEcyKezA3VE2XX98j5sjxT49lUy4uDOOmfU6b3OddzPo8rc2EJhvo9VHukO87tkV+caotarzm5K9Wy7bkAAJtJW4zN8kCNW8rw8/KC7cKUL9NZZdSX6NM0f44fp/U513M+j6tzYYZTa9yfiwN+Sfn2lGdD/e5rd48fr+9q+TWR75dqi1qvOYld4FnyawBg04mTWYvTUltv6KTXFmxP1/ikxpc7N6+Zj2t8OiOmibY2tu9SW3hr/Dg0ttDG9tr4OC7JLeqaXJii70M7/rmrZZeOH9/cqTpsaHztc4loC7Ze/5oHU747FpmTeG62mjlZq74DwNJdVXY9sd3UHUdbvhk877Dl14fDcmHAIrtQq3FBGfXttq7WX4o7o8bnXd7ksd3T5bOc38XtKT+le17zW41bu3zoc8zifd7JxSlWGltbsJ3X1ebpQ+jHlmOWeeZkqA+rmZOh9wGATePllOcTW+QnjiMWHrl9aMGW3zN/U++VlIc3cmEN5JvR4xuwfV//KpOxReSxhb52Y8pDzofMs8OW3yfyP1Ite6+MvvV5eW4YMLRTl/9myHO51pY1J0M1ANg08omsz/cpu95rFO39zzAMLdhaHt/giy8qHDNp/s+rKQ/rsWB7sYwu5TV31Lisy/ON6tHvfFN9P7azuzzGdmyNx8voW5ezrHbBdkCq9d5N+a8pz/L7h1w7uYwuaze5fS0sOicflMXmJP7X4jV5V3c9xgIAG+bDGg+VnRda4e0aX9X4tqv9VEb3qEWcVEaLhDj+osYP3fPifZ4vkxvMm7jsFxG7KO343HHbei3Y2s9TxN98qWuLcX1TRpflwlNlMrYY153j9jy2qLWxXdvVZ5lnwRbaHBzc5UdOmlcUu23T9PMQO3Ptb+W4uYw+k/h8YuxD95jtjkXn5Osy35zsKKM5iZ8liYV0ttKCFgD2akM/E7JRO2zrLRYcIRY5s6x0L9dGiMvZ8XtrW10sRkP8fEjzcHcMAAz4vcYNqZYXbLHTFjsmP6b6ni5+7uT9XNyD9btsW1XsZn6Uav0uMQAwp/1zgQ0Tl3P3Jm0XFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANgq/gWyWi3pOJDR6QAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAZCAYAAAAiwE4nAAAA9ElEQVR4Xu2QwQpBQRSGB29CWbFDESsbW3kHC1vKG9hZewk75QXkSSwoLCRJKf7pztHpOHONnTRf/TVz/vvdczEm8g88vgixR+5sfkUOyJnNBq+nPciXcvJG73xOySTzlSw4PpmYI2UxS3Ooy8mC0GT7pUV3rpj3v0lzCOq6siA0eYg02b3BzhbNIYJ/YQ1pIX135wslvoVVk8wXsuCQPEGmyNLdQxYeXU5s1mPPqWhfa5fzhR12tmhOMJrcRursLnvNCSZEln2I4+WTPELWYvbJScUnZ5GZSbqx6MjJiHkqJIWk4JwbskM2Llvk4rpIJPLjPAGys2+ClgBCkAAAAABJRU5ErkJggg==>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAZCAYAAAC2JufVAAABo0lEQVR4Xu2UvyuGURTHD5GkDAyUGBhkkQykpOQP8FtKMiixSSY2k1n5EySbUgaD1cAilEWvDCIGi2Lw4xz33te53+c8T1LK8Hzq29v5nPO8731vz71EOTl/RxXngPPBOeaUxO1M+jmX5J7dgl6giXNNbuaMUx11DRrIDVf6utbXpcWJdJY476qeJ/esZpRzpOoCuZlB5RI8c3bAnXBewFnIl7cZbh3qcVUHh4uPkOYEuBXvsxgie+aVYm8t4ME7/ENf9JFr9oKf8b4GvOaQkj8mFCj2C5xJVQth4ea7tUiu2Qletlt8N3jNE9mLuiDba6zdK7JGrtkOftj7KfCatC8+JdsHNsn1W7ERmCM30AF+zPsB8Jpbsn/8nGwvhJPdhQ1NeKd6wE97L9dFGmnv1BXZXu4+8Y3YQCrIDf7m9K2SPYOnLyBOLunALKdF1REyvAFu33uNvPx14GQGT6i4PXBy55WBkwORirUrUo+oOmw9zt2RuwIC9eRmypW78c5KJtucN/8pw3JVILucZZTMI+eevne3OW4nFvLjReXk5OT8Rz4BqmV9G9NR7qsAAAAASUVORK5CYII=>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABO0lEQVR4Xu2UTytFQRjGh5SkexcsKN9BUrqUbHwCwkayY2txNyytrG2trCQpKwtfwIKU8gFs7VjcUv4+j3nn9p7HOBfZqPOrp3PnN+975pw50w2h4j/Rj5whb8gF0lWcLmUHeUKekX2ZKzAS4gJ9Nh60cXe74msekHH7nfqYLC3kUNwl8ihOaSB3SM25iRAXunKuDSeWxG2ZL4Nbxpob8dm3mjE5LX7V/IB45Qipi8sutGEy7XNi0Ty35ydMhdjHByiwbROj4ufML4vvBHteVZK1ECfHxC+YnxVfxjHyojKRvhFf2bNinkf/O6wj9yo9vSHe8DenLjGJ3IrL9lLuijs17+EBGRI3jFyLI9r7Qe7pOZ53Y/4l0fm6Huc0566uwEGIH5JXFvLYKydI0433wucFUjZdXUVFxR/wDoHyU/O0IztrAAAAAElFTkSuQmCC>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAbCAYAAABFuB6DAAAAm0lEQVR4XmNgGAUDAr4C8VsgPgPEgkD8H4gvQWkWmCI3IHYGYiWoxAOYBBAcBeJ/MM4XKN3FAFGIDLqxiDH8xiL4EIsYWOA6FjGsCsOxiD1DFgB5CF1nNFSMA1nwOFTQB8pngvLD4CqgACR4C4gvQ9mgkJBCUQEFIEmQVXiBHwOm+7CCDwwQhVlALI4mhwJcGCC+DgBiRjS54QkAahspjFGixIQAAAAASUVORK5CYII=>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAaCAYAAABl03YlAAAAk0lEQVR4XmNgGFCgCMRM6IIw8BCI/0MxO5ocCljMAFGEF4AU/EQXRAcgRY3ogshAmQGiiAOI64B4PhAzoqgAgkUMEEUfGCAO14XyURSCBH4jC0DFNqALtCMLQMVewDiSUAEeuDTEGpDYRJhAGlQAGZRCxVRhAnZQAWQA4j9CE0NR1IHGhwNQxIIkQHgHmtwooCYAANGII3VrZN/xAAAAAElFTkSuQmCC>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAA+CAYAAACWTEfwAAACQUlEQVR4Xu3dMYoUQRQG4EoEURAMFY2M1EjEE6iJiIEn0EQw9QoGHkFlAwUDUUTQWFHMBDEw9wAGgqCBgqiv6Gm2pmh22ZnpnsL5Pvjp7lfDNmz007NdmxIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAe/cx8rQeAgDQjpdJYQMAaJrCBgDQuFUWtuOz49/Im8i+2TkAAEvIhe1ZPVxQX87KkqawAQAsKRe25/WwcGWHDLkTuVtcK2wAAEvKhe1FPVxCWdC2Io+LawAA9uht6gpWzuv5pYXln5W3CrkY+VCtAQBM6nrkcHHtq7+UDiW/BwCgEQ8jB9J2OTkV+RO5139gQ32KXKuHAADrUD9F+jGb1fNNciZyPnK5XgAAWIehYva7HgAAML2zkVupK2z5OLZ8n3ep2ybjWOTJ/DIAAENuRF7Vw5EcSd2Tu3zMDkZOby8vpf8Kd6oAAEzme+RkPRxRWXbuF+e9XOLqDW1329wWAOC/tujTol875GfxuVp5v0XvDQCwUaYsTfnfPH2JnIh8jeyfXwYAYMi3ejCiKcvhbvwtGgDQvFxWHtTDkbVUkB5FbtdDAICW3IwcrYcjuhS5ELlaL6xJS+URAIABubB9Tt1LEqvaWgQAgBXytioAQMO2UvfGak9hAwBoTFnQzlXXAAA04H1xrqwBADTKPmwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACswT/ufXgbkBf/aAAAAABJRU5ErkJggg==>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAZCAYAAADe1WXtAAAA3UlEQVR4XmNgGAV4gCQQTwViNnQJcoEFEP8D4hgg/o8mBwJ/0QWIASCDeqA0sqEgtjUQXwTilUB8BUmOIABp1kQXhIJ4Bog8N7oEPhDOgN3LIAAKkkggPg/Ex4F4P6o0JlAGYi8gPsEAMdQXiD1QVCDAb3QBXMAfiIsYIAaCXARiF6CoQAB2dAFCAGToGnRBSgHIUB90QUqAKQPuSCIbwCKJqgBk4Bt0QUoByNBmdEFKABMDxFAOdAlygCMQ+wFxEgMVwxNk0AcgvgfEpWhyZAOQobuA+Dq6xCgYxgAAjZQsewFbgncAAAAASUVORK5CYII=>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABPElEQVR4Xu2UsUoDQRCGR1FE0qmQQnwFCSk0SrBJYW1QmxAEC20VtIilvoHgA1ipnYVY+ArGF/ApVBAVlfiPOye7f3b1tBPug59jvp2920uGEyn4T5SQK6SHXCMD4XKSO+QAmUKGkBpyE3R4TIp7wKjV41YPfnWk0T7OdtDh8Yickesiz+Ri6I07yDGySWt9aPMquT3zP/HGIsWCuBvWya+ZHyPPvLJIsSXuhlXyK+ZnyTMvyBFyj5yK2zMfdBj74hanyS+Zb5FnHpBFr56RxC+xYQsV8svmG+TzoPv0AAHZfzRHvm1eR/87hlmI29c3SCMm/zJ12WF2yUcfpKg8JHdp3kcHpOzV6xJ/a3W35D6JnV7rplfrJyl2Uq4vIi7gBHm3qzbq2DPnyA65CXH9Ot56fZL838mCgoJf8AEEQE/OfP22wQAAAABJRU5ErkJggg==>

[image18]: <data:image/png;base64,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>

[image19]: <data:image/png;base64,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>

[image20]: <data:image/png;base64,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>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABCCAYAAADqrIpKAAADaElEQVR4Xu3dO4hcVRgH8BOiKFopERFTBYVU4gNFJY0WvlAUBMUHGLBRG0FRgrXGZ2chGB+ghQiKnY2vRhEkdpY+QTCF6SJY+PqOcy777dmZndmZ2U2Y/H7wcc75nzN32487O/eWAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMD87u6DBe3vAwCA08knUf+2qo6nvXkc6oMl2Bd1UR8CAKy6B8takzY4e0y2FXuibuzDJfmuDwAAVt2kxmxSPotFPjuLL/sAAGCVTWquHkjzeubZNuZsWH86Zq/3Rxnll0T93u313irrr/Fzmlfjrg8AsLKmNT/vd+vh/IVpXj2X5v01f2rjK1EflY37vd1l8wawXwMArLRJzc/Lbez3xzVSN6es6j8zmJSPM+7vTFoDAKy0P6Pe7cPwYxv75iivD0Ydizqasqr/zO1tHPIzho0J6o8eLmjzj6OeSHtVf30AgJVXG6An0/qHND+nrP0/2/1RH6S9alzzlLP6GI6/ou5N+Ym17f+zp9N6cFkbp10fAOC0sSvqw6jX+43mvj5o7uyDsrGhuibN70nzwa99EG4oG/9PrjqrjBpHAAAW9F4fbGJvtx6atG+jbskbZWMDBwDAnOqdsOFrzc1c2gfhuqjDfRg+6wMAgJ1Qn0n2TRk95wwAgFNM/npvka/66q88c70T9XbUm1FH0jkAALbg8ag30nqRhg0AgG3QN2j9eitemlIAAMyhNmhnpnl1eVpfFXVFW9fnmA05AAA75O8yeqL/gX6jrG/MLo46v80fTTkAANvsrj4I37fxhZS92kZfbQIA7KDn+yCp79msd96yK4uvQwEATllfRz0WdV6/cZLdFHVbqmnq66luLbOfBwBgTvXl7/X5btUsd/3y+c+j7kh7AABsg60+7DefqS90P5rWAAAs2aGoF9N6loYtnz8edXVaAwCwZNdGPdzmj0Q9k/bObeOJqF9SPpyvcoN3MOq1Nn8q5QAALMFDfdDsj9rdh2Xy+aGBm+VOHQAAC/qnjO6uVb/ljU180cZj61IAALbFrjZevy6dbk/U3j4EAODk+6qNw9sdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqv8AqqqR6kZZVe0AAAAASUVORK5CYII=>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAAAaCAYAAAAHfFpPAAACFklEQVR4Xu2XP2gUQRTGn2ihtSiIqCHGgGhhtBRJE2xCVFSMIBaKGEIK7RSE/CGNRRAC+aOFCimsEhCslJBCUNRAwMZ0ATttgoixMBH9nm8OJt/Ozu1erojc/OBHbr/3ZnZnb/d2I5JIJBKbkxb4Hv6Bs1SLof3D8Dq8Ai/Dbuc+r29T0y62kArHaDuP/WJ9eWq97hzgoA7owfZS9gu+o4zpgw9gG2yFB2EzvAMfeX115y1cgju4UAO7xU6A/vV55fIYLzkA2+BPDqtxCD6HF7hQhRfwO9zDhRL0S3ihTyWcV2ONg2qswhvu8xz84tWK8lBsx3rvlkVPfGih4xLOY0zAIQ5j6A4mve2dLtPLqBYGxcZ3Uh7jtYQXOiqW7+VChNA8udyX7IATLjtFeVl6xOa5yoUAzyR7HMqYlPsyRiQ8Ty7a/ImyKZdvlC6xee5yIUDeb8BjCed5aO8HDmPogHOBrMxOmZti469xIcJJsTG1PAV8tFev6kJckuzkW112hvIiDIiNPc2FgujY85T9gMuU3aPtCmfF5rjFhTwWxQbo62OF3/CJt10EfdnQp8gRLpREv23/8bVF7PiavOy2y756WQV9CvF6omjzPHzjPusijq7riDMDv0n2st0IH+EKnBY7po715X/oy9dhDsXeX3TMcS7koc18/xdlF9zO4f/ERcne/w3FgjT4Cfgs9t9SIpFIJBqNv6mHezjMPIhlAAAAAElFTkSuQmCC>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAZCAYAAACPQVaOAAACP0lEQVR4Xu2WTYhOYRTH/0QJk3wsFCkfmzFlUJOPhWjIwkZmp+wnM5JmFDsLM0ulZEMRsRWlIUpNslE20rCWZopMEfk2/9O5D+ee9733Pve9bw11f/Wr+5xz7nPfc9/7PPcCNTWzzUa62gcdK33gf+QdPUvP0RcuF1hLf/tgVeb4QAHz6DcfTLhNL9L10Hm76T262dT00Z9m/BY63zjdTw/SaWijy01dJfZAJ5Q7HMNLaH2wGY+RrhFvpCqAKfrUjE/SjuR4IfRmdtGbfyoqcAT6IwZ9IpIPyG72ET1Br9MhlwvIuVIX2E17zVjImj+a09BJDvlESfKafYjiZTGG9DodoQvM+BkqPL4X6C+63SdaJK/ZByhudhvS59tjWdv+sY/iFv1C1/lERfKavU+PQzecq9C6fluQcB66Cclcm0w8a95cjkFP3OkTbSCv2Tv0jBnL4ym1e00si+d0mRlfgd60LSaWyzD0YrLdt4u8ZpshtUX1PfSaGU/SU8nxaxQvjRSHoRcc8IkWyGt2vg8grlmbl8Z8vSzJ0uyCTjTqEyXIanYNNH7XxYuanaBLzHgHGus/uXEpNtCv9LJPRJDVrGyEEt/n4hL74WIBaeySi3Wicf5KzQaWIv2Cj+EzGn9MQOJzzTi82+171CKvxGb4+Vt6jKvwEbpxyIYhvqHvod/BAWlUdtDv+Pv4LjZ5yyu6yAcTntCjyXHpDepfpOibXP5NWWpbfcKzih6ItF1fVrPGCuhnWYyyIdTU1NTUtJMZsaWLNpcg6PoAAAAASUVORK5CYII=>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAZCAYAAACPQVaOAAACcUlEQVR4Xu2WS+hNURTGl1JEyCMpBkgJJZQ84y/KwETMlJmJ1whhYoSBgVJkgJRiICETJVKUSCkhmSnlEVHyzuv77L3/rfP9z733HPvmUedXX/esb+1z7l77dY5ZQ8PfZio0Tk1hjBr/I6+g3dB+6IHkEhOgH2rm0k+NNpy20IHP0HbJJSZBtyy0uyw5shr65uKX0BfoGrQcWgm9sXD/SNcuiyUWHsgRrgLbDpWYnfQsjn5ihsTkOXTbxdugIfF6ENQfmgad6m2RwVoLHdikiTYssnDPFeel0Z/sPMbrXUw4IDddzDZXXdwDLXUx0QGqzU4LD1mliQpwtHnvPud9iF6a7dEx5q/nUvQTF624T/dAA118xzKW70HoOzRXE5mwAF/ELokTx63oz5HYX3PZn3RxZc5Bn6CJmsiEs3zfwgD6w+28lRd7yPr6Byxsg7fQdOdru0pstnDjfE1ksgY6DL2ALkiOp2lZZ1kY/bGaEO5BI1zMFcH9PtN5bdlq4Y943Hcbnqp8dppdnp5lxXIb0eeKaMVs6ISLn0E74vUTq/d6/DUj/MONmshgi4VnsmOk1Z49ZuW+x+dZmLbnlqxNeoXs1UQHOOpfxVto4VmpYwvidafTWHkIDXPxPOvb/r3EteBXDr+CjmqiBamoHueti95T5zHWV9s76LV4CRZ2RLwp1uViE8Ot+IJvBZfRdfFYBDs1wHmcRb8C0pIc7zwPT/QytNjfWsY5nLXQicfx96MVC03ctTATZyy0W1ZM9/IIGqxm5Aa0IV7XPqD+RTp9k3M2udVmaULhO21FRXX7y+qPM8rCZ1kV8UBoaGhoaOgmPwFG+podO83xqwAAAABJRU5ErkJggg==>

[image25]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAZCAYAAACPQVaOAAACT0lEQVR4Xu2WT4hNYRjGX2UhkgZJsTDTpFBCyb9iJmqKjWZ2iqxM/q5GsbHCUilWSClWU+yU1NQokUlNkqwRoiGRP2E8T993pvc851z3nHtuDXV+9XTP+7zf+e55z/fvmNXUTDcroaVqCovV+B95D52GzkFPJZfQCU2qWZUZahTkEzSgJuiGHlp40LuSI7znl4vfQT+gUagP2g19sHD/AteuEr0WOuQbLsughXu12G3RT1gjMXkDPXLxcWhuvJ4NzYRWQTemWlRgr4UHOKKJEnA08oqld1A8jtoDF7PNiIt7oO0uJvqCSnPSQif9mijJx/irxS6KHn89d6KfcNvS6/QMNMvFj63C9L0A/YY2aqIF9kH747UWeyp6ylVL+xsk9tec9tddXJib0DeoSxMV4KaUoMXeip5y0bL+eQubEPtb7XxtV4ijFm7crIkKvLX0zq3FcjfNe1gWRn+JJoQn0HwXc0Zwva913l8ZsuxDtcJO6Jh42i93z7xiuYzoc5dtxHromotfQyfi9QsreTzusfCHhzVRkK9qWLbYRmv2iuX7Hp9nYdqeS7I0Wy10dFYTTbgnGrPQz7MYky3Ra7YbK+xjnos3Wbb9F4lLwa+c79BlTRRkuWVHltDTo+0zNCFeAgu7JN4Ka3OxCR2WPuCLkoziAfE5ij9dnEzJZc7z8EjMQ4ttaRq3Ax4ZryxsHC9j7Bm3MBLDFh56Rzo9xXNojpqR+9CheF16g/oXafZNztHkUlunCYVn2q6CaseX1bSy0MJnWRFxQ6ipqampaSd/ADDekdtPkK7rAAAAAElFTkSuQmCC>

[image26]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAbCAYAAACTHcTmAAABA0lEQVR4Xu2UvQ4BQRDHJ4JEKChQegNRCO+gEK3X0anohMIDqCU60Sv1Co9AIeLzP9ndZDLHfYXK/ZJfMjtzO7e3t3dECb+mD5chDU0GVuHTWoEFmIdl2IYHW4sMT3ropCBy0yaZSSNdEERuyvvFk4oil4ZzMT6KOBRuPyU7WFO5SLim2ti0yDQYilzd5mKzItOAj5EjBWdiPIU5Md6L+C0n8q6Kz25HjC8iZvT1HoL2jz+AtRiXyP88U5ZMw60uCLjOx8vFgS9yTKbY1QXQI1PTj34ns1oPC3gj8xj67iznr/AMG3aO4+MK48JfnO9+xmEAJzbmo/gV+IXxP2Cj8gl/zQvXUUkKyBnCeQAAAABJRU5ErkJggg==>

[image27]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD8AAAAaCAYAAAAAPoRaAAACiklEQVR4Xu2WS8hNURTHlyR5pgzFSCSlGEkkAwMUSsmMKWbEiBRFkYwMTAw+r1KSpJRkYERRDJSZR5L3+/1c/9Za7rr/75xzzzH99q9Wd5/122ffffY5+yFSKBRGMsc13mv8SfHM3SiN5+Rea6x0/5LcR8+DV+RQN9hG7m5ywWWNL9Krc7hfD+On9Oq+1VjSr5uJG6u4JuYms1B2irl1LJRzYm4aC2W0xj1OVhD9usMisUXjqFg9tNsJvGHceJuF0zQwa8UcBoG5KuYWs1CecqKCKRonpfn/wQWN79Jcp5atYjeuZuHAfeOkM1fMH6P8GI3f7jaSm66xh3JVHNSYKTad6h7skf/Cv8iiLZjjdY1j7sDtZeGMFfN4yxmsDcvd7SOHQWnDD/+9KNX9W6AxX2OCmMdL7AxuRKzRWCW2oK3wuOFu3L/aw4F/kK7naOwQe2twp5PboLEwXTcRD7w9lTMP/feAmMf07QxuvC/2JzliMav64wzXiTIWH5RvJvc5lZuYqHHKy3jDaGdGT8v5VMYXMqiPlcR8j+2Lgaub70F++M0a88hhCoAhsU+0DXibs9I12tnk5UnS/4nDxfbcCSwSdaO2SMzxnGXyw7/LQvrdrSwGEPM9QBsnvPw15TEQcNjuOpM7x1wRc+NZENEG9nUsgFXuMeUHwX3C9RONXdK//hxy13m+x5z8n/09E/Wus5Cew7bVlqkaZykX7WDfz/zyfGeOiN24noXY6HZ9+CqaXBX4cj5pXKI8DkXcThzOcDxvzRmNDxpvxM7gOAtjBAEWJBwqkINDHcwxbIN14Py/m5MOOreMkzVgW40+oQ/RJ7BfY3a6xgBFH/EsONsvTb5QKBQKhUJh5PAX5AHT5+DhnpEAAAAASUVORK5CYII=>

[image28]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAA9CAYAAAAQ2DVeAAAFXklEQVR4Xu3dW6huVRUA4JmWaVZe0kKFihShEgsSCUw8JSKhBaUmPqkIhYaCqA8KPemDZRmEj2J0EUsrRDGCAqNAM8tMJPGCIV6g1LTS7mpzsOZsjz332v/Oc/6tZ+P3wWDNMdbcc+3HwbrMvxQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXp7Davyjxks1/tNqj7Y84o+tFud6Lfw55Ue1Ws+vanl4PNXnRP3vY3E77VJWrjUGAMCW9qGytqmJ/PiZ2qL82iHv1mua7irz9R3xlxr3DLXnhxwAYMuJu2i/HmpzjVSuHdLyd6XaMWmcfbusXe+8GnvO1HdUrLfPUPvpkAMAbDnR5OyV8t1abZRrt7f8lJbHI9JFYm5/dBoOKtMa16faMuT/8W9pDACwpY3NWTxC/NlQC33eu1N+dRuvJ5qy8LUat7bxl9txvO4y5DUfTmMAgC3r3LK2cYp8j6EWov6WstKE/bvGb2s8878Za/W1P9jGP5w5Nyfeq/vkOvHeNC/7cI3LU75fO366HX/VTwAAbCXRNF05U5sT9XznrT8WfX2qjc5O45j7ujY+seXLNPdxQW8831mm68URAGC7RTOz91isDh8LSzQ2TafN1Lqon5nyr5aVrUDmxN20bSnP675Y48KUL8P4f39uqP0mjQGAJYpHbhGxBcQdNb63+vSmiv3BxiZgsxxc4zM1dq3xVKpfUOOzKX81/XjIjxjynVk0wm8biwDAcuxf1jZNv6/x/aG2WcZrb5Z8nWfTeGyS2D43lOkO5u7jCQBgx801bGGuthleqevk96/6S/2xCSwAwE5vUcN2Ro2j2/jYGk/XOLKdv7PGdWV6V6qLeRH93aa+bh73/KEy7fSf67+s8YMyXWffVttozfgyMY7vqPGvdH7ON2t8YCwCAOzsFjVst7bxJ8r0/lds69DfU7qlHT9f47Y2DmNjFr44Uxvz79Y4daY+juOds5DXfKzGIynPW1usp99xi6Zx0aa03xriGzWuKRvvjwYAsDSLGraPtvEJ+UTzphq/KNO83PBE/oYy/TRSXzfufHXjtXo+1vMu+hutGRu4xteXXXw8scihafyTdlz2rv3xf76WAwBYokUNWzc2bLHX1lfa+CNl9btg22r8tUzbUZzeavGblt14rZ6vVw/bysqavZ7XfLCsbN4a4tHqIje348Vl5aef7m7H0ZcWBADAKyJ2tc/N0YFDHs4q03YYXewPNr5jlv9mvXG4KY2fKyvn447d+D5c1vM3pnH3ZFm9gewDaTyKuV00fX2vsnFNAIAtLx6X9keL8cJ/9rE0fl8ad++v8Z42Pqasvlt2XI0DUt5ttOb/Ix7hjuLR6mVlfkNdAABYV9wJ7HcunyjTndC+0fA/a7y9xp/SnPOnP1v1N+HGlue7l+GFVn/rUA99jT+MJwAAWG18THvUTC3yQ1J+f1n92DfsNeThUzXuLStf3XZXlGnN+DF5AAA2MDZnsRXJz4dazMlfyMadtPx3J6dxFh9wxPt79w31N5e11wUAYMY5ZW3jFPkeM7Ur23iXGhe1Wpf3q8ti77rYUy/P7V/7jtcFAGBGNE0fn6mN4lchftfGXyjTo8w+b27+qM/pXwHHhxnXtzEAAAuMzdYlM7XwozLV895zke+X8kX6mt8ZcgAANjA2TpHH9iOjS8t0LjYz7iLvd93mxE+NdTH360MOAMAGditrG6cx76L5Gs+N+Sifj/HubRz76m30twAAvEz7jIXqpLEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8Kr6L+zzjW1s9CpnAAAAAElFTkSuQmCC>

[image29]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADEAAAAZCAYAAACYY8ZHAAAB80lEQVR4Xu2WTSgFURTHjwillJKSpZBsJEWRlKyELFmzUVYWykoWEhYsZGFFsrDwShY2LFjZi0iR5KMUC/nK1/l37+i8Y+a9mTeP3mJ+9e/dc/537rtz75k7QxQRIenUCRdqdSJTqGG92N93Vn28/cMJq0cn/4s11hfrlTWiPACv3LaLWM+sD9Ywq521aPvc2D4JwQXoPKiNEGC8QhW/idjJecWl9hc7FYgmMgNNayMgLWTG2Ra5e5ursnGxjSU6HqUQZVRBpgRWteGTHDITmhK5J5vTuyORMcbwVUbJwGphBXe1kQKYoJ40yqvPtttYA8pLK/msM9YhK1t5ycCKHrA+WVnKA7ixFdadyI2zukWcNkpYD6wtbSQAq7zAumVtKM+LXNaViKvJlOKOyAUGDyK2dkkbAUF9Y9XddkOC94UDnh+nBAtYR8LzhXPCTGgjRXD2Y7xrbQgmWR0ivqD4HTwV7YT0kvmzMO+MZYpfUdBM7g+3A567S5VD33kRz4q2K0NkLurSRgo4k20VuX6bk/UuwZtao29iTrR/Mcaq08kQxFh7KvdIZlJ5Kg9myByxmn3Wpoh9l1O6WCcz6XP7i+8itxtAGXlNDv3lg42jOiM51glFJZnTUX7CuFJG5lTwo0Z7TcaBz4sGn8LLJyIiIuJv+QZxRHIKh/nZZQAAAABJRU5ErkJggg==>

[image30]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADEAAAAZCAYAAACYY8ZHAAAB/UlEQVR4Xu2Wv0scQRTHHyoqKIogQlAriT9IIyIoBNJIQBCVgE2E2NkErOyEQEihghZaaGMlBP8AEUmjhahgnx9EEgQxIUUgNklUDPH7mLnz7de9u13vlCv2A1923vu+nZvZnZ05kYQEyyAnQujkRLHwCDrz10uoO2inOYSecfI+OIVeQHVQLTQC/QpUiPyHWnxb6/5C/6BJ6Cm04mt++Jqs6A1a/JKNPND+WE2BCpfLFD/wV31TsXgsrqM5Nm6B9jMDLUN95Cn1kn0SypTksYweQufQGhsx4AGFwTU2LpOIyygX+rR0He+wEQEeYBgX0Khv69saJ6+gVEJH0EeolLxM6CR0V/kA7YvbffTpMlr3Fvppcm+gYRMXjAZxO847NjKgg6sw8abP5aIc+m7iDugPtG1ysWkT92pX2YhJu7hJvGKD0DeWokauJ14FfTJeJJ6I62CajYjwsisR11+2gcxCAyY+htZN/MW0s/Jc3I/lc2boj2kf+i2lqPa5XZOzaO0J5bR+ycQLph3KhLibhti4BfoEf1OuX1z/qd2I0ZOa4UksmvYNXkNdnMyDZugr5fTk1b8VYcxL+IF4AG2YOPJyKhRj4p7kN3/dC9ppdBllGpzubvbDfm+8ouIzJ4hWcbvjFhtMo7hdIYp6/T1Fh/696IkoPXwSEhIS7pYr4ExuQFn9rvsAAAAASUVORK5CYII=>

[image31]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADEAAAAZCAYAAACYY8ZHAAAB10lEQVR4Xu2WzytFQRTHTxFKKSUlsSAkG6QoZSMrIVn4tVM2JAsLZeVHSZFYEFkp+QNkwYKFHWsRKSXJQrHyK+J7monzjvfum/tceov7qU9v5pyZeTP3ztx7iUJCJC06EIVKHUgWKuCz/X2DNZHpL85huw7+Bx9wCvbBXtgFO60Fok2xLWfDJ/gOR2ATXLNtbm0bT7gDNx7QiQQpJDNeLDnPcFki63n2l++UL+rJDDSrEz4ZhPOwCpaSudpFcBSu2jY55L0IZox+sY1K4Avc1AlHdnUApMJHFdOTlnVu77SN4sFX6x4e6EQC8MHVvMIeW26E/SoXKBnwEp7AFJVzYRlO6KCFr/4GvBOxSdgm6oGRCx/gjk44oLeNF2nwRtTLyWzDfRHzTRmZW7uuE47Mkb9FyG2XRd99M+GpyDnRQGaAaZ3wCY9xpIMxmIHNon4Ft0T9QpQ96Sbzx0G9M3gsnlw8+Nxdqxj3XRL1BVGOyhCZTq068Qv4cPKYwzoRBX5Ta/QiFkX5B+OwWgcDYIXMRPjTwws+N/yI1RzCbVF33k5B0kFmEV4XiLdRrMmlU+TBPha5pOJMBxT82cJPxz2d0OSTeSq4WGf7JB38eVHrKL98QkJCQv6WTzwrZWtQY7PYAAAAAElFTkSuQmCC>

[image32]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAZCAYAAACPQVaOAAACQElEQVR4Xu2Xz0sVURTHv6GLUEQokaAWSkZUIBZERVCBRYsgIlf9CQkug1biIt0EgaArkSjQVZA7IwShRShBINGvVQsRAyXDH0Gh5jmcua/zzsx17ntvSB/MB768Od9z586cuT9mHpCTs9ecJh2zpuGINaqRZdIj0hPSR5NztJL+WvN/U0v6Y01FG2kWcqNTJsd0kbZUvATp7w3pJukOaQVy/mHVzssNSONum6iAL5A+nZK4iuJch4mZ76R3Kn5AaoiO6yAP8wxpvNAikMuQiz22iQpYRbwAB/v3jcejNqNibjOt4mukThUzvv6DOEH6jTKeVgK+YpshPv9qXke+YxLF67SfdFDF7xE4fdNogqwHXh/l4iu2F8n+UxT7F0xsp/2YijOBn+Q30idSjcml4St2Asn+MOL+IOShc1/tyrftMoOn20/SK5tIwVcsz5Yknwtj/6hNGD6QDqmYZwSv97PKK5mTkE6e2UQgvmJ5P0jyhyA+77I+zpOeq3iR9DA6nicdULkgrkAuOmATJeIr1rdmR5Hsa3SeC7PtX5rYyz3IyVm9c33Futdc2m5s+UxqVPElxNtvmDhGD+Sk2zZRIb5iGfbvGm+d9MN4Di5sxHinEO9/12L7SOesmRG/EL8ZB4/ipordlGxRnmbbGhG2/+BpnBVrkI2DNwzWAmTEjutGxBxkJF5Abvp6cbrAV1K9NSPe4t+yK2uD2m/wv57d4NHkr77UGcrvtFuBuhidU7XwZyF/loWIN4ScnJycnCzZATHDjwalzYUlAAAAAElFTkSuQmCC>

[image33]: <data:image/png;base64,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>

[image34]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIEAAAAaCAYAAACQAT/QAAADnUlEQVR4Xu2ZWahNURjHP7OQUOKFvOHRA3nyQsiQkgyhLimkkCGKUniQJIQXQ8QDN8kQEg+GMmWeypAH8xDKPIXv71vr3O98Z+2z9+nqnnNP61f/7vr+31777OHba6+1L1EkEolEIpFIHYdZf0pQNXPZGoatJNfgMau7yXmmsl6wfrFWmVzFgpMaG/DsDe8V8KqBi5StyH+zBqsY2w5VMdjHeq7i3ax3Kq5IOpGMBJqmJCd43fgAT0C1Mo+Si2AFFeZGBDzEzQOeLZaK4girifHmkhz4KOO3ZK01XjVRrAjg37Umid/Ntde52ALvoTUriTnWYN5T+GQ6sLpYs4pIK4KT1iTxN7j2Dxdb4IV8zzjWUtYuF+M6L2PNzm1B1IK1nLXJ5S0TWDdZJ1gDWJfy06WTdtDVSloRHLImiX9MtUP9k3zPYtY3km0wkRzofNxQeMNYG503xnl+9AEXWNNUvJn1SsUl04zkR9JmyeUCT0uSdrJ2sLaztrG2sFr965WNpCLwc6T9NkHiP1DtUP8kX4ObiG1mGh+efZXYY0HcU8WgXkWwiGSnw22CqaX0k2nMJBUBgH/AmiT+WdUO9U/yNTUU3gZeaOV2SsWfnXeN5LVQbz5S+GA8xXKNnbQiOG5NEh8jDsB3gVD/LEUwicLbwMPrwHpnjOfvm9fI/HRppB1wsVxDsLpEtZdumUgrgqTVASZ2wL/DLfDwjaEYEym5b1oRdFbtHpQ8Qc0EloDoXGw+gDwqH+9dVH5vlXvNmkXyjsRfD/aHyc851lPlf2UtZP2kwmVqOShWBCgAm+tnvK4m9sCbb01DDSX3DRWBfwX52BLyMoGbi841xtfYnesYReHRvv6C5ovgA6uPaw+huslVOcHIgePWT5YHH9WQa608DMFXVAzwxO9RMeZW9pqFQJFgOzyInjbOm6I8AO+2iVeqGEvILL+ZYzTrC8m3gbdOOLmkIcV6iLFs8SxhXXW+x09cMGPF6gMgfqJk99uQ4FxfkhQojgV/31Ddut0ziOQ4D5Jcr/P56RzY332SpxXbt8tPF/CJ9Yzkt/E/h9OsG64NDzlcw8kk19Afo/8cjeXlDJLfgpCzXy3/K/ZmIR7P6uja/knR22GJhQpfo3y7n0gjAjcPN1XHAJ+THwX8vqy9Ab+WtUD591Q7UuFgqMeQf5Rk2GurcndYt0i+oE0nGVLBepICwbDX33kA+/lO+XOGSCQSiUQikUgkEomUhb8EfTU9Fvc2cwAAAABJRU5ErkJggg==>

[image35]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIsAAAAaCAYAAACHI68ZAAAEXElEQVR4Xu2ZW6hWRRTHV5kRFVGJKNH9RSvwQbS3hCgisigiCknxJD0UgYpCFklK9VAREVa+FEk3iKgo7UIo0eUhKbMS7V7SPaP7jW5U69fMOmft9c3m+45J5/NzfvDnzPrPfHP2nj17blukUqlUKpVKZfdhnervUWjQeFV1kmpf1eGq5arvGiUSJ6vektQG94c8z52SynykOjLkGQtUn6v+VF0f8voabuz8ghc7xtSCt7uzj3S+DL83SiSWqP5y8SVSbgvKnOZiypzuYnhI9ZmL71N94+K+5VBJI4tnb0k3+Vrwgbdl0HhbdbvqBtVhIc+gPY4reH5UuDZ7njMLHjGdNHqxU/UdT6j2Ct5iSRd/dvAZpm8O3iDwXDQC50jnA4ffpOmTfsPFBv4ROX1LjiN470Wz31gUDeVbKd/QwapJ0RwAunWWZ6TcHtuls7NscLGBvyqnmeJKdeGVfOMCSWupe3PMs1ihWjhcQmS86hpJoyT5kTmqLar1qlmql5rZO0e3Cx80NktaaDLKfimpE3hY7JbaY5t0dpa1Ljbwn3LpUl1tvnGF6ldJZZj6Tsk+Dx7vDNVt2TsvezaawUbVxS5erdrh4p1inKR/tClm9AHTJL1ZJd2julu1RnWXpB3JHelnXeEheLh/vxtqe5Cvy4hv67xHRrKHwX/XpUt1tfkeHjZlLg0+XpzC4rUQT3Ex/OfOskxSxbNjxh7EA5La4IAcs3MpPcit0vRJP+piA/8Fly7V1eZ7hqRcBq+0m33WxT9nj2MCpqNdwo9SvqA9iZWS2oB1ArStWd6Xzs7ytIsNfBvlmO5KdfXSWeZKuQwe01D0ng+ePVvTWc3s0dPLRY8Vx6huHKW6Ubrfm7J3ao6vynFkNLsh63i2xojg+XOcEhdK+2+7dZaJLn20tC+0e4atMRW0rVesYU9QPSjpLZmgelH1uDQbihPRxySdXXztfKvDLtTS84dL/L/wvxmaPSwGY0MScyYVPX9Gxf3H350YvMkhNvCWRjMwJO2/LXUWm/osjpS8nmGopIKh4HvIvyyn6RD+H5I+KKdXqq7OabZ3fnt6iIz87hPnjwW3SjqdNexEd43z4Atp7pLsobNdNehMePs5j6H/FRcDIwjrIoP1YS8Pjs5EOV5qY//sXeQ8wGNN5ePrXMzWupf/2eBc1S+SzlYYARA32DZMeW+m6g8Xk+e3a8dLWpFzlP2B8+FKKdc/FrCt5Vp+yH9LZ0/wlaQdxJOSyh3bzP4Xpi7yGFVpU0bdErTvO5Lefsof2Mzu4CfVp6qPJX1T4uVjN0YajzwWsfMkXSMeL6J9RmDHZ58oEHnxFHmX4x/wdGluO8mzD2dc7MM5zZH39pw25kvqmORVBhTfWWZI86MbeUe5tH1G4LDoQ0nfYIBp6PKcpty4nK4MEAxzDMUcWDEF2dTFNMbOgDQeuxbWM8zNdBKGa8owmlAH5d6UxPc5fjnHlUqlUqlUKpVKpVKp9BH/ANJfa5zTUqxsAAAAAElFTkSuQmCC>