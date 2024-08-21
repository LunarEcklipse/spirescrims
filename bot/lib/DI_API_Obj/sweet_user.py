from typing import List, Union

class AccountProgression:
        class CharacterProgression:
            character: str
            mastery_level: int
            echelon_level: int

            def __init__(self, character: str, mastery_level: int = 0, echelon_level: int = 0):
                self.character = character
                self.mastery_level = mastery_level
                self.echelon_level = echelon_level
                
        account_level: int
        character_progression: dict # Dict of keys with each character and values of CharacterProgression

        def __init__(self, account_level: int, character_progression: dict):
            self.account_level = account_level
            self.character_progression = AccountProgression.wrap_character_progression(character_progression)

        @staticmethod
        def wrap_character_progression(progression: dict) -> dict:
            '''Wraps the character progression dict in CharacterProgression objects.
            ### Parameters
            - `progression`: The dictionary to wrap. From the DI API, this is the 'progression' key.
            ### Returns
            A dictionary with the same keys as the input, but with the values wrapped in CharacterProgression objects.
            '''
            if type(progression) is not dict:
                return {}
            out = {}
            for key, value in progression.items():
                if type(value) is not dict:
                    continue
                # The value dict must contain the keys "mastery" and "echelon"
                if "mastery" not in value or "echelon" not in value:
                    continue
                out[key] = AccountProgression.CharacterProgression(key, value["mastery"], value["echelon"])
            return out

class AccountStatsWrapper:
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

    not_a_skill_rank: int
    account_progression: AccountProgression

    def __init__(self, sweet_id: str,
                 display_name: str,
                 not_a_skill_rank: int,
                 account_level: int):
        super().__init__(sweet_id, display_name)
        self.not_a_skill_rank = not_a_skill_rank

    
