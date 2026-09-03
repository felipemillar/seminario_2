"""
Consulta los costos de swap (long/short) de todos los instrumentos del broker.
Los swaps son datos estáticos del contrato — funcionan con mercados cerrados.

Uso: python fetch_swap_scan.py
"""
import requests
import json
import csv
from pathlib import Path
from datetime import datetime

GATEWAY_URL = "http://10.211.55.4:8000"
BASE_DIR = Path(__file__).parent.parent / "data" / "queries"


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = BASE_DIR / today
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Consultando swap costs de todos los instrumentos...")

    try:
        r = requests.get(f"{GATEWAY_URL}/symbols/swap_scan", timeout=120)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar al Gateway. ¿Está corriendo en Windows?")
        return
    except Exception as err:
        print(f"[ERROR] Error: {type(err).__name__}")
        return

    results = data.get("results", [])

    # Guardar JSON
    json_file = output_dir / "swap_scan.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Guardar CSV
    csv_file = output_dir / "swap_scan.csv"
    if results:
        fieldnames = ["symbol", "description", "category", "price",
                       "swap_long", "swap_short", "swap_mode_desc",
                       "swap_rollover3days", "currency_base", "currency_profit",
                       "trade_contract_size"]
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)

    # Resumen
    print(f"\n[OK] {data['count']} instrumentos escaneados")
    print(f"JSON: {json_file}")
    print(f"CSV:  {csv_file}\n")

    # Estadísticas por modo de swap
    modes = {}
    for r_item in results:
        mode = r_item["swap_mode_desc"]
        if mode not in modes:
            modes[mode] = 0
        modes[mode] += 1

    print("Distribución por tipo de swap:")
    print("-" * 45)
    for mode, count in sorted(modes.items(), key=lambda x: -x[1]):
        print(f"  {mode:<35} {count:>5}")

    # Top 15 swaps más costosos (long)
    print(f"\nTop 15 — Swap Long más costoso (negativo = tú pagas):")
    print(f"{'#':>3}  {'Symbol':<16} {'Category':<25} {'Swap Long':>12} {'Swap Short':>12} {'Mode'}")
    print("-" * 90)
    # Ordenar por swap_long más negativo
    sorted_long = sorted(results, key=lambda x: x["swap_long"])
    for i, r_item in enumerate(sorted_long[:15], 1):
        print(f"{i:>3}  {r_item['symbol']:<16} {r_item['category']:<25} "
              f"{r_item['swap_long']:>12.4f} {r_item['swap_short']:>12.4f} "
              f"{r_item['swap_mode_desc']}")

    # Top 15 swaps positivos (te pagan)
    positive = [r_item for r_item in results if r_item["swap_long"] > 0 or r_item["swap_short"] > 0]
    if positive:
        print(f"\nTop 15 — Swaps positivos (el broker te paga):")
        print(f"{'#':>3}  {'Symbol':<16} {'Category':<25} {'Swap Long':>12} {'Swap Short':>12}")
        print("-" * 75)
        # Mejor swap positivo
        sorted_positive = sorted(positive, key=lambda x: max(x["swap_long"], x["swap_short"]), reverse=True)
        for i, r_item in enumerate(sorted_positive[:15], 1):
            print(f"{i:>3}  {r_item['symbol']:<16} {r_item['category']:<25} "
                  f"{r_item['swap_long']:>12.4f} {r_item['swap_short']:>12.4f}")

    # Resumen por categoría
    print(f"\nSwap promedio por categoría:")
    print(f"{'Category':<35} {'Count':>6} {'Avg Swap L':>12} {'Avg Swap S':>12}")
    print("-" * 70)

    cat_data = {}
    for r_item in results:
        cat = r_item["category"]
        if cat not in cat_data:
            cat_data[cat] = {"long": [], "short": []}
        cat_data[cat]["long"].append(r_item["swap_long"])
        cat_data[cat]["short"].append(r_item["swap_short"])

    for cat in sorted(cat_data.keys()):
        longs = cat_data[cat]["long"]
        shorts = cat_data[cat]["short"]
        avg_l = sum(longs) / len(longs)
        avg_s = sum(shorts) / len(shorts)
        print(f"  {cat:<33} {len(longs):>6} {avg_l:>12.4f} {avg_s:>12.4f}")


if __name__ == "__main__":
    main()
