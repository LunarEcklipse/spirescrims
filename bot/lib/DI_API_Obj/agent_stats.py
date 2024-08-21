from typing import Union, List
import re
from enum import StrEnum

class ItemSlot(StrEnum):
    DEFAULT = "Default"
    MOD1 = "Mod1"
    MOD2 = "Mod2"

class AgentTimelineStats:
    '''Wraps both lifetime and seasonal statistics for an agent.'''
    playtime_seconds: int
    pick_count_solo: int
    pick_count_duo: int
    pick_count_trio: int
    win_count_solo: int
    win_count_duo: int
    win_count_trio: int
    weapon_pick_solo: dict
    weapon_pick_duo: dict
    weapon_pick_trio: dict
    passive_pick_solo: dict
    passive_pick_duo: dict
    passive_pick_trio: dict
    active_pick_solo: dict
    active_pick_duo: dict
    active_pick_trio: dict

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
