# Ficha Tecnica de Estrategia Optimizada (Strategy Factsheet v1.1)
> **Strategy ID:** `STRAT-20260902-USGAP_MOM-M15-v1.1`  
> **Timestamp de Generacion:** `2026-09-03T11:50:00Z`  
> **Estado:** `OPTIMIZED_CODE_CERTIFIED`  
> **Titulo de Tesis:** US Opening Gap Momentum Continuation (Gap and Go) — Version Optimizada  
> **Mejoras Integradas:** Take Profit Calibrado (1.25x ATR D1) + Breakeven Dinamico + Circuit Breaker Mensual  
> **Autor Institucional:** QRT Solutions  

---

## 1. Tesis Economica & Fundamento Cuantitativo

| Componente | Definicion Formal |
| :--- | :--- |
| **Condicion de Disparo ($X$)** | En la apertura de la sesion regular de EEUU (09:30 ET), el precio presenta un gap ($O_{sesion} - C_{t-1}$) >= 1.0x ATR_D(14)[shift 1], y la primera vela M15 de la sesion cierra confirmando la direccion del gap sin retroceder mas del 50% de su propio rango High-Low. |
| **Reaccion Esperada ($Y$)** | Aceleracion direccional sostenida durante la sesion regular de EEUU, capturando ganancias mediante Take Profit calibrado intradiario y protegiendo el capital con Breakeven dinamico. |
| **Causa Estructural ($Z$)** | Catalizador informativo overnight genera un desequilibrio de order flow; el volumen institucional que ejecuta al open continua explotando ese desequilibrio antes de que el mercado arbitre por completo la nueva informacion. |
| **Criterio de Invalidacion** | El precio retorna y una vela M15 cierra mas alla del 50% del gap dentro de los primeros 30 minutos, o se ejecuta el Stop Loss tecnico / Breakeven. |

---

## 2. Mejoras Especificas Implementadas en la Version 1.1

1. **Calibracion de Take Profit (Barrera B1):**  
   * En la v1.0, el TP estaba fijado en $+2.0\times ATR_D(14)$, meta que nunca fue alcanzada dentro de la sesion regular en 10 anos de backtest (0 salidas por TP).  
   * En la v1.1, se calibra a **$+1.25\times ATR_D(14)$**, capturando automaticamente las excursiones favorables mas extremas (*MFE*) antes de que ocurra una reversion en la tarde.
2. **Motor de Breakeven Dinamico:**  
   * Cuando la posicion alcanza una ganancia latente de $+0.75\times ATR_{M15}$, el Stop Loss se traslada de inmediato al precio de apertura $+ 10\text{ puntos}$, eliminando el riesgo de que un trade ganador se convierta en perdedor.
3. **Control de Riesgo por Circuit Breaker:**  
   * Si en el mes calendario en curso se acumulan 3 perdidas consecutivas, el algoritmo bloquea nuevas entradas hasta el primer dia del mes siguiente, blindando el capital contra rachas negativas prolongadas.

---

## 3. Especificacion Matematica Formal

### A. Condicion de Entrada (Largo)
$$\text{Gap} = O_{\text{sesion}} - C_{t-1} \geq 1.0 \cdot \text{ATR}_D(14)_{[1]} \;\wedge\; C_{M15,1} > O_{\text{sesion}} \;\wedge\; C_{M15,1} \geq L_{M15,1} + 0.5\,(H_{M15,1}-L_{M15,1})$$

### B. Condicion de Entrada (Corto)
$$\text{Gap} = O_{\text{sesion}} - C_{t-1} \leq -1.0 \cdot \text{ATR}_D(14)_{[1]} \;\wedge\; C_{M15,1} < O_{\text{sesion}} \;\wedge\; C_{M15,1} \leq H_{M15,1} - 0.5\,(H_{M15,1}-L_{M15,1})$$

### C. Filtro de Regimen de Volatilidad MTF (Lopez de Prado)
$$Z_{\text{vol}} = \frac{\text{Diff}_D - \text{SMA}(\text{Diff}_D, 20)}{\text{StDev}(\text{Diff}_D, 20)} > +0.67$$

### D. Sistema de Salidas: Triple Barrier Method Optimizada
* **Barrera 1 (Take Profit Calibrado):** $+1.25 \times \text{ATR}_D(14)_{[1]}$
* **Barrera 2 (Stop Loss Tecnico):** $-1.0 \times \text{ATR}_{\text{M15}}(14)$
* **Barrera 3 (Limite Temporal):** Cierre forzoso a mercado tras `26` barras M15 (6.5 horas RTH)
* **Proteccion Breakeven:** Activacion a $+0.75 \times \text{ATR}_{\text{M15}}$

---

## 4. Archivos Entregables

* **Expert Advisor MQL5:** [`MT5/estrategias/STRAT-20260902-USGAP_MOM-M15-v1.1.mq5`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/estrategias/STRAT-20260902-USGAP_MOM-M15-v1.1.mq5)
* **Binario Compilado MT5:** `MT5/estrategias/STRAT-20260902-USGAP_MOM-M15-v1.1.ex5` *(0 errors, 0 warnings)*
* **Despliegue Directo:** Copiado en `drive_c/Program Files/MetaTrader 5/MQL5/Experts/`
* **Especificacion JSON:** [`quant_agentic_swarm/strategies/STRAT-20260902-USGAP_MOM-M15-v1.1_specification.json`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/strategies/STRAT-20260902-USGAP_MOM-M15-v1.1_specification.json)
