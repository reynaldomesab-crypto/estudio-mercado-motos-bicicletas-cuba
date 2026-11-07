# -*- coding: utf-8 -*-
"""Genera el sitio estático en docs/ a partir de data/publico y las cifras del estudio."""
import csv, json, collections, pathlib, datetime as dt
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path('.')
OUT = ROOT / 'docs'
ASSETS = OUT / 'assets'
SITE = 'https://reynaldomesab-crypto.github.io/estudio-mercado-motos-bicicletas-cuba/'
FECHA = 'septiembre de 2026'
TOTAL, VEHICULOS = 4979, 4860

# ---------------- datos ----------------
rows = list(csv.DictReader(open('data/publico/vehiculos_clasificados.csv', encoding='utf-8')))
def price(r):
    try:
        v = float(r['price_usd']); return v if v > 0 else None
    except Exception: return None

def q(vals, p):
    vals = sorted(vals); k = (len(vals) - 1) * p
    f = int(k); c = min(f + 1, len(vals) - 1)
    return vals[f] + (vals[c] - vals[f]) * (k - f)

def agg(vals):
    return dict(n=len(vals), p10=round(q(vals, .1)), p25=round(q(vals, .25)),
                p50=round(q(vals, .5)), p75=round(q(vals, .75)), p90=round(q(vals, .9)))

def slug(s):
    rep = {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ñ':'n','ü':'u'}
    s = s.lower().strip()
    for a,b in rep.items(): s = s.replace(a,b)
    return '-'.join(''.join(c if c.isalnum() else ' ' for c in s).split())

tipos_raw, marcas_raw, zonas_raw = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
for r in rows:
    v = price(r)
    if not v: continue
    tipos_raw[r['categoria'].strip()].append(v)
    if r['marca_detectada'].strip(): marcas_raw[r['marca_detectada'].strip()].append(v)
    if r['province_name'].strip() == 'La Habana' and r['municipality_name'].strip():
        zonas_raw[r['municipality_name'].strip()].append(v)

TIPOS = []
for name in ['Motores', 'Eléctricos', 'Patinetes Eléctricos', 'Bicicletas']:
    if name in tipos_raw and len(tipos_raw[name]) >= 30:
        g = agg(tipos_raw[name]); g.update(id=slug(name), nombre=name); TIPOS.append(g)
MARCAS = []
for name, vals in marcas_raw.items():
    if len(vals) >= 30:
        g = agg(vals); g.update(id=slug(name), nombre=name); MARCAS.append(g)
MARCAS.sort(key=lambda g: -g['n'])
ZONAS = []
for name, vals in zonas_raw.items():
    if len(vals) >= 50:
        g = agg(vals); g.update(id=slug(name), nombre=name); ZONAS.append(g)
ZONAS.sort(key=lambda g: g['p50'])

# sin marca por categoría (sobre vehículos)
sin_marca = {}
for cat in ['Motores', 'Eléctricos', 'Patinetes Eléctricos', 'Bicicletas']:
    sub = [r for r in rows if r['categoria'].strip() == cat]
    if sub:
        sin_marca[cat] = round(100 * sum(1 for r in sub if not r['marca_detectada'].strip()) / len(sub), 1)

DATA = dict(meta=dict(total=TOTAL, vehiculos=VEHICULOS, fecha=FECHA, sitio=SITE), tipos=TIPOS, marcas=MARCAS, zonas=ZONAS)
(ASSETS / 'data.js').write_text('window.PRECIOS=' + json.dumps(DATA, ensure_ascii=False, separators=(',', ':')) + ';', encoding='utf-8')

# ---------------- utilidades HTML ----------------
def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def usd(n): return '${:,.0f}'.format(n).replace(',', '.')

def page(name, title, desc, body, current, extra_head=''):
    nav = [('index.html','Inicio','inicio'),('resumen.html','Resumen','resumen'),('guia.html','Guía','guia'),
           ('precios.html','Precios','precios'),('datos.html','Datos','datos'),('metodo.html','Método','metodo')]
    links = ''.join(
        f'<li><a class="lnk" href="{h}"{" aria-current=\"page\"" if k==current else ""}>{t}</a></li>'
        for h,t,k in nav)
    canonical = SITE + ('' if name == 'index.html' else name)
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}og.png">
<meta property="og:locale" content="es_CU">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#12314a">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='18' fill='%2312314a'/%3E%3Ctext x='50' y='68' font-size='54' font-family='sans-serif' font-weight='bold' fill='%23f2b544' text-anchor='middle'%3E2R%3C/text%3E%3C/svg%3E">
{extra_head}
</head>
<body>
<a class="skip" href="#main">Ir al contenido</a>
<header class="site">
  <div class="wrap nav">
    <a class="brand" href="index.html">Mercado de dos ruedas<small>La Habana · datos abiertos</small></a>
    <nav aria-label="Principal"><ul>{links}</ul></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site">
  <div class="wrap">
    <div class="cols">
      <div>
        <h4>Estudio de mercado</h4>
        <p>4.979 anuncios de Revolico, iTENCEL, ElYerro y Facebook recogidos entre el 19 y el 24 de septiembre de 2026. Estudio independiente, sin fines comerciales.</p>
        <p class="small">Datos anonimizados conforme a la Ley 149/2022. Precios declarados por el vendedor: no son avalúos.</p>
      </div>
      <div>
        <h4>Leer</h4>
        <ul>
          <li><a href="resumen.html">Resumen de 3 minutos</a></li>
          <li><a href="guia.html">Guía para vender</a></li>
          <li><a href="precios.html">Calculadora</a></li>
          <li><a href="metodo.html">Método y límites</a></li>
          <li><a href="prensa.html">Kit de prensa</a></li>
        </ul>
      </div>
      <div>
        <h4>Fuente</h4>
        <ul>
          <li><a href="https://github.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba" rel="noopener">Repositorio en GitHub</a></li>
          <li><a href="https://raw.githubusercontent.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba/main/analysis/INFORME_FINAL.html" rel="noopener" download>Informe completo (HTML, 1,7 MB)</a></li>
          <li><a href="datos.html">Dataset y cómo citar</a></li>
        </ul>
      </div>
    </div>
    <p class="small" style="margin-top:26px;opacity:.75">© 2026 · Contenido abierto para uso educativo y de investigación. Si detectas un error, abre un issue en el repositorio.</p>
  </div>
</footer>
<script src="assets/config.js"></script>
<script src="assets/analytics.js" defer></script>
<script src="assets/data.js" defer></script>
<script src="assets/app.js" defer></script>
</body>
</html>'''

def bars(items, key='p50', label='label', unit='', color='#12314a', highlight=None, width=640):
    n = len(items); rowh = 38; h = n * rowh + 18
    mx = max(i[key] for i in items) or 1
    out = [f'<figure class="chart"><svg viewBox="0 0 {width} {h}" role="img" aria-label="Gráfico de barras">']
    for idx, it in enumerate(items):
        y = idx * rowh + 6
        v = it[key]
        bw = max(2, (v / mx) * (width - 250))
        c = '#c47f00' if (highlight and it[label] == highlight) else color
        out.append(f'<text x="0" y="{y+18}" font-size="13" fill="#31424f">{esc(it[label])}</text>')
        out.append(f'<rect x="150" y="{y+4}" width="{bw:.1f}" height="20" rx="4" fill="{c}"/>')
        val = f'{v:,.0f}'.replace(',', '.') if key != 'pct' else f'{v:.1f}%'
        out.append(f'<text x="{150+bw+8:.1f}" y="{y+19}" font-size="13" font-weight="700" fill="#12314a">{val}{unit}</text>')
    out.append('</svg>')
    return ''.join(out) + f'<figcaption>{esc("")}</figcaption></figure>'

def chart_marca():
    items = [{'label': k, 'v': v} for k, v in sin_marca.items()]
    items.sort(key=lambda x: -x['v'])
    n = len(items); rowh = 42; h = n * rowh + 18; width = 640
    out = [f'<figure class="chart"><svg viewBox="0 0 {width} {h}" role="img" aria-label="Porcentaje de anuncios sin marca por tipo de vehículo">']
    for i, it in enumerate(items):
        y = i * rowh + 6
        bw = (it['v'] / 100) * (width - 220)
        c = '#c47f00' if it['v'] >= 80 else '#12314a'
        out.append(f'<text x="0" y="{y+20}" font-size="13" fill="#31424f">{esc(it["label"])}</text>')
        out.append(f'<rect x="130" y="{y+5}" width="{bw:.1f}" height="22" rx="4" fill="{c}"/>')
        out.append(f'<text x="{130+bw+8:.1f}" y="{y+21}" font-size="13" font-weight="700" fill="#12314a">{it["v"]:.1f}%</text>')
    out.append('</svg><figcaption>Porcentaje de anuncios que no declaran la marca en el título, por tipo de vehículo. Fuente: 4.860 vehículos clasificados.</figcaption></figure>')
    return ''.join(out)

def chart_zonas():
    items = [{'label': z['nombre'], 'p50': z['p50'], 'n': z['n']} for z in ZONAS]
    items.sort(key=lambda x: x['p50'])
    n = len(items); rowh = 34; h = n * rowh + 20; width = 640
    mx = max(i['p50'] for i in items)
    out = [f'<figure class="chart"><svg viewBox="0 0 {width} {h}" role="img" aria-label="Precio mediano por municipio de La Habana">']
    for i, it in enumerate(items):
        y = i * rowh + 4
        bw = (it['p50'] / mx) * (width - 290)
        c = '#c47f00' if it['label'] in ('Cerro', 'Habana del Este') else '#12314a'
        out.append(f'<text x="0" y="{y+18}" font-size="13" fill="#31424f">{esc(it["label"])}</text>')
        out.append(f'<rect x="150" y="{y+4}" width="{bw:.1f}" height="19" rx="4" fill="{c}"/>')
        out.append(f'<text x="{150+bw+8:.1f}" y="{y+18}" font-size="12" font-weight="700" fill="#12314a">{usd(it["p50"])} <tspan fill="#6b7a86" font-weight="400">n={it["n"]}</tspan></text>')
    out.append('</svg><figcaption>Precio mediano declarado por municipio (anuncios con precio y municipio; mezcla tipos de vehículo). No es un avalúo.</figcaption></figure>')
    return ''.join(out)

def chart_tipos():
    items = [{'label': t['nombre'], 'p50': t['p50']} for t in TIPOS]
    n = len(items); rowh = 44; h = n * rowh + 18; width = 640
    mx = max(i['p50'] for i in items)
    out = [f'<figure class="chart"><svg viewBox="0 0 {width} {h}" role="img" aria-label="Precio mediano por tipo de vehículo">']
    for i, it in enumerate(items):
        y = i * rowh + 6
        bw = (it['p50'] / mx) * (width - 250)
        out.append(f'<text x="0" y="{y+20}" font-size="13" fill="#31424f">{esc(it["label"])}</text>')
        out.append(f'<rect x="150" y="{y+5}" width="{bw:.1f}" height="22" rx="4" fill="#12314a"/>')
        out.append(f'<text x="{150+bw+8:.1f}" y="{y+21}" font-size="13" font-weight="700" fill="#12314a">{usd(it["p50"])}</text>')
    out.append('</svg><figcaption>Precio mediano declarado por tipo. Mezcla marcas y estados: úsalo como punto de partida, no como precio de venta.</figcaption></figure>')
    return ''.join(out)

def tabla_tipos():
    r = ''.join(f'<tr><td>{t["nombre"]}</td><td class="num-col">{t["n"]:,}</td><td class="num-col">{usd(t["p10"])}</td><td class="num-col"><strong>{usd(t["p50"])}</strong></td><td class="num-col">{usd(t["p90"])}</td></tr>'.replace(',', '.') for t in TIPOS)
    return f'<div class="tablewrap"><table><thead><tr><th>Tipo</th><th class="num-col">Anuncios</th><th class="num-col">p10</th><th class="num-col">Mediana</th><th class="num-col">p90</th></tr></thead><tbody>{r}</tbody></table></div>'

def tabla_marcas(limit=12):
    r = ''.join(f'<tr><td>{esc(m["nombre"])}</td><td class="num-col">{m["n"]}</td><td class="num-col">{usd(m["p10"])}</td><td class="num-col"><strong>{usd(m["p50"])}</strong></td><td class="num-col">{usd(m["p90"])}</td></tr>' for m in MARCAS[:limit])
    return f'<div class="tablewrap"><table><thead><tr><th>Marca</th><th class="num-col">Anuncios</th><th class="num-col">p10</th><th class="num-col">Mediana</th><th class="num-col">p90</th></tr></thead><tbody>{r}</tbody></table></div>'

def tabla_zonas():
    r = ''.join(f'<tr><td>{esc(z["nombre"])}</td><td class="num-col">{z["n"]}</td><td class="num-col"><strong>{usd(z["p50"])}</strong></td><td class="num-col">{usd(z["p10"])}</td><td class="num-col">{usd(z["p90"])}</td></tr>' for z in ZONAS)
    return f'<div class="tablewrap"><table><thead><tr><th>Municipio</th><th class="num-col">Anuncios</th><th class="num-col">Mediana</th><th class="num-col">p10</th><th class="num-col">p90</th></tr></thead><tbody>{r}</tbody></table></div>'

def share_row(text, title='Estudio de mercado de dos ruedas en La Habana'):
    return f'''<div class="share">
  <button class="btn btn-dark" type="button" data-share data-title="{esc(title)}" data-text="{esc(text)}">Compartir este dato</button>
  <a class="btn btn-line" href="guia.html">Ver la guía</a>
</div>'''

def cta_final():
    return '''<section class="soft"><div class="wrap narrow center">
  <h2>Empieza por lo que te sirve hoy</h2>
  <p>Si vendes: descarga el checklist de 10 cambios que no cuestan nada. Si compras: mira la mediana de tu zona antes de negociar.</p>
  <div class="cta-row" style="justify-content:center">
    <a class="btn btn-primary" href="guia.html">Guía para vender mejor</a>
    <a class="btn btn-line" href="precios.html">Calcular un precio</a>
  </div>
</div></section>'''

# ---------------- páginas ----------------
INDEX = f'''
<section class="hero">
  <div class="wrap">
    <span class="kicker">El mercado invisible · Estudio de 4.979 anuncios · La Habana</span>
    <h1>El <em>45,5%</em> de las motos en venta en La Habana no dice su marca.</h1>
    <p class="lead">Analicé 4.979 anuncios de Revolico, iTENCEL, ElYerro y Facebook. El problema no es el precio: es la información. Y casi todo se arregla gratis.</p>
    <div class="cta-row">
      <a class="btn btn-primary" href="resumen.html">Resumen de 3 minutos</a>
      <a class="btn btn-ghost" href="precios.html">Calcular un precio justo</a>
    </div>
    <div class="stats">
      <div class="stat"><b>4.979</b><span>anuncios únicos analizados en 4 plataformas</span></div>
      <div class="stat"><b>93,9%</b><span>publica precio: el problema es compararlo</span></div>
      <div class="stat"><b>2,7×</b><span>de diferencia de mediana entre municipios</span></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>¿Quién eres?</h2>
    <p class="narrow muted">El estudio habla de tu mercado. Empieza por el camino que te corresponde.</p>
    <div class="grid-2" style="margin-top:22px">
      <div class="card accent">
        <span class="pill">Vendo</span>
        <h3 style="margin-top:12px">Mi anuncio no aparece</h3>
        <p>No es que esté mal posicionado: es que no existe para la búsqueda. Quien busca la marca no lo ve.</p>
        <ul class="checklist small">
          <li>45,5% no dice la marca en el título</li>
          <li>43,3% no tiene ninguna cifra</li>
          <li>8,8% no dice el municipio</li>
        </ul>
        <p style="margin-top:16px"><a href="guia.html"><strong>Guía con 10 cambios gratis →</strong></a></p>
      </div>
      <div class="card accent">
        <span class="pill">Compro</span>
        <h3 style="margin-top:12px">No sé si estoy pagando de más</h3>
        <p>Antes de negociar, mira la mediana y el rango habitual de lo que se está pidiendo.</p>
        <ul class="checklist small">
          <li>Por tipo de vehículo</li>
          <li>Por marca (con muestra suficiente)</li>
          <li>Por municipio de La Habana</li>
        </ul>
        <p style="margin-top:16px"><a href="precios.html"><strong>Calcular precio de referencia →</strong></a></p>
      </div>
      <div class="card accent">
        <span class="pill">Repuestos · delivery</span>
        <h3 style="margin-top:12px">Vivo del taller o de la mensajería</h3>
        <p>Mira qué se está pidiendo, en qué zona y dónde hay menos competencia publicada.</p>
        <ul class="checklist small">
          <li>Precios por municipio</li>
          <li>64 patinetes: casi sin competencia</li>
          <li>130 de 260 “repuestos” eran vehículos</li>
        </ul>
        <p style="margin-top:16px"><a href="resumen.html"><strong>Ver el mercado →</strong></a></p>
      </div>
      <div class="card accent">
        <span class="pill">Prensa · estudio</span>
        <h3 style="margin-top:12px">Escribo, enseño o investigo</h3>
        <p>Llévate los datos listos, dos ángulos de nota y el método para citar sin errores.</p>
        <ul class="checklist small">
          <li>5 datos con fuente</li>
          <li>Dataset anonimizado</li>
          <li>Informe y figuras</li>
        </ul>
        <p style="margin-top:16px"><a href="prensa.html"><strong>Kit de prensa →</strong></a></p>
      </div>
    </div>
  </div>
</section>

<section class="soft">
  <div class="wrap">
    <h2>El cambio de 30 segundos</h2>
    <p class="narrow">Estos dos anuncios podrían ser el mismo vehículo. La diferencia no es el producto: es la información.</p>
    <div class="grid-2" style="margin-top:22px">
      <div class="card">
        <span class="pill" style="color:#8a1c1c;border-color:#e6b8b8;background:#fbe9e9">Antes</span>
        <h3 style="margin-top:12px">“MOTO SE VENDE”</h3>
        <p class="muted">Sin marca, sin cifra, sin zona. No aparece en ninguna búsqueda por marca, por autonomía ni por municipio.</p>
      </div>
      <div class="card">
        <span class="pill" style="color:#1e5a3a;border-color:#b9d8c6;background:#e8f3ec">Después</span>
        <h3 style="margin-top:12px">“Moto eléctrica AVA, 100 km, seminueva, Centro Habana”</h3>
        <p class="muted">Marca, cifra clave, estado y zona. Aparece en las búsquedas que importan.</p>
      </div>
    </div>
    <div class="cta-row" style="margin-top:24px">
      <a class="btn btn-primary" href="assets/checklist.pdf" download>Descargar el checklist (PDF)</a>
      <a class="btn btn-line" href="guia.html">Ver los 10 puntos</a>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Lo que encontró el estudio</h2>
    <div class="finding"><div class="fig">45,5%<small>sin marca</small></div><div><h3>No aparecen cuando alguien busca por marca</h3><p class="muted">2.210 de los 4.860 vehículos no dicen su marca en el título. En bicicletas llega al 87,1%.</p></div></div>
    <div class="finding"><div class="fig">43,3%<small>sin cifra</small></div><div><h3>No hay con qué comparar</h3><p class="muted">2.155 anuncios no tienen ni un número en el título: ni precio, ni cilindraje, ni autonomía.</p></div></div>
    <div class="finding"><div class="fig">2,7×<small>por zona</small></div><div><h3>La ubicación también es precio</h3><p class="muted">Cerro: 700 USD de mediana. Habana del Este: 1.920. Misma ciudad, distinta oferta publicada.</p></div></div>
    <div class="finding"><div class="fig">64<small>patinetes</small></div><div><h3>El hueco más grande del mercado</h3><p class="muted">Ese es el tamaño de la competencia en patinetes eléctricos. En bicicletas, 87,1% no documenta la marca.</p></div></div>
    <p style="margin-top:26px"><a class="btn btn-dark" href="resumen.html">Leer el resumen completo</a></p>
  </div>
</section>

<section class="soft">
  <div class="wrap narrow">
    <h2>Lo que este estudio no puede decir</h2>
    <ul class="checklist">
      <li><strong>No observa ventas.</strong> Solo anuncios: más publicado no es más vendido.</li>
      <li><strong>No distingue nuevo de usado.</strong> No hay campo de condición.</li>
      <li><strong>No mide tendencias.</strong> No hay fecha por anuncio: es una fotografía de cuatro jornadas.</li>
      <li><strong>No es un avalúo.</strong> Los precios son los que declaró cada vendedor.</li>
    </ul>
    <p style="margin-top:18px"><a href="metodo.html">Cómo se hizo y qué se corrigió →</a></p>
  </div>
</section>
{cta_final()}
'''

RESUMEN = f'''
<section class="tight">
  <div class="wrap narrow">
    <span class="pill">Resumen · 3 minutos</span>
    <h1 style="font-size:clamp(28px,4.6vw,42px);line-height:1.12;color:var(--ink);margin:14px 0 10px">El mercado en 3 minutos</h1>
    <p class="lead" style="font-size:19px;color:#31424f">4.979 anuncios. Cuatro plataformas. Una conclusión: el problema no es la oferta, es la información que la hace comparable.</p>
  </div>
</section>

<section class="tight">
  <div class="wrap narrow">
    <h2><span class="num">1</span>El punto de partida</h2>
    <p>Se recogieron <strong>4.979 anuncios únicos</strong> de Revolico, iTENCEL, ElYerro y Facebook entre el 19 y el 24 de septiembre de 2026. Tras clasificarlos, <strong>4.860 son vehículos</strong> (97,6%). El <strong>93,9%</strong> publica precio.</p>
    <p class="muted">El precio, entonces, no es el dato que falta. Lo que falta es lo que permite compararlo.</p>

    <h2><span class="num">2</span>Lo que no se publica</h2>
    <p>El <strong>45,5%</strong> no dice la marca. El <strong>43,3%</strong> no tiene ninguna cifra en el título. El <strong>8,8%</strong> no declara el municipio.</p>
    {chart_marca()}
    <p>En bicicletas el problema es casi total: <strong>87,1%</strong> de 518 anuncios no dice la marca. Es la categoría peor documentada del mercado.</p>

    <h2><span class="num">3</span>Por qué importa</h2>
    <p>Un anuncio sin marca no aparece cuando alguien busca “Topmaq”, “AVA” o “Suzuki”. Sin cifra, no se puede comparar autonomía, cilindraje ni precio. Sin municipio, no entra en ninguna comparación por zona.</p>
    <div class="callout"><p><strong>No es un problema de producto. Es de información.</strong> Y la información se arregla sin gastar un peso.</p></div>

    <h2><span class="num">4</span>El precio, por tipo</h2>
    {chart_tipos()}
    {tabla_tipos()}
    <p class="small muted">Medianas de anuncios con precio declarado. Mezclan marcas y estados: son referencia, no avalúo.</p>

    <h2><span class="num">5</span>El precio, por zona</h2>
    {chart_zonas()}
    <p>Cerro y Habana del Este están a <strong>2,7 veces</strong> en la misma ciudad. La mediana mezcla tipos de vehículo, así que el dato sirve para <strong>posicionarte</strong>, no para fijar un precio exacto.</p>

    <h2><span class="num">6</span>Dónde está la oportunidad</h2>
    <p><strong>Patinetes:</strong> 64 anuncios en todo el mercado. <strong>Bicicletas:</strong> 518, con 87,1% sin marca. <strong>Zonas:</strong> Centro Habana concentra el 24% de los anuncios con precio y municipio; fuera del centro hay menos competencia y casi la misma demanda.</p>

    <h2><span class="num">7</span>El estándar mínimo</h2>
    <p>Cuatro datos convierten un anuncio invisible en uno localizable: <strong>marca, una cifra clave, municipio y WhatsApp</strong>. El 59,9% ya publica WhatsApp; el resto deja compradores fuera.</p>
    <div class="cta-row">
      <a class="btn btn-primary" href="guia.html">Ver la guía de 10 puntos</a>
      <a class="btn btn-line" href="precios.html">Calcular un precio</a>
    </div>
  </div>
</section>

<section class="soft">
  <div class="wrap narrow">
    <h2><span class="num">8</span>Los límites, antes de que los preguntes</h2>
    <ul class="checklist">
      <li>No hay datos de ventas: solo anuncios publicados.</li>
      <li>No hay condición (nuevo/usado) ni fecha por anuncio.</li>
      <li>Los precios son declarados, no avalúos.</li>
      <li>La deduplicación es por URL: un mismo vehículo en dos sitios cuenta dos veces.</li>
    </ul>
    <p style="margin-top:18px"><a href="metodo.html">Leer el método completo →</a></p>
  </div>
</section>
{cta_final()}
'''

GUIA = f'''
<section class="tight">
  <div class="wrap narrow">
    <span class="pill">Guía práctica</span>
    <h1 style="font-size:clamp(28px,4.6vw,42px);line-height:1.12;color:var(--ink);margin:14px 0 10px">Guía para vender mejor</h1>
    <p class="lead" style="font-size:19px;color:#31424f">Diez cambios que no cuestan nada, escritos a partir de 4.860 anuncios reales. No es un curso ni publicidad.</p>
    <div class="callout"><p><strong>Si solo vas a hacer una cosa:</strong> escribe la marca en el título. Es el cambio de costo cero con más efecto.</p></div>
  </div>
</section>

<section class="tight">
  <div class="wrap narrow">
    <ol class="steps">
      <li><h3>Escribe la marca en el título</h3><p>El 45,5% no lo hace. Quien busca una marca concreta no ve esos anuncios: no es que estén mal posicionados, es que no existen para esa búsqueda.</p></li>
      <li><h3>Añade una cifra clave</h3><p>Autonomía en km, cilindraje en cc, voltaje o kilómetros recorridos. El 43,3% de los títulos no tiene ningún número.</p></li>
      <li><h3>Declara el municipio</h3><p>El 8,8% no dice dónde está. Sin municipio no apareces en ninguna comparación por zona ni en la búsqueda de quien busca en su barrio.</p></li>
      <li><h3>Publica WhatsApp y un horario</h3><p>El 59,9% ya lo usa. Un número que no atiende es peor que no publicarlo: el comprador escribe una vez y no vuelve.</p></li>
      <li><h3>Declara el estado</h3><p>Nueva, seminueva o usada. Es la pregunta que el comprador hace primero; si no está, la hace con desconfianza.</p></li>
      <li><h3>Usa fotos reales</h3><p>Del vehículo, no de catálogo. Una foto de catálogo sugiere que el vehículo no está o que oculta algo.</p></li>
      <li><h3>Revisa la mediana de tu marca antes de fijar precio</h3><p>TOPMAQ: 2.150 USD de mediana. CHALLENGER: 850. La diferencia dentro de la misma categoría supera 3 veces.</p></li>
      <li><h3>Compara por zona, no contra tu vecino</h3><p>Cerro y Habana del Este están a 2,7 veces. La zona también explica el precio que puedes pedir.</p></li>
      <li><h3>Publica en más de una fuente</h3><p>Ninguna plataforma cubre el mercado sola. Revolico aporta volumen; iTENCEL, precio y marca; Facebook, contactos.</p></li>
      <li><h3>Borra duplicados y anuncios vacíos</h3><p>Ocupan lugar sin informar a nadie y hacen que tu perfil parezca descuidado. El estudio encontró duplicados en la propia base: se corrigió antes de contar.</p></li>
    </ol>
    <div class="cta-row" style="margin-top:26px">
      <a class="btn btn-primary" href="assets/checklist.pdf" download>Descargar checklist (PDF, 2 páginas)</a>
      <a class="btn btn-line" href="precios.html">Ver precios de referencia</a>
    </div>
  </div>
</section>

<section class="soft">
  <div class="wrap">
    <h2>Antes y después</h2>
    <div class="grid-2">
      <div class="card"><span class="pill">Antes</span><h3 style="margin-top:12px">“MOTO SE VENDE”</h3><p class="muted">No dice marca, cifra ni zona. No aparece en ninguna búsqueda útil.</p></div>
      <div class="card"><span class="pill">Después</span><h3 style="margin-top:12px">“Moto eléctrica AVA, 100 km, seminueva, Centro Habana, WhatsApp”</h3><p class="muted">Aparece por marca, por autonomía, por estado y por zona.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Precios de referencia</h2>
    <p class="narrow muted">Medianas de anuncios con precio declarado. No son avalúos: úsalas para saber dónde estás, no para fijar un precio exacto.</p>
    <h3 style="margin-top:26px">Por tipo de vehículo</h3>
    {tabla_tipos()}
    <h3 style="margin-top:26px">Por marca (todas las categorías)</h3>
    {tabla_marcas(12)}
    <h3 style="margin-top:26px">Por municipio de La Habana</h3>
    {tabla_zonas()}
    <p class="small muted" style="margin-top:16px">Solo se muestran grupos con al menos 30 anuncios (marcas y tipos) o 50 (municipios), para evitar conclusiones sobre muestras pequeñas.</p>
  </div>
</section>
{cta_final()}
'''

PRECIOS = f'''
<section class="tight">
  <div class="wrap narrow">
    <span class="pill">Calculadora</span>
    <h1 style="font-size:clamp(28px,4.6vw,42px);line-height:1.12;color:var(--ink);margin:14px 0 10px">¿Está caro o está bien?</h1>
    <p class="lead" style="font-size:19px;color:#31424f">Compara un precio con la mediana y el rango habitual del mercado. Elige tipo, marca o municipio; si quieres, escribe el precio que te piden.</p>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="calc">
      <div class="modes" role="group" aria-label="Criterio de comparación">
        <button class="mode" type="button" data-mode="tipos" aria-pressed="true">Por tipo</button>
        <button class="mode" type="button" data-mode="marcas" aria-pressed="false">Por marca</button>
        <button class="mode" type="button" data-mode="zonas" aria-pressed="false">Por municipio</button>
      </div>
      <div class="fields">
        <div>
          <label class="field" for="grupo">Grupo</label>
          <select id="grupo"></select>
        </div>
        <div>
          <label class="field" for="precio">Precio que te piden o quieres pedir (USD, opcional)</label>
          <input id="precio" type="number" min="1" step="10" inputmode="numeric" placeholder="Ej.: 1600">
        </div>
      </div>
      <div class="result" id="resultado" aria-live="polite">
        <p class="muted">Cargando datos…</p>
      </div>
      <p class="small muted" style="margin:14px 0 0">La calculadora necesita JavaScript. Si no carga, usa las tablas de abajo.</p>
    </div>

    <div class="warn">
      <p><strong>Esto no es un avalúo.</strong> Son precios declarados por los vendedores en sus anuncios, no precios de venta. La comparación es de posición relativa: sirve para saber si estás dentro del rango, no para certificar cuánto vale un vehículo.</p>
    </div>

    <h2 style="margin-top:36px">Tablas completas</h2>
    <details open><summary><strong>Por tipo de vehículo</strong></summary>{tabla_tipos()}</details>
    <details><summary><strong>Por marca</strong></summary>{tabla_marcas(20)}</details>
    <details><summary><strong>Por municipio</strong></summary>{tabla_zonas()}</details>
    <p class="small muted">Solo grupos con muestra suficiente: 30 anuncios o más para tipo y marca; 50 o más para municipio.</p>
  </div>
</section>
{cta_final()}
'''

DATOS = f'''
<section class="tight">
  <div class="wrap narrow">
    <span class="pill">Datos abiertos</span>
    <h1 style="font-size:clamp(28px,4.6vw,42px);line-height:1.12;color:var(--ink);margin:14px 0 10px">Dataset, campos y cómo citar</h1>
    <p class="lead" style="font-size:19px;color:#31424f">4.979 anuncios anonimizados, con diccionario de campos y límites documentados. Abierto para investigación, docencia y verificación.</p>
  </div>
</section>

<section class="tight">
  <div class="wrap narrow">
    <h2>Descargar</h2>
    <p>El archivo público contiene una fila por anuncio único, sin nombres, teléfonos ni URLs identificativas.</p>
    <p><a class="btn btn-dark" href="https://raw.githubusercontent.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba/main/data/publico/vehiculos_clasificados.csv" rel="noopener" download>vehiculos_clasificados.csv (754 KB)</a></p>

    <h2 style="margin-top:34px">Campos</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>Campo</th><th>Qué contiene</th></tr></thead>
      <tbody>
        <tr><td>title</td><td>Título normalizado del anuncio</td></tr>
        <tr><td>source</td><td>Plataforma de origen (revolico, itencel, facebook, elyerro)</td></tr>
        <tr><td>categoria</td><td>Motores, Eléctricos, Bicicletas, Patinetes, Otros, Partes</td></tr>
        <tr><td>marca_detectada</td><td>Marca atribuida por el clasificador (vacío si no hay señal)</td></tr>
        <tr><td>price_usd</td><td>Precio declarado, normalizado a USD</td></tr>
        <tr><td>province_name / municipality_name</td><td>Provincia y municipio detectados</td></tr>
        <tr><td>tiene_whatsapp</td><td>Si el anuncio incluye un contacto de WhatsApp</td></tr>
        <tr><td>anuncio_id / telefono_id</td><td>Identificadores seudonimizados (hash SHA-256)</td></tr>
      </tbody>
    </table></div>

    <h2 style="margin-top:34px">Cómo citar</h2>
    <div class="callout"><p>Estudio de Mercado de Motos, Bicicletas y Patinetes en Cuba (2026). <em>El mercado de vehículos de dos ruedas en La Habana: 4.979 anuncios analizados</em>. Repositorio: github.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba</p></div>

    <h2 style="margin-top:34px">Condiciones de uso</h2>
    <ul class="checklist">
      <li>Datos anonimizados; no intentes reidentificar a personas.</li>
      <li>No uses el dataset para contactar vendedores ni para publicidad.</li>
      <li>No se recogieron datos sensibles (Art. 15, Ley 149/2022).</li>
      <li>Cita la fuente y conserva las limitaciones junto a las cifras.</li>
    </ul>

    <h2 style="margin-top:34px">Límites que debes arrastrar</h2>
    <p>No hay ventas, ni condición, ni fecha por anuncio. Los precios son declarados. La deduplicación es por URL. Cualquier análisis que ignore esto producirá conclusiones falsas con mucha seguridad.</p>
    <p><a href="metodo.html">Ver el método completo →</a></p>
  </div>
</section>
'''

METODO = f'''
<section class="tight">
  <div class="wrap narrow">
    <span class="pill">Método</span>
    <h1 style="font-size:clamp(28px,4.6vw,42px);line-height:1.12;color:var(--ink);margin:14px 0 10px">Cómo se hizo (y qué se corrigió)</h1>
    <p class="lead" style="font-size:19px;color:#31424f">Un estudio reproducible vale por lo que documenta, incluidos sus errores. Estos son los cinco que cambiaron las cifras.</p>
  </div>
</section>

<section class="tight">
  <div class="wrap narrow">
    <h2>El proceso</h2>
    <ol class="steps">
      <li><h3>Recolección</h3><p>Scrapers contra cuatro plataformas, con límite de velocidad y respeto a <code>robots.txt</code>. Datos crudos inmutables y sello de tiempo por registro.</p></li>
      <li><h3>Deduplicación</h3><p>Conteo inicial: 5.787. Tras deduplicar por URL: <strong>4.979</strong>. La diferencia eran 412 anuncios repetidos.</p></li>
      <li><h3>Normalización</h3><p>Facebook guarda el texto en <code>text</code>, no en <code>title</code>. Recuperarlo redujo los títulos vacíos de 606 a 11.</p></li>
      <li><h3>Taxonomía</h3><p>Cinco categorías con reglas jerárquicas sobre el título sin acentos ni Unicode tipográfico. Auditoría de marcas: cobertura del 22,6% al 50,9%.</p></li>
      <li><h3>Auditoría automática</h3><p>Nueve comprobaciones sobre todas las clasificaciones. Resultado: cero problemas graves, y un bug en la propia auditoría que se corrigió.</p></li>
      <li><h3>Anonimización</h3><p>Lista blanca de campos, hash SHA-256 con sal y retirada de teléfonos, nombres y URLs antes de publicar.</p></li>
    </ol>

    <h2 style="margin-top:34px">Los cinco errores que cambiaron las cifras</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>Error</th><th>Efecto</th></tr></thead>
      <tbody>
        <tr><td>Dataset duplicado</td><td>5.787 anuncios inflados; el real era 4.979</td></tr>
        <tr><td>Texto de Facebook en otro campo</td><td>606 “sin título” que no eran culpa del vendedor</td></tr>
        <tr><td>Acentos y Unicode tipográfico</td><td>“ELÉCTRICA” y “𝐁𝐈𝐂𝐈𝐌𝐎𝐓𝐎” no se reconocían</td></tr>
        <tr><td>Señal eléctrica incompleta</td><td>Motores cayó de 2.264 a 1.036; eléctricos subió a 3.006</td></tr>
        <tr><td>Auditoría con bug de comparación</td><td>Reportaba “cero problemas” siempre</td></tr>
      </tbody>
    </table></div>

    <h2 style="margin-top:34px">Qué no puede decir este estudio</h2>
    <ul class="checklist">
      <li>No observa ventas: solo anuncios publicados.</li>
      <li>No distingue nuevo de usado: no hay campo de condición.</li>
      <li>No hay fecha por anuncio: no se puede afirmar tendencia ni estacionalidad.</li>
      <li>Los precios son declarados, no avalúos.</li>
      <li>La deduplicación es por URL: un vehículo en dos sitios cuenta dos veces.</li>
    </ul>

    <h2 style="margin-top:34px">Privacidad</h2>
    <p>Los datos se obtuvieron de fuentes de acceso público y se disociaron antes de publicar (Ley 149/2022, Arts. 17.e y 17.f). No se recogen datos sensibles. No se usan los teléfonos para contactar a nadie. Si apareces en el dataset y quieres ejercer tus derechos, abre un issue en el repositorio.</p>

    <h2 style="margin-top:34px">Reproducir</h2>
    <p>El pipeline completo, los scripts y la auditoría están en el repositorio. El informe académico se descarga aparte porque pesa 1,7 MB:</p>
    <p><a class="btn btn-line" href="https://raw.githubusercontent.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba/main/analysis/INFORME_FINAL.html" rel="noopener" download>Descargar el informe completo (HTML)</a></p>
  </div>
</section>
{cta_final()}
'''

NOTFOUND = '''
<section class="hero"><div class="wrap narrow">
  <span class="kicker">Error 404</span>
  <h1>Esta página no existe.</h1>
  <p class="lead">Pero el estudio sí. Vuelve al inicio o mira el resumen de 3 minutos.</p>
  <div class="cta-row"><a class="btn btn-primary" href="index.html">Ir al inicio</a><a class="btn btn-ghost" href="resumen.html">Ver el resumen</a></div>
</div></section>
'''

PRENSA = f'''
<section class="tight">
  <div class="wrap narrow">
    <span class="pill">Kit de prensa</span>
    <h1 style="font-size:clamp(28px,4.6vw,42px);line-height:1.12;color:var(--ink);margin:14px 0 10px">Kit de prensa</h1>
    <p class="lead" style="font-size:19px;color:#31424f">Cinco datos con fuente, dos ángulos de nota y todo el material para citar sin errores. Sin registro.</p>
    <div class="cta-row">
      <a class="btn btn-dark" href="https://raw.githubusercontent.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba/main/analysis/INFORME_FINAL.html" rel="noopener" download>Descargar informe (HTML, 1,7 MB)</a>
      <a class="btn btn-line" href="datos.html">Ver dataset y citación</a>
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <h2>Cinco datos con fuente</h2>
    <p class="muted">Todos salen de 4.979 anuncios únicos recogidos entre el 19 y el 24 de septiembre de 2026. Precios declarados, no avalúos.</p>
    <div class="tablewrap"><table>
      <thead><tr><th>Dato</th><th class="num-col">Cifra</th><th>Contexto</th></tr></thead>
      <tbody>
        <tr><td>Anuncios sin marca</td><td class="num-col">45,5%</td><td>2.210 de 4.860 vehículos: no aparecen en búsquedas por marca</td></tr>
        <tr><td>Bicicletas sin marca</td><td class="num-col">87,1%</td><td>451 de 518: la categoría peor documentada</td></tr>
        <tr><td>Títulos sin ninguna cifra</td><td class="num-col">43,3%</td><td>2.155 anuncios: sin precio, cilindraje ni autonomía</td></tr>
        <tr><td>Brecha entre municipios</td><td class="num-col">2,7×</td><td>Cerro 700 USD · Habana del Este 1.920 USD (medianas)</td></tr>
        <tr><td>Patinetes eléctricos</td><td class="num-col">64</td><td>Anuncios en todo el mercado: casi sin competencia</td></tr>
      </tbody>
    </table></div>

    <h2 style="margin-top:34px">Dos ángulos de nota</h2>
    <div class="grid-2">
      <div class="card accent">
        <h3>“Por qué tu moto no se vende”</h3>
        <p>Ángulo de consumo y emprendimiento. El problema no es el precio: es que el anuncio no dice lo que el comprador busca. Se resuelve gratis en 30 segundos.</p>
      </div>
      <div class="card accent">
        <h3>“Cómo saber si te están cobrando de más”</h3>
        <p>Ángulo de comprador. La mediana por tipo, marca y municipio da un punto de comparación antes de negociar. La calculadora lo hace en 10 segundos.</p>
      </div>
    </div>
    <p class="muted" style="margin-top:14px">Tercer ángulo disponible: <strong>“El mercado invisible de las bicicletas”</strong> (87,1% sin marca y 64 patinetes en toda la ciudad).</p>

    <h2 style="margin-top:34px">Qué puedes usar</h2>
    <ul class="checklist">
      <li><a href="resumen.html">Resumen de 3 minutos</a> con las cifras principales.</li>
      <li><a href="https://raw.githubusercontent.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba/main/analysis/INFORME_FINAL.html" rel="noopener" download>Informe completo</a> con 13 figuras y metodología.</li>
      <li><a href="datos.html">Dataset anonimizado</a> y diccionario de campos.</li>
      <li><a href="metodo.html">Método, errores corregidos y límites</a>.</li>
      <li>Entrevista de 20 minutos o datos específicos para tu ángulo.</li>
    </ul>

    <h2 style="margin-top:34px">Cómo citar</h2>
    <div class="callout"><p>Estudio de Mercado de Motos, Bicicletas y Patinetes en Cuba (2026). <em>El mercado de vehículos de dos ruedas en La Habana: 4.979 anuncios analizados</em>. github.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba</p></div>

    <h2 style="margin-top:34px">Contacto</h2>
    <p>Para entrevistas o datos adicionales, abre un issue en el repositorio con la etiqueta <strong>prensa</strong>:</p>
    <p><a class="btn btn-line" href="https://github.com/reynaldomesab-crypto/estudio-mercado-motos-bicicletas-cuba/issues/new" rel="noopener">Abrir un issue de prensa</a></p>
    <p class="small muted">Este estudio es independiente y no tiene fines comerciales. No promete ventas ni predice precios: diagnostica la información publicada.</p>
  </div>
</section>
{cta_final()}
'''

pages = {
    'index.html': ('El 45,5% de las motos en venta en La Habana no dice su marca',
                   'Estudio de 4.979 anuncios del mercado de motos, bicicletas y patinetes en La Habana: qué información falta y cómo arreglarla gratis.', INDEX, 'inicio'),
    'resumen.html': ('El mercado en 3 minutos · Estudio de 4.979 anuncios',
                     'Resumen del estudio: precios, marcas, zonas y los datos que faltan en los anuncios de vehículos de dos ruedas en La Habana.', RESUMEN, 'resumen'),
    'guia.html': ('Guía para vender mejor · 10 cambios que no cuestan nada',
                  'Guía práctica basada en 4.860 anuncios: marca, cifra clave, municipio, WhatsApp y precios de referencia por marca y zona.', GUIA, 'guia'),
    'precios.html': ('Calculadora de precio de referencia · Motos en La Habana',
                     'Compara un precio con la mediana y el rango del mercado por tipo, marca o municipio. Precios declarados, no avalúos.', PRECIOS, 'precios'),
    'datos.html': ('Dataset abierto · 4.979 anuncios anonimizados',
                   'Descarga el dataset anonimizado, revisa los campos, las condiciones de uso y cómo citar el estudio.', DATOS, 'datos'),
    'metodo.html': ('Método, errores corregidos y límites del estudio',
                    'Cómo se recogieron y auditaron 4.979 anuncios, qué errores se corrigieron y qué no puede afirmar el estudio.', METODO, 'metodo'),
    'prensa.html': ('Kit de prensa · Estudio de 4.979 anuncios en La Habana',
                    'Cinco datos con fuente, dos ángulos de nota, informe, dataset y método para citar el estudio del mercado de dos ruedas.', PRENSA, 'prensa'),
}
for name, (title, desc, body, current) in pages.items():
    (OUT / name).write_text(page(name, title, desc, body, current), encoding='utf-8')
(OUT / '404.html').write_text(page('404.html', 'Página no encontrada', 'Vuelve al estudio.', NOTFOUND, ''), encoding='utf-8')
print('páginas generadas:', len(pages) + 1)

# ---------------- imágenes ----------------
FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textbbox((0, 0), t, font=font)[2] <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def og_image():
    W, H = 1200, 630
    im = Image.new('RGB', (W, H), '#12314a'); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 14, H], fill='#c47f00')
    f_kick = ImageFont.truetype(FONT_B, 22); f_big = ImageFont.truetype(FONT_B, 210)
    f_txt = ImageFont.truetype(FONT_B, 50); f_sub = ImageFont.truetype(FONT_R, 26)
    d.text((70, 62), 'ESTUDIO DE MERCADO · LA HABANA', font=f_kick, fill='#f0c56d')
    d.text((62, 120), '45,5%', font=f_big, fill='#f2b544')
    y = 360
    for line in wrap(d, 'de las motos en venta no dice su marca', f_txt, 1040):
        d.text((70, y), line, font=f_txt, fill='#ffffff'); y += 58
    d.text((70, 520), '4.979 anuncios · 4 plataformas · septiembre 2026', font=f_sub, fill='#c9d8e4')
    d.text((70, 562), 'Datos abiertos · sin fines comerciales', font=f_sub, fill='#8fb0c9')
    im.save(OUT / 'og.png', optimize=True)

def card(name, big, lines, foot, accent='#f2b544'):
    W, H = 1080, 1350
    im = Image.new('RGB', (W, H), '#12314a'); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 12], fill=accent)
    f_kick = ImageFont.truetype(FONT_B, 26); f_big = ImageFont.truetype(FONT_B, 300 if len(big) <= 4 else 220)
    f_txt = ImageFont.truetype(FONT_B, 62); f_foot = ImageFont.truetype(FONT_R, 28)
    d.text((72, 74), 'ESTUDIO DE MERCADO · LA HABANA', font=f_kick, fill='#f0c56d')
    d.text((60, 170), big, font=f_big, fill=accent)
    y = 560
    for line in lines:
        for l in wrap(d, line, f_txt, 940):
            d.text((72, y), l, font=f_txt, fill='#ffffff'); y += 74
        y += 10
    d.text((72, 1180), foot, font=f_foot, fill='#c9d8e4')
    d.text((72, 1224), '4.979 anuncios · datos abiertos', font=f_foot, fill='#8fb0c9')
    im.save(OUT / 'assets' / name, optimize=True)

og_image()
card('tarjeta-marca.png', '45,5%', ['de las motos en venta', 'no dice su marca'], 'La información decide si te encuentran')
card('tarjeta-zona.png', '2,7×', ['de diferencia entre', 'municipios de La Habana'], 'Cerro $700 · Habana del Este $1.920')
card('tarjeta-checklist.png', '10', ['cambios que no', 'cuestan nada'], 'marca · cifra · zona · WhatsApp')

# ---------------- checklist PDF ----------------
HTML_CHECK = f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><style>
@page {{ size:A4; margin:18mm 16mm; }}
body {{ font-family:'DejaVu Sans',Arial,sans-serif; color:#1b232a; font-size:10.5pt; line-height:1.45; }}
.kick {{ font-size:8pt; letter-spacing:.16em; text-transform:uppercase; color:#c47f00; font-weight:bold; }}
h1 {{ font-size:25pt; line-height:1.1; color:#12314a; margin:4mm 0 3mm; letter-spacing:-.02em; }}
.lead {{ color:#41525f; font-size:11pt; margin-bottom:6mm; }}
.rule {{ height:2mm; width:32mm; background:#c47f00; margin:4mm 0 6mm; }}
ol {{ padding-left:0; list-style:none; margin:0; counter-reset:s; }}
li {{ counter-increment:s; position:relative; padding-left:12mm; margin-bottom:4.2mm; }}
li:before {{ content:counter(s); position:absolute; left:0; top:-1mm; width:8mm; height:8mm; border-radius:50%;
  background:#12314a; color:#fff; font-weight:bold; font-size:10pt; text-align:center; line-height:8mm; }}
b {{ color:#12314a; }}
.foot {{ margin-top:8mm; border-top:.4pt solid #ddd8cc; padding-top:3mm; font-size:8pt; color:#6b7a86; }}
.pb {{ page-break-before:always; }}
table {{ width:100%; border-collapse:collapse; font-size:9pt; margin:3mm 0 5mm; }}
th {{ background:#12314a; color:#fff; text-align:left; padding:2mm; }}
td {{ padding:1.8mm 2mm; border-bottom:.4pt solid #e6e1d5; }}
.two {{ display:flex; gap:6mm; }}
.box {{ flex:1; border:1px solid #ddd8cc; border-radius:3mm; padding:4mm; }}
.box h3 {{ margin:0 0 2mm; font-size:11pt; color:#12314a; }}
.box p {{ margin:0; font-size:9.5pt; color:#41525f; }}
.warn {{ background:#fdf1f1; border-left:3pt solid #9b2226; padding:3mm 4mm; font-size:9pt; }}
</style></head><body>
<div class="kick">Estudio de mercado · La Habana · 4.979 anuncios</div>
<h1>10 cambios para vender mejor<br>(sin gastar nada)</h1>
<p class="lead">Si solo vas a hacer una cosa: <b>escribe la marca en el título</b>. Es el cambio de costo cero con más efecto.</p>
<div class="rule"></div>
<ol>
<li><b>Marca en el título.</b> El 45,5% no lo hace. Quien busca esa marca no ve el anuncio.</li>
<li><b>Una cifra clave.</b> Autonomía, cc, voltaje o kilómetros. El 43,3% no tiene ningún número.</li>
<li><b>Municipio.</b> El 8,8% no dice dónde está. Sin zona no apareces en las comparaciones.</li>
<li><b>WhatsApp y horario.</b> El 59,9% ya lo usa. Responde en el horario que prometes.</li>
<li><b>Estado declarado.</b> Nueva, seminueva o usada: es la primera pregunta del comprador.</li>
<li><b>Fotos reales.</b> Del vehículo, no de catálogo.</li>
<li><b>Revisa la mediana de tu marca.</b> TOPMAQ 2.150 USD; CHALLENGER 850 USD.</li>
<li><b>Compara por zona.</b> Cerro 700 USD; Habana del Este 1.920 USD.</li>
<li><b>Publica en varias fuentes.</b> Ninguna plataforma cubre el mercado sola.</li>
<li><b>Borra duplicados y vacíos.</b> Ocupan lugar sin informar a nadie.</li>
</ol>
<div class="foot">Datos: 4.979 anuncios únicos de Revolico, iTENCEL, ElYerro y Facebook (19–24 sep 2026). Precios declarados, no avalúos.<br>
Sitio: reynaldomesab-crypto.github.io/estudio-mercado-motos-bicicletas-cuba</div>

<div class="pb"></div>
<div class="kick">Referencia rápida</div>
<h1 style="font-size:20pt">Antes y después</h1>
<div class="two">
  <div class="box"><h3>Antes</h3><p>“MOTO SE VENDE”<br><br>Sin marca, sin cifra, sin zona. No aparece en ninguna búsqueda útil.</p></div>
  <div class="box"><h3>Después</h3><p>“Moto eléctrica AVA, 100 km, seminueva, Centro Habana, WhatsApp”<br><br>Aparece por marca, autonomía, estado y zona.</p></div>
</div>
<h1 style="font-size:20pt;margin-top:8mm">Precios de referencia por tipo</h1>
<table><thead><tr><th>Tipo</th><th>Anuncios</th><th>p10</th><th>Mediana</th><th>p90</th></tr></thead><tbody>
{''.join(f'<tr><td>{t["nombre"]}</td><td>{t["n"]}</td><td>{usd(t["p10"])}</td><td><b>{usd(t["p50"])}</b></td><td>{usd(t["p90"])}</td></tr>' for t in TIPOS)}
</tbody></table>
<div class="warn"><b>Esto no es un avalúo.</b> Son precios declarados por los vendedores, no precios de venta. La comparación es de posición relativa.</div>
<h1 style="font-size:20pt;margin-top:8mm">Lo que el estudio no puede decir</h1>
<p>No observa ventas: solo anuncios. No distingue nuevo de usado. No hay fecha por anuncio. La deduplicación es por URL. Los precios son declarados.</p>
<div class="foot">Comparte este checklist con quien venda o compre. Estudio independiente, sin fines comerciales.<br>
reynaldomesab-crypto.github.io/estudio-mercado-motos-bicicletas-cuba</div>
</body></html>'''
from weasyprint import HTML as WHTML
WHTML(string=HTML_CHECK).write_pdf(OUT / 'assets' / 'checklist.pdf')

# ---------------- sitemap / robots ----------------
urls = ['', 'resumen.html', 'guia.html', 'precios.html', 'datos.html', 'metodo.html', 'prensa.html']
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
    f'  <url><loc>{SITE}{u}</loc><lastmod>2026-11-07</lastmod><priority>{"1.0" if u=="" else "0.8"}</priority></url>\n' for u in urls) + '</urlset>\n'
(OUT / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
(OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n', encoding='utf-8')
print('imágenes, PDF, sitemap y robots generados')

# .nojekyll para GitHub Pages
(OUT / ".nojekyll").write_text("", encoding="utf-8")
