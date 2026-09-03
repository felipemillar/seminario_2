# AGENT CONNECTION GUIDE - MetaTrader 5 (macOS & Windows)

> **Autor Institucional:** QRT Solutions  
> **Ambito:** Guia Maestra para Agentes de IA (Antigravity, Claude Code, Cursor, Windsurf, OpenAI Codex) y Desarrolladores  
> **Sistemas Compatibles:** macOS (Apple Silicon / Intel con Wine) y Windows 10/11 x64 (Nativo)

---

## 1. Proposito y Arquitectura Multiplataforma

Esta guia establece el protocolo tecnico para que cualquier Agente de IA pueda interactuar de forma autonoma, compilar codigo MQL5, diagnosticar cuentas y extraer resultados de backtesting en MetaTrader 5, tanto en entornos **macOS** como **Windows**.

```
+------------------------------------------------------------------------+
| AGENTES DE IA (Antigravity, Claude Code, Cursor, OpenAI Codex)         |
+-----------------------------------+-+----------------------------------+
                                    |
           +------------------------+------------------------+
           |                                                 |
           v                                                 v
+---------------------------+                     +----------------------+
| VIA 1: SERVIDOR MCP       |                     | VIA 2: CLI BRIDGE    |
| (MT5/mcp_server/server.py)|                     | (mt5_agent_bridge.py)|
+-------------+-------------+                     +----------+-----------+
              |                                              |
              +---------------------+------------------------+
                                    |
            +-----------------------+-----------------------+
            | (Deteccion automatica de Sistema Operativo)   |
            v                                               v
+-----------------------------+           +------------------------------+
| ENTORNO MACOS (WINE)        |           | ENTORNO WINDOWS (NATIVO)     |
| - WINEPREFIX net.metaquotes |           | - C:\Program Files\MT5       |
| - MetaEditor via Wine CLI   |           | - MetaEditor 64 CLI Nativo   |
| - Terminal x64 sobre Wine   |           | - Terminal x64 / Python MT5  |
+-----------------------------+           +------------------------------+
```

---

## 2. Mapeo de Rutas del Sistema

### A. Entorno Windows (Nativo)
* **Directorio Raiz MT5:** `C:\Program Files\MetaTrader 5` (o variable de entorno `%MT5_PATH%`).
* **Ejecutable Terminal:** `C:\Program Files\MetaTrader 5\terminal64.exe`.
* **Ejecutable MetaEditor:** `C:\Program Files\MetaTrader 5\metaeditor64.exe`.
* **Directorio MQL5:** `C:\Program Files\MetaTrader 5\MQL5\` (o `%APPDATA%\MetaQuotes\Terminal\<INSTANCE_ID>\MQL5\` si no se ejecuta con el flag `/portable`).
* **Asesores Expertos:** `MQL5\Experts\` y `MQL5\Experts\Advisors\`.
* **Indicadores:** `MQL5\Indicators\`.
* **Logs del Terminal:** `logs\*.log` (codificados en UTF-16 LE).
* **Logs del Tester:** `Tester\Agent-*\logs\*.log`.

### B. Entorno macOS (Apple Silicon / Intel via Wine)
* **Binario Wine:** `/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine`
* **Wine Prefix:** `~/Library/Application Support/net.metaquotes.wine.metatrader5`
* **Directorio Raiz MT5:** `~/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5`
* **Directorio MQL5:** `.../drive_c/Program Files/MetaTrader 5/MQL5`
* **Asesores Expertos:** `.../MQL5/Experts/` y `.../MQL5/Experts/Advisors/`
* **Indicadores:** `.../MQL5/Indicators/`
* **Logs del Terminal:** `.../drive_c/Program Files/MetaTrader 5/logs/*.log` (UTF-16 LE)
* **Logs del Tester:** `.../drive_c/Program Files/MetaTrader 5/Tester/Agent-*/logs/*.log`

---

## 3. Mecanismo 1: Servidor MCP (Model Context Protocol)

El servidor [`MT5/mcp_server/server.py`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/mcp_server/server.py) implementa el estandar oficial de MCP sobre stdio (JSON-RPC 2.0). Funciona de manera identica en macOS y Windows sin dependencias externas pesadas.

### Herramientas Expuestas para Agentes:
1. `mt5_status`: Devuelve el estado de ejecucion del terminal, cuenta activa, broker, servidor y total de simbolos sincronizados.
2. `mt5_compile`: Compila de forma desatendida cualquier archivo `.mq5` y reporta errores, advertencias y ruta del `.ex5`.
3. `mt5_deploy_expert`: Compila y deposita el EA en las carpetas `MQL5/Experts/` y `MQL5/Experts/Advisors/`.
4. `mt5_last_backtest_metrics`: Extrae y analiza las metricas cuantitativas de la ultima simulacion del Strategy Tester (Balance final, P&L neto, Profit Factor, Win Rate, Payoff Ratio y motivos de salida).
5. `mt5_clean_agents`: Termina procesos huerfanos de simulacion en el puerto local 3000.

### Configuracion en Clientes de IA:

#### Configuracion para macOS (`claude_desktop_config.json` o Cursor / Antigravity):
```json
{
  "mcpServers": {
    "metatrader5": {
      "command": "python3",
      "args": [
        "/Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/mcp_server/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

#### Configuracion para Windows (`claude_desktop_config.json` o Cursor):
```json
{
  "mcpServers": {
    "metatrader5": {
      "command": "python",
      "args": [
        "C:\\Proyectos_Desarrollo\\seminario_2\\MT5\\mcp_server\\server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "MT5_PATH": "C:\\Program Files\\MetaTrader 5"
      }
    }
  }
}
```

```

---

## 3.1. Servidor MCP Nativo de MetaTrader 5 y MetaEditor (HTTP / JSON-RPC 2.0)

MetaTrader 5 integra un **servidor MCP interno nativo** basado en HTTP y Server-Sent Events (SSE), corriendo en:
* **Terminal MT5 (`terminal`):** `http://127.0.0.1:22346/mcp`
* **MetaEditor 64 (`metaeditor`):** `http://127.0.0.1:22345/mcp`

### Activacion en MT5:
1. En el terminal MT5, ir a: *Herramientas -> Opciones -> pestana MCP*.
2. Marcar la casilla **`Enable internal server`**.
3. El puerto asignado por defecto es `22346` con token Bearer configurable.

### Configuracion en Clientes de IA:
Configurado directamente en los archivos del repositorio [`.mcp.json`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/.mcp.json) y [`.codex/config.toml`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/.codex/config.toml):

```json
{
  "mcpServers": {
    "terminal": {
      "type": "http",
      "url": "http://127.0.0.1:22346/mcp",
      "headers": {
        "Authorization": "Bearer IIin+jBM/DNuDPG9tBdStKpZ4Vt4YNFjJkHK+0MmwX"
      }
    }
  }
}
```

### Ciclo de Vida y Protocolo de Handshake Obligatorio:
El servidor MCP de MetaQuotes exige un handshake estricto en tres fases antes de permitir llamadas a herramientas operativas:

1. **`initialize`**: Se envia la version del protocolo (`2025-06-18`) y las capacidades del cliente. El servidor retorna las cabeceras HTTP con un identificador de sesion unico: `Mcp-Session-Id`.
2. **`notifications/initialized`**: Confirmacion de sesion activa.
3. **`tools/call` -> `get_workspace_info` (MANDATORIO)**: Por directiva de MetaQuotes, la primera llamada de toda sesion **debe** ser obligatoriamente `get_workspace_info`. Si no se ejecuta, cualquier llamada posterior fallara con error `-32600 (MCP session is not initialized)`.

---

## 3.2. Consulta de Instrumentos y Datos de Mercado via MCP

El servidor MCP nativo expone herramientas para auditoria cuantitativa del universo de activos del broker:

### 1. `get_marketwatch_symbols`: Auditoria de Activos y Precios en Tiempo Real
Devuelve la lista completa de simbolos cargados en la ventana de Market Watch con sus propiedades financieras:

* **Estructura del Objeto de Simbolo:**
  * `symbol`: Ticker oficial (ej. `AAPL.US`, `US100`, `EURUSD`).
  * `description`: Nombre completo de la compania o ETF.
  * `sector` / `industry`: Clasificacion sectorial (ej. `Technology`, `Utilities`, `Healthcare`).
  * `trade_mode_name`: Estado de tradeabilidad:
    * `"full"`: **100% Tradeable** (Permite ordenes BUY y SELL sin restricciones).
    * `"close only"`: Solo permite cerrar posiciones abiertas.
    * `"disabled"`: Trading inhabilitado por el broker.
  * `bid` / `ask`: Ultima cotizacion de compra y venta.
  * `price_close`: Precio de cierre oficial de la jornada anterior.
  * `price_open`: Precio de apertura de la jornada actual.
  * `spread_float`: Booleano que indica si el spread es flotante.
  * `volume_min` / `volume_max`: Limites de tamano de posicion.
  * `contract_size`: Multiplicador del contrato (ej. 1.0 para acciones CFD, 100 para futuros).
  * `currency_margin` / `currency_profit`: Moneda de liquidacion (USD).

* **Formula para Calcular la Variacion Porcentual Diaria:**
  ```python
  change_pct = ((bid - price_close) / price_close) * 100.0
  ```

### 2. `get_chart_history`: Extraccion de Velas Historicas OHLCV
Permite descargar directamente las velas del grafico para cualquier activo y temporalidad:

* **Parametros de Entrada:**
  * `symbol`: Nombre exacto del simbolo (ej. `EIX.US`, `CUSTOM_NQ_M5`).
  * `period`: Temporalidad (`M1`, `M5`, `M15`, `M30`, `H1`, `D1`, `W1`, `MN1`).
  * `datetime_from`: Fecha de inicio en formato ISO (ej. `2026-08-25T00:00:00Z`).
  * `datetime_to`: Fecha de fin en formato ISO (ej. `2026-09-03T12:00:00Z`).
* **Retorno:** Array de objetos `{ time, open, high, low, close, tick_volume, spread }`.

---

## 3.3. Comandos CLI para Consultas MCP (Uso Inmediato para Agentes)

El script puente [`MT5/scripts/mt5_agent_bridge.py`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/scripts/mt5_agent_bridge.py) encapsula automaticamente el handshake HTTP, la extraccion del token desde `.mcp.json` y la ejecucion de `get_workspace_info`:

```bash
# 1. Consultar todos los instrumentos del mercado americano que sean tradeables (trade_mode = full)
python3 MT5/scripts/mt5_agent_bridge.py mcp-symbols --filter .US

# 2. Consultar instrumentos de un sector o empresa especifica (ej. Fortinet o Ciberseguridad)
python3 MT5/scripts/mt5_agent_bridge.py mcp-symbols --filter FTNT.US

# 3. Consultar indices americanos
python3 MT5/scripts/mt5_agent_bridge.py mcp-symbols --filter US100

# 4. Descargar velas historicas diarias (D1) de un activo via MCP
python3 MT5/scripts/mt5_agent_bridge.py mcp-history EIX.US --period D1 --from-date 2026-08-25T00:00:00Z --to-date 2026-09-03T12:00:00Z

# 5. Descargar velas intradiarias M5 de un activo via MCP
python3 MT5/scripts/mt5_agent_bridge.py mcp-history CUSTOM_NQ_M5 --period M5 --from-date 2026-09-02T14:30:00Z --to-date 2026-09-02T21:00:00Z
```

---

## 4. Mecanismo 2: Script CLI Bridge Multiplataforma (`mt5_agent_bridge.py`)

El script [`MT5/scripts/mt5_agent_bridge.py`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/scripts/mt5_agent_bridge.py) detecta automaticamente si se ejecuta en Windows o macOS y despacha las operaciones correspondientes:

```bash
# Diagnostico del entorno y rutas de MT5
python mt5_agent_bridge.py env

# Estado del terminal, cuenta activa y broker
python mt5_agent_bridge.py status

# Compilar silenciosamente un archivo MQL5 (.mq5)
python mt5_agent_bridge.py compile ruta/a/estrategia.mq5

# Compilar y desplegar en la carpeta Experts de MT5
python mt5_agent_bridge.py deploy ruta/a/estrategia.mq5

# Extraer metricas del ultimo backtest ejecutado
python mt5_agent_bridge.py last-test

# Liberar puerto 3000 y matar procesos metatester huerfanos
python mt5_agent_bridge.py clean-agents
```

---

## 5. Mecanismo 3: Comandos de Terminal Directos (Shell Fallback)

### En Windows (PowerShell / CMD):
```powershell
# Compilacion desatendida con MetaEditor nativo
& "C:\Program Files\MetaTrader 5\metaeditor64.exe" /compile:"C:\Program Files\MetaTrader 5\MQL5\Experts\MiEstrategia.mq5" /log:"C:\Program Files\MetaTrader 5\compile.log"

# Limpieza de procesos huerfanos del tester
taskkill /F /IM metatester64.exe

# Ejecucion de Terminal en modo Portable
& "C:\Program Files\MetaTrader 5\terminal64.exe" /portable
```

### En macOS (Zsh / Terminal):
```bash
# Compilacion desatendida con MetaEditor bajo Wine
WINEPREFIX="/Users/fmillar/Library/Application Support/net.metaquotes.wine.metatrader5" \
"/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine" \
cmd /c "cd /d C:\Program Files\MetaTrader 5 && metaeditor64.exe /compile:MQL5\Experts\MiEstrategia.mq5 /log:compile.log"

# Limpieza de procesos huerfanos del tester
pkill -f metatester64
```

---

## 6. Gotchas Criticos y Solucion de Problemas

### [GOTCHA 1] Error: Core 01 tester agent authorization error
* **Sintoma:** Al presionar "Empezar" en el Strategy Tester, la prueba se detiene inmediatamente indicando error de autorizacion del agente.
* **Causa:** Un proceso residual previo de `metatester64.exe` quedo abierto reteniendo el puerto `3000` con credenciales de sesion expiradas.
* **Solucion:**
  * En Windows: Ejecutar `taskkill /F /IM metatester64.exe`.
  * En macOS: Ejecutar `pkill -f metatester64` o `python3 MT5/scripts/mt5_agent_bridge.py clean-agents`.

### [GOTCHA 2] El Strategy Tester no lista un EA recien creado
* **Sintoma:** El archivo `.mq5` compilo sin errores, pero no figura en el menu desplegable de asesores del tester.
* **Causa:** La base de datos de catalogos de MT5 no realiza reescaneo automatico continuo en caliente.
* **Solucion:**
  1. Asegurarse de que el binario `.ex5` este copiado tanto en `MQL5/Experts/` como en `MQL5/Experts/Advisors/`.
  2. En la ventana Navegador de MT5, hacer clic derecho sobre la carpeta "Asesores Expertos" y seleccionar "Actualizar" (Refresh).

### [GOTCHA 3] Codificacion UTF-16 LE de Logs
* **Sintoma:** Al leer archivos `.log` de MT5 con herramientas de texto plano tradicionales, aparecen simbolos extranos o salidas vacias.
* **Causa:** MT5 escribe todos sus registros en formato binario UTF-16 Little Endian.
* **Solucion:** Siempre decodificar con `content.decode('utf-16', errors='replace')` en Python.

---

## 7. Reglas Obligatorias de Seguridad y Error Masking

Al escribir scripts o manejar excepciones en Python dentro de este repositorio:
1. **Error Masking Obligatorio:**  
   Nunca imprimir ni exponer `str(err)` ni stack traces completos. Utilizar obligatoriamente `type(err).__name__` acompanado del sufijo `(detalles omitidos por seguridad)`:
   ```python
   except Exception as err:
       logger.error(f"Error en {context}: {type(err).__name__} (detalles omitidos por seguridad)")
       return {"error": f"Error de operacion: {type(err).__name__}"}
   ```
2. **Proteccion de Credenciales:**  
   Nunca almacenar contraseñas de cuentas, llaves API o tokens en archivos sometidos a control de versiones.
