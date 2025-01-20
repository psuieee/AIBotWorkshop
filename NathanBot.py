import discord
#import elevenlabs
import soundfile
import io
import time
import asyncio
#from elevenlabslib import *
#import elevenlabs
import json
import os
import requests
#from elevenlabslib.helpers import *
from discord import FFmpegPCMAudio
import openai
from datetime import date
from elevenlabs import play, save
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

openAIToken = ""
ElevenLabsToken = ""
discordToken = ''

openai.api_key = openAIToken

Elevenclient = ElevenLabs(
  api_key=ElevenLabsToken, 
)

intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True

today = date.today()

client = discord.Client(intents=intents)
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Scamming Students'))
#self.activity = discord.Activity(type=discord.ActivityType.watching, name="you")


@client.event
async def on_message(message):
    if message.author != client.user:
        
            


        if message.content.startswith('Pudi'): 

            
            
            # Check that the message is not from the bot itself
            if message.author == client.user:
                return


            if 'say' in message.content: #All of this is for a 'Pudi say xxx' command, which gets the bot to just say 'xxx'
                # Check that the message is in a voice channel
                if not message.author.voice:
                    await message.channel.send('Join a voice channel')
                    return

                try:
                    # Extract the text and desired voice from the message content
                    parts = message.content.split('"', maxsplit=2)
                    whatToSay = parts[1]

                except Exception:
                    await message.channel.send('You need a quotation mark so I know WHAT to say')
                    return


                try:
                    print(whatToSay)
                    audio = Elevenclient.generate(
                        text=whatToSay,
                        voice="Pudi"
                    )
                    save(audio, "Pudi.wav")


                    #audio_data = await elevenlabs_client.text_to_speech(text, voice)
                except Exception as e:
                    await message.channel.send(f'Error generating audio: {e}')
                    return
                
                # Play the audio file in the voice channel
                voice_channel = message.author.voice.channel
                voice_client = await voice_channel.connect()
                #discord.FFmpegPCMAudio(sound)
                

                player = voice_client.play( discord.FFmpegPCMAudio("Pudi.wav"))

                while voice_client.is_playing(): #Checks if voice is playing
                        await asyncio.sleep(1) #While it's playing it sleeps for 1 second
                else:
                    await asyncio.sleep(15) #If it's not playing it waits 15 seconds
                    while voice_client.is_playing(): #and checks once again if the bot is not playing
                        break #if it's playing it breaks
                    else:
                        await voice_client.disconnect() #if not it disconnects

            else: #If not telling the bot to say something specific, it's assumed you are talking to the bot, so it will form a response and say it in TTS if you are in a vc channel
                text = message.content
                messages = [


                {"role": "system", "content": "You are Neeli Bennapudi, president of the Pennsylvania State University. You LOVE money, and love getting your students to pay tuition to help you make even more money."},
                {"role": "user", "content": text}



                ]

                response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
                )

                result = ''
                for choice in response.choices:
                    result += choice.message.content
                resultList = [result]
                x = 0
                resultLen = len(result)
                if resultLen > 1999:
                    resultList = []
                    while resultLen > 0:
                        resultList.append(result[:1999])
                        result = result[1999:]
                        resultLen = len(result)
                        x += 1

                if message.author.voice:
                    audio = Elevenclient.generate(
                        text=result,
                        voice="Pudi",
                        model="eleven_flash_v2_5",
                        voice_settings=VoiceSettings(
                            stability=0.42,
                            similarity_boost=0.88,
                            style=0.36,
                            use_speaker_boost=True,
                        ),
                    )
                    save(audio, "Pudi.wav") #Saves generated audio file, so it can be played back in a little

                        
                     # Play the audio file in the voice channel
                    voice_channel = message.author.voice.channel
                    voice_client = await voice_channel.connect()
                    #discord.FFmpegPCMAudio(sound)
                        

                    player = voice_client.play( discord.FFmpegPCMAudio("Pudi.wav"))

                    while voice_client.is_playing(): #Checks if voice is playing
                            await asyncio.sleep(1) #While it's playing it sleeps for 1 second
                    else:
                        await asyncio.sleep(15) #If it's not playing it waits 15 seconds
                        while voice_client.is_playing(): #and checks once again if the bot is not playing
                            break #if it's playing it breaks
                        else:
                            await voice_client.disconnect() #if not it disconnects
                        


                for z in resultList:
                    await message.channel.send(z)
                return
            




        


client.run(discordToken)