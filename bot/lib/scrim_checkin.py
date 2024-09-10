import discord
from discord.ext import commands, tasks
from lib.scrim_sqlite import ScrimCheckin


class ScrimCheckin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checkin_loop.start()

    @tasks.loop(seconds=60)
    async def checkin_loop(self):
        # Iterate through all active scrims and get their checkin times.
        pass # TODO: Implement this
