import os, unicodedata
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Madrid")
SITE_NAME = "Fruta al día"
SITE_TAGLINE = "Cítricos, kaki, frutos rojos y uva en España y Portugal"
HOURS_BACK = 36
REGION_QUOTA = {"ES": 45, "PT": 25, "INT": 25}   # máx. noticias candidatas enviadas a la IA
CHUNK = 30          # noticias por llamada a la IA
MAX_NEWS = 30       # máx. noticias por edición


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
]

# RSS directos de prensa del sector (por verificar: el primer arranque muestra cuáles funcionan)
FEEDS = [
    ("ES", "https://www.valenciafruits.com/feed/"),
    ("ES", "https://www.agroinformacion.com/feed/"),
    ("ES", "https://www.agrodigital.com/feed/"),
]
