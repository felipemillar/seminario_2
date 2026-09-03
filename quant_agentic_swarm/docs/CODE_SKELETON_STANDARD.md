# Estandar Canónico del Esqueleto de Codigo (Code Skeleton Standard)

Este documento define la arquitectura estructural obligatoria de 7 bloques que los agentes desarrolladores (**PineScriptAgent** y **MQL5Agent**) deben seguir estrictamente al generar cualquier estrategia en el **Quant Agentic Swarm (QAS)**.

---

## 1. Los 7 Bloques Anatomicos Obligatorios

```
┌────────────────────────────────────────────────────────────────────────┐
│ BLOQUE 0: Metadatos Institucionales & Declaracion de Compilador        │
├────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 1: Inputs de Usuario Agrupados con Sanity Checks & Clamping     │
├────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 2: Guarda de Calentamiento & Medidor de Historial (5-10 Anos D1)│
├────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 3: Motores de Contexto MTF (D1) & Z-Score de Volatilidad        │
├────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 4: Logica de Disparo & Generacion de Senales (Alpha Engine)     │
├────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 5: Gestion de la Triple Barrera (TP ATR D1, SL, Time-Stop)      │
├────────────────────────────────────────────────────────────────────────┤
│ BLOQUE 6: Diagnostico Visual (HUD Neutro-Informativo & Trazado)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Especificacion Detallada Bloque por Bloque

### Bloque 0: Metadatos Institucionales & Compilador
- **Objetivo:** Identificar unívocamente la estrategia y fijar las reglas del compilador.
- **Elementos Requeridos:**
  - `Strategy UUID`: Formato `STRAT-YYYYMMDD-SETUP-TF-vX.X`.
  - Tesis económica resumida.
  - Parámetros de simulación inicial (capital base, slippage, comisiones).
  - En Pine: `//@version=5` y `strategy(...)`.
  - En MQL5: `#property copyright`, `#property version`, `#property description`.

### Bloque 1: Inputs de Usuario Agrupados (Sanity Clamping)
- **Objetivo:** Permitir al investigador ajustar parámetros sin riesgo de ingresar valores matemáticamente imposibles.
- **Organización en 4 Grupos:**
  1. *Grupo Setup:* Parámetros propios del modelo (periodos de medias, canales, rangos).
  2. *Grupo Régimen MTF (D1):* Periodos de ATR rápido (5), lento (14), ventana Z-Score (20) y umbral (0.67).
  3. *Grupo Triple Barrera:* Multiplicador $k_1$ para $\text{ATR}_D(14)$, multiplicador $k_2$ para Stop, límite de barras $B_3$.
  4. *Grupo Diagnóstico Visual:* Interruptores de visualización del HUD y trazado de barreras.
- **Regla de Clamping:** Todo input numérico debe contener límites explícitos (`minval`, `maxval`, `step`).

### Bloque 2: Guarda de Calentamiento & Medidor de Historial D1
- **Objetivo:** Prevenir disparos con buffers incompletos y auditar la calidad muestral.
- **Lógica Requerida:**
  - Contar las barras diarias disponibles ($N_{D1}$) y convertirlas a años ($N_{D1} / 252$).
  - Activar flag `is_warmed_up = (d1_bars >= slow_atr + z_window)`.
  - Si no está caliente, el motor suspende la evaluación sin colapsar.

### Bloque 3: Motores de Contexto MTF & Z-Score de Volatilidad
- **Objetivo:** Clasificar el entorno macro antes de permitir entradas intradía.
- **Lógica Requerida:**
  - Consulta a barra diaria cerrada anterior ($[1]$ / shift 1) con `lookahead_off`.
  - $\Delta \text{ATR}_D = \text{ATR}_D(5) - \text{ATR}_D(14)$.
  - Cálculo de media y desviación típica sobre ventana $W$.
  - $Z_{\text{vol}} = (\Delta \text{ATR}_D - \mu) / \sigma$.
  - Clasificación en terciles: `is_vol_high` ($Z > +0.67$), `is_vol_low` ($Z < -0.67$), `is_vol_med`.

### Bloque 4: Lógica de Disparo (Alpha Engine)
- **Objetivo:** Evaluar las condiciones canónicas de la tesis sellada.
- **Lógica Requerida:**
  - Sincronización obligatoria al cierre de barra (`barstate.isconfirmed` en Pine, `IsNewBar()` en MQL5).
  - Condición de compra: `is_warmed_up AND is_vol_high AND setup_trigger_long AND flat`.
  - Condición de venta: `is_warmed_up AND is_vol_high AND setup_trigger_short AND flat`.

### Bloque 5: Gestión de la Triple Barrera & Telemetría
- **Objetivo:** Ejecutar entradas y gestionar las 3 barreras de forma determinista.
- **Lógica Requerida:**
  - Al abrir posición:
    - Registrar $P_{\text{entry}}$ y $\text{bar\_index}$ de entrada.
    - Fijar $B_1 (\text{Take Profit}) = P_{\text{entry}} \pm (k_1 \times \text{ATR}_D(14))$.
    - Fijar $B_2 (\text{Stop Loss}) = P_{\text{entry}} \mp (k_2 \times \text{ATR}_{\text{intraday}}(14))$ o nivel estructural.
    - Emitir log estructurado en formato JSON con evento `ENTRY_BUY` o `ENTRY_SELL`.
  - En cada tick/barra mientras haya posición abierta:
    - Evaluar $B_1$: Si High $\ge$ TP, cerrar y loguear `EXIT_B1_TP_D1`.
    - Evaluar $B_2$: Si Low $\le$ SL, cerrar y loguear `EXIT_B2_SL`.
    - Evaluar $B_3$: Si barras transcurridas $\ge N$, cerrar a mercado y loguear `EXIT_B3_TIME`.

### Bloque 6: Diagnóstico Visual (HUD Neutro-Informativo)
- **Objetivo:** Ofrecer al trader visibilidad instantánea del estado interno del algoritmo en el gráfico.
- **Campos del HUD:**
  - Fila 0: Strategy UUID.
  - Fila 1: Historial D1 (Años, barras y badge `[OK]` o `[ALERTA: < 5 ANOS]`).
  - Fila 2: Régimen de Volatilidad (Estado + Z-Score numérico).
  - Fila 3: ATRs Diarios (Valores actuales de ATR5 y ATR14).
  - Fila 4: Configuración de la Triple Barrera ($B_1$, $B_2$, $B_3$).
  - Fila 5: Estado del Motor (`OPERATIVO` / `CALENTANDO`).
