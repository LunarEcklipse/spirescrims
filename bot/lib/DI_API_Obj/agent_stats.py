from typing import Union, List, Dict
import re
from enum import StrEnum
from word2number import w2n
from lib.DI_API_Obj.gamemode_counter import GamemodeCounter

class ItemSlot(StrEnum):
    DEFAULT = "Default"
    MOD1 = "Mod1"
    MOD2 = "Mod2"

class AgentTimelineStats:
    '''Wraps both lifetime and seasonal statistics for an agent, as well as their progression data.'''
    agent_name: str
    playtime_seconds: int
    pick_count: GamemodeCounter
    win_count: GamemodeCounter
    weapon_pick_count: Dict[str, GamemodeCounter]
    passive_pick_count: Dict[str, GamemodeCounter]
    active_pick_count: Dict[str, GamemodeCounter]

    @staticmethod
    def wrap_item_pick_dictionary(item_slot: ItemSlot, item_name: str, pick_count: int) -> dict:
        '''Wraps the pick count for an item in a dictionary. We do this through a function to ensure it's compliant.'''
        return {item_slot: {"name": item_name, "pick_count": pick_count}}
    
    @staticmethod
    def find_item_by_name(self, in_dict: dict, agent_name: str, item_slot: ItemSlot, item_name: str) -> Union[dict, None]:
        '''Finds an item in the dictionary by the Agent's name and the item's slot.'''
        # Items follow the pattern of "<agent_name>_<item_slot>"
        key = f"{agent_name}_{item_slot}"
        if key not in in_dict:
            return None
        if in_dict[key]["name"] == item_name:
            return in_dict[key]
        return None
    

class AgentStats:
    agent_name: str
    mastery_level: int
    echelon_level: int

    lifetime_stats: AgentTimelineStats
    seasonal_stats: dict

    @staticmethod
    def parse_season_number(season_str: str) -> Union[int, None]:
        '''Parses the season number from the season string.'''
        # Seasons are formatted in camelcase with the season number as text at the end (e.g. "seasonFour")
        pattern = re.compile(r'season([A-Za-z]+)')
        match = pattern.search(season_str)
        if match is None:
            return None
        return w2n.word_to_num(match.group(1).lower())
    
    def add_season_stats_to_dict(self, season_str: str, stats: AgentTimelineStats) -> None:
        '''Adds the season statistics to the seasonal stats dictionary.'''
        season_num = AgentStats.parse_season_number(season_str)
        if season_num is None:
            return
        self.seasonal_stats[season_num] = stats

    def __init__(self,
                 agent_name: str,
                 mastery_level: int,
                 echelon_level: int,
                 lifetime_stats: AgentTimelineStats,
                 seasonal_stats: dict = {}):
        self.agent_name = agent_name
        self.mastery_level = mastery_level
        self.echelon_level = echelon_level
        self.lifetime_stats = lifetime_stats
        self.seasonal_stats = seasonal_stats

    