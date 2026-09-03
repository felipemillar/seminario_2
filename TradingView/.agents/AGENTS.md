# Reglas y Contexto de Proyecto: TradingView Quant Suite

> **Autor Canónico:** QRT Solutions  
> **Plataforma:** TradingView / Pine Script v6 / Python Cuantitativo  
> **Ámbito:** Standalone Quant Research & Development Ecosystem

---

## 1. Contexto del Ecosistema

Este proyecto es el repositorio central de **QRT Solutions** para el dominio de TradingView como plataforma de análisis cuantitativo, charting avanzado, ejecución algorítmica y base de conocimiento. Sus componentes son:

1. **Base de Conocimiento (`knowledge/`)**:
   - 31 manuales técnicos especializados en Markdown generados mediante Deep Research.
   - Indexados detalladamente en `knowledge/INDEX.md` y catalogados en `.agents/skills/tradingview-knowledge-navigator/references/knowledge_catalog.md`.
2. **Pine Script (`pine/`)**:
   - Todo el código debe escribirse obligatoriamente bajo el estándar **Pine Script v6** (`//@version=6`).
   - Indicadores en `pine/indicators/`, Estrategias en `pine/strategies/`, Librerías en `pine/libraries/`.
3. **Laboratorio Cuantitativo (`masterclass/`)**:
   - Notebooks de investigación con hipótesis causales, calibración empírica MAE/MFE, optimización 2D en meseta y partición In-Sample / Out-of-Sample.
4. **Biblioteca de Literatura de Trading (Obsidian / Markdown)**:
   - Ubicación: `/Users/fmillar/Proyectos_Desarrollo/Transcripcion_pdf_docx_to_MD/Libros_Markdown_Planos`
   - Colección de 53+ libros clásicos y avanzados en Markdown (Alexander Elder, Wyckoff, Al Brooks, Mark Minervini, CMT, Murphy, Schwager, etc.).

---

## 2. Protocolo de Interacción para Agentes de IA

Cuando un agente interactúe con este repositorio:

1. **Consultar antes de inventar:** Antes de proponer código o arquitecturas, utiliza la skill `tradingview-knowledge-navigator` para consultar los manuales en `knowledge/`.
2. **Estándar Pine Script v6:** Aplica estrictamente las directrices de `pinescript-v6-architect`:
   - Siempre usar `lookahead = barmerge.lookahead_off` en llamadas de marco superior.
   - En futuros CME (`NQ`, `ES`, `GC`), configurar margen al 5% (`margin_long = 5.0, margin_short = 5.0`).
   - No usar la función inexistente `ta.median()`, usar `ta.percentile_nearest_rank(source, length, 50)`.
   - Separar etiquetas de las velas con buffer dinámico basado en ATR (`vBuffer`).
3. **Autoría Obligatoria:** Todas las soluciones, scripts, comentarios y skills deben declarar explícitamente el autor como **"QRT Solutions"**.
4. **Distinción de Proyectos:**
   - **TradingView:** Ecosistema cloud independiente de charting, Pine Script, alertas y webhooks.
   - **GIF:** Análisis de datos masivos desde servidor SQL remoto (`185.56.138.170`).
