# Quant Agentic Swarm (QAS)
> **Laboratorio Cuantitativo Agentico para la Ideacion, Formalizacion y Generacion de Codigo Puro (PineScript v5 & MQL5)**

[![Architecture: Multi-Agent Swarm](https://img.shields.io/badge/Architecture-Multi--Agent%20Swarm-blue.svg)](#)
[![Methodology: Lopez de Prado & Kaufman](https://img.shields.io/badge/Methodology-Lopez%20de%20Prado%20%7C%20Kaufman-emerald.svg)](#)
[![Platforms: TradingView & MT5](https://img.shields.io/badge/Platforms-TradingView%20v5%20%7C%20MetaTrader%205-purple.svg)](#)
[![Status: Research Grade](https://img.shields.io/badge/Status-Research%20Purity%20Certified-orange.svg)](#)

---

## Vision y Proposito

El **Quant Agentic Swarm (QAS)** es una infraestructura agentica de produccion diseñada para transformar intuiciones e ideas de trading en estrategias cuantitativamente formales y ejecutables en **TradingView (PineScript v5)** y **MetaTrader 5 (MQL5 POO)**.

A diferencia de los asistentes de codigo convencionales que inventan reglas o sufren de alucinaciones, QAS opera bajo una **arquitectura por capas con aislamiento estricto**:
1. **Capa 1 (Investigacion Pura):** De la idea en lenguaje natural a la formulacion de hipotesis, modelado de reglas respaldadas por la literatura financiera y codificacion limpia con paridad matematica bajo el **Estandar de 7 Bloques**.
2. **Capa 2 (Optimizacion Parametrica & Validacion):** Analisis de sensibilidad, Walk-Forward y testing de robustez estadistica (aislado para evitar sobreajuste temprano).

---

## Mapa Arquitectonico del Sistema

```
                              ┌──────────────────────────────────────────────┐
                              │ USUARIO: Idea o Intuicion de Mercado         │
                              └──────────────────────┬───────────────────────┘
                                                     │
                                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FASE 1: CO-CREACION DE HIPOTESIS (HUMAN-IN-THE-LOOP)                                               │
│ - Agente de Hipotesis genera 3 Fichas Tecnicas (Variantes A, B, C: Momentum, Pullback, Volatilidad)│
│ - Puerta de Control HITL: El trader aprueba, combina o ajusta antes de pasar a reglas.             │
│ - Memoria Persistente: Consulta previa y registro continuo en STRATEGY_REGISTRY.json.              │
└────────────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                     │ (Hipotesis Certificada y Firmada)
                                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FASE 2: MODELADO DE REGLAS CANONICAS CON RAG 1 (LITERATURA CUANTITATIVA)                           │
│ - Formulas de Autor: Kaufman, Chan, Crabel, Williams (sin reglas inventadas ni sobreajuste).       │
│ - Motor MTF de Volatilidad: Z-Score Diario (ATR 5 vs 14) con Medidor de 5 a 10 Años D1.           │
│ - Motor de Salidas Cuantitativas: Triple Barrier Method (Take Profit ATR D1, Stop y Time-Stop).    │
│ - Contrato JSON: StrategySpecification con citas bibliograficas, formulas en LaTeX y Pseudocodigo. │
└────────────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                     │ (StrategySpecification con Strategy UUID)
                                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FASE 3: ENJAMBRE DE DESARROLLADORES ESPECIALISTAS (MULTI-RAG)                                      │
│ - Router de Entorno (PineScript / MQL5 / Ambos).                                                   │
│ - Agente PineScript v5 + RAG 2 (TradingView nativo, lookahead-off en security, UDTs y alertas).    │
│ - Agente MQL5 POO + RAG 3 (MetaTrader 5, CTrade, IsNewBar Sync, Warmup Guard y control de handles).│
│ - Agente QA de Paridad: Comprueba paridad matematica cruzada y 0 errores / 0 warnings.             │
└────────────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                     │
                                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FASE 4: ENTREGABLES, TELEMETRIA Y FACTSHEET                                                        │
│ - Codigo Fuente Puro: .pine (TradingView v5) y .mq5 (Expert Advisor POO para MT5).                 │
│ - Esqueleto Estandar de 7 Bloques: Anatomia determinista y modular en ambos lenguajes.             │
│ - HUD Neutro-Informativo en Pantalla: Semaforo de 5-10 años D1, Z-Score y resumen de parametros.   │
│ - Telemetria de Razonamiento: Logs estructurados en JSON unicamente en disparos (ENTRY / EXIT).    │
│ - STRATEGY_FACTSHEET.md: Manual ejecutivo con la tesis X-Y-Z, LaTeX, Citas y Guia de Broker.       │
│ - Pureza de Investigacion: Cero filtros de ejecucion en vivo (gaps/spreads) en la fase de estudio. │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes y Principios Clave

### 1. Co-Creacion de Hipotesis (HITL Gatekeeper)
El usuario no recibe un codigo a ciegas. El **Agente de Hipotesis** descompone la idea bruta en **3 Variantes Tecnicas Estructuradas** bajo la formula rigurosa:
$$\text{Si ocurre la condicion } X \implies \text{Esperamos el movimiento } Y \implies \text{Debido a la causa estructural } Z$$
El trader tiene el control para elegir, combinar o ajustar los supuestos antes de sellar la **Hipotesis Certificada**.

### 2. Memoria Canonica Multi-RAG Federada
Cada agente interactua exclusivamente con una base de conocimiento especializada de su dominio:
*   **RAG 1 (Cuantitativo & Literatura):** Libros canonicos (Kaufman, Chan, Crabel, Lopez de Prado, Williams, Van Tharp).
*   **RAG 2 (PineScript v5):** Manual oficial v5, guia anti-repainting y patrones UDTs.
*   **RAG 3 (MQL5 OOP):** MQL5 Reference, Standard Library (`CTrade`), gestion de eventos y memoria.

### 3. Filtro de Regimen MTF: Z-Score de Volatilidad (Lopez de Prado)
Cuantifica la volatilidad en el marco Diario ($D1$) utilizando la aceleracion de $\text{ATR}_D(5)$ frente a $\text{ATR}_D(14)$:
$$Z_{\text{vol}} = \frac{\text{Diff}_D - \text{SMA}(\text{Diff}_D, 20)}{\text{StDev}(\text{Diff}_D, 20)}$$
*   **Volatilidad Baja:** $Z_{\text{vol}} < -0.67$ (Calma / Compresion).
*   **Volatilidad Media:** $-0.67 \le Z_{\text{vol}} \le +0.67$ (Regimen estacionario normal).
*   **Volatilidad Alta:** $Z_{\text{vol}} > +0.67$ (Expansion de rango).

### 4. Salidas Cuantitativas: Triple Barrier Method
Elimina los stops fijos arbitrarios e incorpora el coste de oportunidad del capital mediante 3 barreras simultaneas:
1.  **Barrera 1 (Take Profit Dinamico):** $+k_1 \times \text{ATR}_D(14)$ (anclado a la volatilidad diaria).
2.  **Barrera 2 (Stop Loss Estructural):** $-k_2 \times \text{ATR}$ o nivel tecnico de invalidacion.
3.  **Barrera 3 (Limite Temporal / Time-Stop):** Liquidacion a mercado tras $N$ barras si la tesis no se desenvuelve.

### 5. Esqueleto Estandar de 7 Bloques
Todo codigo generado por los agentes sigue estrictamente el [Estandar de 7 Bloques](docs/CODE_SKELETON_STANDARD.md), garantizando modularidad, reproducibilidad y determinismo entre TradingView y MT5.

---

## Estructura del Repositorio

```text
quant_agentic_swarm/
├── README.md                           # Documento principal del repositorio
├── viewer.html                         # Visualizador interactivo minimalista del enjambre
├── docs/
│   ├── ARCHITECTURE.md                 # Especificacion tecnica profunda del enjambre
│   ├── METHODOLOGY.md                  # Fundamentos cuantitativos y matematicos
│   ├── INTERACTION_GUIDE.md            # Protocolo de co-creacion Humano-en-el-Bucle (HITL)
│   └── CODE_SKELETON_STANDARD.md       # Estandar canónico del esqueleto de código de 7 bloques
├── schemas/
│   └── strategy_specification.schema.json # JSON Schema formal del contrato intermedio
└── templates/
    ├── STRATEGY_FACTSHEET_TEMPLATE.md  # Plantilla de documentacion por estrategia
    ├── STRATEGY_REGISTRY_SAMPLE.json   # Muestra del registro de memoria persistente
    ├── tradingview_v5_template.pine    # Plantilla de referencia en PineScript v5
    └── mql5_ea_template.mq5            # Plantilla de referencia en MQL5 POO
```

---

## Guia de Inicio Rapido

1. **Explorar el Diagrama Interactivo:**
   Abre [`viewer.html`](viewer.html) en cualquier navegador moderno para explorar el flujo con controles de zoom y pan.
2. **Revisar el Estandar de Codigo:**
   Consulta [`docs/CODE_SKELETON_STANDARD.md`](docs/CODE_SKELETON_STANDARD.md) para comprender los 7 bloques estructurales.
3. **Revisar la Metodologia Matematica:**
   Consulta [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) para comprender las formulas en LaTeX y la derivacion del Z-Score y las 3 barreras.
4. **Auditar el Contrato Intermedio:**
   Inspecciona [`schemas/strategy_specification.schema.json`](schemas/strategy_specification.schema.json) para ver como se comunican los agentes de investigacion con los desarrolladores.

---

## Licencia y Reconocimientos
Desarrollado bajo principios cuantitativos rigurosos inspirados en las obras de **Marcos Lopez de Prado, Perry J. Kaufman, Toby Crabel y Ernest P. Chan**.
