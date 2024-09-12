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

    # Set Sweet ID
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
            await ctx.send(f"Could not find user with Discord ID: `{discord_id}`", reference=ctx.message)
            return
        user: ScrimUser = ScrimUserData.get_user_by_discord_id(discord_id)
        if user is None:
            ScrimUserData.insert_user_from_discord(discord_id)
            user = ScrimUserData.get_user_by_discord_id(discord_id)
        ScrimUserData.connect_sweet_to_id(user.scrim_id, sweet_id)
        await ctx.send(f"Connected Sweet ID: `{sweet_id}` to Discord ID `{discord_id}`", reference=ctx.message)

    # Who is
    @commands.command(name="whois")
    async def whois(self, ctx: discord.ApplicationContext, discord_id: int):
        # If not in a debug channel, ignore
        if ctx.channel.id not in self.debug_channels:
            return
        user: ScrimUser = ScrimUserData.get_user_by_discord_id(discord_id)
        if user is None:
            await ctx.send(f"Could not find user with Discord ID: `{discord_id}`", reference=ctx.message)
            return
        discord_user: Union[discord.User, discord.Member] = await self.bot.fetch_user(discord_id)
        # Construct the embed
        emb = discord.Embed(title=discord_user.name, color=discord.Color.green())
        emb.set_thumbnail(url=discord_user.display_avatar.url)
        emb.add_field(name="Spire Scrims ID", value=user.scrim_id, inline=False)
        if user.sweet_id is not None:
            emb.add_field(name="Sweet ID", value=user.sweet_id, inline=False)
        if user.twitch_id is not None:
            emb.add_field(name="Twitch ID", value=user.twitch_id, inline=False)
        emb.set_footer(text=f"Discord ID: {str(discord_user.id)}")
        await ctx.send(content=None, embed=emb, reference=ctx.message)

    
