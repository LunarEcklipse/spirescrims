from typing import Union

class GamemodeCounter:
    solo: Union[int, None]
    duo: Union[int, None]
    trio: Union[int, None]

    def __init__(self, solo: Union[int, None] = None, duo: Union[int, None] = None, trio: Union[int, None] = None):
        self.solo = solo
        self.duo = duo
        self.trio = trio