"""
Setup de cuentas MT5 — Ejecutar UNA VEZ en Windows / Entorno de Trading.
Guarda las credenciales en ~/.mt5_accounts.json (local, no compartido).

Uso: python setup_accounts.py
"""
import os
import json
from pathlib import Path

ACCOUNTS_FILE = Path.home() / ".mt5_accounts.json"

# Cargar desde variables de entorno o usar valores de plantilla
accounts = {
    "pepperstone": {
        "login": int(os.environ.get("PEPPERSTONE_LOGIN", 61552119)),
        "password": os.environ.get("PEPPERSTONE_PASSWORD", "YOUR_PEPPERSTONE_PASSWORD"),
        "server": os.environ.get("PEPPERSTONE_SERVER", "Pepperstone-Demo")
    },
    "capitaria": {
        "login": int(os.environ.get("CAPITARIA_LOGIN", 2883015881)),
        "password": os.environ.get("CAPITARIA_PASSWORD", "YOUR_CAPITARIA_PASSWORD"),
        "server": os.environ.get("CAPITARIA_SERVER", "Capitaria-All")
    },
    "grupointeligencia": {
        "login": int(os.environ.get("GRUPO_INTELIGENCIA_LOGIN", 50870)),
        "password": os.environ.get("GRUPO_INTELIGENCIA_PASSWORD", "YOUR_GI_PASSWORD"),
        "server": os.environ.get("GRUPO_INTELIGENCIA_SERVER", "GrupoInteligenciaSpA-Server")
    }
}

with open(ACCOUNTS_FILE, "w") as f:
    json.dump(accounts, f, indent=2)

print(f"[OK] Cuentas guardadas en: {ACCOUNTS_FILE}")
print(f"   Brokers configurados: {list(accounts.keys())}")
print(f"\n[ADVERTENCIA]  Este archivo local contiene contraseñas. NO lo compartas ni lo subas a repositorios.")

