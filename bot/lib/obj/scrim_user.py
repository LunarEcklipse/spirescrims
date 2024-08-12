from typing import Union, List

class ScrimUser:
    master_id: int
    discord_id: Union[int, None]
    twitch_id: Union[int, None]

    def __init__(self, master_id: int, discord_id: Union[int, None] = None, twitch_id: Union[int, None] = None):
        self.master_id = master_id
        self.discord_id = discord_id
        self.twitch_id = twitch_id

    def __str__(self) -> str:
        return f"ScrimUser(master_id={self.master_id}, discord_id={self.discord_id}, twitch_id={self.twitch_id})"