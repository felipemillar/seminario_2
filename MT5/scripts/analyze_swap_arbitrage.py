"""
Arbitraje de Swaps entre Brokers
Busca combinaciones donde estar Long en un broker y Short en otro
genera un diferencial neto positivo (ganancia sin exposición al mercado).

Uso: python analyze_swap_arbitrage.py
"""
import json
from pathlib import Path
from itertools import combinations

DATA_DIR = Path(__file__).parent.parent / "data" / "queries"

BROKERS = {
    "Pepperstone": DATA_DIR / "2026-06-29" / "swap_scan.json",
    "GrupoInteligencia": DATA_DIR / "grupointeligenciaspa-server" / "2026-06-29" / "swap_scan.json",
    "Capitaria": DATA_DIR / "capitaria-all" / "2026-06-29" / "swap_scan.json",
}


def load_swap_data():
    """Carga datos de swap de todos los brokers como dict {symbol: data}."""
    all_data = {}
    for broker, path in BROKERS.items():
        if not path.exists():
            print(f"  [ADVERTENCIA]  No se encontró data de {broker}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        symbol_map = {}
        for r in raw.get("results", []):
            # Normalizar nombre del símbolo (quitar sufijos como .spot)
            sym = r["symbol"].upper().replace(".SPOT", "").replace("-","")
            symbol_map[sym] = {
                "symbol_original": r["symbol"],
                "swap_long": r["swap_long"],
                "swap_short": r["swap_short"],
                "swap_mode": r["swap_mode_desc"],
                "description": r["description"],
                "category": r["category"],
                "price": r.get("price"),
                "contract_size": r["trade_contract_size"],
                "digits": r.get("digits", 5),
            }
        all_data[broker] = symbol_map
        print(f"  [OK] {broker}: {len(symbol_map)} símbolos cargados")
    return all_data


def find_arbitrage_opportunities(all_data):
    """
    Para cada par de brokers y cada símbolo en común:
    - Escenario A: Long en Broker1 + Short en Broker2 → net = swap_long(B1) + swap_short(B2)
    - Escenario B: Short en Broker1 + Long en Broker2 → net = swap_short(B1) + swap_long(B2)
    
    Si net > 0, hay oportunidad de arbitraje.
    
    IMPORTANTE: Solo comparamos instrumentos con el MISMO swap_mode.
    """
    opportunities = []

    broker_pairs = list(combinations(all_data.keys(), 2))

    for b1, b2 in broker_pairs:
        data1 = all_data[b1]
        data2 = all_data[b2]

        # Encontrar símbolos comunes
        common = set(data1.keys()) & set(data2.keys())

        for sym in common:
            d1 = data1[sym]
            d2 = data2[sym]

            # Solo comparar si ambos tienen swap activo
            if d1["swap_mode"] == "Disabled" or d2["swap_mode"] == "Disabled":
                continue

            # Escenario A: Long B1 + Short B2
            net_a = d1["swap_long"] + d2["swap_short"]
            # Escenario B: Short B1 + Long B2
            net_b = d1["swap_short"] + d2["swap_long"]

            if net_a > 0:
                opportunities.append({
                    "symbol": sym,
                    "symbol_b1": d1["symbol_original"],
                    "symbol_b2": d2["symbol_original"],
                    "description": d1["description"],
                    "category": d1["category"],
                    "long_broker": b1,
                    "short_broker": b2,
                    "swap_long_val": d1["swap_long"],
                    "swap_short_val": d2["swap_short"],
                    "net_daily": round(net_a, 4),
                    "swap_mode_b1": d1["swap_mode"],
                    "swap_mode_b2": d2["swap_mode"],
                    "same_mode": d1["swap_mode"] == d2["swap_mode"],
                    "price_b1": d1["price"],
                    "price_b2": d2["price"],
                    "contract_size": d1["contract_size"],
                })

            if net_b > 0:
                opportunities.append({
                    "symbol": sym,
                    "symbol_b1": d1["symbol_original"],
                    "symbol_b2": d2["symbol_original"],
                    "description": d1["description"],
                    "category": d1["category"],
                    "long_broker": b2,
                    "short_broker": b1,
                    "swap_long_val": d2["swap_long"],
                    "swap_short_val": d1["swap_short"],
                    "net_daily": round(net_b, 4),
                    "swap_mode_b1": d2["swap_mode"],
                    "swap_mode_b2": d1["swap_mode"],
                    "same_mode": d1["swap_mode"] == d2["swap_mode"],
                    "price_b1": d2["price"],
                    "price_b2": d1["price"],
                    "contract_size": d1["contract_size"],
                })

    # Ordenar por net diario descendente
    opportunities.sort(key=lambda x: x["net_daily"], reverse=True)
    return opportunities


def main():
    print("=" * 90)
    print("ARBITRAJE DE SWAPS — Búsqueda de Diferenciales entre Brokers")
    print("=" * 90)
    print("\nCargando datos de swap:")

    all_data = load_swap_data()
    if len(all_data) < 2:
        print("[ERROR] Se necesitan al menos 2 brokers para comparar")
        return

    # Estadísticas de símbolos comunes
    print(f"\nSímbolos comunes entre brokers:")
    broker_list = list(all_data.keys())
    for i, b1 in enumerate(broker_list):
        for b2 in broker_list[i+1:]:
            common = set(all_data[b1].keys()) & set(all_data[b2].keys())
            print(f"  {b1} ∩ {b2}: {len(common)} símbolos en común")

    # Buscar oportunidades
    opportunities = find_arbitrage_opportunities(all_data)

    if not opportunities:
        print("\n[ERROR] No se encontraron oportunidades de arbitraje")
        return

    # Filtrar solo las que tienen el mismo swap_mode (comparación válida)
    same_mode = [o for o in opportunities if o["same_mode"]]
    diff_mode = [o for o in opportunities if not o["same_mode"]]

    # === RESULTADOS CON MISMO MODO DE SWAP (más confiables) ===
    print(f"\n{'=' * 90}")
    print(f"[OK] OPORTUNIDADES CONFIABLES — Mismo modo de swap ({len(same_mode)} encontradas)")
    print(f"{'=' * 90}")
    if same_mode:
        print(f"{'#':>3}  {'Symbol':<12} {'Long en':<18} {'Short en':<18} "
              f"{'Swap L':>10} {'Swap S':>10} {'NET/día':>10} {'NET/mes':>10} {'Modo'}")
        print("-" * 110)
        for i, o in enumerate(same_mode, 1):
            net_month = o["net_daily"] * 30
            print(f"{i:>3}  {o['symbol']:<12} {o['long_broker']:<18} {o['short_broker']:<18} "
                  f"{o['swap_long_val']:>+10.2f} {o['swap_short_val']:>+10.2f} "
                  f"{o['net_daily']:>+10.2f} {net_month:>+10.1f} {o['swap_mode_b1']}")
    else:
        print("  Ninguna con el mismo modo de swap.")

    # === RESULTADOS CON DIFERENTE MODO (requiere conversión manual) ===
    if diff_mode:
        print(f"\n{'=' * 90}")
        print(f"[ADVERTENCIA]  OPORTUNIDADES POTENCIALES — Diferente modo de swap ({len(diff_mode)})")
        print(f"   (Requieren conversión de unidades para validar)")
        print(f"{'=' * 90}")
        print(f"{'#':>3}  {'Symbol':<12} {'Long en':<18} {'Short en':<18} "
              f"{'Swap L':>10} {'Swap S':>10} {'NET':>10} {'Modo L':<12} {'Modo S'}")
        print("-" * 115)
        for i, o in enumerate(diff_mode[:30], 1):
            print(f"{i:>3}  {o['symbol']:<12} {o['long_broker']:<18} {o['short_broker']:<18} "
                  f"{o['swap_long_val']:>+10.2f} {o['swap_short_val']:>+10.2f} "
                  f"{o['net_daily']:>+10.2f} {o['swap_mode_b1']:<12} {o['swap_mode_b2']}")

    # Guardar resultados
    output_file = DATA_DIR / "swap_arbitrage.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "same_mode_opportunities": same_mode,
            "different_mode_opportunities": diff_mode,
            "total": len(opportunities),
        }, f, indent=2, ensure_ascii=False)

    print(f"\nResultados guardados en: {output_file}")
    print(f"\n{'=' * 90}")
    print(f"RESUMEN")
    print(f"   Oportunidades confiables (mismo modo): {len(same_mode)}")
    print(f"   Oportunidades potenciales (diff modo): {len(diff_mode)}")
    print(f"{'=' * 90}")


if __name__ == "__main__":
    main()
