# Estándares Técnicos y Patrones de Producción Pine Script v6
**Autor:** QRT Solutions

---

## 1. Patrón Multi-Timeframe con Tuplas y Seguridad Anti-Lookahead

```pinescript
// Función de cálculo en marco superior (D)
f_daily_data() =>
    d_close = close
    d_atr14 = ta.atr(14)
    d_atrPct = (d_atr14 / d_close) * 100.0
    d_volMed = ta.percentile_nearest_rank(d_atrPct, 250, 50)
    [d_close[0], d_atr14[0], d_atrPct[0], d_volMed[0]]

// Llamada con tupla segura (cero lookahead)
[dClose, dATR, dATRPct, dVolMed] = request.security(syminfo.tickerid, "D", f_daily_data(), lookahead = barmerge.lookahead_off)
```

---

## 2. Patrón de Reloj de Sesión Intradiario Explícito (Nueva York)

Para evitar desajustes en activos que cotizan 23 horas (como futuros de CME) o activos 24/7 (como Crypto):

```pinescript
int nyHour   = hour(time, "America/New_York")
int nyMinute = minute(time, "America/New_York")
bool inRTH   = not na(time(timeframe.period, "0930-1600:23456", "America/New_York"))

// Primera barra de RTH
bool isFirstBar = (nyHour == 9 and nyMinute == 30) or (inRTH and not inRTH[1])

// Última barra de RTH (en velas de 5M es 15:55, en 30M es 15:30)
bool isLastBar  = (nyHour == 15 and nyMinute >= 55) or (not inRTH and inRTH[1])
```

---

## 3. Patrón de Separación Vertical de Etiquetas (*vBuffer*)

Para evitar que las etiquetas colisionen con las velas o con las flechas de ejecución nativas de TradingView:

```pinescript
// Buffer dinámico basado en ATR
float vBuffer = not na(dATR) and dATR > 0 ? (dATR * labelOffsetAtr) : (ta.atr(14) * labelOffsetAtr)

float labelY = isShort ? (high + vBuffer) : (low - vBuffer)
label.new(bar_index, labelY, text = msg, 
     style = isShort ? label.style_label_down : label.style_label_up,
     color = isShort ? color.maroon : color.teal,
     textcolor = color.white, size = size.small)
```

---

## 4. Patrón de Órdenes OCO (Bracket Stop Loss / Take Profit)

```pinescript
if longSignal and strategy.position_size == 0
    strategy.entry("Long Trade", strategy.long, qty = orderQty)
    strategy.exit("Bracket Long", "Long Trade", stop = slPrice, limit = tpPrice)

// Cierre EOD forzado
if isLastBar and strategy.position_size != 0
    strategy.close_all(comment = "Cierre EOD")
```
