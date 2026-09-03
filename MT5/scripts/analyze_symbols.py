"""
Analiza broker_symbols.json y genera un reporte categorizado.
"""
import json
from pathlib import Path
from collections import defaultdict

DATA_FILE = Path(__file__).parent.parent / "data" / "broker_symbols.json"
REPORT_FILE = Path(__file__).parent.parent / "data" / "symbols_report.json"

with open(DATA_FILE, "r") as f:
    data = json.load(f)

# Categorizar por path completo (ej: Markets\Forex\Majors)
categories = defaultdict(list)
for sym in data["symbols"]:
    path = sym["path"]
    # Extraer categoría sin el nombre del símbolo al final
    parts = path.split("\\")
    if len(parts) >= 3:
        cat = "\\".join(parts[1:-1])  # Quitar "Markets\" y el símbolo
    elif len(parts) == 2:
        cat = parts[0]
    else:
        cat = "Other"
    categories[cat].append({
        "name": sym["name"],
        "description": sym["description"],
        "spread": sym["spread"],
        "digits": sym["digits"],
        "contract_size": sym["trade_contract_size"],
        "vol_min": sym["volume_min"],
        "visible": sym["visible"]
    })

# Generar reporte
report = {
    "total": data["count"],
    "categories_count": len(categories),
    "summary": {}
}

for cat in sorted(categories.keys()):
    syms = categories[cat]
    report["summary"][cat] = {
        "count": len(syms),
        "symbols": [s["name"] for s in syms],
        "details": syms
    }

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

# Imprimir resumen
print(f"Total: {data['count']} instrumentos en {len(categories)} categorías\n")
print(f"{'Categoría':<40} {'Cantidad':>8}")
print("=" * 50)
for cat in sorted(categories.keys()):
    print(f"  {cat:<38} {len(categories[cat]):>6}")
print("=" * 50)
print(f"  {'TOTAL':<38} {data['count']:>6}")
print(f"\nReporte guardado en: {REPORT_FILE}")
