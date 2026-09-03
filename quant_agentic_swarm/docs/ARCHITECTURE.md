# Arquitectura del Sistema Multi-Agente (Quant Agentic Swarm)

Este documento detalla la topologia agentica, los contratos de datos, el flujo de estados y los mecanismos de sincronizacion tecnica que gobiernan el **Quant Agentic Swarm (QAS)**.

---

## 1. Topologia del Enjambre: Jerarquia con Supervisor y RAGs Federados

El sistema implementa una **topologia jerarquica con enjambres especializados** (Supervisor / Sub-swarms) para evitar la dispersion cognitiva y la contaminacion de contexto:

```mermaid
flowchart TD
    classDef supervisor fill:#09090b,stroke:#09090b,stroke-width:2px,color:#ffffff;
    classDef research fill:#eff6ff,stroke:#2563eb,stroke-width:1.5px,color:#1e3a8a;
    classDef rag fill:#fdf4ff,stroke:#9333ea,stroke-width:1.5px,color:#581c87;
    classDef spec fill:#fefce8,stroke:#ca8a04,stroke-width:1.5px,color:#713f12;
    classDef dev fill:#f0fdf4,stroke:#16a34a,stroke-width:1.5px,color:#14532d;
    classDef qa fill:#f8fafc,stroke:#64748b,stroke-width:1.5px,color:#1e293b;

    User["Usuario (Trader / Investigador)"]:::supervisor --> LeadSup["Lead Quantitative Strategist (Supervisor)"]:::supervisor
    Registry[("STRATEGY_REGISTRY.json\n(Memoria Persistente)")]:::rag <--> LeadSup

    subgraph SWARM_RESEARCH ["Sub-Enjambre de Investigacion Cuantitativa"]
        direction TB
        HypAgent["Agente de Hipotesis (HITL Co-Creator)"]:::research
        ModelerAgent["Agente Modelador de Reglas"]:::research
        RAG1[("RAG 1: Literatura & Papers\n(Kaufman, Chan, Williams, Crabel)")]:::rag
        
        HypAgent --> ModelerAgent
        ModelerAgent <-->|Formulas Canonicas & Citas| RAG1
    end

    LeadSup --> SWARM_RESEARCH
    SWARM_RESEARCH --> LeadSup

    LeadSup --> SpecDoc["StrategySpecification (JSON Contract)\n+ Formulas en LaTeX + Pseudocodigo + Strategy UUID"]:::spec

    subgraph SWARM_DEV ["Sub-Enjambre de Desarrolladores Especialistas"]
        direction TB
        Router{"Selector de Entorno"}:::spec
        
        subgraph PINE_STACK ["Ecosistema PineScript v5"]
            PineDev["Agente PineScript v5"]:::dev
            RAG2[("RAG 2: PineScript KB\n(Manual v5, Anti-Repainting, UDTs)")]:::rag
            PineDev <--> RAG2
        end

        subgraph MQL_STACK ["Ecosistema MQL5 POO"]
            MQLDev["Agente MQL5 (EA)"]:::dev
            RAG3[("RAG 3: MQL5 KB\n(CTrade, IsNewBar, Handles D1)")]:::rag
            MQLDev <--> RAG3
        end

        QA_Agent["Agente QA & Paridad Cross-Compiler\n(Verificacion 0 Errors / 0 Warnings)"]:::qa

        Router -->|TradingView| PineDev
        Router -->|MetaTrader 5| MQLDev
        Router -->|Ambos| PineDev & MQLDev
        
        PineDev --> QA_Agent
        MQLDev --> QA_Agent
    end

    SpecDoc --> Router
    QA_Agent --> FinalDeliverables["Entregables: .pine + .mq5 + FACTSHEET.md + HUD"]:::supervisor
```

---

## 2. Especializacion de Roles y Agentes

| Agente | Enjambre | Responsabilidad Principal | Tools / Dependencias |
| :--- | :--- | :--- | :--- |
| **`Lead Strategist`** | Supervision | Orquesta el ciclo completo, valida el `Strategy UUID` y administra `STRATEGY_REGISTRY.json`. | Vector Memory, File I/O |
| **`HypothesisAgent`** | Investigacion | Descompone ideas en 3 Fichas Tecnicas (Variantes A, B, C) y gestiona la puerta HITL. | HITL Gatekeeper, Prompt Socratico |
| **`RuleModelerAgent`** | Investigacion | Traduce la hipotesis en condiciones matematicas, el Z-Score de volatilidad MTF y las 3 barreras (con TP anclado a ATR D1). | RAG 1 (Libros de Trading), Motor LaTeX |
| **`PineScriptAgent`** | Desarrollo | Escribe codigo nativo Pine Script v5 idiomatico, con tipos explicitos y `lookahead_off`. | RAG 2 (PineScript v5 Reference) |
| **`MQL5Agent`** | Desarrollo | Diseña Expert Advisors estructurados en POO con la libreria estandar `Trade\Trade.mqh`. | RAG 3 (MQL5 Standard Library) |
| **`QACodeAgent`** | Control Calidad | Audita que no existan discrepancias logicas entre PineScript y MQL5 y valida compilacion. | Cross-Compiler Linter |

---

## 3. Contrato de Comunicacion Intermedia: `StrategySpecification`

Los desarrolladores **NUNCA** reciben texto informal o ambiguo. Reciben un contrato estructurado en formato JSON validado por JSON Schema:

```json
{
  "$schema": "../schemas/strategy_specification.schema.json",
  "strategy_id": "STRAT-20260901-ORB_D1Z-M15-v1.0",
  "timestamp": "2026-09-01T11:00:00Z",
  "hypothesis": {
    "condition_x": "Ruptura del maximo asiatico en vela cerrada M15",
    "expected_outcome_y": "Expansion direccional sostenida en la apertura de Londres",
    "structural_reason_z": "Absorcion institucional de liquidez y ejecucion de ordenes pendientes",
    "invalidation_criterion": "Cierre de vela M15 por debajo del nivel de ruptura"
  },
  "market_regime_mtf": {
    "model": "Lopez_de_Prado_Daily_ZScore",
    "regime_timeframe": "D1",
    "execution_timeframe": "M15",
    "fast_atr_period": 5,
    "slow_atr_period": 14,
    "zscore_threshold_high": 0.67,
    "target_history_years_range": [5, 10]
  },
  "execution_rules": {
    "entry_long": {
      "trigger_formula_latex": "\\text{Close}_{M15} > \\text{High}_{\\text{Asian}}",
      "pseudocode": "IF Close > Asian_High AND z_vol > 0.67 AND InSession() THEN BuySignal = TRUE",
      "canonical_citation": "Toby Crabel - Day Trading with Short Term Price Patterns"
    },
    "triple_barrier_exits": {
      "barrier_1_profit_atr_d1_multiplier": 1.0,
      "barrier_2_stop_atr_multiplier": 1.5,
      "barrier_3_time_stop_max_bars": 24
    }
  },
  "research_purity_declaration": {
    "live_execution_filters_omitted": true,
    "unrequested_passive_protections": false
  }
}
```

---

## 4. Sincronizacion del Modelo de Ejecucion (TV vs MT5)

Para garantizar paridad total entre TradingView y MetaTrader 5:

1. **Sincronizacion Multi-Timeframe (D1 -> M15):**
   * **PineScript:** `request.security(syminfo.tickerid, "D", ta.atr(14)[1], barmerge.gaps_off, barmerge.lookahead_off)` (usa la barra cerrada de ayer `[1]` tanto para el Z-Score como para el Take Profit de $k_1 \times \text{ATR}_D(14)$ para evitar repainting).
   * **MQL5:** `CopyBuffer(handle_atr14_d1, 0, 1, 20, buffer)` (copia desde el `shift = 1` del grafico diario).
2. **Granularidad Temporal (`IsNewBar`):**
   * En PineScript las estrategias evaluan por defecto al cierre de barra (`barstate.isconfirmed`).
   * En MQL5, el agente incluye una clase de utilidad `IsNewBar()` dentro de `OnTick()` para que el EA solo dispare cuando la vela intradia se haya confirmado, eliminando falsos positivos intra-barra.
3. **Telemetria Homogenea:**
   * Ambos lenguajes emiten logs en formato JSON estructurado unicamente en momentos de disparo (`ENTRY` / `EXIT`).
