# Guía Canónica de Importación de Datos Externos y Custom Symbols en MetaTrader 5

> **Autor Institucional:** QRT Solutions  
> **Ámbito:** Repositorio Maestro `seminario_2` / Módulo `MT5`  
> **Estado:** Documento Operativo Oficial y Vinculante  
> **Compatibilidad:** macOS (Apple Silicon / Wine) y Windows 10/11 x64

Este documento establece el protocolo estándar institucional para convertir, normalizar e inyectar cualquier conjunto de datos históricos externos (TradingView, TradeStation, NinjaTrader, Binance, Yahoo Finance, Rithmic, etc.) dentro de MetaTrader 5 para la ejecución de backtesting con cero repainting y máxima fidelidad.

---

## 1. Tabla de Fuentes y Trazabilidad

Conforme a la regla de consolidación del ecosistema, este documento unifica el conocimiento técnico disperso en los siguientes módulos del repositorio:

| Sección del Documento | Archivo Fuente Original | Aporte Técnico |
| :--- | :--- | :--- |
| **API Custom Symbols & Ticks** | [`MT5/knowledge/MQL5_ Capacidades Avanzadas y Extensión.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/knowledge/MQL5_%20Capacidades%20Avanzadas%20y%20Extensi%C3%B3n.md) | Funciones `CustomSymbolCreate`, `CustomRatesReplace`, `CustomRatesUpdate` y alineación temporal. |
| **Flujos de Datos en Tiempo Real** | [`MT5/knowledge/MT5_ Flujos de Datos en Tiempo Real.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/knowledge/MT5_%20Flujos%20de%20Datos%20en%20Tiempo%20Real.md) | Estructura interna de ticks `MqlTick` y procesamiento de milisegundos. |
| **Arquitectura CLI & Wine** | [`MT5/AGENT_CONNECTION_GUIDE.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/AGENT_CONNECTION_GUIDE.md) | Rutas absolutas de Wine en macOS, variables de entorno y comandos `mt5_agent_bridge.py`. |
| **Motor de Conversión Universal** | [`MT5/scripts/universal_data_converter.py`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/scripts/universal_data_converter.py) | Algoritmo de streaming para procesar más de 1.2M velas/seg con detección heurística de columnas. |
| **Inyección Nativa MQL5** | [`MT5/scripts/Script_Universal_Rates_Injector.mq5`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/scripts/Script_Universal_Rates_Injector.mq5) | Script compilable para creación automática de activo y escritura en base de datos. |

---

## 2. Fundamentos de Arquitectura de Datos en MT5

### 2.1. El Concepto de Símbolo Personalizado (Custom Symbol)
MetaTrader 5 no permite sobreescribir los datos de los símbolos provistos por el broker en cuentas comerciales para evitar fraudes y discrepancias de liquidación. Por ello, la terminal implementa el subsistema de **Custom Symbols**:
* Permite crear activos sintéticos o externos (`CUSTOM_NQ_M5`, `CUSTOM_BTC_D1`, etc.).
* Permite inyectar flujos de velas completas (`MqlRates`) o ticks individuales (`MqlTick`).
* Se integra de forma transparente con el Strategy Tester, permitiendo ejecutar Asesores Expertos como si fuese un activo estándar.

### 2.2. Regla de Oro de la Temporalidad Base (M1 o M5)
* Si se importan datos en **M1 (1 minuto)**, el motor interno de MT5 construye de forma nativa e instantánea todas las temporalidades superiores (**M5, M15, M30, H1, H4, D1**).
* Si se importan datos en **M5 (5 minutos)**, MT5 podrá construir temporalidades múltiplos (**M10, M15, M30, H1, H4, D1**), pero no podrá descomponer velas hacia M1.
* Por tanto, para datasets que provienen en M5 (como los futuros del CME `@NQ_5m.csv`), el símbolo debe evaluarse en M5 o superior.

---

## 3. Protocolo de Ejecución 100% Autónomo (Para Agentes de IA)

Cualquier agente que clone este repositorio puede ejecutar la ingesta y preparación de datos externos mediante un único comando CLI sin interacción manual:

### Paso 1: Ejecutar el Conversor y Desplegador Universal
Desde la raíz del repositorio, ejecutar el CLI bridge:

```bash
python3 MT5/scripts/mt5_agent_bridge.py import-data <RUTA_AL_ARCHIVO_CSV> [--from-date AAAA.MM.DD] [--to-date AAAA.MM.DD]
```

**Ejemplo real con el dataset de Nasdaq:**
```bash
python3 MT5/scripts/mt5_agent_bridge.py import-data masterclass/@NQ_5m.csv --from-date 2020.01.01
```

#### ¿Qué ejecuta este comando automáticamente?
1. **Detección Heurística de Columnas:** Detecta si el archivo usa comas, tabulaciones o puntos y comas; mapea las columnas `Open`, `High`, `Low`, `Close`, `Volume` y `Timestamp` sin importar el idioma o mayúsculas.
2. **Normalización ISO a Estándar MT5:** Extrae la fecha en `YYYY.MM.DD` y la hora en `HH:MM`, eliminando offsets de zona horaria (`+00:00` o `Z`).
3. **Formateo Estricto de 7 Columnas:** Genera `<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<TICKVOL>,<VOL>`.
4. **Despliegue Multi-Plataforma:** Copia el archivo optimizado directamente a la carpeta nativa `MQL5/Files/` del terminal (sea macOS Wine o Windows nativo).

### Paso 2: Ejecución del Inyector Universal en MT5
Para registrar el activo en la base de datos de MT5, el agente o usuario cuenta con el script precompilado:
[`MT5/scripts/Script_Universal_Rates_Injector.mq5`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/scripts/Script_Universal_Rates_Injector.mq5)

Parámetros de entrada del script:
* `InpSymbolName`: Nombre del símbolo a crear (ej. `CUSTOM_NQ_M5` o `CUSTOM_GC_M5`).
* `InpFileName`: Nombre del archivo CSV generado en `MQL5/Files` (ej. `@NQ_5m_MT5.csv`).
* `InpBaseClone`: Símbolo base del broker a clonar para copiar márgenes (`US100`, `XAUUSD`, `BTCUSD`).
* `InpDigits`: Dígitos decimales (ej. 2 para índices y oro, 5 para divisas).

Al ejecutarse el script:
1. Verifica si el símbolo existe; si no, lo crea con `CustomSymbolCreate()` copiando propiedades del broker.
2. Abre y lee el CSV directamente desde `MQL5/Files/`.
3. Inyecta el bloque de velas con `CustomRatesReplace()` o `CustomRatesUpdate()`.
4. Actualiza y refresca el gráfico en pantalla inmediatamente con `ChartSetSymbolPeriod()` y `ChartRedraw()`.

---

## 4. Protocolo Manual Paso a Paso (Para Desarrolladores y Traders)

Si un usuario humano prefiere realizar la carga visualmente a través de la interfaz gráfica de MT5:

### Paso 1: Convertir los Datos
Ejecutar en la terminal el script conversor:
```bash
python3 MT5/scripts/universal_data_converter.py -i <RUTA_CSV>
```
El conversor generará un archivo `*_MT5.csv` y lo dejará disponible tanto en el directorio de origen como en el Escritorio.

### Paso 2: Crear el Símbolo Personalizado (GUI)
1. En MT5, presionar **`Ctrl + U`** (o menú *Ver -> Símbolos*).
2. Hacer clic en **"Crear símbolo personalizado"** (*Create Custom Symbol*).
3. En **Copiar de (*Copy from*)**, seleccionar el activo más similar de tu broker:
   * Para Nasdaq: `US100`, `USTEC` o `NAS100`.
   * Para Oro: `XAUUSD` o `GOLD`.
   * Para Bitcoin: `BTCUSD`.
   * Para Euro/Dólar: `EURUSD`.
4. En **Símbolo (*Symbol*)**, escribir el identificador deseado (ej. `CUSTOM_NQ_M5`).
5. En **Ruta (*Path*)**, colocar `Custom\Futures` o `Custom\Crypto`.
6. Presionar **Aceptar**.

### Paso 3: Importar las Barras (GUI)
1. En la misma ventana de Símbolos (`Ctrl + U`), seleccionar el símbolo recién creado.
2. Hacer clic en la pestaña **"Barras"** (*Bars*) en la esquina superior derecha.
3. En el selector de período, seleccionar la temporalidad del archivo (ej. **`M5`** o **`M1`**).
4. Hacer clic en **"Importar barras"** (*Import Bars*).
5. Presionar **"Examinar"** (*Browse*) y seleccionar el archivo `*_MT5.csv`.
6. Presionar **Aceptar**. MT5 procesará el historial y mostrará la tabla de velas.
7. Presionar el botón amarillo **"Mostrar símbolo"** (*Show Symbol*).

### Paso 4: Ejecutar el Backtest
1. Abrir el Strategy Tester (**`Ctrl + R`**).
2. En el menú desplegable **Símbolo**, seleccionar el símbolo personalizado (`CUSTOM_NQ_M5`).
3. En **Período**, seleccionar la temporalidad deseada (igual o superior a la importada).
4. Seleccionar el Asesor Experto y presionar **"Empezar"** (*Start*).

---

## 5. Matriz de Formato y Estándares de Archivo CSV

Para que MT5 reconozca las columnas sin ambigüedad, el archivo CSV final debe ajustarse estrictamente a este esquema:

```csv
<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<TICKVOL>,<VOL>
2024.01.02,00:00,19485.50,19486.25,19483.25,19484.75,199,219
2024.01.02,00:05,19485.00,19485.25,19482.75,19484.00,101,116
```

| Columna | Tipo de Dato | Formato Exigido | Ejemplo |
| :--- | :--- | :--- | :--- |
| `<DATE>` | Cadena | `AAAA.MM.DD` (con puntos o guiones) | `2024.01.02` |
| `<TIME>` | Cadena | `HH:MM` o `HH:MM:SS` (24 horas) | `16:30` |
| `<OPEN>` | Decimal | Punto como separador decimal | `19485.50` |
| `<HIGH>` | Decimal | Punto como separador decimal | `19486.25` |
| `<LOW>` | Decimal | Punto como separador decimal | `19483.25` |
| `<CLOSE>` | Decimal | Punto como separador decimal | `19484.75` |
| `<TICKVOL>` | Entero | Número entero de cambios de precio | `199` |
| `<VOL>` | Entero | Número entero de contratos o lotes | `219` |

---

## 6. Resolución de Problemas y Errores Comunes (Troubleshooting)

### Error: El gráfico aparece completamente en negro
* **Causa:** El símbolo personalizado fue creado, pero aún no se han inyectado barras históricas, o se abrió en una temporalidad inferior a la data importada (ej. intentar ver M1 cuando solo se importó M5).
* **Solución:** Ejecutar el inyector MQL5 o verificar en `Ctrl + U` -> pestaña *Barras* que existan registros en la temporalidad seleccionada.

### Error: `CustomRatesUpdate error 5300 (ERR_CUSTOM_SYMBOL_NOT_FOUND)`
* **Causa:** El símbolo no ha sido creado previamente mediante `CustomSymbolCreate()`.
* **Solución:** Ejecutar el Paso 1 de creación antes de intentar escribir barras.

### Error: Fechas rechazadas por el parser de MT5
* **Causa:** Presencia de identificadores de zona horaria como `+00:00` o sufijos `Z`.
* **Solución:** Utilizar [`MT5/scripts/universal_data_converter.py`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/scripts/universal_data_converter.py), el cual limpia automáticamente los identificadores de huso horario y normaliza a formato puro `AAAA.MM.DD`.

### Error: El Strategy Tester dice "Waiting for update" o arroja error de autorización del Core
* **Causa:** Instancia residual de simulación o proceso externo reteniendo el puerto de simulación local (puerto 3000).
* **Solución:** Ejecutar en terminal:  
  `python3 MT5/scripts/mt5_agent_bridge.py clean-agents`
