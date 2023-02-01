from rlcard.games.base import Card
from .utils import make_yaniv_deck


class YanivDealer:

    def __init__(self, np_random) -> None:
        self.np_random = np_random
        self.deck = make_yaniv_deck()
        self.shuffle()

    def deal_cards(self, player, num):
        for _ in range(num):
            player.add_card(self.deck.pop())

    def flip_top_card(self):
        return self.deck.pop()

    def shuffle(self):
        self.np_random.shuffle(self.deck)

    def reset(self):
        self.deck = make_yaniv_deck()
        self.shuffle()
