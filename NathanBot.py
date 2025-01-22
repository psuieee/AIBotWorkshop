import discord
import asyncio
import openai

from datetime import date
from elevenlabs import save, VoiceSettings
from elevenlabs.client import ElevenLabs

# The config.py file holds private Tokens. It should stay on your device only!
from config import openAI_token, elevenLabs_token, discord_token

BOT_ACTIVATION_KEYWORD = 'Pudi'

openai.api_key = openAI_token

eleven_client = ElevenLabs(api_key=elevenLabs_token)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)


async def parrot(text: str, voice_channel: discord.VoiceChannel) -> str | None:
    try:
        audio = eleven_client.generate(
            text=text,
            voice="Pudi"
        )
        save(audio, "Pudi.wav")
        
    except Exception as e:
        return f'Error generating audio: {e}'

    # Play the audio file in the voice channel
    voice_client = await voice_channel.connect()
    voice_client.play(discord.FFmpegPCMAudio("Pudi.wav"), after=lambda e: asyncio.run_coroutine_threadsafe(voice_client.disconnect(), client.loop))


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Scamming Students'))


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if not message.content.startswith(BOT_ACTIVATION_KEYWORD):
        return

    if 'say' == message.content.split()[1]:
        # Handles 'Pudi say "some message here"', where the bot uses TTS on the contents between the double quotes
        if not message.author.voice:
            await message.channel.send('Join a voice channel')
            return

        try:
            # Extract the text and desired voice from the message content
            parrot_text = message.content.split('"', maxsplit=2)[1]

        except Exception:
            await message.channel.send('You need a quotation mark so I know WHAT to say')
            return

        if parrot_text:
            await parrot(parrot_text, message.author.voice.channel)

    else:  
        # Use GPT to generate a response to the prompt, then repeat it in VC using TTS.
        messages = [
            {"role": "system", "content": "You are Neeli Bennapudi, president of the Pennsylvania State University. You LOVE money, and love getting your students to pay tuition to help you make even more money."},
            {"role": "user", "content": message.content}
        ]

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        output_text = ''.join(choice.message.content for choice in response.choices)
        capped_output_messages = [output_text[i:i+1999] for i in range(0, len(output_text), 1999)]

        if message.author.voice:
            audio = eleven_client.generate(
                text=output_text,
                voice="Pudi",
                model="eleven_flash_v2_5",
                voice_settings=VoiceSettings(
                    stability=0.42,
                    similarity_boost=0.88,
                    style=0.36,
                    use_speaker_boost=True,
                ),
            )
            # Saves generated audio file, so it can be played back in a little
            save(audio, "Pudi.wav")

            # Play the audio file in the voice channel
            voice_client = await message.author.voice.channel.connect()
            voice_client.play(discord.FFmpegPCMAudio("Pudi.wav"), after=lambda e: asyncio.run_coroutine_threadsafe(voice_client.disconnect(), client.loop))

        for msg in capped_output_messages:
            await message.channel.send(msg)
            
        return


client.run(discord_token)
