import discord
from typing import Union, List
from discord.ext import commands, tasks
from lib.scrim_sqlite import ScrimsData, ScrimCheckin
from lib.obj.scrim import Scrim

class ScrimCheckin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checkin_loop.start()

    @tasks.loop(seconds=60)
    async def checkin_loop(self):
        # Iterate through all active scrims and get their checkin times.
        scrims: List[Scrim] = ScrimsData.get_active_scrims()
        for scrim in scrims:
            if scrim.is_checkin_active():
                # Check to see if that checkin message has been sent.
                pass # TODO: Implement this
            
