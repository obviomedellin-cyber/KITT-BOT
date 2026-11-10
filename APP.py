from datetime import datetime, time
import pytz
from flask import Flask, request
import requests

app = Flask(__name__)

# Token de tu bot de Telegram
TELEGRAM_TOKEN = "9084832898:AAGQCqGvBrtNRy9kQ34QnLlrSYUUEBsG7x8"

# Definir la zona horaria legal de Colombia
bogota_tz = pytz.timezone("America/Bogota")


def validar_ventana_horaria(dt_actual):
  """Valida si el momento actual se encuentra dentro de las ventanas operativas."""
  dia_semana = (
      dt_actual.weekday()
  )  # 0: Lun, 1: Mar, 2: Mié, 3: Jue, 4: Vie, 5: Sáb, 6: Dom
  hora_actual = dt_actual.time()

  # Viernes (4) y Sábado (5): 7:00 p.m. a 5:00 a.m. del día siguiente
  if dia_semana == 4 or dia_semana == 5:
    if hora_actual >= time(19, 0) or hora_actual <= time(5, 0):
      return True
  # Domingo (6): 5:00 p.m. a 12:00 a.m.
  elif dia_semana == 6:
    if time(17, 0) <= hora_actual <= time(23, 59):
      return True
  # Lunes a Jueves (0 a 3): 1:00 p.m. a 10:00 p.m.
  elif 0 <= dia_semana <= 3:
    if time(13, 0) <= hora_actual <= time(22, 0):
      return True

  return False


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

  # Procesar comando P (Reporte Total Unificado Valle de Aburrá)
  elif texto.upper() == "P" or texto.lower() == "/p":
    # Validar si está dentro de las ventanas operativas
    if not validar_ventana_horaria(ahora_bogota):
      respuesta = (
          f"🕒 {hora_legal_str}\nFuera de ventana operativa establecida."
          " Consulte más tarde."
      )
    else:
      # Lógica de fuentes y semáforos (🔴 > 🟡 > ⚫ > 🟢)
      secciones_con_novedad = []

      # Ejemplo de validación de prueba (puedes integrar tus datos aquí)
      # secciones_con_novedad.append("🔴 Movilidad: Novedad crítica en la vía.")

      if not secciones_con_novedad:
        respuesta = f"🕒 {hora_legal_str}\nSIN NOVEDADES"
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
    
