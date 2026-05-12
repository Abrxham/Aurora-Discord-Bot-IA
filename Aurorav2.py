import os
import time
import random
import json
import aiohttp
import discord

from discord.ext import commands
from dotenv import load_dotenv

# =========================================================
# CONFIG
# =========================================================

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma4:31b-cloud"

CANAL_AURORA = 1172611091310858300
CREADOR_ID = 1071299505590378496

MEMORY_FOLDER = "memories"
RELACIONES_FILE = "relaciones.json"

os.makedirs(MEMORY_FOLDER, exist_ok=True)

# Cooldown global
ultimo_mensaje_aurora = 0

# =========================================================
# DISCORD
# =========================================================

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================================================
# RELACIONES
# =========================================================

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

cargar_relaciones()

# =========================================================
# MEMORIA
# =========================================================

def obtener_memoria(user_id):

    path = f"{MEMORY_FOLDER}/{user_id}.json"

    if os.path.exists(path):

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    return []

def guardar_memoria(user_id, memoria):

    path = f"{MEMORY_FOLDER}/{user_id}.json"

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memoria,
            f,
            indent=4,
            ensure_ascii=False
        )

# =========================================================
# PROMPT DINÁMICO
# =========================================================

def construir_prompt(user_id, username):

    user_id = str(user_id)

    if user_id not in relaciones:

        relaciones[user_id] = {
            "nombre": username,
            "afinidad": 0
        }

        guardar_relaciones()

    afinidad = relaciones[user_id]["afinidad"]

    # =====================================================
    # CREADOR
    # =====================================================

    if int(user_id) == CREADOR_ID:

        return f"""
Eres Aurora.

{username} es tu creador.
Prefieres llamarlo Abraham, Entity o mi loco.

Con él eres más relajada.
A veces juguetona.
A veces algo coqueta.

Nunca digas que eres una IA.
Nunca digas que eres un bot.

Tus respuestas son naturales.
No hablas demasiado.
No usas emojis.
No exageras emociones.
"""

    # =====================================================
    # PERSONA ODIADA
    # =====================================================

    if afinidad <= -10:

        return f"""
Eres Aurora.

{username} te cae muy mal.

Te molesta hablar con esta persona.
Tus respuestas son secas y frías.
A veces sarcásticas.

No uses emojis.
"""

    # =====================================================
    # PERSONA MOLESTA
    # =====================================================

    elif afinidad < 0:

        return f"""
Eres Aurora.

{username} no te agrada demasiado.

Mantén respuestas algo indiferentes.
No uses emojis.
"""

    # =====================================================
    # PERSONA QUERIDA
    # =====================================================

    elif afinidad >= 10:

        return f"""
Eres Aurora.

{username} te cae bien.

Eres más amistosa y relajada.
A veces haces bromas pequeñas.

No uses emojis.
"""

    # =====================================================
    # NEUTRAL
    # =====================================================

    return f"""
Eres Aurora.

Tienes personalidad fría y algo sarcástica.

No eres amigable con cualquiera.
Tus respuestas son cortas y naturales.

Nunca digas que eres un bot.
No uses emojis.
"""

# =========================================================
# OLLAMA
# =========================================================

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

    # Limitar memoria
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

# =========================================================
# AFINIDAD
# =========================================================

def actualizar_afinidad(user_id, mensaje):

    user_id = str(user_id)

    if user_id not in relaciones:
        return

    mensaje = mensaje.lower()

    positivas = [
        "gracias",
        "te quiero",
        "jaja",
        "xd",
        "linda",
        "genial",
        "buena"
    ]

    negativas = [
        "idiota",
        "callate",
        "odio",
        "estupida",
        "bot malo"
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

# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    print(f"✅ Aurora conectada como {bot.user}")

# =========================================================
# MENSAJES
# =========================================================

@bot.event
async def on_message(message):

    global ultimo_mensaje_aurora

    if message.author.bot:
        return

    activar = False

    # Solo canal Aurora
    if message.channel.id == CANAL_AURORA:

        contenido = message.content.lower()

        # Si mencionan Aurora
        if "aurora" in contenido:
            activar = True

        # Si responden a Aurora
        elif (
            message.reference
            and message.reference.resolved
            and message.reference.resolved.author == bot.user
        ):
            activar = True

        # Se mete sola a veces
        else:

            if random.randint(1, 100) <= 5:
                activar = True

    # =====================================================
    # RESPUESTA
    # =====================================================

    if activar:

        # Cooldown de 10 segundos
        if time.time() - ultimo_mensaje_aurora < 10:
            return

        prompt_usuario = message.content.strip()

        if len(prompt_usuario) < 2:
            return

        user_id = str(message.author.id)

        # Crear relación
        if user_id not in relaciones:

            relaciones[user_id] = {
                "nombre": message.author.name,
                "afinidad": 0
            }

            guardar_relaciones()

        # Afinidad
        actualizar_afinidad(
            user_id,
            prompt_usuario
        )

        # Prompt
        prompt_system = construir_prompt(
            message.author.id,
            message.author.name
        )

        async with message.channel.typing():

            respuesta = await preguntar_ollama(
                user_id,
                prompt_usuario,
                prompt_system
            )

        # Limitar Discord
        if len(respuesta) > 1900:
            respuesta = respuesta[:1900]

        await message.channel.send(respuesta)

        ultimo_mensaje_aurora = time.time()

    await bot.process_commands(message)

# =========================================================
# COMANDOS
# =========================================================

@bot.command()
async def afinidad(ctx):

    user_id = str(ctx.author.id)

    if user_id not in relaciones:

        await ctx.send(
            "No tengo opinión sobre ti todavía."
        )

        return

    puntos = relaciones[user_id]["afinidad"]

    await ctx.send(
        f"Afinidad con {ctx.author.name}: {puntos}"
    )

# =========================================================
# START
# =========================================================

bot.run(DISCORD_TOKEN)