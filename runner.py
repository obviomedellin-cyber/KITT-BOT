import os
import requests
from extractor import extract_latest_reports

# Configuración de Telegram (puedes usar tus variables de entorno)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "9072501655:AAELlv7cG0FkQXhk0FQ0MrY4RBhca0q4KQA")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "TU_CHAT_ID_AQUI") # Opcional: tu ID personal para pruebas

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Error enviando mensaje: {e}")
        return False

def run_extraction_and_notify():
    print("Ejecutando extractor externo...")
    data = extract_latest_reports("ControlVialMed", max_tweets=3)
    
    if data["status"] == "success" and data["reports"]:
        message = f"🚨 **Últimos Reportes Viales ({data['active_mirror']})**:\n\n"
        for rep in data["reports"]:
            message += f"• [{rep['date']}] {rep['report']}\n\n"
    else:
        message = "🟢 SIN NOVEDADES REPORTADAS EN LA RED (Extractor externo sin coincidencias)."
        
    print(message)
    # Si deseas que envíe la notificación automáticamente a un chat:
    # send_telegram_message(CHAT_ID, message)

if __name__ == "__main__":
    run_extraction_and_notify()
                                                  
