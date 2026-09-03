# TradingView Quant Suite & Knowledge Repository
> **Desarrollado por:** QRT Solutions  
> **Plataforma:** TradingView / Pine Script v6 / Python Cuantitativo  
> **Propósito:** Ecosistema integral de investigación avanzada, desarrollo algorítmico institucional y base de conocimiento para análisis financiero y trading cuantitativo.

---

## Arquitectura del Repositorio

El repositorio está organizado bajo una arquitectura modular de alto rendimiento pensada para la colaboración sinérgica entre desarrolladores cuantitativos y **Agentes Autónomos de Inteligencia Artificial**:

```text
TradingView/
├── .agents/                                # Ecosistema de Agentes de IA
│   ├── AGENTS.md                           # Reglas operativas y contexto del proyecto
│   └── skills/                             # Skills modulares (Estándar AgentSkills.io)
│       ├── tradingview-knowledge-navigator/# Navegación y consulta de los 31 manuales
│       ├── pinescript-v6-architect/        # Estándares de desarrollo en Pine Script v6
│       └── trading-literature-researcher/  # Fundamentación en 53+ libros de trading
│
├── knowledge/                              # Base de Conocimiento (Deep Research)
│   ├── INDEX.md                            # Índice maestro de investigación
│   ├── Manual Técnico Pine Script v6.md    # Referencia completa de v6
│   ├── Guía Backtesting Pine Script.md      # Motor de simulación y órdenes
│   ├── Metodología de Validación en Trading.md # Walk-Forward, OOS, Optuna
│   └── ... (31 manuales especializados en Markdown)
│
├── pine/                                   # Código Fuente Pine Script v6
│   ├── indicators/                         # Indicadores técnicos y de régimen
│   ├── strategies/                         # Estrategias algorítmicas institucionales
│   │   ├── gap_fade_simple_30m.pine        # Gap Fade 30M con Dashboard Dual
│   │   └── nq_gap_fade_masterclass_5m.pine # NQ Gap Fade 5M con 3 filtros de régimen
│   └── libraries/                          # Librerías reutilizables v6
│
├── masterclass/                            # Laboratorio Cuantitativo & Notebooks
│   ├── notebooks/                          # Jupyter Notebooks de investigación
│   │   ├── A01_nq_gaps_hipotesis_exploracion.ipynb
│   │   ├── A02_nq_gaps_entradas_salidas_mae_mfe.ipynb
│   │   └── A03_nq_gaps_optimizacion_sizing_validacion.ipynb
│   └── guion.md                            # Guión técnico del framework cuantitativo
│
├── data/                                   # Datasets y Reportes de Backtesting
│   └── backtestings/                       # Reportes CSV exportados de TradingView
│
└── scripts/                                # Utilidades Python y Automatización
```

---

## Base de Conocimiento de TradingView (`knowledge/`)

El directorio `knowledge/` alberga **31 manuales técnicos exhaustivos** desarrollados con Gemini Deep Research, cubriendo todas las facetas de la plataforma:

1. **Pine Script v6 & Optimización:** Tipado estricto, estructuras de usuario (`type`), matrices, maps, garbage collection y límites de memoria.
2. **Backtesting & Validación Institucional:** Partición In-Sample / Out-of-Sample, Walk-Forward Analysis, detección de mesetas (*Plateau Detection*) y prevención de sobreajuste.
3. **Data Engineering & Multi-Timeframe:** Feeds de datos, resoluciones intrabarra, protocolos anti-lookahead y análisis multi-activo.
4. **Microestructura & Order Flow:** Algoritmos de Footprint, Delta Acumulado (CVD) y Volume Profile en Pine Script.
5. **Automatización & Webhooks:** Arquitectura de alertas dinámicas JSON, middlewares de reconciliación y puentes de ejecución hacia brokers externos (Interactive Brokers, Tradovate, Binance).
6. **Integración Python & APIs:** Conexión vía `tvDatafeed`, servidores webhook asíncronos, ingeniería inversa de WebSockets (`wss://data.tradingview.com`) y arbitraje estadístico.

---

## Interacción para Agentes de IA (`.agents/skills/`)

Este repositorio implementa la especificación de **Revelación Progresiva (*Progressive Disclosure*)** para agentes de IA (Antigravity, Cursor, Claude Code):

* **`tradingview-knowledge-navigator`:** Permite a cualquier agente localizar instantáneamente conceptos técnicos y extraer fragmentos específicos de los 31 manuales sin sobrecargar el contexto.
* **`pinescript-v6-architect`:** Proporciona reglas estrictas de sintaxis v6, manejo de margen de futuros CME (5% / 20x), órdenes OCO seguras y arquitectura dual de backtesting.
* **`trading-literature-researcher`:** Conecta las estrategias con una biblioteca local de **53+ libros clásicos y avanzados** (Wyckoff, Al Brooks, Alexander Elder, Mark Douglas, CMT).

---

## Estrategias Cuantitativas Destacadas

### NQ Gap Fade Masterclass (5M) — [nq_gap_fade_masterclass_5m.pine](pine/strategies/nq_gap_fade_masterclass_5m.pine)
* **Activo:** Futuros E-mini Nasdaq 100 (`NQ1!`) y Micro Nasdaq (`MNQ1!`).
* **Timeframe:** 5 Minutos (09:30 a 16:00 NY).
* **Filtros Ex-Ante:**
  1. Magnitud del Gap: $|Gap| \ge 0.10\text{ ATR}$.
  2. Régimen de Volatilidad: Mediana rodante de 250 días ($ATR\% \le \text{Mediana}$).
  3. Filtro de Ruido: Kaufman Efficiency Ratio ($ER_{10} < 0.40$).
* **Salidas MAE/MFE:** Stop Loss a $-0.50\text{ ATR}$, Take Profit a $+0.90\text{ ATR}$, Salida EOD a las 16:00 NY.
* **Validación OOS:** Sharpe Ratio de **1.80** en prueba ciega Out-of-Sample (2019–2026).

---

## Requisitos y Configuración

1. **TradingView:** Cuenta gratuita o de pago con soporte para Pine Script v6.
2. **Python:** Entorno virtual Python 3.10+ para los notebooks del laboratorio en `masterclass/`:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install pandas numpy matplotlib seaborn scipy
   ```

---

## Licencia y Autoría

© **QRT Solutions**. Todos los derechos reservados. Diseñado para desarrollo cuantitativo institucional.
