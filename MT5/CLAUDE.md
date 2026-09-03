# Claude Code Guide — MT5 Knowledge Base & Gateway

## Project Overview
Repository containing 1.83MB of exhaustive MetaTrader 5 (MT5) and MQL5 algorithmic trading documentation across 20 technical guides in `knowledge/`, alongside a local FastAPI gateway in `src/gateway/` and quantitative trading scripts in `scripts/`.

## Key Resources for Claude
- Full manifest & catalog: `llms.txt` and `knowledge/INDEX.md`
- Consolidated reference: `llms-full.txt`
- Canonical agent guidelines: `AGENTS.md`
- Universal agent connection guide: `AGENT_CONNECTION_GUIDE.md`
- Model Context Protocol (MCP) Server: `mcp_server/server.py`
- CLI Bridge tool: `python3 scripts/mt5_agent_bridge.py [status|compile|deploy|last-test|clean-agents]`

## Code Standards & Agent Commands
- Python error masking: In all `except` handlers, use `type(err).__name__` instead of printing raw exceptions to prevent credential/stack leakage.
- Status check: `python3 scripts/mt5_agent_bridge.py status`
- Unattended MQL5 compilation: `python3 scripts/mt5_agent_bridge.py compile <path.mq5>`
- Deploy EA to MT5: `python3 scripts/mt5_agent_bridge.py deploy <path.mq5>`
- Extract last backtest: `python3 scripts/mt5_agent_bridge.py last-test`
- Free tester agents (port 3000): `python3 scripts/mt5_agent_bridge.py clean-agents`
- Gateway execution (legacy): `uvicorn src.gateway.server:app --host 0.0.0.0 --port 8000`
- Secrets management: Credentials must be loaded from `.env` or `~/.mt5_accounts.json`.
