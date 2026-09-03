"""
Consulta completa del broker: instrumentos + swaps.
Auto-detecta el broker conectado y guarda en carpeta separada.

Uso: python fetch_broker_data.py
"""
import requests
import json
import csv
from pathlib import Path
from query_utils import GATEWAY_URL, print_broker_header, get_output_dir


def fetch_symbols(output_dir: Path):
    """Obtiene todos los instrumentos del broker."""
    print("\n[1/2] Obteniendo lista de instrumentos...")
    try:
        r = requests.get(f"{GATEWAY_URL}/symbols", timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as err:
        print(f"  [ERROR] Error: {type(err).__name__}")
        return None

    # Guardar JSON
    with open(output_dir / "symbols.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Guardar CSV
    symbols = data.get("symbols", [])
    if symbols:
        with open(output_dir / "symbols.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=symbols[0].keys())
            writer.writeheader()
            writer.writerows(symbols)

    print(f"  [OK] {data['count']} instrumentos obtenidos")
    return data


def fetch_swaps(output_dir: Path):
    """Obtiene swap costs de todos los instrumentos."""
    print("[2/2] Obteniendo swap costs...")
    try:
        r = requests.get(f"{GATEWAY_URL}/symbols/swap_scan", timeout=120)
        r.raise_for_status()
        data = r.json()
    except Exception as err:
        print(f"  [ERROR] Error: {type(err).__name__}")
        return None

    results = data.get("results", [])

    # Guardar JSON
    with open(output_dir / "swap_scan.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Guardar CSV
    if results:
        fieldnames = ["symbol", "description", "category", "price",
                       "swap_long", "swap_short", "swap_mode_desc",
                       "swap_rollover3days", "currency_base", "currency_profit",
                       "trade_contract_size"]
        with open(output_dir / "swap_scan.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)

    print(f"  [OK] {data['count']} instrumentos con swap data")
    return data


def print_summary(symbols_data, swap_data, output_dir):
    """Imprime resumen consolidado."""
    if not symbols_data or not swap_data:
        return

    print(f"\n{'=' * 60}")
    print(f"RESUMEN DEL BROKER")
    print(f"{'=' * 60}")
    print(f"  Instrumentos totales:  {symbols_data['count']}")
    print(f"  Con datos de swap:     {swap_data['count']}")

    # Categorías
    results = swap_data.get("results", [])
    categories = {}
    for r in results:
        cat = r["category"].split("\\")[0] if "\\" in r["category"] else r["category"]
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

    print(f"\n  Por clase de activo:")
    for cat in sorted(categories.keys(), key=lambda c: -categories[c]):
        print(f"    {cat:<25} {categories[cat]:>5}")

    # Swaps disabled
    disabled = sum(1 for r in results if r["swap_mode_desc"] == "Disabled")
    print(f"\n  Swaps desactivados:    {disabled}")

    # Top 5 carry trade
    positive = [r for r in results if r["swap_long"] > 0 or r["swap_short"] > 0]
    if positive:
        print(f"\n  Top 5 Carry Trade (swap positivo):")
        sorted_pos = sorted(positive, key=lambda x: max(x["swap_long"], x["swap_short"]), reverse=True)
        for r in sorted_pos[:5]:
            direction = "Long" if r["swap_long"] > max(0, r["swap_short"]) else "Short"
            val = r["swap_long"] if direction == "Long" else r["swap_short"]
            print(f"    {r['symbol']:<16} {direction:<6} → +{val:.2f}")

    print(f"\nDatos guardados en: {output_dir}")
    print(f"{'=' * 60}")


def main():
    info = print_broker_header()
    if not info:
        print("[ERROR] No se pudo conectar al Gateway. ¿Está corriendo en Windows?")
        return

    output_dir = get_output_dir()
    print(f"Output: {output_dir}\n")

    symbols_data = fetch_symbols(output_dir)
    swap_data = fetch_swaps(output_dir)
    print_summary(symbols_data, swap_data, output_dir)


if __name__ == "__main__":
    main()
