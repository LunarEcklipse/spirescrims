from typing import Union, List, Dict
from lib.DI_API_Obj.agent_stats import AgentTimelineStats
from lib.DI_API_Obj.gamemode_counter import GamemodeCounter
from lib.DI_API_Obj.gamemode import GameMode

class TimelineStatWrapper:
    '''Wraps the timed statistics for an account, both lifetime and seasonal.'''
    eliminations: GamemodeCounter
    deaths: GamemodeCounter
    matches_played: GamemodeCounter
    matches_won: GamemodeCounter
    time_played: GamemodeCounter
    agent_stats: Dict[str, AgentTimelineStats]

    def calculate_win_rate(self, gamemode: Union[GameMode, None] = None) -> Union[float, None]:
        '''Calculates the win rate for a specific gamemode.'''
        matches_played = self.matches_played.get_total() if gamemode is None else self.matches_played.get_gamemode(gamemode)
        matches_won = self.matches_won.get_total() if gamemode is None else self.matches_won.get_gamemode(gamemode)
        if matches_played is None or matches_won is None:
            return None
        if matches_played == 0:
            return 0.0
        return matches_won / matches_played
    
    def calculate_kd_ratio(self, gamemode: Union[GameMode, None] = None) -> Union[float, None]:
        '''Calculates the kill-death ratio for a specific gamemode.'''
        eliminations = self.eliminations.get_total() if gamemode is None else self.eliminations.get_gamemode(gamemode)
        deaths = self.deaths.get_total() if gamemode is None else self.deaths.get_gamemode(gamemode)
        if eliminations is None or deaths is None:
            return None
        if deaths == 0:
            return eliminations
        return eliminations / deaths
    
    def calculate_kpm(self, gamemode: Union[GameMode, None] = None) -> Union[float, None]:
        '''Calculates the kills per minute for a specific gamemode.'''
        eliminations = self.eliminations.get_total() if gamemode is None else self.eliminations.get_gamemode(gamemode)
        time_played = self.time_played.get_total() if gamemode is None else self.time_played.get_gamemode(gamemode)
        if eliminations is None or time_played is None:
            return None
        if time_played == 0:
            return 0.0
        return eliminations / (time_played / 60)
    
    def calculate_avg_kills_per_game(self, gamemode: Union[GameMode, None] = None) -> Union[float, None]:
        '''Calculates the average kills per game for a specific gamemode.'''
        eliminations = self.eliminations.get_total() if gamemode is None else self.eliminations.get_gamemode(gamemode)
        matches_played = self.matches_played.get_total() if gamemode is None else self.matches_played.get_gamemode(gamemode)
        if eliminations is None or matches_played is None:
            return None
        if matches_played == 0:
            return 0.0
        return eliminations / matches_played
    
    def calculate_average_time_per_match(self, gamemode: Union[GameMode, None] = None) -> Union[float, None]:
        '''Calculates the average time per match for a specific gamemode.'''
        time_played = self.time_played.get_total() if gamemode is None else self.time_played.get_gamemode(gamemode)
        matches_played = self.matches_played.get_total() if gamemode is None else self.matches_played.get_gamemode(gamemode)
        if time_played is None or matches_played is None:
            return None
        if matches_played == 0:
            return 0.0
        return time_played / matches_played

class AccountStats:
    '''Wraps the account statistics for a user.'''
    lifetime: TimelineStatWrapper
    seasonal: Dict[int, TimelineStatWrapper] # Dict of keys with each season and values of AccountStatsWrapper