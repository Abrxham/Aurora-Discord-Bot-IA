import aiohttp

from config import OLLAMA_URL
from config import MODEL_NAME

from memory import obtener_memoria
from memory import guardar_memoria


async def preguntar_ollama(
    user_id,
    mensaje,
    prompt_system
):

    memoria = obtener_memoria(user_id)

    memoria.append({
        "role": "user",
        "content": mensaje
    })

    memoria = memoria[-20:]

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": prompt_system
            }
        ] + memoria,
        "stream": False
    }

    try:

        async with aiohttp.ClientSession() as session:

            async with session.post(
                OLLAMA_URL,
                json=payload
            ) as resp:

                data = await resp.json()

                respuesta = data["message"]["content"]

    except Exception as e:

        return f"Error conectando con Ollama: {e}"

    memoria.append({
        "role": "assistant",
        "content": respuesta
    })

    guardar_memoria(user_id, memoria)

    return respuesta