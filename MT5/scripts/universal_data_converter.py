"""
Conversor Universal de Datos Externos para MetaTrader 5
Autor: QRT Solutions
Licencia: Propietaria / Institucional

Este modulo normaliza cualquier conjunto de datos historicos (TradingView, TradeStation,
NinjaTrader, Binance, Yahoo Finance, etc.) al estandar nativo de barras de MetaTrader 5.
"""

import argparse
import csv
import logging
import os
import re
import shutil
import sys
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("UniversalDataConverter")

# Directorio MQL5/Files segun sistema operativo
def get_mql5_files_dir() -> Optional[str]:
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        p = os.path.join(appdata, "MetaQuotes", "Terminal")
        if os.path.exists(p):
            for d in os.listdir(p):
                target = os.path.join(p, d, "MQL5", "Files")
                if os.path.exists(target):
                    return target
        return "C:\\Program Files\\MetaTrader 5\\MQL5\\Files"
    else:
        # macOS / Linux bajo Wine
        wine_files = os.path.expanduser(
            "~/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/Files"
        )
        if os.path.exists(wine_files):
            return wine_files
    return None

def detect_delimiter(sample_line: str) -> str:
    """Detecta automaticamente el delimitador del archivo de texto."""
    for delim in [",", "\t", ";", "|"]:
        if len(sample_line.split(delim)) >= 5:
            return delim
    return ","

def map_column_indices(header: List[str]) -> Dict[str, int]:
    """Mapea dinamicamente las columnas requeridas analizando el encabezado."""
    mapping = {
        "timestamp": -1,
        "date": -1,
        "time": -1,
        "open": -1,
        "high": -1,
        "low": -1,
        "close": -1,
        "tick_volume": -1,
        "volume": -1
    }
    
    clean_header = [h.strip().lower().replace("<", "").replace(">", "").replace(" ", "_") for h in header]
    
    for idx, col in enumerate(clean_header):
        if col in ["timestamp", "datetime", "date_time", "time_stamp", "ts"]:
            mapping["timestamp"] = idx
        elif col in ["date", "fecha"]:
            mapping["date"] = idx
        elif col in ["time", "hora"] and mapping["timestamp"] != idx:
            mapping["time"] = idx
        elif col in ["open", "apertura", "o"]:
            mapping["open"] = idx
        elif col in ["high", "maximo", "max", "h"]:
            mapping["high"] = idx
        elif col in ["low", "minimo", "min", "l"]:
            mapping["low"] = idx
        elif col in ["close", "cierre", "c"]:
            mapping["close"] = idx
        elif col in ["totalticks", "tickvol", "tick_volume", "ticks"]:
            mapping["tick_volume"] = idx
        elif col in ["totalvolume", "volume", "vol", "volumen", "real_volume"]:
            mapping["volume"] = idx

    # Si hay columna combinada timestamp y no hay date/time separadas
    if mapping["timestamp"] != -1 and (mapping["date"] == -1 or mapping["time"] == -1):
        mapping["date"] = mapping["timestamp"]
        mapping["time"] = mapping["timestamp"]
        
    return mapping

def parse_datetime(val_date: str, val_time: str) -> Tuple[str, str]:
    """Convierte cualquier fecha y hora al estandar MT5: YYYY.MM.DD y HH:MM."""
    # Si vienen en el mismo campo
    combined = f"{val_date} {val_time}".strip() if val_date != val_time else val_date.strip()
    
    # Limpiar sufijos de zona horaria: +00:00 o Z
    clean_ts = combined.split("+")[0].split("Z")[0].replace("T", " ").strip()
    parts = re.split(r"\s+", clean_ts)
    
    raw_date = parts[0]
    raw_time = parts[1] if len(parts) > 1 else "00:00"
    
    # Normalizar fecha con puntos
    date_normalized = re.sub(r"[-/]", ".", raw_date)
    
    # Normalizar hora a HH:MM
    time_normalized = raw_time[:5]
    if len(time_normalized) == 4 and time_normalized[1] == ":":
        time_normalized = "0" + time_normalized
        
    return date_normalized, time_normalized

def convert_dataset_to_mt5(
    input_path: str,
    output_path: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    deploy_to_mql5: bool = True
) -> Dict[str, any]:
    """
    Lee cualquier dataset intradiario y genera un archivo CSV estandarizado de MT5.
    Retorna estadisticas de conversion y rutas de despliegue.
    """
    stats = {
        "success": False,
        "total_read": 0,
        "total_converted": 0,
        "elapsed_seconds": 0.0,
        "output_file": None,
        "deployed_file": None,
        "first_date": None,
        "last_date": None
    }
    
    if not os.path.exists(input_path):
        logger.error(f"Archivo de entrada no existe: {input_path}")
        return stats
        
    t0 = time.time()
    
    try:
        with open(input_path, "r", encoding="utf-8", errors="replace") as f_sample:
            first_line = f_sample.readline()
            delim = detect_delimiter(first_line)
            
        with open(input_path, "r", encoding="utf-8", errors="replace") as f_in:
            reader = csv.reader(f_in, delimiter=delim)
            header = next(reader)
            col_map = map_column_indices(header)
            
            # Validar columnas minimas
            if col_map["date"] == -1 or col_map["open"] == -1 or col_map["close"] == -1:
                logger.error(f"No se pudieron detectar las columnas OHLC obligatorias en el archivo.")
                return stats
                
            # Determinar ruta de salida
            if not output_path:
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(os.path.dirname(input_path), f"{base_name}_MT5.csv")
                
            mt5_header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>"]
            
            with open(output_path, "w", encoding="utf-8", newline="") as f_out:
                writer = csv.writer(f_out)
                writer.writerow(mt5_header)
                
                for row in reader:
                    if not row or len(row) < 4:
                        continue
                        
                    stats["total_read"] += 1
                    
                    try:
                        d_raw = row[col_map["date"]]
                        t_raw = row[col_map["time"]]
                        d_norm, t_norm = parse_datetime(d_raw, t_raw)
                        
                        # Filtros de fecha opcionales
                        if from_date and d_norm < from_date:
                            continue
                        if to_date and d_norm > to_date:
                            continue
                            
                        open_p  = float(row[col_map["open"]])
                        high_p  = float(row[col_map["high"]]) if col_map["high"] != -1 else open_p
                        low_p   = float(row[col_map["low"]]) if col_map["low"] != -1 else open_p
                        close_p = float(row[col_map["close"]])
                        
                        tick_vol = int(float(row[col_map["tick_volume"]])) if col_map["tick_volume"] != -1 else 100
                        real_vol = int(float(row[col_map["volume"]])) if col_map["volume"] != -1 else tick_vol
                        
                        if stats["first_date"] is None:
                            stats["first_date"] = f"{d_norm} {t_norm}"
                        stats["last_date"] = f"{d_norm} {t_norm}"
                        
                        writer.writerow([d_norm, t_norm, open_p, high_p, low_p, close_p, tick_vol, real_vol])
                        stats["total_converted"] += 1
                        
                    except Exception as row_err:
                        continue
                        
        stats["elapsed_seconds"] = round(time.time() - t0, 2)
        stats["output_file"] = os.path.abspath(output_path)
        stats["success"] = (stats["total_converted"] > 0)
        
        # Copiar a MQL5/Files si esta activo
        if deploy_to_mql5:
            mql5_dir = get_mql5_files_dir()
            if mql5_dir and os.path.exists(mql5_dir):
                target_in_mql5 = os.path.join(mql5_dir, os.path.basename(output_path))
                shutil.copy2(output_path, target_in_mql5)
                stats["deployed_file"] = target_in_mql5
                logger.info(f"Copiado automaticamente a MQL5/Files: {target_in_mql5}")
                
        logger.info(
            f"Conversion exitosa: {stats['total_converted']:,} velas procesadas en {stats['elapsed_seconds']}s "
            f"({stats['first_date']} -> {stats['last_date']})"
        )
        
    except Exception as err:
        logger.error(f"Error durante conversion de datos: {type(err).__name__} (detalles omitidos por seguridad)")
        stats["error"] = f"Error de operacion: {type(err).__name__}"
        
    return stats

def main():
    parser = argparse.ArgumentParser(description="Conversor Universal de Datos a MT5")
    parser.add_argument("--input", "-i", required=True, help="Ruta al archivo CSV/TSV de entrada")
    parser.add_argument("--output", "-o", default=None, help="Ruta de salida para el CSV de MT5")
    parser.add_argument("--from-date", default=None, help="Fecha inicio filtro (ej. 2020.01.01)")
    parser.add_argument("--to-date", default=None, help="Fecha fin filtro (ej. 2026.09.01)")
    parser.add_argument("--no-deploy", action="store_true", help="No copiar automaticamente a MQL5/Files")
    
    args = parser.parse_args()
    res = convert_dataset_to_mt5(
        input_path=args.input,
        output_path=args.output,
        from_date=args.from_date,
        to_date=args.to_date,
        deploy_to_mql5=not args.no_deploy
    )
    if res["success"]:
        print(f"[OK] Archivo generado: {res['output_file']}")
        if res["deployed_file"]:
            print(f"[OK] Desplegado en MT5: {res['deployed_file']}")
    else:
        print("[ERROR] Fallo la conversion del dataset.")
        sys.exit(1)

if __name__ == "__main__":
    main()
