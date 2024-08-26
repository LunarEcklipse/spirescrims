from lib.DI_API_Obj.gamemode_counter import GamemodeCounter
from lib.DI_API_Obj.gamemode import GameMode
from typing import Union, Dict, Optional


class GadgetTimelineStats:
    gadget_name: str
    pick_count: GamemodeCounter

    def __init__(self, gadget_name: str, pick_count: GamemodeCounter):
        self.gadget_name = gadget_name
        self.pick_count = pick_count

    def calculate_pick_rate(self, overall_match_count: int, gamemode: Union[GameMode, None] = None) -> float:
        '''Calculates the pick rate for a specific gadget.'''
        matches_played = self.pick_count.get_total() if gamemode is None else self.pick_count.get_gamemode(gamemode)
        if matches_played is None:
            return 0.0
        if overall_match_count == 0:
            return 0.0
        return matches_played / overall_match_count
    
    def get_number_of_picks(self, gamemode: GameMode) -> int:
        '''Returns the number of picks for a specific gamemode.'''
        return self.pick_count.get_gamemode(gamemode)

class GadgetStats:
    gadget_name: str
    lifetime_stats: Optional[GadgetTimelineStats]
    seasonal_stats: Optional[Dict[int, GadgetTimelineStats]]

    def __init__(self, gadget_name: str, lifetime_stats: Optional[GadgetTimelineStats] = None, seasonal_stats: Optional[Dict[int, GadgetTimelineStats]] = {}):
        self.gadget_name = gadget_name
        self.lifetime_stats = lifetime_stats
        self.seasonal_stats = dict.copy(seasonal_stats)