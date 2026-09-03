"""
Análisis de carry trade: identifica todos los instrumentos con swap positivo
en ambos brokers y los compara.

Uso: python analyze_carry_trade.py
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "queries"

BROKERS = {
    "Pepperstone": DATA_DIR / "2026-06-29" / "swap_scan.json",
    "GrupoInteligencia": DATA_DIR / "grupointeligenciaspa-server" / "2026-06-29" / "swap_scan.json",
    "Capitaria": DATA_DIR / "capitaria-all" / "2026-06-29" / "swap_scan.json",
}


def load_broker_data(name, path):
    """Carga datos de swap de un broker."""
    if not path.exists():
        print(f"  [ADVERTENCIA]  No se encontró data de {name} en {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("results", [])


def find_positive_swaps(results, broker_name):
    """Encuentra todos los instrumentos con swap positivo."""
    opportunities = []
    for r in results:
        if r["swap_long"] > 0:
            opportunities.append({
                "broker": broker_name,
                "symbol": r["symbol"],
                "description": r["description"],
                "category": r["category"],
                "direction": "LONG",
                "swap_earn": r["swap_long"],
                "swap_cost_opposite": r["swap_short"],
                "swap_mode": r["swap_mode_desc"],
                "price": r.get("price"),
                "contract_size": r["trade_contract_size"],
                "rollover_3days": r.get("swap_rollover3days", "?"),
            })
        if r["swap_short"] > 0:
            opportunities.append({
                "broker": broker_name,
                "symbol": r["symbol"],
                "description": r["description"],
                "category": r["category"],
                "direction": "SHORT",
                "swap_earn": r["swap_short"],
                "swap_cost_opposite": r["swap_long"],
                "swap_mode": r["swap_mode_desc"],
                "price": r.get("price"),
                "contract_size": r["trade_contract_size"],
                "rollover_3days": r.get("swap_rollover3days", "?"),
            })
    return opportunities


def main():
    print("=" * 80)
    print("ANÁLISIS DE CARRY TRADE — Instrumentos con Swap Positivo")
    print("=" * 80)

    all_opportunities = []

    for broker_name, path in BROKERS.items():
        results = load_broker_data(broker_name, path)
        if not results:
            continue
        opps = find_positive_swaps(results, broker_name)
        all_opportunities.extend(opps)
        print(f"\n{broker_name}: {len(results)} instrumentos → {len(opps)} oportunidades de swap positivo")

    if not all_opportunities:
        print("\n[ERROR] No se encontraron oportunidades de swap positivo")
        return

    # Ordenar por swap ganado (descendente)
    all_opportunities.sort(key=lambda x: x["swap_earn"], reverse=True)

    # Tabla completa
    print(f"\n{'=' * 80}")
    print(f"TODAS LAS OPORTUNIDADES DE CARRY TRADE ({len(all_opportunities)} total)")
    print(f"{'=' * 80}")
    print(f"{'#':>3}  {'Broker':<18} {'Symbol':<16} {'Dir':<6} {'Swap Ganado':>12} "
          f"{'Swap Opuesto':>12} {'Modo':<12} {'Categoría'}")
    print("-" * 105)

    for i, o in enumerate(all_opportunities, 1):
        print(f"{i:>3}  {o['broker']:<18} {o['symbol']:<16} {o['direction']:<6} "
              f"{o['swap_earn']:>+12.2f} {o['swap_cost_opposite']:>+12.2f} "
              f"{o['swap_mode']:<12} {o['category']}")

    # Análisis por broker
    print(f"\n{'=' * 80}")
    print(f"RESUMEN POR BROKER")
    print(f"{'=' * 80}")
    for broker in BROKERS.keys():
        broker_opps = [o for o in all_opportunities if o["broker"] == broker]
        longs = [o for o in broker_opps if o["direction"] == "LONG"]
        shorts = [o for o in broker_opps if o["direction"] == "SHORT"]
        print(f"\n  {broker}:")
        print(f"     Total oportunidades: {len(broker_opps)}")
        print(f"     Long con swap +: {len(longs)}")
        print(f"     Short con swap +: {len(shorts)}")
        if broker_opps:
            best = broker_opps[0] if broker_opps[0]["swap_earn"] == max(o["swap_earn"] for o in broker_opps) else max(broker_opps, key=lambda x: x["swap_earn"])
            print(f"     Mejor: {best['symbol']} {best['direction']} → +{best['swap_earn']:.2f}")

    # Instrumentos comunes (carry trade en ambos brokers)
    print(f"\n{'=' * 80}")
    print(f"COMPARACIÓN — Mismo símbolo en ambos brokers")
    print(f"{'=' * 80}")

    symbols_by_broker = {}
    for o in all_opportunities:
        key = (o["symbol"], o["direction"])
        if key not in symbols_by_broker:
            symbols_by_broker[key] = {}
        symbols_by_broker[key][o["broker"]] = o["swap_earn"]

    common = {k: v for k, v in symbols_by_broker.items() if len(v) > 1}
    if common:
        print(f"{'Symbol':<16} {'Dir':<6}", end="")
        for b in BROKERS.keys():
            print(f" {b:>18}", end="")
        print(f" {'Diferencia':>12}")
        print("-" * 75)
        for (sym, direction), brokers in sorted(common.items()):
            vals = list(brokers.values())
            diff = abs(vals[0] - vals[1])
            print(f"{sym:<16} {direction:<6}", end="")
            for b in BROKERS.keys():
                val = brokers.get(b, 0)
                print(f" {val:>+18.2f}", end="")
            print(f" {diff:>12.2f}")
    else:
        print("  No hay instrumentos con swap positivo en la misma dirección en ambos brokers.")

    # Guardar resultados
    output_file = DATA_DIR / "carry_trade_analysis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_opportunities, f, indent=2, ensure_ascii=False)
    print(f"\nAnálisis guardado en: {output_file}")


if __name__ == "__main__":
    main()
