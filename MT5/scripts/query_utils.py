"""
Utilidades compartidas para los scripts de consulta MT5.
Detecta automáticamente el broker conectado y maneja las rutas de salida.
"""
import requests
from pathlib import Path
from datetime import datetime

GATEWAY_URL = "http://10.211.55.4:8000"
BASE_DIR = Path(__file__).parent.parent / "data" / "queries"


def get_broker_info() -> dict:
    """Consulta la info de la cuenta para identificar el broker."""
    try:
        r = requests.get(f"{GATEWAY_URL}/account_info", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as err:
        print(f"[ERROR] No se pudo obtener info del broker: {type(err).__name__}")
        return {}


def get_output_dir() -> Path:
    """Retorna el directorio de salida: data/queries/{broker}/{fecha}/"""
    info = get_broker_info()
    server = info.get("server", "unknown")
    # Limpiar nombre del servidor para usarlo como carpeta
    broker_name = server.replace(" ", "_").replace("/", "_").lower()
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = BASE_DIR / broker_name / today
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def print_broker_header():
    """Imprime un header con la info del broker conectado."""
    info = get_broker_info()
    if not info:
        print("[ADVERTENCIA]  No se pudo identificar el broker\n")
        return info

    print(f"Broker: {info.get('server', '?')}")
    print(f"Cuenta: {info.get('login', '?')}")
    print(f"Balance: ${info.get('balance', 0):,.2f} {info.get('currency', '')}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    return info
