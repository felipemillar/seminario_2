# Índice de Base de Conocimiento — TradingView

> **Proyecto**: Dominio completo de TradingView como plataforma de análisis financiero y trading algorítmico
> **Método**: Documentos generados con Gemini Deep Research, organizados en generaciones de 10 documentos
> **Última actualización**: 2026-07-11

---

## Generación 1 — Fundamentos y Core (10 documentos)

| # | Prompt | Documento | Tamaño | Temas Clave |
|---|--------|-----------|--------|-------------|
| 01 | Arquitectura Interna de TradingView | [Arquitectura Interna de TradingView.docx](Arquitectura%20Interna%20de%20TradingView.docx) | ~3.0 MB | Arquitectura cloud, motor de renderizado, pipeline de datos, planes, ejecución Pine Script |
| 02 | Pine Script v6 — Referencia Completa | [Manual Técnico Pine Script v6.docx](Manual%20Técnico%20Pine%20Script%20v6.docx) | ~3.0 MB | Tipos de datos, operadores, funciones built-in, tipos definidos por usuario |
| 03 | Pine Script — Indicadores Personalizados | [Manual Técnico de Pine Script.docx](Manual%20Técnico%20de%20Pine%20Script.docx) | ~4.0 MB | Indicadores custom, plots, inputs, multi-timeframe, visual design |
| 04 | Pine Script — Estrategias y Backtesting | [Guía Backtesting Pine Script.docx](Guía%20Backtesting%20Pine%20Script.docx) | ~3.2 MB | strategy.*, órdenes, backtesting, métricas, optimización |
| 05 | Data Engineering — Feeds y Resoluciones | [Informe de Datos de TradingView.docx](Informe%20de%20Datos%20de%20TradingView.docx) | ~3.2 MB | Feeds de datos, resoluciones, request.security(), exchanges, símbolos |
| 06 | Análisis Técnico Built-in — `ta.*` | [Manual Avanzado de Pine Script.docx](Manual%20Avanzado%20de%20Pine%20Script.docx) | ~3.2 MB | Funciones ta.*, indicadores integrados, patrones, divergencias |
| 07 | Sistema de Alertas y Webhooks | [Guía Alertas Webhooks TradingView.docx](Guía%20Alertas%20Webhooks%20TradingView.docx) | ~220 KB | alert(), alertcondition(), webhooks, JSON payloads, automatización |
| 08 | Pipeline de Ejecución → Broker | [Automatización de Trading TradingView.docx](Automatización%20de%20Trading%20TradingView.docx) | ~3.3 MB | Brokers integrados, paper trading, ejecución real, APIs externas |
| 09 | Integración TradingView ↔ Python | [Integración TradingView y Python.docx](Integración%20TradingView%20y%20Python.docx) | ~143 KB | Python, APIs externas, tvdatafeed, selenium, webhooks→Python |
| 10 | Gestión de Riesgo y Position Sizing | [Riesgo y Sizing Pine Script.docx](Riesgo%20y%20Sizing%20Pine%20Script.docx) | ~3.3 MB | Position sizing, drawdown, risk/reward, Kelly, money management |

**Total Gen 1**: ~29.5 MB en 10 documentos

---

## Generación 2 — Avanzado y Ecosistema (prompts listos [OK])

> Prompts diseñados tras análisis de gaps de Gen 1. Cada prompt incluye cláusulas anti-duplicación.
> Ver: [prompts_gen2_tradingview.md](prompts_gen2_tradingview.md)

| # | Prompt | Línea | Prioridad | Estado |
|---|--------|-------|-----------|--------|
| 11 | Ecosistema y Modelo de Negocio | L02 | [INACTIVO] Alta | Pendiente ejecución |
| 12 | UI y Funcionalidades Nativas | L03 | [INACTIVO] Alta | Pendiente ejecución |
| 13 | Pine Avanzado (Arrays, Matrices, Maps, Patrones) | L07 | [PENDIENTE] Media | Pendiente ejecución |
| 14 | Visualización Avanzada (Tables, Polylines, Dashboards) | L08 | [PENDIENTE] Media | Pendiente ejecución |
| 15 | Screeners, Heatmaps y Multi-Activo | L11 | [INACTIVO] Alta | Pendiente ejecución |
| 16 | Charting Library Empresarial + Lightweight Charts | L13 | [INACTIVO] Alta | Pendiente ejecución |
| 17 | Metodología Avanzada de Backtesting | L17 | [ACTIVO] Normal | Pendiente ejecución |
| 18 | Patrones de Estrategias Algorítmicas | L18 | [ACTIVO] Normal | Pendiente ejecución |
| 19 | Infraestructura de Producción Cloud | L19 | [ACTIVO] Normal | Pendiente ejecución |
| 20 | IA y Agentes para Desarrollo Pine Script | L20 | [ACTIVO] Normal | Pendiente ejecución |

---

## Generación 3 — Ingeniería Hardcore y Sinergia (prompts listos [OK])

> Prompts diseñados tras el análisis de gaps de las Gen 1 y Gen 2. Cubren optimización extrema y hacking de datos.
> Ver: [prompts_gen3_tradingview.md](prompts_gen3_tradingview.md)

| # | Prompt | Línea | Prioridad | Estado |
|---|--------|-------|-----------|--------|
| 21 | Librerías, Versionamiento y Arquitectura | L21 | [PENDIENTE] Media | [OK] Listo |
| 22 | Profiling, Garbage Collection y Memoria | L22 | [INACTIVO] Alta | Pendiente ejecución |
| 23 | Algoritmos de Order Flow y Footprint | L23 | [INACTIVO] Alta | [OK] Listo |
| 24 | Ingeniería Inversa del Protocolo WSS | L24 | [INACTIVO] Alta | [OK] Listo |
| 25 | Data Engineering Alternativo (Pine Seed) | L25 | [PENDIENTE] Media | Pendiente ejecución |
| 26 | Middleware de Reconciliación (TV ↔ Broker Externo) | L26 | [INACTIVO] Alta | [OK] Listo |
| 27 | Arbitraje Estadístico y Pairs Trading | L27 | [INACTIVO] Alta | [OK] Listo |

---

## Documentos de Trabajo

| Documento | Descripción |
|-----------|-------------|
| [lineas_investigacion_tradingview.md](lineas_investigacion_tradingview.md) | Las líneas de investigación diseñadas para dominio total de TradingView |
| [prompts_gen1_tradingview.md](prompts_gen1_tradingview.md) | Los 10 prompts de Deep Research (Gen 1) listos para usar |
| [prompts_gen2_tradingview.md](prompts_gen2_tradingview.md) | Los 10 prompts de Deep Research (Gen 2) con anti-duplicación |
| [prompts_gen3_tradingview.md](prompts_gen3_tradingview.md) | Los 7 prompts de Deep Research (Gen 3) para hacking de plataforma y sinergia |

---

## Notas

- Los archivos `.docx` son los documentos crudos tal como los genera Gemini Deep Research
- El mapeo Prompt→Documento se hizo por título/contenido; verificar si algún nombre no coincide exactamente
- Gen 2 incluye cláusulas "NO cubrir" para evitar solapamiento con Gen 1
- Los prompts de prioridad [INACTIVO] cubren temas **avanzados y únicos de la plataforma**
