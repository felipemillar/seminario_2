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
