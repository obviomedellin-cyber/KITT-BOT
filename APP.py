import os
import requests
from flask import Flask, request
from datos import BASE_DATOS_AZULES, VALLE_ABURRA

app = Flask(__name__)

PORT = int(os.environ.get("PORT", "10000"))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "9084832898:AAGQCqGvBrtNRy9kQ34QnLlrSYUUEBsG7x8")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
