Aurora Discord bot whit AI and TTS for voice chanelsç

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

he creado a aurora con el proposito de añadirle un poco de actividad y diversion a mis servidores de discord, para que mis amigos y demas miembros
del servidor puedan interactuar con el bot de forma que logre crear un ambiente sociable con aurora, aurora tiene la capacidad de tener personas con mas carisma que otros,
por ejemplo: con algunos usuarios se mostro mas calida y juguetona, mientras que con otros se mostro mas seria y directa, esto debido a interaciones buenas como malas en su face de interacion.

Aurora pose varios comandos para manejar su funciones los cuales son: 

!unirse:

<img width="469" height="151" alt="image" src="https://github.com/user-attachments/assets/94ed887f-e425-4fa9-9efe-a3e4982051ed" />

al instante de ejecutar este comando Aurora se unira o se movera a el canal de voz donde el usuario que ejecuto el comando este y empezara a escuchar para empezar a socializar
esta opcion se puede desahabilitar, o simplemente ensordeciendo a aurora por un administrador del servidor de discord

<img width="281" height="40" alt="image" src="https://github.com/user-attachments/assets/e096da2f-b21b-4e8a-9a38-9ab250a9de14" />

En caso de que el usuario no se encuentre en un canal de voz Aurora mandara el siguiente mensaje:

<img width="462" height="67" alt="image" src="https://github.com/user-attachments/assets/5dc7bf3b-d0a5-4fc1-a818-9dec1ddca408" />

Diciendole al usuario que primedo debe unirse a un canal de voz para el bot poder unirse

!salir: 

<img width="523" height="147" alt="image" src="https://github.com/user-attachments/assets/60544c35-197a-4cd8-a32b-4163517caa9c" />

al ejecutar este comando Aurora se desconectara del chat de voz instantaneamente.

!say: 

<img width="892" height="143" alt="image" src="https://github.com/user-attachments/assets/8274f056-f598-4119-b9bf-91e5cb0dc1ef" />

Este comando le permite al usuario hablar con Aurora mediante texto, el mensaje enviado se procesa con la IA local (Ollama) y la respuesta
se reproduce por voz usando Piper TTS. En pocas palabras el usuario le escribe a aurora por texto y aurora responde por voz


<img width="303" height="92" alt="image" src="https://github.com/user-attachments/assets/3f0c9fe4-7ccd-4e9c-8835-e552dd9e87fe" />







--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Hice a aurora con un sistema modular para poder configurarla y personalizarla a gusto, en la linea 14 del archivo config.py podra encontrar una sesion dedicada al creador o padre de aurora,
esta persona tendra 10 de carisma con aurora (puntuacion maxima) y aurora se tornara mucho mas amigable

Aurora es un asistente de voz con inteligencia artificial añadida para Discord con las siguientes caracteristicas:

- Whisper (speech-to-text)
- Ollama (IA local)
- Piper TTS (voz offline)
- Conversación en tiempo real

Tecnologías:

- Python
- discord.py
- Whisper
- Piper
- Ollama
- FFmpeg

Instalación:
ejecute the next code for install all requirements:

  pip install -r requirements.txt

Ejecute the command for start the bot:

python bot.py

