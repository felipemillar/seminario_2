# Guia de Interaccion Humano-en-el-Bucle (HITL)

El **Quant Agentic Swarm (QAS)** esta diseñado bajo el principio de **co-creacion guiada**. El trader nunca es un mero espectador pasivo; es el **Arquitecto Principal** que aprueba y calibra la tesis antes de que se escriba codigo.

---

## 1. El Bucle de Co-Creacion de Hipotesis

```
   ┌────────────────────────────────────────────────────────┐
   │ PASO 1: IDEA EN LENGUAJE NATURAL DEL TRADER            │
   │ "Quiero entrar en largo cuando el precio rompa el      │
   │ maximo asiatico en USD/CLP o EUR/USD"                  │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ PASO 2: EL AGENTE DE HIPOTESIS GENERA 3 VARIANTES      │
   │         EN FICHAS TECNICAS ESTRUCTURADAS (X-Y-Z)       │
   └──────┬────────────────────┼────────────────────┬───────┘
          │                    │                    │
          ▼                    ▼                    ▼
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │ VARIANTE A   │     │ VARIANTE B   │     │ VARIANTE C   │
   │ Momentum     │     │ Pullback &   │     │ Filtro       │
   │ Directo      │     │ Retesteo     │     │ Volatilidad  │
   └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                               ▼
 ╔════════════════════════════════════════════════════════════╗
 ║ PASO 3: PUERTA DE DECISION HUMANA (HITL GATEKEEPER)        ║
 ║                                                            ║
 ║  El trader responde con una de estas 3 acciones:           ║
 ║  1. SELECCION DIRECTA: "Elijo la Variante B"               ║
 ║  2. COMBINACION: "Quiero la entrada de B y el stop de C"   ║
 ║  3. AJUSTE PUNTUAL: "Cambia la sesion a Londres 08:00 UTC" ║
 ╚═════════════════════════════╤══════════════════════════════╝
                               │ (Aprobacion explicita)
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ PASO 4: HIPOTESIS CERTIFICADA Y SELLADA                │
   │ Pasa al Agente Modelador de Reglas + RAG 1             │
   └────────────────────────────────────────────────────────┘
```

---

## 2. Formato Canonico de Entrega: Matriz Comparativa Sintetica

Para minimizar la carga cognitiva del trader y permitir una evaluacion visual completa en menos de 5 segundos sin scroll, el agente debe presentar siempre las 3 variantes mediante una **tabla comparativa horizontal** estructurada:

### Ejemplo Canonico Obligatorio:

| Dimension | [VARIANTE A] Momentum Directo | [VARIANTE B] Pullback & Retesteo (Recomendada) | [VARIANTE C] Trailing de Expansion |
| :--- | :--- | :--- | :--- |
| **Señal de Entrada** | Quiebre y cierre sobre maximo asiatico | Quiebre de maximo + retesteo confirmado | Ruptura con compresion previa de rango |
| **Filtro de Tendencia** | Sin filtro | Confirmacion de volumen / absorcion | Z-Score Diario mayor a 0 (mercado activo) |
| **Stop Loss (SL)** | **1.0x ATR Diario** | **0.75x ATR Diario** | **1.0x ATR Diario** (Stop inicial) |
| **Take Profit (TP)** | **2.0x ATR Diario** | **1.5x ATR Diario** | **Sin TP fijo** (Trailing Stop dinamico) |
| **Relacion Beneficio / Riesgo** | **2.0 a 1** | **2.0 a 1** (asimetrica con menor riesgo) | **Abierta** (arriesga 1.0 ATR para correr) |
| **Limite Temporal (Time-Stop)** | 48 barras M30 (24 horas) | 32 barras M30 (16 horas) | 64 barras M30 (32 horas) |
| **Tesis Cuantitativa** | Captura aceleracion tras barrido de liquidez | Entrada en reacumulacion con mayor tasa de acierto | Captura rallies parabolicos sin recortar ganancias |

#### Reglas de Redaccion Obligatorias:
1. **ATR como Unidad Base:** SL y TP siempre deben expresarse en multiplos limpios de ATR Diario (ej. `0.75x ATR Diario`, `1.5x ATR Diario`).
2. **Prohibido Codigo LaTeX:** NUNCA escribir formulas con simbolos de dolar (`$ \times \text{ATR} $`).
3. **Cero Emoticones:** Mantener la sobriedad visual y etiquetas limpias (`[VARIANTE A]`, `[VARIANTE B]`).
4. **Resumen de Decision:** Al pie de la tabla, incluir un resumen de 1 linea por variante para decision inmediata.


---

## 3. Protocolo de Aprobacion

1. **Aprobacion Rapida:**
   *Trader:* `"Aprobada Variante B"`.
   *Efecto:* Se genera inmediatamente el `StrategySpecification` y se delega a los desarrolladores.
2. **Aprobacion con Ajustes:**
   *Trader:* `"Usa la Variante B, pero el Take Profit fijado a 3x ATR en lugar de 2x"`.
   *Efecto:* El agente actualiza la ficha, re-confirma los cambios y sella la hipotesis.
3. **Rechazo / Re-Brainstorming:**
   *Trader:* `"No me convence ninguna, busquemos una hipotesis basada en reversion a la media"`.
   *Efecto:* El agente limpia el estado y propone 3 variantes de reversion a la media.
