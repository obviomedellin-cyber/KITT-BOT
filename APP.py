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
  """Valida si la hora actual está dentro del turno del conductor

  (exclusivo para los crons automáticos).
  """
  ahora = datetime.now(bogota_tz)
  dia_semana = ahora.weekday()
  hora = ahora.hour
  minuto = ahora.minute
  hora_decimal = hora + minuto / 60.0

  if dia_semana == 4 or dia_semana == 5:  # Vie / Sáb
    if hora_decimal >= 19.0 or hora_decimal < 5.0:
      return True
  elif dia_semana == 6:  # Dom
    if 17.0 <= hora_decimal <= 24.0:
      return True
  elif 0 <= dia_semana <= 3:  # Lun-Jue
    if 13.0 <= hora_decimal <= 22.0:
      return True
  return False


def ejecutar_barrido_web():
  """Motor central de extracción que alimenta la caché o responde por demanda."""
  hallazgos = []
  headers = {"User-Agent": "Mozilla/5.0"}

  # Barrido de RSS locales
  for url_rss in FEEDS_RSS_LOCALES:
    try:
      resp = requests.get(url_rss, headers=headers, timeout=3)
      if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, "xml")
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

  # Barrido de Cuentas Oficiales vía Nitter
  for cuenta in CUENTAS_X_OFICIALES:
    try:
      url = f"https://nitter.privacydev.net/{cuenta}"
      resp = requests.get(url, headers=headers, timeout=3)
      if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        for tweet in soup.select(".tweet-content")[:2]:
          texto = tweet.get_text(strip=True)
          if any(f.lower() in texto.lower() for f in FILTROS_VALLE_52):
            hallazgos.append(f"📱 **@{cuenta}**: {texto}")
    except Exception:
      pass

  return list(set(hallazgos))


def tarea_cron():
  """Los crons ejecutan el barrido automáticamente solo dentro de la ventana."""
  global NOVEDADES_CACHE
  if not esta_en_ventana_operativa():
    return
  resultados = ejecutar_barrido_web()
  if resultados:
    NOVEDADES_CACHE = resultados


# Configurar planificador de crons a los minutos 15 y 45
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(tarea_cron, "cron", minute="15,45", id="cron_job")
scheduler.start()


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
    requests.post(
        url_api,
        json={
            "chat_id": chat_id,
            "text": (
                "¡Hola, Raúl! KITT-BOT operando. Crons en horario y Comando P"
                " con barrido en vivo 24/7."
            ),
        },
    )

  elif texto.upper() == "P" or texto.lower() == "/p":
    # El comando P ejecuta un barrido en tiempo real por demanda en cualquier momento
    hallazgos_demanda = ejecutar_barrido_web()

    if not hallazgos_demanda:
      respuesta = (
          f"🕒 **REPORTE TOTAL UNIFICADO VALLE DE ABURRÁ**\n🕒"
          f" {hora_legal_str}\n\nSIN NOVEDADES"
      )
    else:
      cuerpo_reporte = "\n".join(hallazgos_demanda)
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
    
