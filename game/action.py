
from dataclasses import dataclass
from typing import List

@dataclass
class Action:
    call: bool
    pickup_choice: int # 0: left, 1: right, 2: deck
    played_cards: List[int] # indices of cards in hand that player wishes to play