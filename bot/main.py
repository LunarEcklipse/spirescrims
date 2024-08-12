import os, sys
from dotenv import load_dotenv

absPath: str = os.path.abspath(__file__) # This little chunk makes sure the working directory is correct.
dname: str = os.path.dirname(absPath)
os.chdir(dname)
load_dotenv()

import discord, asyncio, logging
from datetime import datetime, timedelta, timezone
from discord.commands import Option

scrims_version: str = "1.0.0"

