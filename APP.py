import os
import math
from datetime import datetime, timedelta
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler

TOKEN_DE_TELEGRAM = os.environ.get("TELEGRAM_TOKEN", "908432898:AAGQ...")
PORT = int(os.environ.get("PORT", "10000"))

app = Flask(__name__)

class KITT:
    def __init__(self):
        self.vehiculo = {"lat": 6.2442, "lon": -75.5670}
        self.reportes = []
    
    def agregar_reporte(self, zona, lat, lon):
        self.reportes.append({"zona": zona, "lat": lat, "lon": lon})
        
        
    

        
        


        
