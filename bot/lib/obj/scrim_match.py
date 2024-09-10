from typing import Union, List, Dict, Tuple

from lib.obj.scrim_format import ScrimFormat
from lib.obj.scrim_user import ScrimUser
from lib.obj.scrim_team import ScrimTeam
from lib.scrim_mmr_calculation import ScrimMMR

class ScrimMatch:
    class MMRChange:
        group: Union[ScrimUser, ScrimTeam]
        max_mmr_loss: int
        max_mmr_gain: int

        def __init__(self, group: Union[ScrimUser, ScrimTeam], max_mmr_loss: int, max_mmr_gain: int) -> None:
            self.group = group
            self.max_mmr_loss = max_mmr_loss
            self.max_mmr_gain = max_mmr_gain

    format: ScrimFormat
    groups: Union[List[ScrimUser], List[ScrimTeam]]
    winner_score: Union[int, None]

    def calculate_mmr_change_range(self, constant: int = 32) -> List['ScrimMatch'.MMRChange]:
        '''
        Calculate the range of MMR changes for each group in the match.
        '''
        mmr_changes = []
        for group in self.groups:
            mmr_changes.append(ScrimMatch.MMRChange(group, ScrimMMR.calculate_maximum_mmr_loss(group, self.groups, constant), ))
        return mmr_changes
    
