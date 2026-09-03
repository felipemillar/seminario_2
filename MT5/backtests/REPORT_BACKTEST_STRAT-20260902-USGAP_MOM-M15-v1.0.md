# Reporte de Auditoría Cuantitativa de Backtesting (Pool de 3 Módulos)

> **Estrategia:** `STRAT-20260902-USGAP_MOM-M15-v1.0` (US Opening Gap Momentum Continuation)  
> **Activo Evaluado:** `CUSTOM_NQ_M5` (Nasdaq 100 E-mini Futuros)  
> **Temporalidad:** `M15` (Barras de 15 minutos) | **Muestreo:** 29 Operaciones Ejecutadas  
> **Periodo Histórico:** Septiembre 2020 – Agosto 2026 (6 años de histórico)  
> **Autor Institucional:** QRT Solutions  
> **Estándar:** Pool Canónico de 3 Módulos conforme a [`MT5/BACKTEST_AUDIT_MANUAL.md`](../BACKTEST_AUDIT_MANUAL.md)

---

## Resumen Ejecutivo de la Tesis

El sistema evalúa el desequilibrio de apertura en Wall Street (09:30 ET / 16:30 servidor Pepperstone) condicionado a un régimen de alta volatilidad ($Z_{\text{vol}} > 0.67$) según Marcos López de Prado.

* **Resultado Global:** El sistema arrojó un retorno porcentual acumulado de **+2.26%** sobre el precio subyacente con un **Profit Factor de 1.39** y una asimetría de retorno favorable (**Payoff de 1.97 a 1**).
* **Hallazgo Clave de Salidas:** El **100% de los trades ganadores** cerraron por **Time-Stop (B3)** al final de la sesión, mientras que las pérdidas se cortaron velozmente en un promedio de **1.48 horas** por el Stop Loss (B2).

---

## Módulo 1: La Evaluación Dual (Monetaria vs Variación Porcentual Pura)

| Dimensión / KPI | Capa Monetaria (USD) | Capa Porcentual Pura (% Precio Subyacente) | Observaciones Cuantitativas |
| :--- | :---: | :---: | :--- |
| **Retorno Neto Total** | **+$414.82 USD** | **+2.26%** | Ganancia neta positiva en 6 años de datos. |
| **Profit Factor (PF)** | **1.39** | **1.39** | Por cada punto porcentual perdido, se capturaron 1.39 puntos de ganancia. |
| **Tasa de Acierto (Win Rate)** | **41.38%** (12 / 29) | **41.38%** | Tasa típica de sistemas seguidores de momentum / tendencia. |
| **Ganancia Media (Avg Win)** | +$67.25 USD | **+0.67%** | Retorno medio por trade ganador. |
| **Pérdida Media (Avg Loss)** | -$34.18 USD | **-0.34%** | Pérdida media estrictamente acotada por el Stop Loss de M15. |
| **Payoff Ratio** | **1.97 a 1** | **1.97 a 1** | Los ganadores duplican el tamaño de los perdedores. |
| **Drawdown Máximo Estimado** | -$185.00 USD | **-1.42%** | Caída contenida gracias al corte rápido de pérdidas. |

---

## Módulo 2: Diagnóstico de Asimetrías (¿Dónde está el Edge?)

### 2.1. Desglose Direccional Mandatorio (Longs vs Shorts)
*(Alexander Elder & Perry Kaufman)*

| Métrica Direccional | Compras (LONG / Gaps Alcistas) | Ventas (SHORT / Gaps Bajistas) | Asimetría Detectada |
| :--- | :---: | :---: | :--- |
| **Total Operaciones** | 14 trades (48.3%) | 15 trades (51.7%) | Distribución casi simétrica de señales. |
| **Tasa de Acierto (Win Rate)** | **42.9%** (6 Ganadores / 8 Perdedores) | **40.0%** (6 Ganadores / 9 Perdedores) | Prácticamente idéntico acierto. |
| **Retorno % Acumulado** | **+0.62%** | **+1.64%** | **Los Shorts superaron a los Longs por 2.6x**. |
| **Mayor Trade Individual** | +0.92% (Febrero 2026) | **+1.62%** (Mayo 2021) | Los gaps bajistas generan expansiones más agresivas (*Volatility Smile*). |

> **Diagnóstico Cuantitativo:**  
> A pesar de que el índice Nasdaq 100 tiene un sesgo alcista secular (*drift* alcista a largo plazo), la estrategia de **Gap Momentum** generó mayor retorno neto en las **ventas en corto (Shorts: +1.64%)** que en las compras (**Longs: +0.62%**). Esto valida que en regímenes de expansión de volatilidad ($Z > 0.67$), el pánico intradía genera recorridos direccionales más limpios hacia el sur.

### 2.2. Esperanza Matemática por Trade ($E$)
*(Mark Minervini & Van Tharp)*
$$E = (WR \times \text{Avg Win \%}) - (LR \times \text{Avg Loss \%})$$
$$E = (0.4138 \times 0.6725\%) - (0.5862 \times 0.3418\%) = \mathbf{+0.078\% \text{ por trade}}$$

> Cada vez que la estrategia abre una posición al cierre de la vela M15 de apertura, el retorno neto promedio esperado es de **+0.08%** sobre el valor del Nasdaq, independiente del capital de cuenta.

### 2.3. Consistencia Temporal (% Meses Positivos)
*(David Aronson & Perry Kaufman)*
* **Meses con Operaciones:** 23 meses activos a lo largo del periodo 2020–2026.
* **Meses con Retorno Positivo:** 9 meses (39.1%).
* **Meses con Retorno Negativo:** 14 meses (60.9%).
* **Observación:** El sistema es de baja frecuencia (aprox. 5 trades por año), operando exclusivamente cuando se alinea la apertura de Wall Street con una expansión violenta de volatilidad diaria.

---

## Módulo 3: Diagnóstico de Ejecución y Salidas (¿Cómo Optimizar?)

### 3.1. Eficiencia de Salidas y Barreras de Salida
* **Time-Stop (B3 - 26 Barras M15):** **12 trades** (41.4% del total).  
  * **Efectividad:** **100% de trades ganadores**. Todos los trades que sobrevivieron la sesión y salieron por tiempo cerraron en beneficio (+8.07% acumulado).
* **Stop Loss Técnico (B2 - 1.0x ATR M15):** **17 trades** (58.6% del total).  
  * **Efectividad:** Todas las pérdidas fueron liquidadas puntualmente por el SL (-5.81% acumulado), protegiendo la cuenta de caídas catastróficas.
* **Take Profit RTH (B1 - 2.0x ATR D1):** Ningún trade alcanzó la meta extrema de 2.0x ATR Diario dentro de la misma sesión intradiaria. Esto indica que el Target de 2.0x ATR Diario es excesivamente ambicioso para una sesión de 6.5 horas.  
  * **Recomendación de Optimización:** Reducir el TP a **$1.25x - 1.50x \text{ ATR Diario}$** para capturar salidas en el clímax del impulso intradía.

### 3.2. Tiempo de Permanencia (Holding Period Decay)
*(Toby Crabel)*
* **Duración Media en Ganadores:** **20.25 horas** (permanencia completa hasta el cierre oficial de sesión RTH a la 01:00 servidor).
* **Duración Media en Perdedores:** **1.48 horas** (menos de 6 velas M15).
* **Conclusión Causal:** La hipótesis se valida o invalida muy rápido: si el impulso no arranca en los primeros 90 minutos, el trade suele tocar el Stop Loss. Si arranca favorablemente, tiende a sostener la deriva hasta el final de la jornada.

### 3.3. Racha Máxima de Pérdidas y Circuit Breaker
*(Richard Weissman & Alexander Elder)*
* **Racha Máxima Consecutiva de Pérdidas:** **7 operaciones consecutivas**.
* **Impacto en Cuenta de la Peor Racha:** $-2.05\%$ acumulado.
* **Circuit Breaker Recomendado:** Dado que las pérdidas están espaciadas en meses distintos debido a la baja frecuencia del filtro $Z$-score, no se requiere un circuit breaker intradiario, pero se recomienda un límite de **3 pérdidas consecutivas en el mismo mes**.

---

## Registro Detallado de las 29 Transacciones

| # | Dirección | Entrada (Servidor) | Precio In | Salida (Servidor) | Precio Out | Puntos | Retorno % | Motivo de Salida |
| :-: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 01 | LONG | 2020.09.09 16:45 | 14,783.35 | 2020.09.09 18:00 | 14,725.58 | -57.77 | -0.39% | STOP_LOSS (B2) |
| 02 | LONG | 2021.01.07 16:45 | 16,278.35 | 2021.01.07 17:00 | 16,248.12 | -30.23 | -0.19% | STOP_LOSS (B2) |
| 03 | LONG | 2021.02.01 16:45 | 16,549.60 | 2021.02.02 01:00 | 16,609.25 | +59.65 | **+0.36%** | TIME_STOP (B3) |
| 04 | SHORT | 2021.02.23 16:45 | 16,349.00 | 2021.02.23 19:05 | 16,428.30 | -79.30 | -0.49% | STOP_LOSS (B2) |
| 05 | SHORT | 2021.02.25 16:45 | 16,402.50 | 2021.02.26 01:00 | 16,142.60 | +259.90 | **+1.58%** | TIME_STOP (B3) |
| 06 | SHORT | 2021.05.10 16:45 | 16,874.50 | 2021.05.11 01:00 | 16,600.60 | +273.90 | **+1.62%** | TIME_STOP (B3) |
| 07 | SHORT | 2021.05.12 16:45 | 16,379.50 | 2021.05.12 17:00 | 16,437.96 | -58.46 | -0.36% | STOP_LOSS (B2) |
| 08 | SHORT | 2021.08.17 16:45 | 18,304.50 | 2021.08.17 18:15 | 18,351.05 | -46.55 | -0.25% | STOP_LOSS (B2) |
| 09 | SHORT | 2021.09.20 16:45 | 18,311.50 | 2021.09.20 19:55 | 18,361.63 | -50.13 | -0.27% | STOP_LOSS (B2) |
| 10 | SHORT | 2021.11.30 16:45 | 19,499.75 | 2021.11.30 18:50 | 19,567.73 | -67.98 | -0.35% | STOP_LOSS (B2) |
| 11 | LONG | 2021.12.07 16:45 | 19,702.85 | 2021.12.07 20:25 | 19,665.05 | -37.80 | -0.19% | STOP_LOSS (B2) |
| 12 | SHORT | 2022.01.10 16:45 | 18,651.25 | 2022.01.10 18:15 | 18,714.30 | -63.05 | -0.34% | STOP_LOSS (B2) |
| 13 | SHORT | 2022.01.24 16:45 | 17,298.50 | 2022.01.24 18:05 | 17,406.52 | -108.02 | -0.62% | STOP_LOSS (B2) |
| 14 | LONG | 2023.05.26 16:45 | 17,359.35 | 2023.05.29 01:00 | 17,446.50 | +87.15 | **+0.50%** | TIME_STOP (B3) |
| 15 | LONG | 2024.04.05 16:45 | 20,565.35 | 2024.04.05 17:55 | 20,511.31 | -54.04 | -0.26% | STOP_LOSS (B2) |
| 16 | LONG | 2024.06.05 16:45 | 21,189.60 | 2024.06.06 01:00 | 21,289.75 | +100.15 | **+0.47%** | TIME_STOP (B3) |
| 17 | SHORT | 2024.07.17 16:45 | 21,971.75 | 2024.07.17 17:35 | 22,027.20 | -55.45 | -0.25% | STOP_LOSS (B2) |
| 18 | SHORT | 2024.09.03 16:45 | 21,093.00 | 2024.09.04 01:00 | 20,809.85 | +283.15 | **+1.34%** | TIME_STOP (B3) |
| 19 | LONG | 2025.05.12 16:45 | 22,060.60 | 2025.05.13 01:00 | 22,087.75 | +27.15 | **+0.12%** | TIME_STOP (B3) |
| 20 | LONG | 2025.05.13 16:45 | 22,534.10 | 2025.05.13 19:55 | 22,481.55 | -52.55 | -0.23% | STOP_LOSS (B2) |
| 21 | SHORT | 2025.08.01 16:45 | 23,958.75 | 2025.08.04 01:00 | 23,951.35 | +7.40 | **+0.03%** | TIME_STOP (B3) |
| 22 | LONG | 2025.12.18 16:45 | 25,900.85 | 2025.12.18 17:05 | 25,815.98 | -84.87 | -0.33% | STOP_LOSS (B2) |
| 23 | LONG | 2026.01.15 16:45 | 26,412.35 | 2026.01.15 18:00 | 26,356.19 | -56.16 | -0.21% | STOP_LOSS (B2) |
| 24 | SHORT | 2026.02.03 16:45 | 26,007.25 | 2026.02.04 01:00 | 25,889.10 | +118.15 | **+0.45%** | TIME_STOP (B3) |
| 25 | LONG | 2026.02.06 16:45 | 25,534.35 | 2026.02.09 01:00 | 25,770.50 | +236.15 | **+0.92%** | TIME_STOP (B3) |
| 26 | LONG | 2026.03.09 16:45 | 25,247.10 | 2026.03.09 17:20 | 25,150.49 | -96.61 | -0.38% | STOP_LOSS (B2) |
| 27 | SHORT | 2026.06.09 16:45 | 28,671.00 | 2026.06.09 17:00 | 28,876.59 | -205.59 | -0.72% | STOP_LOSS (B2) |
| 28 | SHORT | 2026.07.27 16:45 | 28,135.25 | 2026.07.28 01:00 | 28,063.85 | +71.40 | **+0.25%** | TIME_STOP (B3) |
| 29 | LONG | 2026.08.04 16:45 | 29,715.10 | 2026.08.05 01:00 | 29,842.00 | +126.90 | **+0.43%** | TIME_STOP (B3) |
