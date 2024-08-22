from typing import List, Union, Dict, Optional
from enum import Enum
import re, json
from json import JSONDecodeError
from lib.DI_API_Obj.account_progression import AccountProgression
from lib.DI_API_Obj.account_statistics import AccountStats
from lib.DI_API_Obj.gamemode_counter import GamemodeCounter
from lib.DI_API_Obj.agent_stats import AgentStats, AgentTimelineStats, ItemSlot
from lib.DI_API_Obj.gadget_stats import GadgetStats, GadgetTimelineStats
from lib.DI_API_Obj.general_account_stats import GeneralAccountStats
from word2number import w2n
from datetime import datetime, timezone

class GameMode(Enum):
    SOLO=1,
    DUO=2,
    TRIO=3

class SweetUserPartial:
    '''Returned by search results. Contains only the Sweet ID and Display Name.'''
    sweet_id: str
    display_name: Optional[str]

    def __init__(self, sweet_id: str, display_name: Optional[str]):
        self.sweet_id = sweet_id
        self.display_name = display_name
        
    def __str__(self) -> str:
        return f"SweetUserPartial(sweet_id={self.sweet_id}, display_name={self.display_name})"
    
    def __repr__(self) -> str:
        return self.__str__()

class SweetUser(SweetUserPartial):
    sweet_id: str
    display_name: Optional[str]
    not_a_skill_rank: Optional[int]
    account_level: Optional[int]
    general_stats: Dict[Union[str, int], GeneralAccountStats]
    agent_stats: Dict[Union[str, int], AgentStats]
    gadget_stats: Dict[Union[str, int], GadgetStats]

    def __init__(self,
                 sweet_id: str,
                 display_name: Optional[str],
                 not_a_skill_rank: Optional[int],
                 account_level: Optional[int],
                 general_stats: Dict[Union[str, int], GeneralAccountStats],
                 agent_stats: Dict[Union[str, int], AgentStats],
                 gadget_stats: Dict[Union[str, int], GadgetStats]):
        super().__init__(sweet_id, display_name)
        self.not_a_skill_rank = not_a_skill_rank
        self.account_level = account_level
        self.general_stats = general_stats
        self.agent_stats = agent_stats
        self.gadget_stats = gadget_stats


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

    @staticmethod
    def _get_agent_timeline_stats(response: dict, stat_key: str) -> Dict[str, AgentTimelineStats]:
        agent_stats = {}
        agent_keys = response["stats"][stat_key]["agentPlayTime"].keys() if "stats" in response and stat_key in response["stats"] and "agentPlayTime" in response["stats"][stat_key] else []
        for agent_key in agent_keys:
            if agent_key == "None":
                continue
            agent_stats[agent_key] = {} # Create empty dict for every agent
            agent_stats[agent_key]["playtime_seconds"] = response["stats"][stat_key]["agentPlayTime"][agent_key] if "stats" in response and stat_key in response["stats"] and "agentPlayTime" in response["stats"][stat_key] and agent_key in response["stats"][stat_key]["agentPlayTime"] else 0
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
        return agent_stats
        
    @staticmethod
    def _get_gadget_stats(response: dict, stat_key: str) -> Dict[str, GadgetTimelineStats]:
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
            gadget_stats[gadget_key] = GadgetTimelineStats(gadget_key,
                                                   GamemodeCounter(response["stats"][stat_key]["gadgetPickSolo"][gadget_key] if "stats" in response and stat_key in response["stats"] and "gadgetPickSolo" in response["stats"][stat_key] and gadget_key in response["stats"][stat_key]["gadgetPickSolo"] else 0,
                                                                   response["stats"][stat_key]["gadgetPickDuo"][gadget_key] if "stats" in response and stat_key in response["stats"] and "gadgetPickDuo" in response["stats"][stat_key] and gadget_key in response["stats"][stat_key]["gadgetPickDuo"] else 0,
                                                                   response["stats"][stat_key]["gadgetPickTrio"][gadget_key] if "stats" in response and stat_key in response["stats"] and "gadgetPickTrio" in response["stats"][stat_key] and gadget_key in response["stats"][stat_key]["gadgetPickTrio"] else 0))
        return gadget_stats

    @staticmethod
    def _determine_season_number(season: str) -> Optional[int]:
        '''Determines the season number from the season name.'''
        season_search = re.compile(r'season([A-Za-z]+)')
        season_number = None
        season_num = season_search.match(season)
        if season_num is not None:
            season_number = w2n.word_to_num(season_num.group(1).lower())
        return int(season_number) if season_number is not None else None

    @staticmethod
    def from_api_response(sweet_id: str, response: dict) -> Union['SweetUser', None]:
        '''Constructs a SweetUser object from the API response.'''
        if "displayName" not in response:
            return None
        
        # Basic information
        display_name: Optional[str] = str(response["displayName"]) if "displayName" in response else None
        not_a_skill_rank = int(response["notASkillRank"]) if "notASkillRank" in response else None
        
        # Account progression
        account_level = response["progression"]["Account"]["level"] if "progression" in response and "Account" in response["progression"] and "level" in response["progression"]["Account"] else None
        agent_stats: dict = {}
        for key in response["progression"].keys():
            if key == "Account":
                continue
            agent_stats[key] = AgentStats(key,
                                          response["progression"][key]["mastery"] if "mastery" in response["progression"][key] else None,
                                          response["progression"][key]["echelon"] if "echelon" in response["progression"][key] else None)

        general_lifetime_account_stats: GeneralAccountStats = SweetUser._get_general_timeline_stats(response, "lifetime")
        agent_lifetime_stats: Dict[str, AgentTimelineStats] = SweetUser._get_agent_timeline_stats(response, "lifetime")
        for i in agent_lifetime_stats.items(): # Agent lifetime stats
            if i[0] not in agent_stats:
                agent_stats[i[0]] = AgentStats(i[0], 0, 0, i[1], None)
                continue
            agent_stats[i[0]].lifetime_stats = i[1]
        gadget_stats: dict = {}
        gadget_lifetime_stats: Dict[str, GadgetTimelineStats] = SweetUser._get_gadget_stats(response, "lifetime")
        for key in gadget_lifetime_stats.keys():
            gadget_stats[key] = GadgetStats(key, gadget_lifetime_stats[key])

        general_season_account_stats: Dict[Union[int, str], GeneralAccountStats] = {"lifetime": general_lifetime_account_stats}
        for season in response["stats"]:
            if season == "lifetime":
                continue
            season_number: Union[int, None] = SweetUser._determine_season_number(season)
            if season_number is None:
                continue
            general_seasonal_account_stats = SweetUser._get_general_timeline_stats(response, season)
            general_season_account_stats[season_number] = general_seasonal_account_stats
            agent_seasonal_stats: Dict[str, AgentTimelineStats] = SweetUser._get_agent_timeline_stats(response, season)
            gadget_seasonal_stats: Dict[str, GadgetTimelineStats] = SweetUser._get_gadget_stats(response, season)
            for key in agent_seasonal_stats.keys():
                if key not in agent_stats:
                    agent_stats[key] = AgentStats(key, 0, 0, None, {season_number: agent_seasonal_stats[key]})
                    continue
                agent_stats[key].seasonal_stats[season_number] = agent_seasonal_stats[key]
            for key in gadget_seasonal_stats.keys():
                if key not in gadget_stats:
                    gadget_stats[key] = GadgetStats(key, None, {season_number: gadget_seasonal_stats[key]})
                    continue
                gadget_stats[key].seasonal_stats[season_number] = gadget_seasonal_stats[key]
        
        return SweetUser(sweet_id,
                         display_name,
                         not_a_skill_rank,
                         account_level,
                         general_season_account_stats,
                         agent_stats,
                         gadget_stats)

    def dump_json(self) -> str:
        '''Dumps the SweetUser object to a JSON string.'''
        out_dict: dict = {}
        out_dict["sweet_id"] = self.sweet_id
        out_dict["display_name"] = self.display_name
        out_dict["not_a_skill_rank"] = self.not_a_skill_rank
        out_dict["account_level"] = self.account_level
        out_dict["general_stats"] = {}
        for key, value in self.general_stats.items():
            out_dict["general_stats"][key] = {}
            out_dict["general_stats"][key]["eliminations"] = {}
            out_dict["general_stats"][key]["eliminations"]["solo"] = value.eliminations.solo
            out_dict["general_stats"][key]["eliminations"]["duo"] = value.eliminations.duo
            out_dict["general_stats"][key]["eliminations"]["trio"] = value.eliminations.trio
            out_dict["general_stats"][key]["deaths"] = {}
            out_dict["general_stats"][key]["deaths"]["solo"] = value.deaths.solo
            out_dict["general_stats"][key]["deaths"]["duo"] = value.deaths.duo
            out_dict["general_stats"][key]["deaths"]["trio"] = value.deaths.trio
            out_dict["general_stats"][key]["matches_played"] = {}
            out_dict["general_stats"][key]["matches_played"]["solo"] = value.matches_played.solo
            out_dict["general_stats"][key]["matches_played"]["duo"] = value.matches_played.duo
            out_dict["general_stats"][key]["matches_played"]["trio"] = value.matches_played.trio
            out_dict["general_stats"][key]["matches_won"] = {}
            out_dict["general_stats"][key]["matches_won"]["solo"] = value.matches_won.solo
            out_dict["general_stats"][key]["matches_won"]["duo"] = value.matches_won.duo
            out_dict["general_stats"][key]["matches_won"]["trio"] = value.matches_won.trio
            out_dict["general_stats"][key]["time_played"] = {}
            out_dict["general_stats"][key]["time_played"]["solo"] = value.time_played.solo
            out_dict["general_stats"][key]["time_played"]["duo"] = value.time_played.duo
            out_dict["general_stats"][key]["time_played"]["trio"] = value.time_played.trio

        out_dict["agent_stats"] = {}
        for key, value in self.agent_stats.items():
            out_dict["agent_stats"][key] = {}
            out_dict["agent_stats"][key]["mastery_level"] = value.mastery_level
            out_dict["agent_stats"][key]["echelon_level"] = value.echelon_level
            out_dict["agent_stats"][key]["lifetime_stats"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["playtime_seconds"] = value.lifetime_stats.playtime_seconds
            
            out_dict["agent_stats"][key]["lifetime_stats"]["pick_count"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["pick_count"]["solo"] = value.lifetime_stats.pick_count.solo
            out_dict["agent_stats"][key]["lifetime_stats"]["pick_count"]["duo"] = value.lifetime_stats.pick_count.duo
            out_dict["agent_stats"][key]["lifetime_stats"]["pick_count"]["trio"] = value.lifetime_stats.pick_count.trio
            
            out_dict["agent_stats"][key]["lifetime_stats"]["win_count"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["win_count"]["solo"] = value.lifetime_stats.win_count.solo
            out_dict["agent_stats"][key]["lifetime_stats"]["win_count"]["duo"] = value.lifetime_stats.win_count.duo
            out_dict["agent_stats"][key]["lifetime_stats"]["win_count"]["trio"] = value.lifetime_stats.win_count.trio
            
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["default"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["default"]["solo"] = value.lifetime_stats.weapon_pick_count[ItemSlot.DEFAULT].solo
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["default"]["duo"] = value.lifetime_stats.weapon_pick_count[ItemSlot.DEFAULT].duo
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["default"]["trio"] = value.lifetime_stats.weapon_pick_count[ItemSlot.DEFAULT].trio
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["mod1"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["mod1"]["solo"] = value.lifetime_stats.weapon_pick_count[ItemSlot.MOD1].solo
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["mod1"]["duo"] = value.lifetime_stats.weapon_pick_count[ItemSlot.MOD1].duo
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["mod1"]["trio"] = value.lifetime_stats.weapon_pick_count[ItemSlot.MOD1].trio
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["mod2"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["mod2"]["solo"] = value.lifetime_stats.weapon_pick_count[ItemSlot.MOD2].solo
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["mod2"]["duo"] = value.lifetime_stats.weapon_pick_count[ItemSlot.MOD2].duo
            out_dict["agent_stats"][key]["lifetime_stats"]["weapon_pick_count"]["mod2"]["trio"] = value.lifetime_stats.weapon_pick_count[ItemSlot.MOD2].trio

            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["default"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["default"]["solo"] = value.lifetime_stats.passive_pick_count[ItemSlot.DEFAULT].solo
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["default"]["duo"] = value.lifetime_stats.passive_pick_count[ItemSlot.DEFAULT].duo
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["default"]["trio"] = value.lifetime_stats.passive_pick_count[ItemSlot.DEFAULT].trio
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["mod1"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["mod1"]["solo"] = value.lifetime_stats.passive_pick_count[ItemSlot.MOD1].solo
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["mod1"]["duo"] = value.lifetime_stats.passive_pick_count[ItemSlot.MOD1].duo
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["mod1"]["trio"] = value.lifetime_stats.passive_pick_count[ItemSlot.MOD1].trio
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["mod2"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["mod2"]["solo"] = value.lifetime_stats.passive_pick_count[ItemSlot.MOD2].solo
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["mod2"]["duo"] = value.lifetime_stats.passive_pick_count[ItemSlot.MOD2].duo
            out_dict["agent_stats"][key]["lifetime_stats"]["passive_pick_count"]["mod2"]["trio"] = value.lifetime_stats.passive_pick_count[ItemSlot.MOD2].trio

            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["default"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["default"]["solo"] = value.lifetime_stats.active_pick_count[ItemSlot.DEFAULT].solo
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["default"]["duo"] = value.lifetime_stats.active_pick_count[ItemSlot.DEFAULT].duo
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["default"]["trio"] = value.lifetime_stats.active_pick_count[ItemSlot.DEFAULT].trio
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["mod1"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["mod1"]["solo"] = value.lifetime_stats.active_pick_count[ItemSlot.MOD1].solo
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["mod1"]["duo"] = value.lifetime_stats.active_pick_count[ItemSlot.MOD1].duo
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["mod1"]["trio"] = value.lifetime_stats.active_pick_count[ItemSlot.MOD1].trio
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["mod2"] = {}
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["mod2"]["solo"] = value.lifetime_stats.active_pick_count[ItemSlot.MOD2].solo
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["mod2"]["duo"] = value.lifetime_stats.active_pick_count[ItemSlot.MOD2].duo
            out_dict["agent_stats"][key]["lifetime_stats"]["active_pick_count"]["mod2"]["trio"] = value.lifetime_stats.active_pick_count[ItemSlot.MOD2].trio

            out_dict["agent_stats"][key]["seasonal_stats"] = {}
            for season, stats in value.seasonal_stats.items():
                out_dict["agent_stats"][key]["seasonal_stats"][season] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["playtime_seconds"] = stats.playtime_seconds
                
                out_dict["agent_stats"][key]["seasonal_stats"][season]["pick_count"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["pick_count"]["solo"] = stats.pick_count.solo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["pick_count"]["duo"] = stats.pick_count.duo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["pick_count"]["trio"] = stats.pick_count.trio
                
                out_dict["agent_stats"][key]["seasonal_stats"][season]["win_count"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["win_count"]["solo"] = stats.win_count.solo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["win_count"]["duo"] = stats.win_count.duo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["win_count"]["trio"] = stats.win_count.trio
                
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["default"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["default"]["solo"] = stats.weapon_pick_count[ItemSlot.DEFAULT].solo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["default"]["duo"] = stats.weapon_pick_count[ItemSlot.DEFAULT].duo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["default"]["trio"] = stats.weapon_pick_count[ItemSlot.DEFAULT].trio
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["mod1"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["mod1"]["solo"] = stats.weapon_pick_count[ItemSlot.MOD1].solo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["mod1"]["duo"] = stats.weapon_pick_count[ItemSlot.MOD1].duo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["mod1"]["trio"] = stats.weapon_pick_count[ItemSlot.MOD1].trio
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["mod2"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["mod2"]["solo"] = stats.weapon_pick_count[ItemSlot.MOD2].solo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["mod2"]["duo"] = stats.weapon_pick_count[ItemSlot.MOD2].duo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["weapon_pick_count"]["mod2"]["trio"] = stats.weapon_pick_count[ItemSlot.MOD2].trio

                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["default"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["default"]["solo"] = stats.passive_pick_count[ItemSlot.DEFAULT].solo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["default"]["duo"] = stats.passive_pick_count[ItemSlot.DEFAULT].duo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["default"]["trio"] = stats.passive_pick_count[ItemSlot.DEFAULT].trio
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["mod1"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["mod1"]["solo"] = stats.passive_pick_count[ItemSlot.MOD1].solo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["mod1"]["duo"] = stats.passive_pick_count[ItemSlot.MOD1].duo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["mod1"]["trio"] = stats.passive_pick_count[ItemSlot.MOD1].trio
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["mod2"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["mod2"]["solo"] = stats.passive_pick_count[ItemSlot.MOD2].solo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["mod2"]["duo"] = stats.passive_pick_count[ItemSlot.MOD2].duo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["passive_pick_count"]["mod2"]["trio"] = stats.passive_pick_count[ItemSlot.MOD2].trio

                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["default"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["default"]["solo"] = stats.active_pick_count[ItemSlot.DEFAULT].solo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["default"]["duo"] = stats.active_pick_count[ItemSlot.DEFAULT].duo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["default"]["trio"] = stats.active_pick_count[ItemSlot.DEFAULT].trio
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["mod1"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["mod1"]["solo"] = stats.active_pick_count[ItemSlot.MOD1].solo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["mod1"]["duo"] = stats.active_pick_count[ItemSlot.MOD1].duo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["mod1"]["trio"] = stats.active_pick_count[ItemSlot.MOD1].trio
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["mod2"] = {}
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["mod2"]["solo"] = stats.active_pick_count[ItemSlot.MOD2].solo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["mod2"]["duo"] = stats.active_pick_count[ItemSlot.MOD2].duo
                out_dict["agent_stats"][key]["seasonal_stats"][season]["active_pick_count"]["mod2"]["trio"] = stats.active_pick_count[ItemSlot.MOD2].trio

        out_dict["gadget_stats"] = {}
        for key, value in self.gadget_stats.items():
            out_dict["gadget_stats"][key] = {}
            out_dict["gadget_stats"][key]["lifetime_stats"] = {}
            out_dict["gadget_stats"][key]["lifetime_stats"]["pick_count"] = {}
            out_dict["gadget_stats"][key]["lifetime_stats"]["pick_count"]["solo"] = value.lifetime_stats.pick_count.solo
            out_dict["gadget_stats"][key]["lifetime_stats"]["pick_count"]["duo"] = value.lifetime_stats.pick_count.duo
            out_dict["gadget_stats"][key]["lifetime_stats"]["pick_count"]["trio"] = value.lifetime_stats.pick_count.trio
            out_dict["gadget_stats"][key]["seasonal_stats"] = {}
            for season, stats in value.seasonal_stats.items():
                out_dict["gadget_stats"][key]["seasonal_stats"][season] = {}
                out_dict["gadget_stats"][key]["seasonal_stats"][season]["pick_count"] = {}
                out_dict["gadget_stats"][key]["seasonal_stats"][season]["pick_count"]["solo"] = stats.pick_count.solo
                out_dict["gadget_stats"][key]["seasonal_stats"][season]["pick_count"]["duo"] = stats.pick_count.duo
                out_dict["gadget_stats"][key]["seasonal_stats"][season]["pick_count"]["trio"] = stats.pick_count.trio

        out_dict["data_creation_time"] = datetime.now(tz=timezone.utc).isoformat()
        return json.dumps(out_dict, indent=4)
    
    @staticmethod
    def from_json(json_str: Union[dict, str]) -> 'SweetUser':
        try:
            if type(json_str) == str:
                json_str = json.loads(json_str)
            sweet_id: str = json_str["sweet_id"]
            display_name: Optional[str] = json_str["display_name"]
            not_a_skill_rank: Optional[int] = json_str["not_a_skill_rank"]
            account_level: Optional[int] = json_str["account_level"]
            general_stats: Dict[Union[int, str], GeneralAccountStats] = {}
            for key, value in json_str["general_stats"].items():
                general_stats[key] = GeneralAccountStats(GamemodeCounter(value["eliminations"]["solo"],
                                                         value["eliminations"]["duo"],
                                                         value["eliminations"]["trio"]),
                                                         GamemodeCounter(value["deaths"]["solo"],
                                                         value["deaths"]["duo"],
                                                         value["deaths"]["trio"]),
                                                         GamemodeCounter(value["matches_played"]["solo"],
                                                         value["matches_played"]["duo"],
                                                         value["matches_played"]["trio"]),
                                                         GamemodeCounter(value["matches_won"]["solo"],
                                                         value["matches_won"]["duo"],
                                                         value["matches_won"]["trio"]),
                                                         GamemodeCounter(value["time_played"]["solo"],
                                                         value["time_played"]["duo"],
                                                         value["time_played"]["trio"]))
            agent_stats: Dict[str, AgentStats] = {}
            for key, value in json_str["agent_stats"].items():
                seasonal_stats: Dict[Union[int, str], AgentTimelineStats] = {}
                for key2, value2 in value["seasonal_stats"].items():
                    seasonal_stats[key2] = AgentTimelineStats(key,
                                                              value2["playtime_seconds"],
                                                              GamemodeCounter(value2["pick_count"]["solo"],
                                                                              value2["pick_count"]["duo"],
                                                                              value2["pick_count"]["trio"]),
                                                              GamemodeCounter(value2["win_count"]["solo"],
                                                                              value2["win_count"]["duo"],
                                                                              value2["win_count"]["trio"]),
                                                              {ItemSlot.DEFAULT: GamemodeCounter(value2["weapon_pick_count"]["default"]["solo"],
                                                                                                 value2["weapon_pick_count"]["default"]["duo"],
                                                                                                 value2["weapon_pick_count"]["default"]["trio"]),
                                                               ItemSlot.MOD1: GamemodeCounter(value2["weapon_pick_count"]["mod1"]["solo"],
                                                                                              value2["weapon_pick_count"]["mod1"]["duo"],
                                                                                              value2["weapon_pick_count"]["mod1"]["trio"]),
                                                               ItemSlot.MOD2: GamemodeCounter(value2["weapon_pick_count"]["mod2"]["solo"],
                                                                                              value2["weapon_pick_count"]["mod2"]["duo"],
                                                                                              value2["weapon_pick_count"]["mod2"]["trio"])},
                                                              {ItemSlot.DEFAULT: GamemodeCounter(value2["passive_pick_count"]["default"]["solo"],
                                                                                              value2["passive_pick_count"]["default"]["duo"],
                                                                                              value2["passive_pick_count"]["default"]["trio"]),
                                                               ItemSlot.MOD1: GamemodeCounter(value2["passive_pick_count"]["mod1"]["solo"],
                                                                                              value2["passive_pick_count"]["mod1"]["duo"],
                                                                                              value2["passive_pick_count"]["mod1"]["trio"]),
                                                               ItemSlot.MOD2: GamemodeCounter(value2["passive_pick_count"]["mod2"]["solo"],
                                                                                              value2["passive_pick_count"]["mod2"]["duo"],
                                                                                              value2["passive_pick_count"]["mod2"]["trio"])},
                                                              {ItemSlot.DEFAULT: GamemodeCounter(value2["active_pick_count"]["default"]["solo"],
                                                                                              value2["active_pick_count"]["default"]["duo"],
                                                                                              value2["active_pick_count"]["default"]["trio"]),
                                                               ItemSlot.MOD1: GamemodeCounter(value2["active_pick_count"]["mod1"]["solo"],
                                                                                              value2["active_pick_count"]["mod1"]["duo"],
                                                                                              value2["active_pick_count"]["mod1"]["trio"]),
                                                               ItemSlot.MOD2: GamemodeCounter(value2["active_pick_count"]["mod2"]["solo"],
                                                                                              value2["active_pick_count"]["mod2"]["duo"],
                                                                                              value2["active_pick_count"]["mod2"]["trio"])})
                agent_stats[key] = AgentStats(key,
                                              value["mastery_level"],
                                              value["echelon_level"],
                                              AgentTimelineStats(key,
                                                                 value["lifetime_stats"]["playtime_seconds"],
                                                                 GamemodeCounter(value["lifetime_stats"]["pick_count"]["solo"],
                                                                                 value["lifetime_stats"]["pick_count"]["duo"],
                                                                                 value["lifetime_stats"]["pick_count"]["trio"]),
                                                                 GamemodeCounter(value["lifetime_stats"]["win_count"]["solo"],
                                                                                 value["lifetime_stats"]["win_count"]["duo"],
                                                                                 value["lifetime_stats"]["win_count"]["trio"]),
                                                                {ItemSlot.DEFAULT: GamemodeCounter(value["lifetime_stats"]["weapon_pick_count"]["default"]["solo"],
                                                                                                value["lifetime_stats"]["weapon_pick_count"]["default"]["duo"],
                                                                                                value["lifetime_stats"]["weapon_pick_count"]["default"]["trio"]),
                                                                 ItemSlot.MOD1: GamemodeCounter(value["lifetime_stats"]["weapon_pick_count"]["mod1"]["solo"],
                                                                                                value["lifetime_stats"]["weapon_pick_count"]["mod1"]["duo"],
                                                                                                value["lifetime_stats"]["weapon_pick_count"]["mod1"]["trio"]),
                                                                 ItemSlot.MOD2: GamemodeCounter(value["lifetime_stats"]["weapon_pick_count"]["mod2"]["solo"],
                                                                                                value["lifetime_stats"]["weapon_pick_count"]["mod2"]["duo"],
                                                                                                value["lifetime_stats"]["weapon_pick_count"]["mod2"]["trio"])},
                                                                {ItemSlot.DEFAULT: GamemodeCounter(value["lifetime_stats"]["passive_pick_count"]["default"]["solo"],
                                                                                                value["lifetime_stats"]["passive_pick_count"]["default"]["duo"],
                                                                                                value["lifetime_stats"]["passive_pick_count"]["default"]["trio"]),
                                                                 ItemSlot.MOD1: GamemodeCounter(value["lifetime_stats"]["passive_pick_count"]["mod1"]["solo"],
                                                                                                value["lifetime_stats"]["passive_pick_count"]["mod1"]["duo"],
                                                                                                value["lifetime_stats"]["passive_pick_count"]["mod1"]["trio"]),
                                                                 ItemSlot.MOD2: GamemodeCounter(value["lifetime_stats"]["passive_pick_count"]["mod2"]["solo"],
                                                                                                value["lifetime_stats"]["passive_pick_count"]["mod2"]["duo"],
                                                                                                value["lifetime_stats"]["passive_pick_count"]["mod2"]["trio"])},
                                                                {ItemSlot.DEFAULT: GamemodeCounter(value["lifetime_stats"]["active_pick_count"]["default"]["solo"],
                                                                                                value["lifetime_stats"]["active_pick_count"]["default"]["duo"],
                                                                                                value["lifetime_stats"]["active_pick_count"]["default"]["trio"]),
                                                                 ItemSlot.MOD1: GamemodeCounter(value["lifetime_stats"]["active_pick_count"]["mod1"]["solo"],
                                                                                                value["lifetime_stats"]["active_pick_count"]["mod1"]["duo"],
                                                                                                value["lifetime_stats"]["active_pick_count"]["mod1"]["trio"]),
                                                                 ItemSlot.MOD2: GamemodeCounter(value["lifetime_stats"]["active_pick_count"]["mod2"]["solo"],
                                                                                                value["lifetime_stats"]["active_pick_count"]["mod2"]["duo"],
                                                                                                value["lifetime_stats"]["active_pick_count"]["mod2"]["trio"])}),
                                                                                                seasonal_stats),
            gadget_stats: Dict[str, GadgetStats] = {}
            for key, value in json_str["gadget_stats"].items():
                seasonal_stats: Dict[Union[int, str], GadgetTimelineStats] = {}
                for key2, value2 in value["seasonal_stats"].items():
                    seasonal_stats[key2] = GadgetTimelineStats(key,
                                                              GamemodeCounter(value2["pick_count"]["solo"],
                                                                              value2["pick_count"]["duo"],
                                                                              value2["pick_count"]["trio"]))
                gadget_stats[key] = GadgetStats(key,
                                                GadgetTimelineStats(key,
                                                                    GamemodeCounter(value["lifetime_stats"]["pick_count"]["solo"],
                                                                                    value["lifetime_stats"]["pick_count"]["duo"],
                                                                                    value["lifetime_stats"]["pick_count"]["trio"])),
                                                seasonal_stats)
            return SweetUser(sweet_id,
                             display_name,
                             not_a_skill_rank,
                             account_level,
                             general_stats,
                             agent_stats,
                             gadget_stats)
        except JSONDecodeError as e:
            raise ValueError("Could not create SweetUser from JSON string.")
        except KeyError as e:
            raise ValueError("Could not create SweetUser from JSON string.")
