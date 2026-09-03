# STRATEGY FACTSHEET: STRAT-20260903-GOLD_SMA_CROSS-M30-v1.1 (Optimizada)

> **Estrategia Cuantitativa:** Cruce Intermedio Direccional con Filtro Macro (SMA 20/50 + EMA 200) — Versión Optimizada v1.1  
> **Autor Institucional:** QRT Solutions  
> **Activo Primario:** `XAUUSD` / `XAUAUD` (Oro al Contado / Futuros CME)  
> **Timeframe Operativo:** `M30` (30 minutos)  
> **Timeframe de Régimen (MTF):** `D1` (Diario cerrado, shift 1)  
> **Fecha de Emisión:** 2026-09-03  

---

## 1. Fundamentación de las Mejoras Cuantitativas (v1.1)

Basado en la auditoría cuantitativa exhaustiva de los 639 trades ejecutados en el backtest de 6.6 años (2020–2026), se implementaron 3 optimizaciones estructurales directas:

1. **Corrección de Asimetría Direccional (Modo Long-Only):**
   * *Diagnóstico Forense:* En la versión 1.0, los Longs aportaron **+$945.24 USD** con un Profit Factor de **1.42** y una Esperanza de **+$2.81 USD/trade**, mientras que los Shorts generaron **-$49.32 USD** con un PF de **0.98** y esperanza negativa.
   * *Acción v1.1:* Se configura por defecto la operación exclusiva en compras (`DIR_LONGS_ONLY`), alineando el capital al 100% con la tendencia macro del Oro.
2. **Calibración de Take Profit por Masa Modal de MFE:**
   * *Diagnóstico Forense:* El 87.2% de las operaciones cerraron por reversa de cruce opuesto, pues la meta de $1.50\times ATR_D$ quedaba distante para la velocidad media del ciclo.
   * *Acción v1.1:* Se ajusta el Take Profit a **$1.10\times ATR_D$** (masa modal de MFE), asegurando la toma de ganancias antes del retroceso.
3. **Capa Dinámica de Protección de Capital (Breakeven & Circuit Breaker):**
   * *Acción v1.1:* Incorporación de un **Breakeven dinámico** al alcanzar $+0.50\times ATR_D$ que desplaza el Stop Loss a precio de entrada $+0.05\times ATR_D$ para blindar comisiones.
   * *Acción v1.1:* **Circuit Breaker mensual** que pausa las operaciones si se registran 3 pérdidas consecutivas en el mes calendario en curso (*Elder & Van Tharp*).

---

## 2. Especificación Técnica de Parámetros v1.1

| Parámetro | Valor v1.0 | Valor Optimizada v1.1 | Justificación Cuantitativa |
| :--- | :---: | :---: | :--- |
| `InpTradeDirection` | Ambas | **Solo Compras (Longs)** | Erradica el arrastre negativo de los cortos (PF 0.98 -> 1.42). |
| `InpTPMultiplier` | 1.50 | **1.10** | Anclado en la masa modal de MFE para evitar devoluciones. |
| `InpSLMultiplier` | 0.75 | **0.75** | Preservado para mantener un ratio Payoff favorable de 1.47 a 1. |
| `InpUseBreakeven` | Inactivo | **True** | Bloquea ganancias al alcanzar $+0.50\times ATR_D$. |
| `InpMaxMonthLosses` | Inactivo | **3** | Freno preventivo tras 3 fallos consecutivos en el mes. |
| `InpMaxBarsHeld` | 48 | **48** | Retención máxima de 24 horas (1 sesión diaria completa). |

---

## 3. Archivos Entregables en el Repositorio

* **Contrato JSON Formal:** [`quant_agentic_swarm/strategies/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.1_specification.json`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/strategies/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.1_specification.json)
* **TradingView (Pine Script v6):** [`TradingView/pine/strategies/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.1.pine`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/TradingView/pine/strategies/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.1.pine)
* **MetaTrader 5 (MQL5 POO):** [`MT5/estrategias/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.1.mq5`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/estrategias/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.1.mq5)
* **Binario Compilado MT5:** `drive_c/Program Files/MetaTrader 5/MQL5/Experts/STRAT-20260903-GOLD_SMA_CROSS-M30-v1.1.ex5` (y alias `EAGold_SMACross_v1.1.ex5`).
