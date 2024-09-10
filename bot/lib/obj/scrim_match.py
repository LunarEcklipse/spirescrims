from typing import Union, List, Dict, Tuple

from lib.obj.scrim_format import ScrimFormat
from lib.obj.scrim_user import ScrimUser
from lib.obj.scrim_team import ScrimTeam
from lib.scrim_mmr_calculation import ScrimMMR

class ScrimMatch:
    format: ScrimFormat
    groups: Union[List[ScrimUser], List[ScrimTeam]]
    winner_score: Union[int, None]

    def calculate_mmr_change_range(self, constant: int = 32) -> Dict[Union[ScrimUser, ScrimTeam], Tuple[int, int]]:
        '''
        Calculate the range of MMR changes for each group in the match.
        '''
        mmr_changes = {}
        for group in self.groups:
            mmr_changes[group] = (ScrimMMR.calculate_maximum_mmr_loss, ScrimMMR.calculate_maximum_mmr_gain)
        return mmr_changes