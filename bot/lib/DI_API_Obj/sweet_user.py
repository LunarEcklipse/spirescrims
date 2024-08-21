from typing import List, Union
import re
from lib.DI_API_Obj.account_progression import AccountProgression
from lib.DI_API_Obj.account_statistics import AccountStats
from lib.DI_API_Obj.gamemode_counter import GamemodeCounter
from lib.DI_API_Obj.agent_stats import AgentStats, ItemSlot
from lib.DI_API_Obj.gadget_stats import GadgetStats
from lib.DI_API_Obj.general_account_stats import GeneralAccountStats

class SweetUserPartial:
    '''Returned by search results. Contains only the Sweet ID and Display Name.'''
    sweet_id: str
    display_name: str

    def __init__(self, sweet_id: str, display_name: str):
        self.sweet_id = sweet_id
        self.display_name = display_name
        
    def __str__(self) -> str:
        return f"SweetUserPartial(sweet_id={self.sweet_id}, display_name={self.display_name})"
    
    def __repr__(self) -> str:
        return self.__str__()

class SweetUser(SweetUserPartial):
    sweet_id: str
    display_name: str
    not_a_skill_rank: int
    account_level: int
    lifetime_stats: GeneralAccountStats
    seasonal_stats: Dict[str, GeneralAccountStats]
    agent_stats: Dict[str, AgentStats]
    gadget_stats: Dict[str, GadgetStats]

    def __init__(self,
                 sweet_id: str,
                 display_name: str,
                 not_a_skill_rank: int,
                 account_progression: AccountProgression,
                 account_stats: AccountStats):
        self.sweet_id = sweet_id
        self.display_name = display_name
        self.not_a_skill_rank = not_a_skill_rank
        self.account_level = account_level
        self.account_progression = account_progression
        self.account_stats = account_stats

    @staticmethod
    def _get_general_timeline_stats(response: dict, stat_key: str) -> GeneralAccountStats:
        eliminations: GamemodeCounter = GamemodeCounter(response["stats"][stat_key]["eliminationsSolo"] if "stats" in response and stat_key in response["stats"] and "eliminationsSolo" in response["stats"][stat_key] else 0,
                                                        response["stats"][stat_key]["eliminationsDuo"] if "stats" in response and stat_key in response["stats"] and "eliminationsDuo" in response["stats"][stat_key] else 0,
                                                        response["stats"][stat_key]["eliminationsTrio"] if "stats" in response and stat_key in response["stats"] and "eliminationsTrio" in response["stats"][stat_key] else 0)
        deaths: GamemodeCounter = GamemodeCounter(response["stats"][stat_key]["deathsSolo"] if "stats" in response and stat_key in response["stats"] and "deathsSolo" in response["stats"][stat_key] else 0,
                                                  response["stats"][stat_key]["deathsDuo"] if "stats" in response and stat_key in response["stats"] and "deathsDuo" in response["stats"][stat_key] else 0,
                                                  response["stats"][stat_key]["deathsTrio"] if "stats" in response and stat_key in response["stats"] and "deathsTrio" in response["stats"][stat_key] else 0)
        matches_played: GamemodeCounter = GamemodeCounter(response["stats"][stat_key]["matchesPlayedSolo"] if "stats" in response and stat_key in response["stats"] and "matchesPlayedSolo" in response["stats"][stat_key] else 0,
                                                          response["stats"][stat_key]["matchesPlayedDuo"] if "stats" in response and stat_key in response["stats"] and "matchesPlayedDuo" in response["stats"][stat_key] else 0,
                                                          response["stats"][stat_key]["matchesPlayedTrio"] if "stats" in response and stat_key in response["stats"] and "matchesPlayedTrio" in response["stats"][stat_key] else 0)
        matches_won: GamemodeCounter = GamemodeCounter(response["stats"][stat_key]["matchesWonSolo"] if "stats" in response and stat_key in response["stats"] and "matchesWonSolo" in response["stats"][stat_key] else 0,
                                                       response["stats"][stat_key]["matchesWonDuo"] if "stats" in response and stat_key in response["stats"] and "matchesWonDuo" in response["stats"][stat_key] else 0,
                                                       response["stats"][stat_key]["matchesWonTrio"] if "stats" in response and stat_key in response["stats"] and "matchesWonTrio" in response["stats"][stat_key] else 0)
        time_played: GamemodeCounter = GamemodeCounter(response["stats"][stat_key]["timePlayedSolo"] if "stats" in response and stat_key in response["stats"] and "timePlayedSolo" in response["stats"][stat_key] else 0,
                                                       response["stats"][stat_key]["timePlayedDuo"] if "stats" in response and stat_key in response["stats"] and "timePlayedDuo" in response["stats"][stat_key] else 0,
                                                       response["stats"][stat_key]["timePlayedTrio"] if "stats" in response and stat_key in response["stats"] and "timePlayedTrio" in response["stats"][stat_key] else 0)
        return GeneralAccountStats(eliminations, deaths, matches_played, matches_won, time_played)


    def _get_agent_timeline_stats(response: dict, stat_key: str) -> List[AgentTimelineStats]:
        agent_stats = {}
        agent_keys = response["stats"][stat_key]["agentPlaytime"].keys() if "stats" in response and stat_key in response["stats"] and "agentPlaytime" in response["stats"][stat_key] else []
        for agent_key in agent_keys:
            agent_stats[agent_key] = {} # Create empty dict for every agent
            agent_stats[agent_key]["playtime_seconds"] = response["stats"][stat_key]["agentPlaytime"][agent_key] if "stats" in response and stat_key in response["stats"] and "agentPlaytime" in response["stats"][stat_key] and agent_key in response["stats"][stat_key]["agentPlaytime"] else 0
            agent_stats[agent_key]["pick_count"] = GamemodeCounter(response["stats"][stat_key]["agentPickSolo"][agent_key] if "stats" in response and stat_key in response["stats"] and "agentPickSolo" in response["stats"][stat_key] and agent_key in response["stats"][stat_key]["agentPickSolo"] else 0,
                                                                   response["stats"][stat_key]["agentPickDuo"][agent_key] if "stats" in response and stat_key in response["stats"] and "agentPickDuo" in response["stats"][stat_key] and agent_key in response["stats"][stat_key]["agentPickDuo"] else 0,
                                                                   response["stats"][stat_key]["agentPickTrio"][agent_key] if "stats" in response and stat_key in response["stats"] and "agentPickTrio" in response["stats"][stat_key] and agent_key in response["stats"][stat_key]["agentPickTrio"] else 0)
            agent_stats[agent_key]["win_count"] = GamemodeCounter(response["stats"][stat_key]["agentWinSolo"][agent_key] if "stats" in response and stat_key in response["stats"] and "agentWinSolo" in response["stats"][stat_key] and agent_key in response["stats"][stat_key]["agentWinSolo"] else 0,
                                                                  response["stats"][stat_key]["agentWinDuo"][agent_key] if "stats" in response and stat_key in response["stats"] and "agentWinDuo" in response["stats"][stat_key] and agent_key in response["stats"][stat_key]["agentWinDuo"] else 0,
                                                                  response["stats"][stat_key]["agentWinTrio"][agent_key] if "stats" in response and stat_key in response["stats"] and "agentWinTrio" in response["stats"][stat_key] and agent_key in response["stats"][stat_key]["agentWinTrio"] else 0)
            agent_default_key = f"{agent_key}_Default"
            agent_mod1_key = f"{agent_key}_Mod1"
            agent_mod2_key = f"{agent_key}_Mod2"
            agent_stats[agent_key]["weapon_pick_count"] = {}
            agent_stats[agent_key]["weapon_pick_count"][ItemSlot.DEFAULT] = GamemodeCounter(response["stats"][stat_key]["weaponPickSolo"][agent_default_key] if "stats" in response and stat_key in response["stats"] and "weaponPickSolo" in response["stats"][stat_key] and agent_default_key in response["stats"][stat_key]["weaponPickSolo"] else 0,
                                                                                     response["stats"][stat_key]["weaponPickDuo"][agent_default_key] if "stats" in response and stat_key in response["stats"] and "weaponPickDuo" in response["stats"][stat_key] and agent_default_key in response["stats"][stat_key]["weaponPickDuo"] else 0,
                                                                                     response["stats"][stat_key]["weaponPickTrio"][agent_default_key] if "stats" in response and stat_key in response["stats"] and "weaponPickTrio" in response["stats"][stat_key] and agent_default_key in response["stats"][stat_key]["weaponPickTrio"] else 0)
            agent_stats[agent_key]["weapon_pick_count"][ItemSlot.MOD1] = GamemodeCounter(response["stats"][stat_key]["weaponPickSolo"][agent_mod1_key] if "stats" in response and stat_key in response["stats"] and "weaponPickSolo" in response["stats"][stat_key] and agent_mod1_key in response["stats"][stat_key]["weaponPickSolo"] else 0,
                                                                                  response["stats"][stat_key]["weaponPickDuo"][agent_mod1_key] if "stats" in response and stat_key in response["stats"] and "weaponPickDuo" in response["stats"][stat_key] and agent_mod1_key in response["stats"][stat_key]["weaponPickDuo"] else 0,
                                                                                  response["stats"][stat_key]["weaponPickTrio"][agent_mod1_key] if "stats" in response and stat_key in response["stats"] and "weaponPickTrio" in response["stats"][stat_key] and agent_mod1_key in response["stats"][stat_key]["weaponPickTrio"] else 0)
            agent_stats[agent_key]["weapon_pick_count"][ItemSlot.MOD2] = GamemodeCounter(response["stats"][stat_key]["weaponPickSolo"][agent_mod2_key] if "stats" in response and stat_key in response["stats"] and "weaponPickSolo" in response["stats"][stat_key] and agent_mod2_key in response["stats"][stat_key]["weaponPickSolo"] else 0,
                                                                                  response["stats"][stat_key]["weaponPickDuo"][agent_mod2_key] if "stats" in response and stat_key in response["stats"] and "weaponPickDuo" in response["stats"][stat_key] and agent_mod2_key in response["stats"][stat_key]["weaponPickDuo"] else 0,
                                                                                  response["stats"][stat_key]["weaponPickTrio"][agent_mod2_key] if "stats" in response and stat_key in response["stats"] and "weaponPickTrio" in response["stats"][stat_key] and agent_mod2_key in response["stats"][stat_key]["weaponPickTrio"] else 0)
            agent_stats[agent_key]["passive_pick_count"] = {}
            agent_stats[agent_key]["passive_pick_count"][ItemSlot.DEFAULT] = GamemodeCounter(response["stats"][stat_key]["passivePickSolo"][agent_default_key] if "stats" in response and stat_key in response["stats"] and "passivePickSolo" in response["stats"][stat_key] and agent_default_key in response["stats"][stat_key]["passivePickSolo"] else 0,
                                                                                      response["stats"][stat_key]["passivePickDuo"][agent_default_key] if "stats" in response and stat_key in response["stats"] and "passivePickDuo" in response["stats"][stat_key] and agent_default_key in response["stats"][stat_key]["passivePickDuo"] else 0,
                                                                                      response["stats"][stat_key]["passivePickTrio"][agent_default_key] if "stats" in response and stat_key in response["stats"] and "passivePickTrio" in response["stats"][stat_key] and agent_default_key in response["stats"][stat_key]["passivePickTrio"] else 0)
            agent_stats[agent_key]["passive_pick_count"][ItemSlot.MOD1] = GamemodeCounter(response["stats"][stat_key]["passivePickSolo"][agent_mod1_key] if "stats" in response and stat_key in response["stats"] and "passivePickSolo" in response["stats"][stat_key] and agent_mod1_key in response["stats"][stat_key]["passivePickSolo"] else 0,
                                                                                   response["stats"][stat_key]["passivePickDuo"][agent_mod1_key] if "stats" in response and stat_key in response["stats"] and "passivePickDuo" in response["stats"][stat_key] and agent_mod1_key in response["stats"][stat_key]["passivePickDuo"] else 0,
                                                                                   response["stats"][stat_key]["passivePickTrio"][agent_mod1_key] if "stats" in response and stat_key in response["stats"] and "passivePickTrio" in response["stats"][stat_key] and agent_mod1_key in response["stats"][stat_key]["passivePickTrio"] else 0)
            agent_stats[agent_key]["passive_pick_count"][ItemSlot.MOD2] = GamemodeCounter(response["stats"][stat_key]["passivePickSolo"][agent_mod2_key] if "stats" in response and stat_key in response["stats"] and "passivePickSolo" in response["stats"][stat_key] and agent_mod2_key in response["stats"][stat_key]["passivePickSolo"] else 0,
                                                                                   response["stats"][stat_key]["passivePickDuo"][agent_mod2_key] if "stats" in response and stat_key in response["stats"] and "passivePickDuo" in response["stats"][stat_key] and agent_mod2_key in response["stats"][stat_key]["passivePickDuo"] else 0,
                                                                                   response["stats"][stat_key]["passivePickTrio"][agent_mod2_key] if "stats" in response and stat_key in response["stats"] and "passivePickTrio" in response["stats"][stat_key] and agent_mod2_key in response["stats"][stat_key]["passivePickTrio"] else 0)
            agent_stats[agent_key]["active_pick_count"] = {}
            agent_stats[agent_key]["active_pick_count"][ItemSlot.DEFAULT] = GamemodeCounter(response["stats"][stat_key]["activePickSolo"][agent_default_key] if "stats" in response and stat_key in response["stats"] and "activePickSolo" in response["stats"][stat_key] and agent_default_key in response["stats"][stat_key]["activePickSolo"] else 0,
                                                                                     response["stats"][stat_key]["activePickDuo"][agent_default_key] if "stats" in response and stat_key in response["stats"] and "activePickDuo" in response["stats"][stat_key] and agent_default_key in response["stats"][stat_key]["activePickDuo"] else 0,
                                                                                     response["stats"][stat_key]["activePickTrio"][agent_default_key] if "stats" in response and stat_key in response["stats"] and "activePickTrio" in response["stats"][stat_key] and agent_default_key in response["stats"][stat_key]["activePickTrio"] else 0)
            agent_stats[agent_key]["active_pick_count"][ItemSlot.MOD1] = GamemodeCounter(response["stats"][stat_key]["activePickSolo"][agent_mod1_key] if "stats" in response and stat_key in response["stats"] and "activePickSolo" in response["stats"][stat_key] and agent_mod1_key in response["stats"][stat_key]["activePickSolo"] else 0,
                                                                                  response["stats"][stat_key]["activePickDuo"][agent_mod1_key] if "stats" in response and stat_key in response["stats"] and "activePickDuo" in response["stats"][stat_key] and agent_mod1_key in response["stats"][stat_key]["activePickDuo"] else 0,
                                                                                  response["stats"][stat_key]["activePickTrio"][agent_mod1_key] if "stats" in response and stat_key in response["stats"] and "activePickTrio" in response["stats"][stat_key] and agent_mod1_key in response["stats"][stat_key]["activePickTrio"] else 0)
            agent_stats[agent_key]["active_pick_count"][ItemSlot.MOD2] = GamemodeCounter(response["stats"][stat_key]["activePickSolo"][agent_mod2_key] if "stats" in response and stat_key in response["stats"] and "activePickSolo" in response["stats"][stat_key] and agent_mod2_key in response["stats"][stat_key]["activePickSolo"] else 0,
                                                                                  response["stats"][stat_key]["activePickDuo"][agent_mod2_key] if "stats" in response and stat_key in response["stats"] and "activePickDuo" in response["stats"][stat_key] and agent_mod2_key in response["stats"][stat_key]["activePickDuo"] else 0,
                                                                                  response["stats"][stat_key]["activePickTrio"][agent_mod2_key] if "stats" in response and stat_key in response["stats"] and "activePickTrio" in response["stats"][stat_key] and agent_mod2_key in response["stats"][stat_key]["activePickTrio"] else 0)
            agent_stats[agent_key] = AgentTimelineStats(agent_key,
                                     agent_stats[agent_key]["playtime_seconds"],
                                     agent_stats[agent_key]["pick_count"],
                                     agent_stats[agent_key]["win_count"],
                                     agent_stats[agent_key]["weapon_pick_count"],
                                     agent_stats[agent_key]["passive_pick_count"],
                                     agent_stats[agent_key]["active_pick_count"])
        
    @staticmethod
    def _get_gadget_stats(response: dict, stat_key: str) -> Dict[str, GadgetStats]:
        gadget_keys_solo: Union[List[str], None] = response["stats"][stat_key]["gadgetPickSolo"].keys() if "stats" in response and stat_key in response["stats"] and "gadgetPickSolo" in response["stats"][stat_key] else None
        gadget_keys_duo: Union[List[str], None] = response["stats"][stat_key]["gadgetPickDuo"].keys() if "stats" in response and stat_key in response["stats"] and "gadgetPickDuo" in response["stats"][stat_key] else None
        gadget_keys_trio: Union[List[str], None] = response["stats"][stat_key]["gadgetPickTrio"].keys() if "stats" in response and stat_key in response["stats"] and "gadgetPickTrio" in response["stats"][stat_key] else None
        
        # Make a union of all the keys
        gadget_keys = []
        if gadget_keys_solo is not None:
            gadget_keys += gadget_keys_solo
        if gadget_keys_duo is not None:
            gadget_keys += gadget_keys_duo
        if gadget_keys_trio is not None:
            gadget_keys += gadget_keys_trio
        gadget_keys = list(set(gadget_keys)) # Remove duplicates
        gadget_stats = {}
        for gadget_key in gadget_keys:
            gadget_stats[gadget_key] = GadgetStats(gadget_key,
                                                   GamemodeCounter(response["stats"][stat_key]["gadgetPickSolo"][gadget_key] if "stats" in response and stat_key in response["stats"] and "gadgetPickSolo" in response["stats"][stat_key] and gadget_key in response["stats"][stat_key]["gadgetPickSolo"] else 0,
                                                                   response["stats"][stat_key]["gadgetPickDuo"][gadget_key] if "stats" in response and stat_key in response["stats"] and "gadgetPickDuo" in response["stats"][stat_key] and gadget_key in response["stats"][stat_key]["gadgetPickDuo"] else 0,
                                                                   response["stats"][stat_key]["gadgetPickTrio"][gadget_key] if "stats" in response and stat_key in response["stats"] and "gadgetPickTrio" in response["stats"][stat_key] and gadget_key in response["stats"][stat_key]["gadgetPickTrio"] else 0))

    @staticmethod
    def from_api_response(sweet_id: str, response: dict) -> Union['SweetUser', None]:
        '''Constructs a SweetUser object from the API response.'''
        if "display_name" not in response:
            return None
        
        # Basic information
        display_name = response["displayName"] if "displayName" in response else None
        not_a_skill_rank = response["notASkillRank"] if "notASkillRank" in response else None
        
        # Account progression
        account_level = response["progression"]["Account"]["level"] if "progression" in response and "Account" in response["progression"] and "level" in response["progression"]["Account"] else None
        agent_stats: dict = {}
        for key in response["progression"]["Account"].keys():
            if key == "Account":
                continue
            agent_stats[key] = AgentStats(key,
                                          response["progression"]["Account"][key]["masteryLevel"] if "masteryLevel" in response["progression"]["Account"][key] else None,
                                          response["progression"]["Account"][key]["echelonLevel"] if "echelonLevel" in response["progression"]["Account"][key] else None)
                        
        general_lifetime_account_stats = _get_general_timeline_stats(response, "lifetime")
        
        for season in response["stats"]:
            general_seasonal_account_stats = _get_general_timeline_stats(response, season)
            seasonal_stats[season] = general_seasonal_account_stats

