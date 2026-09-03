# MetaTrader 5 (MT5) & MQL5 Algorithmic Trading Knowledge Base

> **Base de Conocimiento Universal de Trading Algorítmico, MQL5, Python API e Infraestructura MT5.**
> Optimizada para consulta humana y consumo autónomo por Agentes de Inteligencia Artificial.

---

## Formatos de Acceso para Agentes de IA

Este repositorio implementa los estándares abiertos para consumo por Modelos de Lenguaje (LLMs) y agentes autónomos:

- **[`llms.txt`](llms.txt)**: Manifiesto curado con resumen y enlaces a todos los módulos (estándar `llms.txt`).
- **[`llms-full.txt`](llms-full.txt)**: Base de conocimiento completa consolidada en un único archivo plano (~1.7 MB).
- **[`AGENTS.md`](AGENTS.md)**: Reglas operativas, distinciones de entorno y arquitectura del sistema para agentes.
- **[`.cursorrules`](.cursorrules)** y **[`CLAUDE.md`](CLAUDE.md)**: Contexto optimizado para Cursor IDE y Claude Code.

---

## Catálogo de Documentación Técnica (`knowledge/`)

El directorio [`knowledge/`](knowledge/) contiene **20 tratados técnicos de grado de producción** (~1.83 MB) con código fuente funcional, benchmarks de latencia y diseño arquitectónico.

### 1. Arquitectura & Fundamentos de Plataforma
- [**Informe Técnico Arquitectura MetaTrader 5**](knowledge/Informe%20T%C3%A9cnico%20Arquitectura%20MetaTrader%205.md): Clúster de 5 servidores, bucle de eventos, coalescencia de ticks, hilos por símbolo, formato de almacenamiento (`.hcc`/`.tkc`) y modo portable.
- [**Informe Técnico MT5 y MQL5**](knowledge/Informe%20T%C3%A9cnico%20MT5%20y%20MQL5.md): Arquitectura cliente-servidor, sincronización de históricos, modelo event-driven y gestión de colas.

### 2. Lenguaje MQL5 & Desarrollo Profesional de EAs
- [**Informe Técnico MQL5 para Desarrolladores**](knowledge/Informe%20T%C3%A9cnico%20MQL5%20para%20Desarrolladores.md): Tipos de datos, OOP, punteros, `ArrayResize`, matrices nativas y **guía exhaustiva de gotchas vs C++**.
- [**MQL5: Capacidades Avanzadas y Extensión**](knowledge/MQL5_%20Capacidades%20Avanzadas%20y%20Extensi%C3%B3n.md): Aceleración GPU con OpenCL, marshaling de DLLs, base de datos SQLite integrada, Services en background y símbolos sintéticos.
- [**Desarrollo Profesional de Expert Advisors en MQL5**](knowledge/Desarrollo%20Profesional%20de%20Expert%20Advisors%20en%20MQL5.md): Ciclo de vida (OnInit a OnDeinit), State Machine resiliente de 5 estados, persistencia, manejo de splits y logging estructurado en JSON.
- [**Desarrollo Profesional de EAs con IA**](knowledge/Desarrollo%20Profesional%20de%20EAs%20con%20IA.md): Arquitectura modular, detección de nueva barra, telemetría con heartbeat y workflows de desarrollo asistido por IA.

### 3. Indicadores, Flujos de Datos & Gráficos
- [**Informe Técnico: Indicadores y Gráficos MT5**](knowledge/Informe%20T%C3%A9cnico_%20Indicadores%20y%20Gr%C3%A1ficos%20MT5.md): `OnCalculate()` incremental, catálogo de 18 estilos de dibujo, caché de handles, objetos gráficos y paneles interactivos con `CAppDialog`.
- [**Creación Indicadores MQL5 Avanzados y ML**](knowledge/Creación%20Indicadores%20MQL5%20Avanzados%20y%20ML.md): Implementaciones completas de VWAP intradiario, Heikin Ashi Smoothed, Volume Profile y motor de Feature Engineering para Machine Learning.
- [**MT5: Flujos de Datos en Tiempo Real**](knowledge/MT5_%20Flujos%20de%20Datos%20en%20Tiempo%20Real.md): Microestructura de mercado, streaming de ticks y DOM (Level 2), IPC por Named Pipes vs ZeroMQ y benchmarks de latencia.

### 4. Motor de Trading, Ejecución & Gestión de Riesgo
- [**MT5: Órdenes, Trades y Posiciones**](knowledge/MT5_%20%C3%93rdenes,%20Trades%20y%20Posiciones.md): Modelo Order-Deal-Position, modos de ejecución, políticas de llenado (FOK, IOC, Return), `MqlTradeRequest` y tracker de transacciones.
- [**Gestión de Órdenes y Riesgo MT5**](knowledge/Gesti%C3%B3n%20de%20%C3%93rdenes%20y%20Riesgo%20MT5.md): Dimensionamiento de posición (Criterio Kelly, Risk Parity), circuit breakers, trailing stops ATR y tratamiento de retcodes.

### 5. Backtesting, Optimización & Validación Estadística
- [**Strategy Tester MT5: Guía Exhaustiva**](knowledge/Strategy%20Tester%20MT5_%20Gu%C3%ADa%20Exhaustiva.md): Modos de modelado (Every Tick, Real Ticks), optimización genética, Frames API (`OnTesterPass`), criterios custom y ejecución CLI automatizada.
- [**Backtesting Estrategias Trading: MT5 y Python**](knowledge/Backtesting%20Estrategias%20Trading_%20MT5%20y%20Python.md): Mitigación de sesgos (Deflated Sharpe Ratio, Overfitting), Walk-Forward Analysis (WFA), simulaciones Monte Carlo y pipeline de validación Go/No-Go.

### 6. Python API & Data Engineering Cuantitativo
- [**Informe Técnico MetaTrader5 Python API**](knowledge/Informe%20T%C3%A9cnico%20MetaTrader5%20Python%20API.md): Extracción vectorizada de OHLCV y ticks, manejo de sesiones, DOM en Python, benchmarks y arquitectura de Pasarela VPS.
- [**Informe Técnico Python para MetaTrader 5**](knowledge/Informe%20T%C3%A9cnico%20Python%20para%20MetaTrader%205.md): Conexión multiterminal, wrappers asíncronos con auto-reconexión y pipelines de datos en `pandas`.
- [**Data Engineering para Trading Algorítmico MT5**](knowledge/Data%20Engineering%20para%20Trading%20Algor%C3%ADtmico%20MT5.md): Extracción masiva paginada, Triple Barrier Method, dollar bars, VPIN, almacenamiento en Parquet/TimescaleDB y pipelines ETL.

### 7. Integración, Infraestructura & macOS
- [**MT5 macOS Trading Algorítmico: Guía Técnica**](knowledge/MT5%20macOS%20Trading%20Algor%C3%ADtmico_%20Gu%C3%ADa%20T%C3%A9cnica.md): Operativa en Apple Silicon (M1-M4), virtualización Parallels, VPS Windows, latencia por broker, watchdog PowerShell y telemetría por Telegram.
- [**Integración de MetaTrader 5 con Sistemas Externos**](knowledge/Integración%20de%20MetaTrader%205%20con%20Sistemas%20Externos.md): WebRequest HTTP/REST, sockets TCP/TLS, ZeroMQ REQ/REP/PUB/SUB, memoria compartida y EA como servidor REST.
- [**Informe Técnico: MT5, Python y Cloud**](knowledge/Informe%20T%C3%A9cnico_%20MT5,%20Python%20y%20Cloud.md): Arquitecturas cloud simple, híbrida y enterprise con TimescaleDB, Grafana y planes de disaster recovery.

### 8. Inteligencia Artificial & Gobernanza
- [**IA para Trading Algorítmico MT5**](knowledge/IA%20para%20Trading%20Algor%C3%ADtmico%20MT5.md): Flujos de trabajo de 7 fases con LLMs, ingeniería de prompts financieros, checklists de auditoría y gestión de riesgos éticos.
- [**Índice Maestro y Matriz de Tags**](knowledge/INDEX.md): Catálogo exhaustivo con resumen de cada documento y mapa de referencias cruzadas.

---

## Herramientas y Código Incluido

### 1. Gateway REST FastAPI (`src/gateway/`)
Permite conectar entornos macOS/Linux con la terminal MT5 corriendo en Windows mediante una API REST protegida:
```bash
# Iniciar servidor Gateway en Windows o VM
uvicorn src.gateway.server:app --host 0.0.0.0 --port 8000
```
- **Endpoints disponibles**: `/initialize`, `/symbols`, `/rates`, `/ticks`, `/order`, `/positions`, `/orders`, `/switch_account`, `/health`.

### 2. Scripts de Análisis de Mercado (`scripts/`)
- `fetch_atr_scan.py` / `fetch_atr_history.py`: Escaneo y serie temporal de volatilidad ATR relativa.
- `fetch_swap_scan.py` / `analyze_swap_arbitrage.py`: Cálculo y detección de arbitraje de tasas swap entre brokers.
- `analyze_carry_trade.py`: Búsqueda de combinaciones con rendimiento neto positivo por financiamiento.
- `build_dashboard_data.py`: Compilador JSON para el panel visual HTML [`dashboard/index.html`](dashboard/index.html).

---

## [SIGNAL] Configuración Rápida

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/mt5-knowledge-base.git
   cd mt5-knowledge-base
   ```
2. Configurar entorno virtual de Python:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   pip install -r requirements.txt  # FastAPI, pandas, uvicorn, MetaTrader5
   ```
3. Copiar archivo de entorno:
   ```bash
   cp .env.example .env
   ```
