
from game.card import YanivCard
from game.action import Action
from game.utils import cards_to_bin_array
import numpy as np

class YanivRound:
    def __init__(self, dealer, num_players, np_random):
        self.np_random = np_random
        self.dealer = dealer
        self.caller_id = 0

        # represents cards that have been played but are unable for pickup
        self.discard_pile = [] 
        self.played_cards = [np.zeros(54) for _ in range(num_players)]

        # cards that are available for pickup
        self.pickup_left = None 
        self.pickup_right = None

        self.num_players = num_players
        self.cur_player = 0
        self.is_over = False

        
    
    def flip_top_card(self):
        top = self.dealer.flip_top_card()
        self.pickup_left = top
        return top

    def proceed_round(self, players, action: Action):
        if action.call == True:
            self.is_over = True
            self.caller_id = self.cur_player
            return
        
        next_left_pickup = None
        next_right_pickup = None

        # encode recency
        self.played_cards[self.cur_player] *= 0.9

        for i, card_index in enumerate(action.played_cards):
            card = players[self.cur_player].hand.pop(card_index)
            self.played_cards[self.cur_player][card.id] = 1
            if i != 0 and i != len(action.played_cards) - 1:
                self.discard_pile.append(card)
            else:
                if i == 0:
                    next_left_pickup = card
                else:
                    next_right_pickup = card
        
        if action.pickup_choice == 0:
            players[self.cur_player].hand.append(self.pickup_left)
            self.discard_pile.append(self.pickup_right)
        elif action.pickup_choice == 1:
            players[self.cur_player].hand.append(self.pickup_right)
            self.discard_pile.append(self.pickup_left)
        else:
            players[self.cur_player].hand.append(self.dealer.flip_top_card())
            self.discard_pile.append(self.pickup_left)
            self.discard_pile.append(self.pickup_right)
        
        self.pickup_left = next_left_pickup
        self.pickup_right = next_right_pickup

        if not self.dealer.deck():
            self.replace_deck()

    def get_legal_actions(self, players, player_id):
        legal_actions = []
        if players[player_id].hand_value() <= 7:
            legal_actions.append(Action(call=True, played_cards=[], pickup_choice=None))

        play_actions = players[player_id].get_play_actions()

        for played_cards in play_actions:
            legal_actions.append(Action(call=False, played_cards=played_cards, pickup_choice=0))
            if self.pickup_right is not None:
                legal_actions.append(Action(call=False, played_cards=played_cards, pickup_choice=1))
            legal_actions.append(Action(call=False, played_cards=played_cards, pickup_choice=2))

        return legal_actions

    def get_state(self, players, player_id):
        state = {}

        player = players[player_id]
        state['hand'] = cards_to_bin_array(player.get_hand_state())
        state['hand_value'] = player.get_hand_score()
        state['discard_pile'] = cards_to_bin_array(self.discard_pile)
        state['pickups'] = cards_to_bin_array([self.pickup_left, self.pickup_right])
        state['legal_actions'] = self.get_legal_actions(players, player_id)
        state['num_cards'] = []
        for player in players:
            state['num_cards'].append(len(player.hand))
        state['my_id'] = player_id
        state['known_in_hand'] = [cards_to_bin_array(self.known[i]) for i in self.num_players]
        state['played_cards'] = self.played_cards
        return state

    def replace_deck(self):
        self.dealer.deck.extend(self.discard_pile)
        self.discard_pile = []
        self.dealer.shuffle()


    