import time, requests
from config import *
from render import email_html, email_text, fecha

API = "https://api.brevo.com/v3"


def _h():
    return {"api-key": env("BREVO_API_KEY"), "accept": "application/json", "content-type": "application/json"}


def recipients():
    emails, lid = set(), env("BREVO_LIST_ID")
    if lid:
        off = 0
        while True:
            r = requests.get(f"{API}/contacts/lists/{lid}/contacts", headers=_h(), params={"limit": 500, "offset": off}, timeout=30)
            r.raise_for_status()
            cs = r.json().get("contacts", [])
            emails |= {c["email"] for c in cs if c.get("email") and not c.get("emailBlacklisted")}
            if len(cs) < 500:
                break
            off += 500
    emails |= {x.strip() for x in env("EXTRA_RECIPIENTS").split(",") if x.strip()}
    return sorted(emails)


def send(ed, to_list, site_url):
    sender = {"name": env("SENDER_NAME", SITE_NAME), "email": env("SENDER_EMAIL")}
    if not sender["email"]:
        raise RuntimeError("Falta SENDER_EMAIL")
    top = ed["items"][0]["titular"] if ed["items"] else "resumen del día"
    subject = f"{SITE_NAME}: {top}"[:110]
    html_body, text_body = email_html(ed, site_url), email_text(ed, site_url)
    ok, fail = 0, []
    for addr in to_list:
        r = requests.post(f"{API}/smtp/email", headers=_h(), timeout=30, json={
            "sender": sender, "to": [{"email": addr}], "subject": subject,
            "htmlContent": html_body, "textContent": text_body, "tags": ["newsletter-fruta"]})
        if r.status_code in (200, 201):
            ok += 1
        else:
            fail.append(f"{addr}: HTTP {r.status_code} {r.text[:150]}")
        time.sleep(0.2)
    if not ok and fail:
        raise RuntimeError("; ".join(fail[:3]))
    return ok, fail
