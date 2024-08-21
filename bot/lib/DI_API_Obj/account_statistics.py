from typing import Union, List, Dict
from lib.DI_API_Obj.agent_stats import AgentTimelineStats
from lib.DI_API_Obj.gamemode_counter import GamemodeCounter

class TimelineStatWrapper:
    '''Wraps the timed statistics for an account, both lifetime and seasonal.'''
    eliminations: GamemodeCounter
    deaths: GamemodeCounter
    matches_played: GamemodeCounter
    matches_won: GamemodeCounter
    time_played: GamemodeCounter
    agent_stats: Dict[str, AgentTimelineStats]

class AccountStats:
    '''Wraps the account statistics for a user.'''
    lifetime: TimelineStatWrapper
    seasonal: Dict[int, TimelineStatWrapper] # Dict of keys with each season and values of AccountStatsWrapper