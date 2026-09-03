# Reporte Cuantitativo Comparativo (Pool de 3 Módulos) — Versión Base v1.0 vs Versión Optimizada v1.1

> **Estrategias Auditadas:**  
> • **Versión Base (v1.0):** `STRAT-20260902-USGAP_MOM-M15-v1.0` (Salidas puras: TP 2.0x ATR D1, SL 1.0x ATR M15, Time-Stop 26b, Sin Breakeven).  
> • **Versión Optimizada (v1.1):** `STRAT-20260902-USGAP_MOM-M15-v1.1` (TP calibrado 1.25x ATR D1, Breakeven dinámico +0.75x ATR M15, Circuit Breaker).  
> **Activo Evaluado:** `CUSTOM_NQ_M5` (Nasdaq 100 E-mini Futuros) | **Temporalidad:** M15  
> **Muestreo:**  
> • v1.0: 51 Operaciones Ejecutadas (Ventana 10 Años: 2016 – 2026)  
> • v1.1: 87 Operaciones Ejecutadas (Ventana 25 Años: 2001 – 2026)  
> **Autor Institucional:** QRT Solutions  
> **Estándar:** Pool Canónico de 3 Módulos conforme a [`MT5/BACKTEST_AUDIT_MANUAL.md`](../BACKTEST_AUDIT_MANUAL.md)

---

## Resumen Ejecutivo de la Comparación

La auditoría cruzada entre ambas versiones pone de manifiesto el **dilema clásico de la ingeniería cuantitativa de salidas (*Exit Engineering Trade-Off*)**:

1. **La Versión Base v1.0 (Trend-Run / Asimétrica):**  
   * Apuesta por una **asimetría de payoff agresiva (Payoff 1.62 a 1)**.
   * Al **no tener Breakeven**, tolera retrocesos intradiarios intermedios y deja correr los trades ganadores hasta el Time-Stop de 6.5 horas, logrando una ganancia media de **$+85.46 USD (+0.52%)** por trade ganador, a costa de un Win Rate más moderado (**47.06%**).
2. **La Versión Optimizada v1.1 (Protección Temprana / Breakeven):**  
   * Maximiza la **tasa de acierto (Win Rate 62.07% en 25 años y 71.15% en 10 años)**.
   * El Breakeven blindó **35 operaciones** que en v1.0 se devolvían a pérdida. Sin embargo, al tener un gatillo ajustado (+0.75x ATR), **cortó prematuramente la cola derecha de ganancias**, reduciendo el Payoff a **0.70** y la ganancia promedio por ganador a **$+25.46 USD (+0.146%)**.

---

## Módulo 1: La Evaluación Dual (Monetario vs Retorno Porcentual Puro)

| Métrica / Dimensión KPI | Versión Base (v1.0) — 10 Años | Versión Optimizada (v1.1) — 25 Años | Diagnóstico Comparativo |
| :--- | :---: | :---: | :--- |
| **Volumen Operado (Lotes)** | **1.0 Lote Completo** | **0.10 Lotes (en MT5)** | La v1.1 operó con 10 veces menos capital en MT5. |
| **PnL Neto Monetario (USD)** | **+$534.63 USD** | **+$342.12 USD** (Neto MT5: $29.52) | v1.0 acumula más USD por dejar correr los trades. |
| **Profit Factor Monetario** | **1.35** | **1.33** | Rentabilidad monetaria muy similar y consistente. |
| **Tasa de Acierto (Win Rate)** | **47.06%** (24W / 27L) | **62.07%** (54W / 33L) | **v1.1 supera en +15.01% el Win Rate**. |
| **Ganancia Media (Avg Win)** | **+$85.46 USD** | **+$25.46 USD** | v1.0 triplica la ganancia media al no asfixiar el trade. |
| **Pérdida Media (Avg Loss)** | **-$56.16 USD** | **-$31.30 USD** | v1.1 reduce la pérdida media en casi un 45%. |
| **Retorno Porcentual Puro** | **+3.77%** | **+1.03%** | v1.0 capturó mayor variación del precio del Nasdaq. |
| **Profit Factor Porcentual (%)** | **1.44** | **1.15** | v1.0 tiene mayor eficiencia de puntos capturados. |
| **Payoff Ratio (%)** | **1.62 a 1** | **0.70 a 1** | **v1.0 tiene ventaja asimétrica; v1.1 ventaja probabilística**. |
| **Drawdown Máximo de Cuenta** | **0.04% ($431.99 USD)** | **0.00% ($30.22 USD)** | v1.1 reduce el Drawdown máximo a niveles casi nulos. |
| **Ratio de Sharpe (MT5)** | **3.92** | **2.72** | Ambas presentan una curva de equity institucional sólida. |

---

## Módulo 2: Diagnóstico de Asimetrías (¿Dónde está el Edge?)

### 2.1. Desglose Direccional Mandatorio (Longs vs Shorts)
*(Alexander Elder & Perry Kaufman)*

```markdown
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ COMPARATIVA DIRECCIONAL: LONGS (COMPRAS) vs SHORTS (VENTAS)                            │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

| Parámetro Direccional | v1.0 Longs | v1.1 Longs | v1.0 Shorts | v1.1 Shorts | Diagnóstico Asimétrico |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **N° de Trades** | 27 trades | 49 trades | 24 trades | 38 trades | Distribución equilibrada en ambas versiones. |
| **Tasa de Acierto (WR)** | **59.26%** | **61.22%** | **33.33%** | **63.16%** | **El Breakeven duplicó el Win Rate en cortos (33% a 63%)**. |
| **Retorno % Acumulado** | +1.82% | **+1.20%** | +1.96% | **-0.17%** | Los cortos perdieron convexidad por salidas en Breakeven. |
| **Beneficio Bruto (USD)** | +$284.66 | **+$288.52** | +$306.08 | **+$53.60** | Los largos aportan estabilidad; los cortos se volvieron neutros. |

> **Hallazgo Fundamental de Asimetría:**  
> * **En los Longs:** El Breakeven funciona bien porque el drift secular alcista absorbe el ruido (Win Rate del 61.2%).  
> * **En los Shorts:** El Breakeven **asfixió la convexidad**. Los gaps bajistas tienen alta volatilidad intradía; el precio rebota bruscamente antes de desplomarse. Al poner un Breakeven rígido a $+0.75x \text{ ATR}$, el rebote saca la posición con $+0.01\text{ USD}$ justo antes de que se produzca la gran venta en pánico.

### 2.2. Esperanza Matemática por Trade ($E$)
*(Mark Minervini & Van Tharp)*

* **Esperanza v1.0:**
  $$E_{\text{v1.0}} = (0.4706 \times 0.521\%) - (0.5294 \times 0.322\%) = \mathbf{+0.075\% \text{ por trade}}$$
* **Esperanza v1.1:**
  $$E_{\text{v1.1}} = (0.6207 \times 0.146\%) - (0.3793 \times 0.207\%) = \mathbf{+0.012\% \text{ por trade}}$$

> Ambas versiones tienen **esperanza matemática positiva comprobada**. La v1.0 ofrece 6 veces mayor retorno esperado por trade debido al recorrido libre hasta el Time-Stop.

### 2.3. Consistencia Temporal
*(David Aronson & Perry Kaufman)*
* **v1.0 (10 Años):** 38 meses activos, **17 meses positivos (44.7%)**.
* **v1.1 (25 Años):** 68 meses activos, **37 meses positivos (54.4%)**.
* El Breakeven eleva la consistencia de meses positivos del 44.7% al **54.4%**.

---

## Módulo 3: Diagnóstico de Ejecución y Salidas (¿Cómo Optimizar?)

### 3.1. Diagnóstico del "Efecto Asfixia de Breakeven" (Breakeven Trap)
* En la v1.1 se registraron **35 operaciones ganadoras que cerraron ganando únicamente $+0.01\text{ USD}$**.
* **Causa:** El gatillo de disparo (`InpBreakevenTrigger = 0.75x ATR_M15`) y la distancia de bloqueo (`10 puntos = 0.10 pts en NQ`) colocaron el Stop demasiado cerca del ruido browniano de apertura.
* **Lección de la Masterclass (Notebook A02):** Para que el Breakeven no destruya el Payoff, el gatillo debe estar en **$+1.25x \text{ ATR M15}$** o ser un **Trailing Stop parabólico**, permitiendo que el trade respire durante las primeras 2 horas.

### 3.2. Tiempo de Permanencia (Holding Period Decay)
*(Toby Crabel)*
* **Tiempo Medio en Mercado v1.0:** **4 horas y 38 minutos** (conducido por el Time-Stop de 6.5h).
* **Tiempo Medio en Mercado v1.1:** **2 horas y 41 minutos** (acortado drásticamente por las 35 salidas anticipadas en Breakeven).
* **Conclusión:** El acortamiento del tiempo de permanencia redujo la exposición al mercado, pero a costa de abandonar prematuramente las mejores tendencias de la tarde.

### 3.3. Racha Máxima y Eficacia del Circuit Breaker
*(Richard Weissman & Alexander Elder)*
* **Racha Máxima Ganadora:** v1.0 = 5 trades | **v1.1 = 12 trades consecutivos ganadores** (gracias a los cierres en Breakeven).
* **Racha Máxima Perdedora:** v1.0 = 7 trades | **v1.1 = 4 trades** (el Circuit Breaker mensual cortó la acumulación de pérdidas).

---

## Veredicto Cuantitativo Institucional y Recomendación Final

1. **Si el objetivo es Máxima Rentabilidad y Payoff Asimétrico:**  
   **La Versión v1.0 es superior**, ya que deja que el desequilibrio de apertura se expanda durante toda la sesión regular, generando un Payoff de **1.62 a 1** y capturando **+3.77% de retorno neto**.
2. **Si el objetivo es Máxima Tasa de Acierto y Mínimo Drawdown Psicológico:**  
   **La Versión v1.1 es superior**, ya que eleva el Win Rate al **62% - 71%** y aplana el Drawdown a prácticamente cero ($30 USD), a costa de sacrificar ganancias masivas en los mejores días.
3. **La Síntesis Óptima (v1.2 Propuesta):**  
   Mantener el **Take Profit calibrado a 1.25x ATR D1** y el **Circuit Breaker mensual**, pero **desactivar el Breakeven rígido (`InpUseBreakeven = false`)** o elevar su disparo a **$+1.50x \text{ ATR M15}$**, logrando lo mejor de ambos mundos: **alta tasa de acierto sin asfixiar la cola derecha de beneficios**.
