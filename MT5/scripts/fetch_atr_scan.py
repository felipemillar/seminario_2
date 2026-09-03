"""
Consulta el ATR Scan del Gateway y guarda los resultados en CSV y JSON.
Incluye: precio actual, ATR(14) D1, ATR% normalizado.

Uso: python fetch_atr_scan.py
"""
import requests
import json
import csv
from pathlib import Path
from datetime import datetime

GATEWAY_URL = "http://10.211.55.4:8000"
OUTPUT_DIR = Path(__file__).parent.parent / "data"


def main():
    print("Ejecutando ATR Scan de todos los instrumentos...")
    print("   (Esto puede tomar 30-60 segundos para 1700+ símbolos)\n")

    try:
        r = requests.get(f"{GATEWAY_URL}/symbols/atr_scan", timeout=600)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar al Gateway. ¿Está corriendo en Windows?")
        return
    except requests.exceptions.ReadTimeout:
        print("[ERROR] Timeout — el scan tarda demasiado. Intenta con un grupo específico.")
        return
    except Exception as err:
        print(f"[ERROR] Error: {type(err).__name__}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Guardar JSON
    json_file = OUTPUT_DIR / "atr_scan.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Guardar CSV
    csv_file = OUTPUT_DIR / "atr_scan.csv"
    results = data.get("results", [])
    if results:
        fieldnames = ["symbol", "description", "category", "price", "bid", "ask",
                       "spread", "atr", "atr_pct", "digits", "contract_size", "price_source"]
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    # Resumen
    print(f"[OK] {data['count']} instrumentos escaneados ({data.get('errors', 0)} errores)")
    print(f"ATR Period: {data.get('atr_period', 14)} | Timeframe: {data.get('timeframe', 'D1')}")
    print(f"JSON: {json_file}")
    print(f"CSV:  {csv_file}\n")

    # Top 20 por ATR%
    print("Top 20 instrumentos por ATR% (mayor volatilidad):")
    print(f"{'#':>3}  {'Symbol':<20} {'Category':<25} {'Price':>12} {'ATR':>12} {'ATR%':>8}")
    print("-" * 85)
    for i, r in enumerate(results[:20], 1):
        print(f"{i:>3}  {r['symbol']:<20} {r['category']:<25} {r['price']:>12} {r['atr']:>12} {r['atr_pct']:>7.2f}%")

    # Bottom 10 (menor volatilidad)
    print(f"\nBottom 10 instrumentos por ATR% (menor volatilidad):")
    print(f"{'#':>3}  {'Symbol':<20} {'Category':<25} {'Price':>12} {'ATR':>12} {'ATR%':>8}")
    print("-" * 85)
    for i, r in enumerate(results[-10:], len(results) - 9):
        print(f"{i:>3}  {r['symbol']:<20} {r['category']:<25} {r['price']:>12} {r['atr']:>12} {r['atr_pct']:>7.2f}%")

    # Resumen por categoría
    print(f"\nATR% promedio por categoría:")
    print(f"{'Category':<35} {'Count':>6} {'Avg ATR%':>10} {'Max ATR%':>10}")
    print("-" * 65)

    cat_data = {}
    for r in results:
        cat = r["category"]
        if cat not in cat_data:
            cat_data[cat] = []
        cat_data[cat].append(r["atr_pct"])

    for cat in sorted(cat_data.keys(), key=lambda c: sum(cat_data[c])/len(cat_data[c]), reverse=True):
        vals = cat_data[cat]
        avg = sum(vals) / len(vals)
        mx = max(vals)
        print(f"  {cat:<33} {len(vals):>6} {avg:>9.2f}% {mx:>9.2f}%")


if __name__ == "__main__":
    main()
