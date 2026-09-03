# Reporte de Auditoría Cuantitativa Dual: Monetaria vs Retorno Porcentual Puro

> **Autor Institucional:** QRT Solutions  
> **Activo Evaluado:** `CUSTOM_NQ_M5` (E-mini Nasdaq 100 Futuros - Datos Externos)  
> **Estrategia:** `EASimple_CruceMedias.ex5` (EMA Rápida 9 / EMA Lenta 21, timeframe M30)  
> **Período de Simulación:** 02 de Enero de 2024 al 07 de Agosto de 2026 (2.6 años / 31,376 barras M30)  
> **Muestreo Total:** 1,239 operaciones round-turn (2,478 deals ejecutados)

---

## 1. Justificación Cuantitativa de la Evaluación Dual

En el análisis cuantitativo institucional, medir una estrategia exclusivamente por su **PnL monetario (USD)** introduce distorsiones severas cuando el activo subyacente experimenta una fuerte tendencia secular o inflación nominal. 

En este período, el Nasdaq transitó desde los 16,500 puntos (inicios de 2024) hasta superar los 29,800 puntos (agosto de 2026). Esto significa que un movimiento de $100 puntos representaba un **0.60%** en 2024, pero solo un **0.33%** en 2026. Al evaluar paralelamente la **variación porcentual pura del precio**, eliminamos el sesgo del apalancamiento y del tamaño de lote, aislando el verdadero **Edge Estadístico** del modelo de precios.

* **Fórmula de Retorno Porcentual en Compras (BUY):**
  $$R_{\text{Long}} = \frac{P_{\text{exit}} - P_{\text{entry}}}{P_{\text{entry}}} \times 100\%$$
* **Fórmula de Retorno Porcentual en Ventas (SELL):**
  $$R_{\text{Short}} = \frac{P_{\text{entry}} - P_{\text{exit}}}{P_{\text{entry}}} \times 100\%$$

---

## 2. Matriz Comparativa Dual: Monetaria vs Porcentual

| Dimensión de Rendimiento | Métrica Monetaria (USD) | Métrica Porcentual Pura (% Precio) | Interpretación Cuantitativa |
| :--- | :--- | :--- | :--- |
| **Resultado Neto Global** | **+$2,000.10 USD** | **+8.96% Acum. (+4.19% Compuesto)** | Estrategia neta positiva pero con fuerte fricción interna. |
| **Profit Factor** | **1.03** | **1.03** | Edge estadístico marginal en la configuración simétrica. |
| **Tasa de Acierto (Win Rate)** | **29.62%** (367 Win / 872 Loss) | **29.62%** | Comportamiento clásico de seguidor de tendencia (Trend Following). |
| **Beneficio / Ganancia Media** | **+$212.04 USD** | **+0.902% por Trade** | Ganancia media casi triplica la pérdida media. |
| **Pérdida Media** | **-$86.95 USD** | **-0.369% por Trade** | Pérdidas controladas por el corte dinámico del cruce. |
| **Payoff Ratio (R:R Real)** | **2.44 a 1** | **2.44 a 1** | Excelente asimetría de corte (deja correr ganancias). |
| **Mejor Operación (Max Win)** | +$1,960.00 USD | **+9.56%** | Captura completa de rally alcista intradiario. |
| **Peor Operación (Max Loss)** | -$720.00 USD | **-3.55%** | Gap o volatilidad adversa en sesión nocturna. |
| **Máximo Drawdown (Rachas)** | -$5,430.00 USD | **-27.14%** | Concentrado en períodos de consolidación lateral / chop. |

---

## 3. Desglose Estructural por Dirección: La Gran Asimetría

Al separar las operaciones por su naturaleza direccional, se observa con total claridad el origen del rendimiento del sistema:

| Métrica | Compras (LONGS - 620 Trades) | Ventas (SHORTS - 619 Trades) | Impacto en el Portafolio |
| :--- | :--- | :--- | :--- |
| **PnL Monetario Neto** | **+$6,178.75 USD** | **-$4,178.65 USD** | Los shorts destruyen el 67.6% del beneficio. |
| **Retorno Porcentual Puro** | **+28.27% Acumulado** | **-19.31% Acumulado** | Edge masivo del lado largo (+28.27% vs -19.31%). |
| **Retorno Compuesto** | **+29.43%** | **-19.50%** | Capitalización asimétrica favorable al Long. |
| **Profit Factor** | **1.18** | **0.88** | Compras viables; Ventas inviables sin filtro macro. |
| **Win Rate** | **32.90%** (204 Win / 416 Loss) | **26.33%** (163 Win / 456 Loss) | El sesgo alcista del Nasdaq penaliza severamente los cortos. |
| **Ganancia Media (%)** | **+0.910%** | **+0.891%** | Similar captura en trades ganadores. |
| **Pérdida Media (%)** | **-0.379%** | **-0.361%** | Similar tolerancia al riesgo de salida. |
| **Máximo Drawdown (%)** | **-10.95%** | **-34.27%** | El drawdown global del 27% proviene de los cortos. |

---

## 4. Hallazgos Cuantitativos y Conclusiones

1. **Validación Exitosa del Dataset Inyectado:**  
   El historial `CUSTOM_NQ_M5` funcionó de manera ininterrumpida a lo largo de 31,376 barras M30, ejecutando 1,239 posiciones completas con 0 errores de sincronización o falta de datos.
2. **El Cruce EMA 9/21 Posee un Edge Fuerte en Compras:**  
   Operar únicamente compras (Long-Only) habría generado **+28.27% de retorno porcentual puro** ($+6,178 USD) con un Profit Factor de **1.18** y un Drawdown controlado de solo el **10.95%**.
3. **El Problema de las Ventas en Activos con Drift Alcista:**  
   Los cortos generaron una fuga neta de **-19.31%** ($-4,178 USD) y un Drawdown del 34.27%, debido a la deriva natural (*drift*) del índice Nasdaq.
4. **Recomendación Cuantitativa Inmediata:**  
   Implementar una regla de filtro direccional:
   * **Opción A:** Modo **Long-Only** en activos bursátiles estadounidenses.
   * **Opción B:** Filtro de Régimen Macro de Alexander Elder (EMA 200 con pendiente alcista, tal como se validó en `STRAT-BTC_TREND_CROSS`), prohibiendo ventas cuando el índice cotice sobre su media móvil diaria.
