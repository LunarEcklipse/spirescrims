from lib.DI_API_Obj.gamemode_counter import GamemodeCounter

class GadgetStats:
    gadget_name: str
    pick_count: GamemodeCounter

    def __init__(self, gadget_name: str, pick_count: GamemodeCounter):
        self.gadget_name = gadget_name
        self.pick_count = pick_count