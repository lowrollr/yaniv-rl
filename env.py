
from collections import OrderedDict

from rlcard.envs import Env
from game.game import YanivGame
from game.action import decode_action

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
        self.action_shape = [[4, 85]]
        

    def _extract_state(self, state):
        obs = np.zeros((3, max(5, self.game.num_players), 54))

        obs[0,0] = state['hand']
        obs[0,1] = state['pickups']
        obs[0,2] = state['discard_pile']
        obs[0,3] = state['next_to_discard']


        for i, num_cards in enumerate(state['num_cards']):
            # player's id should go first
            offset = state['my_id']
            index = (i - offset) % self.game.num_players
            obs[0,4,index] = num_cards / 5

        obs[1,:self.game.num_players] = state['known_in_hand']
        obs[2,:self.game.num_players] = state['played_cards']

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
        return -1 * np.array(self.game.get_payoffs())

    def _get_legal_actions(self):
        legal_actions = self.game.get_legal_actions()
        legal_ids = {action.__hash__(): None for action in legal_actions}
        return OrderedDict(legal_ids)
