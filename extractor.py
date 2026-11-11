import requests
import json
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Lista modular de espejos Nitter aislada
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.cz"
]

def extract_latest_reports(account_name: str = "ControlVialMed", max_tweets: int = 5):
    """
    Script independiente para consultar espejos Nitter y extraer reportes viales limpios.
    Funciona como un módulo externo separado del webhook principal (app.py).
    """
    reports = []
    
    for instance in NITTER_INSTANCES:
        url = f"{instance}/{account_name}"
        try:
            logger.info(f"Consultando fuente: {url}")
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                timeline_items = soup.find_all('div', class_='timeline-item')
                
                for item in timeline_items[:max_tweets]:
                    tweet_content = item.find('div', class_='tweet-content')
                    tweet_date = item.find('span', class_='tweet-date')
                    
                    if tweet_content:
                        text = tweet_content.get_text(strip=True)
                        date_str = tweet_date.get_text(strip=True) if tweet_date else ""
                        reports.append({
                            "source": instance,
                            "account": account_name,
                            "date": date_str,
                            "report": text
                        })
                
                if reports:
                    logger.info(f"Éxito extrayendo {len(reports)} reportes de {instance}")
                    return {
                        "status": "success",
                        "active_mirror": instance,
                        "total_extracted": len(reports),
                        "reports": reports
                    }
        except Exception as e:
            logger.warning(f"Error consultando {instance}: {e}")
            continue
            
    return {
        "status": "no_data",
        "active_mirror": None,
        "total_extracted": 0,
        "reports": []
    }

if __name__ == "__main__":
    result = extract_latest_reports("ControlVialMed")
    print(json.dumps(result
    
