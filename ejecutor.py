# ejecutor.py
# Módulo especializado en extracción, rotación de espejos y análisis flexible de contenido

import requests
from bs4 import BeautifulSoup
from datos import LATEST_TRAFFIC_DATA, get_current_report_text

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def ejecutar_extraccion_desde_fuentes():
    """
    Escanea las fuentes rotando espejos y analiza el HTML de forma flexible 
    para rescatar cualquier reporte disponible.
    """
    print("🚦 [Kitt] Iniciando escaneo flexible de fuentes viales...")
    
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
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 1. Búsqueda principal por clases comunes de tweets
                    items = soup.find_all('div', class_='timeline-item')
                    
                    # 2. Si no encuentra, busca contenedores de texto alternativos
                    if not items:
                        items = soup.find_all('div', class_='tweet-content')
                        
                    # 3. Si aún nada, extrae párrafos generales de la página como respaldo total
                    if not items:
                        items = soup.find_all('p')

                    for item in items[:6]: # Revisar los primeros elementos candidatos
                        texto_limpio = item.get_text(strip=True)
                        # Filtramos textos muy cortos o vacíos para que tengan contenido real
                        if texto_limpio and len(texto_limpio) > 15:
                            # Evitamos repetir reportes idénticos
                            formato_reporte = f"• **{nombre}:** {texto_limpio}"
                            if formato_reporte not in novedades_capturadas:
                                novedades_capturadas.append(formato_reporte)
                    
                    if novedades_capturadas:
                        exito_fuente = True
                        break
                else:
                    print(f"⚠️ Espejo {mirror} retornó estado {response.status_code}")
            except Exception as e:
                print(f"❌ Error consultando espejo {mirror}: {e}")
        
        if exito_fuente and novedades_capturadas:
            break

    if novedades_capturadas:
        reporte_final = "🚨 **REPORTE DE TRÁFICO EN VIVO**:\n\n" + "\n".join(novedades_capturadas[:4])
        return reporte_final
    else:
        return "🟢 SIN NOVEDADES REPORTADAS EN LA RED."

if __name__ == "__main__":
    print(ejecutor_extraccion_desde_fuentes())
                                        
