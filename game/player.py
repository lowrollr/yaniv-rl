import copy
from itertools import combinations
from typing import List
from rlcard.games.base import Card
from game.utils import score_hand
from game.card import YanivCard



def check_pairs(hand: List[YanivCard]) -> List[List[int]]:
    hand.sort(key=lambda card: (card.rank_value, card.suit))
    actions = []
    sames = []
    for i in range(len(hand)):
        if not sames:
            sames.append([i])
        elif hand[sames[-1][0]].rank_id_value == hand[i].rank_id_value:
            sames[-1].append(i)
        else:
            sames.append([i])

    for same in sames:
        
        if len(same) == 1:
            actions.append(same)
        elif len(same) == 2:
            actions.append(same)
        else:
            set_same = set(same)
            for combo in combinations(same, 2):
                set_combo = set(combo)
                others = set_same.difference(set_combo)
                for l in range(1, len(others)+1):
                    for combo2 in combinations(others, l):
                        actions.append(list(combo) + list(combo2))
                actions.append(list(combo))
            for value in same:
                actions.append([value])
    return actions

def check_straights(hand: List[YanivCard]) -> List[List[int]]:
    actions = []
    jokers = 0
    for card in hand:
        if card.rank_value == 0:
            jokers += 1
        else:
            break
    
    straight_cards = sorted(hand[jokers:], key = lambda x: (x.suit, x.rank_id_value))

    def append_valid_straight(straight):
        actions.append([straight[0]] + [straight[-1]] + sorted(straight[1:-1], key=lambda x: (straight_cards[x].rank_id_value, x)))

    def find_straights(start, end, cur, jokers, tot_jokers):
        if end >= len(straight_cards):
            return

        last_card = straight_cards[cur[-1]]
        cur_card = straight_cards[end]

        last_suit = last_card.suit
        cur_suit = cur_card.suit

        last_rank = last_card.rank_id_value
        cur_rank = cur_card.rank_id_value

        if cur_suit == last_suit:
            if cur_rank == last_rank + 1:
                cur.append(jokers + end)
                if end - start >= 2:
                    append_valid_straight(copy.copy(cur))
                find_straights(start, end + 1, cur, jokers, tot_jokers)
                cur.pop()
            elif cur_rank == last_rank + 2 and jokers > 0:
                cur.append(tot_jokers - jokers)
                cur.append(jokers + end)
                if end - start >= 2:
                    append_valid_straight(copy.copy(cur))
                find_straights(start, end + 1, cur, jokers - 1, tot_jokers)
                cur.pop()
                cur.pop()
            elif cur_rank == last_rank + 3 and jokers > 1:
                cur.append(0)
                cur.append(1)
                cur.append(jokers + end)
                if end - start >= 2:
                    append_valid_straight(copy.copy(cur))
                find_straights(start, end + 1, cur, jokers - 2, tot_jokers)
                cur.pop()
                cur.pop()
                cur.pop()

        find_straights(start, end + 1, cur, jokers, tot_jokers)

    for i in range(jokers, len(straight_cards)):
        find_straights(i, i + 1, [jokers + i], jokers, jokers)

    return actions

def get_valid_hand_actions(hand: List[YanivCard]) -> List[List[int]]:
    actions = []
    actions.extend(check_pairs(hand))
    actions.extend(check_straights(hand))
    return actions

class YanivPlayer:
    def __init__(self, player_id, np_random) -> None:
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []

    def get_hand_state(self):
        self.hand.sort(key=lambda card: (card.rank_value, card.suit))
        return self.hand

    def get_hand_score(self):
        return score_hand(self.hand)

    def remove_cards(self, indices):
        indices = set(indices)
        new_hand = []
        for i, card in enumerate(self.hand):
            if i not in indices:
                new_hand.append(card)
        self.hand = new_hand

    def add_card(self, card):
        self.hand.append(card)

    def get_play_actions(self):
        # we can play all single cards in hand
        actions = []

        # we can play all collections of one or more card of the same card from our hand

        actions.extend(check_pairs(self.hand))


        # we can play all straights of 3 or more cards of the same suit from our hand
        # we can augment straights with jokers to fill in one or more missing cards
        # i.e. 10 of Spades -> Joker -> J of Spades is a valid straight, and so is 10 of Spades -> Joker -> Joker -> Q of Spades is also valid
        # so is 10 of Spades -> Joker -> J of Spades -> Joker -> K of Spades    
        actions.extend(check_straights(self.hand))
        

        return actions
