# Ficha Tecnica de Estrategia (Strategy Factsheet)
> **Strategy ID:** `STRAT-20260902-USGAP_MOM-M15-v1.0`
> **Timestamp de Generacion:** `2026-09-02T19:37:17Z`
> **Estado:** `RESEARCH_PURE_CODE_CERTIFIED`
> **Titulo de Tesis:** US Opening Gap Momentum Continuation (Gap and Go)
> **Variante Origen:** Ficha Tecnica A (Momentum Directo) — Aprobada por el Trader

---

## 1. Tesis Economica & Fundamento Cuantitativo

| Componente | Definicion Formal |
| :--- | :--- |
| **Condicion de Disparo ($X$)** | En la apertura de la sesion regular de EEUU (09:30 ET), el precio presenta un gap ($O_{sesion} - C_{t-1}$) >= 1.0x ATR_D(14)[shift 1], y la primera vela M15 de la sesion cierra confirmando la direccion del gap sin retroceder mas del 50% de su propio rango High-Low. |
| **Reaccion Esperada ($Y$)** | Aceleracion direccional sostenida durante la sesion regular de EEUU, extendiendo el rango de precio en la direccion del gap. |
| **Causa Estructural ($Z$)** | Catalizador informativo overnight (earnings, datos macro, noticias) genera un desequilibrio de order flow; el volumen institucional que ejecuta al open continua explotando ese desequilibrio (barrido de liquidez direccional) antes de que el mercado arbitre por completo la nueva informacion. |
| **Criterio de Invalidacion** | El precio retorna y una vela M15 cierra mas alla del 50% del gap dentro de las dos primeras velas M15 de la sesion (primeros 30 minutos). |

---

## 2. Citas y Respaldo Bibliografico (RAG 1)

*   **Autor Principal:** Toby Crabel / Marcos Lopez de Prado
*   **Libro / Paper de Referencia:** *Day Trading with Short Term Price Patterns* (Crabel, 1990) — calculo de Stretch/Opening Range aplicado a gaps de apertura; *Advances in Financial Machine Learning* (Lopez de Prado, 2018) — Filtro de Regimen de Volatilidad Diaria (Z-Score) y Triple Barrier Method.
*   **Concepto Canonico:** Continuacion de momentum tras ruptura/gap de apertura, condicionada a un regimen de volatilidad en expansion (evita operar la tesis en regimenes de compresion o estacionarios, donde el fade es estadisticamente mas probable).

---

## 3. Especificacion Matematica Formal

### A. Condicion de Entrada (Largo)
$$\text{Gap} = O_{\text{sesion}} - C_{t-1} \geq k_{gap} \cdot \text{ATR}_D(14)_{[1]} \;\wedge\; C_{M15,1} > O_{\text{sesion}} \;\wedge\; C_{M15,1} \geq L_{M15,1} + 0.5\,(H_{M15,1}-L_{M15,1})$$

### A'. Condicion de Entrada (Corto, simetrica)
$$\text{Gap} = O_{\text{sesion}} - C_{t-1} \leq -k_{gap} \cdot \text{ATR}_D(14)_{[1]} \;\wedge\; C_{M15,1} < O_{\text{sesion}} \;\wedge\; C_{M15,1} \leq H_{M15,1} - 0.5\,(H_{M15,1}-L_{M15,1})$$

### B. Filtro de Regimen de Volatilidad MTF (Lopez de Prado)
$$\text{Diff}_D = \text{ATR}_D(5) - \text{ATR}_D(14)$$
$$Z_{\text{vol}} = \frac{\text{Diff}_D - \text{SMA}(\text{Diff}_D, 20)}{\text{StDev}(\text{Diff}_D, 20)}$$
*   *Condicion requerida para operar:* $Z_{\text{vol}} > +0.67$ (Regimen de Expansion).

### C. Sistema de Salidas: Triple Barrier Method
*   **Barrera 1 (Take Profit):** $+2.0 \times \text{ATR}_D(14)$ (Anclado a la volatilidad del grafico Diario cerrado anterior).
*   **Barrera 2 (Stop Loss):** $-1.0 \times \text{ATR}_{\text{Intradia}}(14)$
*   **Barrera 3 (Limite Temporal):** Cierre a mercado tras `26` barras M15 (~6.5 horas, equivalente a una sesion regular completa) si no se alcanzaron $B_1$ o $B_2$.

---

## 4. Guia de Instalacion y Uso Rapido

### En TradingView (PineScript v5):
1. Abre TradingView en un simbolo US (ej. SPY, QQQ, AAPL, ES1!) en marco **M15**.
2. **Configura el grafico en "Regular Trading Hours" (RTH)** — Ajustes del grafico > Sesion. Esto es obligatorio: la deteccion de gap depende de que el `open` de sesion coincida con la apertura oficial 09:30 ET.
3. Abre el panel inferior **"Editor Pine"**, copia y pega el codigo de `STRAT-20260902-USGAP_MOM-M15-v1.0.pine`.
4. Haz clic en **"Añadir al grafico"**.
5. Revisa la consola **"Pine Logs"** para auditar los disparos (`ENTRY_BUY`, `ENTRY_SELL`, `EXIT_B1_TP_D1`, `EXIT_B2_SL`, `EXIT_B3_TIME`) en tiempo real.

### En MetaTrader 5 (MQL5):
1. Abre MetaTrader 5 y presiona `F4` para abrir el **MetaEditor 5**.
2. Crea un nuevo Expert Advisor y pega el codigo de `STRAT-20260902-USGAP_MOM-M15-v1.0.mq5`.
3. Presiona `F7` (**Compilar**) verificando `0 errors, 0 warnings`.
4. **CALIBRA `InpSessionStartHour` / `InpSessionStartMin`** a la hora de servidor de tu broker equivalente a 09:30 ET (ej. si tu broker opera en GMT+2/GMT+3, sera 16:30 o 17:30 segun horario de verano — confirmalo con soporte de tu broker). Esto es critico: el EA solo evalua el gap en la vela M15 cuya hora coincide exactamente con este input.
5. Arrastra el EA a tu grafico M15 y activa el boton **Algo Trading**.

---

## 5. Guia de Calibracion de Fricciones por Broker

| Parametro | Donde Ajustarlo en la Plataforma | Valor Recomendado |
| :--- | :--- | :--- |
| **Comision en TradingView** | `Propiedades de la Estrategia > Comision` | `$3.50 por Orden` |
| **Slippage en TradingView** | `Propiedades de la Estrategia > Deslizamiento` | `2 a 3 ticks` |
| **Spread en MT5 Tester** | `Strategy Tester > Configuracion > Spread` | `Current` o `8-12 points` |
| **Latencia en MT5 Tester** | `Strategy Tester > Configuracion > Delay` | `20-50 ms` |
| **Hora de Sesion MT5** | `Inputs del EA > InpSessionStartHour/Min` | Calibrar a 09:30 ET segun huso horario del broker |

---

## 6. Notas de Diseño y Supuestos Asumidos por el Orquestador

Estos parametros fueron fijados como punto de partida razonable (Fase 2) y **quedan abiertos a ajuste** por el trader:

*   `k_gap = 1.0` — el gap debe ser al menos 1x el ATR Diario(14) para considerarse significativo (filtra "common gaps" de ruido).
*   `max_retrace = 0.5` — la vela de confirmacion no debe cerrar en la mitad "equivocada" de su propio rango.
*   `k1 (Take Profit) = 2.0x ATR_D(14)` / `k2 (Stop Loss) = 1.0x ATR Intradia` → ratio Riesgo:Beneficio aproximado de 1:2 (antes de friccion).
*   `k3 (Time-Stop) = 26 barras M15` ≈ duracion de la sesion regular completa (6.5h): si la tesis de continuacion no se materializo en todo el dia, se liquida por "muerte de la tesis temporal".
*   Universo sugerido para pruebas: ETFs/indices US de alta liquidez (SPY, QQQ, DIA) y futuros (ES1!, NQ1!); tambien aplicable a acciones individuales liquidas.

## 7. Pureza de Investigacion

`live_execution_filters_omitted: true` — El codigo NO incluye bloqueos de spread, proteccion de gaps de fin de semana ni filtros de noticias. La hipotesis se evalua en su estado matematico puro para el backtesting, tal como exige el protocolo QAS.
