# AGENTS.md — Reglas y Contexto para Agentes de IA

> Este documento es la **fuente autoritativa de contexto** para agentes de IA (Antigravity, Cursor, Windsurf, Claude Code, GitHub Copilot, ChatGPT, etc.) que operen en este repositorio.

---

## 1. Visión General del Repositorio

Este repositorio es un ecosistema integral de **Trading Algorítmico y MetaTrader 5 (MT5)** con 3 componentes principales:

1. **Base de Conocimiento Técnica (`knowledge/` & `llms.txt` / `llms-full.txt`)**:
   - 20 tratados exhaustivos (~1.83 MB) que cubren arquitectura interna de MT5, programación MQL5 moderna, API de Python, flujos en tiempo real, backtesting riguroso, EAs con IA, gestión de riesgo y despliegue en la nube/macOS.
   - Índice maestro en [`knowledge/INDEX.md`](knowledge/INDEX.md).

2. **Pasarela API REST Local (`src/gateway/`)**:
   - Servidor FastAPI (`server.py`) que se ejecuta en Windows (o VM Parallels) para exponer las capacidades de la DLL de MT5 vía HTTP a clientes macOS/Linux.

3. **Scripts de Análisis Cuantitativo (`scripts/`)**:
   - Herramientas para escaneo de volatilidad ATR, arbitraje de tasas swap entre brokers (Pepperstone, Capitaria, Grupo Inteligencia), carry trade y extracción de metadatos de símbolos.

4. **Conexión Universal para Agentes de IA (`AGENT_CONNECTION_GUIDE.md`, `mcp_server/` y `scripts/mt5_agent_bridge.py`)**:
   - Arquitectura integral para que cualquier agente (Antigravity, Claude Code, Cursor, OpenAI) interactúe con MT5 sobre macOS (Wine).
   - **Guía Maestra:** [`AGENT_CONNECTION_GUIDE.md`](AGENT_CONNECTION_GUIDE.md).
   - **Servidor MCP:** [`mcp_server/server.py`](mcp_server/server.py) (herramientas nativas stdio: `mt5_status`, `mt5_compile`, `mt5_deploy_expert`, `mt5_last_backtest_metrics`, `mt5_clean_agents`).
   - **CLI Bridge:** `python3 scripts/mt5_agent_bridge.py` (`status`, `compile`, `deploy`, `last-test`, `clean-agents`).

---

## [ADVERTENCIA] 2. Regla Fundamental: Distinción MT5 vs GIF (Grupo Inteligencia)

Cuando el usuario mencione *"el servidor"* o *"Grupo Inteligencia"*, debes distinguir claramente:

1. **Proyecto GIF (Grupo Inteligencia / Business Intelligence)**:
   - **Propósito**: Análisis masivo de datos históricos, reportes contables, riesgo y dashboards estáticos.
   - **Servidor al que se refiere**: Servidor SQL Server remoto (`185.56.138.170`, DB: `MT5`) consultado vía `pymssql`.
2. **Proyecto MT5 (Gateway Local / Trading Operativo)**:
   - **Propósito**: API REST FastAPI local para controlar el terminal MetaTrader 5.
   - **Servidor al que se refiere**: Máquina virtual local Parallels (`10.211.55.4:8000`).
   - **Nota**: En este proyecto `"grupointeligencia"` es solo un alias de cuenta/broker en `SwitchAccountRequest`.

---

## 3. Reglas de Codificación y Seguridad

### 3.1. Error Masking en Python
Al escribir bloques `except` en Python:
- **SIEMPRE** usar `type(err).__name__` en lugar de `str(err)` para prevenir filtración involuntaria de información sensible o rutas internas.
- Incluir sufijo descriptivo `(detalles omitidos por seguridad)` en logs de error.
- **Patrón estándar**:
  ```python
  except Exception as err:
      logger.error(f"Error en {context}: {type(err).__name__} (detalles omitidos por seguridad)")
      return {"error": f"Error de operación: {type(err).__name__}"}
  ```

### 3.2. Manejo Seguro de Credenciales
- **NUNCA** hardcodear contraseñas de cuentas MT5 en archivos versionados.
- Utilizar variables de entorno (`.env`) o el archivo local no versionado `~/.mt5_accounts.json` generado por [`scripts/setup_accounts.py`](scripts/setup_accounts.py).

---

## 4. Mapa de Navegación de Conocimiento (`knowledge/`)

Cuando un usuario pregunte sobre un aspecto técnico de MT5, MQL5 o Trading Cuantitativo, consulta el documento específico correspondiente:

| Área Técnica | Documento Recomendado | Temas Clave |
| :--- | :--- | :--- |
| **Arquitectura Interna** | [`knowledge/Informe Técnico Arquitectura MetaTrader 5.md`](knowledge/Informe%20T%C3%A9cnico%20Arquitectura%20MetaTrader%205.md) | Clúster servidores, event loop, coalescencia, threads por símbolo, portable mode. |
| **Lenguaje MQL5** | [`knowledge/Informe Técnico MQL5 para Desarrolladores.md`](knowledge/Informe%20T%C3%A9cnico%20MQL5%20para%20Desarrolladores.md) | Tipos, OOP, punteros, ArrayResize, matrices/vectores nativos, gotchas vs C++. |
| **MQL5 Avanzado** | [`knowledge/MQL5: Capacidades Avanzadas y Extensión.md`](knowledge/MQL5_%20Capacidades%20Avanzadas%20y%20Extensi%C3%B3n.md) | OpenCL (GPU), DLL marshaling, WebRequest REST, SQLite embebido, Services. |
| **Expert Advisors (EAs)** | [`knowledge/Desarrollo Profesional de Expert Advisors en MQL5.md`](knowledge/Desarrollo%20Profesional%20de%20Expert%20Advisors%20en%20MQL5.md) | Ciclo de vida (OnInit a OnDeinit), State Machine, persistencia, OnTradeTransaction, JSON logs. |
| **Indicadores y Gráficos** | [`knowledge/Informe Técnico: Indicadores y Gráficos MT5.md`](knowledge/Informe%20T%C3%A9cnico_%20Indicadores%20y%20Gr%C3%A1ficos%20MT5.md) | OnCalculate incremental, 18 estilos de dibujo, paneles interactivos CAppDialog, objetos gráficos. |
| **Órdenes y Ejecución** | [`knowledge/MT5: Órdenes, Trades y Posiciones.md`](knowledge/MT5_%20%C3%93rdenes,%20Trades%20y%20Posiciones.md) | Modelo Order→Deal→Position, fill policies (FOK/IOC), MqlTradeRequest, Hedging vs Netting. |
| **Gestión de Riesgo** | [`knowledge/Gestión de Órdenes y Riesgo MT5.md`](knowledge/Gesti%C3%B3n%20de%20%C3%93rdenes%20y%20Riesgo%20MT5.md) | Position sizing (Kelly/Risk Parity), circuit breakers, trailing ATR, control de retcodes. |
| **Strategy Tester & Backtest** | [`knowledge/Strategy Tester MT5: Guía Exhaustiva.md`](knowledge/Strategy%20Tester%20MT5_%20Gu%C3%ADa%20Exhaustiva.md) | Every Tick / Real Ticks, optimización genética, Frames API, OnTester custom, CLI. |
| **Backtest Estadístico** | [`knowledge/Backtesting Estrategias Trading: MT5 y Python.md`](knowledge/Backtesting%20Estrategias%20Trading_%20MT5%20y%20Python.md) | Deflated Sharpe Ratio (DSR), Walk-Forward Analysis (WFA), simulaciones Monte Carlo, sesgos. |
| **API Python MT5** | [`knowledge/Informe Técnico MetaTrader5 Python API.md`](knowledge/Informe%20T%C3%A9cnico%20MetaTrader5%20Python%20API.md) | `initialize()`, `copy_rates_range()`, `copy_ticks_range()`, `order_send()`, pasarela VPS. |
| **Data Engineering & ML** | [`knowledge/Data Engineering para Trading Algorítmico MT5.md`](knowledge/Data%20Engineering%20para%20Trading%20Algor%C3%ADtmico%20MT5.md) | Triple Barrier Method, dollar bars, VPIN, Parquet, TimescaleDB, pipelines ETL. |
| **Tiempo Real y Latencia** | [`knowledge/MT5: Flujos de Datos en Tiempo Real.md`](knowledge/MT5_%20Flujos%20de%20Datos%20en%20Tiempo%20Real.md) | Streaming ticks/DOM, Named Pipes duplex, ring buffers, latencias por hardware. |
| **Integración de Sistemas** | [`knowledge/Integración de MetaTrader 5 con Sistemas Externos.md`](knowledge/Integración%20de%20MetaTrader%205%20con%20Sistemas%20Externos.md) | WebRequest HTTP, Sockets TCP/TLS, ZeroMQ REQ/REP/PUB/SUB, EA como servidor REST. |
| **macOS & Infraestructura** | [`knowledge/MT5 macOS Trading Algorítmico: Guía Técnica.md`](knowledge/MT5%20macOS%20Trading%20Algor%C3%ADtmico_%20Gu%C3%ADa%20T%C3%A9cnica.md) | Apple Silicon (M1-M4), Parallels, VPS Windows, latencia brokers, watchdog PowerShell, Telegram. |
| **Cloud & Resiliencia** | [`knowledge/Informe Técnico: MT5, Python y Cloud.md`](knowledge/Informe%20T%C3%A9cnico_%20MT5,%20Python%20y%20Cloud.md) | Arquitectura monolítica vs enterprise, TimescaleDB, Grafana, alertas Telegram, failover. |
| **Datos Externos & Custom Symbols** | [`CUSTOM_DATA_IMPORT_GUIDE.md`](CUSTOM_DATA_IMPORT_GUIDE.md) | Protocolo 100% autónomo para convertir e inyectar datasets intradiarios (M1/M5) en MT5. |

---

## 5. Comandos y Workflows Frecuentes

- **Iniciar Gateway FastAPI**:
  ```bash
  uvicorn src.gateway.server:app --host 0.0.0.0 --port 8000 --reload
  ```
- **Ejecutar Escaneo de ATR / Volatilidad**:
  ```bash
  python scripts/fetch_atr_scan.py
  ```
- **Ejecutar Análisis de Carry Trade y Swaps**:
  ```bash
  python scripts/fetch_swap_scan.py
  python scripts/analyze_swap_arbitrage.py
  ```
- **Compilar Datos para Dashboard Web**:
  ```bash
  python scripts/build_dashboard_data.py
  ```
