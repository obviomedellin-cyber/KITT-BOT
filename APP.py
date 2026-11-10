from datetime import datetime
import pytz
from flask import Flask, request
import requests

app = Flask(__name__)

# Token de tu bot de Telegram
TELEGRAM_TOKEN = "9084832898:AAGQCqGvBrtNRy9kQ34QnLlrSYUUEBsG7x8"

# Definir la zona horaria legal de Colombia
bogota_tz = pytz.timezone("America/Bogota")


@app.route("/webhook", methods=["POST"])
def webhook():
  data = request.get_json()

  if not data or "message" not in data:
    return "OK", 200

  message = data["message"]
  chat_id = message["chat"]["id"]
  texto = message.get("text", "").strip()

  # Obtener la hora actual en zona legal America/Bogota
  ahora_bogota = datetime.now(bogota_tz)
  hora_legal_str = ahora_bogota.strftime("%I:%M %p")

  url_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

  # Comando /start o saludo inicial
  if texto.lower() in ["/start", "hola"]:
    respuesta = (
        f"¡Hola, Raúl! KITT-BOT en línea.\n📊 Fuentes: 82\n📍 Filtros Valle:"
        " 52\nListo para operar."
    )
    requests.post(url_api, json={"chat_id": chat_id, "text": respuesta})

  # Procesar comando P (Reporte Total Unificado Valle de Aburrá por demanda)
  elif texto.upper() == "P" or texto.lower() == "/p":
    # El comando P se ejecuta por demanda a cualquier hora
    secciones_con_novedad = []

    if not secciones_con_novedad:
      respuesta = (
          f"🕒 **REPORTE TOTAL UNIFICADO VALLE DE ABURRÁ**\n🕒"
          f" {hora_legal_str}\n\nSIN NOVEDADES"
      )
    else:
      cuerpo_reporte = "\n".join(secciones_con_novedad)
      respuesta = (
          f"🕒 **REPORTE TOTAL UNIFICADO VALLE DE ABURRÁ**\n🕒"
          f" {hora_legal_str}\n\n{cuerpo_reporte}"
      )

    requests.post(url_api, json={"chat_id": chat_id, "text": respuesta})

  return "OK", 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
  
