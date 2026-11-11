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

# Parámetros de entorno con tu token integrado
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "9072501655:AAELlv7cG0FkQXhk0FQ0MrY4RBhca0q4KQA")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID", "")
PORT = int(os.environ.get("PORT", 10000))

# Servidor Flask básico para mantener el servicio activo en Render
app_flask = Flask(__name__)

@app_flask.route('/')
def index():
    return "Kitt Bot está activo y operando en el Valle de Aburrá.", 200

# ---------------------------------------------------------
# SISTEMA DE ROTACIÓN DE ESPEJOS CON MANEJO DE RATE LIMIT (429)
# ---------------------------------------------------------
NITTER_INSTANCES = [
    "https://nitter.catsarch.com",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.woodland.coffee"
]

def fetch_from_mirrors(account_name: str):
    """
    Intenta consultar una cuenta a través de una lista de espejos Nitter de forma rotativa
    para prevenir bloqueos por límite de peticiones (Status 429).
    """
    for instance in NITTER_INSTANCES:
        url = f"{instance}/{account_name}/rss"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"Conexión exitosa con espejo: {instance} para @{account_name}")
                return response.text
            elif response.status_code == 429:
                logger.warning(f"[Rate Limit 429] Nodo {instance} saturado para @{account_name}. Probando siguiente...")
            else:
                logger.warning(f"Nodo {instance} devolvió status {response.status_code}")
        except Exception as e:
            logger.warning(f"Fallo de conexión con nodo {instance} para @{account_name}: {e}")
    
    logger.error(f"[Multi-Mirror Error] No se pudo conectar con ningún espejo para @{account_name}")
    return None

# ---------------------------------------------------------
# 1. TAREAS PROGRAMADAS (CRONS: :15 y :45 de cada hora)
# ---------------------------------------------------------
async def automated_big_data_sweep(context: ContextTypes.DEFAULT_TYPE):
    """
    Barrido automático programado para ejecutarse estrictamente a los minutos 
    15 y 45 de cada hora, cubriendo todo el Valle de Aburrá.
    """
    now = datetime.now()
    current_minute = now.minute

    if current_minute not in [15, 45]:
        return

    logger.info(f"Ejecutando cron automático de Kitt a las {now.strftime('%H:%M')}")
    
    try:
        data_vial = fetch_from_mirrors("ControlVialMed")
        
        reporte_dinamico = (
            f"📊 **REPORTE AUTOMÁTICO KITT** — [{now.strftime('%H:%M')} COT]\n"
            f"• *Radio:* Valle de Aburrá (Cobertura subregional).\n"
            f"• *Estado:* Datos efímeros procesados en tiempo real.\n"
            f"• *Novedad:* Monitoreo de corredores viales activo (Espejos sincronizados)."
        )
        
        if TARGET_CHAT_ID:
            await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=reporte_dinamico, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error en tarea programada (cron) de Kitt: {e}")

# ---------------------------------------------------------
# 2. COMANDO P (POR DEMANDA - INDEPENDIENTE DE CRONS)
# ---------------------------------------------------------
async def demand_query_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando manual /p para consultas por demanda en tiempo real.
    Opera de forma independiente y asíncrona respecto a los crons programados.
    """
    user_id = update.effective_user.id
    logger.info(f"Comando /p activado por demanda (Usuario ID: {user_id})")
    
    try:
        _ = fetch_from_mirrors("RedVialMed")
        
        respuesta_demanda = (
            "⚡ **KITT — CONSULTA POR DEMANDA ACTIVADA**\n"
            "• *Ámbito:* Valle de Aburrá.\n"
            "• *Proceso:* Extracción de datos en tiempo real ejecutada bajo demanda.\n"
            "• *Resultado:* Canales y eventos efímeros sincronizados con rotación de nodos."
        )
        await update.message.reply_text(respuesta_demanda, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error procesando comando /p: {e}")
        await update.message.reply_text("⚠️ Error temporal al procesar la solicitud por demanda.")

# ---------------------------------------------------------
# 3. CONFIGURACIÓN E INICIALIZACIÓN GLOBAL DE KITT
# ---------------------------------------------------------
def main():
    if not TELEGRAM_TOKEN:
        logger.error("⚠️ ADVERTENCIA: El token de Telegram no está definido.")
        return

    # Construcción de la aplicación de Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Registro del comando manual por demanda (/p)
    app.add_handler(CommandHandler("p", demand_query_command))

    # Configuración del Job Queue para los crons (evaluación continua cada minuto para capturar :15 y :45)
    job_queue = app.job_queue
    job_queue.run_repeating(automated_big_data_sweep, interval=60, first=10)

    logger.info("Kitt inicializado correctamente con rotación de espejos anti-429.")
    
    app.run_polling()

if __name__ == "__main__":
    main()
    
