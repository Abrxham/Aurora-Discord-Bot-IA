import os
import asyncio
import tempfile
import wave

import dotenv
import discord
import whisper

from discord.ext import commands
from discord.ext import voice_recv

from ai import preguntar_ollama
from prompts import construir_prompt

dotenv.load_dotenv()

# =========================================================
# CONFIG
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "output.wav"
)

FFMPEG_PATH = os.getenv(
    "FFMPEG_PATH",
    r"C:\ffmpeg\bin\ffmpeg.exe"
)

# =========================================================
# WHISPER
# =========================================================

print("[INFO] Cargando Whisper...")

whisper_model = whisper.load_model("base")

print("[INFO] Whisper listo.")

# =========================================================
# AUDIO SINK
# =========================================================

class AuroraSink(voice_recv.AudioSink):

    def __init__(self, cog, vc, loop):

        super().__init__()

        self.cog = cog
        self.vc = vc
        self.loop = loop

        self.buffers = {}
        self.tasks = {}

    # =====================================================
    # REQUIRED
    # =====================================================

    def wants_opus(self) -> bool:
        return False

    def cleanup(self):
        pass

    # =====================================================
    # WRITE
    # =====================================================

    def write(self, user, data):

        try:

            if user is None:
                return

            if user.bot:
                return

            pcm = data.pcm

            if not pcm:
                return

            uid = user.id

            if uid not in self.buffers:
                self.buffers[uid] = bytearray()

            self.buffers[uid] += pcm

            if uid in self.tasks:
                self.tasks[uid].cancel()

            self.tasks[uid] = self.loop.call_later(
                1.5,
                lambda: asyncio.run_coroutine_threadsafe(
                    self.flush_user(user),
                    self.loop
                )
            )

        except Exception as e:

            print(f"[ERROR write] {e}")

    # =====================================================
    # FLUSH USER
    # =====================================================

    async def flush_user(self, user):

        try:

            uid = user.id

            pcm = bytes(
                self.buffers.pop(uid, b"")
            )

            if len(pcm) < 9600:

                print("[INFO] Audio demasiado corto.")

                return

            print(f"[INFO] Audio recibido de {user.name}")

            await self.cog.procesar_audio(
                user,
                pcm,
                self.vc
            )

        except Exception as e:

            print(f"[ERROR flush_user] {e}")

# =========================================================
# VOZ COG
# =========================================================

class VozCog(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # =====================================================
    # REPRODUCIR AUDIO
    # =====================================================

    async def reproducir_audio(self, vc, audio_path):

        try:

            while vc.is_playing():
                await asyncio.sleep(0.2)

            source = discord.FFmpegPCMAudio(
                audio_path,
                executable=FFMPEG_PATH
            )

            vc.play(
                source,
                after=lambda e: print(
                    f"[ERROR AUDIO] {e}"
                ) if e else print(
                    "[INFO] Audio reproducido"
                )
            )

            while vc.is_playing():
                await asyncio.sleep(0.2)

        except Exception as e:

            print(f"[ERROR reproducir_audio] {e}")

    # =====================================================
    # GENERAR VOZ (PIPER LOCAL)
    # =====================================================

    async def generar_voz(self, vc, texto):

        try:

            print("[INFO] Generando voz local...")

            wav_path = OUTPUT_PATH

            comando = (
                f'echo "{texto}" | '
                r'C:\piper\piper.exe '
                r'--model C:\piper\models\es_AR-daniela-high.onnx '
                f'--output_file "{wav_path}"'
            )

            os.system(comando)

            await self.reproducir_audio(
                vc,
                wav_path
            )

        except Exception as e:

            print(f"[ERROR generar_voz] {e}")

    # =====================================================
    # PROCESAR AUDIO
    # =====================================================

    async def procesar_audio(
        self,
        user,
        pcm_data,
        vc
    ):

        try:

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as tmp:

                tmp_path = tmp.name

                with wave.open(
                    tmp_path,
                    "wb"
                ) as wf:

                    wf.setnchannels(2)
                    wf.setsampwidth(2)
                    wf.setframerate(48000)

                    wf.writeframes(pcm_data)

            print(
                f"[INFO] Transcribiendo audio de {user.name}..."
            )

            result = whisper_model.transcribe(
                tmp_path,
                language="es"
            )

            texto = result["text"].strip()

            os.unlink(tmp_path)

            if not texto:

                print("[INFO] Texto vacío.")

                return

            print(
                f"[INFO] {user.name} dijo: {texto}"
            )

            prompt_system = construir_prompt(
                user.id,
                user.name
            )

            respuesta = await preguntar_ollama(
                str(user.id),
                texto,
                prompt_system
            )

            print(
                f"[INFO] Aurora responde: {respuesta}"
            )

            await self.generar_voz(
                vc,
                respuesta
            )

        except Exception as e:

            print(f"[ERROR procesar_audio] {e}")

    # =====================================================
    # COMANDO SAY
    # =====================================================

    @commands.command()
    async def say(self, ctx, *, texto):

        try:

            vc = discord.utils.get(
                self.bot.voice_clients,
                guild=ctx.guild
            )

            if vc is None:

                await ctx.send(
                    "Primero usa !unirse"
                )

                return

            prompt_system = construir_prompt(
                ctx.author.id,
                ctx.author.name
            )

            respuesta = await preguntar_ollama(
                str(ctx.author.id),
                texto,
                prompt_system
            )

            await ctx.send(
                f"💬 Aurora: {respuesta}"
            )

            await self.generar_voz(
                vc,
                respuesta
            )

        except Exception as e:

            print(f"[ERROR say] {e}")

    # =====================================================
    # COMANDO HABLAR
    # =====================================================

    @commands.command()
    async def hablar(self, ctx, *, texto):

        try:

            vc = discord.utils.get(
                self.bot.voice_clients,
                guild=ctx.guild
            )

            if vc is None:

                await ctx.send(
                    "No estoy conectado."
                )

                return

            await self.generar_voz(
                vc,
                texto
            )

        except Exception as e:

            print(f"[ERROR hablar] {e}")

    # =====================================================
    # UNIRSE
    # =====================================================

    @commands.command()
    async def unirse(self, ctx):

        try:

            if ctx.author.voice is None:

                await ctx.send(
                    "Entra a un canal primero."
                )

                return

            canal = ctx.author.voice.channel

            vc = discord.utils.get(
                self.bot.voice_clients,
                guild=ctx.guild
            )

            if vc is None:

                vc = await canal.connect(
                    cls=voice_recv.VoiceRecvClient
                )

            else:

                await vc.move_to(canal)

            loop = asyncio.get_running_loop()

            sink = AuroraSink(
                self,
                vc,
                loop
            )

            vc.listen(sink)

            print("[INFO] Escuchando usuarios...")

            await ctx.send(
                "🎙️ Escuchando...",
                delete_after=5
            )

        except Exception as e:

            print(f"[ERROR unirse] {e}")

    # =====================================================
    # SALIR
    # =====================================================

    @commands.command()
    async def salir(self, ctx):

        try:

            vc = discord.utils.get(
                self.bot.voice_clients,
                guild=ctx.guild
            )

            if vc:

                vc.stop_listening()

                await vc.disconnect()

                await ctx.send(
                    "👋 Desconectado",
                    delete_after=5
                )

        except Exception as e:

            print(f"[ERROR salir] {e}")

# =========================================================
# SETUP
# =========================================================

async def setup(bot):

    await bot.add_cog(
        VozCog(bot)
    )