# ejecutor.py
# Motor encargado de leer la base de datos de fuentes desde datos.py 
# y ejecutar la extracción de tráfico en tiempo real de forma independiente.

import requests
from datos import LATEST_TRAFFIC_DATA  # Importamos la base de datos de fuentes existente

def ejecutar_extraccion_desde_fuentes():
    """
    Lee las fuentes y espejos configurados en datos.py y realiza la consulta activa.
    """
    print("Iniciando ejecución de fuentes viales...")
    
    # Obtenemos el espejo activo y las fuentes desde datos.py
    espejo_activo = LATEST_TRAFFIC_DATA.get("active_mirror", "https://nitter.privacydev.net")
    fuentes = LATEST_TRAFFIC_DATA.get("sources", [])
    
    if not fuentes:
        print("⚠️ No hay fuentes registradas en datos.py para ejecutar.")
        return False

    for fuente in fuentes:
        nombre = fuente.get("name")
        url_base = fuente.get("url")
        print(f"Consultando fuente: {nombre} en {url_base}...")
        
        try:
            # Petición HTTP al espejo o plataforma configurada en datos.py
            response = requests.get(url_base, timeout=10)
            if response.status_code == 200:
                print(f"✅ Conexión exitosa con la fuente: {nombre}")
                # Aquí puedes agregar la lógica de análisis/parseo de la respuesta
            else:
                print(f"⚠️ La fuente {nombre} respondió con estado: {response.status_code}")
        except Exception as e:
            print(f"❌ Error al conectar con {nombre}: {e}")

    return True

if __name__ == "__main__":
    ejecutar_extraccion_desde_fuentes()
      
