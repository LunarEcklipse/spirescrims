import discord
from typing import Union, List
from discord.ext import commands, tasks
from lib.scrim_sqlite import ScrimsData, ScrimCheckinData
from lib.obj.scrim import Scrim

class ScrimCheckin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checkin_channels = ScrimCheckinData.get_check_in_channels()
        self.checkin_loop.start()

    async def get_guild_checkin_channels(self, guild: Union[discord.Guild, int]) -> List[discord.TextChannel]:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        checkin_channels = ScrimsData.get_checkin_channels(guild_id)
        return [self.bot.get_channel(channel_id) for channel_id in checkin_channels]

    @tasks.loop(seconds=60)
    async def checkin_loop(self):
        # Iterate through all active scrims and get their checkin times.
        scrims: List[Scrim] = ScrimsData.get_active_scrims()
        for scrim in scrims:
            if scrim.is_checkin_active():
                checkin_time = scrim
                checkin_channels = ScrimCheckinData.get_guild_checkin_channels(scrim.scrim_guild)
                has_start_been_sent: bool = ScrimCheckinData.get_checkin_channel_start_message_sent(scrim.scrim_id)
                if not has_start_been_sent:
                    for channel in checkin_channels:
                        pass # TODO: Add a checkin message here to send.
            else:
                checkin_channels = ScrimCheckinData.get_guild_checkin_channels(scrim.scrim_guild)
                has_end_been_sent: bool = ScrimCheckinData.get_checkin_channel_end_message_sent(scrim.scrim_id)
                if not has_end_been_sent:
                    for channel in checkin_channels:
                        pass # TODO: Send the checkin end message here.
                    
                pass # TODO: Implement this
            
