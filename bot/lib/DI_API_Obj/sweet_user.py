from typing import List, Union
from lib.DI_API_Obj.account_progression import AccountProgression



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

    
