from typing import Union, List, Dict, Optional
import re, json, os
from enum import StrEnum
from word2number import w2n
from lib.DI_API_Obj.gamemode_counter import GamemodeCounter
from lib.DI_API_Obj.gamemode import GameMode

# Find the path of the JSON file
file_path = os.path.abspath(__file__)
dir_path = os.path.dirname(file_path)
json_path = os.path.join(dir_path, "..", "..", "rsc", "api_kv_conversion.json")

api_kv_dict = None
# Load the JSON file
try:
    with open(json_path, "r", encoding="utf-8") as f:
        api_kv_dict = json.load(f)
except FileNotFoundError:
    print(f"api_kv_conversion.json not found. Please ensure it is in the correct location. The searched location was: {json_path}")

def convert_api_key_to_value(key: str, item_class: str) -> Union[str, None]:
    '''Converts an API key to its value using the API key-value conversion dictionary.'''
    if api_kv_dict is None:
        return None
    if item_class not in api_kv_dict:
        return None
    if key not in api_kv_dict[item_class]:
        return None
    return api_kv_dict[item_class][key]

class ItemSlot(StrEnum):
    DEFAULT = "Default"
    MOD1 = "Mod1"
    MOD2 = "Mod2"

class AgentTimelineStats:
    '''Wraps both lifetime and seasonal statistics for an agent, as well as their progression data.'''
    agent_name: str
    playtime_seconds: Optional[int]
    pick_count: Optional[GamemodeCounter]
    win_count: Optional[GamemodeCounter]
    weapon_pick_count: Optional[Dict[ItemSlot, GamemodeCounter]]
    passive_pick_count: Optional[Dict[ItemSlot, GamemodeCounter]]
    active_pick_count: Optional[Dict[ItemSlot, GamemodeCounter]]

    def __init__(self,
                 agent_name: str,
                 playtime_seconds: Optional[int] = None,
                 pick_count: Optional[GamemodeCounter] = None,
                 win_count: Optional[GamemodeCounter] = None,
                 weapon_pick_count: Optional[Dict[ItemSlot, GamemodeCounter]] = None,
                 passive_pick_count: Optional[Dict[ItemSlot, GamemodeCounter]] = None,
                 active_pick_count: Optional[Dict[ItemSlot, GamemodeCounter]] = None):
        self.agent_name = agent_name
        self.playtime_seconds = playtime_seconds
        self.pick_count = pick_count
        self.win_count = win_count
        self.weapon_pick_count = weapon_pick_count
        self.passive_pick_count = passive_pick_count
        self.active_pick_count = active_pick_count

    def get_pick_count(self, gamemode: Union[GameMode, None] = None) -> int:
        '''Gets the total pick count for an agent.'''
        return self.pick_count.get_total() if gamemode is None else self.pick_count.get_gamemode(gamemode)

    def calculate_win_rate(self, gamemode: Union[GameMode, None] = None) -> float:
        '''Calculates the win rate for a specific gamemode.'''
        matches_played = self.pick_count.get_total() if gamemode is None else self.pick_count.get_gamemode(gamemode)
        matches_won = self.win_count.get_total() if gamemode is None else self.win_count.get_gamemode(gamemode)
        if matches_played is None or matches_won is None:
            return None
        if matches_played == 0:
            return 0.0
        return matches_won / matches_played
    
    def calculate_weapon_pick_rate(self, item_slot: ItemSlot, item_name: str, gamemode: Union[GameMode, None] = None) -> float:
        '''Calculates the pick rate for a specific weapon.'''
        weapon_pick_count = self.weapon_pick_count[item_slot].get_total() if gamemode is None else self.weapon_pick_count[item_slot].get_gamemode(gamemode)
        if weapon_pick_count is None:
            return 0.0
        agent_pick_count = self.pick_count.get_total() if gamemode is None else self.pick_count.get_gamemode(gamemode)
        if agent_pick_count is None:
            return 0.0
        if agent_pick_count == 0:
            return 0.0
        return weapon_pick_count / agent_pick_count
    
    def calculate_passive_pick_rate(self, item_slot: ItemSlot, item_name: str, gamemode: Union[GameMode, None] = None) -> float:
        '''Calculates the pick rate for a specific passive ability.'''
        passive_pick_count = self.passive_pick_count[item_slot].get_total() if gamemode is None else self.passive_pick_count[item_slot].get_gamemode(gamemode)
        agent_pick_count = self.pick_count.get_total() if gamemode is None else self.pick_count.get_gamemode(gamemode)
        if passive_pick_count is None or agent_pick_count is None:
            return 0.0
        if agent_pick_count == 0:
            return 0.0
        return passive_pick_count / agent_pick_count
    
    def calculate_active_pick_rate(self, item_slot: ItemSlot, item_name: str, gamemode: Union[GameMode, None] = None) -> float:
        '''Calculates the pick rate for a specific active ability.'''
        active_pick_count = self.active_pick_count[item_slot].get_total() if gamemode is None else self.active_pick_count[item_slot].get_gamemode(gamemode)
        agent_pick_count = self.pick_count.get_total() if gamemode is None else self.pick_count.get_gamemode(gamemode)
        if active_pick_count is None or agent_pick_count is None:
            return 0.0
        if agent_pick_count == 0:
            return 0.0
        return active_pick_count / agent_pick_count

    @staticmethod
    def wrap_item_pick_dictionary(item_slot: ItemSlot, item_name: str, pick_count: int) -> dict:
        '''Wraps the pick count for an item in a dictionary. We do this through a function to ensure it's compliant.'''
        return {item_slot: {"name": item_name, "pick_count": pick_count}}

    @staticmethod
    def find_item_by_name(in_dict: dict, agent_name: str, item_slot: ItemSlot, item_name: str) -> Union[dict, None]:
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
    mastery_level: Optional[int]
    echelon_level: Optional[int]
    lifetime_stats: Optional[AgentTimelineStats]
    seasonal_stats: Optional[Dict[int, AgentTimelineStats]]

    def __init__(self,
                 agent_name: str,
                 mastery_level: Optional[int] = None,
                 echelon_level: Optional[int] = None,
                 lifetime_stats: Optional[AgentTimelineStats] = None,
                 seasonal_stats: Optional[Dict[int, AgentTimelineStats]] = {}):
        self.agent_name = agent_name
        self.mastery_level = mastery_level
        self.echelon_level = echelon_level
        self.lifetime_stats = lifetime_stats
        self.seasonal_stats = seasonal_stats