import os, sys
from dotenv import load_dotenv

absPath: str = os.path.abspath(__file__) # This little chunk makes sure the working directory is correct.
dname: str = os.path.dirname(absPath)
os.chdir(dname)
load_dotenv()

import discord, asyncio, logging
from datetime import datetime, timedelta, timezone
from discord.commands import Option
import lib.scrim_reader as scrim_reader
import lib.scrim_sysinfo as scrim_sysinfo

scrims_version: str = "1.0.0"

intents = discord.Intents.all()

bot = discord.Bot(intents=intents)

# Initialize the ScrimReader cog
if scrim_sysinfo.cpu_is_x86() and not scrim_sysinfo.cpu_supports_avx2():
    RuntimeWarning("You are using an x86_64 CPU does not support AVX2 instructions, which are required for EasyOCR. Disabling Reader...")
else:
    bot.add_cog(scrim_reader.ScrimReader(bot))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

bot.run(os.getenv('DISCORD_BOT_TOKEN')) # Get the token from the .env file