import discord
from typing import Union
from discord.ext import commands
from lib.scrim_sqlite import ScrimDebugChannels, ScrimUserData
from lib.obj.scrim_user import ScrimUser

def is_owner(user: Union[discord.User, discord.Member, int]) -> bool:
    if isinstance(user, discord.User) or isinstance(user, discord.Member):
        user = user.id
    return user == 234874025921347587

class ScrimDebugCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.debug_channels = ScrimDebugChannels.get_debug_channels()
        print(self.debug_channels)

    @commands.command(name="setsweetid")
    async def connect_sweet_id(self, ctx: discord.ApplicationContext, discord_id: int, sweet_id: str):
        print("Command called!")
        print(ctx)
        if not is_owner(ctx.author):
            print("Not owner!")
            return
        # If not in a debug channel, ignore
        if ctx.channel.id not in self.debug_channels:
            print(ctx.channel.id)
            print("Not in debug channel!")
            return
        # Delete the original message
        discord_user = await self.bot.fetch_user(discord_id)
        if discord_user is None:
            await ctx.send(f"Could not find user with Discord ID: `{discord_id}`", reply=True)
            return
        user: ScrimUser = ScrimUserData.get_user_by_discord_id(discord_id)
        if user is None:
            ScrimUserData.insert_user_from_discord(discord_id)
            user = ScrimUserData.get_user_by_discord_id(discord_id)
        ScrimUserData.connect_sweet_to_id(user.scrim_id, sweet_id)
        await ctx.send(f"Connected Sweet ID: `{sweet_id}` to Discord ID `{discord_id}`", reply=True)