#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
MT5 Agent Bridge - Puente CLI Universal Multiplataforma (macOS / Windows)
Autor: QRT Solutions
Uso: python mt5_agent_bridge.py [comando] [argumentos]
Soporta: Windows 10/11 x64 nativo y macOS (Wine / Apple Silicon)
=============================================================================
"""

import os
import sys
import re
import glob
import shutil
import argparse
import subprocess
import logging
from typing import Dict, Any, List, Optional

# Configuracion de Logging Seguro (Error Masking)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MT5AgentBridge")

IS_WINDOWS = (sys.platform == "win32")
IS_MACOS = (sys.platform == "darwin")

# Resolucion dinamica de rutas segun sistema operativo
if IS_WINDOWS:
    # Rutas estandar de Windows
    DEFAULT_WIN_PATH = os.environ.get("MT5_PATH", r"C:\Program Files\MetaTrader 5")
    MT5_ROOT = DEFAULT_WIN_PATH
    METAEDITOR_BIN = os.path.join(MT5_ROOT, "metaeditor64.exe")
    TERMINAL_BIN = os.path.join(MT5_ROOT, "terminal64.exe")
    WINE_BIN = None
    WINE_PREFIX = None
    MQL5_DIR = os.path.join(MT5_ROOT, "MQL5")
    EXPERTS_DIR = os.path.join(MQL5_DIR, "Experts")
    INDICATORS_DIR = os.path.join(MQL5_DIR, "Indicators")
    TESTER_DIR = os.path.join(MT5_ROOT, "Tester")
    LOGS_DIR = os.path.join(MT5_ROOT, "logs")
else:
    # Rutas estandar de macOS bajo Wine
    WINE_BIN = os.environ.get("WINE_BIN", "/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine")
    WINE_PREFIX = os.environ.get("WINEPREFIX", os.path.expanduser("~/Library/Application Support/net.metaquotes.wine.metatrader5"))
    MT5_ROOT = os.path.join(WINE_PREFIX, "drive_c/Program Files/MetaTrader 5")
    METAEDITOR_BIN = "metaeditor64.exe"
    TERMINAL_BIN = "terminal64.exe"
    MQL5_DIR = os.path.join(MT5_ROOT, "MQL5")
    EXPERTS_DIR = os.path.join(MQL5_DIR, "Experts")
    INDICATORS_DIR = os.path.join(MQL5_DIR, "Indicators")
    TESTER_DIR = os.path.join(MT5_ROOT, "Tester")
    LOGS_DIR = os.path.join(MT5_ROOT, "logs")

def check_environment() -> Dict[str, Any]:
    """Verifica el entorno del sistema y la presencia de MetaTrader 5."""
    info = {
        "platform": sys.platform,
        "is_windows": IS_WINDOWS,
        "is_macos": IS_MACOS,
        "mt5_root_exists": os.path.exists(MT5_ROOT) if MT5_ROOT else False,
        "mql5_dir_exists": os.path.exists(MQL5_DIR) if MQL5_DIR else False,
    }
    if IS_MACOS:
        info["wine_bin_exists"] = os.path.exists(WINE_BIN) if WINE_BIN else False
        info["wine_prefix_exists"] = os.path.exists(WINE_PREFIX) if WINE_PREFIX else False
    elif IS_WINDOWS:
        info["metaeditor_exists"] = os.path.exists(METAEDITOR_BIN) if METAEDITOR_BIN else False
    return info

def get_terminal_status() -> Dict[str, Any]:
    """Obtiene el estado de ejecucion de terminal64.exe, la cuenta activa y broker."""
    status = {
        "platform": sys.platform,
        "terminal_running": False,
        "active_account": None,
        "broker": None,
        "symbols_synchronized": 0,
        "server": None
    }
    try:
        if IS_WINDOWS:
            # En Windows usamos tasklist
            tl_out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
            status["terminal_running"] = "terminal64.exe" in tl_out.lower()
        else:
            ps_out = subprocess.run(["ps", "aux"], capture_output=True, text=True).stdout
            status["terminal_running"] = "terminal64.exe" in ps_out

        if os.path.exists(LOGS_DIR):
            log_files = glob.glob(os.path.join(LOGS_DIR, "*.log"))
            log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            if log_files:
                latest_log = log_files[0]
                with open(latest_log, "rb") as f:
                    content = f.read().decode("utf-16", errors="replace")
                
                for line in reversed(content.splitlines()):
                    if status["active_account"] is None and "terminal synchronized with" in line:
                        m = re.search(r"'(\d+)': terminal synchronized with (.+?):.* (\d+) symbols", line)
                        if m:
                            status["active_account"] = m.group(1)
                            status["broker"] = m.group(2)
                            status["symbols_synchronized"] = int(m.group(3))
                    elif status["server"] is None and "authorized on" in line:
                        m = re.search(r"'(\d+)': authorized on (.+?)(?: through|$)", line)
                        if m:
                            status["server"] = m.group(2).strip()
                    if status["active_account"] and status["server"]:
                        break
    except Exception as err:
        logger.error(f"Error al obtener estado del terminal: {type(err).__name__} (detalles omitidos por seguridad)")
        status["error"] = f"Error de operacion: {type(err).__name__}"

    return status

def clean_tester_agents() -> Dict[str, Any]:
    """Termina procesos metatester64.exe huerfanos para liberar el puerto 3000."""
    result = {"success": False, "message": ""}
    try:
        if IS_WINDOWS:
            subprocess.run(["taskkill", "/F", "/IM", "metatester64.exe"], capture_output=True, text=True)
            result["success"] = True
            result["message"] = "[INFO] Procesos metatester64 terminados en Windows."
        else:
            subprocess.run(["pkill", "-f", "metatester64"], capture_output=True, text=True)
            # Verificar y liberar puerto 3000 si esta ocupado por procesos externos (ej. servidores node/vite)
            try:
                out = subprocess.run(["lsof", "-ti", ":3000"], capture_output=True, text=True).stdout.strip()
                if out:
                    for pid_str in out.split():
                        pid = int(pid_str)
                        if pid > 0 and pid != os.getpid():
                            os.kill(pid, 9)
                    result["message"] = "[INFO] Agentes terminados y puerto 3000 liberado en macOS."
                else:
                    result["message"] = "[INFO] Agentes de simulacion locales terminados en macOS (puerto 3000 libre)."
            except Exception:
                result["message"] = "[INFO] Agentes de simulacion locales terminados en macOS."
            result["success"] = True
    except Exception as err:
        logger.error(f"Error al limpiar agentes: {type(err).__name__} (detalles omitidos por seguridad)")
        result["message"] = f"Error de operacion: {type(err).__name__}"
    return result

def compile_mql5(file_path: str) -> Dict[str, Any]:
    """
    Compila un archivo .mq5 usando metaeditor64.exe de forma desatendida (Windows nativo o macOS Wine).
    """
    result = {
        "success": False,
        "errors": -1,
        "warnings": -1,
        "log_output": "",
        "ex5_path": None
    }
    try:
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            result["log_output"] = f"[ERROR] Archivo no encontrado: {abs_path}"
            return result

        filename = os.path.basename(abs_path)
        is_indicator = "indicat" in abs_path.lower()
        is_script = "script" in abs_path.lower()
        if is_indicator:
            target_subfolder = "Indicators"
        elif is_script:
            target_subfolder = "Scripts"
        else:
            target_subfolder = "Experts"
        dest_in_mql5 = os.path.join(MQL5_DIR, target_subfolder, filename)

        os.makedirs(os.path.dirname(dest_in_mql5), exist_ok=True)
        shutil.copy2(abs_path, dest_in_mql5)

        log_file_win = "compile_agent.log"
        log_file_host = os.path.join(MT5_ROOT, log_file_win)

        if IS_WINDOWS:
            cmd = [
                METAEDITOR_BIN,
                f"/compile:{dest_in_mql5}",
                f"/log:{log_file_host}"
            ]
            subprocess.run(cmd, capture_output=True, text=True)
        else:
            wine_compile_arg = f"MQL5\\{target_subfolder}\\{filename}"
            cmd = [
                WINE_BIN,
                "cmd", "/c",
                f"cd /d C:\\Program Files\\MetaTrader 5 && metaeditor64.exe /compile:{wine_compile_arg} /log:{log_file_win}"
            ]
            env = os.environ.copy()
            env["WINEPREFIX"] = WINE_PREFIX
            subprocess.run(cmd, env=env, capture_output=True, text=True)

        if os.path.exists(log_file_host):
            with open(log_file_host, "rb") as f:
                log_text = f.read().decode("utf-16", errors="replace").strip()
            result["log_output"] = log_text

            m = re.search(r"Result:\s*(\d+)\s*errors,\s*(\d+)\s*warnings", log_text)
            if m:
                errors = int(m.group(1))
                warnings = int(m.group(2))
                result["errors"] = errors
                result["warnings"] = warnings
                result["success"] = (errors == 0)

            ex5_win_path = os.path.splitext(dest_in_mql5)[0] + ".ex5"
            if os.path.exists(ex5_win_path):
                result["ex5_path"] = ex5_win_path
                dest_local_ex5 = os.path.splitext(abs_path)[0] + ".ex5"
                if dest_local_ex5 != ex5_win_path:
                    shutil.copy2(ex5_win_path, dest_local_ex5)
    except Exception as err:
        logger.error(f"Error al compilar MQL5: {type(err).__name__} (detalles omitidos por seguridad)")
        result["log_output"] = f"Error de operacion: {type(err).__name__}"

    return result

def deploy_expert(file_path: str) -> Dict[str, Any]:
    """Compila y despliega un EA en Experts y Experts/Advisors de MT5."""
    comp = compile_mql5(file_path)
    if not comp["success"]:
        return comp

    try:
        ex5_file = comp["ex5_path"]
        if ex5_file and os.path.exists(ex5_file):
            advisors_dir = os.path.join(EXPERTS_DIR, "Advisors")
            os.makedirs(advisors_dir, exist_ok=True)
            shutil.copy2(ex5_file, os.path.join(advisors_dir, os.path.basename(ex5_file)))
            comp["deployed_to"] = [EXPERTS_DIR, advisors_dir]
    except Exception as err:
        logger.error(f"Error al desplegar EA: {type(err).__name__} (detalles omitidos por seguridad)")
        comp["deploy_error"] = f"Error de operacion: {type(err).__name__}"

    return comp

def parse_last_backtest() -> Dict[str, Any]:
    """Extrae y procesa los datos cuantitativos de la ultima simulacion del Tester."""
    results = {
        "success": False,
        "strategy": None,
        "symbol": None,
        "period": None,
        "deposit": 10000.0,
        "final_balance": None,
        "net_pnl": 0.0,
        "profit_factor": None,
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "win_rate_pct": 0.0,
        "payoff_ratio": 0.0,
        "avg_win": 0.0,
        "avg_loss": 0.0,
        "max_win": 0.0,
        "max_loss": 0.0,
        "exit_reasons": {}
    }
    try:
        agent_logs = glob.glob(os.path.join(TESTER_DIR, "Agent-*/logs/*.log"))
        agent_logs = [l for l in agent_logs if os.path.getsize(l) > 1024]
        agent_logs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        if not agent_logs:
            results["error"] = "No se encontraron logs de simulacion."
            return results

        latest_log = agent_logs[0]
        with open(latest_log, "rb") as f:
            lines = f.read().decode("utf-16", errors="replace").splitlines()

        start_idx = 0
        for i in range(len(lines)-1, -1, -1):
            if "Inicializado con exito" in lines[i] or "Expert initialization function" in lines[i]:
                start_idx = i
                break

        test_lines = lines[start_idx:] if start_idx > 0 else lines[-5000:]

        deal_pat = re.compile(r"deal #(\d+) (buy|sell) ([\d\.]+) ([A-Z0-9\._\-]+) at ([\d\.]+) done")
        exit_pat = re.compile(r"\{\"event\":\"EXIT\",\"reason\":\"([^\"]+)\",\"ticket\":(\d+)")
        init_pat = re.compile(r"\[([^\]]+)\] Inicializado con exito en ([A-Z0-9\._\-]+)")
        bal_pat  = re.compile(r"final balance ([\d\.]+) USD")

        exits_dict = {}
        deals = []
        for l in test_lines:
            im = init_pat.search(l)
            if im:
                results["strategy"] = im.group(1)
                results["symbol"] = im.group(2)
            xm = exit_pat.search(l)
            if xm:
                exits_dict[xm.group(2)] = xm.group(1)
            bm = bal_pat.search(l)
            if bm:
                results["final_balance"] = float(bm.group(1))
            dm = deal_pat.search(l)
            if dm:
                deals.append({
                    "ticket": dm.group(1),
                    "type": dm.group(2),
                    "symbol": dm.group(4),
                    "price": float(dm.group(5))
                })

        trades = []
        current = None
        for d in deals:
            if current is None:
                current = d
            else:
                if d["type"] != current["type"]:
                    diff = (d["price"] - current["price"]) if current["type"] == "buy" else (current["price"] - d["price"])
                    pnl = diff * 1.0
                    reason = exits_dict.get(current["ticket"], "TP_SL_OR_OTHER")
                    trades.append({"pnl": pnl, "reason": reason})
                    current = None

        if trades:
            wins = [t["pnl"] for t in trades if t["pnl"] > 0]
            losses = [t["pnl"] for t in trades if t["pnl"] <= 0]
            gross_profit = sum(wins)
            gross_loss = abs(sum(losses))

            results["total_trades"] = len(trades)
            results["winning_trades"] = len(wins)
            results["losing_trades"] = len(losses)
            results["win_rate_pct"] = round((len(wins) / len(trades)) * 100, 2)
            results["profit_factor"] = round(gross_profit / gross_loss, 2) if gross_loss > 0 else 999.0
            results["net_pnl"] = round(sum(t["pnl"] for t in trades), 2)
            results["avg_win"] = round(gross_profit / len(wins), 2) if wins else 0.0
            results["avg_loss"] = round(gross_loss / len(losses), 2) if losses else 0.0
            results["payoff_ratio"] = round(results["avg_win"] / results["avg_loss"], 2) if results["avg_loss"] > 0 else 0.0
            results["max_win"] = round(max(wins), 2) if wins else 0.0
            results["max_loss"] = round(min(losses), 2) if losses else 0.0

            reasons = {}
            for t in trades:
                reasons[t["reason"]] = reasons.get(t["reason"], 0) + 1
            results["exit_reasons"] = reasons
            results["success"] = True

    except Exception as err:
        logger.error(f"Error al analizar backtest: {type(err).__name__} (detalles omitidos por seguridad)")
        results["error"] = f"Error de operacion: {type(err).__name__}"

    return results

def main():
    parser = argparse.ArgumentParser(description="MT5 Agent Bridge - CLI Universal para Agentes de IA (macOS / Windows)")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    subparsers.add_parser("status", help="Muestra el estado del terminal, cuenta activa y broker")
    subparsers.add_parser("env", help="Muestra el diagnostico del entorno y rutas de MT5")
    subparsers.add_parser("clean-agents", help="Termina instancias de simulacion huerfanas (libera puerto 3000)")
    subparsers.add_parser("last-test", help="Extrae las metricas cuantitativas del ultimo backtest")

    compile_parser = subparsers.add_parser("compile", help="Compila un archivo MQL5 (.mq5)")
    compile_parser.add_argument("file", help="Ruta al archivo .mq5 a compilar")

    deploy_parser = subparsers.add_parser("deploy", help="Compila y despliega un EA en la carpeta Experts de MT5")
    deploy_parser.add_argument("file", help="Ruta al archivo .mq5 a desplegar")

    args = parser.parse_args()

    if args.command == "status":
        import json
        print(json.dumps(get_terminal_status(), indent=2))
    elif args.command == "env":
        import json
        print(json.dumps(check_environment(), indent=2))
    elif args.command == "clean-agents":
        import json
        print(json.dumps(clean_tester_agents(), indent=2))
    elif args.command == "compile":
        import json
        res = compile_mql5(args.file)
        print(json.dumps(res, indent=2))
    elif args.command == "deploy":
        import json
        res = deploy_expert(args.file)
        print(json.dumps(res, indent=2))
    elif args.command == "last-test":
        import json
        print(json.dumps(parse_last_backtest(), indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
