import os
import requests
from flask import Flask, request
from datos import BASE_DATOS_AZULES, VALLE_ABURRA

app = Flask(__name__)

PORT = int(os.environ.get("PORT", "10000"))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "9084832898:AAGQCqGvBrtNRy9kQ34QnLlrSYUUEBsG7x8")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def enviar_mensaje(chat_id, texto):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error enviando mensaje: {e}")

@app.route("/")
def home():
    total_fuentes = len(BASE_DATOS_AZULES)
    total_valle = len(VALLE_ABURRA)
    return f"KITT-BOT is online and operational! Fuentes cargadas: {total_fuentes} | Filtros Valle: {total_valle}", 200

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.
