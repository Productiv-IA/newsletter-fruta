# Fruta al día

Newsletter diaria sobre naranja, mandarina, kaki, frutos rojos y uva en España y Portugal.
Recoge noticias, las resume con IA (Gemini, con Groq de reserva), publica una web de archivo con buscador
y envía el resumen por correo con Brevo. Se ejecuta sola cada mañana con GitHub Actions.

Prueba local: `pip install -r requirements.txt`, copia `.env.example` a `.env` y rellénalo, y ejecuta
`python main.py --demo` (sin red), `python main.py --dry-run` (noticias reales, sin enviar)
o `python main.py --to tu@correo.com` (envía una prueba solo a ti).

Ajustes (palabras clave, búsquedas, fuentes): `config.py`.
