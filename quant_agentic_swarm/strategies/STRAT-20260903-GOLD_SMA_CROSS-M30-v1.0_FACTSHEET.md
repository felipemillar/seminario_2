# STRATEGY FACTSHEET: STRAT-20260903-GOLD_SMA_CROSS-M30-v1.0

> **Estrategia Cuantitativa:** Cruce Intermedio Direccional con Filtro Macro (SMA 20/50 + EMA 200)  
> **Autor Institucional:** QRT Solutions  
> **Activo Primario:** `XAUUSD` (Oro al Contado / Futuros CME) / Multi-activo mayor  
> **Timeframe Operativo:** `M30` (30 minutos)  
> **Timeframe de Régimen (MTF):** `D1` (Diario cerrado, shift 1)  
> **Fecha de Emisión:** 2026-09-03  

---

## 1. Fundamentación Teórica & Literatura Canónica
* **Perry J. Kaufman (2013)** — *Trading Systems and Methods*: Estudio exhaustivo de la inercia de cruces de medias móviles simples (SMA). Kaufman demuestra que los cruces intermedios (como 20/50) capturan la transición estructural entre acumulación y tendencia, filtrando el ruido de ultra-corto plazo.
* **Alexander Elder (1993, 2014)** — *The New Trading for a Living*: El filtro direccional de marea mayor. Exige que cualquier cruce intradiario esté estrictamente alineado con la media móvil de largo plazo (EMA 200), erradicando las trampas de mercado en rangos laterales.
* **Marcos López de Prado (2018)** — *Advances in Financial Machine Learning*: Implementación del *Triple Barrier Method* normalizado por volatilidad real (Barrera 1: Take Profit a 1.50x ATR D1, Barrera 2: Stop Loss a 0.75x ATR D1, Barrera 3: Time Stop a 48 barras M30 / 24 horas).

---

## 2. Hipótesis Estructural de Mercado
```
           [TENDENCIA MACRO ALCISTA: Precio > EMA 200]
                     ↗
                   ↗     (SMA 20 cruza sobre SMA 50)
                 ↗   - <-- GATILLO: Cruce en vela cerrada [1]
               ↗
  [EMA 200] ───────────────────────────────────────────────
```
1. **Condición (X):** Al cierre de la barra M30 (shift = 1), la SMA 20 cruza por encima de la SMA 50 para compras (o por debajo para ventas), con el precio de cierre a favor de la EMA 200.
2. **Expectativa (Y):** Captura de la aceleración inercial con un ratio beneficio/riesgo de 2.0 a 1, eliminando quiebres falsos contra la tendencia institucional de fondo.
3. **Causa Estructural (Z):** Los grandes operadores y fondos de cobertura rebalancean inventarios en la dirección de la marea macro. El cruce intermedio confirma que la masa crítica de volumen se ha alineado con el sesgo dominante.

---

## 3. Especificación Técnica de Parámetros

| Parámetro | Valor por Defecto | Justificación Cuantitativa |
| :--- | :--- | :--- |
| `InpFastSMAPeriod` | `20` | Media simple de velocidad intermedia (10 horas de mercado). |
| `InpSlowSMAPeriod` | `50` | Media simple lenta de referencia cíclica (25 horas de mercado). |
| `InpMacroEMAPeriod` | `200` | Filtro tendencial macro institucional (100 horas de mercado). |
| `InpTPMultiplier` | `1.50` | Barrera 1 de Take Profit normalizada al ATR Diario(14) shift 1. |
| `InpSLMultiplier` | `0.75` | Barrera 2 de Stop Loss asimétrica (Payoff 2:1 estructural). |
| `InpMaxBarsHeld` | `48` | Barrera 3 de tiempo (24 horas de retención máxima). |
| `InpZScoreMin` | `-0.67` | Filtro de régimen de volatilidad de López de Prado. |

---

## 4. Archivos Entregables en el Repositorio

* **Contrato JSON Formal:** [`quant_agentic_swarm/strategies/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.0_specification.json`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/strategies/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.0_specification.json)
* **TradingView (Pine Script v6):** [`TradingView/pine/strategies/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.0.pine`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/TradingView/pine/strategies/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.0.pine)
* **MetaTrader 5 (MQL5 POO):** [`MT5/estrategias/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.0.mq5`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/estrategias/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.0.mq5)
