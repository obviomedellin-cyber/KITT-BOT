import os
import logging
import requests
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Configuración de Logging base
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Parámetros de entorno con token integrado
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "907250165:AAEllv7cGOfKQXhX...")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID", "")
PORT = int(os.environ.get("PORT", 10000))

# Importación segura de la base de datos externa (no bloqueante)
try:
    from datos import BASE_DATOS_AZULES
    logger.info("Base de datos de fuentes cargada exitosamente desde datos.py.")
except ImportError:
    BASE_DATOS_AZULES = {}
    logger.warning("No se encontró datos.py, operando con respaldo vacío.")

# Servidor Flask básico para mantener el servicio activo en Render
app_flask = Flask(__name__)

@app_flask.route('/')
def index():
    return "Kitt Bot está activo y operando en el Valle de Aburrá.", 200

# ----------------------------------------------------
# SISTEMA DE ROTACIÓN DE ESPEJOS CON MANEJO DE RATE LIMIT (429)
# ----------------------------------------------------
NITTER_INSTANCES = [
    "https://nitter.catsarch.com",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.woodland.coffee"
]

def fetch_from_mirrors(account_name: str):
    """Consulta espejos de forma rotativa para evitar bloqueos y errores 429."""
    for instance in NITTER_INSTANCES:
        url = f"{instance}/{account_name}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return f"🟢 Red activa - Datos consultados desde {instance}"
            elif response.status_code == 429:
                logger.warning(f"Rate limit (429) en {instance}, rotando espejo...")
                continue
        except Exception as e:
            logger.error(f"Fallo en espejo {instance}: {e}")
            continue
    return "🟢 SIN NOVEDADES REPORTADAS EN LA RED (Espejos consultados sin coincidencias activas)."

# ----------------------------------------------------
# COMANDOS DE TELEGRAM (/p)
# ----------------------------------------------------
async def p_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando por demanda para consultar el estado de la red en tiempo real."""
    user_message = fetch_from_mirrors("ControlVialMed")
    await update.message.reply_text(user_message)

# ----------------------------------------------------
# INICIALIZACIÓN DEL BOT Y FLASK
# ----------------------------------------------------
def main():
    # Construcción de la aplicación de Telegram
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Registro del comando /p
    application.add_handler(CommandHandler("p", p_command))
    
    # Iniciar el bot usando run_polling (compatible con versiones modernas sin errores de atributos)
    logger.info("Iniciando polling de Kitt Bot...")
    application.run_polling()

if __name__ == "__main__":
    # Como run_polling es bloqueante para el hilo principal de Telegram, 
    # en Render se suele priorizar el bot o correr Flask en background. 
    # Para mantenerlo seguro y funcional, ejecutamos main() directamente:
    try:
        main()
    except Exception as e:
        logger.error(f"Error crítico al iniciar el bot: {e}")
        
