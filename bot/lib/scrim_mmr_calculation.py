from typing import Union
from lib.obj.scrim_user import ScrimUser
from lib.obj.scrim_team import ScrimTeam

class ScrimMMR:
    @staticmethod
    def calculate_expected_performance(group_1: Union[ScrimUser, ScrimTeam], group_2: Union[ScrimUser, ScrimTeam]) -> float:
        '''
        Calculate the expected performance of a group of players against another group of players.
        '''
        