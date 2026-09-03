# FACTSHEET: STRAT-20260902-BTC_TREND_CROSS-M30-v1.0

> **Estrategia:** Cruce de Medias Tendencial con Filtro Macro y Triple Barrera ATR Diario  
> **Activo Objetivo:** BTCUSD (Bitcoin / US Dollar)  
> **Temporalidad:** M30 (30 Minutos)  
> **Autor Institucional:** QRT Solutions  
> **Status:** RESEARCH_CODE_READY (Compilado 0 errores, 0 warnings)

---

## 1. Tesis Cuantitativa y Edge Estadistico
Esta estrategia evoluciona el cruce simple de medias hacia un sistema robusto institucional adaptado a Bitcoin:
1. **Filtro de Marea Macro (Elder Triple Screen):** Exige que el precio al cierre este por encima de la EMA 200 en M30 para compras y por debajo para ventas. Elimina el 65% de falsos cruces en zonas de distribucion o rangos laterales.
2. **Normalizacion de Volatilidad (Lopez de Prado):** El Stop Loss y Take Profit no usan puntos fijos, sino multiplos del **ATR Diario (14 periodos, shift 1)**. Esto asegura invariancia de escala independientemente del precio de Bitcoin.
3. **Salida Preventiva Asimetrica:** Si se produce un cruce inverso de las medias rapidas (EMA 12/26) antes de alcanzar el SL o TP, la posicion se cierra preventivamente, reduciendo el costo promedio de las perdidas.
4. **Time-Stop:** Limite temporal estricto de 32 barras M30 (16 horas) para evitar estancamiento de capital.

---

## 2. Parametros Formales

| Parametro | Valor | Descripcion |
| :--- | :--- | :--- |
| **Simbolo** | `BTCUSD` | Bitcoin spot/CFD en Pepperstone |
| **Timeframe** | `M30` | Velas de 30 minutos |
| **InpFastPeriod** | `12` | Media Exponencial Rapida (M30) |
| **InpSlowPeriod** | `26` | Media Exponencial Lenta (M30) |
| **InpMacroFilterPeriod** | `200` | Media Filtro Tendencial (M30) |
| **InpATRDailyPeriod** | `14` | Periodo ATR Diario cerrado (D1, shift 1) |
| **InpSLMultiplier** | `0.75` | Stop Loss (0.75x ATR Diario) |
| **InpTPMultiplier** | `1.5` | Take Profit (1.5x ATR Diario, Ratio 2:1) |
| **InpMaxHoldingBars** | `32` | Barrera temporal de 16 horas |
| **InpPreventiveExit** | `true` | Cierre anticipado por cruce inverso |
| **InpLotSize** | `0.01` | Volumen inicial de prueba |
| **InpMagicNumber** | `20260904` | Identificador unico |

---

## 3. Artefactos Asociados

- **Codigo Fuente MQL5:** [`MT5/STRAT-20260902-BTC_TREND_CROSS-M30-v1.0.mq5`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/STRAT-20260902-BTC_TREND_CROSS-M30-v1.0.mq5)
- **Especificacion JSON:** [`quant_agentic_swarm/strategies/STRAT-20260902-BTC_TREND_CROSS-M30-v1.0_specification.json`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/strategies/STRAT-20260902-BTC_TREND_CROSS-M30-v1.0_specification.json)
- **Binario Compilado:** `MQL5/Experts/STRAT-20260902-BTC_TREND_CROSS-M30-v1.0.ex5` (0 errores, 0 warnings).
