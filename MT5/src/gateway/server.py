"""
MT5 Gateway Server — FastAPI
Corre en Windows (VPS o Parallels) junto a MetaTrader 5.
Expone la API de MT5 como endpoints HTTP REST para clientes remotos (macOS).

Uso: python server.py
"""
import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import MetaTrader5 as mt5
import pandas as pd
import numpy as np

# ─── Logging ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s"
)
logger = logging.getLogger("MT5Gateway")

# ─── FastAPI App ───────────────────────────────────────────
app = FastAPI(
    title="MT5 Gateway Server",
    description="Puente REST para MetaTrader 5 — diseñado para conexión macOS → Windows",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Token de seguridad simple ─────────────────────────────
API_TOKEN = "mt5-gateway-2026"

def verify_token(x_api_token: str = Header(default="")):
    if x_api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")

# ─── Configuración de cuentas (local en Windows) ──────────
ACCOUNTS_FILE = Path.home() / ".mt5_accounts.json"

def load_accounts() -> dict:
    """Carga las cuentas desde el archivo local de Windows."""
    if not ACCOUNTS_FILE.exists():
        return {}
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)


# ─── Modelos Pydantic ──────────────────────────────────────
class InitRequest(BaseModel):
    login: Optional[int] = None
    password: Optional[str] = None
    server: Optional[str] = None
    timeout: int = 60000

class CopyRatesRequest(BaseModel):
    symbol: str
    timeframe: int  # mt5.TIMEFRAME_M5 = 5, etc.
    count: int = 100

class SwitchAccountRequest(BaseModel):
    broker: str  # Alias del broker: "pepperstone", "capitaria", "grupointeligencia"

class OrderRequest(BaseModel):
    symbol: str
    order_type: int  # 0 = BUY, 1 = SELL
    volume: float
    sl_points: Optional[int] = None
    tp_points: Optional[int] = None
    magic: int = 20002
    deviation: int = 10
    comment: str = "Gateway Order"


# ─── Endpoints ─────────────────────────────────────────────

@app.post("/initialize")
def initialize(req: InitRequest):
    """Inicializa la conexión IPC con MT5."""
    try:
        args = {"timeout": req.timeout}
        if req.login:
            args["login"] = req.login
        if req.password:
            args["password"] = req.password
        if req.server:
            args["server"] = req.server

        result = mt5.initialize(**args)
        if not result:
            err_code, err_desc = mt5.last_error()
            logger.error(f"Error al inicializar MT5: {err_code} (detalles omitidos por seguridad)")
            return {"success": False, "error_code": err_code, "error": err_desc}

        logger.info("MT5 inicializado correctamente via Gateway")
        return {"success": True}
    except Exception as err:
        logger.error(f"Error en initialize: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.get("/account_info")
def account_info():
    """Retorna información de la cuenta de trading."""
    try:
        info = mt5.account_info()
        if info is None:
            raise HTTPException(status_code=503, detail="MT5 no conectado")
        return info._asdict()
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Error en account_info: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.get("/terminal_info")
def terminal_info():
    """Retorna información del terminal MT5."""
    try:
        info = mt5.terminal_info()
        if info is None:
            raise HTTPException(status_code=503, detail="MT5 no conectado")
        return info._asdict()
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Error en terminal_info: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.get("/symbol_info/{symbol}")
def symbol_info(symbol: str):
    """Retorna especificaciones del contrato de un activo."""
    try:
        info = mt5.symbol_info(symbol)
        if info is None:
            raise HTTPException(status_code=404, detail=f"Símbolo {symbol} no encontrado")
        return info._asdict()
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Error en symbol_info: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.get("/symbol_info_tick/{symbol}")
def symbol_info_tick(symbol: str):
    """Retorna el último tick de un activo."""
    try:
        if not mt5.symbol_select(symbol, True):
            raise HTTPException(status_code=404, detail=f"No se pudo seleccionar {symbol}")
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise HTTPException(status_code=404, detail=f"Sin tick para {symbol}")
        return tick._asdict()
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Error en symbol_info_tick: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.post("/copy_rates")
def copy_rates(req: CopyRatesRequest):
    """Extrae barras OHLCV históricas y las retorna como lista de diccionarios."""
    try:
        if not mt5.symbol_select(req.symbol, True):
            raise HTTPException(status_code=404, detail=f"No se pudo seleccionar {req.symbol}")

        rates = mt5.copy_rates_from_pos(req.symbol, req.timeframe, 0, req.count)
        if rates is None or len(rates) == 0:
            err_code, err_desc = mt5.last_error()
            logger.error(f"Error al copiar rates: {err_code} (detalles omitidos por seguridad)")
            raise HTTPException(status_code=500, detail=f"Sin datos para {req.symbol}")

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s', utc=True).astype(str)
        return {"symbol": req.symbol, "count": len(df), "rates": df.to_dict(orient="records")}
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Error en copy_rates: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.post("/order_send")
def order_send(req: OrderRequest):
    """Envía una orden de mercado a MT5."""
    try:
        sym_info = mt5.symbol_info(req.symbol)
        tick = mt5.symbol_info_tick(req.symbol)
        if sym_info is None or tick is None:
            raise HTTPException(status_code=404, detail=f"Cotización no disponible para {req.symbol}")

        if req.order_type == mt5.ORDER_TYPE_BUY:
            price = tick.ask
            sl = price - (req.sl_points * sym_info.point) if req.sl_points else 0.0
            tp = price + (req.tp_points * sym_info.point) if req.tp_points else 0.0
        elif req.order_type == mt5.ORDER_TYPE_SELL:
            price = tick.bid
            sl = price + (req.sl_points * sym_info.point) if req.sl_points else 0.0
            tp = price - (req.tp_points * sym_info.point) if req.tp_points else 0.0
        else:
            raise HTTPException(status_code=400, detail="order_type debe ser 0 (BUY) o 1 (SELL)")

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": req.symbol,
            "volume": float(req.volume),
            "type": req.order_type,
            "price": float(price),
            "sl": float(round(sl, sym_info.digits)) if sl > 0 else 0.0,
            "tp": float(round(tp, sym_info.digits)) if tp > 0 else 0.0,
            "deviation": req.deviation,
            "magic": req.magic,
            "comment": req.comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
        }

        # Validación pre-trade
        check = mt5.order_check(request)
        if check is None or check.retcode != 0:
            detail = check.comment if check else "order_check falló"
            raise HTTPException(status_code=400, detail=f"Pre-check fallido: {detail}")

        result = mt5.order_send(request)
        if result is None:
            err_code, err_desc = mt5.last_error()
            logger.error(f"Error en order_send: {err_code} (detalles omitidos por seguridad)")
            raise HTTPException(status_code=500, detail="Error al enviar orden")

        result_dict = result._asdict()
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise HTTPException(status_code=400, detail=f"Orden rechazada: {result.comment}")

        logger.info(f"Orden ejecutada — Ticket: {result.order}")
        return result_dict
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Error en order_send: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.get("/positions")
def positions():
    """Retorna todas las posiciones abiertas."""
    try:
        pos = mt5.positions_get()
        if pos is None:
            return {"positions": []}
        return {"positions": [p._asdict() for p in pos]}
    except Exception as err:
        logger.error(f"Error en positions: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.get("/symbols")
def symbols(group: Optional[str] = None):
    """Retorna todos los instrumentos disponibles del broker.
    
    Args:
        group: Filtro opcional por grupo (ej: '*EUR*', 'Forex*', 'Crypto*')
    """
    try:
        if group:
            syms = mt5.symbols_get(group=group)
        else:
            syms = mt5.symbols_get()

        if syms is None:
            return {"count": 0, "symbols": []}

        result = []
        for s in syms:
            result.append({
                "name": s.name,
                "description": s.description,
                "path": s.path,
                "currency_base": s.currency_base,
                "currency_profit": s.currency_profit,
                "digits": s.digits,
                "point": s.point,
                "spread": s.spread,
                "trade_contract_size": s.trade_contract_size,
                "volume_min": s.volume_min,
                "volume_max": s.volume_max,
                "volume_step": s.volume_step,
                "trade_mode": s.trade_mode,
                "visible": s.visible,
            })

        # Agrupar por path (categoría)
        categories = {}
        for s in result:
            cat = s["path"].split("\\")[0] if "\\" in s["path"] else "Other"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(s["name"])

        logger.info(f"Símbolos consultados: {len(result)} instrumentos en {len(categories)} categorías")
        return {
            "count": len(result),
            "categories": categories,
            "symbols": result
        }
    except Exception as err:
        logger.error(f"Error en symbols: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.get("/symbols/atr_scan")
def atr_scan(group: Optional[str] = None, atr_period: int = 14):
    """Escanea todos los instrumentos y calcula ATR(14) en D1.
    
    Retorna precio actual, ATR y ATR% (ATR normalizado como % del precio).
    
    Args:
        group: Filtro opcional por grupo (ej: '*EUR*', 'Forex*')
        atr_period: Períodos para el ATR (default: 14)
    """
    try:
        if group:
            syms = mt5.symbols_get(group=group)
        else:
            syms = mt5.symbols_get()

        if syms is None or len(syms) == 0:
            return {"count": 0, "results": []}

        results = []
        errors = 0
        bars_needed = atr_period + 1  # +1 para calcular TR del primer período
        total = len(syms)
        log_step = max(1, total // 10)  # Log cada 10%

        logger.info(f"ATR Scan iniciado: {total} instrumentos por procesar")
        for idx, s in enumerate(syms):
            if idx % log_step == 0:
                pct = (idx / total) * 100
                logger.info(f"  ATR Scan: {pct:.0f}% ({idx}/{total}) — {len(results)} OK, {errors} errores")
            try:
                # Seleccionar símbolo
                if not mt5.symbol_select(s.name, True):
                    errors += 1
                    continue

                # Obtener barras D1 (primero, porque necesitamos el precio de cierre como fallback)
                rates = mt5.copy_rates_from_pos(s.name, mt5.TIMEFRAME_D1, 0, bars_needed + 1)
                if rates is None or len(rates) < bars_needed:
                    errors += 1
                    continue

                df = pd.DataFrame(rates)

                # Precio: usar tick actual si disponible, sino último cierre D1
                tick = mt5.symbol_info_tick(s.name)
                if tick and tick.bid > 0 and tick.ask > 0:
                    price = (tick.bid + tick.ask) / 2.0
                    bid = tick.bid
                    ask = tick.ask
                    price_source = "live"
                else:
                    price = float(df['close'].iloc[-1])
                    bid = price
                    ask = price
                    price_source = "last_close"

                if price <= 0:
                    errors += 1
                    continue

                # Calcular True Range
                df['prev_close'] = df['close'].shift(1)
                df['tr1'] = df['high'] - df['low']
                df['tr2'] = (df['high'] - df['prev_close']).abs()
                df['tr3'] = (df['low'] - df['prev_close']).abs()
                df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

                # ATR = media de los últimos N true ranges
                tr_values = df['tr'].dropna().values
                if len(tr_values) < atr_period:
                    errors += 1
                    continue

                atr = float(np.mean(tr_values[-atr_period:]))
                atr_pct = (atr / price) * 100.0

                # Extraer categoría del path
                path = s.path
                parts = path.split("\\")
                category = "\\".join(parts[1:-1]) if len(parts) >= 3 else "Other"

                results.append({
                    "symbol": s.name,
                    "description": s.description,
                    "category": category,
                    "price": round(price, s.digits),
                    "bid": bid,
                    "ask": ask,
                    "spread": s.spread,
                    "atr": round(atr, s.digits),
                    "atr_pct": round(atr_pct, 4),
                    "digits": s.digits,
                    "contract_size": s.trade_contract_size,
                    "price_source": price_source,
                })

            except Exception:
                errors += 1
                continue

        # Ordenar por ATR% descendente
        results.sort(key=lambda x: x["atr_pct"], reverse=True)

        logger.info(f"ATR Scan completado: {len(results)} instrumentos procesados, {errors} errores")
        return {
            "count": len(results),
            "errors": errors,
            "atr_period": atr_period,
            "timeframe": "D1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results
        }
    except Exception as err:
        logger.error(f"Error en atr_scan: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.get("/symbols/atr_history")
def atr_history(group: Optional[str] = None, symbols: Optional[str] = None, atr_period: int = 14, days: int = 30):
    """Calcula el ATR(14) rolling para los últimos N días de cada instrumento.
    
    Retorna la serie temporal de ATR y ATR% para análisis de tendencia de volatilidad.
    
    Args:
        group: Filtro opcional por grupo
        symbols: Lista de símbolos separados por coma (ej: 'EURUSD,GBPUSD,XAUUSD')
        atr_period: Períodos para el ATR (default: 14)
        days: Días de historia a retornar (default: 30)
    """
    try:
        if symbols:
            # Lista específica de símbolos
            sym_list = [s.strip() for s in symbols.split(",")]
            syms = []
            for sym_name in sym_list:
                info = mt5.symbol_info(sym_name)
                if info is not None:
                    mt5.symbol_select(sym_name, True)
                    syms.append(info)
                else:
                    logger.warning(f"Símbolo no encontrado: {sym_name}")
        elif group:
            syms = mt5.symbols_get(group=group)
        else:
            syms = mt5.symbols_get()

        if syms is None or len(syms) == 0:
            return {"count": 0, "results": []}

        results = []
        errors = 0
        # Necesitamos: days de ATR output + atr_period para el cálculo + 1 para prev_close
        bars_needed = days + atr_period + 2
        total = len(syms)
        log_step = max(1, total // 10)

        logger.info(f"ATR History iniciado: {total} instrumentos, {days} días de historia")
        for idx, s in enumerate(syms):
            if idx % log_step == 0:
                pct = (idx / total) * 100
                logger.info(f"  ATR History: {pct:.0f}% ({idx}/{total}) — {len(results)} OK, {errors} errores")
            try:
                if not mt5.symbol_select(s.name, True):
                    errors += 1
                    continue

                rates = mt5.copy_rates_from_pos(s.name, mt5.TIMEFRAME_D1, 0, bars_needed)
                if rates is None or len(rates) < atr_period + 2:
                    errors += 1
                    continue

                df = pd.DataFrame(rates)
                df['date'] = pd.to_datetime(df['time'], unit='s').dt.strftime('%Y-%m-%d')

                # Calcular True Range
                df['prev_close'] = df['close'].shift(1)
                df['tr'] = pd.concat([
                    df['high'] - df['low'],
                    (df['high'] - df['prev_close']).abs(),
                    (df['low'] - df['prev_close']).abs()
                ], axis=1).max(axis=1)

                # Rolling ATR
                df['atr'] = df['tr'].rolling(window=atr_period).mean()

                # ATR% usando el precio de cierre de cada día
                df['atr_pct'] = (df['atr'] / df['close']) * 100.0

                # Tomar solo los últimos N días con ATR válido
                valid = df.dropna(subset=['atr']).tail(days)

                if len(valid) < 2:
                    errors += 1
                    continue

                # Serie temporal
                history = []
                for _, row in valid.iterrows():
                    history.append({
                        "date": row['date'],
                        "close": round(float(row['close']), s.digits),
                        "atr": round(float(row['atr']), s.digits),
                        "atr_pct": round(float(row['atr_pct']), 4),
                    })

                # Métricas de tendencia
                atr_now = history[-1]['atr_pct']
                atr_start = history[0]['atr_pct']
                atr_change = round(atr_now - atr_start, 4)
                atr_max = round(max(h['atr_pct'] for h in history), 4)
                atr_min = round(min(h['atr_pct'] for h in history), 4)

                # Categoría
                path = s.path
                parts = path.split("\\")
                category = "\\".join(parts[1:-1]) if len(parts) >= 3 else "Other"

                results.append({
                    "symbol": s.name,
                    "description": s.description,
                    "category": category,
                    "atr_current": round(atr_now, 4),
                    "atr_30d_ago": round(atr_start, 4),
                    "atr_change": atr_change,
                    "atr_max": atr_max,
                    "atr_min": atr_min,
                    "trend": "expanding" if atr_change > 0.5 else ("contracting" if atr_change < -0.5 else "stable"),
                    "days_available": len(history),
                    "history": history,
                })

            except Exception:
                errors += 1
                continue

        # Ordenar por cambio absoluto de ATR (los que más cambiaron)
        results.sort(key=lambda x: abs(x["atr_change"]), reverse=True)

        logger.info(f"ATR History completado: {len(results)} instrumentos, {errors} errores")
        return {
            "count": len(results),
            "errors": errors,
            "atr_period": atr_period,
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results
        }
    except Exception as err:
        logger.error(f"Error en atr_history: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.get("/symbols/swap_scan")
def swap_scan(group: Optional[str] = None):
    """Escanea todos los instrumentos y retorna costos de swap (long y short).
    
    Los swaps son datos estáticos del contrato, funcionan incluso con mercados cerrados.
    
    Args:
        group: Filtro opcional por grupo (ej: 'Forex*', 'Crypto*')
    """
    try:
        if group:
            syms = mt5.symbols_get(group=group)
        else:
            syms = mt5.symbols_get()

        if syms is None or len(syms) == 0:
            return {"count": 0, "results": []}

        # Mapa de swap_mode
        SWAP_MODES = {
            0: "Disabled",
            1: "Points",
            2: "Money (base currency)",
            3: "Money (margin currency)",
            4: "Money (deposit currency)",
            5: "Interest (annual %)",
            6: "Reopen by close price",
            7: "Reopen by bid price",
        }

        results = []
        total = len(syms)
        log_step = max(1, total // 10)  # Log cada 10%

        logger.info(f"Swap Scan iniciado: {total} instrumentos por procesar")
        for idx, s in enumerate(syms):
            if idx % log_step == 0:
                pct = (idx / total) * 100
                logger.info(f"  Swap Scan: {pct:.0f}% ({idx}/{total})")
            try:
                info = mt5.symbol_info(s.name)
                if info is None:
                    continue

                # Extraer categoría del path
                parts = info.path.split("\\")
                category = "\\".join(parts[1:-1]) if len(parts) >= 3 else "Other"

                # Obtener precio mid si hay tick disponible
                tick = mt5.symbol_info_tick(s.name)
                price = round((tick.bid + tick.ask) / 2.0, info.digits) if tick and tick.bid > 0 else None

                results.append({
                    "symbol": info.name,
                    "description": info.description,
                    "category": category,
                    "price": price,
                    "swap_long": info.swap_long,
                    "swap_short": info.swap_short,
                    "swap_mode": info.swap_mode,
                    "swap_mode_desc": SWAP_MODES.get(info.swap_mode, f"Unknown ({info.swap_mode})"),
                    "swap_rollover3days": info.swap_rollover3days,
                    "digits": info.digits,
                    "currency_base": info.currency_base,
                    "currency_profit": info.currency_profit,
                    "trade_contract_size": info.trade_contract_size,
                })
            except Exception:
                continue

        # Ordenar por swap_long descendente (más costosos primero)
        results.sort(key=lambda x: abs(x["swap_long"]), reverse=True)

        logger.info(f"Swap Scan completado: {len(results)} instrumentos procesados")
        return {
            "count": len(results),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results
        }
    except Exception as err:
        logger.error(f"Error en swap_scan: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.post("/switch_account")
def switch_account(req: SwitchAccountRequest):
    """Cambia la cuenta de MT5 conectada.
    
    Las credenciales se leen del archivo local ~/.mt5_accounts.json en Windows.
    Solo se envía el alias del broker por HTTP (nunca la contraseña).
    """
    try:
        accounts = load_accounts()
        if not accounts:
            raise HTTPException(
                status_code=500,
                detail=f"No se encontró archivo de cuentas en {ACCOUNTS_FILE}. Ejecuta setup_accounts.py primero."
            )

        broker_key = req.broker.lower().strip()
        if broker_key not in accounts:
            available = list(accounts.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Broker '{broker_key}' no encontrado. Disponibles: {available}"
            )

        acct = accounts[broker_key]
        login = acct["login"]
        password = acct["password"]
        server = acct["server"]

        # Cerrar conexión actual
        mt5.shutdown()
        logger.info(f"Conexión MT5 cerrada. Reconectando a {server}...")

        # Reconectar con nueva cuenta
        if not mt5.initialize(login=login, password=password, server=server, timeout=10000):
            err_code, err_desc = mt5.last_error()
            # Intentar reconectar a la cuenta anterior
            mt5.initialize()
            raise HTTPException(
                status_code=500,
                detail=f"No se pudo conectar a {server}: {err_code} - {err_desc}"
            )

        info = mt5.account_info()
        logger.info(f"Cuenta cambiada exitosamente → {info.server} | Login: {info.login}")

        return {
            "status": "ok",
            "login": info.login,
            "server": info.server,
            "balance": info.balance,
            "currency": info.currency,
            "name": info.name,
        }
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Error en switch_account: {type(err).__name__} (detalles omitidos por seguridad)")
        raise HTTPException(status_code=500, detail=f"Error de operación: {type(err).__name__}")


@app.get("/accounts")
def list_accounts():
    """Lista los brokers disponibles (sin mostrar credenciales)."""
    accounts = load_accounts()
    current = mt5.account_info()
    return {
        "available": list(accounts.keys()),
        "current": {
            "server": current.server if current else None,
            "login": current.login if current else None,
        }
    }


@app.get("/health")
def health():
    """Health check del Gateway."""
    t_info = mt5.terminal_info()
    connected = t_info is not None and t_info.connected if t_info else False
    return {
        "gateway": "online",
        "mt5_connected": connected,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Apagando Gateway — cerrando conexión MT5")
    mt5.shutdown()


# ─── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    # Inicializar MT5 al arrancar
    if not mt5.initialize():
        err_code, err_desc = mt5.last_error()
        logger.critical(f"No se pudo inicializar MT5: {err_code} - {err_desc}")
        exit(1)

    logger.info(f"MT5 conectado — Cuenta: {mt5.account_info().login} | Servidor: {mt5.account_info().server}")
    logger.info("Iniciando Gateway en http://0.0.0.0:8000")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
