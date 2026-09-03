# Reglas del Asistente IA — TradingView Quant Suite

Este archivo define las directrices y reglas operativas para cualquier agente o modelo de IA que interactúe con este repositorio.

---

## 1. Autoría Institucional
Todo código, script, skill de agente, comentario y documento debe declarar como autor explícito:
**`QRT Solutions`**

---

## 2. Acceso a la Base de Conocimiento
El proyecto cuenta con **31 manuales técnicos exhaustivos en `knowledge/`**. 
Para consultar cualquier tema (Pine Script v6, data feeds, webhooks, WSS websocket, Python integration, order flow, validación, sizing):
- Consulta primero `.agents/skills/tradingview-knowledge-navigator/SKILL.md` y su catálogo de referencias.
- Cita siempre el documento correspondiente en tus explicaciones.

---

## 3. Normas de Programación en Pine Script v6
- Iniciar siempre con `//@version=6`.
- Cero lookahead en `request.security()` (`lookahead = barmerge.lookahead_off`).
- Margen de futuros CME: `margin_long = 5.0, margin_short = 5.0` en `strategy()`.
- Mediana rodante: Usar `ta.percentile_nearest_rank(source, length, 50)`.
- Manejo de buffers verticales para etiquetas con `vBuffer` basado en ATR.
