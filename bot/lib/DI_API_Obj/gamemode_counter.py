from typing import Union
from lib.DI_API_Obj.gamemode import GameMode

class GamemodeCounter:
    solo: Union[int, None]
    duo: Union[int, None]
    trio: Union[int, None]

    def __init__(self, solo: Union[int, None] = None, duo: Union[int, None] = None, trio: Union[int, None] = None):
        self.solo = solo
        self.duo = duo
        self.trio = trio

    def __str__(self) -> str:
        return f"Solo: {self.solo}, Duo: {self.duo}, Trio: {self.trio}"
    
    def get_total(self) -> int:
        return (self.solo if self.solo is not None else 0) + (self.duo if self.duo is not None else 0) + (self.trio if self.trio is not None else 0)

    def get_all_team_modes(self) -> int:
        return (self.duo if self.duo is not None else 0) + (self.trio if self.trio is not None else 0)
    
    def get_gamemode(self, gamemode: GameMode) -> Union[int, None]:
        if gamemode == GameMode.SOLO:
            return self.solo
        elif gamemode == GameMode.DUO:
            return self.duo
        elif gamemode == GameMode.TRIO:
            return self.trio
        return None