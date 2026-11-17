import re, html, difflib, datetime as dt
from urllib.parse import quote_plus, urlparse
import feedparser, requests
from config import *

UA = {"User-Agent": "Mozilla/5.0 (compatible; FrutaAlDia/1.0)"}
KW = re.compile(r"\b(?:" + "|".join(re.escape(norm(w)) for ws in CROP_WORDS.values() for w in ws) + ")")

# Una coincidencia aislada de una fruta también puede ser un color, una
# prenda o una alerta meteorológica. Exigimos contexto profesional.
SECTOR_CONTEXT = (
    "agricult agricultur cultivo cultivos productor productores cosecha campaña "
    "mercado mercados precio precios export exportacion import importacion "
    "comercial comercializacion venta distribucion produccion empresa empresas "
    "compania sector hortofrut fruta frutas citrico citricos campo agricultor "
    "cooperativa cooperativas finca plantacion recoleccion variedad variedades "
    "calibre toneladas hectarea hectareas plaga plagas enfermedad enfermedades "
    "riego fertilizante fitosanitario vivero invernadero arancel aranceles "
    "aduana logistica transporte normativa regulacion origen destino supermercado "
    "cadena alimentaria innovacion tecnologia sostenibilidad feria congreso jornada"
).split()
OFF_TOPIC = (
    "alerta naranja", "nivel naranja", "aviso naranja", "vestido", "vestidos",
    "camiseta", "camisetas", "ropa", "moda", "pasarela", "maquillaje",
    "perfume", "color", "colores", "decoracion", "receta", "recetas",
    "cocina", "gastronomia", "postre", "vino", "bodega", "futbol",
    "videojuego", "pelicula", "serie", "musica",
)


def source_section(link="", source=""):
    host = urlparse(link or "").netloc.lower().split(":")[0]
    for domain, section in TRUSTED_DOMAINS.items():
        if host == domain or host.endswith("." + domain):
            return section
    text = norm(source)
    if any(x in text for x in ("mapa", "olimerca", "precio")):
        return "mercado"
    if any(x in text for x in ("interempresas", "phytoma")):
        return "innovacion"
    if any(x in text for x in ("intercitrus", "interberry", "freshuelva", "apoexpa", "aekaki", "fepex")):
        return "interprofesional"
    return "actualidad"


def trusted_source(link="", source=""):
    host = urlparse(link or "").netloc.lower().split(":")[0]
    if any(host == d or host.endswith("." + d) for d in TRUSTED_DOMAINS):
        return True
    source_text = norm(source)
    return any(d in source_text or d.split(".")[0] in source_text for d in TRUSTED_DOMAINS)


def is_relevant_item(item):
    """Descarta coincidencias de fruta sin relación hortofrutícola."""
    title = norm(item.get("title", ""))
    snippet = norm(item.get("snippet", ""))
    text = f"{title} {snippet}"
    if not KW.search(text):
        return False
    if any(term in text for term in OFF_TOPIC):
        explicit_agriculture = any(term in text for term in ("cultiv", "agricult", "cosecha", "campana", "productor", "fruta", "hortofrut", "citric"))
        if not explicit_agriculture:
            return False
    if trusted_source(item.get("link", ""), item.get("source", "")):
        return True
    return any(term in text for term in SECTOR_CONTEXT)


def _clean(s):
    s = re.sub(r"<[^>]+>", " ", html.unescape(s or ""))
    return re.sub(r"\s+", " ", s).strip()


def to_item(e, region):
    title = _clean(e.get("title"))
    source = _clean((e.get("source") or {}).get("title"))
    if source and title.endswith(" - " + source):
        title = title[: -len(source) - 3]
    elif not source and " - " in title:
        title, source = title.rsplit(" - ", 1)
    snippet = _clean(e.get("summary"))[:400]
    if norm(snippet)[:40] == norm(title)[:40]:
        snippet = ""
    ts = e.get("published_parsed") or e.get("updated_parsed")
    pub = dt.datetime(*ts[:6], tzinfo=dt.timezone.utc) if ts else None
    link = e.get("link", "")
    return {"title": title, "source": source, "link": link, "snippet": snippet,
            "published": pub.isoformat() if pub else None, "region": region,
            "section_hint": source_section(link, source)}


def dedupe(items, key="title"):
    out = []
    for it in items:
        t = norm(it[key])
        if any((it.get("link") and it.get("link") == o.get("link"))
               or difflib.SequenceMatcher(None, t, norm(o[key])).ratio() > 0.8 for o in out):
            continue
        out.append(it)
    return out


def _fetch(url):
    r = requests.get(url, headers=UA, timeout=25)
    r.raise_for_status()
    return feedparser.parse(r.content)


def sources():
    for region, q in GOOGLE_QUERIES:
        yield f"Google Noticias {region}: {q[:45]}", f"{GN}?q={quote_plus(q + ' when:2d')}&{GN_LOCALES[region]}", region, ""
    for region, url in FEEDS:
        yield url, url, region, url.split("/")[2]


def collect(hours=HOURS_BACK):
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    items, report = [], []
    for name, url, region, default_src in sources():
        try:
            n = 0
            for e in _fetch(url).entries:
                it = to_item(e, region)
                it["source"] = it["source"] or default_src
                if it["published"] and dt.datetime.fromisoformat(it["published"]) < cutoff:
                    continue
                if not is_relevant_item(it):
                    continue
                items.append(it)
                n += 1
            report.append((name, n, ""))
        except Exception as ex:
            report.append((name, 0, str(ex)[:120]))
    items.sort(key=lambda i: i["published"] or "", reverse=True)
    items = dedupe(items)
    picked = []
    for region, quota in REGION_QUOTA.items():
        picked += [i for i in items if i["region"] == region][:quota]
    return picked, report
