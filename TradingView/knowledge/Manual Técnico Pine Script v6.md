Manual de Referencia Técnica de Pine Script v6: Especificación Formal y Arquitectura de Compilación

La programación en el entorno de TradingView requiere una comprensión exhaustiva de la arquitectura interna de su motor de ejecución y de las reglas lógicas que rigen su compilador. Este informe técnico funciona como una referencia formal del lenguaje para la versión 6 de Pine Script (v6), analizando sus estructuras sintácticas, su modelo de datos y los patrones de optimización que los desarrolladores deben aplicar para construir indicadores y estrategias de grado institucional^1^.

1. Evolución del Lenguaje y Compatibilidad de Versiones

El desarrollo de Pine Script ha transitado desde un motor de cálculo simplificado orientado al procesamiento rápido de fórmulas matemáticas en sus primeras versiones, hasta consolidarse en una especificación de lenguaje robusta, estructurada y tipada en la nube en su versión 6^1^.

[v1 / v2: Motor Primitivo] 

   └── Sin tipos explícitos, ámbito global lineal, funciones como macros simples.

[v3: Introducción Estructural] 

   └── Operador de reasignación `:=`, modularidad en declaraciones, control de nulos básico.

[v4: Sistema de Tipos Inicial] 

   └── Introducción de calificadores (const/input/simple/series), objetos gráficos dinámicos (labels/lines).

[v5: Estandarización de Espacios de Nombres] 

   └── Organización en módulos `ta.*`, `math.*`; introducción de UDTs (`type`), arrays y métodos.

[v6: Compilador Estricto y Peticiones Dinámicas] 

   └── Tipado estricto, evaluación booleana por cortocircuito, enums, llamadas request locales/dinámicas.

Cambios Disruptivos (Breaking Changes) entre Versiones

Las transiciones de versión en Pine Script han redefinido sistemáticamente las restricciones de compilación para mitigar la aparición de errores lógicos y de ejecución en tiempo real^4^.

| **Transición de Versión** | **Cambio Disruptivo Introducido** | **Propósito del Cambio** |
| --- | --- | --- |
| **v3  v4** | Introducción obligatoria del operador de reasignación := en lugar de = para variables preexistentes. | Diferenciar claramente la declaración de una variable de su modificación, evitando colisiones en ámbitos locales. |
| **v4  v5** | Depreciación de funciones globales dispersas y su agrupamiento en espacios de nombres específicos (ta.*, math.*, str.*)^6^. | Ordenar el ecosistema de APIs integradas bajo una nomenclatura modular estándar y predecible. |
| **v5  v6** | Prohibición absoluta de casteo implícito de numéricos a valores lógicos bool^8^. | Evitar la ambigüedad en la evaluación de expresiones condicionales complejas^5^. |
| **v5  v6** | Los valores booleanos no pueden ser asignados como na ni procesados por na(), nz() o fixnan()^4^. | Establecer un estado estrictamente binario para el tipo lógico, eliminando errores de lógica triestatal en backtesting^5^. |
| **v5  v6** | El operador de referencia histórica [] no puede aplicarse directamente sobre literales ni sobre propiedades de objetos UDT^4^. | Prevenir operaciones de lectura de pila inválidas y unificar el acceso histórico a nivel de punteros del objeto completo^5^. |
| **v5  v6** | Las divisiones aritméticas entre constantes de tipo entero (const int) retornan un decimal (float)^4^. | Corregir el comportamiento de división truncada inesperado que causaba errores en el cálculo de tamaños de lote^4^. |

Políticas de Soporte del Entorno de Ejecución

El motor de TradingView mantiene compatibilidad regresiva con scripts publicados en versiones antiguas (v3, v4, y v5) para preservar los indicadores de la comunidad^1^. Sin embargo, la máquina virtual en la nube no permite la mezcla de código de diferentes versiones en un mismo script. Todo el desarrollo moderno y las optimizaciones de procesamiento se reservan exclusivamente para el compilador de la versión v6, haciendo obligatoria la migración para acceder a nuevas capacidades como los datos volumétricos de huella de volumen (Volume Footprint), las variables de ticks en tiempo real bid/ask y las llamadas dinámicas a bases de datos de otros activos^1^.

Ejemplo de Migración Estructural de v5 a v6

La migración de código requiere la reestructuración de expresiones booleanas y la adaptación de las llamadas de orden de estrategia^5^.

Pine Script

// === CÓDIGO NO COMPILABLE EN VERSIÓN 5 ===

//@version=5

indicator("Mi Indicador v5", overlay=true)

int periodo = input.int(14, "Periodo")

// Error de casteo implícito: se usa un decimal como booleano en el if

float cambio = ta.change(close)

if cambio

    label.new(bar_index, high, "Cambio detectado", offset=1) // Error en v6: offset acepta series en v5, pero no en v6

// Error de triestatalidad: asume que una variable bool puede ser na

bool señalCompra = close > open ? true : na

Pine Script

// === CÓDIGO COMPILABLE Y OPTIMIZADO EN VERSIÓN 6 ===

//@version=6

indicator("Mi Indicador v6", overlay=true)

int periodo = input.int(14, "Periodo")

// Corrección 1: Comparación explícita para generar una expresión estrictamente booleana

float cambio = ta.change(close)

bool cambioValido = not na(cambio) and cambio != 0.0

if cambioValido

    // Corrección 2: El offset ahora requiere un valor const o simple. Usamos una constante.

    label.new(bar_index, high, "Cambio detectado")

// Corrección 3: Eliminación de nulos en variables booleanas mediante inicialización explícita

bool señalCompra = close > open

2. Sistema de Tipos Completo y Coerción de Datos

El sistema de tipos de Pine Script v6 se compone de tipos de datos fundamentales y tipos estructurados complejos gestionados por referencias^13^. El compilador utiliza análisis estático de tipos para validar la asignación de variables antes de ejecutar el código en el entorno de pruebas de la nube^6^.

┌─────────────────────────────────────────────────────────────────────────┐

│                           SISTEMA DE TIPOS                              │

├──────────────────────────────────────┬──────────────────────────────────┤

│ Fundamental (Valor)                  │ Complejo (Referencia)            │

├──────────────────────────────────────┼──────────────────────────────────┤

│ int, float, bool, string, color      │ array<T>, matrix<T>, map<K,V>    │

│ (Se copian por valor en memoria)     │ (Gestión por punteros, .copy())  │

└──────────────────────────────────────┴──────────────────────────────────┘

Tipos de Datos Fundamentales

- **int**: Representa números enteros de 64 bits de precisión^13^. Se emplea para indexación, recuento de períodos y marcas de tiempo UNIX^15^.
- **float**: Números de punto flotante de doble precisión (64 bits) bajo el estándar IEEE 754^13^. Es el tipo predeterminado para el almacenamiento de cotizaciones y resultados de cálculos de indicadores financieros^15^.
- **bool**: Tipo de dato lógico binario^4^. Solo admite los estados literales true y false^4^. En v6, las variables booleanas no pueden contener el valor na bajo ninguna circunstancia^4^.
- **string**: Cadena de caracteres codificados en formato UTF-8^13^. En v6, el límite máximo por cadena se incrementó a 40,960 caracteres^4^.
- **color**: Formato que representa un valor de color en términos hexadecimales de 32 bits, incluyendo el canal alfa para gestionar la transparencia de los elementos visuales (#RRGGBB o #RRGGBBAA)^13^.
- **na**: Literal polimórfico especial que denota un valor nulo o no disponible^8^. Puede asignarse a variables de tipo int, float, string, color y tipos complejos para indicar un estado no inicializado, pero genera un error de compilación inmediato si se asigna a una variable declarada como bool^8^.

Colecciones Complejas y Tipos de Referencia

Las colecciones dinámicas se almacenan en el montón (heap) del entorno en la nube, y su ciclo de vida es gestionado mediante punteros de referencia^13^.

- **Arrays (array<type>)**: Estructuras lineales indexadas unidimensionales^17^. Su tamaño puede cambiar de forma dinámica barra por barra^17^. En v6, admiten índices negativos para referenciar elementos desde el extremo final (v.g., miArray[-1] recupera el último elemento insertado)^4^. El límite máximo de celdas permitidas por array es de 100,000^17^.
- **Matrices (matrix<type>)**: Estructuras de datos bidimensionales de filas y columnas^15^. El total máximo de elementos indexables en una matriz es de 100,000^17^.
- **Mapas (map<keyType, valueType>)**: Colecciones de pares clave-valor que no guardan un orden secuencial en memoria^21^. Permiten la recuperación instantánea de información con complejidad algorítmica constante ()^23^. La clave debe ser un tipo fundamental (excluyendo colecciones u objetos), mientras que el valor puede albergar cualquier tipo de dato^21^. El límite de un mapa es de 50,000 pares de elementos^21^.
- **Tipos Definidos por el Usuario (UDT)**: Estructuras personalizadas declaradas mediante la directiva type^16^. Permiten la composición de objetos de datos avanzados con campos tipados^13^.

Matriz de Coerción y Casteo de Tipos (Type Casting)

El compilador aplica reglas estrictas para la promoción de tipos. La promoción de un tipo más restringido a uno más amplio ocurre de manera implícita, mientras que el proceso inverso requiere la invocación de funciones de casteo explícito^8^.

| **Tipo de Entrada** | **Tipo de Destino** | **Tipo de Coerción** | **Operador / Método de Conversión** |
| --- | --- | --- | --- |
| int | float | Implícita | No requiere operador (Conversión automática de precisión). |
| float | int | Explícita | Función int(valor_float) (Aplica truncamiento fraccionario)^4^. |
| int / float | bool | Explícita | Función bool(valor_numerico) ( o ; otros )^8^. |
| Cualquiera | string | Explícita | Función str.tostring(valor) (Serialización de datos)^27^. |

Pine Script

//@version=6

indicator("Especificación de Tipos y Colecciones", overlay=false)

// Declaración de Tipo Definido por el Usuario (UDT)

type RegistroEstadistico

    int barrasAnalizadas

    float mediaCierre

    string identificador

// Inicialización de colecciones usando plantillas de tipo estructuradas

var array<float> historialPrecios = array.new<float>()

var map<string, RegistroEstadistico> baseOperaciones = map.new<string, RegistroEstadistico>()

// Inserción de datos

historialPrecios.push(close)

// Casteo explícito numérico y de string

float promedioCalculado = historialPrecios.avg()

int promedioEntero = int(promedioCalculado)

bool mercadoAlza = bool(close > promedioCalculado ? 1 : 0)

// Instanciación del UDT y almacenamiento en mapa

RegistroEstadistico registroNuevo = RegistroEstadistico.new(

     barrasAnalizadas = bar_index,

     mediaCierre = promedioCalculado,

     identificador = syminfo.tickerid

     )

baseOperaciones.put(syminfo.tickerid, registroNuevo)

// Recuperación de datos del mapa y verificación de nulos (na) sobre referencias

RegistroEstadistico datosRecuperados = baseOperaciones.get(syminfo.tickerid)

bool registroExiste = not na(datosRecuperados)

plot(registroExiste ? datosRecuperados.mediaCierre : na, "Media Recuperada", color=color.blue)

3. Sistema de Qualifiers (Calificadores de Tipo)

El sistema de tipos de Pine Script se basa en un modelo bidimensional donde cada variable posee un **tipo de dato** y un **calificador**^14^. Los calificadores determinan en qué momento de la compilación o ejecución un valor está disponible y si es modificable o dinámico^13^.

[CONSTRICCIÓN MÁXIMA]                                                     [VARIABILIDAD MÁXIMA]

     const             ──>             input             ──>  simple  ──>  series

(Tiempo de Compilación)       (Configuración de Usuario)    (Barra Cero)  (Barra a Barra / Ticks)

Jerarquía de Calificadores de Tipo

Existe una jerarquía de dominancia de calificadores definida formalmente como^13^:

Un tipo con un calificador más débil puede promoverse implícitamente a un calificador más fuerte (por ejemplo, pasar una constante const a un parámetro que requiere un tipo series es perfectamente válido), pero un calificador más fuerte nunca puede degradarse a uno más débil^28^.

- **const**: Valores conocidos en tiempo de compilación que no varían bajo ninguna circunstancia durante la ejecución del gráfico (literales numéricos, colores constantes, strings estáticos)^13^.
- **input**: Valores configurados por el usuario mediante los controles de entrada del panel de propiedades (input.*())^13^. Son inmutables durante el transcurso del análisis de las barras en tiempo de ejecución^13^.
- **simple**: Valores calculados una única vez en la primera barra disponible del gráfico (bar_index == 0) y que permanecen constantes durante toda la ejecución de la serie^13^.
- **series**: Flujos dinámicos de datos que cambian en cada barra histórica o tick de tiempo real^13^. Conservan una traza de historial en memoria secuencial, permitiendo el acceso a estados del pasado mediante el operador de referencia histórica []^29^.

Errores Comunes de Incompatibilidad de Calificadores

El error más común de compilación en TradingView ocurre al intentar suministrar una variable de tipo series a funciones integradas que exigen argumentos restrictivos de tipo const o simple^7^.

Por ejemplo, los títulos de las funciones de dibujo (plot(), indicator()) o los parámetros de compensación temporal estática (offset en plot()) requieren calificadores inmutables para que el compilador estructure la memoria visual del gráfico antes de procesar los precios^4^.

Pine Script

//@version=6

indicator("Demostración de Calificadores de Tipo", overlay=true)

// Declaración de variables con diferentes calificadores

const string TITULO_ESTATICO = "Promedio de Precios"

int longitudPeriodos = input.int(14, "Longitud SMA") // Calificador 'input int'

// Una variable determinada por funciones del sistema en la barra cero

simple string tickerGráfico = syminfo.tickerid 

// Variable dinámica calculada en cada barra

float mediaMovil = ta.sma(close, longitudPeriodos) // Calificador 'series float'

// INTENTO DE ERROR DE COMPILACIÓN (Demostrativo):

// El desplazamiento temporal (offset) requiere un calificador simple/const.

// Si calculamos un offset variable que cambia barra a barra (series), el compilador fallará.

// int offsetDinamico = close > open ? 1 : -1

// plot(mediaMovil, offset = offsetDinamico) // ERROR: No se puede usar 'series int' en 'offset'

// Implementación Correcta: Uso de un calificador inmutable 'input' que se promueve a 'simple'

int offsetSeguro = input.int(0, "Offset Fijo de Dibujo")

plot(mediaMovil, title=TITULO_ESTATICO, offset=offsetSeguro, color=color.purple)

4. Modelo de Ejecución

El motor de ejecución de TradingView opera bajo un esquema orientado a eventos que difiere del procesamiento de los lenguajes imperativos convencionales^2^. Comprender el flujo temporal de procesamiento sobre la serie de datos es fundamental para garantizar resultados predictivos^30^.

[ EJE DE TIEMPO DEL GRÁFICO ]

    Barra Histórica (Index 0) ──> Barra Histórica (Index 1) ──> Barra Tiempo Real (Último Index)

             │                             │                              │

             ▼                             ▼                              ▼

    Una ejecución completa        Una ejecución completa        Se ejecuta con cada nuevo tick

     (Rollback inactivo)           (Rollback inactivo)        (Mecanismo de Rollback activo)

Procesamiento de Barras Históricas frente a Tiempo Real

- **Ejecución en Barras Históricas**: El compilador lee la base de datos de precios históricos de izquierda a derecha^2^. Ejecuta el código completo del script exactamente **una vez por cada vela cerrada**, procesando exclusivamente los datos consolidados (Open, High, Low, Close, Volume)^2^. Durante esta fase, el mecanismo de rollback de estado no se activa, pues los datos de la vela son definitivos e inalterables^30^.
- **Ejecución en Barras de Tiempo Real**: Cuando la ejecución alcanza la última barra activa disponible, el script entra en el modo de tiempo real^2^. El código se vuelve a ejecutar **con la llegada de cada tick de cotización** enviado por el proveedor de datos^2^. Esto permite que el indicador responda dinámicamente a las fluctuaciones instantáneas del mercado^2^.

El Mecanismo de Rollback (Retroceso de Estado transaccional)

Para evitar la contaminación de los estados históricos y prevenir el sesgo de supervivencia de datos en tiempo real, el entorno de ejecución implementa un sistema transaccional de retroceso (rollback)^13^.

Antes de que comience el procesamiento de un nuevo tick en la barra de tiempo real, la máquina virtual realiza una copia de seguridad del estado de todas las variables al cierre de la barra histórica anterior (barra consolidada)^30^. Al terminar el tick actual, todas las modificaciones de las variables no marcadas como persistentes se destruyen y el sistema vuelve a restaurar los valores iniciales guardados en la copia de seguridad^30^. Solo cuando la barra actual finalmente cierra de manera oficial (barstate.isconfirmed se evalúa como true), el estado final calculado de ese último tick se consolida de forma permanente en la memoria histórica del script^30^.

Variables de Consulta de Estado del Gráfico

El espacio de nombres integrado barstate proporciona flags booleanos de serie que se emplean para aislar la ejecución de bloques de código costosos en el procesador^13^.

| **Variable de Estado** | **Tipo** | **Descripción de Comportamiento Técnico** |
| --- | --- | --- |
| **barstate.ishistory** | series bool | Retorna true únicamente si la barra actual procesada pertenece a los datos consolidados del pasado^31^. |
| **barstate.isrealtime** | series bool | Retorna true si el motor de ejecución se encuentra procesando ticks activos de la vela actual^19^. |
| **barstate.isconfirmed** | series bool | Retorna true únicamente en la última ejecución de tick de la barra de tiempo real, en el momento exacto en que la vela se cierra para pasar a ser histórica^31^. |
| **barstate.islast** | series bool | Retorna true si la ejecución se encuentra en la última barra física del gráfico (independientemente de si es histórica o de tiempo real)^19^. |
| **barstate.islastconfirmedhistory** | series bool | Retorna true en el punto exacto donde termina el historial estático, sirviendo como barrera óptima para inicializar cálculos visuales^20^. |

Pine Script

//@version=6

indicator("Visualizador del Modelo de Ejecución", overlay=true)

// Variables de estado estándar (Sujetas a Rollback en cada tick)

int ticksProcesadosNormal = 0

ticksProcesadosNormal := ticksProcesadosNormal + 1

// Variables de estado persistente interbarra (Sujetas a Rollback en ticks de tiempo real)

var int contadorBarrasHistoricas = 0

if barstate.ishistory

    contadorBarrasHistoricas := contadorBarrasHistoricas + 1

// Variables persistentes intra-barra (Exentas de Rollback entre ticks)

varip int acumuladorTicksTiempoReal = 0

if barstate.isrealtime

    acumuladorTicksTiempoReal := acumuladorTicksTiempoReal + 1

// Dibujo de un panel informativo al final del gráfico

if barstate.islast

    var table panelInfo = table.new(position.top_right, 2, 4, bgcolor=color.new(color.black, 70))

    table.cell(panelInfo, 0, 0, "Velas Históricas:", text_color=color.white)

    table.cell(panelInfo, 1, 0, str.tostring(contadorBarrasHistoricas), text_color=color.green)

    table.cell(panelInfo, 0, 1, "Ticks Totales en RT:", text_color=color.white)

    table.cell(panelInfo, 1, 1, str.tostring(acumuladorTicksTiempoReal), text_color=color.yellow)

    table.cell(panelInfo, 0, 2, "Ticks en este Tick (Normal):", text_color=color.white)

    table.cell(panelInfo, 1, 2, str.tostring(ticksProcesadosNormal), text_color=color.red)

5. Variables y Persistencia

El compilador de Pine Script v6 requiere la gestión explícita de los mecanismos de persistencia de las variables en memoria^3^. Las variables pueden re-inicializarse en cada barra o mantener su estado de forma indefinida según los modificadores de declaración empleados^3^.

Modificadores de Persistencia

- **Declaración Regular (Series sin modificador)**: La variable se declara de nuevo y calcula su expresión en cada barra o iteración del motor de ejecución^3^. No conserva modificaciones de valor aplicadas en la barra anterior.
- **var**: Modificador que ordena al compilador inicializar la variable exactamente una sola vez en la primera barra disponible (bar_index == 0)^3^. Las modificaciones que sufra la variable mediante reasignaciones := persisten de barra en barra a lo largo de toda la serie temporal^3^.
- **varip**: Inicializa la variable una única vez en la barra cero^13^. Se diferencia de var en que **ignora el mecanismo de rollback** en tiempo real^13^. Cada cambio de valor realizado durante un tick intermedio se consolida en memoria inmediatamente, lo que resulta fundamental para calcular velocidades de propagación de órdenes o recuentos absolutos de ticks intrabarra^13^.

Ámbito y Árbol de Visibilidad de Variables (Scopes)

A partir del compilador v6 (actualización de febrero de 2025), se eliminó por completo el límite de compilación de 550 ámbitos locales de control^4^. Esto habilita la creación de scripts sofisticados sin generar errores de desbordamiento de ámbitos lógicos^4^.

- **Ámbito Global**: Declaraciones situadas fuera de cualquier función, método, bucle o estructura condicional^14^. No deben contener espacios en blanco iniciales en su definición^14^. Son visibles desde cualquier parte del script^32^.
- **Ámbito Local**: Declaraciones definidas dentro de bloques de control de flujo o cuerpos de función^14^. Requieren de manera obligatoria una indentación estricta de cuatro espacios o un tabulador^13^. Tienen visibilidad restringida y no pueden accederse desde el ámbito global superior.

Pine Script

//@version=6

indicator("Control de Persistencia y Ámbitos", overlay=false)

// Ámbito Global

float precioCierre = close

// Inicialización de variables persistentes

var float acumuladorCierreVar = 0.0

varip float acumuladorCierreVarip = 0.0

if barstate.isrealtime

    acumuladorCierreVar := acumuladorCierreVar + close

    acumuladorCierreVarip := acumuladorCierreVarip + close

// Demostración de Scope local en una estructura if

float precioNormalizado = if close > open

    // Ámbito Local del bloque 'if'

    float rangoVela = high - low

    close - (rangoVela / 2.0) // Retorno del bloque

else

    close

// La variable 'rangoVela' no está disponible aquí por pertenecer al ámbito local del 'if'

plot(precioNormalizado, "Precio Normalizado", color=color.purple)

6. Operadores y Expresiones

El cálculo matemático y lógico se fundamenta en un conjunto de operadores con reglas específicas para series de tiempo y el manejo de valores nulos^14^.

Clasificación Completa de Operadores

Operadores Aritméticos

+ (Suma y concatenación de strings), - (Resta), * (Multiplicación), / (División), % (Módulo aritmético)^14^. En v6, la división de constantes enteras no se trunca, produciendo siempre un resultado fraccionario de tipo float^4^.

Operadores de Comparación

== (Igualdad), != (Desigualdad), < (Menor que), > (Mayor que), <= (Menor o igual que), >= (Mayor o igual que)^14^. Retornan de forma estricta valores booleanos^14^.

Operadores Lógicos

and, or, not^7^. En v6 operan bajo el esquema de evaluación perezosa por cortocircuito, deteniendo la evaluación tan pronto como el resultado lógico final es conocido^1^.

Operador Ternario

condición ? valor_verdadero : valor_falso^14^. Permite la construcción compacta de asignaciones condicionales sin necesidad de abrir un nuevo ámbito local^14^.

El Operador de Referencia Histórica []

El operador [] permite consultar valores calculados en ejecuciones del pasado sobre una serie temporal^29^. El índice numérico entero indica cuántas barras en el pasado se desea realizar la lectura (v.g., close[1] hace referencia al precio de cierre de la barra previa)^29^.

Restricciones Estrictas de Uso de [] en v6

- **No se permite sobre literales**: Expresiones como 10[1] o true[5] provocan un error de compilación en v6^4^. Los literales son inmutables y carecen de un historial de serie de tiempo^9^.
- **No se permite sobre campos de objetos UDT directamente**: La sintaxis miObjeto.campo[1] es inválida en v6^4^. Se debe realizar primero la referencia histórica sobre el objeto completo en la pila y posteriormente acceder a su propiedad utilizando paréntesis para definir la precedencia: (miObjeto[1]).campo^4^.

Precedencia de Operadores

La jerarquía de evaluación matemática y lógica se rige de acuerdo con el siguiente orden de precedencia (de mayor a menor importancia)^13^:

| **Precedencia** | **Operador** | **Descripción Técnica** |
| --- | --- | --- |
| **1** | [] | Operador de referencia histórica sobre series^13^. |
| **2** | +, -, not | Operadores aritméticos unarios y negación lógica^13^. |
| **3** | *, /, % | Operaciones aritméticas multiplicativas^13^. |
| **4** | +, - | Operaciones aritméticas aditivas^13^. |
| **5** | <, >, <=, >= | Operaciones de comparación de desigualdad^13^. |
| **6** | ==, != | Operaciones de comparación de igualdad o desigualdad estricta^13^. |
| **7** | and | Operación lógica de conjunción con cortocircuito^1^. |
| **8** | or | Operación lógica de disyunción con cortocircuito^1^. |
| **9** | ?: | Operación de evaluación condicional ternaria^13^. |

Propagación de na en Expresiones Aritméticas

Cualquier operación aritmética que contenga un operando evaluado como na propagará el estado nulo a todo el resultado, inutilizando el cálculo subsiguiente^25^.

Pine Script

//@version=6

indicator("Operadores e Historial Avanzado", overlay=true)

type DatosMercado

    float precioCierre

var DatosMercado registroActivo = DatosMercado.new(close)

registroActivo.precioCierre := close

// Operador de referencia histórica correcto en v6 para campos de UDT

// Se envuelve el objeto en paréntesis antes de acceder a la propiedad

float cierreAnteriorUDT = (registroActivo[1]).precioCierre

// Cortocircuito lógico que protege de errores en el manejo de arrays vacíos

var array<float> listaPrecios = array.new<float>()

listaPrecios.push(close)

// Si la longitud es insuficiente, el segundo operando indexado nunca se evalúa

bool condicionSegura = listaPrecios.size() > 10 and listaPrecios[10] > 100.0

plot(cierreAnteriorUDT, "Cierre Anterior UDT", color=color.purple, display=display.none)

7. Control de Flujo

Las estructuras de control de flujo en Pine Script v6 permiten bifurcar la lógica algorítmica y repetir iteraciones dinámicas barra a barra^13^.

Estructuras Condicionales (if / switch)

- **Estructura if**: Evalúa una condición booleana estricta^13^. Puede utilizarse como un asignador de valor directo, obligando a que todas las ramas de ejecución retornen tipos de datos compatibles^13^. Si la asignación se realiza sobre tipos únicos de datos (v.g., UDTs, dibujos, enums), la estructura debe contar de forma mandatoria con una rama final else para garantizar la consistencia en tiempo de ejecución^8^.
- **Estructura switch**: Permite la comparación múltiple de una expresión lógica o el control de flujo estructurado sin fall-through implícito (no requiere sentencias break de salida)^13^. Exige la incorporación de una condición por defecto => al final si devuelve valores únicos^8^.

Bucles de Iteración (for, for...in, while)

Bucle for con Límite Dinámico

Una de las innovaciones del compilador v6 es que la condición de parada del bucle for (to_num) se evalúa **dinámicamente antes de cada iteración**^4^. En v5, el límite final se fijaba de manera inmutable antes de ingresar al bucle^4^. Esta flexibilidad permite alterar dinámicamente el número de repeticiones de la iteración modificando la variable de límite directamente dentro del cuerpo del bucle^4^.

Pine Script

// Ejemplo de bucle for dinámico en v6

int limiteDinamico = 10

int acumulador = 0

for i = 0 to limiteDinamico

    acumulador := acumulador + 1

    if i == 5

        limiteDinamico := 15 // Extiende el límite del bucle a mitad de ejecución

Bucle for...in

Especializado en recorrer colecciones indexadas elemento por elemento^13^. Permite capturar la tupla desestructurada del índice y el valor correspondiente^8^.

Bucle while

Ejecuta de manera repetitiva un bloque lógico siempre que la condición de parada sea verdadera^14^. Requiere de un manejo de variables internas para prevenir bloqueos infinitos de procesamiento^14^.

Limitaciones Operativas de los Bucles en la Nube

Para mitigar el riesgo de denegación de servicio en la infraestructura de computación en la nube de TradingView, se limita el procesamiento a un máximo de 100,000 operaciones por ejecución de vela en un mismo script^17^. Superar esta cota de procesamiento generará un error fatal en tiempo de ejecución y desactivará el script del gráfico^33^.

Pine Script

//@version=6

indicator("Estructuras de Flujo de Trabajo", overlay=false)

// Bucle For estructurado para rastreo dinámico de pivots

int rangoAnalisis = 50

int conteoPivotsDeseados = 3

int pivotsEncontrados = 0

var array<float> preciosPivots = array.new<float>()

for i = 1 to rangoAnalisis

    // Evaluación condicional para detectar máximos locales en el pasado

    bool esMaximoLocal = ta.highest(high, 5)[i] == high[i]

    if esMaximoLocal

        preciosPivots.push(high[i])

        pivotsEncontrados := pivotsEncontrados + 1

    // Modificación dinámica de la cota final del bucle for en v6

    if pivotsEncontrados >= conteoPivotsDeseados

        rangoAnalisis := i // Reduce el límite del bucle forzando su terminación temprana

// Uso de for...in para sumar los precios de pivots detectados

float sumatoriaPivots = 0.0

for [index, valorPivot] in preciosPivots

    sumatoriaPivots := sumatoriaPivots + valorPivot

plot(sumatoriaPivots, "Sumatoria Pivots", color=color.purple)

8. Funciones y Espacios de Nombres

Las funciones modulares en Pine Script v6 permiten la reutilización de código estructurado y la invocación de herramientas del sistema organizadas bajo espacios de nombres dedicados^6^.

Espacios de Nombres de Funciones Built-in

- **math.***: Operaciones matemáticas avanzadas, trigonometría, logaritmos, exponentes y funciones estadísticas básicas^7^.
- **ta.***: Funciones dedicadas al análisis técnico clásico (v.g., osciladores, medias móviles, volatilidad, rangos y detecciones de cruce)^6^.
- **str.***: Herramientas de formateo, división, manipulación y traducción de strings de caracteres^7^.
- **array.* / matrix.* / map.***: Módulos que exponen las APIs de manipulación de estructuras de colecciones dinámicas^6^.
- **request.***: Peticiones de datos a marcos de tiempo alternativos (request.security()), información financiera empresarial (request.financial()) y datos volumétricos detallados (request.footprint())^4^.
- **ticker.* / timeframe.* / syminfo.***: Consulta de propiedades del activo bajo análisis y del intervalo del gráfico actual^4^.

Firma de Funciones Definidas por el Usuario (UDF)

Las funciones personalizadas pueden incorporar firmas de tipos explícitas tanto en sus parámetros de entrada como en su salida^14^. El compilador verificará que los argumentos de entrada pasados coincidan con el tipo y calificador definidos en la firma de la función^14^.

Pine Script

// Firma de función explícita con parámetros tipados y valores por defecto

calcularOsciladorRsi(series float serieDatos, simple int periodos = 14) =>

    float rsiCalculado = ta.rsi(serieDatos, periodos)

    rsiCalculado // Retorno explícito de la última expresión

Deconstrucción de Retorno Múltiple de Valores (Tuplas)

Debido a que Pine Script prohíbe la asignación directa de tuplas complejas a una única variable, se debe recurrir a la deconstrucción o desempaquetamiento condicionado situando una lista de variables separadas por comas entre corchetes rectos a la izquierda del operador de asignación =^18^.

Pine Script

// Función que retorna múltiples parámetros calculados

obtenerMetricasVela() =>

    float tamañoCuerpo = math.abs(close - open)

    float rangoTotal = high - low

    bool esAlcista = close > open

    [tamañoCuerpo, rangoTotal, esAlcista] // Retorno de tupla de datos

// Deconstrucción segura de la tupla devuelta por la función

[cuerpo, rango, alcista] = obtenerMetricasVela()

9. User Defined Types (UDT)

Los Tipos Definidos por el Usuario (UDT) permiten la creación de estructuras orientadas a objetos, facilitando el diseño modular y la encapsulación lógica de componentes algorítmicos complejos^13^.

Declaración de Estructuras UDT

Se emplea la palabra clave type seguida del nombre de la estructura, declarando en un bloque anidado indentado el tipo y nombre de cada uno de sus campos de datos constitutivos^16^. Se pueden establecer valores de inicialización por defecto para cada campo mediante el uso del operador =^16^.

Pine Script

type CuentaOperaciones

    int idIdentificador

    float balanceInicial

    float balanceActual = 10000.0 // Valor asignado por defecto

    string divisa = "USD"

Instanciación mediante Constructores y Asignación por Referencia

Para instanciar un objeto estructurado en memoria, se utiliza el método constructor automático .new() provisto por el compilador para el tipo personalizado^13^. El constructor admite el paso posicional de parámetros o la asignación explícita mediante claves nominales^16^.

Pine Script

// Instanciación del objeto

CuentaOperaciones cuentaEstatica = CuentaOperaciones.new(

     idIdentificador = 8821,

     balanceInicial = 10000.0

     )

Comportamiento por Referencia y Clonación

Los objetos UDT se gestionan estrictamente **por referencia** en memoria^13^. Si se asigna un objeto existente a una nueva variable, ambas variables compartirán el mismo puntero de acceso^13^. Si se desea duplicar un objeto de forma independiente, se debe llamar al método .copy(), que realiza una copia superficial (shallow copy) del elemento original^13^.

Pine Script

CuentaOperaciones cuentaOriginal = CuentaOperaciones.new(12, 500.0)

CuentaOperaciones cuentaDuplicada = cuentaOriginal

// Ambas variables apuntan al mismo objeto en memoria. Su modificación altera a ambas.

cuentaDuplicada.balanceActual := 15000.0 // Altera también a cuentaOriginal

// Clonación real (Copia independiente en memoria)

CuentaOperaciones cuentaIndependiente = cuentaOriginal.copy()

cuentaIndependiente.balanceActual := 2000.0 // No modifica la cuentaOriginal

Comparativa Estructural: Pine Script UDT frente a Clases Tradicionales

| **Característica** | **Pine Script v6 UDT** | **Clases OOP Tradicionales (C++, Python)** |
| --- | --- | --- |
| **Herencia de Tipos** | No admitida (Estructuras planas sin relación jerárquica). | Soportada (Herencia simple, múltiple e interfaces polimórficas). |
| **Encapsulación y Acceso** | Todos los campos son públicos. No existen palabras clave como private o protected. | Soportada mediante especificadores de acceso y métodos de encapsulación. |
| **Métodos Internos** | No se pueden declarar funciones dentro de type^16^. Deben declararse externamente con la directiva method^14^. | Métodos y constructores personalizados embebidos dentro de la estructura de la clase. |
| **Referencia Histórica** | No se puede aplicar el operador [] directamente sobre las propiedades^4^. Requiere envolver el objeto completo: (obj[1]).campo^5^. | Manejo directo mediante punteros e indexación nativa del compilador de bajo nivel. |

10. Methods (Métodos)

Los métodos de Pine Script v6 proporcionan un mecanismo sintáctico para encapsular funciones asociándolas directamente a tipos fundamentales, UDTs o tipos enumerados^23^.

Declaración de Métodos de Usuario

Para definir un método personalizado, se utiliza la palabra clave method^36^. El primer parámetro de la función determina a qué tipo de datos queda asociado el método y se comporta de manera análoga al puntero implícito this de los lenguajes orientados a objetos^13^.

Pine Script

// Declaración de un método enlazado al tipo de datos de arrays de floats

method obtenerUltimoElemento(array<float> srcArray) =>

    float retorno = na

    if srcArray.size() > 0

        retorno := srcArray.get(srcArray.size() - 1)

    retorno

Una vez declarado, se puede invocar sobre variables del tipo de datos enlazado utilizando la sintaxis de punto tradicional^23^:

Pine Script

var array<float> registroCierres = array.new<float>()

registroCierres.push(close)

// Invocación fluida del método de usuario

float ultimoCierre = registroCierres.obtenerUltimoElemento()

Sobrecarga de Métodos (Method Overloading)

Pine Script v6 admite la sobrecarga de métodos, lo que permite declarar múltiples métodos utilizando el mismo identificador siempre que sus firmas de parámetros de entrada sean diferentes^14^. El compilador resolverá de manera automática cuál implementación emplear analizando los tipos reales enviados en la llamada^13^.

Pine Script

// Sobrecarga de método de cálculo de desviación porcentual

// Implementación para valores numéricos simples

method calcularDesviacion(float valorActual, float valorReferencia) =>

    ((valorActual - valorReferencia) / valorReferencia) * 100.0

// Implementación para colecciones de tipo array

method calcularDesviacion(array<float> datos, float valorReferencia) =>

    float ultimoDato = datos.size() > 0 ? datos.get(datos.size() - 1) : na

    float res = na

    if not na(ultimoDato)

        res := ((ultimoDato - valorReferencia) / valorReferencia) * 100.0

    res

Encadenamiento de Métodos (Method Chaining)

Si las firmas de los métodos devuelven como valor de retorno una referencia del mismo objeto de entrada, se pueden encadenar llamadas sucesivas sobre una misma línea de código de forma secuencial^3^.

Pine Script

//@version=6

indicator("Especificación de Métodos y Encadenamiento", overlay=false)

type FiltroProcesamiento

    float multiplicador

    float offsetSuma

// Métodos mutadores que devuelven el objeto para permitir encadenamiento

method setMultiplicador(FiltroProcesamiento obj, float mult) =>

    obj.multiplicador := mult

    obj

method setOffset(FiltroProcesamiento obj, float off) =>

    obj.offsetSuma := off

    obj

method aplicarFiltro(FiltroProcesamiento obj, float precioBase) =>

    (precioBase * obj.multiplicador) + obj.offsetSuma

// Instanciación y uso de encadenamiento de métodos (Method Chaining)

var FiltroProcesamiento configurador = FiltroProcesamiento.new(1.0, 0.0)

// Configuración encadenada y cálculo en un único paso lógico

float resultadoFinal = configurador.setMultiplicador(1.5).setOffset(2.5).aplicarFiltro(close)

plot(resultadoFinal, "Resultado Filtro", color=color.blue)

11. Manejo de na (Null Handling)

El valor na representa un estado no disponible o nulo en el entorno de ejecución de TradingView^8^. Debido a la naturaleza continua de las series de datos financieros, la gestión robusta de los nulos es crítica para evitar la degradación de los cálculos algorítmicos^26^.

Funciones de Gestión de Nulos

- **na(x)**: Retorna true si el argumento x es equivalente a na^8^. En v6, esta función **no acepta tipos de datos booleanos**^4^.
- **nz(x, reemplazo)**: Evalúa el argumento x^5^. Si el valor es válido, lo retorna; si es na, devuelve el valor de sustitución especificado en el segundo parámetro^5^. Si se omite este parámetro, asume por defecto 0 o 0.0 según el contexto^5^. En v6, ya no acepta argumentos bool^4^.
- **fixnan(x)**: Reemplaza valores na devolviendo el último valor no nulo registrado en las ejecuciones anteriores de la serie temporal^10^. Si no se ha registrado ningún valor válido previo, retorna na^10^.

Reglas de Propagación de Nulos

La presencia de na en operaciones matemáticas propaga el estado de forma destructiva a través de toda la cadena de cálculo^25^.

Trampas de Diseño Comunes con na

Los programadores que migran desde otros entornos de desarrollo suelen intentar validar la existencia de un valor nulo utilizando el comparador de igualdad directa variable == na. En Pine Script, esta comparación **siempre** retornará false debido a que el compilador no puede evaluar equivalencias sobre estados indeterminados. Se debe emplear de manera mandatoria la función integrada na(variable) para realizar estas comprobaciones^8^.

Pine Script

//@version=6

indicator("Manejo de Valores Nulos", overlay=true)

// Un indicador de periodos largos genera na en las primeras barras del gráfico

float rsiLargo = ta.rsi(close, 200)

// Comprobación segura de nulidad en v6

bool rsiListo = not na(rsiLargo)

// Reemplazo seguro mediante nz() para evitar propagación en sumatorias acumuladas

float cambioCierre = ta.change(close)

float cambioSeguro = nz(cambioCierre, 0.0)

// Uso de fixnan para corregir saltos de datos en solicitudes de otros marcos de tiempo (MTF)

float precioDiarioConGaps = request.security(syminfo.tickerid, "D", close, gaps=barmerge.gaps_on)

float precioDiarioCorregido = fixnan(precioDiarioConGaps)

plot(precioDiarioCorregido, "MTF Sin Nulos", color=color.green)

12. Annotations y Metadata (Anotaciones de Compilador)

Las directivas de anotación de metadatos y las declaraciones de cabecera configuran el comportamiento macro del script, inicializan los paneles gráficos de interfaz de usuario e integran la documentación del código con el motor de autocompletado del editor de TradingView^2^.

Declaraciones de Script de Primer Nivel

- **indicator()**: Inicializa el script para que opere como un indicador visual convencional^2^.

- *Parámetros clave*: title (Título const string)^28^, shorttitle (Título corto visualizado en gráfico)^38^, overlay (Determina si se renderiza encima de las velas principales o en un panel inferior independiente)^20^, dynamic_requests (Habilita el modo dinámico de peticiones externas de base de datos)^8^.

- **strategy()**: Inicializa el script de backtesting habilitando las herramientas de simulación de órdenes de compra y venta del Strategy Tester de TradingView^2^.

- *Parámetros clave*: margin_long, margin_short (Definen el apalancamiento financiero de la cuenta simulada; el valor por defecto en v6 es 100)^4^, default_qty_type, default_qty_value (Establecen las unidades predeterminadas de entrada de contratos)^37^, process_orders_on_close (Fuerza la ejecución inmediata de órdenes al cierre de la vela)^37^.

- **library()**: Permite empaquetar conjuntos de funciones, métodos e inicializaciones estructuradas para que puedan ser importadas y reutilizadas por otros desarrolladores^2^.

Etiquetas de Documentación Formal de Metadatos (PineDoc)

El compilador de TradingView utiliza comentarios estructurados especiales para alimentar el sistema de análisis estático del editor^41^:

- **//@version=6**: Especifica obligatoriamente la versión de compilación del lenguaje^3^.
- **//@description**: Texto descriptivo que documenta el propósito global del script, funciones o tipos de datos definidos.
- **//@param**: Describe la función, el tipo de dato y el uso del parámetro asignado en una UDF^6^.
- **//@returns**: Detalla el tipo de dato y la estructura de salida que devuelve un subprograma^6^.
- **//@type**: Especifica las características de datos de una estructura de tipo UDT.
- **//@field**: Documenta individualmente los campos constitutivos internos de un UDT o Enum^6^.
- **//@enum**: Documenta los propósitos funcionales y los rangos de constantes de un tipo enumerado^27^.

Pine Script

//@version=6

//@description Biblioteca de cálculo de herramientas volumétricas.

library("HerramientasVolumetricasPro")

//@enum Define las opciones disponibles para la normalización del volumen negociado.

//@field absoluto Sin aplicar factores de normalización de escala.

//@field relativo Escala normalizada respecto al promedio de las últimas barras.

export enum ModoVolumen

    absoluto = "Absoluto"

    relativo = "Relativo"

//@description Normaliza el flujo volumétrico según el modo seleccionado.

//@param longitud Periodo de análisis del promedio móvil de volumen. Es inmutable.

//@param seleccion Opción de normalización de volumen.

//@returns El volumen negociado transformado.

export calcularVolumenNormalizado(simple int longitud, ModoVolumen seleccion) =>

    float res = na

    if seleccion == ModoVolumen.absoluto

        res := volume

    else if seleccion == ModoVolumen.relativo

        float promedioVol = ta.sma(volume, longitud)

        res := promedioVol > 0.0 ? volume / promedioVol : 0.0

    res

13. Limitaciones del Lenguaje y Sandbox en la Nube

Para garantizar la estabilidad operativa del entorno de computación en la nube (Cloud Engine) que procesa concurrentemente millones de peticiones lógicas, TradingView confina el entorno de ejecución de Pine Script a una caja de arena altamente restringida (Sandbox)^2^.

Restricciones Absolutas de Diseño en Pine Script

- **Sin Operaciones de File System**: No existe ninguna API que permita interactuar con el sistema de archivos local del ordenador del usuario ni de los servidores de procesamiento. No es posible crear, guardar o modificar archivos planos de datos.
- **Sin Conectividad de Red Externa**: El script no puede realizar peticiones HTTP, abrir conexiones WebSocket ni interactuar con recursos de red externos. Toda automatización externa de datos de salida debe gestionarse obligatoriamente redirigiendo payloads textuales estructurados mediante el sistema oficial de alertas con webhooks del servidor^11^.
- **Entorno Monohilo Estricto**: No se soporta la concurrencia multihilo o la creación de procesos en paralelo. El procesamiento de las barras se realiza de manera lineal secuencial sobre un único hilo físico del procesador asignado temporalmente^2^.
- **Prohibición Absoluta de Recursión**: Las funciones tienen estrictamente prohibido realizar llamadas autorreferenciales directas. El compilador detecta inmediatamente cualquier intento de invocación recursiva para evitar desbordamientos de pila de memoria de computación^4^.

Límites Físicos de Compilación e Infraestructura

La máquina virtual en la nube impone topes estrictos de consumo de recursos y dimensiones lógicas para evitar que scripts mal optimizados saturen los servidores de cálculo^43^:

- **Límite de Variables Locales**: Un script no puede superar un máximo de **500 variables locales** simultáneas dentro de un mismo bloque lógico de procesamiento.
- **Límite de Colecciones en Memoria**: El total de elementos asignados a colecciones de tipo array y matrix está limitado a un tamaño de **100,000 celdas** lógicas de datos^17^. Los mapas se restringen a un máximo de **50,000 pares** clave-valor^21^.
- **Límites de Dibujo Dinámico**: Para mantener la fluidez visual de los gráficos interactivos, solo se permite representar un máximo de **100 polígonos complejos (polylines)** de forma simultánea, admitiendo cada polilínea un máximo de **10,000 puntos de coordenadas** cartesianas^39^. El número total de etiquetas (labels) y cajas gráficas (boxes) representables de forma dinámica simultánea está limitado a **500 elementos**^44^.
- **Límite de Solicitudes Externas**: El número total de peticiones dinámicas concurrentes de acceso a bases de datos secundarias mediante request.*() se limita de forma predeterminada a un máximo de **40 peticiones únicas** (y hasta **64 peticiones únicas** para los usuarios con el plan Premium/Ultimate)^34^.

Pine Script

//@version=6

strategy("Estrategia con Mitigación de Límites", overlay=true, max_labels_count=500)

// Las estrategias están expuestas a recortar órdenes antiguas si superan 9000 trades en v6.

// Para evitar lecturas inválidas sobre trades ya recortados (Trimming), se valida

// de manera defensiva el índice más antiguo disponible de trade no recortado en v6.

int indicePrimerTrade = strategy.closedtrades.first_index // Devuelve el primer trade disponible tras el recorte [cite: 1, 19]

// Consulta defensiva de operaciones cerradas previniendo un error fuera de límites

float gananciaUltimoTradeActivo = if strategy.closedtrades.size() > 0 and indicePrimerTrade == 0

    strategy.closedtrades.profit(strategy.closedtrades.size() - 1)

else

    na

plot(gananciaUltimoTradeActivo, "Ganancia Último Trade", color=color.purple, display=display.none)

14. Gotchas para Desarrolladores (Trampas de Diseño)

Los desarrolladores con experiencia previa en lenguajes como Python, JavaScript o MQL5 suelen cometer errores sistemáticos debido a las particularidades lógicas y de compilación de Pine Script^2^.

El Error del Cortocircuito Lógico Histórico (State-Dependent RSI Gotcha)

La introducción de la evaluación por cortocircuito (lazy evaluation) en Pine Script v6 introduce un bug lógico de difícil detección si se sitúan funciones que almacenan estados históricos dentro de condicionales lógicos complejos^1^.

Comportamiento del Bug

Considere la siguiente estructura condicional:

Pine Script

// CÓDIGO CON BUG LÓGICO HISTÓRICO EN v6

if close > open and ta.rsi(close, 14) > 50

    strategy.entry("Largo", strategy.long)

En Pine Script v5, tanto la parte izquierda como la derecha de la operación and se evaluaban obligatoriamente en cada barra (eager evaluation)^5^. Como resultado, la función ta.rsi() mantenía sus cálculos actualizados de manera interna en cada vela, consolidando su histórico correctamente en todas las barras del gráfico^5^.

En Pine Script v6, la evaluación por cortocircuito de la expresión lógica evita evaluar la parte derecha si el término izquierdo (close > open) resulta falso^4^. Al no ejecutarse el miembro derecho en las barras donde el precio cae, la función ta.rsi() omite actualizar sus variables históricas^5^. Esto corrompe de manera destructiva el cálculo del RSI, produciendo valores desfasados e incorrectos cuando la condición izquierda vuelve a ser verdadera, lo que desestabiliza las señales del sistema de trading^5^.

La Solución Estructural

Para prevenir este comportamiento anómalo en el compilador v6, se deben aislar de manera mandatoria todas las funciones que guarden estados e historial interno (tales como indicadores, promedios, desviaciones estándar, filtros o cruces técnicos) y ejecutarlas directamente en el ámbito global del script para asegurar una actualización limpia barra por barra^5^:

Pine Script

// SOLUCIÓN CORRECTA Y OPTIMIZADA EN v6

// Al declarar el RSI en el ámbito global, se garantiza su cálculo ininterrumpido en todas las barras

float rsiConsolidado = ta.rsi(close, 14)

bool condicionCompra = close > open and rsiConsolidado > 50

if condicionCompra

    strategy.entry("Largo", strategy.long)

El Gotcha de División de Constantes

Los programadores habituados a la división truncada de enteros nativa de lenguajes como C++ o Python suelen esperar que una operación entre enteros deseche la fracción de decimales^4^. Como en Pine Script v6 la división de constantes enteras (1 / 2) genera automáticamente un valor de tipo float (0.5), cualquier cálculo que asuma un truncamiento de enteros de manera implícita provocará fallos matemáticos graves en el cálculo de períodos de análisis o el dimensionamiento de estructuras de bucles^4^.

Para restaurar el comportamiento clásico de la división entera truncada, se debe forzar el casteo explícito de nielado envolviendo el resultado dentro de la función de conversión de enteros int()^4^:

Pine Script

// Comportamiento por defecto en v6

float ratioDecimal = 5 / 2 // Retorna 2.5

// Comportamiento truncado clásico (Equivalente al truncamiento por defecto en v5 y MQL5)

int ratioTruncado = int(5 / 2) // Retorna 2

Gotcha del Calificador offset en la Función plot

El compilador v6 restringe las firmas de dibujo, impidiendo que el argumento de compensación temporal offset reciba variables que tengan el calificador series^4^. Si se desea realizar un desplazamiento dinámico basado en condiciones del mercado que cambian barra por barra, se debe generar un buffer de datos dinámico mediante el uso de colecciones array en lugar de manipular los parámetros estructurales del dibujo^4^.

Pine Script

//@version=6

indicator("Gotcha de Desplazamiento y Solución Estructural", overlay=true)

// INTENTO INVÁLIDO EN v6 (Comentar para compilar):

// El desplazamiento dinámico no se puede aplicar directamente sobre plot en v6

// int offsetDinamico = close > open ? 3 : 1

// plot(close, offset = offsetDinamico) // ERROR DE COMPILACIÓN EN v6

// SOLUCIÓN ESTRUCTURAL RECOMENDADA:

// Implementación de un buffer dinámico manual que gestiona el desplazamiento

var array<float> bufferDesplazamiento = array.new<float>()

bufferDesplazamiento.push(close)

int retardoDeseado = 3

float precioRetardado = na

if bufferDesplazamiento.size() > retardoDeseado

    // Recupera de forma segura el dato con el desfase temporal deseado

    precioRetardado := bufferDesplazamiento.shift()

plot(precioRetardado, "Cierre Retardado Buffer", color=color.purple)

Fuentes citadas

- Pine Script® v6已发布— TradingView博客, https://www.tradingview.com/blog/cn/pine-script-v6-has-landed-48830/
- Pine Script™ v6 User Manual | PDF | Scope (Computer Science) | Time Series - Scribd, https://www.scribd.com/document/860957045/1-Pine-Script-V6-User-Manual-PDF-1
- Cracking Pine script version 6. Get my strategy - Medium, https://medium.com/@drwebdev.future/cracking-pine-script-version-6-61faad4d5c9d
- Pine Script v6 Release Notes Explained (2024-2026) - TradersPost, https://blog.traderspost.io/article/pine-script-v6-release-notes-explained
- Pine Script v6 Breaking Changes the Converter Misses - TradersPost, https://blog.traderspost.io/article/pine-script-v6-breaking-changes
- tradesdontlie/pine-script-v6-extension - GitHub, https://github.com/tradesdontlie/pine-script-v6-extension
- Pine Script v6 IDE Tools - Visual Studio Marketplace, https://marketplace.visualstudio.com/items?itemName=jpantsjoha.pinescript-v6-extension
- To Pine Script version 6 - Migration guides - TradingView, https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/
- How to Convert Pine Script v5 to v6 Without Bugs - TradersPost, https://blog.traderspost.io/article/pine-script-v5-to-v6-migration-guide
- Pine Script v6 Migration Guide | PDF | Boolean Data Type - Scribd, https://www.scribd.com/document/872972761/Migration-Guides-to-Pine-Script-Version-6
- Pine Script™ v6: An Exciting Update for Traders and Developers - CrossTrade, https://crosstrade.io/blog/pine-script-v6-an-exciting-update-for-traders-and-developers
- 4 Pine Script v6 Strategy Changes That Alter Backtests - TradersPost, https://blog.traderspost.io/article/pine-script-v6-strategy-changes
- pine-script-reference | Skills Marke... - LobeHub, https://lobehub.com/es/skills/adamelliotfields-skills-pine-script-reference
- pine-script-reference | Skills Marke... - LobeHub, https://lobehub.com/skills/adamelliotfields-skills-pine-script-reference
- A minimal reference to pine script v5 - GitHub Gist, https://gist.github.com/dnavarrom/5b8a36411a8a6fb2a0380d12cfe52673
- Objects - Language - TradingView, https://www.tradingview.com/pine-script-docs/v5/language/objects/
- Language / Arrays - TradingView, https://www.tradingview.com/pine-script-docs/language/arrays/
- Data structures - TradingView, https://www.tradingview.com/pine-script-docs/faq/data-structures/
- O Pine Script® v6 foi lançado — Blog TradingView, https://www.tradingview.com/blog/pb/pine-script-v6-has-landed-48830/
- Ha llegado Pine Script® v6: TradingView Blog, https://www.tradingview.com/blog/es/pine-script-v6-has-landed-48830/
- Language / Maps - TradingView, https://www.tradingview.com/pine-script-docs/language/maps/
- GitHub - woodstock-tokyo/pinescription: Pine Script v6 compiler and runtime for Go, https://github.com/woodstock-tokyo/pinescription
- TradingView Pine Script Reference - GitHub Gist, https://gist.github.com/0xdevalias/7fd548eccb1cad6db4c92284bafd1607
- Introduce a DICTIONARY (key,value) pair data type in pine script : r/TradingView - Reddit, https://www.reddit.com/r/TradingView/comments/1iqnk3k/introduce_a_dictionary_keyvalue_pair_data_type_in/
- Pine Script Compatibility | PyneCore Documentation, https://pynecore.org/docs/overview/compatibility/
- 3 Boolean Changes in Pine Script v6 (With Fixes) - TradersPost, https://blog.traderspost.io/article/pine-script-v6-boolean-changes
- Complete Guide to Enums in Pine Script v6 - TradersPost, https://blog.traderspost.io/article/pine-script-v6-enums-guide
- Language / Type system - TradingView, https://www.tradingview.com/pine-script-docs/v5/language/type-system/
- Primer / Next steps - TradingView, https://www.tradingview.com/pine-script-docs/primer/next-steps/
- Pine Script User Manual Guide | PDF - Scribd, https://www.scribd.com/document/970916586/Pine-Script-v6-User-Manual
- Pine Script v5 User Manual (200-350) | PDF | Parameter (Computer Programming) - Scribd, https://www.scribd.com/document/707960100/Pine-Script-v5-User-Manual-200-350
- Programming - TradingView, https://www.tradingview.com/pine-script-docs/v5/faq/programming/
- Pine Script For Loops Now Re-Evaluate Boundaries - TradersPost, https://blog.traderspost.io/article/pine-script-dynamic-for-loops
- Concepts / Other timeframes and data - TradingView, https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/
- How to use tuples as inputs to a function in PineScript? - Stack Overflow, https://stackoverflow.com/questions/69716242/how-to-use-tuples-as-inputs-to-a-function-in-pinescript
- WWW Tradingview Com Pine Script Docs Language Methods #Methods... | PDF - Scribd, https://www.scribd.com/document/815343909/Www-Tradingview-Com-Pine-Script-Docs-Language-Methods-Methods-1-1
- Pine Script v6 Strategy Code Examples - CrossTrade, https://crosstrade.io/blog/pine-script-v6-strategy-code-examples
- TradingView Pine Script Reference v6 (websites/cn_tradingview_pine-script-reference_v6), https://context7.com/websites/cn_tradingview_pine-script-reference_v6
- What's New in Pine Script v6: All Features Covered - TradersPost, https://blog.traderspost.io/article/pine-script-v6-complete-guide
- Build Strategy Dropdowns with Pine Script Enums - TradersPost, https://blog.traderspost.io/article/pine-script-v6-enum-strategy-settings
- New Github Repository with full Pinescript v6 reference manual for AI and LLM models, https://www.reddit.com/r/TradingView/comments/1m7ref8/new_github_repository_with_full_pinescript_v6/
- codenamedevan/pinescriptv6: markdown file of full pinescript v6 file for LLM's to ingest, https://github.com/codenamedevan/pinescriptv6
- Writing / Profiling and optimization - TradingView, https://www.tradingview.com/pine-script-docs/writing/profiling-and-optimization/
- Pine Script v6: Syntax error at function definition 'input "("' - How to declare functions correctly? - Stack Overflow, https://stackoverflow.com/questions/79655755/pine-script-v6-syntax-error-at-function-definition-input-how-to-declare
- Pine Script v6: Common Questions and Mistakes - TradersPost, https://blog.traderspost.io/article/pine-script-v6-faq