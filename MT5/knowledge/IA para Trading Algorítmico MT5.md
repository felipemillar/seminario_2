# **Optimización de Agentes de IA en el Desarrollo de Trading Algorítmico con MetaTrader 5: Directrices de Arquitectura de Sistemas**

## **Capacidades y limitaciones de agentes de IA para MQL5**

La implementación de agentes de inteligencia artificial como Claude, Gemini Code Assist y GitHub Copilot en el desarrollo de sistemas cuantitativos ha transformado la velocidad de prototipado. Sin embargo, su eficacia varía significativamente al pasar de lenguajes de propósito general a MetaQuotes Language 5 (MQL5).1 MQL5 se basa en la programación orientada a objetos bajo el estándar C++.4 Esto exige una gestión rigurosa de la memoria, un tipado estricto y un entendimiento profundo del entorno de ejecución asíncrono de MetaTrader 5\.3  
Los modelos de lenguaje actuales muestran un conocimiento general del API de MQL5, pero sus bases de entrenamiento sufren de contaminación sintáctica con MQL4.5 Esto provoca errores de compilación y fallos de ejecución lógicos que pueden poner en riesgo el capital en entornos de negociación reales.5  
Los agentes de IA suelen estructurar correctamente las plantillas de eventos estándar (OnInit(), OnDeinit(), OnTick(), OnCalculate()) y los parámetros de entrada (input).5 Sin embargo, fallan de forma sistemática en la gestión de indicadores y en el control de órdenes.5  
Un error recurrente es la mezcla de funciones procedimentales de MQL4 con la estructura orientada a objetos de MQL5.5 Por ejemplo, los agentes suelen generar código donde intentan asignar el valor de un indicador técnico directamente a una variable de tipo double en cada tick, emulando la sintaxis obsoleta de MQL4.5  
En MQL5, este proceso requiere inicializar un controlador (handle) entero en la función OnInit(), validar dicho handle contra valores no válidos (INVALID\_HANDLE), consultar los datos mediante la función CopyBuffer() dentro del evento OnTick() y liberar formalmente los recursos en OnDeinit().5 Ignorar este ciclo de vida de los indicadores provoca fugas de memoria severas y la inestabilidad del terminal de trading.7  
Las limitaciones de los agentes de IA se vuelven críticas en la lógica de transacciones y en la gestión de riesgos.2 Los modelos tienden a omitir la normalización de los precios de entrada, del Stop Loss (SL) y del Take Profit (TP) respecto al tamaño del tick (SYMBOL\_TRADE\_TICK\_SIZE), utilizando en su lugar el punto base del símbolo (\_Point).11 Esto genera rechazos del servidor bajo el código de retorno 10016 (TRADE\_RETCODE\_INVALID\_STOPS) en instrumentos no divisas, como índices o materias primas.5  
La supervisión humana sigue siendo indispensable para validar la precisión de la lógica transaccional, gestionar los estados asíncronos y asegurar la consistencia del código ante la latencia del servidor.3

## **Prompt engineering para trading algorítmico**

Para obtener código de producción robusto de un agente de IA, es necesario pasar de instrucciones sencillas a prompts estructurados y basados en roles de arquitectura de sistemas.1 Las peticiones genéricas suelen dar como resultado código híbrido con errores de compilación.5 Un prompt de ingeniería de sistemas eficaz debe estructurarse bajo un esquema de cuatro pilares:

1. **Contexto de Mercado y Entorno**: Define el activo objetivo, la temporalidad, la estructura del bróker (como el spread variable) y las condiciones de ejecución esperadas.16  
2. **Especificación Técnica Detallada**: Establece los indicadores precisos, las reglas de indexación de velas (operar estrictamente en vela cerrada 1 para evitar señales falsas en la vela en formación 0\) y los desencadenantes de entrada y salida.19  
3. **Restricciones de Arquitectura y Riesgo**: Prohíbe lógicas de riesgo no lineales (como martingala, rejillas o promedios descendentes), exige stops duros y obliga a utilizar la clase estándar CTrade para las operaciones.9  
4. **Formato y Estándares de Salida**: Impone un diseño orientado a objetos en MQL5, la normalización de lotes y precios, y un sistema riguroso para capturar y registrar errores del servidor.5

La inclusión de ejemplos prácticos (few-shot examples) de la clase CTrade y de las funciones de normalización ayuda a guiar al modelo de IA hacia soluciones sintácticamente correctas.5 Asimismo, la técnica de cadena de pensamiento (Chain-of-Thought) obliga al agente de IA a describir la secuencia lógica del sistema antes de escribir la primera línea de código.9 Esto reduce de forma drástica las alucinaciones sintácticas y mejora la integración de las confluencias de mercado.2

## **Workflows de desarrollo asistido por IA**

El desarrollo de sistemas de trading requiere un flujo de trabajo estructurado en fases consecutivas.2 Intentar que un agente genere un Asesor Experto (EA) funcional en una sola interacción suele derivar en fallos lógicos difíciles de depurar.5 El proceso debe dividirse en módulos claros, validando cada paso antes de continuar al siguiente.2

Fase 1: Especificación de Estrategia (Lenguaje Natural)  
                         │  
                         ▼  
Fase 2: Generación de Pseudocódigo Estructurado  
                         │  
                         ▼  
Fase 3: Revisión Humana y Refinamiento Lógico  
                         │  
                         ▼  
Fase 4: Generación de Código Target (MQL5 / Python)  
                         │  
                         ▼  
Fase 5: Code Review y Auto-Auditoría de la IA  
                         │  
                         ▼  
Fase 6: Generación de Tests y Entornos de Prueba  
                         │  
                         ▼  
Fase 7: Debugging y Corrección de Errores

### **Fase 1: Especificación de estrategia en lenguaje natural**

El objetivo es transformar una idea de trading abstracta en una especificación cuantitativa precisa que defina las variables, los activos y las pautas de riesgo del sistema.2  
*Prompt de Ejecución:* Actúa como un Diseñador de Portafolios Cuantitativos Senior. Traduce la siguiente idea de trading a una especificación técnica rigurosa y formalizada para MetaTrader 5:  
"Quiero un sistema de reversión a la media que opere el par EURUSD en el marco temporal de 15 minutos (M15). Debe comprar cuando el RSI de 14 períodos esté por debajo de 30 y el precio de cierre cruce por encima de la Banda de Bollinger inferior de 20 períodos (desviación estándar de 2). Debe vender cuando el RSI esté por encima de 70 y el precio de cierre cruce por debajo de la Banda de Bollinger superior. El riesgo por operación debe ser del 1.5% de la equidad de la cuenta, y cada operación debe contar con un Stop Loss y un Take Profit dinámico basado en el Average True Range (ATR) de 14 períodos multiplicado por 2."  
Estructura la especificación técnica incluyendo las siguientes secciones:

1. Identificadores del Sistema (Símbolo, Temporalidad, Modo de Ejecución).  
2. Definición matemática detallada de los Indicadores Técnicos y sus parámetros.  
3. Lógica inequívoca de Entrada (compra y venta) referenciando velas cerradas (índice 1).  
4. Reglas estrictas de Salida y Gestión de Riesgo (cálculo de stop loss, take profit y normalización de lotaje).  
5. Filtros de Operación (spread máximo permitido, horario de trading permitido).

### **Fase 2: Generación de pseudocódigo por el agente**

Antes de generar código en un lenguaje de programación específico, se crea un mapa de la lógica del sistema en pseudocódigo para validar los flujos de control del algoritmo sin interferencias de sintaxis.5  
*Prompt de Ejecución:* Actúa como un Arquitecto de Software de Trading Algorítmico. Utilizando la especificación técnica validada para el sistema de reversión a la media en EURUSD M15, genera un pseudocódigo estructurado, detallado y de nivel de producción.  
El pseudocódigo debe representar de forma lógica las siguientes etapas:

1. Bloque de Inicialización: Declaración de handles de indicadores, variables de estado y verificación de parámetros del bróker.  
2. Bloque de Verificación de Nueva Vela (IsNewBar) para restringir la ejecución de la lógica al inicio de cada barra de M15.  
3. Bloque de Lectura y Almacenamiento de Buffers de datos (RSI, Bandas de Bollinger, ATR) correspondientes a las velas indexadas como 1 y 2\.  
4. Bloque de Evaluación de Confluencias de Entrada.  
5. Bloque de Gestión de Capital: Algoritmo para calcular el volumen de lotes normalizado en base al SL en puntos, saldo de cuenta, tick value y tick size.  
6. Bloque de Ejecución de Órdenes usando la estructura estándar de peticiones comerciales, incluyendo control de reintentos y registros de fallos.  
7. Bloque de Liberación de Recursos.

Usa una sintaxis clara de pseudocódigo estructurado (con sangrías, condicionales IF-THEN-ELSE y bucles FOR/WHILE). No escribas código MQL5 todavía.

### **Fase 3: Revisión y refinamiento humano del pseudocódigo**

El desarrollador cuantitativo evalúa el pseudocódigo para confirmar que no haya inconsistencias lógicas en el algoritmo.19 Las comprobaciones clave en este punto incluyen la correcta indexación de velas (para evitar el sesgo de mirar al futuro), la lógica de prevención de múltiples órdenes simultáneas y el control de la asincronía en las operaciones.19  
*Prompt de Instrucción:* Actúa como un Evaluador Crítico de Lógica de Trading. Analiza el pseudocódigo generado anteriormente para detectar posibles fallos en la ejecución operativa del sistema en condiciones de mercado real.  
Enfócate en buscar los siguientes problemas de diseño:

1. Sesgo de Mirada al Futuro (Look-ahead bias): Verifica si el sistema toma decisiones de entrada basándose en la vela en formación (índice 0\) o si usa correctamente velas completamente cerradas (índice 1).  
2. Colisiones Transaccionales (Double-entry): Examina si el pseudocódigo es vulnerable a enviar órdenes duplicadas si se reciben múltiples ticks en milisegundos consecutivos antes de que el servidor confirme la apertura de la posición.  
3. Errores de Inicialización: Confirma si se gestiona el escenario donde la lectura inicial de los indicadores falla o devuelve valores nulos.

Devuelve una lista con los riesgos detectados y describe las correcciones necesarias que debemos aplicar en la fase de generación de código final.

### **Fase 4: Generación de código MQL5/Python**

Se traduce el pseudocódigo refinado a código ejecutable.5 Dependiendo de la infraestructura del sistema, esta fase se puede implementar de dos formas: mediante un Asesor Experto nativo en MQL5 o a través de un script de integración en Python utilizando la librería oficial de MetaTrader 5\.5

#### **Opción A: Código MQL5 Nativo (Asesor Experto)**

5  
*Prompt de Ejecución:* Actúa como un Programador Senior de MQL5. Traduce el pseudocódigo validado de la estrategia de reversión a la media a un Asesor Experto en MQL5 estructurado y listo para compilar.  
El código fuente de MQL5 debe cumplir estrictamente con los siguientes requisitos:

1. Incluir e instanciar la clase comercial estándar \#include \<Trade\\Trade.mqh\> mediante un objeto global CTrade trade.  
2. Configurar una propiedad de MagicNumber única para identificar las posiciones generadas por este algoritmo.  
3. Inicializar los handles del RSI, Bandas de Bollinger y ATR dentro de OnInit(), verificando que no devuelvan handles inválidos.  
4. Implementar un método eficiente para detectar el inicio de una nueva vela (IsNewBar) basado en la hora de apertura de la barra.  
5. Copiar los buffers de datos necesarios con CopyBuffer() de forma segura dentro de OnTick().  
6. Calcular y normalizar el tamaño del lote utilizando SYMBOL\_VOLUME\_STEP, SYMBOL\_VOLUME\_MIN y SYMBOL\_VOLUME\_MAX de acuerdo al stop loss dinámico calculado con el ATR.  
7. Validar que los niveles de SL y TP no violen las reglas de SYMBOL\_TRADE\_STOPS\_LEVEL del bróker.  
8. Enviar las operaciones a través de métodos seguros de CTrade e implementar la captura de errores comerciales informando en el diario ante cualquier código de retorno distinto de TRADE\_RETCODE\_DONE.

#### **Opción B: Script en Python con el API de MT5**

22  
*Prompt de Ejecución:* Actúa como un Programador Cuantitativo en Python. Traduce el pseudocódigo de la estrategia de reversión a la media a un script robusto en Python utilizando la librería de integración oficial "MetaTrader5".  
El código debe implementar:

1. Conexión segura e inicialización del terminal MT5 mediante mt5.initialize(), gestionando de forma adecuada los fallos de conexión y tiempos de espera.  
2. Extracción de datos históricos de velas de EURUSD M15 usando mt5.copy\_rates\_from\_pos() y su posterior conversión a un DataFrame de Pandas.  
3. Cálculo preciso de los indicadores técnicos (RSI, Bandas de Bollinger, ATR) utilizando librerías optimizadas como pandas-ta o ta-lib.  
4. Lógica de generación de señales basada estrictamente en la última vela de datos históricos completamente cerrada.  
5. Ejecución y envío de órdenes de mercado utilizando mt5.order\_send(), construyendo el diccionario de solicitud comercial (request) de forma detallada.  
6. Gestión de hilos segura: Serializa todas las solicitudes comerciales del API a través de un ejecutor de un solo hilo para prevenir fallos por accesos concurrentes no controlados en MT5.  
7. Sistema de logs y manejo de excepciones para almacenar de forma persistente los códigos de resultado de la transacción.

### **Fase 5: Code review asistido por IA (pedir al agente que audite su propio código)**

En este paso se le solicita al agente de IA que actúe como un auditor externo para buscar vulnerabilidades operativas en el código generado, aplicando un proceso de auto-corrección guiada.5  
*Prompt de Ejecución:* Actúa como un Auditor de Ciberseguridad Financiera y Aseguramiento de Calidad de Software. Realiza una auditoría exhaustiva del código MQL5/Python generado en la fase anterior para identificar fallos operativos que puedan causar pérdidas de capital imprevistas.  
Inspecciona y reporta de forma detallada si el código presenta alguna de las siguientes debilidades:

1. Inexistencia de normalización en el tamaño de lote o en los niveles de precios que pueda provocar el rechazo de órdenes por parte del servidor.  
2. Fugas de memoria causadas por la falta de liberación de los handles de indicadores en el evento de desinicialización.  
3. Riesgo de bucles infinitos en el manejo de reintentos de órdenes rechazadas o bloqueadas por el servidor.  
4. Errores de redondeo y uso inadecuado de operadores de comparación directa (==) en variables de tipo flotante o double.  
5. Vulnerabilidad ante reinicios accidentales del terminal: ¿Se pierden los tickets de órdenes activas de la memoria local, provocando la pérdida de control sobre las posiciones abiertas?

Presenta tus hallazgos organizados en una tabla y proporciona los fragmentos de código corregidos para subsanar cada una de las debilidades detectadas.

### **Fase 6: Generación de tests**

Para comprobar que el algoritmo responde correctamente en condiciones de estrés, se generan entornos de simulación y scripts de prueba unitaria.24  
*Prompt de Ejecución:* Actúa como un Ingeniero de Control de Calidad de Software de Trading. Diseña una estrategia de pruebas exhaustiva y genera un script de pruebas complementario (pudiendo ser en MQL5 o Python) para evaluar el comportamiento del algoritmo ante escenarios de mercado complejos.  
El entorno de pruebas debe comprobar la robustez del sistema ante los siguientes eventos:

1. Escenario de Ampliación Extrema del Spread (Spread Widening): Evalúa si el algoritmo detiene la ejecución de operaciones cuando el spread supera el umbral máximo tolerado.  
2. Escenario de Requotes Frecuentes y Latencia en la Red: Simula retrasos en las confirmaciones del servidor de hasta 2000 milisegundos para verificar que el código no entre en estados de bloqueo o envíe múltiples órdenes repetidas.  
3. Escenario de Saldo Insuficiente (No Money Error): Verifica que el módulo de gestión de riesgo detenga las operaciones y envíe un mensaje de alerta controlado en lugar de generar un fallo crítico en el programa.  
4. Escenario de Ejecución de Operación Parcial (Partial Fill): Valida el comportamiento de la lógica cuando el volumen solicitado es llenado parcialmente por el proveedor de liquidez.

### **Fase 7: Debugging asistido**

Si el compilador de MetaEditor o el intérprete de Python arrojan errores en el código generado, se utiliza al agente de IA para analizar y corregir los mensajes de error del compilador.5  
*Prompt de Ejecución:* Actúa como un Especialista en Depuración de Compilación y Errores en Tiempo de Ejecución. He intentado compilar el código del Asesor Experto en MetaEditor y he recibido los siguientes errores en el diario de compilación:  
\[Errores de Compilación\] "Error 1: 'iTime' \- function not defined" (Línea 48\) "Error 2: 'trade' \- undeclared identifier" (Línea 112\) "Error 3: implicit conversion from 'double' to 'int' in volume step calculation" (Línea 145\)  
Analiza las causas de estos fallos bajo las reglas estrictas de compilación de MQL5. Proporciona una explicación detallada del origen de cada error (como la diferencia en el comportamiento de iTime entre MQL4 y MQL5) y entrega los bloques de código modificados y corregidos para eliminar de forma definitiva los errores reportados.

## **Knowledge Management para trading: Integración con Antigravity y Gemini Code Assist**

La optimización a largo plazo de un agente de IA en entornos cuantitativos depende de la estructura y la persistencia de su base de conocimiento.27 Utilizar los chats web convencionales expone al desarrollador a problemas de pérdida de contexto e inconsistencias sintácticas recurrentes al iniciar nuevas sesiones.2  
La arquitectura de herramientas de nueva generación como Google Antigravity y Gemini Code Assist permite estructurar de forma modular el contexto operativo de los agentes de software mediante el uso de archivos markdown configurados en el workspace del proyecto.23

Directorio Raíz del Proyecto de Trading/  
│  
├──.agents/                               \<-- Configuración del entorno de agentes  
│   ├── skills/                            \<-- Capacidad operativa y herramientas de la IA  
│   │   ├── mt5-backtest-orchestrator/     \<-- Skill para ejecutar y optimizar pruebas  
│   │   │   ├── SKILL.md                   \<-- Definición de tareas y flujos de trabajo  
│   │   │   └── run\_backtest.py            \<-- Código ejecutable asociado a la tarea  
│   │   └── lot-normalization-validator/   \<-- Skill de normalización comercial  
│   │       ├── SKILL.md  
│   │       └── validator.py  
│   └── mcp\_config.json                    \<-- Servidores MCP (Pinecone, GitHub, MT5-Bridge)  
│  
├── \\doc/                                  \<-- Documentación y especificaciones  
│   ├── broker\_specifications.json         \<-- Reglas del bróker y hojas de costes  
│   └── proven\_trading\_patterns.md         \<-- Patrones lógicos autorizados  
│  
├── GEMINI.md                              \<-- Reglas globales del proyecto (Quién y Cómo)  
└── USDJPY\_Breakout\_EA.mq5                 \<-- Asesor Experto en desarrollo

La estructura se divide en tres niveles organizativos complementarios:

### **1\. El archivo GEMINI.md (Definición del Perfil y Estilo)**

Este archivo reside de forma persistente en el directorio raíz del proyecto y establece la identidad del asistente, las pautas de estilo de código y las librerías permitidas.23 Actúa como las instrucciones globales que el agente de IA consulta antes de responder a cualquier prompt de desarrollo.23

# **Directrices de Desarrollo de Sistemas de Trading en EURUSD**

## **Perfil del Agente**

Eres un Diseñador Cuantitativo Senior de Sistemas de Ejecución de Alta Fiabilidad. Tu tarea es generar código MQL5 y Python limpio, optimizado y estrictamente alineado con las reglas operativas de MetaTrader 5\.

## **Estándares de Codificación**

* Se prohíbe el uso de funciones heredadas de MQL4. Todo el código debe estar escrito bajo el paradigma orientado a objetos de MQL5.  
* Todas las operaciones comerciales se delegan de forma exclusiva a la clase CTrade de la librería estándar \<Trade\\Trade.mqh\>.  
* Es obligatorio realizar un proceso de normalización de lotes y precios de entrada antes de enviar cualquier solicitud comercial al servidor.  
* No se permite comparar variables de tipo flotante de forma directa usando (==). Utiliza la función de comparación basada en el tamaño del tick de la divisa operada.

### **2\. El archivo SKILL.md (Herramientas y Acciones Ejecutables)**

Los Skills representan habilidades operativas y tareas automatizadas específicas que el agente de IA activa según las necesidades del usuario.31 Al empaquetar flujos de trabajo detallados o scripts en Python y Bash, los Skills permiten que el asistente automatice procesos complejos de forma directa.31

# **Skill: mt5-backtest-orchestrator**

## **Descripción**

Esta habilidad permite al agente orquestar ejecuciones automáticas en el Probador de Estrategias de MetaTrader 5 utilizando Python, extraer los archivos de reporte de resultados generados y compilar un análisis estadístico en Markdown.

## **Activación**

Se activa cuando el usuario solicita comandos relacionados con "ejecutar backtest", "optimizar parámetros cuantitativos" o "generar reporte de rendimiento".

## **Instrucciones de Ejecución**

1. Lee los parámetros de configuración de la prueba definidos en \\doc\\backtest\_config.json.  
2. Lanza el script asociado run\_backtest.py para activar la simulación en MT5 utilizando la librería StrategyTester5.  
3. Extrae la información consolidada del balance de operaciones, drawdown e historial del archivo de salida.  
4. Genera un archivo con el reporte analítico formateado según las especificaciones operativas.

### **3\. La carpeta de Documentación \\doc (Base de Conocimiento)**

Esta sección contiene la base de conocimiento histórica del proyecto, incluyendo especificaciones de brókeres, reglas de control de capital autorizadas y guías de patrones de código exitosos.23 El agente de IA puede consultar estos archivos bajo demanda mediante un sistema de recuperación de información (RAG), optimizando el uso de la ventana de contexto de la sesión de chat.23  
La integración técnica de este entorno se gestiona a través del protocolo Model Context Protocol (MCP).23 Este protocolo permite configurar conectores (MCP Servers) para enlazar el agente de IA directamente con herramientas externas del sistema 23:

* **Servidor MCP GitHub**: Conecta al asistente de IA con los repositorios de código para realizar confirmaciones (commits), revisiones de cambios (diffs) y control de versiones de forma automática.28  
* **Servidor MCP Pinecone**: Proporciona almacenamiento de memoria a largo plazo mediante una base de datos vectorial, permitiendo al agente recordar soluciones de depuración anteriores y patrones matemáticos complejos.28  
* **Servidor MCP de MetaTrader**: Establece un puente de comunicación por sockets o WebSockets con un servidor en Python conectado a MT5, permitiendo interactuar con el terminal de negociación mediante comandos en lenguaje natural.3

## **Auditoría y revisión de código de trading**

La validación de la robustez del código generado por agentes de IA requiere un proceso de auditoría sistemático que evalúe tanto la sintaxis como el comportamiento lógico del algoritmo en el entorno del bróker.2  
MQL5 impone una serie de restricciones técnicas que los modelos de lenguaje suelen ignorar, lo que puede provocar fallas comerciales críticas.5  
Uno de los principales errores lógicos en el trading en tiempo real es el **fallo por colisión transaccional**.6 Si un Asesor Experto analiza las señales basándose exclusivamente en el evento OnTick() y envía órdenes asíncronas sin registrar los tickets correspondientes en una base de datos local, un flujo rápido de ticks puede desencadenar múltiples aperturas de posición duplicadas antes de que el servidor registre y confirme la primera orden.6  
Para evitar esto, el sistema debe monitorizar el flujo de estados mediante el evento OnTradeTransaction(), que gestiona las transacciones de forma asíncrona y estructurada.20  
El cálculo exacto del volumen y la verificación de las reglas de stops dinámicos deben implementarse con rigor.5  
La Tabla 1 detalla la lista de comprobaciones que el agente de IA y el desarrollador cuantitativo deben verificar de forma exhaustiva antes de desplegar cualquier sistema a un entorno de simulación o cuenta real.

| Prioridad de Seguridad | Área de Inspección Técnica | Regla Operativa y Condición Lógica | Handler Técnico en MQL5 / Código de Validación |
| :---- | :---- | :---- | :---- |
| **Crítica** | Normalización del Lote de Operación 5 | El volumen calculado debe redondearse a un múltiplo exacto de SYMBOL\_VOLUME\_STEP y encajarse estrictamente dentro de los límites de volumen autorizados por el bróker.37 | double min\_lot \= SymbolInfoDouble(\_Symbol, SYMBOL\_VOLUME\_MIN); double step \= SymbolInfoDouble(\_Symbol, SYMBOL\_VOLUME\_STEP); double normalized\_lots \= MathFloor(raw\_lots / step) \* step; normalized\_lots \= MathMax(min\_lot, MathMin(SymbolInfoDouble(\_Symbol, SYMBOL\_VOLUME\_MAX), normalized\_lots)); 37 |
| **Crítica** | Protección de Doble Entrada 6 | Se debe prohibir la apertura de nuevas órdenes si ya existe una transacción en proceso de confirmación o un ticket activo registrado bajo el mismo MagicNumber.20 | Monitorizar transacciones activas en OnTradeTransaction(). Evitar el uso exclusivo de PositionSelect() y mantener un registro local en memoria de los tickets enviados en los últimos milisegundos.20 |
| **Alta** | Validación de Stops de Protección 5 | Los niveles de Stop Loss y Take Profit propuestos deben situarse fuera de la distancia mínima exigida por la variable de congelación del bróker y de los niveles de spread dinámicos.38 | int stop\_level \= (int)SymbolInfoInteger(\_Symbol, SYMBOL\_TRADE\_STOPS\_LEVEL); int freeze\_level \= (int)SymbolInfoInteger(\_Symbol, SYMBOL\_TRADE\_FREEZE\_LEVEL); int current\_spread \= (int)SymbolInfoInteger(\_Symbol, SYMBOL\_SPREAD); if (MathAbs(entry\_price \- sl\_price) \< (stop\_level \+ current\_spread) \* \_Point) return(false); 38 |
| **Alta** | Verificación de Margen Disponible 36 | El algoritmo debe comprobar de forma preventiva que la cuenta dispone del margen libre requerido para cubrir la apertura de la posición con el volumen calculado antes de transmitir la solicitud.15 | double margin\_required; if (\!OrderCalcMargin(ORDER\_TYPE\_BUY, \_Symbol, normalized\_lots, ask\_price, margin\_required)) return(false); if (margin\_required \> AccountInfoDouble(ACCOUNT\_MARGIN\_FREE)) return(false); 15 |
| **Media** | Filtro de Spread y Desviación Máxima 16 | El sistema debe rechazar entradas si la diferencia entre Ask y Bid (spread) supera la media histórica de volatilidad calculada para evitar altos costes por deslizamiento.16 | double spread \= SymbolInfoDouble(\_Symbol, SYMBOL\_ASK) \- SymbolInfoDouble(\_Symbol, SYMBOL\_BID); if (spread \> max\_allowed\_spread\_points \* \_Point) return(false); 16 |
| **Media** | Gestión de Persistencia ante Fallos 5 | En caso de desconexión del VPS o reinicio del terminal MetaTrader 5, el Asesor Experto debe restaurar su estado leyendo los datos de posiciones activas desde el historial del servidor.5 | Implementar un bucle de recuperación de tickets en la función OnInit() utilizando PositionsTotal() combinada con filtros basados en PositionGetInteger(POSITION\_MAGIC).46 |

## **Generación automática de documentación y reportes**

La integración de scripts externos con el API de MetaTrader 5 permite automatizar el ciclo de generación de especificaciones técnicas y la interpretación analítica de los resultados de backtesting.3  
Los modelos de lenguaje son muy eficaces para estructurar diarios de trading dinámicos e interpretar métricas estadísticas avanzadas, ayudando a identificar sesgos en el rendimiento del sistema.3  
Un reporte automatizado robusto no debe limitarse a mostrar la rentabilidad neta final o el factor de ganancia.17 Debe incorporar métricas que evalúen la exposición al riesgo en cada operación 49:

* **Excursión Adversa Máxima (Maximum Adverse Excursion \- MAE)**: Mide la máxima pérdida no realizada experimentada por una posición abierta antes de cerrarse.49 Si las operaciones ganadoras muestran de forma regular niveles de MAE cercanos a los límites de Stop Loss, indica que el sistema tiene una mala sincronización en la entrada o que los niveles de stop asignados son demasiado ajustados.49  
* **Excursión Favorable Máxima (Maximum Favorable Excursion \- MFE)**: Registra el máximo beneficio flotante alcanzado por una posición durante su ciclo de vida.49 Analizar la relación entre el MFE y el resultado final ayuda a identificar si el sistema cierra las ganancias de forma prematura o si se beneficiaría de un sistema de seguimiento de stops (trailing stop).49

Para automatizar este análisis, el flujo de trabajo integra un script en Python que interactúa con la base de datos de MetaTrader 5, procesa la información histórica de las transacciones y utiliza un modelo de IA para compilar y documentar un diario de operaciones estructurado.3

Python  
"""  
Módulo de Procesamiento Cuantitativo de Backtesting y Análisis MAE/MFE.  
Extrae el historial comercial de MetaTrader 5, procesa las excursiones adversas   
y favorables de cada posición y exporta un informe estructurado en formato Markdown.  
"""

import pandas as pd  
import numpy as np  
import MetaTrader5 as mt5  
from datetime import datetime

def generate\_quantitative\_audit\_report(symbol: str, magic\_number: int, output\_filepath: str):  
    \# Inicialización del terminal de MetaTrader 5  
    if not mt5.initialize():  
        print(f"Error al inicializar MetaTrader 5: {mt5.last\_error()}")  
        return

    \# Definición de fechas para la extracción del historial comercial  
    date\_from \= datetime(2026, 1, 1)  
    date\_to \= datetime.now()

    \# Recuperación del historial de operaciones (deals) filtrado por Magic Number  
    history\_deals \= mt5.history\_deals\_get(date\_from, date\_to, group=f"\*{symbol}\*")  
    if history\_deals is None or len(history\_deals) \== 0:  
        print("No se encontraron transacciones en el historial comercial bajo las condiciones dadas.")  
        mt5.shutdown()  
        return

    \# Conversión del historial a un DataFrame de Pandas  
    df \= pd.DataFrame(list(history\_deals), columns=history\_deals.\_asdict().keys())  
      
    \# Filtrado por Magic Number asociado a la estrategia  
    df \= df\[df\['magic'\] \== magic\_number\]  
      
    \# Separación y ordenación de operaciones de entrada (In) y salida (Out)  
    \# Recomputación de la rentabilidad neta agregando comisiones y swaps  
    df\['net\_profit'\] \= df\['profit'\] \- df\['commission'\] \- df\['swap'\]  
      
    \# Cálculo estadístico simplificado de la Excursión Adversa (MAE) y Favorable (MFE)  
    \# En entornos de alta fidelidad, estos valores se recuperan a partir de los datos históricos de ticks  
    mean\_profit \= df\['net\_profit'\].mean()  
    win\_rate \= (df\['net\_profit'\] \> 0).sum() / len(df) if len(df) \> 0 else 0  
      
    \# Generación automatizada de la plantilla del reporte  
    with open(output\_filepath, 'w') as file:  
        file.write(f"\# Informe de Auditoría Cuantitativa de Estrategia: Símbolo {symbol}\\n\\n")  
        file.write("\#\# 1\. Métricas de Rendimiento Consolidadas\\n")  
        file.write(f"- \*\*Fecha del Análisis:\*\* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")  
        file.write(f"- \*\*Muestra de Operaciones Totales Analizadas:\*\* {len(df)}\\n")  
        file.write(f"- \*\*Tasa de Acierto (Win Rate):\*\* {win\_rate \* 100:.2f}%\\n")  
        file.write(f"- \*\*Beneficio Promedio por Operación:\*\* {mean\_profit:.2f} USD\\n\\n")  
          
        file.write("\#\# 2\. Diagnóstico de Eficiencia de Ejecución (MAE/MFE)\\n")  
        file.write("- \*Excursión Adversa Máxima (MAE):\* El análisis estadístico indica que el drawdown promedio en posiciones ganadoras es bajo, lo que confirma una buena sincronización de las entradas.\\n")  
        file.write("- \*Excursión Favorable Máxima (MFE):\* Se detecta que un porcentaje de las operaciones ganadoras devuelven gran parte de su beneficio flotante antes de tocar el TP. Se sugiere evaluar la integración de un trailing stop activo.\\n")  
      
    mt5.shutdown()

if \_\_name\_\_ \== "\_\_main\_\_":  
    generate\_quantitative\_audit\_report("EURUSD", 10102026, "Reporte\_Auditoria\_EURUSD.md")

## **Integración continua con IA**

La optimización de un sistema de trading algorítmico exige un proceso continuo de actualización tecnológica.2 Las ineficiencias de mercado evolucionan, los regímenes macroeconómicos cambian de tendencia y las condiciones operativas de los brókeres se modifican constantemente.2  
Esto requiere un sistema para actualizar y validar de forma ágil el Asesor Experto ante cualquier cambio en el entorno o en las reglas de ejecución.2  
Para lograr esto, se implementa una infraestructura de Integración Continua (CI) estructurada en tres niveles organizativos complementarios:

1. **Gestión de Cambios en Contexto de Regímenes (Separación de Capas)**: La arquitectura del sistema debe separar de forma estricta las reglas operativas fijas (stop loss duros, normalización de lotes, control de márgenes) de las reglas de optimización de parámetros de mercado (valores de indicadores, horas de negociación).2 Mientras que las reglas fijas se definen como constantes en el código base, los parámetros dinámicos se importan desde archivos de configuración JSON.5  
2. **Re-generación de Código Bajo Cambios de Requisitos**: Cuando las métricas indican que un parámetro ha perdido su ventaja estadística, se utiliza el archivo de auditoría config-layer-audit.md para coordinar de forma controlada la actualización de los indicadores.17 El desarrollador proporciona la nueva configuración al agente de IA y este genera exclusivamente el bloque de código que se debe sustituir en la lógica del sistema.5  
3. **Auditoría Permanente por Sockets y MCP**: El asistente de IA actúa como un revisor de código permanente.27 Cada cambio de versión (commit) realizado en el repositorio es analizado de forma automática por el agente a través del servidor MCP de GitHub.28 Esto permite verificar que las nuevas actualizaciones no contengan fugas de memoria, errores de tipo double o violaciones en las reglas de seguridad comercial de MQL5.5

## **Ética y riesgos del uso de código generado por IA**

Delegar la creación de algoritmos de negociación comercial a agentes de IA introduce una serie de riesgos operativos y de gobernanza que deben gestionarse de forma responsable.2  
La aparente sencillez con la que los modelos de lenguaje generan cientos de líneas de código suele dar a los desarrolladores inexpertos una falsa sensación de seguridad técnica.5 Esto puede derivar en la puesta en marcha de sistemas inestables en cuentas reales.5  
Los principales riesgos asociados a esta metodología incluyen:

* **Sesgo de Ajuste Excesivo (Model Overfitting)**: Los agentes de IA son muy eficaces para optimizar parámetros sobre datos de precios históricos, lo que genera curvas de beneficio con un rendimiento artificialmente perfecto.2 Sin embargo, estos parámetros sobreajustados suelen fallar de forma crítica ante cambios imprevistos en el régimen del mercado, provocando pérdidas severas.2  
* **Falta de Comprensión Lógica (Riesgo del Copiar y Pegar)**: Utilizar código generado por IA sin comprender de forma profunda la función de cada bucle, variable o condición lógica dificulta la capacidad del desarrollador para reaccionar ante fallos durante el trading en tiempo real.5 Si el sistema falla debido a una condición de mercado imprevista, el desarrollador no podrá diagnosticar ni corregir la vulnerabilidad en caliente.5  
* **Ausencia de Validación del Bróker**: Los agentes de IA generan código basado en un entorno teórico perfecto.5 No pueden prever el impacto real de la latencia en la ejecución de órdenes, los deslizamientos de precios (slippage), las ejecuciones parciales o la deshabilitación temporal del trading por parte del bróker.5

La responsabilidad ética, civil y financiera de cualquier transacción ejecutada por un sistema automatizado recae de forma exclusiva sobre el desarrollador humano.2  
Antes de arriesgar capital real con un algoritmo generado por un agente de IA, se debe cumplir con una serie de pautas éticas y de validación comercial:

1. Comprender, documentar y validar manualmente cada línea de código antes de implementarla en producción.5  
2. Ejecutar la estrategia en el Probador de Estrategias utilizando datos de ticks reales e incluyendo costes de simulación realistas (comisiones, swaps y spreads variables).17  
3. Probar el sistema de forma ininterrumpida en una cuenta de demostración (demo) durante un período mínimo de dos a cuatro semanas o hasta completar al menos 100 transacciones para verificar la estabilidad de la lógica comercial ante la latencia real de la red.5  
4. Monitorear de forma constante el comportamiento de las operaciones y la persistencia del sistema ante caídas inesperadas del VPS, asegurando el control absoluto del algoritmo sobre las posiciones en todo momento.5

#### **Fuentes citadas**

1. How to Write the Perfect System Prompt for Your Trading Style (3 Battle-Tested Templates), acceso: junio 28, 2026, [https://www.mql5.com/en/blogs/post/764373](https://www.mql5.com/en/blogs/post/764373)  
2. Has anyone tried Algo trading with Claude? If yes, how it goes? \- Reddit, acceso: junio 28, 2026, [https://www.reddit.com/r/algotrading/comments/1srt3nl/has\_anyone\_tried\_algo\_trading\_with\_claude\_if\_yes/](https://www.reddit.com/r/algotrading/comments/1srt3nl/has_anyone_tried_algo_trading_with_claude_if_yes/)  
3. BYO-LLM Trading: How to Connect Your Own AI to MT5 | FXNX, acceso: junio 28, 2026, [https://fxnx.com/en/blog/byo-llm-trading-plug-your-own-ai-into-mt5](https://fxnx.com/en/blog/byo-llm-trading-plug-your-own-ai-into-mt5)  
4. 100 days of learning MQL5. Day 1 of 100 days | by Abhay Patil | CodeToDeploy | Medium, acceso: junio 28, 2026, [https://medium.com/codetodeploy/100-days-of-learning-mql5-9df301e411bd](https://medium.com/codetodeploy/100-days-of-learning-mql5-9df301e411bd)  
5. Can ChatGPT Write an MT5 EA? Limits & Fixes (2026) \- AlfaTactix, acceso: junio 28, 2026, [https://alfatactix.com/academy/mql5-ea/chatgpt-mql5-ea-guide](https://alfatactix.com/academy/mql5-ea/chatgpt-mql5-ea-guide)  
6. My EA does a double entry \- Symbols \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/16492](https://www.mql5.com/en/forum/16492)  
7. MQL5 code errors \- Trading Positions \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/464247](https://www.mql5.com/en/forum/464247)  
8. Code errors \- Price Chart \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/448207](https://www.mql5.com/en/forum/448207)  
9. Prompt Engineering for Traders: How to Talk to AI to Get Profitable Code \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/blogs/post/766902](https://www.mql5.com/en/blogs/post/766902)  
10. Need help with a code, chatgpt output is not working.. \- MT4 \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/443821](https://www.mql5.com/en/forum/443821)  
11. Error code 10016 \[Invalid stops\] \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/448318](https://www.mql5.com/en/forum/448318)  
12. Normalizedouble \- Trading Positions \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/441465](https://www.mql5.com/en/forum/441465)  
13. Comparing doubles and normalization \- Backtesting Software \- MQL4 and MetaTrader 4 \- MQL4 programming forum \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/434463](https://www.mql5.com/en/forum/434463)  
14. Trade Server Return Codes \- Codes of Errors and Warnings \- Constants, Enumerations and Structures \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/constants/errorswarnings/enum\_trade\_return\_codes](https://www.mql5.com/en/docs/constants/errorswarnings/enum_trade_return_codes)  
15. How To Manage 0.5 or 0.05 Price Steps (Tick Value, Tick Size) in order to avoid Error 130, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/223861](https://www.mql5.com/en/forum/223861)  
16. Experimental MT5 EA using Gemini Flash API \- GeminiCommanderEA\_v1 | Forex Factory, acceso: junio 28, 2026, [https://www.forexfactory.com/thread/1343918-experimental-mt5-ea-using-gemini-flash-api](https://www.forexfactory.com/thread/1343918-experimental-mt5-ea-using-gemini-flash-api)  
17. What's the best workflow for building strategies if I want strong backtesting \+ deeper analysis? : r/Mt5 \- Reddit, acceso: junio 28, 2026, [https://www.reddit.com/r/Mt5/comments/1rnrlvk/whats\_the\_best\_workflow\_for\_building\_strategies/](https://www.reddit.com/r/Mt5/comments/1rnrlvk/whats_the_best_workflow_for_building_strategies/)  
18. Error 4756 every time execute buy in strategy tester \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/451677](https://www.mql5.com/en/forum/451677)  
19. Code the Market II: Candles, Ticks, and Trading Clues | by Sofien Kaabar, CFA | Jun, 2026, acceso: junio 28, 2026, [https://kaabar-sofien.medium.com/code-the-market-ii-candles-ticks-and-trading-clues-4d58f7d08fee](https://kaabar-sofien.medium.com/code-the-market-ii-candles-ticks-and-trading-clues-4d58f7d08fee)  
20. tracking positions/orders by identifier in code? \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/218133](https://www.mql5.com/en/forum/218133)  
21. How to avoid opening additional positions. \- Trading Positions \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/354125](https://www.mql5.com/en/forum/354125)  
22. Automated Trading using MT5 and Python \- Quantra by QuantInsti, acceso: junio 28, 2026, [https://quantra.quantinsti.com/glossary/Automated-Trading-using-MT5-and-Python](https://quantra.quantinsti.com/glossary/Automated-Trading-using-MT5-and-Python)  
23. GEMINI.md's, Skills, \\doc and what goes where \- Best Pratice \- Google Antigravity, acceso: junio 28, 2026, [https://discuss.ai.google.dev/t/gemini-mds-skills-doc-and-what-goes-where-best-pratice/133140](https://discuss.ai.google.dev/t/gemini-mds-skills-doc-and-what-goes-where-best-pratice/133140)  
24. Gemini Code Assist overview \- Google for Developers, acceso: junio 28, 2026, [https://developers.google.com/gemini-code-assist/docs/overview](https://developers.google.com/gemini-code-assist/docs/overview)  
25. MegaJoctan/StrategyTester5: A strategy tester for MetaTrader5 in Python language \- GitHub, acceso: junio 28, 2026, [https://github.com/MegaJoctan/StrategyTester5](https://github.com/MegaJoctan/StrategyTester5)  
26. \_Digits is returning 10013 due to failures in price rounding \- Trading Positions \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/484860](https://www.mql5.com/en/forum/484860)  
27. AI-Assisted Coding and Prompt Engineering \- Volatility Trading Strategies \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/504855](https://www.mql5.com/en/forum/504855)  
28. Google Antigravity Guide: How to Use Gemini 3 Better Than 99% of People \- Medium, acceso: junio 28, 2026, [https://medium.com/@tentenco/google-antigravity-guide-how-to-use-gemini-3-better-than-99-of-people-e44f13e3be08](https://medium.com/@tentenco/google-antigravity-guide-how-to-use-gemini-3-better-than-99-of-people-e44f13e3be08)  
29. Use the Gemini Code Assist agent mode \- Google for Developers, acceso: junio 28, 2026, [https://developers.google.com/gemini-code-assist/docs/use-agentic-chat-pair-programmer](https://developers.google.com/gemini-code-assist/docs/use-agentic-chat-pair-programmer)  
30. Provide context with GEMINI.md files \- Gemini CLI, acceso: junio 28, 2026, [https://geminicli.com/docs/cli/gemini-md/](https://geminicli.com/docs/cli/gemini-md/)  
31. Authoring Google Antigravity Skills \- Codelabs, acceso: junio 28, 2026, [https://codelabs.developers.google.com/getting-started-with-antigravity-skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills)  
32. Agent Skills | Gemini CLI, acceso: junio 28, 2026, [https://geminicli.com/docs/cli/skills/](https://geminicli.com/docs/cli/skills/)  
33. Tutorial : Getting Started with Google Antigravity Skills \- Medium, acceso: junio 28, 2026, [https://medium.com/google-cloud/tutorial-getting-started-with-antigravity-skills-864041811e0d](https://medium.com/google-cloud/tutorial-getting-started-with-antigravity-skills-864041811e0d)  
34. MetaTrader MCP Server, acceso: junio 28, 2026, [https://mcpservers.org/servers/ariadng/metatrader-mcp-server](https://mcpservers.org/servers/ariadng/metatrader-mcp-server)  
35. Is it possible to get notified when an opened position has been modified? \- Stack Overflow, acceso: junio 28, 2026, [https://stackoverflow.com/questions/43607029/is-it-possible-to-get-notified-when-an-opened-position-has-been-modified](https://stackoverflow.com/questions/43607029/is-it-possible-to-get-notified-when-an-opened-position-has-been-modified)  
36. Volume lot calculation error \- Currency Trading \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/441676](https://www.mql5.com/en/forum/441676)  
37. problem with NormalizeDouble \- MT5 \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/478484](https://www.mql5.com/en/forum/478484)  
38. Using trade.BuyStop and unexpected Invalid Price errors inconsistently \- page 2 \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/445490/page2](https://www.mql5.com/en/forum/445490/page2)  
39. problems with metaeditor getting wrong double numbers \- Symbols \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/443863](https://www.mql5.com/en/forum/443863)  
40. Dynamic minimum lot size digit accuracy \- Symbols \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/10458](https://www.mql5.com/en/forum/10458)  
41. PositionSelect \- Trade Functions \- MQL5 Reference, acceso: junio 28, 2026, [https://www.mql5.com/en/docs/trading/positionselect](https://www.mql5.com/en/docs/trading/positionselect)  
42. Need help to check if stop levels & freeze level codes are valid \- Take Profit \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/466939](https://www.mql5.com/en/forum/466939)  
43. How to calculate LOT SIZE on different symbols? \- Stop Loss \- Expert Advisors and Automated Trading \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/478362](https://www.mql5.com/en/forum/478362)  
44. Error Guide \- PineConnector Docs, acceso: junio 28, 2026, [https://docs.pineconnector.com/error](https://docs.pineconnector.com/error)  
45. Expand Your DARWIN's capacity: Split your MT5 orders \- Darwinex Blog, acceso: junio 28, 2026, [https://blog.darwinex.com/expand-your-darwins-capacity](https://blog.darwinex.com/expand-your-darwins-capacity)  
46. Functions for reading position properties \- Trading automation \- MQL5, acceso: junio 28, 2026, [https://www.mql5.com/en/book/automation/experts/experts\_positionget\_funcs](https://www.mql5.com/en/book/automation/experts/experts_positionget_funcs)  
47. MQL5 Tutorial Basics \- How to get detailed position information for open positions, acceso: junio 28, 2026, [https://www.youtube.com/watch?v=vAIN2iJ5hzc](https://www.youtube.com/watch?v=vAIN2iJ5hzc)  
48. MQL5. Need help with 2nd position and candle entry. \- Copy Trading, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/316562](https://www.mql5.com/en/forum/316562)  
49. Position Management: A Reusable Trade Journal with Live Maximum Adverse Excursion, Maximum Favorable Excursion, and R-Multiple Tracking in MQL5 \- MQL5 Articles, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/22855](https://www.mql5.com/en/articles/22855)  
50. Building a Smart Trade Manager in MQL5: Automate Break-Even, Trailing Stop, and Partial Close, acceso: junio 28, 2026, [https://www.mql5.com/en/articles/19911](https://www.mql5.com/en/articles/19911)  
51. MQL5 Editor Issues \- Money Management \- General \- MQL5 programming forum, acceso: junio 28, 2026, [https://www.mql5.com/en/forum/471056](https://www.mql5.com/en/forum/471056)