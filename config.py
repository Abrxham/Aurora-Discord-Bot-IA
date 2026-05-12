import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma4:31b-cloud"

CANALES_AURORA = [ 
    1172611091310858300, 
    1294055332284338237
    ]
CREADOR_ID = 1071299505590378496

MEMORY_FOLDER = "data/memories"
RELACIONES_FILE = "data/relaciones.json"