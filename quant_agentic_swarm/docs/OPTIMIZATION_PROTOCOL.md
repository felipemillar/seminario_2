# Manual Canónico: Protocolo Institucional de Optimización Cuantitativa

> **Autor Canónico:** QRT Solutions  
> **Ámbito:** Repositorio Maestro `seminario_2` & Quant Agentic Swarm  
> **Estado:** Fuente autoritativa y vinculante para cualquier Agente de IA y Estratega Cuantitativo.  
> **Fundamento Metodológico:** Masterclass de Diseño Cuantitativo (`masterclass/notebooks/A01-A03`), Robert Pardo, Marcos López de Prado, John Sweeney, Toby Crabel, Perry Kaufman, Alexander Elder y Van Tharp.

---

## 1. Declaración de Principios y Prohibición de Sobreajuste (Anti-Overfitting Manifesto)

El principal peligro en el diseño de estrategias algorítmicas es el **sobreajuste estadístico (*overfitting*)**: encontrar una combinación de parámetros que funcionó de forma espectacular en el pasado únicamente por azar o ruido de mercado, pero que colapsa inmediatamente al operar con capital real.

### Reglas Inmutables del Agente:
1. **PROHIBIDO:** Seleccionar parámetros basándose en "el mejor Sharpe" o "el máximo beneficio neto" si este corresponde a un pico aislado (*spike*) rodeado de combinaciones mediocres o perdedoras.
2. **PROHIBIDO:** Optimizar parámetros en la muestra completa sin reservar un período estricto fuera de muestra (*Out-of-Sample*).
3. **PROHIBIDO:** Optimizar utilizando valores absolutos en puntos o ticks fijos. Toda calibración de salidas y filtros debe formularse en **múltiplos normalizados de volatilidad (ATR)** para asegurar la invarianza de escala temporal.

---

## 2. Los 5 Pilares Obligatorios del Protocolo de Optimización

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ FLUJO SECUENCIAL DE OPTIMIZACIÓN CUANTITATIVA                                          │
│                                                                                        │
│  1. Causa Estructural Ex-Ante (Z)                                                      │
│        ▼                                                                               │
│  2. Calibración Empírica por Excursiones (MAE / MFE)                                   │
│        ▼                                                                               │
│  3. Barrido Bidimensional Grid Search (SL × TP en unidades ATR)                        │
│        ▼                                                                               │
│  4. Selección por Baricentro de Meseta de Robustez (Robustness Plateau)                │
│        ▼                                                                               │
│  5. Validación Cruzada In-Sample vs Out-of-Sample + Semáforo de Degradación            │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Pilar 1: Causa Estructural Ex-Ante y Calibración de Salidas (MAE / MFE)
*(John Sweeney & Toby Crabel)*

Antes de optimizar cualquier número, el estratega debe declarar el mecanismo causal económico (*Test de la Frase Única*):
$$\boxed{\text{"Cuando pasa } X\text{, espero que el precio haga } Y\text{, porque } Z\text{."}}$$

#### Calibración Empírica de Salidas mediante Excursiones:
En lugar de fijar valores arbitrarios, el espacio de búsqueda se acota analizando la distribución empírica de las operaciones del activo:

1. **Maximum Adverse Excursion (MAE):**
   * Se calcula el retroceso máximo adverso de todas las operaciones históricas.
   * **Regla del Percentil 90:** El Stop Loss inicial se ancla en el percentil 90 del MAE de los trades ganadores ($P_{90}(\text{MAE}_{\text{wins}})$). Si un trade excede este nivel en contra, la probabilidad de recuperación estadística es inferior al 12%, haciendo ineficiente mantener la posición abierta.
2. **Maximum Favorable Excursion (MFE):**
   * Se analiza la densidad de probabilidad Kernel del avance máximo a favor.
   * El Take Profit se fija en la **mediana o moda de la masa de probabilidad de MFE**. Fijar targets alejados en la cola derecha deja desprotegidas las ganancias antes del retroceso de la sesión.

---

### Pilar 2: Barrido de Cuadrícula (Grid Search) en Unidades de ATR
*(Robert Pardo)*

La exploración de parámetros se ejecuta mediante un barrido bidimensional exhaustivo pero disciplinado sobre múltiplos de volatilidad:

$$\text{Espacio de Búsqueda:} \quad \begin{cases} 
\text{SL} \in [0.3, 2.5] \times \text{ATR}, & \Delta_{\text{SL}} = 0.1 \times \text{ATR} \\
\text{TP} \in [0.3, 3.5] \times \text{ATR}, & \Delta_{\text{TP}} = 0.1 \times \text{ATR}
\end{cases}$$

#### Matriz de Evaluación:
Para cada celda $(i, j)$ de la cuadrícula se calcula:
* **Sharpe Ratio Anualizado:** $S = \frac{\mu_R}{\sigma_R} \times \sqrt{252}$
* **Profit Factor (%):** $\text{PF} = \frac{\sum R_{\text{positivos}}}{\sum |R_{\text{negativos}}|}$
* **Win Rate (%):** $\text{WR} = \frac{N_{\text{ganadores}}}{N_{\text{totales}}} \times 100$
* **Drawdown Máximo (% de precio):** $\text{MaxDD} = \max(Peak - Equity)$

---

### Pilar 3: Criterio de Selección por Baricentro de Meseta de Robustez
*(Robert Pardo & Perry Kaufman)*

La selección del par óptimo $(\text{SL}^*, \text{TP}^*)$ **NUNCA** se realiza buscando el punto con el máximo absoluto de Sharpe en la cuadrícula.

#### Criterio del Baricentro:
1. **Definición de Meseta Establé:** Se identifican las regiones contiguas de la cuadrícula donde:
   $$S_{i,j} \ge 0.80 \times S_{\max} \quad \text{y} \quad \text{PF}_{i,j} \ge 1.25$$
2. **Rechazo de Picos Aislados (*Spikes*):** Si una celda tiene un Sharpe elevado pero sus vecinas inmediatas caen más de un 40%, se descarta automáticamente como sobreajuste (*overfitting*).
3. **Punto Óptimo Institucional:** Se selecciona el **centro geométrico (baricentro)** de la meseta más amplia y continua:
   $$\text{SL}^* = \text{Mediana}(\text{SL}_{\text{meseta}}), \quad \text{TP}^* = \text{Mediana}(\text{TP}_{\text{meseta}})$$
   *Garantía:* Pequeños cambios en la volatilidad futura del mercado mantendrán al sistema dentro de la zona de rentabilidad positiva.

---

### Pilar 4: Validación Temporal Cruzada In-Sample vs Out-of-Sample
*(Marcos López de Prado)*

Todo proceso de optimización debe someterse a una partición temporal estricta y sin fuga de información (*data leakage*):

* **Conjunto In-Sample (IS - Entrenamiento):** Datos históricos empleados para calibrar la meseta (ej. 2000 a 2018).
* **Conjunto Out-of-Sample (OOS - Validación Ciega):** Período reciente que el algoritmo jamás ha observado durante el diseño (ej. 2019 a 2026).

#### Coeficiente de Degradación Paramétrica:
$$\text{Degradación} = \frac{|\text{Métrica}_{\text{IS}} - \text{Métrica}_{\text{OOS}}|}{\text{Métrica}_{\text{IS}}} \times 100$$

#### Semáforo Cuantitativo de Validación Obligatorio:

| Métrica Auditada | Umbral Verde (Robusto) | Umbral Amarillo (Precaución) | Umbral Rojo (Rechazo / Sobreajustado) |
| :--- | :---: | :---: | :---: |
| **Sharpe Ratio** | Degradación $\le 30\%$ | $30\% < \text{Degradación} \le 50\%$ | Degradación $> 50\%$ o $S_{\text{OOS}} < 0.50$ |
| **Profit Factor** | $\text{PF}_{\text{OOS}} \ge 1.25$ | $1.10 \le \text{PF}_{\text{OOS}} < 1.25$ | $\text{PF}_{\text{OOS}} < 1.10$ |
| **Tasa de Acierto (WR)** | Variación $\le 15\%$ | $15\% < \text{Variación} \le 25\%$ | Caída $> 25\%$ respecto a IS |
| **Drawdown Máximo** | $\text{MaxDD}_{\text{OOS}} \le 1.5 \times \text{IS}$ | $1.5x < \text{MaxDD}_{\text{OOS}} \le 2.0x$ | $\text{MaxDD}_{\text{OOS}} > 2.0 \times \text{IS}$ |

> **Regla de Rechazo:** Si el sistema activa cualquier condición en **Umbral Rojo**, la hipótesis se declara nula o sobreajustada y no se autoriza su despliegue ni codificación en MQL5 o Pine Script.

---

### Pilar 5: Gestión Dinámica de Asimetrías (Breakeven & Circuit Breakers)
*(Alexander Elder, Toby Crabel & Van Tharp)*

Para que una estrategia optimizada sea ejecutable en cuentas institucionales, debe complementar sus parámetros fijos con dos mecanismos dinámicos de protección de capital:

1. **Protección de Breakeven Elástico:**
   * **Gatillo de Activación:** Debe ubicarse más allá del ruido de retesteo matutino ($+0.75x$ a $+1.25x \text{ ATR}$).
   * **Bloqueo de Ganancia:** Mueve el Stop Loss al precio de entrada más un margen de cobertura de comisiones y spread (+10 puntos en futuros / índices).
   * **Advertencia de Microestructura:** Nunca fijar un Breakeven excesivamente ceñido en activos con alta volatilidad inicial, ya que produce el fenómeno de *Breakeven Trap* (asfixia prematura de trades ganadores).
2. **Circuit Breaker Temporal / Mensual:**
   * Conteo de pérdidas continuas en la ventana de tiempo del activo.
   * **Límite Canónico:** Bloqueo preventivo de nuevas operaciones tras acumular **3 pérdidas consecutivas** en el mes calendario.
   * *Objetivo:* Evitar que rachas desfavorables en transiciones macroeconómicas erosionen el capital antes de que el mercado retome su régimen causal normal.

---

## 3. Checklist Obligatorio Antes de Guardar una Versión Optimizada

Cualquier propuesta de optimización debe acompañarse de este checklist en la documentación y en la bitácora:

- [ ] ¿El Stop Loss y Take Profit están expresados en múltiplos limpios de ATR?
- [ ] ¿Se verificó que los parámetros provienen del centro de una meseta plana y no de un pico aislado?
- [ ] ¿Se realizó la partición In-Sample / Out-of-Sample sin contaminación de datos?
- [ ] ¿El semáforo de degradación del Sharpe Ratio se encuentra en zona verde ($\le 30\%$)?
- [ ] ¿Se evaluó el impacto direccional por separado (Longs vs Shorts)?
- [ ] ¿Se auditó el tiempo medio de permanencia en mercado (*holding period*) para evitar sobre-exposición?
