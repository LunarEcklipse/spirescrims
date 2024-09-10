from typing import List
from lib.obj.scrim_format import ScrimFormat

class ScrimMatchGroups:
    format: ScrimFormat
    lobby_sizes: List[int]
    waitlist_playercount: int

    def __init__(self, format: ScrimFormat, lobby_sizes: List[int], waitlist_playercount: int) -> None:
        self.format = format
        self.lobby_sizes = lobby_sizes
        if type(self.lobby_sizes) == list:
            self.lobby_sizes.sort(reverse=True)
        self.waitlist_playercount = waitlist_playercount
