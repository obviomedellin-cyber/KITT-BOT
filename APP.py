import os
from flask import Flask

app = Flask(__name__)

PORT = int(os.environ.get("PORT", "10000"))
