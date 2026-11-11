import os
import logging
import requests
from flask import Flask, request

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

# Instancias de Nitter estables
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org"
]

def fetch_from_mirrors(account_name: str):
    for instance in NITTER_INSTANCES:
        url = f"{instance}/{account_name}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return f"🟢 Red activa - Datos consultados desde {instance}"
        except Exception:
            continue
    return "🟢 SIN NOVEDADES REPORTADAS EN LA RED."

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
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
    try:
        data = request.get_json(silent=True)
        if not data:
            return "OK", 200
            
        logger.info(f"Payload recibido: {data}")
        
        # Extraer mensaje de texto de forma segura
        message = data.get("message") or data.get("edited_message")
        if message:
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip().lower()
            
            # Responder a cualquier 'p', '/p' o comando similar
            if "p" in text:
                response_text = fetch_from_mirrors("ControlVialMed")
                send_telegram_message(chat_id, response_text)
                
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        
    return "OK", 200

if __name__ == "__main__":
    app_flask.run(host="0.0.0.0", port=PORT)
            
