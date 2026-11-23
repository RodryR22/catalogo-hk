# Actualiza "Disponible / Sin stock" del catálogo HK.
# Uso: python3 herramientas/actualizar_stock.py STOCK_REPRE.xls STOCK_AUTOCENTRO.xls
# Escribe stock.js y stock-historial.json (data.js no se toca). También se puede cargar a mano en admin.html.
# Disponible = la suma de las columnas "Stock 1..7" de ambos archivos es mayor a 0.
# Solo se publica la lista de códigos disponibles, nunca cantidades.
import xlrd, json, re, sys, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def num(v):
    if isinstance(v, (int, float)): return float(v)
    try: return float(str(v).strip().replace('.', '').replace(',', '.') or 0)
    except: return 0
ST = {}
for f in sys.argv[1:3]:
    sh = xlrd.open_workbook(f).sheet_by_index(0)
    hdr = [str(x).strip() for x in sh.row_values(1)]
    ci = hdr.index('Código'); cols = [j for j, h in enumerate(hdr) if h.startswith('Stock')]
    if not cols: sys.exit('ERROR: no encuentro columnas Stock en ' + f)
    for i in range(2, sh.nrows):
        r = sh.row_values(i); c = str(r[ci]).strip().upper()
        if c: ST[c] = ST.get(c, 0) + sum(num(r[j]) for j in cols)
D = [{'hk': c} for c in re.findall(r'"hk":\s*"([^"]+)"', open(os.path.join(ROOT, 'data.js'), encoding='utf8').read())]
miss = [d['hk'] for d in D if d['hk'].upper() not in ST]
if len(miss) > len(D) * 0.2: sys.exit(f'ERROR: {len(miss)} códigos no figuran en los archivos; no se actualiza.')
av = [d['hk'] for d in D if ST.get(d['hk'].upper(), 0) > 0]
sp = os.path.join(ROOT, 'stock.js')
old = re.search(r'window\.HK_STOCK=(\[.*?\]);', open(sp, encoding='utf8').read(), re.S) if os.path.exists(sp) else None
old = json.loads(old.group(1)) if old else []
hoy = datetime.date.today().isoformat()
open(sp, 'w', encoding='utf8').write('// Stock HK: solo la lista de códigos disponibles (nunca cantidades). Se actualiza desde admin.html o herramientas/actualizar_stock.py\nwindow.HK_STOCK=' + json.dumps(av) + ';\nwindow.HK_STOCK_FECHA=' + json.dumps(hoy) + ';\n')
hp = os.path.join(ROOT, 'stock-historial.json')
hist = json.load(open(hp, encoding='utf8')) if os.path.exists(hp) else []
up, dn = sorted(set(av) - set(old)), sorted(set(old) - set(av))
if up or dn:
    hist = [{'fecha': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'origen': 'automática', 'archivos': {}, 'disponibles': len(av), 'sin_stock': len(D) - len(av), 'a_disponible': up, 'a_sin_stock': dn}] + hist
    json.dump(hist[:200], open(hp, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(f'Disponibles: {len(av)} de {len(D)} · Sin stock: {len(D)-len(av)}')
print('Pasaron a SIN STOCK:', dn)
print('Pasaron a DISPONIBLE:', up)
print('CAMBIO' if (up or dn) else 'SIN CAMBIOS')
