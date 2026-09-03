# pandas_ta_classic

Siempre usar `pandas_ta_classic` en lugar de `pandas_ta`. La librería `pandas_ta` no funciona correctamente en el entorno del usuario.

```python
# Correcto
import pandas_ta_classic as ta

# Incorrecto — NO usar
import pandas_ta as ta
```
