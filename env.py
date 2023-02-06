
from collections import OrderedDict

from rlcard.envs import Env
from game.game import YanivGame
from game.action import decode_action
from game.utils import cards_to_bin_array
import numpy as np


DEFAULT_GAME_CONFIG = {
    'game_num_players': 4,
    'allow_step_back': False,
    'seed': 0
}


class YanivEnv(Env):
    def __init__(self, config=None):
        self.name = 'yaniv'
        self.config = DEFAULT_GAME_CONFIG if config is None else config
        num_players = self.config.get('game_num_players', 4)
        self.game = YanivGame(self.config.get('seed', 0), num_players=num_players)
        self.allow_step_back = False
        super().__init__(self.config)
        self.state_shape = [[3, max(5, self.game.num_players), 54]]
        self.action_shape = [[2,3,85]]
        

    def _extract_state(self, state):
        obs = np.zeros((3, max(5, self.game.num_players), 54))

        obs[0,0] = cards_to_bin_array(state['hand'])
        obs[0,1] = cards_to_bin_array(state['pickups'])
        obs[0,2] = cards_to_bin_array(state['discard_pile'])
        obs[0,3] = cards_to_bin_array(state['next_to_discard'])

        offset = state['my_id']
        for i, num_cards in enumerate(state['num_cards']):
            # player's id should go first
            
            index = (i - offset) % self.game.num_players
            obs[0,4,index] = num_cards / 5

        obs[1,:self.game.num_players] = np.roll(state['known_in_hand'], shift=-offset, axis=0)
        obs[2,:self.game.num_players] = np.roll(state['played_cards'], shift=-offset, axis=0)

        legal_ids = {}
        for action in state['legal_actions']:
            legal_ids[action.__hash__()] = None

        extracted_state = {
            'obs': obs,
            'legal_actions': OrderedDict(legal_ids),
            'raw_obs': state,
            'raw_legal_actions': state['legal_actions']
        }
        return extracted_state

    def _decode_action(self, action_id):
        return decode_action(action_id)

    def get_payoffs(self):
        payoffs = self.game.get_payoffs()
        payoff_sum = sum(payoffs)
        return [((payoff_sum - payoff)/(len(payoffs)-1)) - payoff for payoff in payoffs]
    def _get_legal_actions(self):
        legal_actions = self.game.get_legal_actions()
        legal_ids = {action.__hash__(): None for action in legal_actions}
        return OrderedDict(legal_ids)
