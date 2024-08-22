from lib.DI_API_Obj.gamemode_counter import GamemodeCounter
from typing import Union, Dict, Optional

class GadgetTimelineStats:
    gadget_name: str
    pick_count: GamemodeCounter

    def __init__(self, gadget_name: str, pick_count: GamemodeCounter):
        self.gadget_name = gadget_name
        self.pick_count = pick_count

class GadgetStats:
    gadget_name: str
    lifetime_stats: Optional[GadgetTimelineStats]
    seasonal_stats: Optional[Dict[int, GadgetTimelineStats]]

    def __init__(self, gadget_name: str, lifetime_stats: Optional[GadgetTimelineStats] = None, seasonal_stats: Optional[Dict[int, GadgetTimelineStats]] = {}):
        self.gadget_name = gadget_name
        self.lifetime_stats = lifetime_stats
        self.seasonal_stats = seasonal_stats