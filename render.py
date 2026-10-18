import html, json, datetime as dt, pathlib
from config import *

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]


def e(s):
    return html.escape(str(s or ""), quote=True)


def url(u):
    return u if str(u).startswith(("http://", "https://")) else "#"


def fecha(d):
    x = dt.date.fromisoformat(d)
    return f"{DIAS[x.weekday()]} {x.day} de {MESES[x.month - 1]} de {x.year}"


def groups(items):
    return [(k, v, [i for i in items if i["cultivo"] == k]) for k, v in CROPS.items() if any(i["cultivo"] == k for i in items)]


def section_groups(items):
    return [(k, SECTIONS[k], [i for i in items if i.get("seccion", "actualidad") == k])
            for k in SECTION_ORDER if any(i.get("seccion", "actualidad") == k for i in items)]


CSS = """:root{--paper:#F5F7F0;--ink:#18271D;--muted:#5C6A60;--line:#D6DCCF;--link:#1D5B3A}
@media (prefers-color-scheme:dark){:root{--paper:#111915;--ink:#E7EEE5;--muted:#98A89C;--line:#27342B;--link:#8FD3A8}}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:18px/1.6 "Source Serif 4",Georgia,serif}
.wrap{max-width:46rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}a{color:var(--link)}
a:focus-visible,input:focus-visible{outline:3px solid var(--link);outline-offset:2px}
h1{font-size:clamp(2.1rem,6vw,3.3rem);line-height:1.05;margin:.3rem 0 .4rem;letter-spacing:-.02em}
.sub{color:var(--muted);margin:0 0 1.6rem}.back{font-size:.95rem}
h2{font-size:1.25rem;margin:2.4rem 0 .6rem;display:flex;align-items:center;gap:.6rem}
.dot{width:.8rem;height:.8rem;border-radius:50%;background:var(--c);flex:none}
.n{border-left:4px solid var(--c);padding:.1rem 0 .1rem 1rem;margin:1.2rem 0}
.n h3{font-size:1.1rem;line-height:1.3;margin:0 0 .25rem}.n p{margin:.2rem 0}.m{color:var(--muted);font-size:.9rem}
input[type=search]{width:100%;font:inherit;padding:.7rem .9rem;border:1px solid var(--line);border-radius:6px;background:transparent;color:inherit}
.day{border-top:1px solid var(--line);padding:1rem 0}.day h2{margin:.2rem 0}.day ul{margin:.3rem 0 0;padding-left:1.1rem}
.note{border:1px solid var(--line);padding:.6rem .9rem;border-radius:6px;color:var(--muted);font-size:.9rem}"""

PAGE = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,700&display=swap" rel="stylesheet">
<style>__CSS__</style></head><body><div class="wrap">__BODY__</div></body></html>"""


def page(title, body):
    return PAGE.replace("__TITLE__", e(title)).replace("__CSS__", CSS).replace("__BODY__", body)


def item_html(i, show_date=False):
    meta = f'{e(i["fuente"])}, {e(i["pais"])}'
    return (f'<article class="n" style="--c:{CROPS[i["cultivo"]]["color"]}"><h3><a href="{e(url(i["link"]))}" '
            f'rel="noopener noreferrer">{e(i["titular"])}</a></h3>'
            + (f'<p>{e(i["resumen"])}</p>' if i.get("resumen") else "") + f'<p class="m">{meta}</p></article>')


def day_page(ed):
    body = f'<a class="back" href="index.html">Todas las ediciones</a><h1>{e(SITE_NAME)}</h1><p class="sub">{e(fecha(ed["date"]))}</p>'
    if ed.get("demo"):
        body += '<p class="note">Edición de demostración con noticias ficticias.</p>'
    if not ed["items"]:
        body += "<p>Hoy no hay noticias relevantes.</p>"
    for sk, sv, section_items in section_groups(ed["items"]):
        body += f'<section><h2><span class="dot" style="--c:{sv["color"]}"></span>{e(sv["label"])}</h2>'
        for k, v, items in groups(section_items):
            body += f'<h3 style="color:{v["color"]};margin:1.2rem 0 .3rem">{e(v["label"])}</h3>'
            body += "".join(item_html(i) for i in items)
        body += "</section>"
    if not ed.get("ia", True):
        body += '<p class="note">Edición generada sin resumen de IA: se muestran los titulares originales.</p>'
    return page(f'{SITE_NAME}, {fecha(ed["date"])}', body)


JS = """const q=document.getElementById('q'),box=document.getElementById('res'),days=document.getElementById('days');let data=null;
const n=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
q.addEventListener('input',async()=>{const t=n(q.value.trim()).split(/\\s+/).filter(Boolean);
if(!t.length){box.hidden=true;days.hidden=false;return}
if(!data){data=await (await fetch('search.json')).json()}
const r=data.filter(x=>{const h=n(x.t+' '+x.r+' '+x.f);return t.every(w=>h.includes(w))}).slice(0,60);
days.hidden=true;box.hidden=false;
box.innerHTML=r.length?r.map(x=>`<article class="n" style="--c:${esc(x.c)}"><h3><a href="${esc(x.l)}" rel="noopener noreferrer">${esc(x.t)}</a></h3><p>${esc(x.r)}</p><p class="m"><a href="${esc(x.d)}.html">${esc(x.d)}</a>, ${esc(x.f)}</p></article>`).join(''):'<p>No hay resultados.</p>'});"""


def index_page(eds):
    body = (f'<h1>{e(SITE_NAME)}</h1><p class="sub">{e(SITE_TAGLINE)}</p>'
            '<input id="q" type="search" placeholder="Buscar en todas las ediciones" aria-label="Buscar noticias">'
            '<div id="res" hidden></div><div id="days">')
    for ed in eds:
        top = ed["items"][:3]
        body += (f'<div class="day"><h2><a href="{e(ed["date"])}.html">{e(fecha(ed["date"]))}</a></h2>'
                 f'<p class="m">{len(ed["items"])} noticias</p><ul>'
                 + "".join(f'<li>{e(i["titular"])}</li>' for i in top) + "</ul></div>")
    body += f"</div><script>{JS}</script>"
    return page(SITE_NAME, body)


def build_site(eds, out):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for ed in eds:
        (out / f'{ed["date"]}.html').write_text(day_page(ed), "utf-8")
    (out / "index.html").write_text(index_page(eds), "utf-8")
    idx = [{"d": ed["date"], "t": i["titular"], "r": i["resumen"], "f": i["fuente"], "l": url(i["link"]),
            "c": CROPS[i["cultivo"]]["color"]} for ed in eds for i in ed["items"]]
    (out / "search.json").write_text(json.dumps(idx, ensure_ascii=False), "utf-8")
    (out / ".nojekyll").write_text("", "utf-8")


def email_html(ed, site_url):
    ink, muted = "#18271D", "#5C6A60"
    top = ed["items"][:5]
    def row(i, big=False):
        c = CROPS[i["cultivo"]]["color"]
        return (f'<tr><td style="border-left:4px solid {c};padding:2px 0 2px 12px;font-family:Georgia,serif">'
                f'<a href="{e(url(i["link"]))}" style="color:{ink};font-size:{18 if big else 16}px;font-weight:bold;text-decoration:none">{e(i["titular"])}</a>'
                + (f'<div style="color:{ink};font-size:15px;line-height:1.5;margin-top:4px">{e(i["resumen"])}</div>' if i.get("resumen") else "")
                + f'<div style="color:{muted};font-size:13px;margin-top:4px">{e(i["fuente"])}, {e(i["pais"])}</div></td></tr>'
                '<tr><td style="height:16px"></td></tr>')
    h = (f'<div style="background:#F5F7F0;padding:24px 0"><table role="presentation" align="center" width="600" cellpadding="0" cellspacing="0" '
         f'style="max-width:100%;background:#FFFFFF;padding:28px;font-family:Georgia,serif;color:{ink}"><tr><td>'
         f'<div style="font-size:30px;font-weight:bold">{e(SITE_NAME)}</div><div style="color:{muted};font-size:14px;margin:4px 0 20px">{e(fecha(ed["date"]))}</div>'
         '</td></tr>')
    if not ed.get("ia", True):
        h += f'<tr><td style="color:{muted};font-size:13px;padding-bottom:12px">Edición sin resumen de IA: titulares originales.</td></tr>'
    h += f'<tr><td style="font-size:18px;font-weight:bold;padding-bottom:10px">Lo más importante</td></tr>' + "".join(row(i, True) for i in top)
    rest = [i for i in ed["items"] if i not in top]
    for sk, sv, section_items in section_groups(rest):
        h += f'<tr><td style="font-size:17px;font-weight:bold;color:{sv["color"]};padding:12px 0 10px">{e(sv["label"])}</td></tr>'
        h += "".join(row(i) for i in section_items)
    if site_url:
        h += f'<tr><td style="padding-top:8px;font-size:15px"><a href="{e(url(site_url))}{e(ed["date"])}.html" style="color:#1D5B3A">Ver la edición completa y el archivo</a></td></tr>'
    h += f'<tr><td style="color:{muted};font-size:12px;padding-top:20px">Si no quieres recibir más correos, responde a este mensaje indicándolo.</td></tr></table></div>'
    return h


def email_text(ed, site_url):
    t = f'{SITE_NAME}, {fecha(ed["date"])}\n\n'
    for k, v, items in groups(ed["items"]):
        t += f'{v["label"]}\n' + "".join(f'- {i["titular"]} ({i["fuente"]})\n  {i["link"]}\n' for i in items) + "\n"
    return t + (f"Edición completa: {site_url}{ed['date']}.html\n" if site_url else "")
