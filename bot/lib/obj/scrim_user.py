from typing import Union, List

class ScrimUser:
    scrim_id: str
    username: str
    discord_id: Union[int, None]
    sweet_id: Union[str, None]
    twitch_id: Union[str, None]
    mmr: Union[int, None]
    priority: Union[int, None]

    def __init__(self, scrim_id: str, username: Union[str, None] = None, discord_id: Union[int, None] = None, sweet_id: Union[str, None] = None, twitch_id: Union[str, None] = None, mmr: Union[int, None] = None, priority: Union[int, None] = None) -> None:
        self.scrim_id = scrim_id
        self.username = username
        self.discord_id = discord_id
        self.sweet_id = sweet_id
        self.twitch_id = twitch_id
        self.mmr = mmr
        self.priority = priority
    
    def __str__(self) -> str:
        return f"ScrimUser: {self.scrim_id} - Discord ID: {self.discord_id} - Sweet ID: {self.sweet_id} - Twitch ID: {self.twitch_id}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other: object) -> bool:
        if type(other) == str:
            return self.scrim_id == other
        elif type(other) == ScrimUser:
            return self.scrim_id == other.scrim_id
        return False