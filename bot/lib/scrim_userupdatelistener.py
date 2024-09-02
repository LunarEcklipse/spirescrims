from typing import Union, List
import discord
from discord.ext import commands
from lib.scrim_sqlite import ScrimUserData

class ScrimUserUpdateListener(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot:
                    continue
                if ScrimUserData.get_user_by_discord_id(member) == None:
                    ScrimUserData.insert_user_from_discord(member)
                ScrimUserData.update_username_by_discord_id(member, member.name)
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        for member in guild.members:
            if member.bot:
                continue
            if ScrimUserData.get_user_by_discord_id(member) == None:
                ScrimUserData.insert_user_from_discord(member)
            ScrimUserData.update_username_by_discord_id(member, member.name)
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return
        if ScrimUserData.get_user_by_discord_id(member) == None:
            ScrimUserData.insert_user_from_discord(member)
        ScrimUserData.update_username_by_discord_id(member, member.name)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.bot:
            return
        if before.name != after.name:
            ScrimUserData.update_username_by_discord_id(after, after.name)

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if before.bot:
            return
        if before.name != after.name:
            ScrimUserData.update_username_by_discord_id(after, after.name)
    
    