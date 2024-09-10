from typing import Union, List
from lib.obj.scrim_user import ScrimUser
from lib.obj.scrim_team import ScrimTeam

class ScrimGroupResult:
    group: Union[ScrimUser, ScrimTeam]
    placement: int
    total_score: int

    def __init__(self, group: Union[ScrimUser, ScrimTeam], placement: int, total_score: int) -> None:
        self.group = group
        self.placement = placement
        self.total_score = total_score

class ScrimMMR:
    @staticmethod
    def calculate_expected_performance_against_group(group: Union[ScrimUser, ScrimTeam], opposing_group: Union[ScrimUser, ScrimTeam]) -> float:
        '''
        Calculate the expected performance of a group of players against another group of players.
        '''
        group = group.calculate_group_mmr() if type(group) == ScrimTeam else group.mmr
        opposing_group = opposing_group.calculate_group_mmr() if type(opposing_group) == ScrimTeam else opposing_group.mmr
        return 1 / (1 + 10 ** ((opposing_group - group) / 400))
    
    @staticmethod
    def calculate_expected_performance_against_lobby(group: Union[ScrimUser, ScrimTeam], opposing_groups: Union[List[ScrimUser], List[ScrimTeam]]) -> float:
        '''
        Calculate the expected performance of a group of players against a lobby of players.
        '''
        average_opponent_mmr = 0
        for opposing_group in opposing_groups:
            average_opponent_mmr += opposing_group.calculate_group_mmr() if type(opposing_group) == ScrimTeam else opposing_group.mmr
        average_opponent_mmr //= len(opposing_groups)
        group = group.calculate_group_mmr() if type(group) == ScrimTeam else group.mmr
        return 1 / (1 + 10 ** ((average_opponent_mmr - group) / 400))
    
    @staticmethod
    def calculate_mmr_change_against_group(group: Union[ScrimUser, ScrimTeam], match: Union[List[ScrimUser], List[ScrimTeam]], group_score: int, winner_score: int, constant: int = 32) -> float:
        '''
        Calculate the mmr change of a group of players against another group of players based on how they placed.
        '''
        
        expected_performance = ScrimMMR.calculate_expected_performance_against_group(group, match)
        actual_performance = group_score / winner_score
        return constant * (actual_performance - expected_performance)
    
    @staticmethod
    def calculate_new_group_mmr(group: Union[ScrimUser, ScrimTeam], match: Union[List[ScrimUser], List[ScrimTeam]], group_score: int, winner_score: int, constant: int = 32) -> int:
        '''
        Calculate the new MMR of a group of players after a match.
        '''
        current_mmr = group.calculate_group_mmr() if type(group) == ScrimTeam else group.mmr
        return current_mmr + ScrimMMR.calculate_mmr_change_against_group(group, match, group_score, winner_score, constant)
    
    @staticmethod
    def calculate_maximum_mmr_gain(group: Union[ScrimUser, ScrimTeam], match: Union[List[ScrimUser], List[ScrimTeam]], constant: int = 32) -> int:
        '''
        Calculate the maximum MMR a group of players can gain in a match.
        '''
        expected_performance = ScrimMMR.calculate_expected_performance_against_group(group, match)
        return constant * (1 - expected_performance)
    
    @staticmethod
    def calculate_maximum_mmr_loss(group: Union[ScrimUser, ScrimTeam], match: Union[List[ScrimUser], List[ScrimTeam]], constant: int = 32) -> int:
        '''
        Calculate the maximum MMR a group of players can lose in a match.
        '''
        expected_performance = ScrimMMR.calculate_expected_performance_against_group(group, match)
        return constant * (0 - expected_performance)