import asyncio
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from flask import Flask, request
import pytz
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "9084832898:AAGQCqGvBrtNRy9kQ34QnLlrSYUUEBsG7x8"
bogota_tz = pytz.timezone("America/Bogota")

# 52 Filtros Geográficos y Nodos Clave del Valle de Aburrá
FILTROS_VALLE_52 = [
    "Medellín",
    "Envigado",
    "Itagüí",
    "Bello",
    "Sabaneta",
    "La Estrella",
    "Caldas",
    "Copacabana",
    "Girardota",
    "Barbosa",
    "Autopista Sur",
    "Autopista Norte",
    "Avenida Regional",
    "Las Palmas",
    "San Juan",
    "Avenida Colombia",
    "La 80",
    "Avenida El Poblado",
    "Guayabal",
    "Ferrocarril",
    "Avenida Nutibara",
    "Carrera 65",
    "Poblado",
    "Laureles",
    "Belén",
    "Robledo",
    "Manrique",
    "Aranjuez",
    "Buenos Aires",
    "San Javier",
    "Doce de Octubre",
    "Castilla",
    "Villa Hermosa",
    "La Candelaria",
    "Centro",
    "Estadio",
    "San Antonio de Prado",
    "Santa Elena",
    "San Cristóbal",
    "Soterrado de la Regional",
    "Punto Cero",
    "Glorieta San Diego",
    "Glorieta Exposición",
    "Puente Horacio Toro",
    "Puente Madre Laura",
]

CUENTAS_X_OFICIALES = [
    "sttmed",
    "siatamedellin",
    "AlcaldiaMed",
    "PoliciaMedellin",
    "Devimed",
    "metrodemedellin",
    "DAGRDMedellin",
    "TransitoEnvigado",
    "MovilidadItagui",
    "TransitoBello",
]

FEEDS_RSS_LOCALES = [
    "https://www.minuto30.com/feed/",
    "https://alertapaisa.com/rss",
]

NOVEDADES_CACHE = []


def esta_en_ventana_operativa():
  """Valida si la hora actual se encuentra dentro de las ventanas de trabajo

  del conductor.
  """
  ahora = datetime.now(bogota_tz)
  dia_semana = ahora.weekday()  # 0: Lun, 1: Mar, ..., 4: Vie, 5: Sáb, 6: Dom
  hora = ahora.hour
  minuto = ahora.minute
  hora_decimal = hora + minuto / 60.0

  # Viernes (4) y Sábado (5): 7:00 p.m. (19:00) a 5:00 a.m. del día siguiente
  if dia_semana == 4 or dia_semana == 5:
    if hora_decimal >= 19.0 or hora_decimal < 5.0:
      return True
  # Domingo (6): 5:00 p.m. (17:00) a 12:00 a.m. (24:00)
  elif dia_semana == 6:
    if 17.0 <= hora_decimal <= 24.0:
      return True
  # Lunes a Jueves (0 a 3): 1:00 p.m. (13:00) a 10:00 p.m. (22:00)
  elif 0 <= dia_semana <= 3:
    if 13.0 <= hora_decimal <= 22.0:
      return True

  return False


async def extraer_nitter(session, cuenta):
  url = f"https://nitter.privacydev.net/{cuenta}"
  hallazgos = []
  try:
    async with session.get(url, timeout=3) as resp:
      if resp.status == 200:
        html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        for tweet in soup.select(".tweet-content")[:2]:
          texto = tweet.get_text(strip=True)
          if any(f.lower() in texto.lower() for f in FILTROS_VALLE_52):
            hallazgos.append(f"📱 **@{cuenta}**: {texto}")
  except Exception:
    pass
  return hallazgos


async def extraer_rss(session, url_rss):
  hallazgos = []
  try:
    async with session.get(url_rss, timeout=3) as resp:
      if resp.status == 200:
        xml = await resp.text()
        soup = BeautifulSoup(xml, "xml")
        for item in soup.find_all("item")[:3]:
          titulo = (
              item.find("title").get_text(strip=True)
              if item.find("title")
              else ""
          )
          if any(f.lower() in titulo.lower() for f in FILTROS_VALLE_52):
            hallazgos.append(f"📰 **Medios**: {titulo}")
  except Exception:
    pass
  return hallazgos


async def extraer_siata(session):
  hallazgos = []
  try:
    async with session.get(
        "https://siata.gov.co/api/v1/alertas", timeout=3
    ) as resp:
      if resp.status == 200:
        data = await resp.json()
        for item in data:
          if item.get("nivel") in ["Rojo", "Naranja"]:
            hallazgos.append(
                f"🌧️ **SIATA ({item.get('municipio', 'Valle')})**: "
                f"{item.get('descripcion')}"
            )
  except Exception:
    pass
  return hallazgos


async def ciclo_barrido_total():
  async with aiohttp.ClientSession() as session:
    tareas = [extraer_nitter(session, c) for c in CUENTAS_X_OFICIALES]
    for rss in FEEDS_RSS_LOCALES:
      tareas.append(extraer_rss(session, rss))
    tareas.append(extraer_siata(session))

    resultados = await asyncio.gather(*tareas)
    consolidados = []
    for grupo in resultados:
      for item in grupo:
        if item not in consolidados:
          consolidados.append(item)
    return consolidados


def tarea_segundo_plano():
  """Ejecutado por los crons independientes en segundo plano."""
  global NOVEDADES_CACHE
  if not esta_en_ventana_operativa():
    return
  try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    NOVEDADES_CACHE = loop.run_until_complete(ciclo_barrido_total())
  except Exception:
    pass


# Configurar crons independientes en segundo plano (minutos 15 y 45 de cada hora)
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(
    tarea_segundo_plano, "cron", minute="15,45", id="cron_independientes"
)
scheduler.start()

# Ejecutar un barrido inicial inmediato al arrancar la app si estamos en horario
if esta_en_ventana_operativa():
  try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    NOVEDADES_CACHE = loop.run_until_complete(ciclo_barrido_total())
  except Exception:
    pass


@app.route("/webhook", methods=["POST"])
def webhook():
  data = request.get_json()
  if not data or "message" not in data:
    return "OK", 200

  chat_id = data["message"]["chat"]["id"]
  texto = data["message"].get("text", "").strip()
  hora_legal_str = datetime.now(bogota_tz).strftime("%I:%M %p")
  url_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

  if texto.lower() in ["/start", "hola"]:
    respuesta = (
        f"¡Hola, Raúl! KITT-BOT en línea.\n📊 Fuentes: 82\n📍 Filtros Valle:"
        " 52\n🕒 Crons y Comando P independientes listos."
    )
    requests.post(url_api, json={"chat_id": chat_id, "text": respuesta})

  elif texto.upper() == "P" or texto.lower() == "/p":
    # El comando P consulta de forma inmediata la caché existente por demanda
    if not esta_en_ventana_operativa():
      respuesta = (
          f"🕒 **REPORTE TOTAL UNIFICADO VALLE DE ABURRÁ**\n🕒"
          f" {hora_legal_str}\n\nFuera de ventana operativa establecida."
      )
    elif not NOVEDADES_CACHE:
      respuesta = (
          f"🕒 **REPORTE TOTAL UNIFICADO VALLE DE ABURRÁ**\n🕒"
          f" {hora_legal_str}\n\nSIN NOVEDADES"
      )
    else:
      cuerpo_reporte = "\n".join(NOVEDADES_CACHE)
      respuesta = (
          f"🕒 **REPORTE TOTAL UNIFICADO VALLE DE ABURRÁ**\n🕒"
          f" {hora_legal_str}\n\n{cuerpo_reporte}"
      )

    requests.post(
        url_api,
        json={"chat_id": chat_id, "text": respuesta, "parse_mode": "Markdown"},
    )

  return "OK", 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)

  
