# ejecutor.py
# Módulo especializado en procesar y ejecutar la extracción de tráfico 
# con rotación de espejos y cabeceras anti-bloqueo.

import requests
from datos import LATEST_TRAFFIC_DATA, get_current_report_text

# Cabeceras simulando un navegador real para evitar bloqueos anti-scraping por defecto
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def ejecutar_extraccion_desde_fuentes():
    """
    Lee las fuentes y rota por los espejos configurados en datos.py, 
    aplicando cabeceras reales y manejo de reintentos ante bloqueos.
    """
    print("🚦 [Kitt] Iniciando ejecución y escaneo de fuentes viales...")
    
    # Lista de espejos disponibles o espejo activo principal
    espejos = LATEST_TRAFFIC_DATA.get("mirrors", [
        LATEST_TRAFFIC_DATA.get("active_mirror", "https://nitter.privacydev.net"),
        "https://nitter.poast.org",
        "https://nitter.lucabased.xyz"
    ])
    
    fuentes = LATEST_TRAFFIC_DATA.get("sources", [])
    
    if not fuentes:
        print("⚠️ No hay fuentes registradas en datos.py para ejecutar.")
        return get_current_report_text()

    exito_extraccion = False

    for fuente in fuentes:
        nombre = fuente.get("name")
        path_fuente = fuente.get("url") # Ruta o usuario objetivo (ej: /transitomedellin)
        
        # Intentar conectar rotando por los espejos disponibles
        for mirror in espejos:
            url_completa = f"{mirror.rstrip('/')}{path_fuente}"
            print(f"🔍 Consultando [{nombre}] en espejo: {url_completa}...")
            
            try:
                response = requests.get(url_completa, headers=HEADERS, timeout=8)
                
                # Verificar si respondió correctamente sin bloqueos (403, 429, 503)
                if response.status_code == 200:
                    print(f"✅ Éxito con {nombre} usando {mirror}")
                    # Aquí puedes parsear el contenido HTML de response.text si lo requieres
                    exito_extraccion = True
                    break
                else:
                    print(f"⚠️ Espejo {mirror} respondió con estado {response.status_code}. Probando siguiente...")
            except requests.exceptions.RequestException as e:
                print(f"❌ Fallo de conexión con {mirror} para {nombre}: {e}")
        
        if exito_extraccion:
            break # Si al menos una fuente responde bien en esta pasada, continuamos

    # Retorna el texto formateado listo para Telegram
    return get_current_report_text()

if __name__ == "__main__":
    resultado = ejecutar_extraccion_desde_fuentes()
    print("\n--- REPORTE OBTENIDO ---")
    print(resultado)
