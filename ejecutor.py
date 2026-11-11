# ejecutor.py
# Módulo especializado en procesar y ejecutar la extracción de tráfico 
# utilizando la base de datos de fuentes almacenada en datos.py.

import requests
from datos import LATEST_TRAFFIC_DATA, get_current_report_text

def ejecutar_extraccion_desde_fuentes():
    """
    Lee las fuentes y espejos configurados en datos.py, realiza la consulta activa
    y actualiza/genera los reportes viales bajo demanda.
    """
    print("🚦 [Kitt] Iniciando ejecución de fuentes viales...")
    
    # Obtenemos el espejo activo y las fuentes desde datos.py
    espejo_activo = LATEST_TRAFFIC_DATA.get("active_mirror", "https://nitter.privacydev.net")
    fuentes = LATEST_TRAFFIC_DATA.get("sources", [])
    
    if not fuentes:
        print("⚠️ No hay fuentes registradas en datos.py para ejecutar.")
        return False

    for fuente in fuentes:
        nombre = fuente.get("name")
        url_base = fuente.get("url")
        print(f"🔍 Consultando fuente: {nombre} en {url_base}...")
        
        try:
            # Petición HTTP al espejo o plataforma configurada
            response = requests.get(url_base, timeout=10)
            if response.status_code == 200:
                print(f"✅ Conexión exitosa con la fuente: {nombre}")
            else:
                print(f"⚠️ La fuente {nombre} respondió con estado: {response.status_code}")
        except Exception as e:
            print(f"❌ Error al conectar con {nombre}: {e}")

    # Retorna el texto formateado listo para ser enviado por Telegram cuando se solicite la 'P'
    return get_current_report_text()

if __name__ == "__main__":
    resultado = ejecutar_extraccion_desde_fuentes()
    print("\n--- REPORTE OBTENIDO ---")
    print(resultado)
    
