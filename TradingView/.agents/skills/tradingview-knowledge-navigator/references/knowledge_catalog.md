# Catálogo Detallado de la Base de Conocimiento (31 Manuales)
**Autor:** QRT Solutions  
**Ubicación de archivos:** `knowledge/`

---

## 1. Pine Script v6 y Desarrollo de Indicadores/Librerías
* **`Manual Técnico Pine Script v6.md`** (~60 KB): Tipado estricto v6, operadores, funciones built-in, tipos de usuario (`type`), eliminación de `when` en `strategy.exit`, manejo de arrays, matrices y maps.
* **`Manual Avanzado Pine Script V6.md`** (~54 KB): Técnicas avanzadas de optimización de ejecución, Garbage Collection, límites de memoria, manejo de polylines, tablas y cajas (`box`).
* **`Manual Técnico de Pine Script.md`** (~53 KB): Guía fundamental de dibujo técnico, inputs dinámicos, plots estilizados y manejo de estilos de barra.
* **`Manual Avanzado de Pine Script.md`** (~80 KB): Catálogo completo de la librería `ta.*`, osciladores, cálculos estadísticos, divergencias algorítmicas y filtros digitales.
* **`Librerías Pine Script v6.md`** (~35 KB): Creación, exportación, publicación y versionamiento semántico de librerías (`library`) en Pine Script v6.

---

## 2. Estrategias, Backtesting y Validación
* **`Guía Backtesting Pine Script.md`** (~64 KB): Motor `strategy()`, cálculo de órdenes, `process_orders_on_close`, emulación de broker, comisiones, slippage, fill assumptions y diagnóstico de trades.
* **`Metodología de Validación en Trading.md`** (~65 KB): Marco de validación institucional, partición In-Sample vs Out-of-Sample, Walk-Forward Analysis, optimización Bayesiana con Optuna, detección de mesetas (*Plateau Detection*) y prevención de sobreajuste (*Curve Fitting*).
* **`Patrones Trading Pine Script v6.md`** (~42 KB): Catálogo de patrones de trading cuantitativos codificados en Pine Script v6 (Reversión a la Media, Seguimiento de Tendencia, Rupturas de Volatilidad, Squeezes).
* **`Riesgo y Sizing Pine Script.md`** (~73 KB): Modelos de dimensionamiento de posición (Fixed Risk, % de Equity, Kelly Criterion, Volatility Sizing), control de drawdown y reglas de stop loss/take profit.

---

## 3. Datos, Multi-Timeframe y Order Flow
* **`Informe de Datos de TradingView.md`** (~79 KB): Arquitectura de feeds de datos, resolución intrabarra, manejo seguro de `request.security()`, lookahead prevention (`barmerge.lookahead_off`) y símbolos sintéticos.
* **`Análisis Multi-Activo TradingView.md`** (~45 KB): Análisis intermercado, correlaciones dinámicas, ratios de fuerza relativa (RS), screeners y matrices multi-activo.
* **`Desarrollo Order Flow Pine Script.md`** (~33 KB): Algoritmos de flujo de órdenes, Footprint charts, Delta de volumen acumulado (CVD), Volume Profile y desbalances de liquidez en Pine Script.

---

## 4. Alertas, Webhooks, Automatización y Python
* **`Guía Alertas Webhooks TradingView.md`** (~90 KB): Sistema de alertas, payloads JSON dinámicos con placeholders (`{{strategy.order.action}}`, `{{close}}`), seguridad y headers HTTP.
* **`Automatización de Trading TradingView.md`** (~80 KB): Pipeline de ejecución hacia brokers (Interactive Brokers, Tradovate, Binance, MetaTrader) mediante webhooks y puentes de automatización.
* **`Middleware de Reconciliación Algorítmica.md`** (~43 KB): Sistemas de sincronización de estado y reconciliación de órdenes entre TradingView y el broker externo (manejo de desconexiones y reintentos).
* **`Integración TradingView y Python.md`** (~90 KB): Conexión bidireccional Python ↔ TradingView, `tvDatafeed`, servidores Flask/FastAPI para recepción de webhooks y procesamiento de datos.
* **`Arbitraje Multi Pierna TradingView Python.md`** (~41 KB): Modelos de arbitraje estadístico, pairs trading, cointegración (Engle-Granger, Johansen) y ejecución de spreads.
* **`Análisis WebSocket de TradingView.md`** (~30 KB): Ingeniería inversa del protocolo WSS (`wss://data.tradingview.com/socket.io/websocket`), extracción de datos tick en tiempo real y decodificación de mensajes JSON-RPC.

---

## 5. Infraestructura Cloud y Desarrollo con IA
* **`Arquitectura Interna de TradingView.md`** (~76 KB): Infraestructura distribuida, clústeres de renderizado gráfico, balanceo de carga y aislamiento de computación Pine Script.
* **`Infraestructura Producción Cloud.md`** (~66 KB): Despliegue de bots de trading en AWS/GCP, Docker, alta disponibilidad, monitoreo y alertas de fallos.
* **`APIs Gráficas de TradingView.md`** (~78 KB): Integración de *TradingView Charting Library* y *Lightweight Charts* en aplicaciones web propietarias.
* **`Guía de Interfaz TradingView.md`** (~68 KB): Dominio de todas las funciones nativas, atajos de teclado, capas de dibujo y herramientas analíticas del frontend.
* **`Ecosistema Comercial de TradingView.md`** (~60 KB): Monetización de scripts con acceso exclusivo por invitación (*Invite-only*), licencias y protección de propiedad intelectual.
* **`Desarrollo Pine Script con IA.md`** (~64 KB): Protocolos para programar, auditar y optimizar código Pine Script v6 utilizando modelos LLM y agentes autónomos.
