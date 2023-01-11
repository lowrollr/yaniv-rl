
from rlcard.envs import Env
from game.game import YanivGame
from game.action import Action

import numpy as np
import itertools


DEFAULT_GAME_CONFIG = {
    'game_num_players': 4
}

PERM_ID_MAP = {''.join([str(c) for c in p]): i for i, p in enumerate(itertools.permutations(range(5)))}

class YanivEnv(Env):
    def __init__(self, config=None):
        self.name = 'yaniv'
        self.config = DEFAULT_GAME_CONFIG if config is None else config
        num_players = config['game_num_players']
        self.game = YanivGame(num_players=num_players)
        super().__init__(config)
        self.state_shape = [[3, num_players, 54]]
        self.action_shape = [[2,3,325]]

    def _extract_state(self, state):
        obs = np.zeros((3, self.game.num_players, 54))

        obs[0][0] = state['hand']
        obs[0][1] = state['pickups']
        obs[0][2] = state['discard_pile']
        for i, num_cards in state['num_cards']:
            obs[0][3][5*i+num_cards] = 1
        obs[0][3][5*self.game.num_players+state['my_id']] = 1

        obs[1] = state['known_in_hand']
        obs[2] = state['played_cards'] 

        encoded_legal_actions = np.zeros((2,3,325))
        for action in state['legal_actions']:
            x = int(action.call)
            y = action.pickup_choice
            z = PERM_ID_MAP[''.join([str(c) for c in action.played_cards])]
            encoded_legal_actions[x][y][z] = 1

        extracted_state = {
            'obs': obs,
            'legal_actions': encoded_legal_actions,
            'raw_obs': state,
            'raw_legal_actions': [a for a in state['legal_actions']]
        }
        return extracted_state

    def _decode_action(self, action_id):
        return Action(call=action_id[0], played_cards=action_id[1], pickup_choice=action_id[2])

    def get_payoffs(self):
        return np.array(self.game.get_payoffs())