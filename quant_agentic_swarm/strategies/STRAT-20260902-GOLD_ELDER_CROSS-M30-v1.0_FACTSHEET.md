# Ficha Técnica de Estrategia (Strategy Factsheet)
> **Strategy ID:** `STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0`  
> **Timestamp de Generación:** `2026-09-02T20:30:00Z`  
> **Estado:** `RESEARCH_PURE_CODE_CERTIFIED`  
> **Autor Institucional:** `QRT Solutions`

---

## 1. Tesis Económica & Fundamento Cuantitativo

| Componente | Definición Formal |
| :--- | :--- |
| **Condición de Disparo ($X$)** | En vela cerrada de M30, cruce de EMA 9 sobre EMA 21 (o bajo ella para cortos), condicionado a que el precio de cierre esté estrictamente alineado con la EMA 200 en M30 con pendiente no contraria ($\text{Close} > \text{EMA}_{200} \land \Delta\text{EMA}_{200} \ge 0$ para compras; $\text{Close} < \text{EMA}_{200} \land \Delta\text{EMA}_{200} \le 0$ para ventas). |
| **Reacción Esperada ($Y$)** | Desplazamiento tendencial asimétrico en la dirección macro del oro (XAUUSD), capturando expansiones de momentum con ratio riesgo/beneficio $\ge 2.0$ y filtrando más del 50% de los falsos quiebres de rango (*whipsaws*). |
| **Causa Estructural ($Z$)** | Flujo institucional macroeconómico pasivo y de cobertura en metales preciosos (bancos centrales y fondos soberanos). Los retrocesos intradía hacia el valor medio (EMA 200) ofrecen una asimetría estadística positiva cuando el impulso de corto plazo (EMA 9/21) reanuda la marea dominante (Alexander Elder - Triple Screen). |
| **Criterio de Invalidación** | Cierre de vela M30 que cruce y vulnere la EMA 200 en sentido opuesto, o activación de la Barrera 2 de Stop Loss anclada a volatilidad diaria. |

---

## 2. Citas y Respaldo Bibliográfico (RAG 1)

* **Autor Principal:** Alexander Elder / Perry J. Kaufman / Marcos López de Prado.
* **Libros de Referencia:** 
  - *The New Trading for a Living* (Alexander Elder, Cap. 9: Sistema de Triple Pantalla).
  - *Trading Systems and Methods* (Perry J. Kaufman, Cap. 8: Trend Identification & Moving Average Filters).
  - *Advances in Financial Machine Learning* (Marcos López de Prado, Cap. 3: Triple Barrier Method).
* **Concepto Canónico:** Filtro de tendencia macro de orden superior + disparo de momentum de corto plazo + Triple Barrera anclada a volatilidad diaria.

---

## 3. Especificación Matemática Formal

### A. Condición de Entrada
$$\text{Trigger}_{\text{Long}} = \text{EMA}_9[1] > \text{EMA}_{21}[1] \;\land\; \text{EMA}_9[2] \le \text{EMA}_{21}[2] \;\land\; C_{M30}[1] > \text{EMA}_{200}[1] \;\land\; \text{EMA}_{200}[1] \ge \text{EMA}_{200}[2]$$
$$\text{Trigger}_{\text{Short}} = \text{EMA}_9[1] < \text{EMA}_{21}[1] \;\land\; \text{EMA}_9[2] \ge \text{EMA}_{21}[2] \;\land\; C_{M30}[1] < \text{EMA}_{200}[1] \;\land\; \text{EMA}_{200}[1] \le \text{EMA}_{200}[2]$$

### B. Filtro de Régimen de Volatilidad MTF (López de Prado)
$$\text{Diff}_D = \text{ATR}_D(5) - \text{ATR}_D(14)$$
$$Z_{\text{vol}} = \frac{\text{Diff}_D - \text{SMA}(\text{Diff}_D, 20)}{\text{StDev}(\text{Diff}_D, 20)}$$
* *Condición requerida:* $Z_{\text{vol}} \ge -0.67$ (excluye régimen de compresión extrema).

### C. Sistema de Salidas: Triple Barrier Method
* **Barrera 1 (Take Profit):** $+1.5 \times \text{ATR}_D(14)_{[1]}$ (anclado al gráfico diario cerrado previo).
* **Barrera 2 (Stop Loss):** $-0.75 \times \text{ATR}_D(14)_{[1]}$ (Ratio Riesgo/Beneficio asimétrico 2.0 : 1).
* **Barrera 3 (Límite Temporal):** Cierre a mercado tras 32 barras M30 (16 horas de mercado).

---

## 4. Archivos Entregables

1. **Especificación JSON:** [`STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0_specification.json`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/strategies/STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0_specification.json)
2. **Pine Script v6 (TradingView):** [`STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0.pine`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/strategies/STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0.pine)
3. **MQL5 POO (MetaTrader 5):** [`STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0.mq5`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/strategies/STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0.mq5)
4. **Binario Compilado (.ex5):** [`STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0.ex5`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/strategies/STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0.ex5)

---

## 5. Guía de Ejecución Rápida en MetaTrader 5

1. En MT5, el Asesor Experto ya está disponible en el Navegador bajo `Expertos/STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0`.
2. En el **Strategy Tester**:
   - Símbolo: `XAUUSD`
   - Temporalidad: `M30`
   - Depósito: `10000 USD`
   - Modelado: `Every tick`
   - Parámetros por defecto: Lote `0.01`, TP `1.5x ATR D1`, SL `0.75x ATR D1`.
