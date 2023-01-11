
from collections import OrderedDict
from rlcard.envs import Env
from game.game import YanivGame
from game.action import Action, PERM_ID_MAP, ID_PERM_MAP, decode_action

import numpy as np
import itertools


DEFAULT_GAME_CONFIG = {
    'game_num_players': 4
}



class YanivEnv(Env):
    def __init__(self, config=None):
        self.name = 'yaniv'
        self.config = DEFAULT_GAME_CONFIG if config is None else config
        num_players = config['game_num_players']
        self.game = YanivGame(num_players=num_players)
        super().__init__(config)
        self.state_shape = [[3, num_players, 54]]
        self.action_shape = [[4,325]]

    def _extract_state(self, state):
        obs = np.zeros((3, self.game.num_players, 54))

        obs[0][0] = state['hand']
        obs[0][1] = state['pickups']
        obs[0][2] = state['discard_pile']
        for i, num_cards in enumerate(state['num_cards']):
            obs[0][3][5*i+num_cards] = 1
        obs[0][3][5*self.game.num_players+state['my_id']] = 1

        obs[1] = state['known_in_hand']
        obs[2] = state['played_cards'] 

        legal_ids = {}
        for action in state['legal_actions']:
            legal_ids[action.__hash__()] = None

        extracted_state = {
            'obs': obs,
            'legal_actions': OrderedDict(legal_ids),
            'raw_obs': state,
            'raw_legal_actions': [a for a in state['legal_actions']]
        }
        return extracted_state

    def _decode_action(self, action_id):
        return decode_action(action_id)

    def get_payoffs(self):
        return np.array(self.game.get_payoffs())

    def _get_legal_actions(self, legal_actions):
        return super()._get_legal_actions()