# Metodologia Cuantitativa y Matematica

Este documento expone las bases matematicas, la literatura de referencia y los modelos de evaluacion estadistica incorporados en el **Quant Agentic Swarm**.

---

## 1. Filtro de Regimen de Volatilidad MTF (Lopez de Prado)

El regimen de mercado no se evalua en el marco temporal intradia donde abunda el ruido, sino en el **marco Diario ($D1$)**, extrayendo la dinamica de dispersion de mediano y corto plazo.

### A. Definicion del Diferencial de Volatilidad
Calculamos la diferencia entre el Average True Range de corto plazo ($5$ dias) y el de referencia ($14$ dias):

$$\Delta \text{ATR}_D = \text{ATR}_D(5) - \text{ATR}_D(14)$$

Donde $\text{ATR}_D(N)$ se calcula segun el metodo canonico de Wilder:
$$\text{TR}_t = \max \left( \text{High}_t - \text{Low}_t, |\text{High}_t - \text{Close}_{t-1}|, |\text{Low}_t - \text{Close}_{t-1}| \right)$$
$$\text{ATR}_{D,t}(N) = \frac{(N-1) \cdot \text{ATR}_{D,t-1}(N) + \text{TR}_t}{N}$$

### B. Estandarizacion por Z-Score
Normalizamos la aceleracion de volatilidad dividiendola por su dispersion estadistica en una ventana historica:

$$Z_{\text{vol}} = \frac{\Delta \text{ATR}_D - \mu(\Delta \text{ATR}_D, W)}{\sigma(\Delta \text{ATR}_D, W)}$$

Donde:
*   $\mu(\Delta \text{ATR}_D, W) = \frac{1}{W} \sum_{i=0}^{W-1} \Delta \text{ATR}_{D, t-i}$
*   $\sigma(\Delta \text{ATR}_D, W) = \sqrt{\frac{1}{W} \sum_{i=0}^{W-1} (\Delta \text{ATR}_{D, t-i} - \mu)^2}$
*   $W$: Ventana historica ($20$ dias como estandar base, evaluada sobre la muestra historica de $5$ a $10$ años).

### C. Clasificacion en Terciles Estadisticos
Bajo el supuesto de una distribucion normal estandar $Z \sim \mathcal{N}(0, 1)$, los cuantiles que dividen la distribucion en 3 areas simetricas de $33.3\%$ son $\pm \Phi^{-1}(0.667) \approx \pm 0.674$:

$$\text{Regimen}(\text{Volatilidad}) = \begin{cases} 
\text{BAJA (Compresion / Squeeze)} & \text{si } Z_{\text{vol}} < -0.67 \\
\text{MEDIA (Estacionaria / Normal)} & \text{si } -0.67 \le Z_{\text{vol}} \le +0.67 \\
\text{ALTA (Expansion / Breakout)} & \text{si } Z_{\text{vol}} > +0.67 
\end{cases}$$

---

## 2. El Metodo de Triple Barrera (Triple Barrier Method)

Inspirado en *Advances in Financial Machine Learning* (Marcos Lopez de Prado, 2018), cada posicion abierta cuenta con **tres barreras simultaneas** que definen su ciclo de vida, anclando el Take Profit a la volatilidad diaria de 14 periodos:

```
  Precio
    ▲
    │         ┌──────────────────────────────────────┐  Barrera 1: Take Profit Dinamico
    │         │                                      │  (Fijado a +k1 * ATR_D(14))
    │         │                                      │
    │  Entrada│                                      │
    ┼─────────┼──────────────────────────────────────┼──► Tiempo
    │         │                                      │
    │         │                                      │  Barrera 2: Stop Loss Estructural
    │         └──────────────────────────────────────┘  (Fijado a -k2 * ATR o invalidacion)
    │                                                │
    │                                                ▼
    │                                     Barrera 3: Limite Temporal (Time-Stop)
    │                                     (Si tras N barras no toco B1 ni B2, se liquida)
    └──────────────────────────────────────────────────────────────────────────────►
```

### Formulacion Matematica de las Barreras:
1.  **Barrera Superior ($B_1$ - Profit Target Dinamico basado en ATR Diario):**
    $$P_{\text{exit, long}} = P_{\text{entry}} + \left( k_1 \cdot \text{ATR}_D(14) \right)$$
    $$P_{\text{exit, short}} = P_{\text{entry}} - \left( k_1 \cdot \text{ATR}_D(14) \right)$$
    *Donde $\text{ATR}_D(14)$ se extrae del grafico Diario cerrado anterior ($D1$, shift 1) para evitar repainting.*
2.  **Barrera Inferior ($B_2$ - Stop de Invalidacion):**
    $$P_{\text{stop, long}} = P_{\text{entry}} - \left( k_2 \cdot \text{ATR}(14) \right)$$
    *(o nivel tecnico estructural de invalidacion, ej. $\text{Low}_{\text{Asian}}$)*.
3.  **Barrera Vertical ($B_3$ - Time-Stop):**
    $$t_{\text{exit}} = t_{\text{entry}} + (N_{\text{max\_bars}} \cdot \Delta t_{\text{bar}})$$
    Si $t \ge t_{\text{exit}}$ y la posicion no ha alcanzado ni $B_1$ ni $B_2$, se emite una orden a mercado de liquidacion inmediata por **muerte de la tesis temporal**.

---

## 3. Representatividad Temporal: Rango de 5 a 10 Años en D1

La robustez de una hipotesis depende de su capacidad de sobrevivir a multiples ciclos macroeconomicos:

*   **10 Años (~2,520 barras D1):** Horizonte ideal que cubre expansiones monetarias, subidas de tasas, shocks de liquidez y crisis geopoliticas.
*   **5 Años (~1,260 barras D1):** Umbral minimo para considerar que una anomalia no es fruto de la casualidad temporal.
*   **Muestra Reducida (< 5 Años):** El enjambre ejecuta el backtesting sin bloquear, pero añade una advertencia explicita en el HUD (`[MUESTRA REDUCIDA < 5 ANOS]`).

---

## 4. Bibliografia Canonica Integrada en el RAG

1. **Marcos Lopez de Prado (2018):** *Advances in Financial Machine Learning*, Wiley. (Triple Barrier Method, Market Regimes, Anti-Overfitting).
2. **Perry J. Kaufman (2013):** *Trading Systems and Methods (5th Ed)*, Wiley. (Volatility Ratio, Adaptive Moving Averages, Noise Filtering).
3. **Toby Crabel (1990):** *Day Trading with Short Term Price Patterns*, Traders Press. (Opening Range Breakout, Stretch Calculation).
4. **Ernest P. Chan (2013):** *Algorithmic Trading: Winning Strategies and Their Rationale*, Wiley. (Mean Reversion, Variance Ratio, Half-Life Decay).
5. **Larry Williams (1999):** *Long-Term Secrets to Short-Term Trading*, Wiley. (Range Expansion Cycles).
