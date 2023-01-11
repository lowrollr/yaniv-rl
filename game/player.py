import copy
from itertools import permutations, combinations
from rlcard.games.base import Card
from game.card import YanivCard

class YanivPlayer:
    def __init__(self, player_id, np_random) -> None:
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []

    def get_hand_state(self):
        self.hand.sort(key=lambda card: (card.rank_value, card.suit))
        return self.hand

    def get_hand_score(self):
        return sum([card.rank_value for card in self.hand])

    def get_play_actions(self):
        # we can play all single cards in hand
        actions = []

        self.hand.sort(key=lambda card: (card.rank_value, card.suit))

        # we can play all collections of one or more card of the same card from our hand

        

        sames = []

        for i in range(len(self.hand)):
            for j in range(i, len(self.hand)):
                if self.hand[i].rank == self.hand[j].rank:
                    sames.append([k for k in range(i, j + 1)])
                else:
                    break

        # we can play all straights of 3 or more cards of the same suit from our hand
        # we can augment straights with jokers to fill in one or more missing cards
        # i.e. 10 of Spades -> Joker -> J of Spades is a valid straight, and so is 10 of Spades -> Joker -> Joker -> Q of Spades is also valid
        # so is 10 of Spades -> Joker -> J of Spades -> Joker -> K of Spades
        
        for combo in sames:
            if len(combo) < 2:
                actions.append(combo)
            else:
                # get all combinations of 2 cards from the combo, which take the first and last positions
                # put the rest of the cards in the middle
                for first in range(0, len(combo) - 1):
                    for last in range(first + 1, len(combo)):
                        actions.append([combo[first]] + [l for l in combo if l not in {combo[first], combo[last]}] + [combo[last]])
                    


        jokers = 0
        for card in self.hand:
            if card.rank_value == 0:
                jokers += 1
            else:
                break

        valid_straights = []

        def find_straights(start, end, cur, jokers, tot_jokers):
            if end >= len(self.hand):
                return

            last_card = self.hand[cur[-1]]
            cur_card = self.hand[end]

            last_suit = last_card.suit
            cur_suit = cur_card.suit

            last_rank = last_card.rank_value
            cur_rank = cur_card.rank_value

            if cur_suit == last_suit:
                if cur_rank == last_rank + 1:
                    cur.append(end)
                    if end - start >= 2:
                        valid_straights.append(copy.copy(cur))
                    find_straights(start, end + 1, cur, jokers, tot_jokers)
                    cur.pop()
                elif cur_rank == last_rank + 2 and jokers > 0:
                    cur.append(tot_jokers - jokers)
                    cur.append(end)
                    if end - start >= 2:
                        valid_straights.append(copy.copy(cur))
                    find_straights(start, end + 1, cur, jokers - 1, tot_jokers)
                    cur.pop()
                    cur.pop()
                elif cur_rank == last_rank + 3 and jokers > 1:
                    cur.append(tot_jokers - jokers)
                    cur.append(tot_jokers - jokers + 1)
                    cur.append(end)
                    if end - start >= 2:
                        valid_straights.append(copy.copy(cur))
                    find_straights(start, end + 1, cur, jokers - 2, tot_jokers)
                    cur.pop()
                    cur.pop()
                    cur.pop()

            find_straights(start, end + 1, cur, jokers, tot_jokers)

        for i in range(jokers, len(self.hand)):
            find_straights(i, i + 1, [i], jokers, jokers)

        actions.extend(valid_straights)

        return actions



        
                        
        
        
