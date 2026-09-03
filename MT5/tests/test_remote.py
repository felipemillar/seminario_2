"""
Test de conexión remota macOS → MT5 Gateway (Windows/Parallels)
Ejecutar desde macOS para verificar que el puente funciona.

Uso: python test_remote.py
"""
import requests
import json
from datetime import datetime

# ─── Configuración ─────────────────────────────────────────
GATEWAY_URL = "http://10.211.55.4:8000"
API_TOKEN = "mt5-gateway-2026"
HEADERS = {"X-Api-Token": API_TOKEN}


def test_health():
    """Test 1: Health check del Gateway."""
    print("=" * 60)
    print(" Test 1: Health Check")
    print("=" * 60)
    try:
        r = requests.get(f"{GATEWAY_URL}/health", headers=HEADERS, timeout=5)
        data = r.json()
        print(f"  Gateway:       {data.get('gateway', '?')}")
        print(f"  MT5 Conectado: {data.get('mt5_connected', '?')}")
        print(f"  Timestamp:     {data.get('timestamp', '?')}")
        print(f"  [OK] Health check OK\n")
        return True
    except requests.exceptions.ConnectionError:
        print(f"  [ERROR] No se puede conectar a {GATEWAY_URL}")
        print(f"  → Verifica que el Gateway esté corriendo en Windows")
        print(f"  → Verifica el firewall de Windows\n")
        return False
    except Exception as err:
        print(f"  [ERROR] Error: {type(err).__name__}\n")
        return False


def test_account_info():
    """Test 2: Información de la cuenta."""
    print("=" * 60)
    print("Test 2: Account Info")
    print("=" * 60)
    try:
        r = requests.get(f"{GATEWAY_URL}/account_info", headers=HEADERS, timeout=5)
        data = r.json()
        print(f"  Login:    {data.get('login', '?')}")
        print(f"  Servidor: {data.get('server', '?')}")
        print(f"  Balance:  ${data.get('balance', '?'):,.2f}")
        print(f"  Equity:   ${data.get('equity', '?'):,.2f}")
        print(f"  Moneda:   {data.get('currency', '?')}")
        print(f"  [OK] Account info OK\n")
        return True
    except Exception as err:
        print(f"  [ERROR] Error: {type(err).__name__}\n")
        return False


def test_symbol_tick():
    """Test 3: Tick en tiempo real de EURUSD."""
    print("=" * 60)
    print("Test 3: Tick EURUSD en Tiempo Real")
    print("=" * 60)
    try:
        r = requests.get(f"{GATEWAY_URL}/symbol_info_tick/EURUSD", headers=HEADERS, timeout=5)
        data = r.json()
        print(f"  Bid:    {data.get('bid', '?')}")
        print(f"  Ask:    {data.get('ask', '?')}")
        print(f"  Spread: {round((data.get('ask', 0) - data.get('bid', 0)) * 10000, 1)} pips")
        print(f"  [OK] Tick recibido OK\n")
        return True
    except Exception as err:
        print(f"  [ERROR] Error: {type(err).__name__}\n")
        return False


def test_copy_rates():
    """Test 4: Datos OHLCV históricos."""
    print("=" * 60)
    print("Test 4: OHLCV Histórico (EURUSD M5, 10 barras)")
    print("=" * 60)
    try:
        payload = {"symbol": "EURUSD", "timeframe": 5, "count": 10}
        r = requests.post(f"{GATEWAY_URL}/copy_rates", json=payload, headers=HEADERS, timeout=10)
        data = r.json()
        rates = data.get("rates", [])
        print(f"  Barras recibidas: {len(rates)}")
        if rates:
            last = rates[-1]
            print(f"  Última barra:")
            print(f"    Tiempo: {last.get('time', '?')}")
            print(f"    Open:   {last.get('open', '?')}")
            print(f"    High:   {last.get('high', '?')}")
            print(f"    Low:    {last.get('low', '?')}")
            print(f"    Close:  {last.get('close', '?')}")
        print(f"  [OK] Datos OHLCV OK\n")
        return True
    except Exception as err:
        print(f"  [ERROR] Error: {type(err).__name__}\n")
        return False


def test_positions():
    """Test 5: Posiciones abiertas."""
    print("=" * 60)
    print("Test 5: Posiciones Abiertas")
    print("=" * 60)
    try:
        r = requests.get(f"{GATEWAY_URL}/positions", headers=HEADERS, timeout=5)
        data = r.json()
        positions = data.get("positions", [])
        print(f"  Posiciones abiertas: {len(positions)}")
        for pos in positions:
            print(f"    #{pos.get('ticket')} | {pos.get('symbol')} | "
                  f"{'BUY' if pos.get('type') == 0 else 'SELL'} | "
                  f"Vol: {pos.get('volume')} | P/L: ${pos.get('profit', 0):.2f}")
        print(f"  [OK] Posiciones OK\n")
        return True
    except Exception as err:
        print(f"  [ERROR] Error: {type(err).__name__}\n")
        return False


# ─── Ejecución Principal ──────────────────────────────────
if __name__ == "__main__":
    print("\n" + "[SIGNAL]" * 30)
    print("  MT5 GATEWAY — Test de Conexión Remota (macOS → Windows)")
    print(f"  Gateway: {GATEWAY_URL}")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print("[SIGNAL]" * 30 + "\n")

    results = []
    results.append(("Health Check", test_health()))

    if results[0][1]:  # Solo continuar si health check pasó
        results.append(("Account Info", test_account_info()))
        results.append(("Symbol Tick", test_symbol_tick()))
        results.append(("OHLCV Data", test_copy_rates()))
        results.append(("Positions", test_positions()))

    # Resumen
    print("=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)
    for name, passed in results:
        status = "[OK] PASS" if passed else "[ERROR] FAIL"
        print(f"  {status}  {name}")

    passed = sum(1 for _, p in results if p)
    total = len(results)
    print(f"\n  Resultado: {passed}/{total} tests exitosos")
    print("=" * 60)
