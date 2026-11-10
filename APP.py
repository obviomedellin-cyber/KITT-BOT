import os
import requests
from flask import Flask, request
from datos import BASE_DATOS_AZULES, VALLE_ABURRA

app = Flask(__name__)

PORT = int(os.environ.get("PORT", "10000"))
TOKEN = "9084832898:AAGQCqGvBrtNRy9kQ34QnLlrSYUUEBsG7x8"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", TOKEN)
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def enviar_mensaje(chat_id, texto):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error enviando mensaje: {e}")

@app.route("/")
def home():
    tf = len(BASE_DATOS_AZULES)
    tv = len(VALLE_ABURRA)
    return f"KITT-BOT online! Fuentes: {tf} | Valle: {tv}", 200

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data:
        msg = data["message"]
        chat_id = msg["chat"].get("id")
        txt = msg.get("text", "")

        if txt.startswith("/start"):
            resp = (
                "¡Hola, Raúl! KITT-BOT en línea.\n"
                f"📊 Fuentes: {len(BASE_DATOS_AZULES)}\n"
                f"📍 Filtros Valle: {len(VALLE_ABURRA)}\n"
                "Listo para operar."
            )
        else:
            resp = f"KITT-BOT procesando: '{txt}'"

        enviar_mensaje(chat_id, resp)

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
