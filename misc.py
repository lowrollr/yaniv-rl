
from dataclasses import dataclass

@dataclass
class Card:
    # Spades = 0, Hearts = 1, Diamonds = 2, Clubs = 3, Joker = 4
    suit: int 
    # Ace = 0, 2 = 1, 3 = 2, ..., King = 12
    value: int
