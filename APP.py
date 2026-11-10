import os
import math
from datetime import datetime, timedelta
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters

TOKEN_DE_TELEGRAM = os.environ.get("TELEGRAM_TOKEN", "9084832898:AAGQCqGvBrtNRy9kQ34QnLlrSYUUEBsG7x8")
PORT = int(os.environ.get("PORT", "10000"))

app = Flask(__name__)

class MINIKITLogic:
    def __init__(self):
        self.vehiculo = {"lat": 6.2442, "lon": -75.5736}
        self.reportes = [
            {
                "zona": "Medellín (El Poblado - Las Palmas)",
                "lat": 6.2090, "lon": -75.5670
          }
        ]
        
