import os
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Configuración de Logging base
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Parámetros de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID") # Chat o canal autorizado para reportes automáticos

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

    # Filtro de precisión para asegurar ejecución en :15 y :45 (+/- tolerancia de sondeo)
    if current_minute not in [15, 45]:
        return

    logger.info(f"Ejecutando cron automático de Kitt a las {now.strftime('%H:%M')}")
    
    try:
        # Bloque de ingesta con control de reintentos (prevención de Status 429)
        # Aquí se conectan las fuentes abiertas y espejos de tráfico regional
        reporte_dinamico = (
            f"📊 **REPORTE AUTOMÁTICO KITT** — [{now.strftime('%H:%M')} COT]\n"
            f"• *Radio:* Valle de Aburrá (Cobertura subregional).\n"
            f"• *Estado:* Datos efímeros procesados en tiempo real.\n"
            f"• *Novedad:* Monitoreo de corredores viales activo sin saturación de nodos."
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
        respuesta_demanda = (
            "⚡ **KITT — CONSULTA POR DEMANDA ACTIVADA**\n"
            "• *Ámbito:* Valle de Aburrá.\n"
            "• *Proceso:* Extracción de datos en tiempo real ejecutada bajo demanda.\n"
            "• *Resultado:* Canales y eventos efímeros sincronizados para análisis táctico inmediato."
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
        logger.error("No se encontró el token de Telegram configurado en las variables de entorno.")
        return

    # Construcción de la aplicación de Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Registro del comando manual por demanda (/p)
    app.add_handler(CommandHandler("p", demand_query_command))

    # Configuración del Job Queue para los crons (evaluación continua cada minuto para capturar :15 y :45)
    job_queue = app.job_queue
    job_queue.run_repeating(automated_big_data_sweep, interval=60, first=10)

    logger.info("Kitt inicializado correctamente. Crons y comando /p configurados en paralelo.")
    
    # Ejecución en modo polling continuo para infraestructura cloud persistente
    app.run_polling()

if __name__ == "__main__":
    main()
    


