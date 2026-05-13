import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma4:31b-cloud"

CANALES_AURORA = [ 
    #Aqui añadir las ID de los canales de discord deseados para que aurora pueda escribir
    ]
CREADOR_ID = #ID de la persona que sera creador de aurora o padre

MEMORY_FOLDER = "data/memories"
RELACIONES_FILE = "data/relaciones.json"
