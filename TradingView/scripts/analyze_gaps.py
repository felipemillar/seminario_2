import re
import os
import glob

# Extraer títulos de los archivos MD generados
md_files = glob.glob('knowledge/*.md')
generated = []
for f in md_files:
    if f.endswith('INDEX.md') or f.endswith('prompts_gen1_tradingview.md') or f.endswith('prompts_gen2_tradingview.md') or f.endswith('lineas_investigacion_tradingview.md'):
        continue
    generated.append(os.path.basename(f).replace('.md', ''))

# Listar todos
print("DOCUMENTOS GENERADOS (" + str(len(generated)) + "):")
for g in sorted(generated):
    print(" - " + g)
print("")

# Extraer contenido de los archivos md para hacer un mapa de calor/resumen de temas
print("EXTRAYENDO CABECERAS PARA MAPEO DE TEMAS...")
temas = {}
for f in md_files:
    if f.endswith('INDEX.md') or f.endswith('prompts_gen1_tradingview.md') or f.endswith('prompts_gen2_tradingview.md') or f.endswith('lineas_investigacion_tradingview.md'):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        headers = re.findall(r'^#+ (.*)', content, re.MULTILINE)
        temas[os.path.basename(f)] = headers[:5] # Tomar los primeros 5 headers principales

for k, v in temas.items():
    print(f"\n{k}:")
    for h in v:
        print(f"  - {h}")

