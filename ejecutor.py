# ejecutor.py
# Módulo especializado en extracción, rotación de espejos y análisis de contenido (parser)

import requests
from bs4aitan if hasattr(requests, 'bs4') else None # O importar BeautifulSoup si está disponible
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from datos import LATEST_TRAFFIC_DATA, get_current_report_text

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def ejecutar_extraccion_desde_fuentes():
    """
    Escanea las fuentes institucionales rotando espejos y parsea el contenido HTML 
    para extraer novedades viales reales.
    """
    print("🚦 [Kitt] Iniciando escaneo y análisis de fuentes viales...")
    
    espejos = LATEST_TRAFFIC_DATA.get("mirrors", [
        LATEST_TRAFFIC_DATA.get("active_mirror", "https://nitter.privacydev.net"),
        "https://nitter.poast.org",
        "https://nitter.lucabased.xyz"
    ])
    
    fuentes = LATEST_TRAFFIC_DATA.get("sources", [])
    novedades_capturadas = []

    if not fuentes:
        print("⚠️ No hay fuentes registradas en datos.py.")
        return get_current_report_text()

    for fuente in fuentes:
        nombre = fuente.get("name")
        path_fuente = fuente.get("url")
        exito_fuente = False
        
        for mirror in espejos:
            url_completa = f"{mirror.rstrip('/')}{path_fuente}"
            print(f"🔍 Consultando [{nombre}] en: {url_completa}...")
            
            try:
                response = requests.get(url_completa, headers=HEADERS, timeout=8)
                
                if response.status_code == 200:
                    print(f"✅ Conexión exitosa con {nombre} via {mirror}")
                    
                    # Parsear HTML para extraer tweets/reportes
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Estructura típica de Nitter para los items de los tweets
                    items_timeline = soup.find_all('div', class_='timeline-item')
                    
                    if not items_timeline:
                        # Fallback genérico por si cambia la clase del espejo
                        items_timeline = soup.find_all(['p', 'div'], class_='tweet-content')

                    for item in items_timeline[:5]: # Revisar los últimos 5 tweets
                        texto_tweet = item.get_text(strip=True)
                        if texto_tweet and texto_tweet not in novedades_capturadas:
                            novedades_capturadas.append(f"• **{nombre}:** {texto_tweet}")
                    
                    exito_fuente = True
                    break
                else:
                    print(f"⚠️ Espejo {mirror} retornó estado {response.status_code}")
            except Exception as e:
                print(f"❌ Error consultando espejo {mirror}: {e}")
        
        if exito_fuente and novedades_capturadas:
            break # Si ya obtuvimos datos válidos, podemos consolidar

    if novedades_capturadas:
        reporte_final = "🚨 **REPORTE DE TRÁFICO EN VIVO**:\n\n" + "\n".join(novedades_capturadas)
        return reporte_final
    else:
        # Si no hay nada fresco, retorna el estado por defecto sin alterar la estructura
        return "🟢 SIN NOVEDADES REPORTADAS EN LA RED."

if __name__ == "__main__":
    print(ejecutor_extraccion_desde_fuentes())
            
