# Actualiza "Disponible / Sin stock" del catálogo HK.
# Uso: python3 herramientas/actualizar_stock.py STOCK_REPRE.xls STOCK_AUTOCENTRO.xls
# Disponible = la suma de las columnas "Stock 1..7" de ambos archivos es mayor a 0.
# Solo se publica la lista de códigos disponibles, nunca cantidades.
import xlrd, json, re, sys, os, datetime, hashlib
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
p = os.path.join(ROOT, 'data.js')
s = open(p, encoding='utf8').read()
base = s.split('\nwindow.HK_STOCK=')[0].rstrip('\n')
D = json.loads(re.search(r'window\.HK_DATA=(\[.*?\]);\nwindow', base, re.S).group(1))
miss = [d['hk'] for d in D if d['hk'].upper() not in ST]
if len(miss) > len(D) * 0.2: sys.exit(f'ERROR: {len(miss)} códigos no figuran en los archivos; no se actualiza.')
av = [d['hk'] for d in D if ST.get(d['hk'].upper(), 0) > 0]
old = re.search(r'window\.HK_STOCK=(\[.*?\]);', s)
old = json.loads(old.group(1)) if old else []
new = base + '\nwindow.HK_STOCK=' + json.dumps(av) + ';\nwindow.HK_STOCK_FECHA=' + json.dumps(datetime.date.today().isoformat()) + ';\n'
open(p, 'w', encoding='utf8').write(new)
if set(av) != set(old):
    sw = os.path.join(ROOT, 'sw.js'); t = open(sw, encoding='utf8').read()
    t = re.sub(r"const VERSION = '[^']*';", "const VERSION = 'hk-" + hashlib.md5(new.encode()).hexdigest()[:10] + "';", t, 1)
    open(sw, 'w', encoding='utf8').write(t)
print(f'Disponibles: {len(av)} de {len(D)} · Sin stock: {len(D)-len(av)}')
print('Pasaron a SIN STOCK:', sorted(set(old) - set(av)))
print('Pasaron a DISPONIBLE:', sorted(set(av) - set(old)))
print('CAMBIO' if set(av) != set(old) else 'SIN CAMBIOS')
