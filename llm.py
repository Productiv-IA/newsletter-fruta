import json, re, requests
from config import *
from collect import dedupe

def providers():
    gem = env("GEMINI_MODEL")
    grq = env("GROQ_MODEL")
    return [
        ("gemini", "https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY",
         [gem] if gem else ["gemini-flash-latest", "gemini-2.5-flash", "gemini-2.5-flash-lite"]),
        ("groq", "https://api.groq.com/openai/v1", "GROQ_API_KEY",
         [grq] if grq else ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "llama-3.1-8b-instant"]),
    ]


def _parse(text):
    a, b = text.find("{"), text.rfind("}")
    return json.loads(text[a:b + 1])


def chat_json(messages):
    """Prueba cada proveedor y modelo en orden hasta obtener un JSON válido."""
    errors = []
    for name, base, keyvar, models in providers():
        key = env(keyvar)
        if not key:
            errors.append(f"{name}: sin clave")
            continue
        for model in models:
            try:
                r = requests.post(f"{base}/chat/completions", headers={"Authorization": f"Bearer {key}"},
                                  json={"model": model, "messages": messages, "temperature": 0.2}, timeout=120)
                if r.status_code != 200:
                    errors.append(f"{name}/{model}: HTTP {r.status_code} {r.text[:120]}")
                    if r.status_code in (401, 403):
                        break
                    continue
                return _parse(r.json()["choices"][0]["message"]["content"]), f"{name}/{model}"
            except Exception as ex:
                errors.append(f"{name}/{model}: {str(ex)[:100]}")
    raise RuntimeError(" | ".join(errors))


SYSTEM = """Eres el editor de una newsletter diaria del sector hortofrutícola. Recibirás noticias candidatas (JSON) sobre naranja, mandarina, kaki, frutos rojos (fresa, arándano, frambuesa) y uva de mesa en España y Portugal. Las fuentes sectoriales y oficiales tienen prioridad editorial.
Tu trabajo:
1. Quédate solo con noticias de interés profesional: producción, campañas, precios, mercados, exportación, plagas, clima, normativa, comercio. Descarta recetas, salud/nutrición, ocio, vino y cualquier cosa fuera del sector.
2. Si varias noticias cuentan lo mismo, conserva solo la mejor.
3. Noticias internacionales: inclúyelas únicamente si son muy importantes o afectan directamente a España o Portugal.
4. Asigna una sección: mercado para precios y tendencias; actualidad para campañas, comercio, clima, regulación y noticias empresariales; innovacion para tecnología, riego, manejo y sanidad vegetal; interprofesional para comunicados y datos de Intercitrus, Interberry, Freshuelva, APOEXPA, AEKAKI, FEPEX u otras asociaciones; agenda para ferias, jornadas y congresos.
5. Para cada noticia elegida devuelve: id (el recibido), cultivo (citricos, kaki, frutos_rojos, uva u otros), seccion (mercado, actualidad, innovacion, interprofesional o agenda), pais (España, Portugal o Internacional, según de qué país trata la noticia), importancia (1 a 5), titular (en español, claro y breve; tradúcelo si viene en portugués o inglés) y resumen (1 o 2 frases, máximo 45 palabras, en español).
REGLA ESTRICTA: el resumen debe basarse SOLO en el título y el extracto recibidos. No inventes cifras, nombres ni hechos. Si solo hay título, reformúlalo sin añadir información.
Responde ÚNICAMENTE con un objeto JSON: {"noticias":[{"id":0,"cultivo":"citricos","seccion":"actualidad","pais":"España","importancia":3,"titular":"...","resumen":"..."}]}"""


def summarize(items):
    news, used = [], set()
    for i in range(0, len(items), CHUNK):
        chunk = items[i:i + CHUNK]
        payload = [{"id": n, "titulo": it["title"], "fuente": it["source"], "region": it["region"],
                    "extracto": it["snippet"], "seccion_sugerida": it.get("section_hint", "actualidad")} for n, it in enumerate(chunk)]
        data, who = chat_json([{"role": "system", "content": SYSTEM},
                               {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}])
        used.add(who)
        for n in data.get("noticias", []):
            try:
                it = chunk[int(n["id"])]
            except Exception:
                continue
            pais = n.get("pais") if n.get("pais") in ("España", "Portugal", "Internacional") else \
                {"ES": "España", "PT": "Portugal"}.get(it["region"], "Internacional")
            try:
                imp = max(1, min(5, int(n.get("importancia", 3))))
            except Exception:
                imp = 3
            section = n.get("seccion") if n.get("seccion") in SECTIONS else it.get("section_hint", "actualidad")
            news.append({"cultivo": n.get("cultivo") if n.get("cultivo") in CROPS else "otros", "seccion": section, "pais": pais,
                         "importancia": imp, "titular": str(n.get("titular") or it["title"])[:200],
                         "resumen": str(n.get("resumen") or "")[:400], "fuente": it["source"],
                         "link": it["link"], "publicado": it["published"]})
    news = dedupe(news, "titular")
    news.sort(key=lambda x: x["publicado"] or "", reverse=True)
    news.sort(key=lambda x: -x["importancia"])
    return news[:MAX_NEWS], ", ".join(sorted(used))


def fallback(items):
    """Sin IA: clasifica por palabras clave y usa los titulares tal cual."""
    news = []
    for it in items[:MAX_NEWS]:
        t = norm(it["title"] + " " + it["snippet"])
        crop = next((c for c, ws in CROP_WORDS.items() if any(w in t for w in ws)), "otros")
        news.append({"cultivo": crop, "seccion": it.get("section_hint", "actualidad"), "pais": {"ES": "España", "PT": "Portugal"}.get(it["region"], "Internacional"),
                     "importancia": 3, "titular": it["title"], "resumen": it["snippet"][:250], "fuente": it["source"],
                     "link": it["link"], "publicado": it["published"]})
    return news
