import discord
from discord import guild_only
from discord.ext import commands
from lib.scrim_sqlite import ScrimUserData, ScrimTeams

class ScrimTeamManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Create command group team
    team_commands = discord.SlashCommandGroup(name="team", help="Commands for managing scrim teams.")

    @team_commands.command(name="list", description="List all scrim teams you are in.")
    @guild_only()
    async def list_teams(self, ctx: discord.ApplicationContext):
        guild_id = ctx.guild.id
        scrim_user = ScrimUserData.get_user_by_discord_id(ctx.author)
        if scrim_user is None:
            ScrimUserData.insert_user_from_discord(ctx.author, ctx.author)
            ctx.respond("You are not part of any teams.", ephemeral=True)
            return 
        ctx.respond("You've discovered a WIP feature! This isn't quite implemented yet, so not much is happening.", ephemeral=True)

    @team_commands.command(name="create", description="Create a new scrim team.")
    @guild_only()
    async def create_team(self, ctx: discord.ApplicationContext, team_name: discord.Option(str, "The name of the team.", required=True), team_member_1: discord.Option(discord.Member, "Your first teammate.", required=True), team_member_2: discord.Option(discord.Member, "Your second teammate.", required=False)): # type: ignore
        ctx.respond("You've discovered a WIP feature! This isn't quite implemented yet, so not much is happening.", ephemeral=True)
    
    team_edit = team_commands.create_subgroup("edit", "Edit an existing scrim team. You must own the team to edit it.")

    @team_edit.command(name="name", description="Change the name of the team.")
    @guild_only()
    async def edit_name(self, ctx: discord.ApplicationContext, team_name: discord.Option(str, "The new name of the team.", required=True)): #type: ignore
        ctx.respond("You've discovered a WIP feature! This isn't quite implemented yet, so not much is happening.", ephemeral=True)

    
    @team_edit.command(name="add", description="Add a member to the team.")
    @guild_only()
    async def add_member(self, ctx: discord.ApplicationContext, member: discord.Option(discord.Member, "The member to add to the team.", required=True)): #type: ignore
        ctx.respond("You've discovered a WIP feature! This isn't quite implemented yet, so not much is happening.", ephemeral=True)

    @team_edit.command(name="remove", description="Remove a member from the team.")
    @guild_only()
    async def remove_member(self, ctx: discord.ApplicationContext, member: discord.Option(discord.Member, "The member to remove from the team.", required=True)): #type: ignore
        ctx.respond("You've discovered a WIP feature! This isn't quite implemented yet, so not much is happening.", ephemeral=True)

    @team_edit.command(name="owner", description="Transfer ownership of the team.")
    @guild_only()
    async def transfer_ownership(self, ctx: discord.ApplicationContext, new_owner: discord.Option(discord.Member, "The new owner of the team.", required=True)): #type: ignore
        ctx.respond("You've discovered a WIP feature! This isn't quite implemented yet, so not much is happening.", ephemeral=True)

    @team_commands.command(name="delete", description="Delete a scrim team. You must own the team to delete it.")
    @guild_only()
    async def delete_team(self, ctx: discord.ApplicationContext):
        ctx.respond("You've discovered a WIP feature! This isn't quite implemented yet, so not much is happening.", ephemeral=True)

    # COMMANDS LIST:
    # # create - Create a new scrim team
    # # edit - Edit an existing scrim team
    # # delete - Delete an existing scrim team
    # # list - List all scrim teams a user is in