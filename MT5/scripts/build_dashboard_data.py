import json
import os
import glob
from pathlib import Path

def main():
    print("Construyendo dashboard/data.json...")
    output = {}
    base_dir = Path(__file__).parent.parent
    
    # 1. ATR data (general)
    atr_path = base_dir / 'data' / 'atr_scan.json'
    if atr_path.exists():
        with open(atr_path) as f:
            atr = json.load(f)
        output['atr'] = {
            'count': atr['count'],
            'errors': atr.get('errors', 0),
            'top': atr['results'][:50],
            'bottom': atr['results'][-20:],
        }
        
        cat_atr = {}
        for r in atr['results']:
            cat = r['category'].split('\\\\')[0] if '\\\\' in r['category'] else r['category']
            if cat not in cat_atr:
                cat_atr[cat] = []
            cat_atr[cat].append(r['atr_pct'])
        output['atr_by_category'] = {k: {'avg': round(sum(v)/len(v),4), 'max': round(max(v),4), 'min': round(min(v),4), 'count': len(v)} for k,v in cat_atr.items()}

    # 2. Swap data - 3 brokers
    brokers = {}
    for name, rel_path in [('Pepperstone', 'data/queries/2026-06-29/swap_scan.json'), 
                           ('Capitaria', 'data/queries/capitaria-all/2026-06-29/swap_scan.json'), 
                           ('GrupoInteligencia', 'data/queries/grupointeligenciaspa-server/2026-06-29/swap_scan.json')]:
        path = base_dir / rel_path
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            positive = [r for r in data['results'] if r['swap_long'] > 0 or r['swap_short'] > 0]
            brokers[name] = {
                'count': data['count'],
                'positive_count': len(positive),
                'top_positive': sorted(positive, key=lambda x: max(x['swap_long'], x['swap_short']), reverse=True)[:15],
            }
    output['brokers'] = brokers

    # 3. Arbitrage
    arb_path = base_dir / 'data' / 'queries' / 'swap_arbitrage.json'
    if arb_path.exists():
        with open(arb_path) as f:
            arb = json.load(f)
        output['arbitrage'] = arb['same_mode_opportunities']

    # 4. ATR History (Latam or specific)
    history_files = glob.glob(str(base_dir / 'data' / 'queries' / '*' / '*' / 'atr_history.json'))
    if history_files:
        # Tomamos el primero que encontremos para el dashboard (debería ser el recién generado)
        with open(history_files[0]) as f:
            hist_data = json.load(f)
        output['atr_history'] = hist_data.get('results', [])

    # Guardar
    out_path = base_dir / 'dashboard' / 'data.json'
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
    
    print(f"[OK] Dashboard data actualizada: {out_path} ({out_path.stat().st_size//1024}KB)")

if __name__ == "__main__":
    main()
