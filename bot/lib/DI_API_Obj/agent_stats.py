from typing import Union, List, Dict
import re, json, os
from enum import StrEnum
from word2number import w2n
from lib.DI_API_Obj.gamemode_counter import GamemodeCounter

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
    playtime_seconds: int
    pick_count: GamemodeCounter
    win_count: GamemodeCounter
    weapon_pick_count: Dict[ItemSlot, GamemodeCounter]
    passive_pick_count: Dict[ItemSlot, GamemodeCounter]
    active_pick_count: Dict[ItemSlot, GamemodeCounter]

    def __init__(self, agent_name: str, mastery_level: int = None, echelon_level: int = None, playtime_seconds: int = None, pick_count: GamemodeCounter = None, win_count: GamemodeCounter = None, weapon_pick_count: Dict[ItemSlot, GamemodeCounter] = None, passive_pick_count: Dict[ItemSlot, GamemodeCounter] = None, active_pick_count: Dict[ItemSlot, GamemodeCounter] = None):
        self.agent_name = agent_name
        self.playtime_seconds = playtime_seconds
        self.pick_count = pick_count
        self.win_count = win_count
        self.weapon_pick_count = weapon_pick_count
        self.passive_pick_count = passive_pick_count
        self.active_pick_count = active_pick_count

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
    seasonal_stats: Dict[int, AgentTimelineStats]

    def __init__(self, agent_name: str, mastery_level: int = None, echelon_level: int = None, lifetime_stats: AgentTimelineStats = None, seasonal_stats: Dict[int, AgentTimelineStats] = {}):
        self.agent_name = agent_name
        self.mastery_level = mastery_level
        self.echelon_level = echelon_level
        self.lifetime_stats = lifetime_stats
        self.seasonal_stats = seasonal_stats