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
import json
import logging
from pathlib import Path
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

def get_mcp_config():
    """Recupera la configuracion de conexion al servidor MCP de MT5 desde .mcp.json."""
    config = {
        "url": "http://127.0.0.1:22346/mcp",
        "headers": {
            "Authorization": "Bearer IIin+jBM/DNuDPG9tBdStKpZ4Vt4YNFjJkHK+0MmwX",
            "Content-Type": "application/json"
        }
    }
    # Intentar buscar .mcp.json en la raiz o en la carpeta actual
    possible_paths = [
        Path.cwd() / ".mcp.json",
        Path.cwd() / "MT5" / ".mcp.json",
        Path(__file__).parent.parent / ".mcp.json",
        Path(__file__).parent.parent.parent / ".mcp.json"
    ]
    for p in possible_paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    terminal = data.get("mcpServers", {}).get("terminal", {})
                    if terminal.get("url"):
                        config["url"] = terminal["url"]
                    if terminal.get("headers"):
                        config["headers"].update(terminal["headers"])
                        config["headers"]["Content-Type"] = "application/json"
                break
            except Exception as err:
                logger.error(f"Error al leer .mcp.json: {type(err).__name__} (detalles omitidos por seguridad)")
    return config

def call_mt5_mcp(tool_name: str, arguments: dict = None):
    """Ejecuta una llamada al servidor MCP nativo de MT5 respetando el ciclo de vida oficial."""
    import urllib.request
    cfg = get_mcp_config()
    url = cfg["url"]
    headers = dict(cfg["headers"])

    def _post(payload):
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            s_id = resp.headers.get("Mcp-Session-Id")
            return (json.loads(body) if body else {}), s_id

    try:
        # 1. Initialize
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "MT5AgentBridge", "version": "1.0"}
            }
        }
        res_init, sess_id = _post(init_payload)
        if not sess_id:
            return {"error": "No se obtuvo identificador de sesion Mcp-Session-Id"}
        headers["Mcp-Session-Id"] = sess_id

        # 2. notifications/initialized
        try:
            _post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        except Exception:
            pass

        # 3. Pre-flight obligatorio: get_workspace_info
        _post({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "get_workspace_info", "arguments": {}}
        })

        # 4. Invocar herramienta solicitada
        call_payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments or {}}
        }
        res_tool, _ = _post(call_payload)
        if "error" in res_tool:
            return res_tool

        content = res_tool.get("result", {}).get("content", [])
        if content and content[0].get("type") == "text":
            raw_text = content[0].get("text", "")
            try:
                return json.loads(raw_text)
            except Exception:
                return {"raw_output": raw_text}
        return res_tool.get("result", {})

    except Exception as err:
        logger.error(f"Error al invocar herramienta MCP {tool_name}: {type(err).__name__} (detalles omitidos por seguridad)")
        return {"error": f"Error de operacion: {type(err).__name__}"}

def query_mcp_symbols(filter_text: str = None, only_tradeable: bool = True, include_hidden: bool = True):
    """Consulta y filtra simbolos del Market Watch o catalogo completo a traves de MT5 MCP."""
    args = {"limit": 2000, "include_hidden": include_hidden} if include_hidden else {}
    data = call_mt5_mcp("get_marketwatch_symbols", args)
    if "error" in data:
        return data

    symbols = data.get("symbols", [])
    output = []
    for s in symbols:
        sym = s.get("symbol", "")
        desc = s.get("description", "")
        sector = s.get("sector", "")
        trade_mode = s.get("trade_mode_name", "")

        if only_tradeable and trade_mode != "full":
            continue

        if filter_text:
            ft = filter_text.upper()
            if ft not in sym.upper() and ft not in desc.upper() and ft not in sector.upper():
                continue

        bid = s.get("bid", 0.0)
        ask = s.get("ask", 0.0)
        prev_c = s.get("price_close", 0.0)
        chg = round(((bid - prev_c) / prev_c) * 100.0, 2) if prev_c > 0 and bid > 0 else 0.0

        output.append({
            "symbol": sym,
            "description": desc,
            "sector": sector,
            "bid": bid,
            "ask": ask,
            "prev_close": prev_c,
            "change_pct": chg,
            "trade_mode": trade_mode,
            "digits": s.get("digits", 2),
            "min_volume": s.get("volume_min", 0.1),
            "max_volume": s.get("volume_max", 1000),
            "contract_size": s.get("contract_size", 1.0)
        })

    return {"total_found": len(output), "symbols": output}

CACHE_FILE_PATH = "/tmp/mt5_marketwatch_cache.json"

def get_cached_marketwatch_symbols(ttl_seconds: int = 20, force_fresh: bool = False):
    """Obtiene la lista de simbolos de MarketWatch con cache efimera en RAM (/tmp) para tiempo sub-segundo."""
    import time
    now = time.time()
    if not force_fresh and os.path.exists(CACHE_FILE_PATH):
        try:
            mtime = os.path.getmtime(CACHE_FILE_PATH)
            age = now - mtime
            if age < ttl_seconds:
                with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
                    symbols = json.load(f)
                return symbols, round(age, 1), True
        except Exception as err:
            logger.error(f"Error al leer cache de MT5: {type(err).__name__} (detalles omitidos por seguridad)")

    # Consulta fresca via MCP (MarketWatch activo con precios en vivo)
    data = call_mt5_mcp("get_marketwatch_symbols", {})
    symbols = data.get("symbols", []) if isinstance(data, dict) else []

    if symbols:
        try:
            tmp_file = CACHE_FILE_PATH + ".tmp"
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(symbols, f)
            os.replace(tmp_file, CACHE_FILE_PATH)
        except Exception as err:
            logger.error(f"Error al guardar cache de MT5: {type(err).__name__} (detalles omitidos por seguridad)")

    return symbols, 0.0, False

def fast_scan_market(market: str = "US", top_n: int = 3, sort_mode: str = "BOTH", ttl: int = 20, force_fresh: bool = False, output_format: str = "table"):
    """Escanea y clasifica activos de Pepperstone a velocidad sub-segundo (< 50ms con cache)."""
    import time
    t0 = time.time()
    symbols, cache_age, is_cached = get_cached_marketwatch_symbols(ttl_seconds=ttl, force_fresh=force_fresh)

    mkt = market.upper().strip()
    filtered = []

    for s in symbols:
        sym = s.get("symbol", "")
        desc = s.get("description", "")
        sector = s.get("sector", "Undefined")
        bid = s.get("bid", 0.0)
        p_close = s.get("price_close", 0.0)

        if bid <= 0 or p_close <= 0:
            continue

        chg = round(((bid - p_close) / p_close) * 100.0, 2)
        spread_pts = round((s.get("ask", 0.0) - bid), s.get("digits", 2))

        is_etf = any(k in desc.upper() for k in ["ETF", "TRUST", "ISHARES", "SPDR"])
        is_us_stock = sym.endswith(".US") and not is_etf
        is_index = sym in ["NAS100", "US500", "US30", "US2000", "GER40", "UK100", "AUS200", "JP225", "HK50", "ESTX50"]
        is_forex = sector.lower() == "currency" or (len(sym) == 6 and sym.isalpha() and not sym.endswith(".US"))
        is_crypto = any(sym.startswith(c) for c in ["BTC", "ETH", "SOL", "XRP", "LTC", "ADA", "DOGE", "DOT", "LINK"]) and ("USD" in sym or "USDT" in sym)
        is_commodity = any(m in sym for m in ["XAU", "XAG", "XTI", "XBR", "COPPER"])

        match = False
        if mkt in ["US", "US_STOCKS", "STOCKS"]:
            match = is_us_stock
        elif mkt in ["ETFS", "US_ETFS"]:
            match = is_etf and sym.endswith(".US")
        elif mkt in ["INDICES", "INDEX"]:
            match = is_index
        elif mkt in ["FOREX", "FX"]:
            match = is_forex
        elif mkt in ["CRYPTO", "CRIPTOS"]:
            match = is_crypto
        elif mkt in ["COMMODITIES", "METALES"]:
            match = is_commodity
        elif mkt == "ALL":
            match = True

        if match:
            filtered.append({
                "symbol": sym,
                "description": desc,
                "sector": sector,
                "bid": bid,
                "ask": s.get("ask", 0.0),
                "price_close": p_close,
                "change_pct": chg,
                "spread": spread_pts
            })

    # Ordenamiento
    filtered.sort(key=lambda x: x["change_pct"], reverse=True)
    gainers = filtered[:top_n]
    losers = filtered[-top_n:][::-1] if len(filtered) >= top_n else filtered[::-1]

    elapsed_ms = round((time.time() - t0) * 1000, 1)

    result_data = {
        "market": mkt,
        "total_active_assets": len(filtered),
        "is_cached": is_cached,
        "cache_age_sec": cache_age,
        "query_time_ms": elapsed_ms,
        "top_gainers": gainers,
        "top_losers": losers
    }

    if output_format == "json":
        return result_data

    # Formato tabla visual para consola
    lines = []
    cache_badge = f"[CACHE: {cache_age}s]" if is_cached else "[FRESCO: MT5 LIVE]"
    lines.append(f"\n=== PEPPERSTONE FAST-SCANNER · MERCADO: {mkt} ({len(filtered)} ACTIVOS) · {elapsed_ms} ms {cache_badge} ===")

    if sort_mode.upper() in ["GAINERS", "BOTH"]:
        lines.append("\n🟢 TOP GANADORES:")
        for idx, g in enumerate(gainers, 1):
            lines.append(f"  {idx}. {g['symbol']:<10} | {g['description'][:30]:<30} | {g['change_pct']:>+6.2f}% | Bid: ${g['bid']:<9} | Sector: {g['sector']}")

    if sort_mode.upper() in ["LOSERS", "BOTH"]:
        lines.append("\n🔴 TOP PERDEDORES:")
        for idx, l in enumerate(losers, 1):
            lines.append(f"  {idx}. {l['symbol']:<10} | {l['description'][:30]:<30} | {l['change_pct']:>+6.2f}% | Bid: ${l['bid']:<9} | Sector: {l['sector']}")

    lines.append(f"\nLatencia de escaneo: {elapsed_ms} ms | Servidor MT5: Pepperstone-Demo\n")
    return "\n".join(lines)

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

    import_parser = subparsers.add_parser("import-data", help="Convierte y despliega un dataset externo para MT5")
    import_parser.add_argument("file", help="Ruta al archivo CSV de entrada")
    import_parser.add_argument("--symbol", default=None, help="Nombre del Custom Symbol en MT5")
    import_parser.add_argument("--from-date", default=None, help="Fecha inicio filtro (ej. 2020.01.01)")
    import_parser.add_argument("--to-date", default=None, help="Fecha fin filtro (ej. 2026.09.01)")

    sym_parser = subparsers.add_parser("mcp-symbols", help="Consulta simbolos del Market Watch via servidor MCP de MT5")
    sym_parser.add_argument("--filter", default=None, help="Filtro de texto (ej. .US, US100, Tech)")
    sym_parser.add_argument("--all-modes", action="store_true", help="Incluir activos no tradeables o solo cierre")

    hist_parser = subparsers.add_parser("mcp-history", help="Consulta velas historicas OHLC via servidor MCP de MT5")
    hist_parser.add_argument("symbol", help="Simbolo a consultar (ej. AAPL.US, US100)")
    hist_parser.add_argument("--period", default="D1", help="Temporalidad (M1, M5, M15, M30, H1, D1)")
    hist_parser.add_argument("--from-date", default="2026-08-25T00:00:00Z", help="Fecha inicio ISO")
    hist_parser.add_argument("--to-date", default="2026-09-03T12:00:00Z", help="Fecha fin ISO")

    scan_parser = subparsers.add_parser("scan", help="Fast-Scanner sub-segundo de activos y líderes de mercado")
    scan_parser.add_argument("--market", default="US", choices=["US", "ETFS", "INDICES", "FOREX", "CRYPTO", "COMMODITIES", "ALL"], help="Mercado a escanear")
    scan_parser.add_argument("--top", type=int, default=3, help="Cantidad de lideres a mostrar")
    scan_parser.add_argument("--sort", default="BOTH", choices=["BOTH", "GAINERS", "LOSERS"], help="Sentido de clasificacion")
    scan_parser.add_argument("--ttl", type=int, default=20, help="Tiempo de vida de cache en segundos (default: 20)")
    scan_parser.add_argument("--fresh", action="store_true", help="Forzar consulta fresca en vivo a MT5")
    scan_parser.add_argument("--format", default="table", choices=["table", "json"], help="Formato de salida")

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
    elif args.command == "import-data":
        import json
        from universal_data_converter import convert_dataset_to_mt5
        res = convert_dataset_to_mt5(
            input_path=args.file,
            from_date=args.from_date,
            to_date=args.to_date,
            deploy_to_mql5=True
        )
        print(json.dumps(res, indent=2))
    elif args.command == "mcp-symbols":
        import json
        res = query_mcp_symbols(filter_text=args.filter, only_tradeable=not args.all_modes)
        print(json.dumps(res, indent=2))
    elif args.command == "mcp-history":
        import json
        res = call_mt5_mcp("get_chart_history", {
            "symbol": args.symbol,
            "period": args.period,
            "datetime_from": args.from_date,
            "datetime_to": args.to_date
        })
        print(json.dumps(res, indent=2))
    elif args.command == "scan":
        import json
        res = fast_scan_market(
            market=args.market,
            top_n=args.top,
            sort_mode=args.sort,
            ttl=args.ttl,
            force_fresh=args.fresh,
            output_format=args.format
        )
        if args.format == "json":
            print(json.dumps(res, indent=2))
        else:
            print(res)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

