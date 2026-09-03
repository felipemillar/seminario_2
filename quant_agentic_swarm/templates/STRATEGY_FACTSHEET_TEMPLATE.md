# Ficha Tecnica de Estrategia (Strategy Factsheet)
> **Strategy ID:** `STRAT-{{DATE}}-{{SETUP_NAME}}-{{TIMEFRAME}}-v{{VERSION}}`  
> **Timestamp de Generacion:** `{{TIMESTAMP}}`  
> **Estado:** `RESEARCH_PURE_CODE_CERTIFIED`  

---

## 1. Tesis Economica & Fundamento Cuantitativo

| Componente | Definicion Formal |
| :--- | :--- |
| **Condicion de Disparo ($X$)** | `{{CONDITION_X}}` |
| **Reaccion Esperada ($Y$)** | `{{EXPECTED_OUTCOME_Y}}` |
| **Causa Estructural ($Z$)** | `{{STRUCTURAL_REASON_Z}}` |
| **Criterio de Invalidacion** | `{{INVALIDATION_CRITERION}}` |

---

## 2. Citas y Respaldo Bibliografico (RAG 1)

*   **Autor Principal:** `{{AUTHOR_NAME}}`
*   **Libro / Paper de Referencia:** `{{BOOK_OR_PAPER_TITLE}}` (Capitulo `{{CHAPTER}}`, pag. `{{PAGES}}`).
*   **Concepto Canonico:** `{{CANONICAL_CONCEPT}}`

---

## 3. Especificacion Matematica Formal

### A. Condicion de Entrada
$$\text{Trigger} = {{LATEX_FORMULA_ENTRY}}$$

### B. Filtro de Regimen de Volatilidad MTF (Lopez de Prado)
$$\text{Diff}_D = \text{ATR}_D(5) - \text{ATR}_D(14)$$
$$Z_{\text{vol}} = \frac{\text{Diff}_D - \text{SMA}(\text{Diff}_D, 20)}{\text{StDev}(\text{Diff}_D, 20)}$$
*   *Condicion requerida para operar:* $Z_{\text{vol}} > +0.67$ (Regimen de Expansion).

### C. Sistema de Salidas: Triple Barrier Method
*   **Barrera 1 (Take Profit):** $+{{K1}} \times \text{ATR}_D(14)$ (Anclado a la volatilidad del grafico Diario cerrado anterior).
*   **Barrera 2 (Stop Loss):** $-{{K2}} \times \text{ATR}(14)$
*   **Barrera 3 (Limite Temporal):** Cierre a mercado tras `{{N_BARS}}` barras si no se alcanzaron $B_1$ o $B_2$.

---

## 4. Guia de Instalacion y Uso Rapido

### En TradingView (PineScript v5):
1. Abre TradingView y accede al panel inferior **"Editor Pine"**.
2. Copia y pega el codigo del archivo `{{PINE_FILENAME}}`.
3. Haz clic en **"Añadir al grafico"**.
4. Revisa la consola **"Pine Logs"** para auditar los disparos en tiempo real.

### En MetaTrader 5 (MQL5):
1. Abre MetaTrader 5 y presiona `F4` para abrir el **MetaEditor 5**.
2. Crea un nuevo Expert Advisor y pega el codigo de `{{MQL5_FILENAME}}`.
3. Presiona `F7` (**Compilar**) verificando `0 errors, 0 warnings`.
4. Arrastra el EA a tu grafico de `{{TIMEFRAME}}` y activa el boton **Algo Trading**.

---

## 5. Guia de Calibracion de Fricciones por Broker

| Parametro | Donde Ajustarlo en la Plataforma | Valor Recomendado |
| :--- | :--- | :--- |
| **Comision en TradingView** | `Propiedades de la Estrategia > Comision` | `$3.50 por Orden` |
| **Slippage en TradingView** | `Propiedades de la Estrategia > Deslizamiento` | `2 a 3 ticks` |
| **Spread en MT5 Tester** | `Strategy Tester > Configuracion > Spread` | `Current` o `8-12 points` |
| **Latencia en MT5 Tester** | `Strategy Tester > Configuracion > Delay` | `20-50 ms` |
