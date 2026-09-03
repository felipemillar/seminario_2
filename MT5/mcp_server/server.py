#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
MT5 MCP Server — Servidor Model Context Protocol para MetaTrader 5 en macOS
Autor: QRT Solutions
Protocolo: MCP (Model Context Protocol) sobre stdio (JSON-RPC 2.0)
Compatible con: Claude Desktop, Claude Code, Cursor, Antigravity IDE, Windsurf
=============================================================================
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List

# Asegurar importacion de mt5_agent_bridge
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import mt5_agent_bridge

# Logging a stderr para no contaminar la salida stdio JSON-RPC
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MT5_MCP")

TOOLS_REGISTRY = [
    {
        "name": "mt5_status",
        "description": "Obtiene el estado de conexion de MetaTrader 5, cuenta activa, broker, servidor y cantidad de simbolos sincronizados.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "mt5_compile",
        "description": "Compila de forma desatendida un codigo fuente MQL5 (.mq5) usando MetaEditor 64 bajo Wine, reportando errores, advertencias y generando el ejecutable .ex5.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Ruta absoluta o relativa al archivo .mq5 que se desea compilar."
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "mt5_deploy_expert",
        "description": "Compila y despliega un Asesor Experto (.mq5) directamente en las carpetas MQL5/Experts y MQL5/Experts/Advisors de MetaTrader 5.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Ruta al archivo .mq5 del Asesor Experto."
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "mt5_clean_agents",
        "description": "Termina y limpia procesos huerfanos de simulacion (metatester64.exe) para liberar el puerto 3000 y prevenir errores de autorizacion en el Strategy Tester.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "mt5_last_backtest_metrics",
        "description": "Extrae y analiza las metricas cuantitativas de la ultima simulacion del Strategy Tester (Balance final, P&L neto, Profit Factor, Win Rate, Payoff Ratio y desglose de salidas).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
    try:
        if name == "mt5_status":
            return mt5_agent_bridge.get_terminal_status()
        elif name == "mt5_compile":
            file_path = arguments.get("file_path", "")
            return mt5_agent_bridge.compile_mql5(file_path)
        elif name == "mt5_deploy_expert":
            file_path = arguments.get("file_path", "")
            return mt5_agent_bridge.deploy_expert(file_path)
        elif name == "mt5_clean_agents":
            return mt5_agent_bridge.clean_tester_agents()
        elif name == "mt5_last_backtest_metrics":
            return mt5_agent_bridge.parse_last_backtest()
        else:
            return {"error": f"Herramienta desconocida: {name}"}
    except Exception as err:
        logger.error(f"Error al ejecutar herramienta {name}: {type(err).__name__} (detalles omitidos por seguridad)")
        return {"error": f"Error de operacion: {type(err).__name__}"}

def process_message(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    msg_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "mt5-agent-mcp",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS_REGISTRY
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        result_data = handle_tool_call(tool_name, tool_args)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result_data, indent=2, ensure_ascii=False)
                    }
                ]
            }
        }
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Metodo no encontrado: {method}"
            }
        }

def run_server():
    logger.info("Servidor MT5 MCP iniciado en modo stdio.")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = process_message(req)
            if res is not None:
                sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception as err:
            logger.error(f"Error procesando mensaje MCP: {type(err).__name__} (detalles omitidos por seguridad)")
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Error de parseo: {type(err).__name__}"}
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("=== Test de Servidor MT5 MCP ===")
        print(f"Herramientas registradas: {len(TOOLS_REGISTRY)}")
        for t in TOOLS_REGISTRY:
            print(f"- {t['name']}: {t['description'][:60]}...")
        test_init = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        print("\nPrueba de initialize:")
        print(json.dumps(process_message(test_init), indent=2))
        test_tools = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        print("\nPrueba de tools/list:")
        print(json.dumps(process_message(test_tools), indent=2))
    else:
        run_server()
