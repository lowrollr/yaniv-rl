import unittest
import numpy as np
from env import YanivEnv
from rlcard.agents.random_agent import RandomAgent

class TestYanivEnv(unittest.TestCase):
    def test_reset_and_extract_state(self):
        env = YanivEnv()
        state, _ = env.reset()
        self.assertEqual(state['obs'].shape, (3, 4, 54))

    def test_get_legal_actions(self):
        env = YanivEnv()
        env.reset()
        legal_actions = env._get_legal_actions()
        # with default seed = 0, there are 10 legal actions
        self.assertEqual(len(legal_actions), 10)

    def test_step(self):
        env = YanivEnv()
        state, _ = env.reset()
        action = np.random.choice(list(state['legal_actions'].keys()))
        _, player_id = env.step(action)
        self.assertEqual(player_id, env.game.round.cur_player)

    def test_step_back(self):
        pass

    def test_run(self):
        env = YanivEnv()
        env.reset()
        env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
        trajectories, payoffs = env.run(is_training=False)
        self.assertEqual(len(trajectories), env.num_players)
        self.assertEqual(len(payoffs), env.num_players)
        # payoffs are tested elsewhere
        env.reset()
        env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
        trajectories, payoffs = env.run(is_training=True)
        self.assertEqual(len(trajectories), env.num_players)
        self.assertEqual(len(payoffs), env.num_players)

    def test_decode_action(self):
        env = YanivEnv()
        env.reset()
        legal_actions = env._get_legal_actions()
        for legal_action in legal_actions:
            action = env._decode_action(legal_action)
            self.assertEqual(action.__hash__(), legal_action)
        
    def test_get_perfect_information(self):
        pass
        


if __name__ == '__main__':
    unittest.main()