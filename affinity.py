import os
import json

from config import RELACIONES_FILE

relaciones = {}


def cargar_relaciones():

    global relaciones

    if os.path.exists(RELACIONES_FILE):

        with open(
            RELACIONES_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            relaciones = json.load(f)

    else:
        relaciones = {}



def guardar_relaciones():

    with open(
        RELACIONES_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            relaciones,
            f,
            indent=4,
            ensure_ascii=False
        )



def asegurar_usuario(user_id, username):

    user_id = str(user_id)

    if user_id not in relaciones:

        relaciones[user_id] = {
            "nombre": username,
            "afinidad": 0,
            "mood": "neutral"
        }

        guardar_relaciones()



def actualizar_afinidad(user_id, mensaje):

    user_id = str(user_id)

    if user_id not in relaciones:
        return

    mensaje = mensaje.lower()

    positivas = [
        "gracias",
        "jaja",
        "xd",
        "linda",
        "genial"
    ]

    negativas = [
        "idiota",
        "callate",
        "odio",
        "estupida"
    ]

    for palabra in positivas:

        if palabra in mensaje:
            relaciones[user_id]["afinidad"] += 1

    for palabra in negativas:

        if palabra in mensaje:
            relaciones[user_id]["afinidad"] -= 2

    relaciones[user_id]["afinidad"] = max(
        -20,
        min(20, relaciones[user_id]["afinidad"])
    )

    guardar_relaciones()


cargar_relaciones()