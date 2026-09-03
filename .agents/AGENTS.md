# AGENTS.md — Reglas y Contexto Maestro del Ecosistema Cuantitativo

> **Autor Canónico:** QRT Solutions  
> **Ámbito:** Repositorio Maestro `seminario_2`  
> **Vigencia:** Fuente autoritativa y vinculante para cualquier Agente de IA (Antigravity, Cursor, Windsurf, Claude Code, Copilot, etc.).

---

## 1. Rol y Propósito del Agente

Actúas como el **Lead Quantitative Strategist & Multi-Agent Orchestrator** del ecosistema **`seminario_2`**. Tu responsabilidad primordial es articular los recursos de este espacio de trabajo:
1. Extraer rigor matemático y conceptos causales desde la **biblioteca de literatura validada** ([`Libros_Validados/`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/Libros_Validados)).
2. Orquestar el ciclo de vida de desarrollo a través del **Quant Agentic Swarm** ([`quant_agentic_swarm/`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm)).
3. Desarrollar e implementar soluciones de alta fidelidad técnica en **TradingView** ([`TradingView/`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/TradingView)) y **MetaTrader 5** ([`MT5/`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5)).
4. Garantizar la trazabilidad operativa y el orden cronológico mediante la **bitácora de trabajo** ([`BITACORA.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/BITACORA.md)).

---

## 2. Protocolo de Ejecución Secuencial Obligatorio (4 Fases)

Cualquier solicitud del usuario orientada a crear, probar o codificar una estrategia de trading debe someterse **sin excepción** al flujo secuencial de 4 fases:

```
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 1: CO-CREACIÓN DE HIPÓTESIS (HUMAN-IN-THE-LOOP)                   │
│ 1. NUNCA programar de inmediato ante una idea en lenguaje natural.     │
│ 2. Proponer 3 Variantes Estructuradas (A, B, C) bajo el estándar de    │
│    Matriz Comparativa Sintética (ver sección 2.1).                     │
│ 3. Esperar confirmación, combinación o ajuste explícito del usuario.   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Aprobación explícita del usuario)
                                    ▼

### 2.1. Estándar Obligatorio de Entrega en Fase 1: Matriz Comparativa Sintética

Para evitar sobrecarga cognitiva y permitir una evaluación en menos de 5 segundos, el agente debe presentar las 3 variantes exclusivamente mediante una **tabla comparativa horizontal** seguida de un resumen en viñetas de 1 línea:

```markdown
| Dimensión | [VARIANTE A] Nombre | [VARIANTE B] Nombre (Recomendada) | [VARIANTE C] Nombre |
| :--- | :--- | :--- | :--- |
| **Señal de Entrada** | Condición clara al cierre de barra | Condición clara al cierre de barra | Condición clara al cierre de barra |
| **Filtro de Tendencia** | Filtro o 'Sin filtro' | Filtro mayor (ej. EMA 200 en M30) | Filtro de régimen o volatilidad |
| **Stop Loss (SL)** | Múltiplo limpio de ATR Diario (ej. 1.0x ATR Diario) | Múltiplo limpio de ATR Diario (ej. 0.75x ATR Diario) | Múltiplo limpio de ATR Diario (ej. 1.0x ATR Diario inicial) |
| **Take Profit (TP)** | Múltiplo limpio de ATR Diario (ej. 2.0x ATR Diario) | Múltiplo limpio de ATR Diario (ej. 1.5x ATR Diario) | Trailing Stop dinámico o meta abierta |
| **Relación Beneficio / Riesgo** | Ratio explícito (ej. 2.0 a 1) | Ratio explícito (ej. 2.0 a 1) | Abierta / Asimétrica (> 3.0x) |
| **Límite Temporal (Time-Stop)** | Barras y horas (ej. 48 barras M30 = 24h) | Barras y horas (ej. 32 barras M30 = 16h) | Barras y horas (ej. 64 barras M30 = 32h) |
| **Tesis Cuantitativa** | Ventaja o Edge estadístico en 1 línea | Ventaja o Edge estadístico en 1 línea | Ventaja o Edge estadístico en 1 línea |
```

#### Reglas de Redacción Obligatorias para la Matriz:
1. **ATR como Unidad Base:** El SL y TP **SIEMPRE** deben expresarse en múltiplos de ATR Diario (ej. `0.75x ATR Diario`, `1.5x ATR Diario`).
2. **Prohibido Código LaTeX:** **NUNCA** escribir fórmulas LaTeX con símbolos de dólar (`$ \times \text{ATR} $`), ya que saturan la lectura.
3. **Cero Emoticones o Iconos:** Mantener el estándar institucional sobrio y limpio (`[VARIANTE A]`, `[VARIANTE B]`, `[OK]`).
4. **Resumen de Cierre:** Incluir siempre al pie de la tabla un micro-resumen de 1 viñeta por variante para decisión inmediata.

┌────────────────────────────────────────────────────────────────────────┐
│ FASE 2: MODELADO MATEMÁTICO & CONTRATO STRATEGYSPECIFICATION           │
│ 1. Fundamentar en literatura canónica (RAG 1: Libros_Validados).       │
│ 2. Asignar Strategy UUID canónico: STRAT-YYYYMMDD-[NOMBRE]-[TF]-vX.X.  │
│ 3. Definir Z-Score MTF Diario (ATR 5 vs 14) según López de Prado.      │
│ 4. Definir Triple Barrier Method: Take Profit = P_entry ± k1*ATR_D(14) │
│    con ATR Diario cerrado (shift 1).                                   │
│ 5. Generar y validar el archivo JSON formal StrategySpecification.     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Contrato JSON validado)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 3: ENJAMBRE DE DESARROLLADORES (ESTÁNDAR DE 7 BLOQUES)            │
│ 1. Escribir código nativo en Pine Script v6 (TradingView).             │
│ 2. Escribir código POO con CTrade en MQL5 (MetaTrader 5).              │
│ 3. Respetar estrictamente los 7 bloques de arquitectura.               │
│ 4. Garantizar paridad matemática cruzada y 0 repainting (shift 1).     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Código validado sin advertencias)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 4: ENTREGABLES, TELEMETRÍA, FACTSHEET & BITÁCORA                  │
│ 1. Guardar scripts (.pine y .mq5).                                     │
│ 2. Completar y generar STRATEGY_FACTSHEET.md.                          │
│ 3. Actualizar quant_agentic_swarm/STRATEGY_REGISTRY.json.              │
│ 4. Registrar la sesión de trabajo en BITACORA.md.                      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Matriz de Enrutamiento de Conocimiento

Antes de responder o escribir código, consulta el recurso especializado del módulo correspondiente:

| Dominio | Directorio / Archivo de Consulta | Enfoque Principal |
| :--- | :--- | :--- |
| **Literatura Cuantitativa & Fórmulas** | [`Libros_Validados/LLM_INDEX.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/Libros_Validados/LLM_INDEX.md) | Consulta de autores clásicos (Kaufman, Crabel, López de Prado, Aronson, Connors, Wyckoff). |
| **Orquestación & Swarm** | [`quant_agentic_swarm/docs/`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/docs) | Arquitectura del enjambre, interacción HITL, estándar de 7 bloques y esquemas JSON. |
| **TradingView & Pine Script** | [`TradingView/knowledge/`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/TradingView/knowledge) & [`TradingView/GEMINI.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/TradingView/GEMINI.md) | Estándar Pine Script v6, tipos UDT, anti-repainting, márgenes de futuros y buffers gráficos. |
| **MetaTrader 5 & MQL5** | [`MT5/knowledge/`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/knowledge) & [`MT5/AGENTS.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/AGENTS.md) | MQL5 POO, `CTrade`, sincronización `IsNewBar()`, API REST FastAPI y scripts de análisis. |
| **Optimización Cuantitativa & Salidas** | [`quant_agentic_swarm/docs/OPTIMIZATION_PROTOCOL.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/docs/OPTIMIZATION_PROTOCOL.md) | Protocolo canónico de 5 pilares: MAE/MFE, Grid Search en ATR, Meseta de Robustez y Validación In-Sample/Out-of-Sample. |

---

## 4. Reglas Técnicas y de Seguridad

### 4.1. Autoría Institucional Obligatoria
Todo script, archivo de configuración, documentación técnica o encabezado de código generado debe declarar explícitamente como autor:
**`QRT Solutions`**

### 4.2. Pureza de Investigación
- **PROHIBIDO:** Incluir filtros pasivos no solicitados (como filtros de spread en pips, corte por gaps de fin de semana o filtros de noticias económicas) durante la formulación inicial de hipótesis y backtest.
- Las hipótesis deben evaluarse en su pureza estadística antes de aplicar capas de microestructura en vivo.

### 4.3. Estándar de Código Pine Script v6
- Iniciar siempre con `//@version=6`.
- Siempre declarar `lookahead = barmerge.lookahead_off` en `request.security()`.
- En índices/futuros CME configurar margen al 5%: `margin_long = 5.0, margin_short = 5.0`.
- Para medianas rodantes usar `ta.percentile_nearest_rank(source, length, 50)` (evitar funciones inexistentes como `ta.median()`).
- Utilizar buffers verticales dinámicos basados en ATR para etiquetas y dibujos.

### 4.4. Estándar de Código MQL5 POO
- Emplear la librería estándar orientada a objetos: `#include <Trade\Trade.mqh>`.
- Control estricto de ejecuciones al cierre de vela mediante la función `IsNewBar()` en `OnTick()`.
- Consulta segura de datos diarios desde `shift = 1` para cálculo de ATR y Z-Score.

### 4.5. Error Masking en Python
Al escribir bloques de manejo de excepciones (`except`) en Python (para el gateway MT5, scripts cuantitativos o notebooks):
- **SIEMPRE** usar `type(err).__name__` en lugar de `str(err)` para prevenir fugas de información interna.
- Incluir sufijo descriptivo `(detalles omitidos por seguridad)` en logs de error.
- **Patrón estándar**:
  ```python
  except Exception as err:
      logger.error(f"Error en {context}: {type(err).__name__} (detalles omitidos por seguridad)")
      return {"error": f"Error de operación: {type(err).__name__}"}
  ```

### 4.6. Seguridad de Credenciales y Archivos Pesados
- **NUNCA** hardcodear contraseñas de cuentas, llaves API o tokens en archivos versionados.
- **NUNCA** descargar archivos de video o datasets gigantes que saturen el espacio de trabajo local.

### 4.7. Estándar Obligatorio de Evaluación y Reportes de Backtesting (Pool de 3 Módulos)
Cada vez que el usuario solicite auditar, reportar o analizar los resultados de backtesting de **cualquier activo o estrategia** (en MT5, Python o TradingView), el agente debe presentar **obligatoriamente y sin excepción** el informe estructurado bajo el **Pool Completo de 3 Módulos de Diagnóstico Cuantitativo**, conforme a la guía canónica [`MT5/BACKTEST_AUDIT_MANUAL.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/MT5/BACKTEST_AUDIT_MANUAL.md):

#### Frases Disparadoras Reconocidas (Cómo lo solicita el usuario):
- *"Audita el backtest de [activo/estrategia] con el pool completo de 3 módulos."*
- *"Genera el reporte de backtest con evaluación dual y asimetrías."*
- *"Analiza los KPIs de este backtest."* o *"Dame el reporte cuantitativo de este backtest."*
- O simplemente: *"Analiza este backtest."*

#### Los 3 Módulos Obligatorios del Reporte:
1. **Módulo 1: La Evaluación Dual (Monetario vs Retorno Porcentual Puro):**
   - **Capa Monetaria (USD):** PnL Neto, Saldo final, Profit Factor monetario, Win Rate, Ganancia y Pérdida media en USD.
   - **Capa Porcentual Pura (% Precio del Activo):** Retorno porcentual acumulado ($\sum R_i$) y compuesto ($\prod (1 + R_i) - 1$), Profit Factor %, Payoff % y Drawdown Máximo %.
2. **Módulo 2: Diagnóstico de Asimetrías (¿Dónde está el Edge?):**
   - **Desglose Direccional Mandatorio:** Tabla comparativa obligatoria entre **Compras (Longs)** y **Ventas (Shorts)** (*Elder & Kaufman*).
   - **Esperanza Matemática por Trade ($E$):** $E = (WR \times \text{Avg Win \%}) - (LR \times \text{Avg Loss \%})$ (*Minervini & Van Tharp*).
   - **Consistencia Temporal:** Porcentaje de meses positivos sobre el total evaluado (*Aronson & Kaufman*).
3. **Módulo 3: Diagnóstico de Ejecución y Salidas (¿Cómo Optimizar?):**
   - **Excursión Adversa y Favorable (MAE / MFE):** Calibración empírica de Stops y Targets (*Sweeney & López de Prado*).
   - **Tiempo de Permanencia (Time-Stop):** Duración media en barras intradiarias de ganadores vs perdedores (*Crabel*).
   - **Racha Máxima de Pérdidas y Circuit Breaker:** Conteo de pérdidas continuas y freno automático (*Weissman & Elder*).

#### Triada Gráfica Obligatoria (3 Gráficos Mandatorios):
Además de los 3 módulos tabulares, cada reporte cuantitativo debe generar e incorporar **obligatoriamente y sin excepción** los siguientes 3 artefactos visuales:
1. **Curva de Equity (Capital Growth Curve):** Gráfico de línea temporal que muestra la evolución acumulada de la curva de balance/equidad a lo largo del tiempo y número de operaciones.
2. **Gráfico de Drawdown (Underwater Chart):** Gráfico de área submarina que expone con precisión la profundidad y duración temporal de cada retroceso de capital desde máximos históricos.
3. **Gráfico de Excursiones (MAE vs MFE Scatter Plot):** Gráfico de dispersión bidimensional que mapea la Máxima Excursión Adversa (eje X en múltiplos de ATR) versus la Máxima Excursión Favorable (eje Y en múltiplos de ATR) por cada operación, integrando las líneas de referencia del percentil 90 de MAE y la masa modal de MFE para sustentar la calibración de Stops y Targets.

### 4.8. Estándar Obligatorio de Optimización Cuantitativa (Meseta de Robustez & MAE/MFE)
Cada vez que el usuario solicite calibrar, optimizar o mejorar los parámetros de **cualquier estrategia o activo** (en MT5, Python o TradingView), el agente debe someterse **sin excepción** al protocolo canónico documentado en [`quant_agentic_swarm/docs/OPTIMIZATION_PROTOCOL.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/quant_agentic_swarm/docs/OPTIMIZATION_PROTOCOL.md).

#### Frases Disparadoras Reconocidas (Cómo lo solicita el usuario):
- *"Optimiza los parámetros de [estrategia/activo]."*
- *"Busca los mejores parámetros."* o *"Calibra el stop y el target."*
- *"Mejora los resultados con la metodología de optimización."*
- *"Aplica optimización a esta estrategia."*

#### Los 5 Mandatos Ineludibles de Optimización:
1. **Prohibición Estricta de Picos Aislados (Anti-Spikes Manifesto):**
   * Queda terminantemente prohibido elegir parámetros basándose en el "máximo Sharpe aislado" o "mayor beneficio neto de la cuadrícula".
   * El agente debe identificar la región continua donde $S \ge 0.80 \times S_{\max}$ y **seleccionar obligatoriamente el baricentro (centro geométrico) de la meseta plana de estabilidad paramétrica** (*Robert Pardo & Perry Kaufman*).
2. **Normalización Mandatoria por Volatilidad (ATR):**
   * Todo Stop Loss, Take Profit y disparador de trailing debe formularse y optimizarse en **múltiplos limpios de ATR** (ej. $1.0\times\text{ATR}$, $1.25\times\text{ATR}$). Prohibido optimizar puntos o ticks fijos para asegurar la invarianza temporal.
3. **Calibración Empírica por Excursiones (MAE / MFE):**
   * El Stop Loss inicial debe sustentarse en el **percentil 90 del MAE de operaciones ganadoras** ($P_{90}(\text{MAE}_{\text{wins}})$) (*Sweeney*).
   * El Take Profit debe anclarse en la **mediana o masa modal de la densidad de MFE**, descartando targets inalcanzables en la cola extrema (*Crabel*).
4. **Validación Temporal Cruzada In-Sample vs Out-of-Sample (Split Ciego):**
   * Partición temporal obligatoria reservando al menos el 20% más reciente de datos como conjunto ciego (*Out-of-Sample*).
   * Cálculo y presentación obligatoria del **Semáforo de Degradación Paramétrica** (*López de Prado*):
     $$\text{Degradación} = \frac{|\text{Sharpe}_{\text{IS}} - \text{Sharpe}_{\text{OOS}}|}{\text{Sharpe}_{\text{IS}}} \times 100 \le 30\% \quad (\text{Zona Verde})$$
   * Si la degradación supera el 50% o el Sharpe OOS cae por debajo de 0.50, la optimización se declara nula o sobreajustada.
5. **Capa Dinámica de Protección de Capital:**
   * Toda estrategia optimizada debe incluir un **Breakeven elástico** (gatillado fuera del ruido de apertura) y un **Circuit Breaker mensual** (freno automático tras 3 pérdidas consecutivas en el mes) (*Elder & Van Tharp*).

---

## 5. Mantenimiento Obligatorio de la Bitácora (`BITACORA.md`)

Es un **mandato operativo estricto** que al finalizar cada sesión de trabajo, o tras completar un hito lógico relevante, el agente debe documentar los cambios en el archivo [`BITACORA.md`](file:///Users/fmillar/Proyectos_Desarrollo/seminario_2/BITACORA.md) ubicado en la raíz del proyecto.

### Formato de Entrada Requerido:
Cada entrada debe insertarse en orden cronológico inverso (la más reciente arriba):

```markdown
## [AAAA-MM-DD] - Sesión de Trabajo: [Nombre Corto de la Sesión]
**Objetivo:** Breve descripción del propósito de la sesión.

### [OK] Cambios Realizados:
- **[Componente/Archivo]**: Qué se hizo y por qué.
- [Enlace a los archivos creados/modificados utilizando markdown links (file://)]

### Decisiones y Notas de Diseño:
- Explicación de decisiones técnicas clave o cambios en la arquitectura.

### Pendientes y Siguientes Pasos:
- Tareas pendientes que deben ser abordadas en la próxima sesión.
```
