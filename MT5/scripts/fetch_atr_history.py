"""
Obtiene el histórico de ATR(14) D1 de los últimos 30 días para todos los instrumentos.
Guarda en data/queries/{broker}/{fecha}/atr_history.json

Uso: python fetch_atr_history.py
"""
import requests
import json
import sys
from pathlib import Path
from query_utils import GATEWAY_URL, print_broker_header, get_output_dir

# Presets de instrumentos
PRESETS = {
    "latam": "USDCLP,USDMXN,USDBRL,USDCOP,USDARS,XAUUSD,EURUSD,USDJPY,GBPUSD,USDCAD",
}


def main():
    info = print_broker_header()
    if not info:
        print("[ERROR] No se pudo conectar al Gateway.")
        return

    output_dir = get_output_dir()
    print(f"Output: {output_dir}\n")

    # Determinar símbolos: preset, lista personalizada, o todos
    params = {}
    label = "todos los instrumentos"

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in PRESETS:
            params["symbols"] = PRESETS[arg]
            label = f"preset '{arg}' ({len(PRESETS[arg].split(','))} símbolos)"
        else:
            params["symbols"] = sys.argv[1].upper()
            label = f"{len(sys.argv[1].split(','))} símbolos específicos"

    days = 30
    if len(sys.argv) > 2:
        try:
            days = int(sys.argv[2])
            params["days"] = days
        except ValueError:
            pass

    print(f"ATR History ({days} días) — {label}")
    if "symbols" in params:
        print(f"   Símbolos: {params['symbols']}")
    else:
        print("   Esto tomará bastante tiempo para 1700+ símbolos")
    print()

    try:
        r = requests.get(f"{GATEWAY_URL}/symbols/atr_history", params=params, timeout=900)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar al Gateway.")
        return
    except requests.exceptions.Timeout:
        print("[ERROR] Timeout — el scan tarda demasiado.")
        return
    except Exception as err:
        print(f"[ERROR] Error: {type(err).__name__}")
        return

    # Guardar JSON completo
    with open(output_dir / "atr_history.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    results = data.get("results", [])
    count = data.get("count", 0)
    errors = data.get("errors", 0)

    print(f"[OK] {count} instrumentos con historia ATR ({errors} errores)\n")

    # Resumen de tendencias
    expanding = [r for r in results if r["trend"] == "expanding"]
    contracting = [r for r in results if r["trend"] == "contracting"]
    stable = [r for r in results if r["trend"] == "stable"]

    print(f"Tendencias de volatilidad:")
    print(f"   [INACTIVO] Expandiendo:   {len(expanding):>5} instrumentos (volatilidad subiendo)")
    print(f"   [ACTIVO] Contrayendo:   {len(contracting):>5} instrumentos (volatilidad bajando)")
    print(f"   [INFO] Estable:       {len(stable):>5} instrumentos")

    # Top 10 mayor cambio
    print(f"\n{'=' * 70}")
    print(f"[INACTIVO] Top 10 — Mayor AUMENTO de volatilidad (últimos 30 días)")
    print(f"{'=' * 70}")
    print(f"{'Symbol':<16} {'ATR% Antes':>10} {'ATR% Ahora':>10} {'Cambio':>10} {'Categoría'}")
    print("-" * 70)
    top_exp = sorted([r for r in results if r["atr_change"] > 0],
                     key=lambda x: x["atr_change"], reverse=True)[:10]
    for r in top_exp:
        print(f"{r['symbol']:<16} {r['atr_30d_ago']:>9.2f}% {r['atr_current']:>9.2f}% "
              f"{r['atr_change']:>+9.2f}% {r['category']}")

    print(f"\n{'=' * 70}")
    print(f"[ACTIVO] Top 10 — Mayor REDUCCIÓN de volatilidad (últimos 30 días)")
    print(f"{'=' * 70}")
    print(f"{'Symbol':<16} {'ATR% Antes':>10} {'ATR% Ahora':>10} {'Cambio':>10} {'Categoría'}")
    print("-" * 70)
    top_con = sorted([r for r in results if r["atr_change"] < 0],
                     key=lambda x: x["atr_change"])[:10]
    for r in top_con:
        print(f"{r['symbol']:<16} {r['atr_30d_ago']:>9.2f}% {r['atr_current']:>9.2f}% "
              f"{r['atr_change']:>+9.2f}% {r['category']}")

    print(f"\nDatos guardados en: {output_dir / 'atr_history.json'}")


if __name__ == "__main__":
    main()
