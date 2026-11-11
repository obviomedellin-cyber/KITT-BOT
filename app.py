# app.py
# Servidor Flask principal para el webhook de Kitt en Render

import os
import logging
import requests
from flask import Flask, request
from ejecutor import ejecutar_extraccion_desde_fuentes

# Configuración de Logging base
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Parámetros esenciales
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "9072501655:AAELlv7cG0FkQXhk0FQ0MrY4RBhca0q4KQA")
PORT = int(os.environ.get("PORT", 10000))

# Inicializar Flask
app_flask = Flask(__name__)

def send_telegram_message(chat_id, text):
    """Envía la respuesta formateada a Telegram con soporte Markdown"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        res = requests.post(url, json=payload, timeout=5)
        logger.info(f"Respuesta de Telegram API: {res.status_code}")
    except Exception as e:
        logger.error(f"Error enviando mensaje: {e}")

@app_flask.route('/')
def index():
    return "Kitt Bot está activo.", 200

@app_flask.route('/webhook', methods=["POST"])
def telegram_webhook():
    """Recibe los pings de Telegram y dispara la vasija al detectar la 'P'"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return "OK", 200
            
        logger.info(f"Payload recibido: {data}")
        
        message = data.get("message") or data.get("edited_message")
        if message:
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip().lower()
            
            # Si el usuario envía la 'P' (o comando que la contenga)
            if "p" in text:
                # Se delega completamente la obtención del reporte a ejecutor.py
                response_text = ejecutar_extraccion_desde_fuentes()
                send_telegram_message(chat_id, response_text)
                
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        
    return "OK", 200

if __name__ == "__main__":
    app_flask.run(host="0.0.0.0", port=PORT)
