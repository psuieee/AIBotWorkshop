import discord
import asyncio
import openai

from datetime import date
from elevenlabs import save, VoiceSettings
from elevenlabs.client import ElevenLabs

# The config.py file holds private Tokens. It should stay on your device only!
from config import openAI_token, elevenLabs_token, discord_token

BOT_ACTIVATION_KEYWORD = 'Pudi'
CHATGPT_SYSTEM_PROMPT = "You are Neeli Bennapudi, president of the Pennsylvania State University. You LOVE money, and love getting your students to pay tuition to help you make even more money. You LOVE asking for more money from students, and encourage them to join the Blue and White society and other alumni groups so they can donate more to the university. When faced with problems, you like to avoid them. Keep responses brief."
THINKING_TEXT = "Hmm..."
global voice_client
voice_client = None

openai.api_key = openAI_token

eleven_client = ElevenLabs(api_key=elevenLabs_token)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)

def gptGenerate(userContent: str): #Generates response using gpt's API
    messages = [
                {"role": "system", "content": CHATGPT_SYSTEM_PROMPT},
                {"role": "user", "content": userContent}
            ]

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    output_text = ''.join(
        choice.message.content for choice in response.choices)
    
    return output_text


async def text_to_speech(text: str, voice_channel: discord.VoiceChannel, invoked_channel: discord.TextChannel, thinking_message: discord.Message | None = None):
    """Performs text to speech on text, playing the output audio in voice_channel.
    
    If thinking_message is None, a new message indicating the bot is thinking will be sent to invoked_channel.

    Args:
        text (str): The text to be converted to speech.
        voice_channel (discord.VoiceChannel): The voice channel where the bot will play the audio.
        invoked_channel (discord.TextChannel): The text channel where the bot will send status messages and text output.
        thinking_message (discord.Message | None, optional): An optional message indicating the bot is thinking. Defaults to None.
    """
    global voice_client

    if thinking_message is None:
        thinking_message = await invoked_channel.send(THINKING_TEXT)

    try:
        audio = eleven_client.generate(
            text=text,
            voice="Pudi",
            model="eleven_flash_v2_5",
            voice_settings=VoiceSettings(
                stability=0.42,
                similarity_boost=0.88,
                style=0.36,
                use_speaker_boost=True,
            ),
        )
        save(audio, BOT_ACTIVATION_KEYWORD + '.wav')

    except Exception as e:
        await thinking_message.edit(content=f'Error generating audio: {e}')
        return

    await thinking_message.edit(content=f"*Speaking in <#{voice_channel.id}>.*")

    if voice_client is None:
    
        voice_client = await voice_channel.connect()
        voice_client.play(discord.FFmpegPCMAudio(BOT_ACTIVATION_KEYWORD + '.wav'))

        # Wait for the audio to finish playing before deleting the thinking message
        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()
        await thinking_message.delete()
    else:
        await invoked_channel.send("I'm already talking! Please wait then try again.")
        return

    voice_client = None

    # Discord limits messages to 2000 characters, so split the output text into
    # multiple messages if needed.
    capped_output_messages = [text[i:i+1999]
                              for i in range(0, len(text), 1999)]
    for msg in capped_output_messages:
        await invoked_channel.send(msg)


@client.event
async def on_ready():
    """
    Used to add a status to the bot. You can set it to whatever you want!
    """
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Buying my fourth mansion!'))


@client.event
async def on_message(message: discord.Message):
    """Handles message processing.
    
    Ignores messages sent by self and those that do not begin with BOT_ACTIVATION_KEYWORD.
    
    If the 2nd word of the sentence is 'say', text to speech will occur.
    Else, a response to the input will be generated before performing TTS.

    Args:
        message (discord.Message): Message object provided by discord.py
    """
    if message.author == client.user:
        return

    if not message.content.lower().startswith(BOT_ACTIVATION_KEYWORD.lower()):
        return
    
    if not message.author.voice:
        await message.channel.send('Join a voice channel')
        return
    


    if not message.author.voice:
        # CASE 1: If user isn't in a VC, bot generate's response and then output's in the text channel.
            output = gptGenerate(message.content)
            await message.channel.send(output)
            return

    elif 'say' == message.content.split()[1]:
        # CASE 2: We 'parrot' the input text using TTS.
        

        start_char = message.content.find('"')
        if start_char == -1 or message.content[-1] != '"':
            await message.channel.send("Hmm, I'm not sure what you want me to say. Try surrounding it in quotes.")
        else:
            await text_to_speech(message.content[start_char+1:-1], message.author.voice.channel, message.channel)

    else:
        # CASE 3: We generate an output before performing TTS, treating the input text as a ChatGPT prompt.
        
        # This provides immediate user feedback while an API call is made to ChatGPT
        thinking_message = await message.channel.send(THINKING_TEXT)

        output_text = gptGenerate(message.content)

        await text_to_speech(output_text, message.author.voice.channel, message.channel, thinking_message)


client.run(discord_token)
