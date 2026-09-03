# Reporte Maestro: Pool Completo de Diagnóstico de Backtesting en Nasdaq

> **Autor Institucional:** QRT Solutions  
> **Activo y Timeframe:** `CUSTOM_NQ_M5` en **M30** (31,376 barras evaluadas)  
> **Estrategia:** `EASimple_CruceMedias.ex5` (EMA 9 vs EMA 21)  
> **Período Histórico:** 02 de Enero de 2024 al 07 de Agosto de 2026 (32 meses / 2.6 años)  
> **Muestreo Total:** 1,239 operaciones round-turn (2,478 deals de mercado)

---

## 1. Módulo 1: La Evaluación Dual Obligatoria (Monetaria vs Porcentual Pura)

| Métrica Cuantitativa | Capa Monetaria (USD) | Capa Porcentual Pura (% Precio) | Interpretación Operativa |
| :--- | :--- | :--- | :--- |
| **Rendimiento Neto** | **+$2,000.10 USD** | **+8.96% Acum. (+4.19% Compuesto)** | Sistema con ventaja neta pero penalizado por el lado corto. |
| **Profit Factor (PF)** | **1.03** | **1.03** | Marginalmente rentable en configuración simétrica bruta. |
| **Tasa de Acierto (Win Rate)** | **29.62%** (367 Ganadores / 872 Perdedores) | **29.62%** | Comportamiento estándar de un seguidor de tendencia clásico. |
| **Ganancia Media por Trade** | **+$212.04 USD** | **+0.902%** | Captura de impulsos sostenidos en velas de tendencia. |
| **Pérdida Media por Trade** | **-$86.95 USD** | **-0.369%** | Corte ágil de pérdidas ante cruces fallidos. |
| **Payoff Ratio (Riesgo/Beneficio)** | **2.44 a 1** | **2.44 a 1** | Excelente: la ganancia media es 2.44 veces la pérdida media. |
| **Mayor Trade Ganador** | +$1,960.00 USD | **+9.56%** | Rally alcista ininterrumpido de varios días. |
| **Mayor Trade Perdedor** | -$720.00 USD | **-3.55%** | Falso quiebre con gap en apertura. |
| **Máximo Drawdown de Curva** | -$5,430.00 USD | **-27.14%** | Ocurrido en fases prolongadas de consolidación lateral. |

---

## 2. Módulo 2: Diagnóstico de Asimetrías (¿Dónde está el Edge?)

### 2.1. Desglose Direccional Mandatorio (Longs vs Shorts)
*Fundamento: Alexander Elder (Triple Pantalla) y Perry Kaufman.*

| Métrica | Compras (LONGS - 620 Trades) | Ventas (SHORTS - 619 Trades) | Diagnóstico Crítico |
| :--- | :---: | :---: | :--- |
| **PnL Neto Monetario** | **+$6,178.75 USD** | **-$4,178.65 USD** | Los shorts devoran el **67.6%** de la ganancia total. |
| **Retorno Porcentual Puro** | **+28.27% Acumulado** | **-19.31% Acumulado** | **El Edge reside 100% en las compras**. |
| **Retorno Compuesto** | **+29.43%** | **-19.50%** | Capitalización asimétrica masiva en compras. |
| **Profit Factor** | **1.18** | **0.88** | Compras viables; Ventas destructivas. |
| **Win Rate** | **32.90%** | **26.33%** | Deriva alcista secular castiga severamente los cortos. |
| **Máximo Drawdown** | **-10.95%** | **-34.27%** | El drawdown global del 27% proviene de los cortos. |

### 2.2. Esperanza Matemática por Trade (Expectancy / $E$)
*Fundamento: Mark Minervini (Think & Trade Like a Champion, Cap. 4).*

$$E = (\text{Win Rate} \times \text{Avg Win \%}) - (\text{Loss Rate} \times \text{Avg Loss \%})$$

* **Expectativa Global:** **$+0.0072\%$ por trade** ($E_R = +0.02$).
* **Expectativa en Compras (Longs):** **$+0.0456\%$ por trade** ($E_R = +0.12$). Multiplica por **6.3 veces** la expectativa global.
* **Expectativa en Ventas (Shorts):** **$-0.0312\%$ por trade** ($E_R = -0.09$). Expectativa negativa matemáticamente garantizada.

### 2.3. Consistencia Temporal (% Meses Rentables)
*Fundamento: David Aronson (Evidence-Based Technical Analysis).*

* **Total de Meses Evaluados:** 32 meses (Enero 2024 a Agosto 2026).
* **Meses Positivos:** **16 meses (50.0%)** | Meses Negativos: 16 meses (50.0%).
* **Top 3 Mejores Meses:**
  1. `2025.01`: +7.75% (+$1,780 USD en 34 trades)
  2. `2026.03`: +7.40% (+$1,811 USD en 33 trades)
  3. `2025.04`: +7.00% (+$1,306 USD en 44 trades)
* **Peores 3 Meses:**
  1. `2024.09`: -17.37% (-$3,731 USD en 46 trades) -> Mes de fuerte lateralidad.
  2. `2025.05`: -11.64% (-$2,524 USD en 48 trades).
  3. `2025.07`: -4.96% (-$1,192 USD en 53 trades).

---

## 3. Módulo 3: Diagnóstico de Ejecución, Tiempos y Salidas

### 3.1. Tiempo de Permanencia (Barras en Posición / Time-Stop)
*Fundamento: Toby Crabel (Short Term Price Patterns).*

* **Duración Promedio en Trades Ganadores:** **78.3 barras M30** (~39.2 horas / 1.6 días).
* **Duración Promedio en Trades Perdedores:** **19.2 barras M30** (~9.6 horas).
* **Hallazgo:**  
  El cruce de medias actúa como un excelente filtro de corte rápido para operaciones perdedoras (cerrando en menos de 20 barras), permitiendo que los trades ganadores permanezcan abiertos casi **4 veces más tiempo** (78 barras) para capturar la tendencia.

### 3.2. Racha Máxima de Pérdidas y Riesgo de Ruina
*Fundamento: Richard Weissman (Mechanical Trading Systems) y Alexander Elder (Regla del 6%).*

* **Racha Máxima de Pérdidas Consecutivas Global:** **18 pérdidas seguidas**.
* **Racha Máxima en Ventas (Shorts):** **15 pérdidas seguidas**.
* **Racha Máxima en Compras (Longs):** **13 pérdidas seguidas**.
* **Racha Máxima de Ganancias Consecutivas:** 5 ganancias seguidas (Longs: 6).
* **Hallazgo & Calibración de Riesgo:**  
  Con un Win Rate del ~30%, una racha de 18 pérdidas es matemáticamente coherente.  
  * Si se arriesga el 2% por trade: Drawdown en racha = $-36\%$.
  * Si se arriesga el 0.5% por trade: Drawdown en racha = $-9\%$.
  * **Regla de Circuit Breaker Requerida:** Pausar la operativa del día tras **3 pérdidas consecutivas**.

### 3.3. Segmentación por Sesión Horaria (RTH vs Overnight)
* **Sesión Regular Americana (RTH: 16:30 a 23:00 MT5):**
  * 301 trades | Win Rate: 30.56% | PnL: -$976.85 USD | Retorno: +0.89% | PF: 1.01.
* **Sesión Fuera de Horas (Overnight / Globex: 00:00 a 16:30 MT5):**
  * 938 trades | Win Rate: 29.32% | PnL: +$2,976.95 USD | Retorno: +8.07% | PF: 1.05.
* **Hallazgo:** Los movimientos que nacieron en la sesión overnight lograron capitalizar mejor la aceleración de tendencia de varios días que los cruces tardíos generados dentro del horario de máxima volatilidad de apertura americana.

---

## 4. Cuadro Síntesis de Mejoras Inmediatas Recomendadas

| Hallazgo del Diagnóstico | Causa Raíz | Solución Cuantitativa en Código |
| :--- | :--- | :--- |
| **Shorts en -19.31%** | Lucha contra la deriva secular alcista del Nasdaq | Implementar modo **Long-Only** o filtro de pendiente EMA 200 D1 |
| **Racha de 18 pérdidas** | Falso quiebre reiterado en mercados laterales | Agregar **Circuit Breaker** (máximo 3 pérdidas por sesión) |
| **50% de meses en pérdida** | Falta de filtro de volatilidad en fases muertas | Agregar **Filtro Z-Score ATR Diario** (solo operar con ATR > media) |
| **Trades perdedores en 19 barras** | Pérdida de impulso sin definición | Incorporar **Time-Stop** en barra 24 si el PnL es negativo |
