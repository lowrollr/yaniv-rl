



from game.action import CALL_ACTION_ID
from game.player import get_valid_hand_actions
from game.utils import score_hand, cards_to_bin_array

import numpy as np
import itertools

PTS = np.clip(((np.arange(54) % 13) + 1) * (np.arange(54) < 52), a_min=None, a_max=10)


class PseudoOptimalAgent:
    def __init__(self, num_actions) -> None:
        self.num_actions = num_actions
        self.use_raw = False

    @staticmethod
    def step(state):
        # choose the action that minimizes the hand's value after the next time we discard 
        # i.e. if we had a ten and see another in pickup, we should pickup the new ten and choose a different card to discard
        legal_actions = state['raw_legal_actions']
        state = state['raw_obs']
        hand_value = score_hand(state['hand'])

        # choose whether or not to call yaniv
        if hand_value <= 7:
            call = True
            # check if we know another player has a lower or equal_hand_value
            for i in range(len(state['known_in_hand'])):
                if i != state['my_id'] and len(state['known_in_hand'][i]) == state['num_cards'][i]:  
                    op_known_hand_value = np.sum(PTS * state['known_in_hand'][i])
                    if op_known_hand_value <= hand_value:
                        call = False
                        break
            
            if call:
                return CALL_ACTION_ID
        
        # choose which cards to play
        

        hand = state['hand']
        possible_cards_in_deck = np.ones(54) - (np.sum(state['known_in_hand'], axis=0) + cards_to_bin_array(state['discard_pile']) + cards_to_bin_array(state['next_to_discard']) + cards_to_bin_array(hand) + cards_to_bin_array(state['pickups']))
        ev_top = np.sum(PTS * possible_cards_in_deck) / np.sum(possible_cards_in_deck)
        scores = []
        for action in legal_actions:
            valid_indices = np.ones(len(hand), dtype=bool)
            for hi in action.played_cards:
                valid_indices[hi] = False
            
            new_hand = [hand[i] for i in range(len(hand)) if valid_indices[i]] + ([state['pickups'][action.pickup_choice]] if action.pickup_choice < 2 else [])
            new_hand_value = score_hand(new_hand)
            if action.pickup_choice < 2:
                most_played = (max([len(played_cards) for played_cards in get_valid_hand_actions(new_hand)]) - 1) + (len(action.played_cards) - 1)
                scores.append((most_played, -new_hand_value, action))
            else:
                most_played = (len(action.played_cards) - 1)
                # get ev of top card
    
                scores.append((most_played, -(new_hand_value + ev_top), action))

        return max(scores)[2].__hash__()
    
    def eval_step(self, state):
        return self.step(state), {}


