import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Token leído de forma segura desde las variables de entorno de Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Lista completa de las 82 fuentes del Valle de Aburrá
FUENTES_ABURRA = [
    # --- MEDELLÍN Y SECRETARÍA DE MOVILIDAD ---
    "https://nitter.privacydev.net/AlcaldiaMed",
    "https://nitter.privacydev.net/TransitoMedellin",
    "https://nitter.privacydev.net/DAGRDMedellin",
    "https://nitter.privacydev.net/Areametropol",
    "https://nitter.privacydev.net/MetroMedellin",
    "https://nitter.privacydev.net/MedellinResponde",
    "https://nitter.privacydev.net/SecMovilidadMed",
    "https://nitter.privacydev.net/CulturaTransito",
    
    # --- EMERGENCIAS, BOMBEROS Y SEGURIDAD ANTIOQUIA ---
    "https://nitter.privacydev.net/GobAntioquia",
    "https://nitter.privacydev.net/SecSeguridadMed",
    "https://nitter.privacydev.net/BomberosMed",
    "https://nitter.privacydev.net/Ruta40_Med",
    "https://nitter.privacydev.net/PoliciaMedellin",
    "https://nitter.privacydev.net/TransitPolicia",
    "https://nitter.privacydev.net/EmergenciasMed",
    "https://nitter.privacydev.net/MovilidadAnt",
    
    # --- CONCESIONES VIALES Y AUTOPISTAS ---
    "https://nitter.privacydev.net/Devimed",
    "https://nitter.privacydev.net/ConvisaVias",
    "https://nitter.privacydev.net/AutopistasCafe",
    "https://nitter.privacydev.net/Coviandes",
    "https://nitter.privacydev.net/ViasAmericas",
    "https://nitter.privacydev.net/ConcesionAburra",
    "https://nitter.privacydev.net/TusViasAntioquia",
    "https://nitter.privacydev.net/Inviias",
    "https://nitter.privacydev.net/RedVialNal",
    
    # --- MUNICIPIOS DEL VALLE DE ABURRÁ (NORTE A SUR) ---
    "https://nitter.privacydev.net/AlcaldiaBarbosa",
    "https://nitter.privacydev.net/TransitoBarbosa",
    "https://nitter.privacydev.net/AlcaldiaGirardota",
    "https://nitter.privacydev.net/TransitoGirardota",
    "https://nitter.privacydev.net/AlcaldiaCopa",
    "https://nitter.privacydev.net/TransitoCopa",
    "https://nitter.privacydev.net/AlcaldiaBello",
    "https://nitter.privacydev.net/SecMovilidadBello",
    "https://nitter.privacydev.net/BomberosBello",
    "https://nitter.privacydev.net/AlcaldiaItagui",
    "https://nitter.privacydev.net/MovilidadItagui",
    "https://nitter.privacydev.net/AlcaldiaEnvigado",
    "https://nitter.privacydev.net/MovilidadEnviga",
    "https://nitter.privacydev.net/AlcaldiaSabaneta",
    "https://nitter.privacydev.net/TransitoSaba",
    "https://nitter.privacydev.net/AlcaldiaEstrella",
    "https://nitter.privacydev.net/TransitoEstrella",
    "https://nitter.privacydev.net/AlcaldiaCaldasAnt",
    "https://nitter.privacydev.net/TransitoCaldas",
    
    # --- MEDIOS DE COMUNICACIÓN Y REPORTES CIUDADANOS / RADIALES ---
    "https://nitter.privacydev.net/DenunciasAntio2",
    "https://nitter.privacydev.net/GuardianesMed",
    "https://nitter.privacydev.net/AlertaMedellin",
    "https://nitter.privacydev.net/MobilityMedellin",
    "https://nitter.privacydev.net/NoticiasTelemed",
    "https://nitter.privacydev.net/Teleantioquia",
    "https://nitter.privacydev.net/Hora13Noticias",
    "https://nitter.privacydev.net/QHuboMedellin",
    "https://nitter.privacydev.net/ElColombiano",
    "https://nitter.privacydev.net/ElMundoMedellin",
    "https://nitter.privacydev.net/Minuto30com",
    "https://nitter.privacydev.net/BluRadioMed",
    "https://nitter.privacydev.net/CaracolMedellin",
    "https://nitter.privacydev.net/RCNRadioMed",
    "https://nitter.privacydev.net/WRadioColombia",
    "https://nitter.privacydev.net/Antena2Medellin",
    "https://nitter.privacydev.net/TropicanaMed",
    "https://nitter.privacydev.net/LaMegaMedellin",
    "https://nitter.privacydev.net/FmMedellin",
    "https://nitter.privacydev.net/LaFM_Medellin",
    "https://nitter.privacydev.net/TeleMedellin",
    "https://nitter.privacydev.net/Cosmovision",
    "https://nitter.privacydev.net/CanalU",
    "https://nitter.privacydev.net/TMVNoticias",
    "https://nitter.privacydev.net/PrensaMedellin",
    "https://nitter.privacydev.net/RedVialMed",
    "https://nitter.privacydev.net/TraficoMedellin",
    "https://nitter.privacydev.net/ReporteVialAnt",
    "https://nitter.privacydev.net/CamarasMedellin",
    "https://nitter.privacydev.net/SemáforosMed",
    "https://nitter.privacydev.net/ObrasMedellin",
    "https://nitter.privacydev.net/InviasAntioquia",
    "https://nitter.privacydev.net/AeroMedellin",
    "https://nitter.privacydev.net/ClimaMedellin",
    "https://nitter.privacydev.net/SIATA_Medellin",
    "https://nitter.privacydev.net/IdeamColombia",
    "https://nitter.privacydev.net/CruzRojaAnt",
    "https://nitter.privacydev.net/DefensaCivilAnt",
    "https://nitter.privacydev.net/AidsMovilidad",
    "https://nitter.privacydev.net/ControlVialMed"
]

def enviar_mensaje_telegram(chat_id, texto, incluir_teclado=False):
    if not TELEGRAM_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown"
    }
    
    if incluir_teclado:
        payload["reply_markup"] = {
            "keyboard": [[{"text": "P"}]],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"-> Error enviando mensaje a Telegram: {e}")

def ejecutar_barrido_trafico():
    print(f"--- INICIANDO BARRIDO DE {len(FUENTES_ABURRA)} FUENTES EN VIVO ---")
    novedades_capturadas = set()
    
    for fuente in FUENTES_ABURRA:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(fuente, headers=headers, timeout=2)
            
            if response.status_code == 200:
                contenido = response.text
                if any(palabra in contenido.lower() for palabra in ["colisión", "trafico", "tráfico", "accidente", "vehicular", "bloqueo", "cierres", "mobilidad", "movilidad"]):
                    novedades_capturadas.add(f"Alerta en fuente: {fuente}")
        except Exception:
            pass

    print(f"--- FIN DEL BARRIDO. Novedades únicas encontradas: {len(novedades_capturadas)} ---")
    return list(novedades_capturadas)

@app.route('/', methods=['GET'])
def home():
    return "KITT-BOT Valle de Aburrá Operativo y Escuchando Webhooks", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    print(f"--> WEBHOOK RECIBIDO EXITOSAMENTE: {data}")
    
    if data and 'message' in data:
        chat = data['message'].get('chat', {})
        chat_id = chat.get('id')
        texto_msg = data['message'].get('text', '').strip()
        
        if texto_msg.lower() == '/start':
            enviar_mensaje_telegram(
                chat_id, 
                "🤖 **Kitt activado.** Presiona el botón **P** abajo en tu pantalla para iniciar el barrido de tráfico en las 82 fuentes.",
                incluir_teclado=True
            )
        elif texto_msg != '':
            print("--> Ejecutando barrido de tráfico por demanda a petición del usuario...")
            resultados = ejecutar_barrido_trafico()
            
            if not resultados:
                respuesta = "🟢 **SIN NOVEDADES** en el Valle de Aburrá."
            else:
                respuesta = "⚠️ **NOVEDADES DETECTADAS:**\n\n" + "\n".join(resultados)
                
            if chat_id:
                enviar_mensaje_telegram(chat_id, respuesta, incluir_teclado=True)
    
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
