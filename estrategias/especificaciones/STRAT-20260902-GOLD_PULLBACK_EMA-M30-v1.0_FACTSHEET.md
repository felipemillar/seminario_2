# STRATEGY FACTSHEET: STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0

> **Estrategia Cuantitativa:** Tendencia de Fibonacci con Entrada en Retroceso (Pullback a la Media)  
> **Autor Institucional:** QRT Solutions  
> **Activo Primario:** `XAUUSD` (Oro al Contado / Futuros CME)  
> **Timeframe Operativo:** `M30` (30 minutos)  
> **Timeframe de Régimen (MTF):** `D1` (Diario cerrado, shift 1)  
> **Fecha de Emisión:** 2026-09-02  

---

## 1. Fundamentación Teórica & Literatura Canónica
* **Tushar Chande & Stanley Kroll (1994)** — *The New Technical Trader*: Concepto de alineación de medias dinámicas y zonas de valor. En lugar de perseguir rupturas que compran en máximos relativos, el modelo espera la confirmación de la tendencia y ejecuta en el agotamiento del retroceso (*pullback*).
* **Marcos López de Prado (2018)** — *Advances in Financial Machine Learning*: Implementación del *Triple Barrier Method* (Barrera 1: Take Profit a $1.5 \times \text{ATR}_D(14)$, Barrera 2: Stop Loss a $0.75 \times \text{ATR}_D(14)$, Barrera 3: Límite de retención temporal a 32 barras M30 / 16 horas).

---

## 2. Hipótesis Estructural de Mercado
```
           [IMPULSO 1]
             ↗
           ↗ (Tendencia: EMA 13 > EMA 34 > EMA 89)
         ↗
       ↗   ↘ [RETROCESO / PULLBACK]
             ↘ (El precio testea la zona entre EMA 13 y 34)
               - <-- GATILLO: Vela de rechazo con Close > EMA 13
                 ↗
               ↗ [IMPULSO 2 ASIMÉTRICO]
```
1. **Condición (X):** Cascada de medias exponenciales de Fibonacci alineadas ($EMA_{13} > EMA_{34} > EMA_{89}$ para compras; $EMA_{13} < EMA_{34} < EMA_{89}$ para ventas). El mínimo/máximo penetra la zona de valor ($EMA_{13}$ a $EMA_{34}$) y la vela cierra confirmando el rechazo a favor del flujo principal.
2. **Expectativa (Y):** Entradas con bajo *drawdown* inicial y ratio de retorno asimétrico ($> 1.8:1$), evitando comprar en sobreextensión.
3. **Causa Estructural (Z):** Los creadores de mercado institucionales acumulan liquidez en las pausas de tendencia antes de defender el valor medio y reanudar el flujo direccional.

---

## 3. Especificación Técnica de Parámetros

| Parámetro | Valor por Defecto | Justificación |
| :--- | :--- | :--- |
| `InpFastEMAPeriod` | `13` | Secuencia Fibonacci de corto plazo (guía del impulso). |
| `InpMedEMAPeriod` | `34` | Secuencia Fibonacci intermedia (soporte/resistencia dinámico). |
| `InpSlowEMAPeriod` | `89` | Secuencia Fibonacci macro (filtro de marea institucional). |
| `InpTPMultiplier` | `1.5` | Barrera 1 de Take Profit anclada al ATR Diario(14) shift 1. |
| `InpSLMultiplier` | `0.75` | Barrera 2 de Stop Loss asimétrica (Payoff 2:1 estructural). |
| `InpMaxBarsHeld` | `32` | Barrera 3 de tiempo (16 horas de mercado). |
| `InpZScoreMin` | `-0.67` | Filtro de volatilidad MTF Diario de López de Prado. |

---

## 4. Archivos Entregables en el Repositorio

* **Contrato JSON Formal:** [`quant_agentic_swarm/strategies/STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0_specification.json`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/strategies/STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0_specification.json)
* **TradingView (Pine Script v6):** [`TradingView/pine/strategies/STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0.pine`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/TradingView/pine/strategies/STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0.pine)
* **MetaTrader 5 (MQL5 POO):** [`MT5/STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0.mq5`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0.mq5)
* **Binario Compilado MT5:** [`MQL5/Experts/STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0.ex5`](file:///Users/fmillar/Library/Application%20Support/net.metaquotes.wine.metatrader5/drive_c/Program%20Files/MetaTrader%205/MQL5/Experts/STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0.ex5) *(y alias `EAGold_PullbackEMA.ex5`)*
* **Indicador Visual Gráfico:** [`MQL5/Indicators/Ind_Pullback_EMA_M30.ex5`](file:///Users/fmillar/Library/Application%20Support/net.metaquotes.wine.metatrader5/drive_c/Program%20Files/MetaTrader%205/MQL5/Indicators/Ind_Pullback_EMA_M30.ex5)
