# AIBotWorkshop
Project 1 of Spring 2025.

# Requirements
This workshop creates a Discord bot. You must have a Discord account to create a bot.
https://discord.com

The FFmpeg executable must be in your path environment variable. 
https://ffmpeg.org/download.html

Running this code requires Python.
https://www.python.org/

If you are using Python 3.13 or newer, you will also have to install the `audioop.lts` dependency. This is included in `requirements.txt` for your convenience.

# Setup Instructions

1. Download the repository
2. Create a `config.py` file to hold the following tokens:
   - openAI_token
   - elevenLabs_token
   - discord_token
OPTIONAL 3-5:
3. Create a new virtual environment using `py -m venv .venv`
4. Start your virtual environment. If using powershell, execute `.\.venv\Scripts\Activate.ps1`
5. Install requirements using `pip install -r .\requirements.txt`
6. Run the program using `py main.py`

Read more about virtual environments [here](https://www.geeksforgeeks.org/python-virtual-environment/).