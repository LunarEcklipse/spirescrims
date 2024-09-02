import os, sys
from typing import Optional
from dotenv import load_dotenv, find_dotenv
from discord.ext import commands

from PIL import Image

absPath: str = os.path.abspath(__file__) # This little chunk makes sure the working directory is correct.
dname: str = os.path.dirname(absPath)
os.chdir(dname)
load_dotenv(find_dotenv())

import discord, asyncio, logging
from datetime import datetime, timedelta, timezone
from discord.commands import Option
import lib.scrim_reader as scrim_reader
import lib.scrim_sysinfo as scrim_sysinfo
import lib.scrim_di_api as scrim_di_api
from lib.scrim_sqlite import ScrimUserData
from lib.obj.scrim_user import ScrimUser
from lib.scrim_logging import scrim_logger
from lib.scrim_playerstats import ScrimPieCharts, ScrimPlots
from lib.DI_API_Obj.gamemode import GameMode

scrims_version: str = "1.0.4"

intents = discord.Intents.all()

bot = discord.Bot(intents=intents)

scrim_logger.info(f"Starting Scrim Helper v{scrims_version}")
# Initialize the ScrimReader cog
if scrim_sysinfo.cpu_is_x86() and not scrim_sysinfo.cpu_supports_avx2():
    scrim_logger.warning("You are using an x86_64 CPU does not support AVX2 instructions, which are required for EasyOCR. OCR Readers will not work.")
else:
    scrim_logger.info("Initializing Reader modules, this may take several minutes...")
    scrim_logger.debug("Initializing ScrimReader Cog...")
    bot.add_cog(scrim_reader.ScrimReader(bot))

@bot.event
async def on_ready():
    scrim_logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})') #type: ignore
    # Iterate through the guilds the bot is in and get their members
    for guild in bot.guilds:
        for member in guild.members:
            if member.bot:
                continue
            # Check if the user is in the database
            if ScrimUserData.get_user_by_discord_id(member) == None:
                # If not, add them to the database
                ScrimUserData.insert_user_from_discord(member)


    api = await scrim_di_api.DeceiveIncAPIClient.initialize(os.getenv("DI_CLIENT_ID"), os.getenv("DI_CLIENT_SECRET")) #type: ignore
    sw = await api.get_user("1jii7052-k048-6392-1kk4-784il9l47khj")
    # im = ScrimPlots.calculate_agent_pickrates_over_seasons(sw)
    # im.save("test.png")

scrim_logger.debug("Starting bot...")
bot.run(os.getenv('DISCORD_BOT_TOKEN')) # Get the token from the .env file