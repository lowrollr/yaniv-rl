
from copy import copy
from game.card import YanivCard
from game.action import Action

import numpy as np

class YanivRound:
    def __init__(self, dealer, num_players, np_random):
        self.np_random = np_random
        self.dealer = dealer
        self.caller_id = 0

        # represents cards that have been played by a player
        self.discard_pile = [] 
        self.played_cards = np.zeros((num_players, 54))

        # cards that are available for pickup
        self.pickup_left = None 
        self.pickup_right = None
        self.next_to_discard = []

        self.known_cards = np.zeros((num_players, 54))

        self.num_players = num_players
        self.cur_player = np.random.randint(num_players)
        self.is_over = False

        self.turns = 0
        
    
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

        self.discard_pile.extend(self.next_to_discard)
        self.next_to_discard = []
        # encode recency
        self.played_cards[self.cur_player] *= 0.9

        for i, card_index in enumerate(action.played_cards):
            card = players[self.cur_player].hand[card_index]
            self.played_cards[self.cur_player][card.id] = 1
            self.known_cards[self.cur_player][card.id] = 0
            if i == 0:
                next_left_pickup = card
            elif i == 1:
                next_right_pickup = card
            else:
                self.next_to_discard.append(card)
                    
        players[self.cur_player].remove_cards(action.played_cards)
        
        if action.pickup_choice == 0:
            players[self.cur_player].add_card(self.pickup_left)
            if self.pickup_right:
                self.discard_pile.append(self.pickup_right)
            self.known_cards[self.cur_player][self.pickup_left.id] = 1
        elif action.pickup_choice == 1:
            players[self.cur_player].add_card(self.pickup_right)
            self.discard_pile.append(self.pickup_left)
            self.known_cards[self.cur_player][self.pickup_right.id] = 1
        else:
            players[self.cur_player].add_card(self.dealer.flip_top_card())
            self.discard_pile.append(self.pickup_left)
            if self.pickup_right:
                self.discard_pile.append(self.pickup_right)
        
        self.pickup_left = next_left_pickup
        self.pickup_right = next_right_pickup

        if not self.dealer.deck:
            self.replace_deck()
        
        self.cur_player = (self.cur_player + 1) % self.num_players

        self.turns += 1
        if self.turns > 1000:
            self.is_over = True
            self.caller_id = self.cur_player

        
    def get_legal_actions(self, players, player_id):
        legal_actions = []
        

        play_actions = players[player_id].get_play_actions()
        
            
        for played_cards in play_actions:
            legal_actions.append(Action(call=False, played_cards=played_cards, pickup_choice=0))
            if self.pickup_right is not None:
                legal_actions.append(Action(call=False, played_cards=played_cards, pickup_choice=1))
            legal_actions.append(Action(call=False, played_cards=played_cards, pickup_choice=2))
        if players[player_id].get_hand_score() <= 7:
            for action in list(legal_actions):
                legal_actions.append(Action(call=True, played_cards=action.played_cards, pickup_choice=action.pickup_choice))

        return legal_actions

    def get_state(self, players, player_id):
        state = {}

        player = players[player_id]
        state['hand'] = player.get_hand_state()
        state['hand_value'] = player.get_hand_score()
        state['discard_pile'] = self.discard_pile
        state['pickups'] = [self.pickup_left, self.pickup_right]
        state['next_to_discard'] = self.next_to_discard
        state['legal_actions'] = self.get_legal_actions(players, player_id)
        state['num_cards'] = []
        for player in players:
            state['num_cards'].append(len(player.hand))
        state['my_id'] = player_id
        state['known_in_hand'] = self.known_cards
        state['played_cards'] = self.played_cards
        return state

    def replace_deck(self):
        self.dealer.deck.extend(self.discard_pile)
        self.discard_pile = []
        self.dealer.shuffle()


    