import os, sys
from typing import Optional
from dotenv import load_dotenv, find_dotenv
from discord.ext import commands

from PIL import Image

absPath: str = os.path.abspath(__file__) # This little chunk makes sure the working directory is correct.
dname: str = os.path.dirname(absPath)
os.chdir(dname)
load_dotenv(find_dotenv())

import discord, asyncio, logging, easyocr
from datetime import datetime, timedelta, timezone
from discord.commands import Option
import lib.scrim_reader as scrim_reader
import lib.scrim_sysinfo as scrim_sysinfo
import lib.scrim_di_api as scrim_di_api
from lib.scrim_sqlite import ScrimUserData
from lib.obj.scrim_user import ScrimUser
from lib.scrim_logging import scrim_logger
from lib.scrim_playerstats import ScrimPieCharts, ScrimPlots
from lib.obj.scrim_format import ScrimFormat
from lib.scrim_userupdatelistener import ScrimUserUpdateListener
from lib.scrim_teammanagement import ScrimTeamManager
from lib.obj.scrim_matchgroups import ScrimMatchGroups
from lib.scrim_matchmaking import ScrimMatchmaking

scrims_version: str = "1.0.4"

for i in range(32):
    if i == 14:
        pass
    out = ScrimMatchmaking.calculate_lobby_sizes(i, ScrimFormat.TRIO)
    if isinstance(out, ScrimMatchGroups):
        print(f"Number of Trios: {str(i)} - Lobbies: {out.lobby_sizes} - Waitlist: {out.waitlist_playercount}")
    else:
        print(f"Number of Trios: {str(i)} - Not Enough Trios")

x = input()

intents = discord.Intents.all()

bot = discord.Bot(intents=intents)

scrim_logger.info(f"Starting Scrim Helper v{scrims_version}")
# Initialize the ScrimReader cog
if scrim_sysinfo.cpu_is_x86() and not scrim_sysinfo.cpu_supports_avx2():
    scrim_logger.warning("You are using an x86_64 CPU does not support AVX2 instructions, which are required for EasyOCR. OCR Readers will not work.")
else:
    scrim_logger.info("Initializing Reader modules, this may take several minutes...")
    scrim_logger.debug("Initializing ScrimReader Cog...")
    model_download = easyocr.Reader(['en'], download_enabled=True) # We create this at the very beginning to ensure the model is downloaded. By doing it here we avoid a potential crash if the model isn't downloaded as it will try and complete on multiple threads
    del model_download # Then we delete it to keep memory usage low
    bot.add_cog(scrim_reader.ScrimReader(bot))
scrim_logger.info("Initializing User Update Listeners...")
bot.add_cog(ScrimUserUpdateListener(bot))
scrim_logger.info("Initializing Team Management Cog...")
bot.add_cog(ScrimTeamManager(bot))

@bot.event
async def on_ready():
    scrim_logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})') #type: ignore

    api = await scrim_di_api.DeceiveIncAPIClient.initialize(os.getenv("DI_CLIENT_ID"), os.getenv("DI_CLIENT_SECRET")) #type: ignore
    sw = await api.get_user("1jii7052-k048-6392-1kk4-784il9l47khj")
    # im = ScrimPlots.calculate_agent_pickrates_over_seasons(sw)
    # im.save("test.png")

scrim_logger.debug("Starting bot...")
bot.run(os.getenv('DISCORD_BOT_TOKEN')) # Get the token from the .env file