from typing import Union, List

class AccountStatsWrapper:
    class AgentStats:
        agent: str
        playtime_seconds: int
        pick_count: int
        win_count: int

        
    class AgentPlayTime:
        agent: str
        playtime_seconds: int

        def __init__(self, agent: str, playtime_seconds: int):
            self.agent = agent
            self.playtime_seconds = playtime_seconds
        
        def __str__(self) -> str:
            return f"AgentPlayTime(agent={self.agent}, playtime_seconds={str(self.playtime_seconds)})"

    class AgentPickCounter:
        agent: str
        pick_count: int

        def __init__(self, agent: str, pick_count: int):
            self.agent = agent
            self.pick_count = pick_count
        
        def __str__(self) -> str:
            return f"AgentPickCounter(agent={self.agent}, pick_count={str(self.pick_count)})"
        
    class GadgetPickCounter:
        gadget: str
        pick_count: str

        def __init__(self, gadget: str, pick_count: int):
            self.gadget = gadget
            self.pick_count = pick_count

        def __str__(self) -> str:
            return f"GadgetPickCounter(gadget={self.gadget}, pick_count={str(self.pick_count)})"

    class AgentItemPickCounter:
        agent: str
        item: str
        pick_count: int

        def __init__(self, agent: str, item: str, pick_count: int):
            self.agent = agent
            self.item = item
            self.pick_count = pick_count
        
        def __str__(self) -> str:
            return f"AgentItemPickCounter(agent={self.agent}, item={self.item}, pick_count={str(self.pick_count)})"
    
        @staticmethod
        def determine_agent_identity(key_str: str) -> str:
            '''Determines the agent from the key string.
            ### Parameters
            - `key_str`: The key string from the DI API.
            ### Returns
            The agent name.
            '''
            return key_str.split("_")[0]
        
        @staticmethod
        def determine_item_identity(key_str: str) -> str:
            '''Determines the item from the key string.
            ### Parameters
            - `key_str`: The key string from the DI API.
            ### Returns
            The item name.
            '''
            return key_str.split("_")[1]
        
    class ModeStatWrapper:
        solo: Union[int, None]
        duo: Union[int, None]
        trio: Union[int, None]

        def __init__(self, solo: Union[int, None], duo: Union[int, None], trio: Union[int, None]):
            self.solo = solo
            self.duo = duo
            self.trio = trio
    
    eliminations: ModeStatWrapper
    deaths: ModeStatWrapper
    matches_played: ModeStatWrapper
    matches_won: ModeStatWrapper
    time_played: ModeStatWrapper
    
    agent_play_time: dict # Dict of keys with each agent and values of AgentPlayTime
    agent_pick_counter: dict # Dict of keys with each agent and values of AgentPickCounter
    agent_win_counter: dict
    agent_weapon_pick_counter: dict
    agent_passive_pick_counter: dict
    agent_expertise_pick_counter: dict
    gadget_pick_counter: dict # Dict of keys with each gadget and values of GadgetPickCounter

class AccountStats:
    lifetime: AccountStatsWrapper
    seasonal: dict # Dict of keys with each season and values of AccountStatsWrapper
