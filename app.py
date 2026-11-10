import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Token oficial de Telegram y URL externa de Render
TELEGRAM_TOKEN = "9072501655:AAELlv7cG0FkQXhk0FQ0MrY4RBhca0q4KQA"
RENDER_EXTERNAL_URL = "https://kitt-bot.onrender.com"

# Las 84 fuentes completas de movilidad, tráfico y emergencias del Valle de Aburrá
FUENTES_ABURRA = [
    "https://nitter.privacydev.net/AlcaldiaMed",
    "https://nitter.privacydev.net/TransitoMedellin",
    "https://nitter.privacydev.net/DAGRDMedellin",
    "https://nitter.privacydev.net/Areametropol",
    "https://nitter.privacydev.net/MetroMedellin",
    "https://nitter.privacydev.net/MedellinResponde",
    "https://nitter.privacydev.net/SecMovilidadMed",
    "https://nitter.privacydev.net/CulturaTransito",
    "https://nitter.privacydev.net/GobAntioquia",
    "https://nitter.privacydev.net/SecSeguridadMed",
    "https://nitter.privacydev.net/BomberosMed",
    "https://nitter.privacydev.net/Ruta40_Med",
    "https://nitter.privacydev.net/PoliciaMedellin",
    "https://nitter.privacydev.net/TransitPolicia",
    "https://nitter.privacydev.net/EmergenciasMed",
    "https://nitter.privacydev.net/MovilidadAnt",
    "https://nitter.privacydev.net/Devimed",
    "https://nitter.privacydev.net/ConvisaVias",
    "https://nitter.privacydev.net/AutopistasCafe",
    "https://nitter.privacydev.net/Coviandes",
    "https://nitter.privacydev.net/ViasAmericas",
    "https://nitter.privacydev.net/ConcesionAburra",
    "https://nitter.privacydev.net/TusViasAntioquia",
    "https://nitter.privacydev.net/Inviias",
    "https://nitter.privacydev.net/RedVialNal",
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

def configurar_webhook_automatico():
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={RENDER_EXTERNAL_URL}/webhook"
        res = requests.get(url, timeout=5)
        print(f"-> AUTOREGISTRO WEBHOOK TELEGRAM: {res.text}", flush=True)
    except Exception as e:
        print(f"-> EXCEPCIÓN AL REGISTRAR WEBHOOK: {e}", flush=True)

def enviar_mensaje_telegram(chat_id, texto, incluir_teclado=False):
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
    except Exception:
        pass

def ejecutar_barrido_trafico():
    novedades = []
    palabras_clave = [
        "accidente", "reten", "cierre", "trancon", "congestion", "atropello", 
        "volcado", "incendio", "caida arbol", "protesta", "bloqueo", "marcha", 
        "fallecido", "heridos", "emergencia", "azules", "azulitos", "retenes", 
        "Mega reten", "circo", "puesto de control", "gases", "Puntos", "tránsito", 
        "alcoholemia", "puestos de control", "pitufos", "guarda", "guardas", "901", 
        "muerto", "matado", "choque", "taco", "7 3", "parqueadero", "cierres programados", 
        "persisten", "continúa", "sigue", "túnel", "oriente", "caliente", "vías cerradas", 
        "vía cerrada", "balacera", "orden público", "zona roja", "no se mueve", 
        "activo", "activos", "siniestro"
    ]
    
    for fuente in FUENTES_ABURRA:
        try:
            res = requests.get(fuente, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=3)
            if res.status_code == 200:
                c = res.text.lower()
                if any(p in c for p in palabras_clave):
                    novedades.append(f"⚠️ Alerta en fuente: {fuente}")
        except Exception:
            pass
            
    # Mostramos los reportes más recientes primero
    return list(reversed(novedades))

@app.route('/', methods=['GET'])
def home():
    configurar_webhook_automatico()
    return "KITT-BOT Valle de Aburrá Operativo", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True, silent=True) or request.form.to_dict()
    print(f"-> WEBHOOK RECIBIDO: {data}", flush=True)
    
    chat_id = None
    texto_msg = ""
    
    if data and 'message' in data:
        msg = data['message']
        chat_id = msg.get('chat', {}).get('id')
        texto_msg = msg.get('text', '').strip()
    
    if chat_id:
        if texto_msg.lower() == '/start':
            enviar_mensaje_telegram(
                chat_id, 
                "🤖 **Kitt en línea.** Presiona el botón **P** abajo para ejecutar el barrido manual por demanda.",
                incluir_teclado=True
            )
        else:
            # Petición por demanda independiente de los cron jobs programados
            resultados = ejecutar_barrido_trafico()
            if not resultados:
                resp = "🟢 **SIN NOVEDADES** en el Valle de Aburrá."
            else:
                resp = "⚠️ **NOVEDADES DETECTADAS (Más recientes primero):**\n\n" + "\n".join(resultados)
            enviar_mensaje_telegram(chat_id, resp, incluir_teclado=True)
            
    return "OK", 200

# Configuramos el webhook al arrancar
configurar_webhook_automatico()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    

# Fin de la aplicación Flask de Kitt para el Valle de Aburrá
