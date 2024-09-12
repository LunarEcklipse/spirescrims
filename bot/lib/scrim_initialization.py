import discord, uuid
from datetime import datetime, timedelta
from discord.ext import commands
from lib.scrim_sqlite import ScrimDebugChannels, ScrimsData
from lib.obj.scrim import Scrim
from lib.obj.scrim_format import ScrimFormat
from lib.scrim_datetime import DiscordDatestring

class ScrimInitializer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.debug_channels = ScrimDebugChannels.get_debug_channels()

    @commands.command(name="startscrim")
    async def start_scrim(self, ctx: discord.ApplicationContext, format: str, time: str):
        # If not in a debug channel, ignore
        if ctx.channel.id not in self.debug_channels:
            return
        # Create the scrimscrim_format = None
        match format.lower():
            case "solo":
                scrim_format = ScrimFormat.SOLO
            case "duo":
                scrim_format = ScrimFormat.DUO
            case "trio":
                scrim_format = ScrimFormat.TRIO
            case "custom":
                scrim_format = ScrimFormat.CUSTOM
            case _:
                await ctx.send("Invalid format. Valid formats are: `solo`, `duo`, `trio`, `custom`", reference=ctx.message)
                return
        if DiscordDatestring.is_valid_discord_timestamp(time):
            time = DiscordDatestring.get_datetime_from_discord_timestamp(time)
        else:
            await ctx.send("Invalid time format. Please use a valid Discord timestamp.", reference=ctx.message)
        # Check to see if the scrim start time is before the current time.
        if time < datetime.now(datetime.UTC):
            await ctx.send("Scrim start time cannot be before current time.", reference=ctx.message)
            return
        # Check to see if the scrim begins less than an hour from now.
        if time - datetime.now(datetime.UTC) < timedelta(hours=1):
            await ctx.send("Scrim start time must be at least 1 hour from now.", reference=ctx.message)
            return
        # Create a new scrim
        checkin_start_time: datetime = None
        if time - datetime.now(datetime.UTC) < timedelta(hours=24):
            checkin_start_time = time
        else:
            checkin_start_time = time - timedelta(hours=24)
        # Checkin end time is 1 hour before scrim.
        checkin_end_time: datetime = time - timedelta(hours=1)
        scrim: Scrim = Scrim(str(uuid.uuid4()), scrim_format, time, time - timedelta(hours=24), time - timedelta(hours=1))
        # Insert the scrim into the database
        scrim.insert_scrim()

        
    @commands.command(name="startweeklyscrim")
    async def start_scrim_weekly(self, ctx: discord.ApplicationContext, format: str, time: str):
        pass