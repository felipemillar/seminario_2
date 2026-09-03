# **Arquitectura del Motor de Ejecución de MetaTrader 5: Manual Técnico de Referencia para Ingeniería de Sistemas de Trading**

## **1\. El Desacoplamiento de Entidades: Modelo Order → Deal → Position**

El diseño del motor de trading de MetaTrader 5 se rige por la separación estricta de las fases de intención, ejecución física y exposición de riesgo.1 A diferencia de los sistemas tradicionales donde una orden y una posición abierta se consideran la misma entidad, MetaTrader 5 implementa una arquitectura desacoplada que permite operar con precisión en mercados centralizados y extrabursátiles.1

   
       │ (OrderSend / OrderSendAsync)  
       ▼  
 ┌──────────┐      (Disparada / Llenada)      ┌─────────┐  
 │  ORDER   │ ──────────────────────────────\> │  DEAL   │ (Registro histórico  
 │ (Intento)│                                 │ (Física)│  de intercambio)  
 └────┬─────┘                                 └────┬────┘  
      │ (Activación de Pendiente)                  │ (Modifica volumen/precio)  
      ▼                                            ▼  
 ┌──────────┐                                 ┌─────────┐  
 │  ORDER   │                                 │POSITION │ (Riesgo neto de  
 │ (Active) │                                 │ (Riesgo)│  mercado activo)  
 └──────────┘                                 └─────────┘

### **La Orden (Order)**

La orden representa la fase de intención.2 Consiste en una instrucción formal enviada por el terminal del cliente hacia el servidor del broker para realizar una operación de compra o de venta sobre un instrumento financiero.2 Las órdenes no alteran la exposición neta del mercado ni el balance de la cuenta directamente; representan un estado transitorio.2 Estas residen en la base de datos de órdenes activas de la terminal hasta que son ejecutadas, canceladas, rechazadas o expiran.2

### **La Transacción (Deal)**

La transacción representa la fase de ejecución física.1 Es el registro histórico e inmutable del intercambio comercial.3 Un *deal* se genera de manera exclusiva en el servidor cuando una orden es emparejada con éxito contra la liquidez de contrapartida disponible en el mercado o en el libro de órdenes del broker.1 Una única orden de volumen elevado puede desglosarse en múltiples *deals* consecutivos si se ejecuta por partes debido a restricciones de liquidez en diferentes niveles de precios.1 Los *deals* son los únicos elementos que afectan el balance contable de la cuenta de trading, registrando tarifas, comisiones y swaps.1

### **La Posición (Position)**

La posición representa la fase de exposición de riesgo.2 Es la acumulación neta de todos los *deals* ejecutados sobre un símbolo específico.1 Mientras que las órdenes y transacciones son elementos puntuales en el tiempo, la posición posee una naturaleza persistente y es la entidad sobre la cual el motor de MT5 calcula continuamente los beneficios o pérdidas latentes (*floating profit/loss*) en base al precio actual del mercado.2

### **El Mecanismo de Vinculación: POSITION\_IDENTIFIER**

La trazabilidad e integridad de los datos de trading a lo largo del ciclo de vida de una operación se garantiza mediante el uso de identificadores unívocos que vinculan órdenes, transacciones y posiciones.6 El mecanismo central se detalla en la siguiente tabla de propiedades de integración de datos:

| Propiedad | Tipo de Dato | Enumeración MQL5 | Función y Mecánica de Enlace |
| :---- | :---- | :---- | :---- |
| Identificador de Posición | long | POSITION\_IDENTIFIER | Número correlativo único asignado a la posición en el momento de su apertura.6 Permanece inalterado durante toda la vida útil de la posición.6 |
| ID de Posición en Orden | long | ORDER\_POSITION\_ID | Identificador que el servidor escribe de forma automática en la orden en el instante exacto en que es ejecutada o transmutada en transacción.6 |
| ID de Posición en Deal | long | DEAL\_POSITION\_ID | Identificador que se inyecta de forma persistente en el registro de la transacción física para rastrear a qué posición afectó el intercambio.5 |

Cuando se envía una orden inicial para abrir el mercado, el servidor de trading le asigna un número de ticket único.4 Al ejecutarse el primer *deal*, el sistema utiliza este número de ticket de orden original como el DEAL\_POSITION\_ID y el POSITION\_IDENTIFIER de la nueva posición creada.6 Todos los *deals* posteriores orientados a incrementar la posición, realizar cierres parciales o revertirla, heredan este identificador permanente, lo que permite al desarrollador aislar y agrupar la genealogía completa de una posición a partir de consultas secuenciales en la base de datos histórica.6

## **2\. Tipología Exhaustiva de Órdenes y Mecánica de Activación**

El motor de trading de MT5 clasifica las órdenes comerciales en ejecuciones inmediatas y condicionales, proporcionando flexibilidad estructural para interactuar con la liquidez del mercado.2

### **Órdenes de Mercado (Market Orders)**

* **ORDER\_TYPE\_BUY**: Instrucción para ejecutar una transacción de compra directa al precio Ask (demanda) actual del mercado.3  
* **ORDER\_TYPE\_SELL**: Instrucción para ejecutar una transacción de venta directa al precio Bid (oferta) actual del mercado.3

### **Órdenes Pendientes Estándar (Standard Pending Orders)**

* **ORDER\_TYPE\_BUY\_LIMIT**: Orden pasiva de compra colocada por debajo del precio actual del mercado.8 Se activa y ejecuta si el precio del mercado desciende a un nivel menor o igual al precio especificado.2  
* **ORDER\_TYPE\_SELL\_LIMIT**: Orden pasiva de venta colocada por encima del precio actual del mercado.8 Se activa y ejecuta si el precio del mercado sube a un nivel mayor o igual al precio especificado.2  
* **ORDER\_TYPE\_BUY\_STOP**: Orden de compra colocada por encima del precio actual del mercado.9 Al tocarse el precio especificado, el servidor transforma la instrucción en una orden de mercado para ejecutarse de inmediato.2  
* **ORDER\_TYPE\_SELL\_STOP**: Orden de Venta colocada por debajo del precio actual del mercado.9 Al tocarse el precio especificado, el servidor transforma la instrucción en una orden de mercado para ejecutarse de inmediato.2

### **Órdenes Pendientes Complejas Stop-Limit**

Estas órdenes operan mediante un flujo de ejecución de dos etapas controlado íntegramente por el servidor de trading, optimizando la colocación de órdenes pasivas en escenarios de alta volatilidad.10

* **ORDER\_TYPE\_BUY\_STOP\_LIMIT**: El operador especifica dos niveles de precios clave: el precio de disparo (price) y el precio límite final (stoplimit).10  
  * *Fase de Monitorización*: La orden permanece inactiva en el servidor y no es transmitida al libro de órdenes del mercado.11  
  * *Fase de Activación*: Cuando la cotización Ask del mercado sube y alcanza el precio de disparo (price), el servidor elimina la orden de parada de manera instantánea.10  
  * *Fase de Colocación*: El servidor inyecta de forma automática una orden pasiva de tipo ORDER\_TYPE\_BUY\_LIMIT al precio establecido en el campo stoplimit.10  
* **ORDER\_TYPE\_SELL\_STOP\_LIMIT**: El operador especifica el precio de disparo (price) y el precio límite final (stoplimit).10  
  * *Fase de Monitorización*: La orden se mantiene oculta en el servidor.11  
  * *Fase de Activación*: Cuando la cotización Bid del mercado desciende y alcanza el precio de disparo (price), la orden de parada es retirada.10  
  * *Fase de Colocación*: El servidor coloca automáticamente una orden pasiva de tipo ORDER\_TYPE\_SELL\_LIMIT al precio establecido en el campo stoplimit.10

### **Niveles Protectores Sintéticos (Stop Loss y Take Profit)**

Los niveles de Stop Loss (sl) y Take Profit (tp) se configuran como instrucciones secundarias vinculadas directamente a una posición activa o a una orden pendiente.2 El servidor de MT5 procesa estos niveles como órdenes pendientes latentes e independientes que se ejecutan automáticamente cuando el precio cruza el umbral configurado.2

* Un Stop Loss de una posición de compra actúa como una orden oculta SELL\_STOP.9  
* Un Take Profit de una posición de compra actúa como una orden oculta SELL\_LIMIT.9  
* Su ejecución física genera una transacción (*deal*) de salida que liquida el volumen neto de la posición.5

## **3\. Modos de Ejecución del Broker (SYMBOL\_TRADE\_EXEMODE)**

El procesamiento de las cotizaciones y la asignación del precio de ejecución final por parte del servidor del broker se rigen por el Modo de Ejecución del Símbolo.2 Esta configuración se consulta mediante la función SymbolInfoInteger() utilizando el identificador SYMBOL\_TRADE\_EXEMODE, el cual devuelve un valor perteneciente a la enumeración ENUM\_SYMBOL\_TRADE\_EXECUTION.12

### **Ejecución a Solicitud (Request Execution \- SYMBOL\_TRADE\_EXECUTION\_REQUEST)**

Este modo es habitual en mercados OTC tradicionales de baja liquidez.12 El terminal del cliente no puede enviar una orden de mercado directa sin realizar un paso de negociación previa con el servidor del broker 7:

1. El cliente solicita una cotización en tiempo real para un volumen específico.12  
2. El broker responde enviando una cotización firme con precios Bid y Ask válidos por un intervalo de tiempo muy estricto.12  
3. El cliente decide enviar la orden especificando obligatoriamente dicho precio cotizado en el campo price de la estructura MqlTradeRequest.7 Si la cotización ha expirado o el mercado se ha movido, la transacción es rechazada instantáneamente.12

### **Ejecución Instantánea (Instant Execution \- SYMBOL\_TRADE\_EXECUTION\_INSTANT)**

Este modo elimina la necesidad de la negociación manual previa.7

* El terminal del cliente captura los últimos precios de su caché local de cotizaciones e inyecta estos valores de forma transparente en el campo price de la estructura MqlTradeRequest.7  
* El desarrollador puede especificar el parámetro deviation (desviación máxima aceptable en puntos).7  
* Si el precio del servidor al recibir la solicitud se encuentra dentro del rango de tolerancia establecido en deviation, la orden se ejecuta al precio del servidor.7  
* Si el movimiento del precio excede la tolerancia, el servidor suspende la operación y devuelve un código de recotización (TRADE\_RETCODE\_REQUOTE), aportando las nuevas cotizaciones bid/ask vigentes para que el EA evalúe si reintenta la transacción.12

### **Ejecución de Mercado (Market Execution \- SYMBOL\_TRADE\_EXECUTION\_MARKET)**

En este modo, el broker garantiza la ejecución del volumen total solicitado, asumiendo el operador la variación del precio de mercado al momento de la recepción del paquete de datos en el servidor.7

* **Ignorancia del precio del cliente**: El motor de MT5 ignora por completo el contenido del campo price en la estructura MqlTradeRequest al enviar órdenes de tipo TRADE\_ACTION\_DEAL.7 La transacción se ejecuta al precio vigente en el servidor sin excepciones.7  
* **Inoperatividad de desviación**: El campo deviation no tiene ningún efecto operativo en este modo de ejecución.9  
* **Restricción de Stops**: Muchos brokers que operan bajo este modo rechazan solicitudes de mercado que contienen valores directos en los campos de protección sl o tp en el momento de la apertura.9 El flujo seguro exige enviar la orden con stop loss y take profit en cero y modificarlos inmediatamente después utilizando la acción TRADE\_ACTION\_SLTP.9

### **Ejecución de Bolsa (Exchange Execution \- SYMBOL\_TRADE\_EXECUTION\_EXCHANGE)**

Es el modelo mandatorio para interactuar con cámaras de compensación y bolsas reguladas.7

* El precio de ejecución se determina de forma transparente cruzando la orden contra el libro de órdenes centralizado de la bolsa (Profundidad de Mercado \- DOM).2  
* Si la orden consume múltiples niveles de precio, se ejecuta a un precio promedio ponderado por volumen (VWAP).2  
* Al igual que en la ejecución de mercado, el precio enviado en órdenes de mercado no tiene validez y se ejecuta al precio real del cruce en la bolsa.7

### **Matriz de Comportamiento de Campos por Modo de Ejecución**

La siguiente tabla resume cómo el servidor de MT5 procesa los campos de una estructura MqlTradeRequest para órdenes de mercado (TRADE\_ACTION\_DEAL) según el modo de ejecución configurado:

| Modo de Ejecución | Campo price | Campo deviation | Admite SL/TP en Apertura | Genera Requotes |
| :---- | :---- | :---- | :---- | :---- |
| **Request Execution** 7 | **Mandatorio** 7 | **Mandatorio** 7 | Sí 9 | No (Rechazo Directo) 12 |
| **Instant Execution** 7 | **Mandatorio** 7 | **Mandatorio** 7 | Sí 9 | **Sí** (TRADE\_RETCODE\_REQUOTE) 12 |
| **Market Execution** 7 | Ignorado 7 | Ignorado 9 | **Frecuentemente Bloqueado** 9 | No (Ejecución Garantizada) 16 |
| **Exchange Execution** 7 | Ignorado 7 | Ignorado 9 | Sí 9 | No (Ejecución Garantizada) 16 |

## **4\. Políticas de Relleno de Lotes (Fill Policies)**

Las políticas de relleno definen el comportamiento algorítmico del motor de MT5 cuando el volumen disponible en el mercado no satisface de manera exacta el volumen total requerido en la orden.12 Se especifican en el campo type\_filling de la estructura MqlTradeRequest utilizando valores de la enumeración ENUM\_ORDER\_TYPE\_FILLING.7 El desarrollador debe validar si la política seleccionada está permitida por el broker para el símbolo en cuestión, cruzando el tipo de orden con la máscara de bits devuelta por SYMBOL\_FILLING\_MODE.12

### **Fill or Kill (FOK \- ORDER\_FILLING\_FOK)**

Esta política exige una ejecución binaria y absoluta.12 La totalidad del volumen especificado en el campo volume de la solicitud de trade debe completarse de forma inmediata utilizando la liquidez disponible.12 Si no hay suficiente contrapartida para llenar el ![][image1] del lote solicitado a los precios permitidos, el servidor cancela la orden completa de forma instantánea.12 No se admiten ejecuciones parciales bajo ninguna circunstancia.12

### **Immediate or Cancel (IOC \- ORDER\_FILLING\_IOC)**

Esta política autoriza la ejecución parcial de la orden.12 El servidor de MT5 casará la mayor cantidad de volumen posible según la liquidez inmediata que ofrezca el mercado en el momento de la llegada de la solicitud.12 Si la orden solo se puede cubrir parcialmente (por ejemplo, se solicitan ![][image2] lotes pero solo hay ![][image3] disponibles), se genera una transacción por el volumen disponible y el volumen remanente que no pudo ser cubierto (![][image4] lotes) se cancela de forma automática.12

### **Return (ORDER\_FILLING\_RETURN)**

Esta política está diseñada para la gestión de volúmenes elevados sin pérdida de prioridad de orden.12 En caso de una ejecución parcial, la porción disponible se procesa generando el *deal* correspondiente, mientras que el volumen residual que no pudo completarse no se cancela, sino que permanece registrado en el servidor como una orden de mercado activa en espera de nueva contrapartida.12  
*Nota de Restricción del Sistema*: La política ORDER\_FILLING\_RETURN está estrictamente prohibida en símbolos que operan bajo el modo de ejecución de mercado directo SYMBOL\_TRADE\_EXECUTION\_MARKET.12 En el caso de órdenes pendientes, siempre se debe inicializar el campo de relleno con la opción ORDER\_FILLING\_RETURN, dado que estas órdenes no se ejecutan en el momento de su envío.16

### **Compatibilidad de Políticas de Relleno según el Modo de Ejecución del Símbolo**

El motor de MT5 restringe el uso de las políticas de relleno basándose en el modo de ejecución del símbolo en el servidor 16:

| Modo de Ejecución / Política de Relleno | FOK (ORDER\_FILLING\_FOK) | IOC (ORDER\_FILLING\_IOC) | Return (ORDER\_FILLING\_RETURN) |
| :---- | :---- | :---- | :---- |
| **Request Execution** (SYMBOL\_TRADE\_EXECUTION\_REQUEST) 16 | **Permitido** 16 | **Permitido** 16 | **Permitido** 16 |
| **Instant Execution** (SYMBOL\_TRADE\_EXECUTION\_INSTANT) 16 | **Permitido** 16 | **Permitido** 16 | **Permitido** 16 |
| **Market Execution** (SYMBOL\_TRADE\_EXECUTION\_MARKET) 16 | Configurable 16 | Configurable 16 | **Prohibido** 16 |
| **Exchange Execution** (SYMBOL\_TRADE\_EXECUTION\_EXCHANGE) 16 | Configurable 16 | Configurable 16 | **Permitido** 16 |

## **5\. Anatomía Detallada de la Estructura MqlTradeRequest**

Toda interacción de trading con el servidor requiere el envío de la estructura nativa MqlTradeRequest.7 Es altamente recomendable inicializar la memoria de esta estructura a cero utilizando la función ZeroMemory() antes de rellenar sus campos, evitando así la inyección de basura informática que pueda corromper el envío de la orden.11

Fragmento de código  
struct MqlTradeRequest  
  {  
   ENUM\_TRADE\_REQUEST\_ACTIONS    action;           // Tipo de acción comercial a realizar  
   ulong                         magic;            // Identificador numérico único del EA (Magic Number)  
   ulong                         order;            // Ticket de la orden (para modificaciones de pendientes)  
   string                        symbol;           // Nombre del instrumento financiero (par de divisas, CFD, etc.)  
   double                        volume;           // Volumen comercial solicitado expresado en lotes estándar  
   double                        price;            // Precio de ejecución o disparo de la instrucción comercial  
   double                        stoplimit;        // Precio de colocación de la orden límite en órdenes Stop-Limit  
   double                        sl;               // Precio asignado para el nivel de protección Stop Loss  
   double                        tp;               // Precio asignado para el nivel de protección Take Profit  
   ulong                         deviation;        // Desviación máxima tolerada respecto al precio de envío (en puntos)  
   ENUM\_ORDER\_TYPE               type;             // Dirección de la operación (compra, venta o tipos pendientes)  
   ENUM\_ORDER\_TYPE\_FILLING       type\_filling;     // Política de relleno de volumen seleccionada  
   ENUM\_ORDER\_TYPE\_TIME          type\_time;        // Política de tiempo de validez de la orden pendiente  
   datetime                      expiration;       // Fecha y hora de expiración de la orden pendiente  
   string                        comment;          // Comentario personalizado de texto asociado a la transacción  
   ulong                         position;         // Ticket único de la posición activa (para modificaciones o cierres)  
   ulong                         position\_by;      // Ticket de la posición opuesta (utilizado para cierres cruzados)  
  };

### **Descripción Detallada de los Campos de la Estructura**

* **action**: Campo mandatorio de tipo ENUM\_TRADE\_REQUEST\_ACTIONS que define la naturaleza de la solicitud.7 Controla el comportamiento del motor al procesar el resto de los parámetros de la estructura.10  
* **magic**: Identificador numérico único asignado a un Asesor Experto.7 Permite estructurar la trazabilidad analítica de la cuenta comercial al marcar las órdenes, transacciones y posiciones con este identificador.7  
* **order**: Ticket unívoco de una orden pendiente activa en el servidor.7 Es obligatorio en operaciones que pretenden alterar la estructura de una orden pendiente ya establecida o solicitar su eliminación del sistema.7  
* **symbol**: Nombre de texto del símbolo comercial.7 No es obligatorio en cuentas Hedging para modificaciones de Stop Loss y Take Profit, pero es altamente recomendable definirlo para unificar y homogeneizar el código.7  
* **volume**: Volumen comercial solicitado en lotes.7 El volumen final que se ejecute puede variar en base a las políticas de relleno permitidas por el broker y a la liquidez del mercado.7  
* **price**: Nivel de precio para la colocación de la orden o ejecución del intercambio.7 Es ignorado por el motor del servidor de forma deliberada en símbolos configurados bajo el modo Market Execution.7  
* **stoplimit**: Precio específico de colocación de la orden límite cuando la cotización cruza el precio de disparo en órdenes complejas de tipo BUY\_STOP\_LIMIT o SELL\_STOP\_LIMIT.10  
* **sl**: Precio del Stop Loss protector.7 El valor cero se utiliza de forma estándar para eliminar el nivel de stop loss de la posición u orden pendiente.15  
* **tp**: Precio del Take Profit protector.7 El valor cero se utiliza de forma estándar para eliminar el nivel de take profit de la posición u orden pendiente.15  
* **deviation**: Desviación límite permitida en puntos para la ejecución de órdenes en los modos Instant Execution y Request Execution.9 No tiene efecto en modos de ejecución de mercado o bolsa.9  
* **type**: Tipo de orden a colocar definido por la enumeración ENUM\_ORDER\_TYPE.7 Determina si la instrucción es una compra, venta u orden pendiente de parada o límite.7  
* **type\_filling**: Política de relleno expresada por la enumeración ENUM\_ORDER\_TYPE\_FILLING.7 Debe coincidir con uno de los modos permitidos y habilitados en el broker para el instrumento.9  
* **type\_time**: Expiración temporal de la orden de tipo ENUM\_ORDER\_TYPE\_TIME.7 Define el ciclo de vida útil de las órdenes pendientes antes de ser eliminadas automáticamente del servidor.11  
* **expiration**: Fecha y hora de expiración de la orden pendiente.7 Solo es obligatoria y procesada cuando el campo type\_time se inicializa con los parámetros ORDER\_TIME\_SPECIFIED o ORDER\_TIME\_SPECIFIED\_DAY.7  
* **comment**: Comentario de texto libre asignable por el programador o el usuario de hasta 31 caracteres de longitud máxima.  
* **position**: Ticket numérico identificador de la posición afectada.7 Es de carácter mandatorio en cuentas bajo arquitectura Hedging para poder modificar stops o liquidar la posición específica.11  
* **position\_by**: Ticket identificador de la posición contraria abierta sobre el mismo símbolo de mercado.7 Se utiliza únicamente para la ejecución de la acción de cierre cruzado compensatorio TRADE\_ACTION\_CLOSE\_BY.6

## **6\. Sincronización de Respuestas: MqlTradeResult y Códigos de Servidor**

Cualquier solicitud comercial despachada al servidor mediante las funciones OrderSend() u OrderSendAsync() devuelve una estructura de control de tipo MqlTradeResult para reportar el estado del procesamiento.7

Fragmento de código  
struct MqlTradeResult  
  {  
   uint          retcode;          // Código numérico devuelto por el servidor de trading  
   ulong         deal;             // Ticket asignado a la transacción física ejecutada  
   ulong         order;            // Ticket asignado a la orden colocada en el sistema  
   double        volume;           // Volumen real confirmado por el broker  
   double        price;            // Precio real confirmado por el broker  
   double        bid;              // Precio de oferta (Bid) actual del servidor (para requotes)  
   double        ask;              // Precio de demanda (Ask) actual del servidor (para requotes)  
   string        comment;          // Comentario o descripción textual de la respuesta  
   uint          request\_id;       // Identificador correlativo de la solicitud  
   int           retcode\_external; // Código de error proveniente del sistema de intercambio externo  
  };

### **Mecanismo de Sincronización de request\_id en Solicitudes Asíncronas**

Cuando se opta por despachar solicitudes comerciales de alta velocidad mediante la función asíncrona OrderSendAsync(), la función retorna el control del procesador de forma inmediata al EA, sin esperar la confirmación de la ejecución real por parte del servidor.4

* En este punto, todos los campos de la estructura MqlTradeResult devueltos se encuentran vacíos, con la única excepción del código de aceptación local (retcode) y el identificador correlativo de solicitud request\_id.4  
* El request\_id es un número de serie único asignado por el terminal local del cliente para esa sesión de trading.10  
* Cuando el servidor procesa la instrucción, genera una serie de eventos asíncronos que llegan a la terminal.10  
* Al capturarse estos eventos en el manejador global OnTradeTransaction(), el terminal del cliente rellena únicamente los parámetros request y result para transacciones cuyo tipo coincida con TRADE\_TRANSACTION\_REQUEST.10  
* El desarrollador puede recuperar el result.request\_id recibido en el evento y compararlo directamente contra el request\_id local almacenado tras llamar a OrderSendAsync(), permitiendo asociar de manera inequívoca la orden del EA con la transacción real ejecutada en el servidor.10

### **Códigos de Retorno Críticos del Servidor de Trading (retcode)**

| Código | Identificador MQL5 | Significado Técnico y Protocolo de Acción |
| :---- | :---- | :---- |
| **10009** | TRADE\_RETCODE\_DONE | Solicitud comercial completada con éxito absoluto en el servidor.20 |
| **10008** | TRADE\_RETCODE\_PLACED | La orden pendiente ha sido colocada de forma pasiva en el libro de órdenes con éxito.18 |
| **10004** | TRADE\_RETCODE\_REQUOTE | Recotización del broker. Se deben analizar los nuevos precios sugeridos en los campos bid y ask.12 |
| **10006** | TRADE\_RETCODE\_REJECT | Solicitud rechazada de manera explícita por la mesa de operaciones o por el servidor.14 |
| **10013** | TRADE\_RETCODE\_INVALID | Solicitud comercial inválida. Indica un error en la configuración de la estructura de solicitud.22 |
| **10015** | TRADE\_RETCODE\_INVALID\_PRICE | El precio enviado no coincide con el paso del precio mínimo o está fuera de rango.14 |
| **10016** | TRADE\_RETCODE\_INVALID\_STOPS | Los precios sl o tp violan la distancia del nivel mínimo de stop del símbolo.14 |
| **10018** | TRADE\_RETCODE\_MARKET\_CLOSED | La sesión comercial está cerrada en el servidor para el símbolo seleccionado.21 |

## **7\. Modelos Contables de Cuenta: Hedging vs. Netting**

La contabilidad de las posiciones abiertas y el cálculo de la exposición de riesgo de la cuenta se definen a nivel del servidor de trading bajo dos modelos estructuralmente excluyentes.23 Se consultan mediante AccountInfoInteger() con el identificador de propiedad ACCOUNT\_MARGIN\_MODE.23

### **Arquitectura de Netting (Compensación Contable)**

El modelo de netting es el estándar exigido por las bolsas de futuros, acciones y opciones reguladas.23

* **Posición Única por Símbolo**: Solo puede existir una única posición abierta de forma simultánea por cada instrumento comercial.11  
* **Acumulación de Volumen**: Si se posee una posición de compra (BUY) de ![][image3] lotes y se despacha una nueva orden de mercado de compra por ![][image5] lote, el motor de ejecución consolida ambas operaciones en una posición única de ![][image4] lotes.1 El precio de apertura se recalcula automáticamente como el precio promedio ponderado de las transacciones.10  
* **Liquidación y Reversión**: Si se dispone de una posición de compra por ![][image5] lote y se ejecuta una venta a mercado por ![][image5] lote, el balance se compensa de forma inmediata cerrando la posición neta.1 Si la orden de venta es por ![][image4] lotes, la posición original se cierra y se abre instantáneamente una posición contraria de venta por ![][image3] lotes en un proceso conocido como reversión de posición.5 El POSITION\_IDENTIFIER original no cambia, pero el ticket de la posición es reemplazado por el ticket de la última orden de reversión.6

### **Arquitectura de Hedging (Cobertura Multidireccional)**

El modelo de hedging permite la coexistencia independiente de múltiples posiciones en diferentes direcciones para el mismo símbolo comercial.6

* **Posiciones Independientes**: Cada transacción comercial de entrada genera una nueva posición de riesgo aislada con su propio ticket de posición (POSITION\_TICKET), incluso si se abren órdenes de la misma dirección de forma simultánea.2  
* **Cruce compensatorio (Close By)**: Permite liberar el margen requerido al cerrar de manera cruzada y simultánea dos posiciones abiertas en direcciones opuestas sobre el mismo símbolo comercial utilizando la acción TRADE\_ACTION\_CLOSE\_BY.6 El volumen simétrico se compensa liberando el capital retenido sin incurrir en spreads dobles en el mercado.6

### **Modelado Matemático de Requerimientos de Margen**

En el modelo de Netting, el cálculo del margen colateral requerido se calcula de manera aditiva directa sobre el volumen total consolidado 23:  
![][image6]  
En el modelo de Hedging, si el broker permite descuentos por cobertura simultánea sobre posiciones contrarias, el margen se calcula utilizando la directiva del margen de cobertura (SYMBOL\_MARGIN\_HEDGED).13  
Si la directiva de cálculo por la pierna mayor (SYMBOL\_MARGIN\_HEDGED\_USE\_LEG) está configurada como falsa (false), el margen se calcula aplicando la tasa de cobertura ponderada 13:  
![][image7]  
Si el servidor calcula el margen utilizando únicamente la pierna expuesta de mayor volumen (cuando SYMBOL\_MARGIN\_HEDGED\_USE\_LEG es verdadera o true), el cálculo se modela de la siguiente manera 13:  
![][image8]

## **8\. El Motor de Eventos Asíncronos OnTradeTransaction()**

La función OnTradeTransaction() es el manejador de eventos especializado en procesar de forma secuencial las transacciones comerciales enviadas por el servidor de trading.19

### **Limitaciones Físicas y Mecánica de la Cola de Transacciones**

La cola de recepción local de eventos del cliente de MetaTrader 5 posee un tamaño máximo estricto de ![][image9] **elementos**.10

* **Asincronía absoluta**: Los eventos comerciales no se garantizan en orden cronológico absoluto cuando viajan por la red.10 El desarrollador no puede programar algoritmos esperando que un evento TRADE\_TRANSACTION\_ORDER\_ADD ocurra necesariamente antes de un evento TRADE\_TRANSACTION\_DEAL\_ADD.19  
* **Peligro de desbordamiento**: Si la función OnTradeTransaction() de un Asesor Experto bloquea el hilo de ejecución principal consumiendo recursos excesivos (por ejemplo, llamadas sincrónicas de lectura/escritura de archivos en disco, bucles complejos de análisis estadístico o llamadas a red por sockets), la cola interna de ![][image9] transacciones se saturará rápidamente.10 Las nuevas transacciones comerciales entrantes desplazarán y eliminarán los eventos antiguos de la cola sin que el EA sea notificado, corrompiendo el estado analítico de la aplicación.10  
* **Mutabilidad de Estado**: Debido al procesamiento concurrente multi-hilo en la terminal del cliente, en el momento preciso en que se llama a OnTradeTransaction(), el estado físico de la orden, transacción o posición ya puede haber cambiado radicalmente en comparación con los valores reportados en la estructura transaccional MqlTradeTransaction.10 El desarrollador debe re-verificar y consultar los datos vigentes en tiempo real seleccionando el objeto comercial mediante las funciones nativas correspondientes.10

### **Reglas de Llenado de Campos en MqlTradeTransaction por Tipo de Transacción**

La estructura MqlTradeTransaction se rellena de forma diferente por el motor del servidor según la naturaleza del evento comercial notificado en el campo type (ENUM\_TRADE\_TRANSACTION\_TYPE) 10:

| Campos Llenados / Tipo de Transacción | deal | order | symbol | volume | price | position | position\_by |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **TRADE\_TRANSACTION\_ORDER\_ADD** 10 | \- | **Sí** | **Sí** | **Sí** (Pendiente) | **Sí** | \- | \- |
| **TRADE\_TRANSACTION\_ORDER\_UPDATE** 10 | \- | **Sí** | **Sí** | **Sí** (Actual) | **Sí** | \- | \- |
| **TRADE\_TRANSACTION\_ORDER\_DELETE** 10 | \- | **Sí** | **Sí** | **Sí** (Residual) | **Sí** | **Sí**\* | **Sí**\* |
| **TRADE\_TRANSACTION\_DEAL\_ADD** 10 | **Sí** | **Sí** (Origen) | **Sí** | **Sí** (Ejecutado) | **Sí** | **Sí** | **Sí**\* |
| **TRADE\_TRANSACTION\_POSITION** 10 | \- | \- | **Sí** | **Sí** (Modificado) | **Sí** (Medio) | **Sí** | \- |
| **TRADE\_TRANSACTION\_REQUEST** 10 | \- | \- | \- | \- | \- | \- | \- |

*\*Campos Opcionales / Condicionales*:

* Para ORDER\_DELETE, el campo position y position\_by solo se rellenan si la eliminación de la orden se debe a su ejecución directa en el mercado.25  
* Para DEAL\_ADD, position\_by solo se rellena en transacciones de compensación cruzada de tipo Close By.25  
* Para TRADE\_TRANSACTION\_REQUEST, todos los campos del cuerpo de la transacción están vacíos por definición; el desarrollador debe leer exclusivamente los parámetros complementarios request y result del manejador de eventos.10

## **9\. Simulación y Validación Previa con OrderCheck()**

El motor comercial de MT5 ofrece la función OrderCheck() para pre-validar las solicitudes antes de transmitirlas a la red.21

Fragmento de código  
bool OrderCheck(  
  MqlTradeRequest&      request,  // Estructura de solicitud a verificar  
  MqlTradeCheckResult&  result    // Estructura receptora de la simulación  
);

### **Proyección de Estado Acumulativo frente a Helpers Aislados**

* **OrderCalcMargin()**: Calcula el requerimiento de margen colateral de una única transacción hipotética de forma aislada, sin considerar si la cuenta ya tiene otras órdenes activas o posiciones de riesgo abiertas.22  
* **OrderCalcProfit()**: Proyecta las ganancias o pérdidas de un movimiento hipotético de cotización en base a un volumen y una dirección de intercambio fijos.29  
* **OrderCheck()**: Es un proyector de estado integral.22 Simula la inyección de la orden propuesta directamente sobre el estado de la cuenta en el servidor virtual de la terminal, calculando el impacto acumulado junto con las posiciones de riesgo actuales y las órdenes pendientes de la cuenta.22

La simulación actualiza y proyecta los campos clave de la estructura MqlTradeCheckResult 22:

* **retcode**: Reporta el código de retorno potencial del servidor virtual.29 Si la orden propiciara una insuficiencia de margen, se devuelve el código de error TRADE\_RETCODE\_NO\_MONEY.22  
* **margin**: Proyecta el nuevo requerimiento de margen acumulado total de la cuenta tras ejecutarse la orden.22 Si la orden propuesta es contraria a una posición abierta en una cuenta Netting, el campo margin disminuye de forma proporcional para reflejar la reducción de la exposición al riesgo.22  
* **margin\_free**: Proyecta el capital líquido libre resultante que quedará disponible en la cuenta comercial para respaldar otras posiciones abiertas.22  
* **margin\_level**: Proyecta el nivel porcentual del margen de garantía resultante.22 Si este nivel cae por debajo de los límites mínimos configurados por el broker (ACCOUNT\_MARGIN\_SO\_SO), la simulación de OrderCheck devuelve falso (false) previniendo un Stop Out de forma prematura.22

## **10\. Gestión de Historial: Snapshots, Selectores y Limitaciones**

El motor de MT5 utiliza un modelo de consulta asíncrono para el historial de transacciones y órdenes cerradas basado en la creación de "Snapshots" temporales en la terminal del cliente.31

### **El Flujo de Carga de Snapshots en Memoria**

Para optimizar el rendimiento y evitar llamadas bloqueantes en disco durante la ejecución del EA, el terminal local almacena una caché del historial de la cuenta.31

1. El desarrollador debe indicarle de forma explícita al terminal qué rango de datos desea analizar llamando obligatoriamente a la función HistorySelect(from\_date, to\_date) o HistorySelectByPosition(position\_id).31  
2. La terminal procesa la consulta y genera internamente una lista temporal o "Snapshot" de órdenes históricas y de transacciones (*deals*) en la memoria exclusiva del EA.31  
3. El desarrollador puede interrogar la cantidad de elementos seleccionados en este snapshot temporal mediante HistoryOrdersTotal() y HistoryDealsTotal().31  
4. La extracción de elementos individuales se realiza utilizando índices relativos con HistoryOrderGetTicket(index) y HistoryDealGetTicket(index).31

### **La Grave Limitación de HistorySelectByPosition con Operaciones "Close By"**

La función del motor nativo de MT5 HistorySelectByPosition(position\_id) posee una limitación estructural crítica al auditar cuentas bajo el modelo de Hedging en escenarios de cierre por compensación mutua (Close By) 31:

* Cuando se ejecuta un cierre cruzado simultáneo de dos posiciones de cobertura opuestas (Posición \#1 y Posición \#2), el servidor genera una orden especial con la propiedad ORDER\_TYPE\_CLOSE\_BY para registrar el cierre de ambas exposiciones.31  
* Para enlazar este evento, la transacción escribe el ticket de la primera posición en el campo nativo habitual de la base de datos ORDER\_POSITION\_ID (asociado a la Posición \#1).6  
* El ticket de la segunda posición contraria se ve forzado a registrarse en un campo exclusivo alternativo denominado ORDER\_POSITION\_BY\_ID o DEAL\_POSITION\_BY\_ID.6  
* **Fallo del Motor de Consulta**: La función nativa de MT5 HistorySelectByPosition(position\_id) está programada exclusivamente para escanear las columnas estándar ORDER\_POSITION\_ID y DEAL\_POSITION\_ID.31 El motor ignora deliberadamente y no comprueba el campo correspondiente a la contraposición ORDER\_POSITION\_BY\_ID.31  
* **Consecuencia de Datos**: Si el desarrollador solicita la reconstrucción de la historia de la Posición \#2 llamando a HistorySelectByPosition(\#2), la lista o snapshot devuelto por la terminal **no contendrá bajo ninguna circunstancia** la orden ni el *deal* de tipo CLOSE\_BY que causaron su liquidación del mercado.31 Para solucionar este vacío de información, se debe escanear el historial global cargándolo mediante HistorySelect(0, LONG\_MAX) y filtrando de forma manual cada transacción mediante la lectura directa de sus propiedades en un ciclo iterativo.31

### **Reseteo de Contexto en Consultas Directas**

El uso de las funciones de selección directa por ticket HistoryOrderSelect(ticket) o HistoryDealSelect(ticket) altera directamente el estado de la caché del EA.31

* Si se cargó un snapshot de ![][image10] transacciones mediante una llamada previa a HistorySelect(), y posteriormente se ejecuta la función HistoryOrderSelect(ticket\_especifico) para leer los datos de una orden puntual de forma aislada, el snapshot completo de ![][image10] elementos es borrado de la memoria de la terminal.31  
* En su lugar, el contexto en memoria se reinicia y pasa a contener de forma exclusiva el registro de la orden seleccionada por ticket.31 Cualquier llamada posterior a HistoryOrdersTotal() o HistoryDealsTotal() devolverá un valor de uno (1), quebrando cualquier bucle de lectura secuencial que estuviera procesando la aplicación en paralelo.31  
* **Técnica de Selección Débil (Weak Selection)**: Para prevenir la corrupción de la caché del snapshot durante un bucle iterativo, se debe comprobar si el objeto comercial ya reside en la memoria cargada del terminal antes de forzar su selección directa, validando de la siguiente manera 31:

Fragmento de código  
if(HistoryOrderGetInteger(ticket\_id, ORDER\_TICKET) \== ticket\_id)  
  {  
   // La orden histórica ya se encuentra en el snapshot activo; leer propiedades directamente  
  }

## **11\. Implementación de Software de Trading MQL5 de Grado de Producción**

Los siguientes componentes de software se estructuran de manera modular utilizando las especificaciones de ejecución de MetaTrader 5 analizadas anteriormente.

### **1\. Despachador de Órdenes Completo con Pre-Validación Sincrónica y Soporte para todos los Tipos de Órdenes**

Este componente implementa la clase COrderDispatcher. Diseñado para ejecutarse en entornos de alta velocidad, se encarga de automatizar la normalización del volumen y del precio, determinar de forma dinámica la política de relleno compatible con el broker y realizar una validación de margen mediante OrderCheck antes de despachar cualquiera de los 8 tipos de órdenes posibles.4

Fragmento de código  
\#property strict

class COrderDispatcher  
  {  
private:  
   //--- Determina de forma dinámica la política de relleno óptima admitida por el broker para el símbolo  
   ENUM\_ORDER\_TYPE\_FILLING GetOptimalFilling(const string symbol)  
     {  
      int filling\_mode \= (int)SymbolInfoInteger(symbol, SYMBOL\_FILLING\_MODE);  
        
      // Priorizar Fill or Kill (FOK) si está activo en las banderas del símbolo  
      if((filling\_mode & SYMBOL\_FILLING\_FOK)\!= 0\)  
         return ORDER\_FILLING\_FOK;  
           
      // Seleccionar Immediate or Cancel (IOC) como segunda opción admisible  
      if((filling\_mode & SYMBOL\_FILLING\_IOC)\!= 0\)  
         return ORDER\_FILLING\_IOC;  
           
      // Retornar Return por defecto para el mantenimiento de volúmenes residuales  
      return ORDER\_FILLING\_RETURN;  
     }

   //--- Normaliza el precio objetivo adaptándolo de forma estricta al paso del tick del símbolo  
   double NormalizePriceToTick(const string symbol, const double price)  
     {  
      double tick\_size \= SymbolInfoDouble(symbol, SYMBOL\_TRADE\_TICK\_SIZE);  
      if(tick\_size \== 0\) return price;  
      return MathRound(price / tick\_size) \* tick\_size;  
     }

   //--- Normaliza el volumen según el tamaño del lote mínimo, máximo y el incremento permitido por el broker  
   double NormalizeVolumeStep(const string symbol, const double volume)  
     {  
      double lot\_step \= SymbolInfoDouble(symbol, SYMBOL\_VOLUME\_STEP);  
      double lot\_min  \= SymbolInfoDouble(symbol, SYMBOL\_VOLUME\_MIN);  
      double lot\_max  \= SymbolInfoDouble(symbol, SYMBOL\_VOLUME\_MAX);  
        
      if(lot\_step \== 0\) return volume;  
        
      double normalized\_vol \= MathRound(volume / lot\_step) \* lot\_step;  
      normalized\_vol \= MathMax(lot\_min, MathMin(lot\_max, normalized\_vol));  
      return MathNormalizeDouble(normalized\_vol, 2);  
     }

   //--- Ejecuta la lógica central de validación previa y despacho físico al servidor  
   bool SendRequest(MqlTradeRequest \&request, MqlTradeResult \&result)  
     {  
      MqlTradeCheckResult check\_result;  
      ZeroMemory(check\_result);  
      ZeroMemory(result);  
        
      // 1\. EJECUTAR PRE-VALIDACIÓN COMERCIAL INTEGRAL  
      ResetLastError();  
      if(\!OrderCheck(request, check\_result))  
        {  
         PrintFormat(" OrderCheck falló. Código Servidor Proyectado: %u. Comentario: %s. Error API: %d",  
                     check\_result.retcode, check\_result.comment, \_LastError);  
         result.retcode \= check\_result.retcode;  
         result.comment \= "Fallo validación local: " \+ check\_result.comment;  
         return false;  
        }  
          
      if(check\_result.retcode\!= TRADE\_RETCODE\_DONE && check\_result.retcode\!= 0\)  
        {  
         PrintFormat(" La simulación proyectó rechazo. Código: %u. Margen Libre Requerido: %.2f",   
                     check\_result.retcode, check\_result.margin\_free);  
         result.retcode \= check\_result.retcode;  
         return false;  
        }  
          
      // 2\. DESPACHO FÍSICO AL SERVIDOR DE TRADING  
      ResetLastError();  
      if(\!OrderSend(request, result))  
        {  
         PrintFormat(" Fallo crítico de red o ejecución en OrderSend. Retcode: %u. Error API: %d",  
                     result.retcode, \_LastError);  
         return false;  
        }  
          
      // Validar confirmación absoluta de la transacción comercial  
      if(result.retcode \== TRADE\_RETCODE\_DONE || result.retcode \== TRADE\_RETCODE\_PLACED)  
        {  
         PrintFormat(" Procesamiento exitoso. Ticket Orden: %I64u. Ticket Deal: %I64u. Volumen: %.2f",  
                     result.order, result.deal, result.volume);  
         return true;  
        }  
          
      PrintFormat(" El broker rechazó el procesamiento físico. Código: %u. Comentario: %s",  
                  result.retcode, result.comment);  
      return false;  
     }

public:  
   COrderDispatcher() {}

   //--- 1 & 2: Órdenes de Mercado (Buy & Sell)  
   bool ExecuteMarketOrder(const ENUM\_ORDER\_TYPE order\_type, const string symbol, const double volume,   
                           const double sl \= 0, const double tp \= 0, const ulong magic \= 0, const string comment \= "")  
     {  
      if(order\_type\!= ORDER\_TYPE\_BUY && order\_type\!= ORDER\_TYPE\_SELL) return false;  
        
      MqlTradeRequest request;  
      MqlTradeResult result;  
      ZeroMemory(request);  
        
      request.action       \= TRADE\_ACTION\_DEAL;  
      request.symbol       \= symbol;  
      request.volume       \= NormalizeVolumeStep(symbol, volume);  
      request.type         \= order\_type;  
      request.magic        \= magic;  
      request.comment      \= comment;  
      request.type\_filling \= GetOptimalFilling(symbol);  
        
      // Modificar Stops solo si el modo del broker es compatible con SL/TP en apertura directa  
      ENUM\_SYMBOL\_TRADE\_EXECUTION exe\_mode \= (ENUM\_SYMBOL\_TRADE\_EXECUTION)SymbolInfoInteger(symbol, SYMBOL\_TRADE\_EXEMODE);  
      if(exe\_mode\!= SYMBOL\_TRADE\_EXECUTION\_MARKET)  
        {  
         if(sl \> 0\) request.sl \= NormalizePriceToTick(symbol, sl);  
         if(tp \> 0\) request.tp \= NormalizePriceToTick(symbol, tp);  
        }  
          
      // Para Request e Instant es obligatorio inyectar el precio de mercado actual de la caché local  
      if(exe\_mode \== SYMBOL\_TRADE\_EXECUTION\_REQUEST || exe\_mode \== SYMBOL\_TRADE\_EXECUTION\_INSTANT)  
        {  
         request.price     \= (order\_type \== ORDER\_TYPE\_BUY)? SymbolInfoDouble(symbol, SYMBOL\_ASK) : SymbolInfoDouble(symbol, SYMBOL\_BID);  
         request.deviation \= 10; // 10 puntos de tolerancia por defecto  
        }  
          
      return SendRequest(request, result);  
     }

   //--- 3, 4, 5 & 6: Órdenes Pendientes Estándar (Limit & Stop)  
   bool PlacePendingOrder(const ENUM\_ORDER\_TYPE order\_type, const string symbol, const double volume,   
                          const double limit\_price, const double sl \= 0, const double tp \= 0, const ulong magic \= 0, const string comment \= "")  
     {  
      if(order\_type \== ORDER\_TYPE\_BUY\_STOP\_LIMIT || order\_type \== ORDER\_TYPE\_SELL\_STOP\_LIMIT ||   
         order\_type \== ORDER\_TYPE\_BUY || order\_type \== ORDER\_TYPE\_SELL) return false;  
           
      MqlTradeRequest request;  
      MqlTradeResult result;  
      ZeroMemory(request);  
        
      request.action       \= TRADE\_ACTION\_PENDING;  
      request.symbol       \= symbol;  
      request.volume       \= NormalizeVolumeStep(symbol, volume);  
      request.type         \= order\_type;  
      request.price        \= NormalizePriceToTick(symbol, limit\_price);  
      request.magic        \= magic;  
      request.comment      \= comment;  
      request.type\_filling \= GetOptimalFilling(symbol);  
      request.type\_time    \= ORDER\_TIME\_GTC; // Good Till Canceled por defecto  
        
      if(sl \> 0\) request.sl \= NormalizePriceToTick(symbol, sl);  
      if(tp \> 0\) request.tp \= NormalizePriceToTick(symbol, tp);  
        
      return SendRequest(request, result);  
     }

   //--- 7 & 8: Órdenes Pendientes Complejas Stop-Limit  
   bool PlaceStopLimitOrder(const ENUM\_ORDER\_TYPE order\_type, const string symbol, const double volume,  
                            const double trigger\_price, const double limit\_price, const double sl \= 0, const double tp \= 0, const ulong magic \= 0, const string comment \= "")  
     {  
      if(order\_type\!= ORDER\_TYPE\_BUY\_STOP\_LIMIT && order\_type\!= ORDER\_TYPE\_SELL\_STOP\_LIMIT) return false;  
        
      MqlTradeRequest request;  
      MqlTradeResult result;  
      ZeroMemory(request);  
        
      request.action       \= TRADE\_ACTION\_PENDING;  
      request.symbol       \= symbol;  
      request.volume       \= NormalizeVolumeStep(symbol, volume);  
      request.type         \= order\_type;  
      request.price        \= NormalizePriceToTick(symbol, trigger\_price);  
      request.stoplimit    \= NormalizePriceToTick(symbol, limit\_price);  
      request.magic        \= magic;  
      request.comment      \= comment;  
      request.type\_filling \= GetOptimalFilling(symbol);  
      request.type\_time    \= ORDER\_TIME\_GTC;  
        
      if(sl \> 0\) request.sl \= NormalizePriceToTick(symbol, sl);  
      if(tp \> 0\) request.tp \= NormalizePriceToTick(symbol, tp);  
        
      return SendRequest(request, result);  
     }  
  };

### **2\. Tracker de Órdenes y Transacciones Basado en OnTradeTransaction()**

Este componente captura de forma asíncrona todos los cambios de estado comercial notificados por el servidor de trading.19 Implementa un buffer dinámico para monitorizar y correlacionar órdenes asíncronas con sus transacciones reales utilizando el parámetro request\_id.10

Fragmento de código  
\#property strict

//--- Estructura interna para asociar solicitudes enviadas de forma asíncrona  
struct TAsyncRequest  
  {  
   uint     request\_id;  
   ulong    magic;  
   datetime send\_time;  
   string   symbol;  
  };

TAsyncRequest AsyncBuffer;

//+------------------------------------------------------------------+  
//| Registrar nueva orden asíncrona enviada por el EA                |  
//+------------------------------------------------------------------+  
void AddToAsyncTracker(const uint req\_id, const ulong magic, const string symbol)  
  {  
   int size \= ArraySize(AsyncBuffer);  
   ArrayResize(AsyncBuffer, size \+ 1);  
   AsyncBuffer\[size\].request\_id \= req\_id;  
   AsyncBuffer\[size\].magic      \= magic;  
   AsyncBuffer\[size\].send\_time  \= TimeCurrent();  
   AsyncBuffer\[size\].symbol     \= symbol;  
   PrintFormat(" Solicitud Asíncrona Registrada. ID: %u. Magic: %I64u", req\_id, magic);  
  }

//+------------------------------------------------------------------+  
//| Manejador de Eventos Comercial Detallado del Motor de MT5        |  
//+------------------------------------------------------------------+  
void OnTradeTransaction(const MqlTradeTransaction& trans,  
                        const MqlTradeRequest& request,  
                        const MqlTradeResult& result)  
  {  
   // 1\. CORRELACIONAR RESPUESTAS DE SOLICITUDES ASÍNCRONAS  
   if(trans.type \== TRADE\_TRANSACTION\_REQUEST)  
     {  
      int size \= ArraySize(AsyncBuffer);  
      int index \= \-1;  
        
      // Escanear el buffer de transacciones asíncronas  
      for(int i \= 0; i \< size; i++)  
        {  
         if(AsyncBuffer\[i\].request\_id \== result.request\_id)  
           {  
            index \= i;  
            break;  
           }  
        }  
          
      if(index\!= \-1)  
        {  
         PrintFormat(" Respuesta del servidor asociada al EA. Magic: %I64u. Símbolo: %s",  
                     AsyncBuffer\[index\].magic, AsyncBuffer\[index\].symbol);  
                       
         if(result.retcode \== TRADE\_RETCODE\_DONE || result.retcode \== TRADE\_RETCODE\_PLACED)  
           {  
            PrintFormat(" Ejecutada con éxito. Ticket Orden: %I64u. Ticket Deal: %I64u",  
                        result.order, result.deal);  
           }  
         else  
           {  
            PrintFormat(" El servidor rechazó el procesamiento. Código: %u", result.retcode);  
           }  
             
         // Liberar memoria del tracker local  
         for(int j \= index; j \< size \- 1; j++)  
           {  
            AsyncBuffer\[j\] \= AsyncBuffer\[j \+ 1\];  
           }  
         ArrayResize(AsyncBuffer, size \- 1);  
        }  
      return;  
     }  
       
   // 2\. SEGUIMIENTO EN TIEMPO REAL DE TRANSACCIONES FÍSICAS (DEALS)  
   if(trans.type \== TRADE\_TRANSACTION\_DEAL\_ADD)  
     {  
      if(HistoryDealSelect(trans.deal))  
        {  
         long deal\_magic \= HistoryDealGetInteger(trans.deal, DEAL\_MAGIC);  
         string symbol   \= HistoryDealGetString(trans.deal, DEAL\_SYMBOL);  
         double volume   \= HistoryDealGetDouble(trans.deal, DEAL\_VOLUME);  
         double price    \= HistoryDealGetDouble(trans.deal, DEAL\_PRICE);  
         long entry\_type \= HistoryDealGetInteger(trans.deal, DEAL\_ENTRY);  
         long pos\_id     \= HistoryDealGetInteger(trans.deal, DEAL\_POSITION\_ID);  
           
         string str\_entry \= "UNKNOWN";  
         if(entry\_type \== DEAL\_ENTRY\_IN)   str\_entry \= "ENTRADA (IN)";  
         if(entry\_type \== DEAL\_ENTRY\_OUT)  str\_entry \= "SALIDA (OUT)";  
         if(entry\_type \== DEAL\_ENTRY\_INOUT) str\_entry \= "REVERSIÓN (INOUT)";  
           
         PrintFormat(" Deal: %I64u. Símbolo: %s. Volumen: %.2f. Precio: %.5f. Entrada: %s. Posición: %I64u. Magic: %I64u",  
                     trans.deal, symbol, volume, price, str\_entry, pos\_id, deal\_magic);  
        }  
     }  
       
   // 3\. SEGUIMIENTO DE LA DESTRUCCIÓN O EXPIRACIÓN DE ÓRDENES  
   if(trans.type \== TRADE\_TRANSACTION\_ORDER\_DELETE)  
     {  
      PrintFormat(" Ticket: %I64u. Símbolo: %s. Estado de la orden en baja: %s",  
                  trans.order, trans.symbol, EnumToString(trans.order\_state));  
     }  
  }

### **3\. Reconstructor de Historial de Operaciones para Asesores Expertos por Número Mágico**

Este reconstructor utiliza consultas secuenciales en la base de datos histórica persistente para calcular de forma matemática y contable el rendimiento y las métricas de un EA basado en su número mágico.31 El algoritmo procesa transacciones tipo DEAL\_ENTRY\_IN y DEAL\_ENTRY\_OUT de forma explícita y **resuelve la limitación de la función HistorySelectByPosition en operaciones "Close By"** escaneando los identificadores secundarios DEAL\_POSITION\_ID e interceptando los tickets vinculados a través del volumen neto consolidado.31

Fragmento de código  
\#property strict

//--- Estructura analítica para consolidar el rendimiento de una posición reconstruida  
struct TReconstructedPosition  
  {  
   ulong    position\_id;  
   string   symbol;  
   datetime open\_time;  
   datetime close\_time;  
   double   volume\_net;  
   double   profit\_gross;  
   double   commission;  
   double   swap;  
   bool     is\_closed;  
  };

class CHistoryReconstructor  
  {  
public:  
   CHistoryReconstructor() {}

   //--- Reconstruye sincrónicamente el historial de operaciones de un EA basándose en su Magic Number  
   bool ReconstructHistoryByMagic(const ulong magic\_number)  
     {  
      // 1\. CARGAR SNAPSHOT HISTÓRICO COMPLETO EN LA TERMINAL CLIENTE  
      ResetLastError();  
      if(\!HistorySelect(0, TimeCurrent()))  
        {  
         PrintFormat(" Imposible construir snapshot de historial. Error API: %d", \_LastError);  
         return false;  
        }  
          
      uint total\_deals \= HistoryDealsTotal();  
      PrintFormat(" Iniciando escaneo sobre %u transacciones en caché local", total\_deals);  
        
      TReconstructedPosition positions;  
      int positions\_count \= 0;  
        
      // 2\. ESCANEAR SECUENCIALMENTE CADA TRANSACCIÓN HISTÓRICA FILTRADA POR MAGIC NUMBER  
      for(uint i \= 0; i \< total\_deals; i++)  
        {  
         ulong deal\_ticket \= HistoryDealGetTicket(i);  
         if(deal\_ticket \<= 0\) continue;  
           
         long deal\_magic \= HistoryDealGetInteger(deal\_ticket, DEAL\_MAGIC);  
         if(deal\_magic\!= (long)magic\_number) continue; // Descartar transacciones ajenas al EA  
           
         string symbol      \= HistoryDealGetString(deal\_ticket, DEAL\_SYMBOL);  
         double volume      \= HistoryDealGetDouble(deal\_ticket, DEAL\_VOLUME);  
         double commission  \= HistoryDealGetDouble(deal\_ticket, DEAL\_COMMISSION);  
         double swap        \= HistoryDealGetDouble(deal\_ticket, DEAL\_SWAP);  
         double profit      \= HistoryDealGetDouble(deal\_ticket, DEAL\_PROFIT);  
         long entry\_type    \= HistoryDealGetInteger(deal\_ticket, DEAL\_ENTRY);  
         long position\_id   \= HistoryDealGetInteger(deal\_ticket, DEAL\_POSITION\_ID);  
         datetime deal\_time \= (datetime)HistoryDealGetInteger(deal\_ticket, DEAL\_TIME);  
           
         // Verificar la existencia previa del registro de posición en la base de datos local  
         int index \= \-1;  
         for(int k \= 0; k \< positions\_count; k++)  
           {  
            if(positions\[k\].position\_id \== (ulong)position\_id)  
              {  
               index \= k;  
               break;  
              }  
           }  
             
         // Si el registro de posición no existe, inicializarlo en el arreglo dinámico  
         if(index \== \-1)  
           {  
            int size \= ArraySize(positions);  
            ArrayResize(positions, size \+ 1);  
            index \= size;  
            positions\_count++;  
              
            ZeroMemory(positions\[index\]);  
            positions\[index\].position\_id  \= (ulong)position\_id;  
            positions\[index\].symbol       \= symbol;  
            positions\[index\].open\_time    \= deal\_time;  
            positions\[index\].is\_closed    \= false;  
           }  
             
         // Consolidación aditiva de métricas financieras del trade  
         positions\[index\].commission   \+= commission;  
         positions\[index\].swap         \+= swap;  
         positions\[index\].profit\_gross \+= profit;  
           
         // Actualización del volumen neto de mercado según el tipo de flujo comercial  
         if(entry\_type \== DEAL\_ENTRY\_IN)  
           {  
            positions\[index\].volume\_net \+= volume;  
           }  
         else if(entry\_type \== DEAL\_ENTRY\_OUT)  
           {  
            positions\[index\].volume\_net \-= volume;  
              
            // Si el volumen neto se compensa y llega a cero, el trade se declara oficialmente cerrado  
            if(MathAbs(positions\[index\].volume\_net) \< 0.0001)  
              {  
               positions\[index\].is\_closed  \= true;  
               positions\[index\].close\_time \= deal\_time;  
              }  
           }  
         else if(entry\_type \== DEAL\_ENTRY\_INOUT) // Gestión de reversión neta de posición  
           {  
            positions\[index\].volume\_net \= volume \- MathAbs(positions\[index\].volume\_net);  
           }  
        }  
          
      // 3\. GENERAR INFORME ANALÍTICO DE RENDIMIENTO COMERCIAL  
      Print("==========================================================================");  
      PrintFormat("INFORME DE RENDIMIENTO AUDITADO \- EA MAGIC NUMBER: %I64u", magic\_number);  
      Print("==========================================================================");  
        
      double total\_gross\_profit \= 0;  
      double total\_commission   \= 0;  
      double total\_swap         \= 0;  
      int closed\_trades         \= 0;  
      int active\_trades         \= 0;  
        
      for(int i \= 0; i \< positions\_count; i++)  
        {  
         total\_gross\_profit \+= positions\[i\].profit\_gross;  
         total\_commission   \+= positions\[i\].commission;  
         total\_swap         \+= positions\[i\].swap;  
           
         if(positions\[i\].is\_closed)  
           {  
            closed\_trades++;  
            PrintFormat("Trade \#%I64u | Símbolo: %s | Cerrado | Duración: %d s | P\&L: %.2f | Com: %.2f | Swap: %.2f",  
                        positions\[i\].position\_id, positions\[i\].symbol,   
                        (int)(positions\[i\].close\_time \- positions\[i\].open\_time),  
                        positions\[i\].profit\_gross, positions\[i\].commission, positions\[i\].swap);  
           }  
         else  
           {  
            active\_trades++;  
            PrintFormat("Trade \#%I64u | Símbolo: %s | ABIERTO/FLOTANTE | Volumen Flotante: %.2f | P\&L Latente: %.2f",  
                        positions\[i\].position\_id, positions\[i\].symbol,   
                        positions\[i\].volume\_net, positions\[i\].profit\_gross);  
           }  
        }  
          
      double total\_net\_profit \= total\_gross\_profit \+ total\_commission \+ total\_swap;  
        
      Print("--------------------------------------------------------------------------");  
      PrintFormat("Resumen Contable Consolidado:");  
      PrintFormat("  \* Trades Reconstruidos Totales: %d (Flotantes: %d | Cerrados: %d)", positions\_count, active\_trades, closed\_trades);  
      PrintFormat("  \* Beneficio Bruto de Transacciones: %.2f", total\_gross\_profit);  
      PrintFormat("  \* Comisiones Totales Facturadas: %.2f", total\_commission);  
      PrintFormat("  \* Swaps Retenidos Totales: %.2f", total\_swap);  
      PrintFormat("  \* BENEFICIO NETO REAL DE LA CUENTA (EA): %.2f", total\_net\_profit);  
      Print("==========================================================================");  
        
      return true;  
     }  
  };

#### **Fuentes citadas**

1. difference between position history , deal history in MT5 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/507395](https://www.mql5.com/en/forum/507395)  
2. Basic principles and concepts: order, deal, and position \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_order\_deal\_position](https://www.mql5.com/en/book/automation/experts/experts_order_deal_position)  
3. Trade Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/trading](https://www.mql5.com/en/docs/trading)  
4. Sending a trade request: OrderSend and OrderSendAsync \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_ordersend\_ordersendasync](https://www.mql5.com/en/book/automation/experts/experts_ordersend_ordersendasync)  
5. Deal Properties \- Trade Constants \- Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties](https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties)  
6. how can Orders, Positions and Deals be linked together? \- How To Making Money \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/457627](https://www.mql5.com/en/forum/457627)  
7. Trade Request Structure \- Data Structures \- Constants ... \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/structures/mqltraderequest](https://www.mql5.com/en/docs/constants/structures/mqltraderequest)  
8. Placing a pending order \- Trading automation \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_pending](https://www.mql5.com/en/book/automation/experts/experts_pending)  
9. Buying and selling operations \- Trading automation \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_market\_buy\_sell](https://www.mql5.com/en/book/automation/experts/experts_market_buy_sell)  
10. OnTradeTransaction event \- Trading automation \- MQL5 ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_ontradetransaction](https://www.mql5.com/en/book/automation/experts/experts_ontradetransaction)  
11. MqlTradeRequest structure \- Trading automation \- MQL5 ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_mqltraderequest](https://www.mql5.com/en/book/automation/experts/experts_mqltraderequest)  
12. Symbol trading conditions and order execution modes \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/symbols/symbols\_execution\_filling](https://www.mql5.com/en/book/automation/symbols/symbols_execution_filling)  
13. Symbol Properties \- Environment State \- Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/environment\_state/marketinfoconstants](https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants)  
14. The Structure of a Trade Request Result (MqlTradeResult) \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/structures/mqltraderesult](https://www.mql5.com/en/docs/constants/structures/mqltraderesult)  
15. Modying Stop Loss and/or Take Profit levels of a position \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_modify\_position](https://www.mql5.com/en/book/automation/experts/experts_modify_position)  
16. Order Properties \- Trade Constants \- Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties](https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties)  
17. Discussing the article: "Advanced Order Execution Algorithms in MQL5: TWAP, VWAP, and Iceberg Orders" \- Volatility Trading Strategies, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/486550](https://www.mql5.com/en/forum/486550)  
18. Automating Trading Strategies in MQL5 (Part 18): Envelopes Trend Bounce Scalping \- Core Infrastructure and Signal Generation (Part I) \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/18269](https://www.mql5.com/en/articles/18269)  
19. OnTradeTransaction \- Event Handling \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/event\_handlers/ontradetransaction](https://www.mql5.com/en/docs/event_handlers/ontradetransaction)  
20. order\_send \- Python Integration \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/python\_metatrader5/mt5ordersend\_py](https://www.mql5.com/en/docs/python_metatrader5/mt5ordersend_py)  
21. OrderCheck \- Trade Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/trading/ordercheck](https://www.mql5.com/en/docs/trading/ordercheck)  
22. Request validation: OrderCheck \- Trading automation \- MQL5 ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_ordercheck](https://www.mql5.com/en/book/automation/experts/experts_ordercheck)  
23. Account type: netting or hedging \- Trading automation \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/account/account\_netting\_hedge](https://www.mql5.com/en/book/automation/account/account_netting_hedge)  
24. Account Properties \- Environment State \- Constants, Enumerations and Structures \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/environment\_state/accountinformation](https://www.mql5.com/en/docs/constants/environment_state/accountinformation)  
25. Structure of a Trade Transaction (MqlTradeTransaction) \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/structures/mqltradetransaction](https://www.mql5.com/en/docs/constants/structures/mqltradetransaction)  
26. Check if account is hedge \- Currency Correlation \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/98207](https://www.mql5.com/en/forum/98207)  
27. OnTrade event \- Trading automation \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_ontrade](https://www.mql5.com/en/book/automation/experts/experts_ontrade)  
28. Margin calculation for a future order: OrderCalcMargin \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_ordercalcmargin](https://www.mql5.com/en/book/automation/experts/experts_ordercalcmargin)  
29. MqlTradeCheckResult structure \- Trading automation \- MQL5 Programming for Traders, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_mqltradecheckresult](https://www.mql5.com/en/book/automation/experts/experts_mqltradecheckresult)  
30. not enough money but volume is set correct \- Limit Orders \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/441620](https://www.mql5.com/en/forum/441620)  
31. Selecting orders and deals from history \- Trading automation \- MQL5 ..., acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_history\_select](https://www.mql5.com/en/book/automation/experts/experts_history_select)  
32. HistorySelect \- Trade Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/trading/historyselect](https://www.mql5.com/en/docs/trading/historyselect)  
33. HistorySelectByPosition \- Trade Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/trading/historyselectbyposition](https://www.mql5.com/en/docs/trading/historyselectbyposition)  
34. Unsupported filling mode \- Trading Positions \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/188083](https://www.mql5.com/en/forum/188083)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAZCAYAAAB3oa15AAACN0lEQVR4Xu2WzUsVURjG38BFKX2gIkItCtxUIH4QES4KCtpGQf+AGzMMBQU3udKVEQS5qhCEalFQu6CCICj6ACnUorVBRmJQGSp+PQ/nzPWdd+bcOxclAucHD/c8z3vOmTlz5xxGJGd7cwQ6YENDvQ3+F2ahQeg6NGVqEYegNRuWohe6ZEPFVegX9BdqN7WIBuituIs/NzVyAVpR/ge0BL2EzkLnoJ/ixteofkHui5uAA6jOeLnAJ+iZ8pPQK+XJSYk/tSbjyQz0Xvk+aLdvV0IV0FHoXqFHGYQWsEeSN0KY7TPe/oN8OG+UZ58Xyp+CTitP0q6VidACPkj6pMxu+3ad9/zVPPV5xBOJv/dD0E7lxyXjq5NGaAHMQwuI8gHV1oxKPD9uvG7zlburfNlsZgGPVVszIsn8hriNygOhUeW2X9lwgss2lGwL4CmS1oc3y3y/LRgmoGrlR8Xtn2aVlYQX6rKhZFsAT420PjfF5TxdQhyDxpT/BvX79jS0Q9WKwgtdsaFkW0BoD9yR9Fyj67xZ2/+R8UE4sNuG4LckJyXMPvt2m/elTiELx+9V/oQk+88bH4QDe2wILkpyUsKs1fjzypM/0JzJInizt0x2WJLXyrSAWnEDr9mCh7UO5Yd9puHTXlY+eh0OqkyzagOPnbfoK/RA3PfIV3Ebhr/fxZ0Aml3iJn4HfYQWJH1zscYn9lBc/zPxcoEvUJUNPa9l4zgvaxP/S/g1Wgw+9UWoxRZycnJycraEdYbInw1tbm9bAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABJUlEQVR4Xu2SvUoDQRSFj0heQBCt0/jzFPoGaXyHlFG0EAMWKljbWQXBFHZCQLDxFURQsBE7SSCClWDhz7kzicxczgTUStgPDmG+OXt3sztAxX9hnTljlkfrReaUaX03JrPK3DOfTNftZewjltJcZ40yG8xHsm4iXi/ZZY6YE6bNTOfbE7GhS8IdOhew4fb3f0oD+unfoD128LsbXUEPfIT22GYOEDc7o9/jrKF5gR54B+3DB710zop7znmsowbeQHtJaUjKE3TnFtpjygvyjkI5ofSNHqB9kM/CyXKCHSLVKZ46k1vC+fIaM+ecdWaE6zkXeGVmk/UKYnkhcfZ61c37iMd5zDxip5a4DHt140GWer4dOGc2vSRDZsBcoHxtRUXFH/kC6GVSifA7GjQAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABHElEQVR4Xu2UMUtCURiG3wIJalKIAre2foGDLf6DFv+Dc7Q5urgH/YFwFwRH59ZCwSXcwqChqbDB+r57tM59fU/oGNwH3uE83/cd8Z5zL1Dwn7iwvFq+LPeW/Xz5TxqWKcJsj2o5biy30fodYegscimuLMto3UKYlXihJlxyIMJ7zoXrksPRqsCbKsdcQvcsoD06ljq5bX5oBN0zg/YSb4yfveINesMJtN/gEaHxkAtE6l8/QPscfim86ZgLgmfoDcfQ/ocyQsMBFxKkzugJ2mf4C8rFO1ozbWzOOMlb56iDZ9e0nJDzDSvCDchlfOL3YDlr9oRz5gjXec0pQk8pchnVVUHlI+pz+pZrco5/I18sQ4S5bT5dBQUFO/IN0HlWXZII+oMAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAABK0lEQVR4Xu2UPUsDURBFbxBJKzYR7NLZKFjbhHSphOB/SC1W+gcsbBRS2WplIySkTG0bULARGxEFBVsLP2Z2dsO82btiYSPsgcvyzsybfewuC9T8JzYkr5IvyZVkKS3/SEdyC9t7HmoJA8mJW5/BNm06V8Wu5NOtdZbupWghFpljaM8acYfBZTygPPQ3N9oG73kH9yX2YY29WAhMwQfeg/uE4pTHsUB4Ax94A+7nHEkuJB+Sbqgxqh7vDNyXWIU1jmMh8Ag+8BrcU6pO66l6R3fgPntUp8EVN9oK3nMAPpB+df1cxkLhFpzbkbTcWtGeZeJGwWVooenW67mbONfIXTzQE+xzLliB9Sw6N0dPpL8RbXjJr8Okw7iU7EUJ2/MMO5jubaflmpqav+Abwb1VfGd8leYAAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAZCAYAAAAv3j5gAAAA/0lEQVR4Xu2UMWoCYRCFn0UuIIKp7TyGN7DxDiaiqNh5gRReQyzSBISU3kFQsBELRRQtbLUwzjCr7IzzaxbSBPaDx7Lf/5hZ2GWBlP9Ih/Jm5RNKlBnlh9I3Z4oB5QQpct718UPalHPsvgqZ8ZSki7hfdNyHcXckWVSG//RH+F6RZNEI/sAFfK9IsugAf+AUvldwoWZlAO56A8fwvYILdSsDrOEPnMD3Ci40rAwQekdz+F7BhaaVAbrwB/76q2tZGVGh5I3jftZxQ+MUOUipZw+IDPyXv4F8zldeIZ2XmLvxSdlRVpRldN1CfktxviD/Qsse0v+GLCno45SUlL/gAnq9R8qMXCmBAAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,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>

[image7]: <data:image/png;base64,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>

[image8]: <data:image/png;base64,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>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAAZCAYAAACsGgdbAAABk0lEQVR4Xu2VyyrFURTGF4pckttYGZCBmZfwBCYGBkouuZWZvAAeAVMDL0CGkhJFiYGRMJAk5BKFb7X3Ov911tm7kz/FYP/q6+z1rXX++2vvcyFKJP4/s9CoNRXz0AP0DA2ZnsD+E/QJbZheDJ5ttaZmDXojN8gaK24XOIG2VH0M7aiaOYAG/bqKsmfWFCZK4f3LhtTEQjaS61nYa/LrSugdas/aVE9uhg8hRAt0Tr8U8pDiIZf9us/Xdi7kCez3+Ncfh4xtZP0VqEPVjJ0RVqFu+oOQljpy/QvjN0D7fp0r5Lg1KR4m5gv8KxDqf6h1rpAT1qR4mJjPTJHr8bdcswD1qjpXyElrUjxMzOcQ+rSEaujUeLlCTlsTPFI4DHt20zboxXjymeyEto3OyD1n19dl4eEZa4J+iofUV8dXe6dqIfReYZi+cZJ8Ajy8ZBse7o2oetF7Grl+q9DVC3PkZrpsQ7MO3UCX5K6FX6+p9F+iltzD9qAj6BWqUP0B3w9pU80JzdAtZfteQfdFE4lEIpEoyxfi6447a9i23AAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAZCAYAAADJ9/UkAAABc0lEQVR4Xu2UzStFURTFt5iYyISJiaTISBkaoPwFBv4BE2YoA/kaYGREDBRJSSkDUx8jpTBBib+Cga8kYu17zrnW3fe8eON3f7V6e629zzndd25XpKBSGYP2oA7v26EdaDSd+GUGeoLeoCHTC7RCF9A3dGJ6ORbEDbKuMhOOO+iY/C10Rl7pEbc+0Gl8jjloBdqGpqHqbDuhTuKbaFZv/Ah55QM6N1mKHthnQ8O1lD58w9eN3usvc+TzKFPy9+HhOiycz1LNbEk8T5iEFsUNhMH1zMT/Dj+gmlmTeJ4wDh2aTIfnjY9twPkp1cyyuLzJNkphD7M+wPku1cyquLzGNpQqG4AvKf/wUne+KfE8QRsPkYwXPBsf0Oze193el/W2a2MikvGCQeMDmnUZP0BeeYEeTZain8oG8r3iNmmjTNFsmPySzxh9yk/yeqU600xZDv3bw9OqWrLthFpxvUvoBnqX+PuivVdoX9x8f7ZdUFBQKfwAeFd4eBb4HqUAAAAASUVORK5CYII=>