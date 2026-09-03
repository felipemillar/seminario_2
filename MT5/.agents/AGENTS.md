# Reglas de Proyecto: MT5

## Regla: Distinción de Proyectos MT5 vs GIF (Grupo Inteligencia)

Cuando el usuario hable del "servidor" o de "Grupo Inteligencia", debes distinguir claramente entre dos contextos:

1. **Proyecto GIF (Grupo Inteligencia / Business Intelligence):**
   - **Propósito:** Análisis de datos masivos, extracción de reportes, riesgo y dashboards HTML estáticos.
   - **Servidor al que se refiere:** Servidor SQL remoto (`185.56.138.170`, DB: `MT5`) consultado mediante `pymssql` en Python.
   - **Archivos clave:** Dashboards HTML, archivos CSV, y el Excel maestro `GI 01-02-2025...`.

2. **Proyecto MT5 (Gateway Local):**
   - **Propósito:** API REST FastAPI local para interconectar scripts Python en macOS con el terminal MetaTrader 5 (vía librería de Windows).
   - **Servidor al que se refiere:** Máquina virtual local Parallels (`10.211.55.4:8000`).
   - **Nota:** En este proyecto "grupointeligencia" es solo un alias de broker para `SwitchAccountRequest`, NO el objetivo analítico principal.

**Por defecto:** Si el usuario menciona "servidor de Grupo Inteligencia" o "servidor GIF", asume que es el entorno remoto de base de datos SQL, a menos que el usuario esté debugeando activamente endpoints de FastAPI local.
