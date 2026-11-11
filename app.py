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

# Importación segura de la base de datos externa
try:
    from datos import BASE_DATOS_AZULES
    logger.info("Base de datos de fuentes cargada exitosamente desde datos.py.")
except ImportError:
    BASE_DATOS_AZULES = {}
    logger.warning("No se encontró datos.py, operando con respaldo vacío.")

# Inicializar Flask
app_flask = Flask(__name__)

# ----------------------------------------------------
# SISTEMA DE ESPEJOS (Instancias limpias y estables)
# ----------------------------------------------------
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
    """Envía mensajes directamente vía HTTP API de Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Error enviando mensaje a Telegram: {e}")

@app_flask.route('/')
def index():
    return "Kitt Bot está activo y operando en el Valle de Aburrá.", 200

@app_flask.route('/webhook', methods=["POST"])
def telegram_webhook():
    """Recibe los eventos directamente en la ruta /webhook que usa Telegram."""
    data = request.get_json(force=True)
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text.startswith("/p"):
            response_text = fetch_from_mirrors("ControlVialMed")
            send_telegram_message(chat_id, response_text)
            
    return "OK", 200

if __name__ == "__main__":
    app_flask.run(host="0.0.0.0", port=PORT)
        
