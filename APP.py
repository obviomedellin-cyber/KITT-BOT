import os
from flask import Flask
from datos import BASE_DATOS_AZULES, VALLE_ABURRA

app = Flask(__name__)

PORT = int(os.environ.get("PORT", "10000"))

@app.route("/")
def home():
    total_fuentes = len(BASE_DATOS_AZULES)
    total_valle = len(VALLE_ABURRA)
    return f"KITT-BOT is online and operational! Fuentes cargadas: {total_fuentes} | Filtros Valle: {total_valle}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
    
