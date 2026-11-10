import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Token oficial de Telegram y URL externa de Render
TELEGRAM_TOKEN = "9072501655:AAELlv7cG0FkQXhk0FQ0MrY4RBhca0q4KQA"
RENDER_EXTERNAL_URL = "https://kitt-bot.onrender.com"

# Cuentas clave de gremios, conductores y reportes ciudadanos en el Valle de Aburrá
PERFILES_OBJETIVO = [
    "DenunciasAntio2",
    "GuardianesMed",
    "AlertaMedellin",
    "TraficoMedellin",
    "ReporteVialAnt",
    "MoterosMedellin",
    "TaxistasMed",
    "ConduceMedellin",
    "CamionerosAnt",
    "TransporteMed",
    "QHuboMedellin",
    "Minuto30com",
    "Hora13Noticias",
    "MovilidadAnt",
    "TransitoMedellin",
    "RedVialMed",
    "ControlVialMed"
]

# Múltiples instancias espejo de Nitter para evitar bloqueos y garantizar alta disponibilidad
INSTANCIAS_NITTER = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.catsarch.com"
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

def ejecutar_barrido_multiespejo():
    novedades = []
    palabras_clave = [
        "reten", "retenes", "Mega reten", "puesto de control", "puestos de control", 
        "azulitos", "pitufos", "azules", "guarda", "guardas", "tránsito", "alcoholemia", 
        "901", "accidente", "cierre", "trancon", "congestion", "bloqueo", "taco", 
        "vía cerrada", "vías cerradas", "siniestro", "protesta", "chocar", "choque",
        "moteros", "taxistas", "platillos", "agentes"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    for perfil in PERFILES_OBJETIVO:
        leido_exitosamente = False
        
        # Probamos de forma inteligente en diferentes espejos si uno falla o rechaza la conexión
        for instancia in INSTANCIAS_NITTER:
            if leido_exitosamente:
                break
            
            target_url = f"{instancia}/{perfil}/rss"
            try:
                res = requests.get(target_url, headers=headers, timeout=3)
                print(f"[Multi-Mirror] Nodo {target_url} -> Status: {res.status_code}", flush=True)
                
                if res.status_code == 200:
                    contenido = res.text.lower()
                    for keyword in palabras_clave:
                        if keyword in contenido:
                            novedades.append(f"🚨 **Alerta en @{perfil}:** Match con `{keyword}`")
                            break
                    leido_exitosamente = True
                    break
            except Exception as e:
                # Si falla una instancia, pasamos silenciosamente a la siguiente del espejo
                continue
                
        if not leido_exitosamente:
            print(f"[Multi-Mirror Warning] No se pudo conectar con ningún espejo para @{perfil}", flush=True)
            
    # Mostramos los reportes más recientes primero
    return list(reversed(novedades))

@app.route('/', methods=['GET'])
def home():
    configurar_webhook_automatico()
    return "KITT-BOT Multiespejo Gremios Operativo", 200

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
                "🤖 **Kitt (Sistema Multiespejo) en línea.** Presiona la **P** para buscar retenes y alertas viales.",
                incluir_teclado=True
            )
        else:
            # Petición por demanda independiente de los cron jobs programados
            resultados = ejecutar_barrido_multiespejo()
            if not resultados:
                resp = "🟢 **SIN NOVEDADES REPORTADAS EN LA RED** (Espejos consultados sin coincidencias activas)."
            else:
                resp = "🚨 **ALERTAS DE CONDUCTORES Y GREMIOS (Más recientes primero):**\n\n" + "\n".join(resultados)
            enviar_mensaje_telegram(chat_id, resp, incluir_teclado=True)
            
    return "OK", 200

configurar_webhook_automatico()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
            
