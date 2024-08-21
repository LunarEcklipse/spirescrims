from typing import Union, List
from lib.DI_API_Obj.agent_stats import AgentStats

class TimelineStatWrapper:
    '''Wraps the timed statistics for an account, both lifetime and seasonal.'''
    


class AccountStats:
    '''Wraps the account statistics for a user.'''
    seasonal: dict # Dict of keys with each season and values of AccountStatsWrapper