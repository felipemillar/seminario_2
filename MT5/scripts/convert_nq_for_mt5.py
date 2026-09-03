"""
Script de Conversion de Datos NQ M5 para MetaTrader 5
Autor: QRT Solutions
Modulo: seminario_2 / MT5 / masterclass
"""

import csv
import os
import shutil
import time

SRC_FILE = "/Users/fmillar/Proyectos_Desarrollo/seminario_2/masterclass/@NQ_5m.csv"
OUT_DIR = "/Users/fmillar/Proyectos_Desarrollo/seminario_2/masterclass"
WINE_DESKTOP = "/Users/fmillar/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/users/user/Desktop"

OUT_ALL = os.path.join(OUT_DIR, "NQ_5M_MT5_ALL.csv")
OUT_RECENT = os.path.join(OUT_DIR, "NQ_5M_MT5_2020_2026.csv")

def run_conversion():
    print(f"[INICIO] Leyendo origen: {SRC_FILE}")
    t0 = time.time()
    
    total_rows = 0
    recent_rows = 0
    
    # Abrir archivos de salida
    with open(SRC_FILE, "r", encoding="utf-8", errors="replace") as f_in, \
         open(OUT_ALL, "w", encoding="utf-8", newline="") as f_all, \
         open(OUT_RECENT, "w", encoding="utf-8", newline="") as f_rec:
        
        reader = csv.reader(f_in)
        header = next(reader)
        
        # MT5 standard header
        mt5_header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>"]
        writer_all = csv.writer(f_all)
        writer_rec = csv.writer(f_rec)
        
        writer_all.writerow(mt5_header)
        writer_rec.writerow(mt5_header)
        
        for row in reader:
            if not row or len(row) < 7:
                continue
            
            total_rows += 1
            
            # Timestamp: "2024-01-02 00:00:00+00:00"
            raw_ts = row[0]
            ts_clean = raw_ts.split("+")[0]
            parts = ts_clean.split(" ")
            if len(parts) != 2:
                continue
            
            date_str = parts[0].replace("-", ".")
            time_str = parts[1][:5]
            
            o = row[2]
            h = row[3]
            l = row[4]
            c = row[5]
            vol = row[6]      # TotalVolume
            ticks = row[10]   # TotalTicks
            
            out_row = [date_str, time_str, o, h, l, c, ticks, vol]
            
            # Escribir en archivo completo
            writer_all.writerow(out_row)
            
            # Filtrar para reciente (desde 2020.01.01)
            if date_str >= "2020.01.01":
                recent_rows += 1
                writer_rec.writerow(out_row)
    
    elapsed = time.time() - t0
    sz_all = os.path.getsize(OUT_ALL) / (1024 * 1024)
    sz_rec = os.path.getsize(OUT_RECENT) / (1024 * 1024)
    
    print(f"\n[OK] Conversion completada en {elapsed:.2f} segundos.")
    print(f"  - Archivo Completo (2000-2026): {total_rows:,} velas | {sz_all:.2f} MB -> {OUT_ALL}")
    print(f"  - Archivo Reciente (2020-2026): {recent_rows:,} velas | {sz_rec:.2f} MB -> {OUT_RECENT}")
    
    # Copiar a Wine Desktop para acceso instantaneo en MT5
    if os.path.exists(WINE_DESKTOP):
        shutil.copy2(OUT_ALL, os.path.join(WINE_DESKTOP, "NQ_5M_MT5_ALL.csv"))
        shutil.copy2(OUT_RECENT, os.path.join(WINE_DESKTOP, "NQ_5M_MT5_2020_2026.csv"))
        print(f"\n[OK] Archivos desplegados directamente en el Escritorio de MT5 (Wine):")
        print(f"  -> {WINE_DESKTOP}/NQ_5M_MT5_ALL.csv")
        print(f"  -> {WINE_DESKTOP}/NQ_5M_MT5_2020_2026.csv")

if __name__ == "__main__":
    run_conversion()
