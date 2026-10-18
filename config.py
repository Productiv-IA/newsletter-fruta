import os, unicodedata
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Madrid")
SITE_NAME = "Fruta al día"
SITE_TAGLINE = "Cítricos, kaki, frutos rojos y uva en España y Portugal"
HOURS_BACK = 36
REGION_QUOTA = {"ES": 45, "PT": 25, "INT": 25}   # máx. noticias candidatas enviadas a la IA
CHUNK = 30          # noticias por llamada a la IA
MAX_NEWS = 30       # máx. noticias por edición

SECTION_ORDER = ["mercado", "actualidad", "innovacion", "interprofesional", "agenda"]
SECTIONS = {
    "mercado": {"label": "El pulso del mercado", "color": "#236B4A"},
    "actualidad": {"label": "Actualidad del sector", "color": "#245B8A"},
    "innovacion": {"label": "Innovación en el campo", "color": "#8A5A20"},
    "interprofesional": {"label": "La voz de la interprofesional", "color": "#7A3B72"},
    "agenda": {"label": "Agenda", "color": "#5C6A60"},
}


def env(name, default=""):
    """Lee una variable de entorno sin distinguir mayúsculas (Brevo_API_KEY = BREVO_API_KEY)."""
    for k, v in os.environ.items():
        if k.upper() == name.upper() and v.strip():
            return v.strip()
    return default


def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


CROPS = {
    "citricos": {"label": "Cítricos: naranja y mandarina", "color": "#E8890C"},
    "kaki": {"label": "Kaki", "color": "#D2491F"},
    "frutos_rojos": {"label": "Frutos rojos", "color": "#B3123F"},
    "uva": {"label": "Uva", "color": "#6A44A0"},
    "otros": {"label": "Otros", "color": "#5C6A60"},
}

# Palabras (sin acentos) para filtrar noticias y para clasificar si la IA falla
CROP_WORDS = {
    "citricos": ["naranja", "mandarina", "clementina", "citric", "citrin", "laranja", "tangerina", "citrus", "orange", "mandarin"],
    "kaki": ["kaki", "caqui", "persimon", "diospir", "persimmon"],
    "frutos_rojos": ["frutos rojos", "frutos vermelhos", "arandano", "frambuesa", "fresa", "mirtilo", "framboesa",
                     "morango", "blueberr", "raspberr", "strawberr", "berries"],
    "uva": ["uva", "grape"],
}

GN = "https://news.google.com/rss/search"
GN_LOCALES = {
    "ES": "hl=es&gl=ES&ceid=ES:es",
    "PT": "hl=pt-PT&gl=PT&ceid=PT:pt-150",
    "INT": "hl=en&gl=US&ceid=US:en",
}

# (región, búsqueda de Google Noticias). Se añade "when:2d" automáticamente.
GOOGLE_QUERIES = [
    ("ES", "naranja OR mandarina OR clementina OR cítricos"),
    ("ES", "kaki OR caqui OR persimon"),
    ("ES", '"frutos rojos" OR arándanos OR frambuesa OR fresa'),
    ("ES", '"uva de mesa" OR (uva -vino -vendimia -bodega)'),
    ("ES", "(naranja OR mandarina OR kaki OR arándanos OR fresa OR uva) (site:valenciafruits.com OR site:agroinformacion.com OR site:agrodigital.com OR site:fepex.es OR site:freshplaza.es)"),
    ("PT", "laranja OR tangerina OR citrinos"),
    ("PT", "dióspiro OR dióspiros"),
    ("PT", '"frutos vermelhos" OR mirtilo OR framboesa OR morango'),
    ("PT", '"uva de mesa" OR uvas -vinho -vindima'),
    ("INT", 'citrus exports OR "citrus market" (Spain OR Morocco OR Egypt OR "South Africa")'),
    ("INT", "blueberries OR raspberries OR strawberries market (Spain OR Morocco OR Peru OR Portugal)"),
    ("INT", '"table grapes" market OR "persimmon" market'),
    ("INT", 'citrus (tariff OR pest OR greening OR "black spot") Europe'),
    ("ES", '(naranja OR mandarina OR kaki OR caqui OR "frutos rojos" OR uva) (site:freshplaza.es OR site:freshplaza.com OR site:fruittoday.com OR site:hortiespana.com OR site:interempresas.net OR site:agroinformacion.com)'),
    ("ES", '(naranja OR mandarina OR cítricos) (site:intercitrus.org OR site:valenciafruits.com OR site:fepex.es)'),
    ("ES", '(fresa OR arándano OR frambuesa OR "frutos rojos") (site:interberry.es OR site:freshuelva.es OR site:fepex.es)'),
    ("ES", '"uva de mesa" (site:apoexpa.es OR site:fepex.es)'),
    ("ES", '(kaki OR caqui OR persimon) (site:aekaki.es OR site:fepex.es)'),
    ("ES", '(precio OR precios OR cotización) (naranja OR mandarina OR kaki OR uva OR fresa OR arándano) (site:mapa.gob.es OR site:olimerca.com)'),
    ("ES", '(jornada OR feria OR congreso OR Fruit Attraction OR Fruit Logistica) (fruta OR cítricos OR uva OR berries) (site:fepex.es OR site:freshplaza.es OR site:interempresas.net OR site:agro-alimentarias.coop)'),
    ("ES", '(riego OR plagas OR innovación OR tecnología OR sostenibilidad) (fruta OR cítricos OR uva OR berries) (site:interempresas.net OR site:phytoma.com)'),
]

# RSS directos de prensa del sector (por verificar: el primer arranque muestra cuáles funcionan)
FEEDS = [
    ("ES", "https://www.valenciafruits.com/feed/"),
    ("ES", "https://www.agroinformacion.com/feed/"),
    ("ES", "https://www.agrodigital.com/feed/"),
]

TRUSTED_DOMAINS = {
    "freshplaza.es": "actualidad", "freshplaza.com": "actualidad", "fruittoday.com": "actualidad", "fruitoday.com": "actualidad",
    "hortiespana.com": "actualidad", "interempresas.net": "innovacion", "agroinformacion.com": "actualidad",
    "intercitrus.org": "interprofesional", "valenciafruits.com": "interprofesional", "interberry.es": "interprofesional",
    "freshuelva.es": "interprofesional", "apoexpa.es": "interprofesional", "aekaki.es": "interprofesional",
    "fepex.es": "interprofesional", "agro-alimentarias.coop": "interprofesional", "mapa.gob.es": "mercado", "olimerca.com": "mercado", "phytoma.com": "innovacion",
}
