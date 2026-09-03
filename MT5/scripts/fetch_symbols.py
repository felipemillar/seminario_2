"""
Consulta todos los instrumentos del broker via Gateway y guarda el resultado
en un archivo JSON para análisis posterior.

Uso: python fetch_symbols.py
"""
import requests
import json
from pathlib import Path

GATEWAY_URL = "http://10.211.55.4:8000"
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "broker_symbols.json"


def main():
    print("Consultando instrumentos del broker via Gateway...")

    try:
        r = requests.get(f"{GATEWAY_URL}/symbols", timeout=15)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar al Gateway. ¿Está corriendo en Windows?")
        return
    except Exception as err:
        print(f"[ERROR] Error: {type(err).__name__}")
        return

    # Guardar JSON completo
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Resumen en terminal
    print(f"\n[OK] {data['count']} instrumentos obtenidos")
    print(f"Guardado en: {OUTPUT_FILE}\n")
    print("Categorías:")
    print("-" * 50)
    for cat, syms in sorted(data.get("categories", {}).items()):
        print(f"  {cat:30s} → {len(syms):>4} instrumentos")
    print("-" * 50)
    print(f"  {'TOTAL':30s} → {data['count']:>4} instrumentos")


if __name__ == "__main__":
    main()
