
from rlcard.games.base import Card

rank_point_values = {
    'A': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'T': 10,
    'J': 10,
    'Q': 10,
    'K': 10
}

suit_id_values = {
    'S': 0,
    'H': 1,
    'D': 2,
    'C': 3
}

rank_id_values = {
    'A': 0,
    '2': 1,
    '3': 2,
    '4': 3,
    '5': 4,
    '6': 5,
    '7': 6,
    '8': 7,
    '9': 8,
    'T': 9,
    'J': 10,
    'Q': 11,
    'K': 12
}

class YanivCard(Card):
    def __init__(self, card: Card) -> None:
        super().__init__(card.suit, card.rank)
        self.value = self._value()
        self.id = self._id()
        self.rank_value = rank_point_values[self.rank] if self.suit != 'BJ' and self.suit != 'RJ' else 0

    def _value(self):
        if self.suit == 'BJ' or self.suit == 'RJ':
            return 0
        else:
            return rank_point_values[self.rank]

    def _id(self):
        if self.suit == 'BJ':
            return 52
        elif self.suit == 'RJ':
            return 53
        else:
            return suit_id_values[self.suit] * 13 + rank_id_values[self.rank]