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