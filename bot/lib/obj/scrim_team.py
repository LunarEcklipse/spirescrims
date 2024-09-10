import discord
from typing import List
from lib.obj.scrim_user import ScrimUser

class ScrimTeam:
    team_id: str
    name: str
    guild: discord.Guild
    team_owner: ScrimUser
    team_members: List[ScrimUser]

    def __init__(self, team_id: str, name: str, guild: discord.Guild, team_owner: ScrimUser, team_members: List[ScrimUser]):
        self.team_id = team_id
        self.name = name
        self.guild = guild
        self.team_owner = team_owner
        self.team_members = team_members

    def calculate_group_mmr(self) -> int:
        '''
        Calculate the MMR of the team.
        '''
        for member in self.team_members:
            if member.mmr is None: # If none, the member's MMR is assumed to be 1500.
                member.mmr = 1500
        return sum([member.mmr for member in self.team_members]) // len(self.team_members)
    
    

