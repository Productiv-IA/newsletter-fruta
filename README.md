# Fruta al día

Newsletter diaria sobre naranja, mandarina, kaki, frutos rojos y uva en España y Portugal.
Recoge noticias, las resume con IA (Gemini, con Groq de reserva), publica una web de archivo con buscador
y envía el resumen por correo con Brevo. Se ejecuta sola cada mañana con GitHub Actions.

Prueba local: `pip install -r requirements.txt`, copia `.env.example` a `.env` y rellénalo, y ejecuta
`python main.py --demo` (sin red), `python main.py --dry-run` (noticias reales, sin enviar)
o `python main.py --to tu@correo.com` (envía una prueba solo a ti).

Ajustes (palabras clave, búsquedas, fuentes): `config.py`.

## Enfoque editorial

La edición se organiza en cinco secciones fijas:

1. **El pulso del mercado**: precios, cotizaciones y tendencias de MAPA y Olimerca.
2. **Actualidad del sector**: campañas, comercio, clima, logística y regulación.
3. **Innovación en el campo**: riego, manejo, sanidad vegetal, tecnología y sostenibilidad.
4. **La voz de la interprofesional**: comunicados y datos de Intercitrus, Interberry, Freshuelva, APOEXPA, AEKAKI, FEPEX y Cooperativas Agro-alimentarias.
5. **Agenda**: ferias, jornadas y congresos relevantes.

Las búsquedas priorizan FreshPlaza, Fruit Today, Hortiespaña, Interempresas, Agroinformación y Valencia Fruits, junto con las fuentes específicas de cada cultivo. La clasificación combina el dominio de origen, la fuente identificada y la revisión de la IA; cuando una fuente prioritaria no publica novedades recientes, se mantiene la búsqueda general del cultivo para evitar dejar la edición vacía.

