import time
import random
import logging

import discord
from discord.ext import commands

from voice import VozCog

from config import (
    CANALES_AURORA,
    DISCORD_TOKEN
)

from ai import preguntar_ollama
from prompts import construir_prompt

from affinity import (
    relaciones,
    asegurar_usuario,
    actualizar_afinidad
)

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(level=logging.INFO)

# =========================================================
# OPUS
# =========================================================

# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.messages = True

# =========================================================
# BOT
# =========================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

ultimo_mensaje_aurora = 0

# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():
    print(f"✅ Aurora conectada como {bot.user}")

# =========================================================
# SETUP COG
# =========================================================

@bot.event
async def setup_hook():
    await bot.add_cog(VozCog(bot))
    print("✅ VozCog cargado")

# =========================================================
# MENSAJES
# =========================================================

@bot.event
async def on_message(message):

    global ultimo_mensaje_aurora

    if message.author.bot:
        return

    await bot.process_commands(message)

    activar = False

    if message.channel.id in CANALES_AURORA:

        contenido = message.content.lower()

        if "aurora" in contenido:
            activar = True

        elif (
            message.reference
            and message.reference.resolved
            and message.reference.resolved.author == bot.user
        ):
            activar = True

        else:
            if random.randint(1, 100) <= 10:
                activar = True

    if activar:

        if time.time() - ultimo_mensaje_aurora < 10:
            return

        prompt_usuario = message.content.strip()

        if len(prompt_usuario) < 2:
            return

        if prompt_usuario.startswith("!"):
            return

        user_id = str(message.author.id)

        asegurar_usuario(user_id, message.author.name)
        actualizar_afinidad(user_id, prompt_usuario)

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

        if len(respuesta) > 1900:
            respuesta = respuesta[:1900]

        await message.channel.send(respuesta)

        voz_cog = bot.get_cog("VozCog")

        if voz_cog:
            await voz_cog.speak_auto(message.guild, respuesta)

        ultimo_mensaje_aurora = time.time()

# =========================================================
# AFINIDAD
# =========================================================

@bot.command()
async def afinidad(ctx):

    user_id = str(ctx.author.id)

    if user_id not in relaciones:
        await ctx.send("No tengo opinión sobre ti todavía.")
        return

    puntos = relaciones[user_id]["afinidad"]

    await ctx.send(
        f"Afinidad con {ctx.author.name}: {puntos}"
    )

# =========================================================
# START
# =========================================================

bot.run(DISCORD_TOKEN)