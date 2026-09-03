# Indice de Estrategias Cuantitativas — seminario_2

> **Autor Institucional:** QRT Solutions  
> **Ubicacion Central:** `seminario_2/estrategias/`

Esta carpeta centraliza todos los artefactos de las estrategias desarrolladas y validadas en el ecosistema:

---

## 1. Estructura del Directorio

```
estrategias/
├── mql5/                # Codigo fuente de Asesores Expertos e Indicadores (.mq5)
├── pine/                # Estrategias en Pine Script v6 para TradingView (.pine)
└── especificaciones/   # Contratos JSON formales y Fichas Tecnicas (Factsheets)
```

---

## 2. Inventario de Estrategias

| ID Estrategia | Activo / Timeframe | Descripcion Cuantitativa | MQL5 (.mq5) | TradingView (.pine) | Ficha / JSON |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **STRAT-20260902-BTC_TREND_CROSS-M30-v1.0** | BTCUSD (M30) | Cruce de medias EMA 12/26 con Filtro de Marea Macro EMA 200 (Pendiente Elder) y Triple Barrera ATR Diario | [Ver MQL5](mql5/STRAT-20260902-BTC_TREND_CROSS-M30-v1.0.mq5) | — | [Factsheet](especificaciones/STRAT-20260902-BTC_TREND_CROSS-M30-v1.0_FACTSHEET.md) |
| **STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0** | XAUUSD (M30) | Sistema de Triple Pantalla de Alexander Elder con filtro Z-Score MTF y Triple Barrera ATR Diario | [Ver MQL5](mql5/STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0.mq5) | [Ver Pine](pine/STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0.pine) | [Factsheet](especificaciones/STRAT-20260902-GOLD_ELDER_CROSS-M30-v1.0_FACTSHEET.md) |
| **STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0** | XAUUSD (M30) | Cascada de Fibonacci (EMA 13/34/89) con retroceso a zona de valor y filtro Z-Score MTF Diario | [Ver MQL5](mql5/STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0.mq5) | [Ver Pine](pine/STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0.pine) | [Factsheet](especificaciones/STRAT-20260902-GOLD_PULLBACK_EMA-M30-v1.0_FACTSHEET.md) |
| **STRAT-20260902-USGAP_MOM-M15-v1.0** | USGAP (M15) | Momentum direccional en apertura de mercado americano con barreras de volatilidad | [Ver MQL5](mql5/STRAT-20260902-USGAP_MOM-M15-v1.0.mq5) | [Ver Pine](pine/STRAT-20260902-USGAP_MOM-M15-v1.0.pine) | [Factsheet](especificaciones/STRAT-20260902-USGAP_MOM-M15-v1.0_FACTSHEET.md) |
| **STRAT-20260902-ORB_MOM-M5-v1.0 / v1.1** | Acciones US (M5) | Ruptura de Rango de Apertura (Opening Range Breakout) con sesgo institucional | [Ver MQL5](mql5/STRAT-20260902-ORB_MOM-M5-v1.0.mq5) | — | [JSON](especificaciones/STRAT-20260902-ORB_MOM-M5-v1.0_specification.json) |

---

## 3. Indicadores Auxiliares

* **`mql5/Ind_BTC_Trend_Cross_M30.mq5`:** Indicador visual para MetaTrader 5 que grafica las medias 12, 26, 200 y flechas de señales filtradas por la pendiente de Elder.
* **`mql5/Ind_Elder_Cross_M30.mq5`:** Indicador de cruce de Elder para Oro en M30.
* **`mql5/Ind_Pullback_EMA_M30.mq5`:** Indicador de cascada Fibonacci EMA 13/34/89.
