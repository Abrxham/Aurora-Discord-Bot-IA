import os
import json

from config import MEMORY_FOLDER

os.makedirs(MEMORY_FOLDER, exist_ok=True)


def obtener_memoria(user_id):

    path = f"{MEMORY_FOLDER}/{user_id}.json"

    if os.path.exists(path):

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    return []


def guardar_memoria(user_id, memoria):

    path = f"{MEMORY_FOLDER}/{user_id}.json"

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            memoria,
            f,
            indent=4,
            ensure_ascii=False
        )