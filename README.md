# Ecosistema Cuantitativo & Orquestación Multi-Agente (seminario_2)

> **Autor Institucional:** QRT Solutions  
> **Ámbito:** Investigación Cuantitativa, Modelado Matemático y Generación Algorítmica con Paridad Multiplataforma (TradingView & MetaTrader 5)  
> **Estado:** Entorno Activo de Investigación y Desarrollo

---

## 1. Visión y Arquitectura Global

El proyecto **`seminario_2`** es un entorno integrado de investigación cuantitativa y desarrollo algorítmico diseñado para transformar conceptos, anomalías estadísticas y literatura financiera en sistemas de trading formalizados y ejecutables con paridad matemática absoluta entre **TradingView (Pine Script v6)** y **MetaTrader 5 (MQL5 POO)**.

El ecosistema se articula en cuatro pilares complementarios:

```mermaid
flowchart TD
    classDef kb fill:#eff6ff,stroke:#2563eb,stroke-width:2px,color:#1e3a8a;
    classDef swarm fill:#09090b,stroke:#09090b,stroke-width:2px,color:#ffffff;
    classDef tv fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef mt5 fill:#fefce8,stroke:#ca8a04,stroke-width:2px,color:#713f12;
    classDef log fill:#fdf4ff,stroke:#9333ea,stroke-width:2px,color:#581c87;

    KB["Libros_Validados\n(51+ Tratados Canónicos en Markdown\n+ LLM_INDEX.md)"]:::kb
    Swarm["quant_agentic_swarm\n(Lead Strategist + RAG 1 + StrategySpecification\n+ STRATEGY_REGISTRY.json)"]:::swarm
    TV["TradingView\n(Pine Script v6 + 31 Manuales Técnicos\n+ Masterclasses y Backtest)"]:::tv
    MT5["MT5\n(MQL5 POO + CTrade + FastAPI Gateway\n+ 20 Manuales Técnicos)"]:::mt5
    Bitacora["BITACORA.md\n(Gestión y Trazabilidad de Sesiones)"]:::log

    KB -->|RAG 1: Fórmulas de Autor & Tesis| Swarm
    Swarm -->|StrategySpecification.json\n(UUID + Triple Barrera + Z-Score)| TV
    Swarm -->|StrategySpecification.json\n(UUID + Triple Barrera + Z-Score)| MT5
    TV & MT5 -->|Feedback de Calidad & Paridad| Swarm
    Swarm -->|Registro de Hitos| Bitacora
```

### 1.1. Módulos del Repositorio

1. **[Libros_Validados/](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/Libros_Validados)**:
   - Colección curada de 51+ libros canónicos de trading, análisis técnico cuantitativo, microestructura, price action y psicología de mercado transcriptos a Markdown plano.
   - Cuenta con [`LLM_INDEX.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/Libros_Validados/LLM_INDEX.md) con enrutamiento semántico temático y optimización de tokens para modelos de lenguaje.

2. **[quant_agentic_swarm/](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm)**:
   - Orquestador multi-agente jerárquico (**Quant Agentic Swarm - QAS**).
   - Gestiona el pipeline de 4 fases, la memoria persistente en [`STRATEGY_REGISTRY.json`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/STRATEGY_REGISTRY.json), contratos JSON formales (`StrategySpecification`) y visualización interactiva en [`viewer.html`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/viewer.html).

3. **[TradingView/](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/TradingView)**:
   - Entorno especializado en Pine Script v6 (`//@version=6`) bajo la autoría institucional de **QRT Solutions**.
   - Incluye 31 manuales técnicos exhaustivos en `knowledge/`, notebooks de optimización en `masterclass/` y módulos reutilizables en `pine/`.

4. **[MT5/](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5)**:
   - Entorno especializado en MetaTrader 5 y programación MQL5 POO con la librería estándar `Trade\Trade.mqh`.
   - Incorpora una pasarela REST FastAPI local (`src/gateway/`), herramientas de escaneo de volatilidad ATR y arbitraje de swaps (`scripts/`) y 20 monografías de arquitectura en `knowledge/`.

---

## 2. Protocolo de Ejecución Secuencial Obligatorio (4 Fases)

Cualquier agente de IA o desarrollador que opere en este repositorio debe seguir estrictamente el protocolo de 4 fases definido por el enjambre:

```
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 1: CO-CREACIÓN DE HIPÓTESIS (HITL GATEKEEPER)                     │
│ Idea Natural → 3 Fichas Técnicas (Variantes A, B, C) → Aprobación Trader│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 2: MODELADO MATEMÁTICO & CONTRATO STRATEGYSPECIFICATION           │
│ Consulta RAG 1 (Libros) + Z-Score MTF + Triple Barrera + JSON Schema   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 3: ENJAMBRE DESARROLLADOR ESPECIALISTA (7 BLOQUES)                │
│ Código Pine Script v6 + Código MQL5 POO + Auditoría de Paridad Cruzada │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 4: ENTREGABLES, TELEMETRÍA, FACTSHEET & BITÁCORA                  │
│ .pine + .mq5 + FACTSHEET.md + STRATEGY_REGISTRY.json + BITACORA.md    │
└────────────────────────────────────────────────────────────────────────┘
```

### Fase 1: Co-Creación de Hipótesis (HITL Gatekeeper)
- **Regla de Oro:** NUNCA saltar directamente a generar código ante una idea informal.
- Descomponer la idea del trader en **3 Fichas Técnicas Estructuradas** (Variante A: Momentum, Variante B: Retesteo/Pullback, Variante C: Compresión/Volatilidad).
- Cada ficha sigue la fórmula canónica:
  $$\text{Condición } (X) \implies \text{Expectativa } (Y) \implies \text{Causa Estructural } (Z) \implies \text{Invalidación} \implies \text{Régimen Óptimo}$$
- El trader debe seleccionar, combinar o ajustar explícitamente una variante antes de continuar.

### Fase 2: Modelado Matemático & Contrato `StrategySpecification`
- Contrastar la tesis aprobada contra la literatura financiera en [`Libros_Validados`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/Libros_Validados) (López de Prado, Kaufman, Chan, Crabel, etc.).
- Asignar un **Strategy UUID** único: `STRAT-YYYYMMDD-[NOMBRE]-[TF]-vX.X`.
- Incorporar el filtro MTF de régimen de mercado mediante el **Z-Score Diario de Volatilidad**:
  $$Z_{\text{vol}} = \frac{\text{Diff}_D - \text{SMA}(\text{Diff}_D, 20)}{\text{StDev}(\text{Diff}_D, 20)} \quad \text{donde } \text{Diff}_D = \text{ATR}_D(5) - \text{ATR}_D(14)$$
- Diseñar las salidas mediante el **Triple Barrier Method**:
  1. Barrera 1 (Take Profit): $P_{\text{entry}} \pm (k_1 \times \text{ATR}_D(14)[1])$
  2. Barrera 2 (Stop Loss): Nivel estructural o múltiplo ATR.
  3. Barrera 3 (Time-Stop): Liquidación a mercado tras $N$ barras intradía.
- Emitir el contrato JSON formal validado con [`quant_agentic_swarm/schemas/strategy_specification.schema.json`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/schemas/strategy_specification.schema.json).

### Fase 3: Enjambre de Desarrolladores Especialistas (Estándar de 7 Bloques)
Generar el código fuente respetando de forma idéntica los 7 bloques estructurales en ambas plataformas:
- **Bloque 0:** Metadatos institucionales y declaración de compilador (`//@version=6` en Pine, `mql5` en MT5).
- **Bloque 1:** Inputs agrupados con límites estrictos (`minval`, `maxval`, `step`).
- **Bloque 2:** Guarda de calentamiento histórico (5 a 10 años D1).
- **Bloque 3:** Motor MTF Diario sin repainting (`[1]` / `shift = 1`).
- **Bloque 4:** Alpha Engine sincronizado al cierre de vela (`barstate.isconfirmed` / `IsNewBar()`).
- **Bloque 5:** Triple Barrera de salidas y logs JSON únicamente en disparos (`ENTRY` / `EXIT`).
- **Bloque 6:** HUD Neutro-Informativo en pantalla con semáforo y telemetría de parámetros.

### Fase 4: Entregables, Factsheet y Bitácora
1. Script `.pine` en [`quant_agentic_swarm/strategies/`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/strategies) y/o [`TradingView/pine/strategies/`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/TradingView/pine).
2. Expert Advisor `.mq5` en [`quant_agentic_swarm/strategies/`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/strategies).
3. Documento ejecutivo [`STRATEGY_FACTSHEET.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/templates/STRATEGY_FACTSHEET_TEMPLATE.md) con formulación matemática en LaTeX y citas.
4. Registro de la estrategia en [`quant_agentic_swarm/STRATEGY_REGISTRY.json`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/STRATEGY_REGISTRY.json).
5. Asignación y documentación de la sesión en [`BITACORA.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/BITACORA.md).

---

## 3. Principio de Pureza de Investigación

Para evitar sesgos y sobreajuste en etapas preliminares:
- **Queda terminantemente prohibido** incorporar filtros pasivos no solicitados (como filtros de spread en pips, bloqueo de gaps de fin de semana o filtros de noticias) en el código de estudio inicial.
- La hipótesis debe evaluarse en su estado estadístico puro antes de aplicar capas de ejecución en vivo.

---

## 4. Mapa del Repositorio

```text
seminario_2/
├── README.md                           # Visión maestra y orquestación del ecosistema
├── BITACORA.md                         # Bitácora cronológica de sesiones de trabajo (DevLog)
├── .agents/
│   └── AGENTS.md                       # Reglas de comportamiento locales para agentes de IA
│
├── Libros_Validados/                   # Biblioteca de 51+ libros de trading en Markdown
│   ├── README.md                       # Catálogo bibliográfico clasificado por escuelas
│   ├── LLM_INDEX.md                    # Matriz de enrutamiento semántico y optimización
│   └── assets/                         # Gráficos y diagramas rasterizados de los libros
│
├── quant_agentic_swarm/                # Orquestador del enjambre multi-agente
│   ├── README.md                       # Arquitectura general del swarm
│   ├── viewer.html                     # Visor interactivo SVG del flujo de trabajo
│   ├── INSTRUCTIONS_FOR_AI.md          # Protocolo de operación estándar para LLMs
│   ├── STRATEGY_REGISTRY.json          # Registro maestro de estrategias producidas
│   ├── docs/                           # Arquitectura, metodología y estándares
│   ├── schemas/                        # JSON Schema para StrategySpecification
│   ├── templates/                      # Plantillas para Pine, MQL5 y Factsheets
│   └── strategies/                     # Estrategias generadas con paridad total
│
├── TradingView/                        # Entorno cuantitativo en Pine Script v6
│   ├── README.md                       # Guía de la suite de TradingView
│   ├── GEMINI.md / AGENTS.md           # Reglas de desarrollo en Pine Script v6
│   ├── knowledge/                      # 31 manuales técnicos exhaustivos
│   ├── masterclass/                    # Laboratorios de análisis cuantitativo
│   └── pine/                           # Indicadores, librerías y estrategias
│
└── MT5/                                # Entorno cuantitativo en MetaTrader 5
    ├── README.md                       # Guía de la suite MetaTrader 5
    ├── AGENTS.md                       # Reglas de desarrollo en MQL5 y Python
    ├── knowledge/                      # 20 tratados técnicos de arquitectura MT5
    ├── src/gateway/                    # Servidor REST FastAPI para control de MT5
    └── scripts/                        # Escaneo de ATR, carry trade y swaps
```

---

## [SIGNAL] 5. Guía de Inicio Rápido para Sesiones de Trabajo

1. **Revisar la Bitácora:** Abre [`BITACORA.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/BITACORA.md) para conocer el último estado y las tareas pendientes.
2. **Consultar la Biblioteca:** Utiliza [`Libros_Validados/LLM_INDEX.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/Libros_Validados/LLM_INDEX.md) para extraer conceptos o fórmulas canónicas.
3. **Explorar el Enjambre:** Abre [`quant_agentic_swarm/viewer.html`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/viewer.html) en tu navegador para revisar visualmente la tubería de producción.
4. **Proponer Nueva Estrategia:** Presenta la idea de trading al agente; el agente ejecutará automáticamente la **Fase 1** generando las 3 fichas técnicas y esperando tu aprobación.
5. **Cerrar Sesión:** Al finalizar la jornada o hito, actualiza de forma obligatoria la [`BITACORA.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/BITACORA.md).
