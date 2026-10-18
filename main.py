import argparse, json, pathlib, datetime as dt
from dotenv import load_dotenv
load_dotenv()
import config, collect, llm, render, mailer
from config import env

ROOT = pathlib.Path(__file__).parent

DEMO = [
    ("citricos", "España", 5, "La campaña de mandarina arranca con precios firmes en origen", "Los productores valoran un inicio de campaña con buena demanda y precios por encima del año pasado."),
    ("kaki", "España", 4, "El kaki Rojo Brillante afronta la recta final de recolección", "Las cooperativas prevén una cosecha estable y destacan la calidad del fruto."),
    ("frutos_rojos", "España", 4, "Huelva prepara la nueva campaña de arándanos con más superficie", "El sector espera un aumento de la superficie y refuerza la apuesta por nuevas variedades."),
    ("uva", "España", 3, "La uva de mesa sin semillas gana peso en las exportaciones", "Las empresas del sector destacan el crecimiento de la demanda europea."),
    ("citricos", "Portugal", 3, "Algarve: produtores de laranja antecipam boa colheita", "Los productores del Algarve esperan una cosecha de naranja de buena calidad."),
    ("citricos", "Internacional", 4, "Sudáfrica aumenta sus envíos de cítricos a Europa", "Las exportaciones sudafricanas de cítricos crecen y reabren el debate sobre la competencia en la UE."),
]


def demo_edition():
    today = dt.datetime.now(config.TZ).date().isoformat()
    items = [{"cultivo": c, "pais": p, "importancia": n, "titular": t, "resumen": r, "fuente": "Fuente de ejemplo",
              "link": "https://example.com/noticia", "publicado": None} for c, p, n, t, r in DEMO]
    return {"date": today, "items": items, "ia": True, "email_sent": False, "demo": True}


def load_all(d):
    return sorted((json.loads(p.read_text("utf-8")) for p in d.glob("20*.json")), key=lambda x: x["date"], reverse=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="edición de ejemplo, sin red ni IA")
    ap.add_argument("--dry-run", action="store_true", help="no envía correos")
    ap.add_argument("--scheduled", action="store_true", help="modo automático (comprueba hora y envío previo)")
    ap.add_argument("--refresh", action="store_true", help="vuelve a recoger noticias aunque ya exista la edición")
    ap.add_argument("--to", help="envía solo a este correo (prueba; no marca como enviada)")
    a = ap.parse_args()

    data_dir, site_dir = (ROOT / "demo_out" / "data", ROOT / "demo_out" / "docs") if a.demo else (ROOT / "data", ROOT / "docs")
    data_dir.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(config.TZ)
    today = now.date().isoformat()
    path = data_dir / f"{today}.json"
    site_url = env("SITE_URL")
    if site_url and not site_url.endswith("/"):
        site_url += "/"

    if a.scheduled and now.hour < 7:
        print("Aún no son las 7:00 en Madrid; se omite (el segundo disparo lo hará).")
        return
    ed = json.loads(path.read_text("utf-8")) if path.exists() and not a.refresh and not a.demo else None
    if a.scheduled and ed and ed.get("email_sent"):
        print("La edición de hoy ya se envió.")
        return

    if ed is None:
        if a.demo:
            ed = demo_edition()
        else:
            items, report = collect.collect()
            for name, n, err in report:
                print(f"  [{'ERROR' if err else 'ok'}] {name}: {n} noticias {err}")
            print(f"Candidatas tras filtrar y deduplicar: {len(items)}")
            try:
                news, who = llm.summarize(items) if items else ([], "")
                ia = True
                print(f"IA usada: {who or '-'}")
            except Exception as ex:
                print(f"AVISO: la IA falló ({ex}). Se usa el modo sin IA.")
                news, ia = llm.fallback(items), False
            ed = {"date": today, "items": news, "ia": ia, "email_sent": False}
        path.write_text(json.dumps(ed, ensure_ascii=False, indent=1), "utf-8")

    render.build_site(load_all(data_dir), site_dir)
    print(f"Web generada en {site_dir} ({len(ed['items'])} noticias hoy)")

    if a.dry_run or (a.demo and not a.to):
        print("Sin envío de correo (dry-run/demo).")
        return
    if a.to:
        ok, fail = mailer.send(ed, [a.to], site_url)
        print(f"Prueba enviada a {a.to}: {ok} ok, {fail}")
        return
    if ed.get("email_sent"):
        print("Ya enviada; nada más que hacer.")
        return
    if not ed["items"]:
        print("Sin noticias hoy: no se envía correo.")
        return
    to = mailer.recipients()
    if not to:
        print("AVISO: no hay destinatarios (revisa BREVO_LIST_ID o EXTRA_RECIPIENTS).")
        return
    ok, fail = mailer.send(ed, to, site_url)
    print(f"Correos enviados: {ok}. Fallos: {fail}")
    ed["email_sent"] = True
    path.write_text(json.dumps(ed, ensure_ascii=False, indent=1), "utf-8")


if __name__ == "__main__":
    main()
