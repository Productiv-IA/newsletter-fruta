import re, html, difflib, datetime as dt
from urllib.parse import quote_plus
import feedparser, requests
from config import *

UA = {"User-Agent": "Mozilla/5.0 (compatible; FrutaAlDia/1.0)"}
KW = re.compile(r"\b(?:" + "|".join(re.escape(norm(w)) for ws in CROP_WORDS.values() for w in ws) + ")")


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
    return {"title": title, "source": source, "link": e.get("link", ""), "snippet": snippet,
            "published": pub.isoformat() if pub else None, "region": region}


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
                if not KW.search(norm(it["title"] + " " + it["snippet"])):
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
