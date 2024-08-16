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

scrims_version: str = "1.0.0"

intents = discord.Intents.all()

bot = discord.Bot(intents=intents)

# Initialize the ScrimReader cog
bot.add_cog(scrim_reader.ScrimReader(bot))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

bot.run(os.getenv('DISCORD_BOT_TOKEN')) # Get the token from the .env file