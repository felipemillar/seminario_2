Arquitectura Modular de Grado Institucional en Pine Script v6: Diseño, Publicación y Mantenimiento de Librerías

El desarrollo de software financiero sobre la plataforma TradingView ha evolucionado desde la creación de indicadores individuales simples hacia el diseño de sistemas de negociación algorítmica complejos y distribuidos. En entornos institucionales, donde la robustez, la mantenibilidad del código y la eficiencia computacional son imperativos operacionales, la transición hacia arquitecturas modulares se convierte en una necesidad crítica. Pine Script v6 introduce mejoras fundamentales que permiten implementar estas estructuras mediante el uso avanzado de librerías, permitiendo la segregación estricta de responsabilidades, la optimización en el consumo de tokens y una gestión rigurosa del ciclo de vida del software^1^.

Diseño de la Capa de Exportación y Control de Calificadores

El diseño de una librería en Pine Script v6 requiere una comprensión profunda de cómo se exponen las funciones, los tipos de datos y las constantes a los scripts consumidores, así como del comportamiento del sistema de tipos y la jerarquía de calificadores de la plataforma^3^. Una librería se inicia obligatoriamente con la declaración library(), lo que indica al compilador que el script no se aplicará directamente a un gráfico, sino que actuará como un contenedor de recursos exportables^3^.

Jerarquía de Calificadores y Compatibilidad de Tipos

El sistema de tipos de Pine Script clasifica la información según su naturaleza y la disponibilidad temporal de sus valores^6^. Para comprender las restricciones de exportación, es indispensable modelar la jerarquía de los calificadores de tipo, la cual determina en qué momento del ciclo de compilación o ejecución un dato se vuelve inmutable o dinámico^6^.

| **Calificador** | **Momento de Establecimiento** | **Mutabilidad durante la Ejecución** | **Tipos de Datos Compatibles** | **Relación en la Jerarquía** |
| --- | --- | --- | --- | --- |
| const | Tiempo de compilación^7^ | Estrictamente inmutable en todas las barras^7^ | Tipos primitivos (int, float, bool, color, string)^6^ | Base de la jerarquía (el más débil)^6^ |
| input | Tiempo de inicialización (interfaz de usuario)^7^ | Inmutable durante la ejecución del dataset^7^ | Tipos primitivos y fuentes de datos seleccionadas^6^ | Superior a const<br>[cite: 6, 7] |
| simple | Primer bar histórico de la ejecución^7^ | No puede cambiar en barras subsiguientes^7^ | Tipos primitivos^6^ | Superior a input<br>[cite: 6, 7] |
| series | Dinámico bar a bar^7^ | Completamente mutable en cada iteración^7^ | Todos los tipos de datos y referencias de la plataforma^6^ | Dominante (el más fuerte)^6^ |

La ley fundamental de compatibilidad de calificadores establece que un parámetro o variable diseñado para aceptar un calificador determinado puede recibir valores con un calificador idéntico o de jerarquía inferior (más débil), pero nunca de jerarquía superior^3^. Matemáticamente, la regla de asignación se rige por la relación:

Por consiguiente, si una función de librería requiere internamente un argumento de tipo simple int, rechazará de manera categórica un valor de tipo series int^3^.

Reglas Estrictas para la Exportación de Funciones y Métodos

Al diseñar la interfaz pública de una librería mediante la palabra clave export, se aplican restricciones de compilación sumamente rígidas en comparación con las funciones locales estándar^3^:

- **Tipado Explícito Obligatorio**: A diferencia de las funciones de usuario ordinarias donde el compilador infiere dinámicamente los tipos, cada parámetro en la firma de una función o método exportado debe declarar de forma explícita tanto su tipo como, de ser necesario, su calificador de restricciones (por ejemplo, simple int o series float)^3^.
- **Aislamiento del Ámbito Global**: Las funciones exportadas tienen prohibido leer o modificar variables mutables declaradas en el ámbito global de la librería^3^. Solo se les permite interactuar con variables globales que hayan sido definidas como constantes en tiempo de compilación mediante el calificador const^3^.
- **Prohibición de Entradas Directas**: Ninguna función exportada puede invocar funciones del espacio de nombres input.*(), dado que la parametrización es responsabilidad exclusiva del script que orquesta la ejecución final^3^.
- **Restricción de Retorno**: Las funciones y métodos exportados solo pueden devolver valores con calificadores de nivel simple o series^9^. No es técnicamente posible que una función exportada retorne un valor calificado como const o input^9^.

Para forzar a que una función devuelva un calificador simple (por ejemplo, para construir identificadores de símbolos estáticos requeridos en llamadas no dinámicas de obtención de datos externos), el programador debe anteponer explícitamente la palabra clave simple en la declaración de los parámetros de entrada de la firma^3^:

Pine Script

// Forzado explícito de parámetros simples para garantizar un retorno simple

export generarTicker(simple string mercado, simple string activo) =>

    mercado + ":" + activo

Exportación de Constantes, Tipos de Datos Personalizados (UDTs) y Enumeraciones

Pine Script v6 proporciona capacidades nativas para exportar variables estáticas del sistema, estructuras complejas de datos y enumeraciones con tipado estricto, facilitando la creación de estándares operativos unificados a nivel corporativo^1^.

- **Exportación de Constantes (export const)**: Introducida para evitar la ineficiente práctica de envolver valores fijos en funciones de ejecución en tiempo de desarrollo^9^. Permite compartir coeficientes matemáticos, variables lógicas globales o configuraciones de estilos directamente a través del espacio de nombres de la librería^9^. Estas constantes quedan limitadas a tipos de datos básicos y no admiten estructuras de referencia^9^.

Pine Script

export const float LIMITE_APALANCAMIENTO = 3.5

export const color COLOR_COMPRA = #00ff00

- **Exportación de Tipos de Datos Personalizados (export type)**: Para empaquetar conjuntos de datos complejos bajo el patrón de objetos sin métodos^8^. Si un UDT se utiliza como parámetro de entrada o retorno en cualquier función expuesta al exterior, la declaración de dicho UDT debe ser exportada de manera obligatoria^3^.

Pine Script

export type Posicion

    string ticker

    float volumen

    float precioEntrada

    bool esLargo

- **Exportación de Enumeraciones (export enum)**: Permite implementar máquinas de estado estricto o listados cerrados de parámetros operativos que evitan errores semánticos comunes por el uso de cadenas de texto crudas^1^. Las opciones se validan estrictamente en tiempo de compilación y se integran automáticamente en los menús desplegables del script consumidor a través de input.enum()^1^.

Pine Script

export enum RegimenMercado

    alcista = "Regimen Alcista"

    bajista = "Regimen Bajista"

    rango = "Consolidacion Lateral"

Patrones de Inmutabilidad, Control de Referencias y Aislamiento de Memoria

El manejo de variables y colecciones en memoria difiere de forma radical dependiendo de su categoría de almacenamiento en el motor de ejecución de TradingView^8^. Mientras que los tipos primitivos se copian por valor al ser transmitidos a funciones de librerías, las referencias complejas (arrays, matrices, mapas y UDTs) se transmiten estrictamente por referencia^8^.

Cuando una librería recibe una referencia de datos y altera alguno de sus elementos o atributos, esta modificación se refleja de forma instantánea en el script consumidor de origen, violando los principios de diseño de software limpio y provocando efectos secundarios impredecibles^8^. Para mitigar esto, se debe aplicar sistemáticamente el patrón de **copia defensiva** a través de la función nativa .copy() disponible para colecciones de datos, asegurando la inmutabilidad de la estructura original expuesta por el cliente de la librería^8^.

Pine Script

// Anti-patrón: Modificación directa de la estructura del cliente

export depurarMuestrasMalas(float[] muestras) =>

    array.sort(muestras)

    array.shift(muestras) // Altera de manera permanente la colección del llamador

// Patrón de Diseño Recomendado: Preservación de la inmutabilidad mediante copia defensiva

export depurarMuestrasDefensivo(float[] muestras) =>

    float[] muestrasClonadas = array.copy(muestras)

    array.sort(muestrasClonadas)

    array.shift(muestrasClonadas)

    muestrasClonadas // Retorna una nueva referencia aislada en memoria

Este comportamiento está fuertemente correlacionado con el mecanismo de **aislamiento de funciones** de la plataforma de TradingView^15^. Cada llamada individual a una función de librería crea un entorno de memoria lógicamente aislado, asignando vectores de estado independientes en tiempo de ejecución^15^. Cuando se instancian llamadas consecutivas, el motor gestiona buffers históricos y persistencias de variables diferenciadas para cada punto de llamada del script^15^. Esto garantiza que las funciones que rastrean estados históricos (como el cálculo de medias móviles o desviaciones estándar) operen de forma correcta sin que los datos de un hilo de ejecución contaminen los cálculos del otro^15^.

Namespaces, Alias e Integración Semántica

En un entorno de producción donde interactúan múltiples librerías, es crítico estructurar la carga de dependencias de forma ordenada para evitar colisiones de nombres y ambigüedades en la interpretación de los tipos de datos estructurados por parte del compilador^3^.

Mecanismos de Importación y Resolución de Colisiones de Nombres

El enlace a una librería publicada se realiza mediante la palabra clave import indicando el camino único de publicación, compuesto por el nombre del publicador, el título de la librería y la versión de compilación principal requerida^3^:

Pine Script

import ActiveQuants/RiskEngine/2 as risk

import Institutional/CoreMetrics/4 as metrics

La asignación de un alias mediante la cláusula as determina el identificador del espacio de nombres bajo el cual se accederá a las funciones, constantes, enumeraciones y constructores de tipos expuestos por la librería^3^. Si dos librerías diferentes exponen métodos o funciones idénticos en su firma (por ejemplo, una función calcularStop()), la colisión nominal queda perfectamente resuelta al requerir el uso mandatorio del prefijo correspondiente al alias^3^:

Pine Script

// Resolución inequívoca de funciones homónimas mediante espacios de nombres

float stopConservador = risk.calcularStop(close)

float stopAgresivo = metrics.calcularStop(close)

Reglas para Declaraciones de Variables Basadas en Tipos de Librerías

El compilador de Pine Script v6 requiere la calificación inequívoca del espacio de nombres cuando se trabaja con variables que almacenan objetos definidos en librerías externas^3^. Se presentan dos escenarios operacionales:

- **Inicialización con Constructor Activo**: Si la variable se asigna de manera directa invocando el constructor .new() del tipo expuesto por la librería, la declaración explícita de su tipo en el lado izquierdo de la asignación es opcional, dado que el motor realiza la inferencia automática del tipo de datos basándose en el espacio de nombres del constructor^3^.
- **Inicialización Nula (na)**: Si se requiere declarar una variable que inicialmente apunte a una referencia ausente (na) para ser posteriormente inicializada o reasignada dentro de bloques de ejecución condicionales, la especificación explícita de su tipo de datos —anteponiendo el espacio de nombres calificado de la librería— es un requisito obligatorio de compilación^3^.

Pine Script

import Institutional/AccountManager/1 as manager

// Inicialización directa implícita (Permitida y recomendada por simplicidad)

cuentaActiva = manager.PerfilCliente.new(id = 89432, saldo = 500000.0)

// Inicialización de referencia nula explícita (Mandatoria bajo inicialización con 'na')

manager.PerfilCliente cuentaInactiva = na

if barstate.isconfirmed

    cuentaInactiva := manager.PerfilCliente.new(id = 11209, saldo = 0.0)

Es crucial resaltar que cada enumeración o tipo definido por el usuario (UDT) importado se consolida en un tipo nominal estrictamente único^13^. Dos UDTs declarados en librerías distintas, incluso si comparten exactamente la misma cantidad, tipo y nombre de campos internos, son tratados por el compilador como entidades lógicamente incomparables, y cualquier intento de conversión directa o asignación cruzada provocará un error de compilación inmediato^13^.

Mantenimiento de Ciclo de Vida y Versionamiento Semántico

El mantenimiento de librerías destinadas al despliegue en entornos de trading algorítmico institucional exige un control de versiones riguroso que prevenga la interrupción de las operaciones automatizadas de los sistemas clientes ante actualizaciones del código base^3^.

Funcionamiento del Versionado en TradingView

La plataforma de TradingView maneja un esquema de versionamiento estricto e inmutable^3^. La firma de importación especifica un número de versión mayor estático^3^:

No existe soporte para la resolución dinámica de la versión más reciente en tiempo de ejecución (como el uso de comodines o punteros dinámicos)^4^. Esto garantiza que un script en producción sea completamente inmune a las modificaciones del código fuente de la librería que su autor publique posteriormente^4^. Cada publicación con cambios destructivos incrementa la versión de la librería, y es responsabilidad del desarrollador del script consumidor actualizar manualmente la firma de importación para beneficiarse de las nuevas características^4^.

Ciclo de Vida: Librerías Públicas frente a Privadas

El control de acceso y las restricciones de uso varían según la visibilidad elegida en el momento de la publicación del código^3^:

- **Librerías Públicas**: Se publican bajo la licencia de dominio público y su código fuente es visible de forma transparente para toda la comunidad de TradingView^3^. Cualquier usuario de la plataforma puede consumirlas e importarlas en scripts tanto abiertos como cerrados (protegidos o de acceso restringido)^3^. La reutilización del código fuente original de estas librerías dentro de otros scripts de código abierto no requiere autorización previa, conforme a las normas de publicación de la plataforma, aunque se requiere el debido crédito al autor original^5^.
- **Librerías Privadas**: Mantienen su código fuente oculto para el público general. Únicamente el autor y aquellas cuentas con las que se comparta el enlace directo de la librería tienen permisos de importación^3^. Solo son compatibles con scripts de carácter privado o personal guardados en el editor local; ningún script publicado de forma pública en la sección de "Scripts de la Comunidad" puede importar una librería privada^3^.

Gestión de Breaking Changes en la Transición a Pine Script v6

Al actualizar librerías críticas de la versión v5 a la v6, los desarrolladores deben prestar especial atención a los cambios destructivos introducidos en el compilador^1^:

- **Eliminación del Cast de Booleanos**: Los tipos numéricos int y float ya no se convierten de manera implícita a bool^1^. Expresiones lógicas como if variable_int fallarán al compilar en v6^1^; debe emplearse una condición explícita como if variable_int != 0^18^.
- **Prohibición de Valores na en Booleanos**: Los tipos lógicos bool en v6 están estrictamente restringidos a los estados true o false^1^. Funciones de manejo de nulos como na(), nz() o fixnan() ya no aceptan variables de tipo booleano como argumentos admisibles^1^.
- **Evaluación de Cortocircuito (Lazy Evaluation)**: Los operadores lógicos and y or interrumpen la evaluación tan pronto como el resultado final queda determinado^1^. Esto introduce un peligro silencioso si la expresión del operando derecho contiene una función con persistencia histórica (como ta.ema() o ta.rsi()), ya que al no ejecutarse en cada barra por efecto del cortocircuito, su historial interno se corromperá, invalidando los cálculos subsiguientes^1^.
- **División de Enteros**: La división entre constantes de tipo entero (const int) en Pine Script v6 ahora produce un resultado real (float) en lugar de truncarse de forma automática^1^. Es imperativo emplear un casteo explícito con int() si se requiere la parte entera exacta para indexar arrays o definir longitudes de cálculo^1^.

La siguiente tabla presenta una comparativa técnica detallada de los cambios rompedores de compatibilidad (breaking changes) más importantes al migrar módulos hacia Pine Script v6, ofreciendo soluciones recomendadas de refactorización de código:

| **Área del Cambio** | **Comportamiento en Versión Anterior** | **Comportamiento en Versión v6** | **Solución de Ingeniería Requerida** | **Impacto Operativo en Producción** |
| --- | --- | --- | --- | --- |
| **Evaluación Lógica de Booleans** | Permite el valor na en variables y condiciones booleanas^1^. | Los tipos booleanos son estrictamente true o false y no aceptan na^1^. | Sustituir con evaluaciones explícitas o usar variables auxiliares de control de estado^1^. | Alto: Provoca errores de detención de cálculo inmediatos en tiempo de ejecución. |
| **Casteo Implícito Numérico** | Conversión implícita de int/float a lógico en condicionales (if 1 -> true)^1^. | Desactivado por completo; requiere compatibilidad de tipos lógica estricta^1^. | Comparar explícitamente el valor numérico contra cero o límites de control (if val != 0.0)^18^. | Crítico: El compilador bloqueará la ejecución del script de inmediato. |
| **Evaluación de Cortocircuito** | Ambos operandos de los operadores lógicos and y or se ejecutan en cada barra^1^. | Detiene la evaluación si el primer miembro define el resultado final^1^. | Extraer las funciones con persistencia temporal (ej. ta.*) a variables globales previas antes de la evaluación condicional^1^. | Crítico: Corrupción silenciosa del histórico de cálculos matemáticos. |
| **División de Constantes Enteras** | La división entre dos valores const int truncaba el residuo (división entera)^1^. | Retorna una fracción decimal de tipo float de precisión completa^1^. | Envolver la operación en el constructor de conversión explícita int() si se requiere índice entero^1^. | Medio: Altera ligeramente valores de períodos o índices de colecciones. |

Presupuesto de Tokens y Rendimiento de Compilación

La optimización de la modularidad en arquitecturas empresariales se ve altamente influenciada por la gestión del **presupuesto de tokens** de la plataforma TradingView^2^. Durante el proceso de análisis y traducción, cada script se transforma en un Lenguaje Intermedio (IL) tokenizado limitado estrictamente a  tokens por archivo principal de ejecución^2^.

La modularización estratégica mediante la importación de librerías independientes permite eludir este límite físico^2^. Cuando un script importa librerías externas bien diseñadas, el límite acumulativo de la jerarquía global se expande hasta permitir un presupuesto de hasta  de tokens^2^. Esto faculta a los desarrolladores a construir complejos sistemas multi-estrategia que de otro modo serían imposibles de compilar en un único archivo monolítico^2^.

Documentación Automática del Código de la Librería

La mantenibilidad del software y la facilidad de uso para los equipos internos dependen de la calidad de la documentación embebida en el código fuente de las librerías^8^. Pine Script v6 emplea un sistema de anotaciones que permite al motor de análisis estático de TradingView extraer la estructura semántica de la librería para poblar la descripción en el formulario de publicación y proporcionar completado automático en tiempo real^3^.

Estándar de Docstrings para Componentes de Librería

Las anotaciones deben colocarse inmediatamente encima de la firma del componente correspondiente utilizando el prefijo especial //@^8^. La tabla subsiguiente compendia la sintaxis y los casos de uso para las anotaciones disponibles en la plataforma:

Pine Script

//@version=6

library("EstiloCorporativo", overlay = false)

//@type Almacena la paleta de colores institucional del fondo de inversión.

//@field colorPrincipal Tono primario utilizado en plots de tendencia.

//@field colorSecundario Tono auxiliar para visualización de rangos estáticos.

export type PaletaColores

    color colorPrincipal

    color colorSecundario

//@enum Máquina de estados para la gobernanza del riesgo operativo de las posiciones.

//@field restringido No se permiten nuevas asignaciones de capital bajo este estado.

//@field monitoreado Permitido entrar con precaución y stop-loss dinámico activo.

//@field libre Operación normal bajo parámetros estándar de riesgo.

export enum EstadoRiesgo

    restringido = "Limite de Riesgo Superado"

    monitoreado = "Alerta de Volatilidad"

    libre = "Parametros Normales"

//@function Calcula de manera dinámica la exposición ajustada por el nivel de volatilidad actual del mercado.

//@param saldo Balance de cuenta líquido actual sobre el cual se calcula el riesgo.

//@param atrValor Lectura actual del indicador de rango verdadero medio (ATR).

//@param factorRiesgo Multiplicador de escala de riesgo determinado por la mesa de control.

//@returns Un número flotante con el tamaño exacto del lote de entrada sugerido.

export calcularPosicionExposicion(float saldo, float atrValor, simple float factorRiesgo) =>

    float exposicion = (saldo * factorRiesgo) / atrValor

    exposicion

Cuando este módulo se importa en el editor de TradingView, el servidor de lenguaje (LSP) procesa las anotaciones de forma transparente^18^. Al posicionar el cursor sobre la función calcularPosicionExposicion(), se despliega una interfaz que detalla su comportamiento, el significado de cada parámetro esperado, sus requisitos de calificación (simple float), el tipo de dato devuelto y la enumeración sugerida para controlar el flujo de llamadas de forma interactiva^18^.

Arquitectura de Referencia de Cuatro Capas

Para ilustrar de manera definitiva el diseño de software algorítmico institucional bajo Pine Script v6, se desarrolla a continuación un sistema de trading modular basado en el cruce adaptativo de la media móvil exponencial triple (). Este sistema se estructura estrictamente en cuatro niveles desacoplados de software, maximizando la modularidad y facilitando el mantenimiento y testeo independiente de cada componente.

Nivel 1: Librería de Tipos (InstitutionalTypes)

Esta capa define las estructuras de datos fundamentales, las enumeraciones lógicas del estado del sistema y las constantes globales. No realiza cálculos ni contiene variables dinámicas dependientes del tiempo, sirviendo únicamente como la base terminológica común de la arquitectura.

Pine Script

//@version=6

// @description Capa Base (Nivel 1): Define UDTs, enums y constantes del sistema de trading corporativo.

library("InstitutionalTypes", overlay = false)

// Declaración de constantes de límites corporativos de riesgo

export const float RIESGO_MAXIMO_PERMITIDO = 0.03

export const float RIESGO_PREDETERMINADO = 0.01

// Enumeración del estado estructural del mercado

export enum RegimenTendencia

    alcista = "Mercado en Alza"

    bajista = "Mercado en Baja"

    rango = "Mercado en Consolidacion"

// Estructura contenedora del estado analítico de un activo financiero

export type EstadoMercado

    float precioActual

    float emaRapida

    float emaLenta

    RegimenTendencia regimen = RegimenTendencia.rango

Nivel 2: Librería de Cálculos Core (QuantitativeCore)

Esta capa aloja los algoritmos cuantitativos y la lógica de detección de señales de negociación. No dibuja elementos en pantalla ni gestiona órdenes del simulador, operando de manera aislada de las capas externas mediante funciones puras que consumen la librería de tipos básica.

Pine Script

//@version=6

// @description Capa Logica (Nivel 2): Implementa algoritmos matematicos y gestion de senales analiticas.

library("QuantitativeCore", overlay = false)

import ActiveQuants/InstitutionalTypes/1 as types

//@function Evalúa el estado cuantitativo actual del mercado.

//@param precio Serie de datos de precios (típicamente cierre de barras).

//@param periodoRapido Longitud para el cálculo de la EMA de velocidad rápida.

//@param periodoLento Longitud para el cálculo de la EMA de velocidad lenta.

//@returns Un objeto estructurado `EstadoMercado` con las métricas del bar actual.

export evaluarEstado(float precio, int periodoRapido, int periodoLento) =>

    float fastEMA = ta.ema(precio, periodoRapido)

    float slowEMA = ta.ema(precio, periodoLento)

    types.RegimenTendencia regimenDetectado = types.RegimenTendencia.rango

    if fastEMA > slowEMA

        regimenDetectado := types.RegimenTendencia.alcista

    else if fastEMA < slowEMA

        regimenDetectado := types.RegimenTendencia.bajista

    types.EstadoMercado estadoActual = types.EstadoMercado.new(

         precioActual = precio,

         emaRapida = fastEMA,

         emaLenta = slowEMA,

         regimen = regimenDetectado

         )

    estadoActual

//@function Compara el estado actual para confirmar si ha ocurrido un cruce alcista (Crossover).

//@param estado Instancia del objeto de estado actual.

//@returns Un booleano verdadero si la EMA rápida cruzó por encima de la EMA lenta en el bar actual.

export esCruceAlcista(types.EstadoMercado estado) =>

    bool alcista = ta.crossover(estado.emaRapida, estado.emaLenta)

    alcista

//@function Compara el estado actual para confirmar si ha ocurrido un cruce bajista (Crossunder).

//@param estado Instancia del objeto de estado actual.

//@returns Un booleano verdadero si la EMA rápida cruzó por debajo de la EMA lenta en el bar actual.

export esCruceBajista(types.EstadoMercado estado) =>

    bool bajista = ta.crossunder(estado.emaRapida, estado.emaLenta)

    bajista

Nivel 3: Script de Interfaz y Visualización (TrendUI)

Este script actúa como indicador en el gráfico principal de TradingView. Su responsabilidad exclusiva es recoger los parámetros del usuario, consumir las librerías analíticas básicas y renderizar tablas y gráficos avanzados en el gráfico sin interactuar con el motor de estrategias.

Pine Script

//@version=6

indicator("Trend Analyser Board - Institutional UI", overlay = true)

import ActiveQuants/InstitutionalTypes/1 as types

import ActiveQuants/QuantitativeCore/1 as core

// Carga de parámetros configurables por el operador institucional

int emaRapidaLen = input.int(21, "Periodo EMA de Tendencia Rápida", minval = 5)

int emaLentaLen = input.int(55, "Periodo EMA de Tendencia Lenta", minval = 10)

color tonoAlcista = input.color(color.green, "Color Alcista")

color tonoBajista = input.color(color.red, "Color Bajista")

// Invocación segura de la lógica cuantitativa del Nivel 2

types.EstadoMercado analisisInfo = core.evaluarEstado(close, emaRapidaLen, emaLentaLen)

// Renderizado gráfico de líneas analíticas

plot(analisisInfo.emaRapida, "EMA de Velocidad Rápida", color = analisisInfo.regimen == types.RegimenTendencia.alcista ? tonoAlcista : tonoBajista, linewidth = 2)

plot(analisisInfo.emaLenta, "EMA de Velocidad Lenta", color = color.gray, linewidth = 1)

// Identificación y señalización de eventos críticos

bool entradaCompra = core.esCruceAlcista(analisisInfo)

bool entradaVenta = core.esCruceBajista(analisisInfo)

plotshape(entradaCompra, title = "Trigger Compra", style = shape.labelup, location = location.belowbar, color = tonoAlcista, size = size.normal, text = "BUY", textcolor = color.white)

plotshape(entradaVenta, title = "Trigger Venta", style = shape.labeldown, location = location.abovebar, color = tonoBajista, size = size.normal, text = "SELL", textcolor = color.white)

// Visualización informativa mediante panel de control (Dashboard)

var table panelExposicion = table.new(position.top_right, 2, 2, bgcolor = color.new(color.black, 40))

if barstate.islast

    table.cell(panelExposicion, 0, 0, "Indicador Clave", text_color = color.white, bgcolor = color.black)

    table.cell(panelExposicion, 1, 0, "Estado / Lectura", text_color = color.white, bgcolor = color.black)

    table.cell(panelExposicion, 0, 1, "Estado Estructural", text_color = color.white)

    table.cell(panelExposicion, 1, 1, str.tostring(analisisInfo.regimen), text_color = analisisInfo.regimen == types.RegimenTendencia.alcista ? tonoAlcista : tonoBajista)

Nivel 4: Script de Ejecución y Estrategia (InstitutionalRunner)

Este script actúa como el motor de orquestación de backtesting e integración operativa con brokers^20^. Realiza los cálculos monetarios precisos del tamaño de la posición ajustados por riesgo y envía instrucciones directas de compra y venta al simulador utilizando las señales del core matemático.

Pine Script

//@version=6

strategy("Trend Follower Core Strategy - Institutional", 

     overlay = true, 

     initial_capital = 500000, 

     default_qty_type = strategy.percent_of_equity, 

     default_qty_value = 100.0, 

     commission_type = strategy.commission.percent, 

     commission_value = 0.04

     )

import ActiveQuants/InstitutionalTypes/1 as types

import ActiveQuants/QuantitativeCore/1 as core

// Parametrización operativa del algoritmo

int fastEMAInput = input.int(21, "Periodo EMA Rápida")

int slowEMAInput = input.int(55, "Periodo EMA Lenta")

float fraccionRiesgo = input.float(1.5, "Porcentaje Máximo de Riesgo (%)", minval = 0.1, maxval = 5.0) / 100.0

// Carga analítica del estado actual del mercado desde la capa del core de cálculo

types.EstadoMercado mercadoEstado = core.evaluarEstado(close, fastEMAInput, slowEMAInput)

// Determinación exacta de señales lógicas de compra y venta

bool senalComprar = core.esCruceAlcista(mercadoEstado)

bool senalVender = core.esCruceBajista(mercadoEstado)

// Gestión matemática del Stop Loss y tamaño dinámico de la posición

float stopLossPips = ta.atr(14) * 2.5

float saldoDisponible = strategy.equity

float capitalEnRiesgo = saldoDisponible * math.min(fraccionRiesgo, types.RIESGO_MAXIMO_PERMITIDO)

// Validación de pips de stop para evitar divisiones matemáticas por cero o nulos

float volumenunidades = stopLossPips > 0.0 ? capitalEnRiesgo / stopLossPips : na

// Ejecución controlada de órdenes en el simulador sin usar el parámetro deprecated 'when'

if senalComprar and not na(volumenunidades)

    strategy.entry("Apertura Compra", strategy.long, qty = volumenunidades)

if senalVender and not na(volumenunidades)

    strategy.entry("Apertura Venta", strategy.short, qty = volumenunidades)

// Gestión automatizada del riesgo de mercado una vez dentro de la posición

if strategy.position_size > 0

    float precioEntradaPromedio = strategy.position_avg_price

    float nivelStopLoss = precioEntradaPromedio - stopLossPips

    float nivelTakeProfit = precioEntradaPromedio + (stopLossPips * 2.0)

    strategy.exit("Salida Compra", "Apertura Compra", stop = nivelStopLoss, limit = nivelTakeProfit)

if strategy.position_size < 0

    float precioEntradaPromedio = strategy.position_avg_price

    float nivelStopLoss = precioEntradaPromedio + stopLossPips

    float nivelTakeProfit = precioEntradaPromedio - (stopLossPips * 2.0)

    strategy.exit("Salida Venta", "Apertura Venta", stop = nivelStopLoss, limit = nivelTakeProfit)

Fuentes citadas

- Pine Script v6: Common Questions and Mistakes - TradersPost, https://blog.traderspost.io/article/pine-script-v6-faq
- The Main Limitations of Pine Script on TradingView - Quant Nomad, https://quantnomad.com/the-main-limitations-of-pine-script-on-tradingview/
- Concepts / Libraries - TradingView, https://www.tradingview.com/pine-script-docs/concepts/libraries/
- Concepts / Libraries - TradingView, https://www.tradingview.com/pine-script-docs/v5/concepts/libraries/
- What is a Pine Library and how do I use it? - TradingView, https://www.tradingview.com/support/solutions/43000638371-what-is-a-pine-library-and-how-do-i-use-it/
- Language / Type system - TradingView, https://www.tradingview.com/pine-script-docs/v5/language/type-system/
- Language / Type system - TradingView, https://www.tradingview.com/pine-script-docs/language/type-system/
- pine-script-reference | Skills Marke... - LobeHub, https://lobehub.com/skills/adamelliotfields-skills-pine-script-reference
- Export Constants from Pine Script Libraries (v6) - TradersPost, https://blog.traderspost.io/article/pine-script-library-constant-exports
- Pine Script Structure and Requirements | PDF | Scope (Computer Science) | Compiler, https://www.scribd.com/document/859274981/00009-language-Script-structure
- How to define the 'return type form' of a pinescript method/function? - Stack Overflow, https://stackoverflow.com/questions/76014656/how-to-define-the-return-type-form-of-a-pinescript-method-function
- Language / Objects - TradingView, https://www.tradingview.com/pine-script-docs/language/objects/
- Complete Guide to Enums in Pine Script v6 - TradersPost, https://blog.traderspost.io/article/pine-script-v6-enums-guide
- How to Change global variable from function in pine script? - Stack Overflow, https://stackoverflow.com/questions/60904563/how-to-change-global-variable-from-function-in-pine-script
- Function Isolation | PyneCore Documentation, https://pynecore.org/docs/advanced/function-isolation/
- Language / Enums - TradingView, https://www.tradingview.com/pine-script-docs/v5/language/enums/
- Pine Script v6 Migration Guide | PDF | Boolean Data Type - Scribd, https://www.scribd.com/document/872972761/Migration-Guides-to-Pine-Script-Version-6
- tradesdontlie/pine-script-v6-extension - GitHub, https://github.com/tradesdontlie/pine-script-v6-extension
- Language / Script structure - TradingView, https://www.tradingview.com/pine-script-docs/language/script-structure/
- Turn ChatGPT into a TradingView Strategy – Full Automation Guide, https://blog.alphainsider.com/how-to-create-automate-pine-script-strategies-with-chatgpt-2/