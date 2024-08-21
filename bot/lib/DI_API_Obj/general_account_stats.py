from lib.DI_API_Obj.gamemode_counter import GamemodeCounter

class GeneralAccountStats:
    eliminations: GamemodeCounter
    deaths: GamemodeCounter
    matches_played: GamemodeCounter
    matches_won: GamemodeCounter
    time_played: GamemodeCounter

    def __init__(self, eliminations: GamemodeCounter, deaths: GamemodeCounter, matches_played: GamemodeCounter, matches_won: GamemodeCounter, time_played: GamemodeCounter):
        self.eliminations = eliminations
        self.deaths = deaths
        self.matches_played = matches_played
        self.matches_won = matches_won
        self.time_played = time_played