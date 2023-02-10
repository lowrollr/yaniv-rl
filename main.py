import rlcard
from rlcard.envs.registration import register
from rlcard.utils import get_device, Logger, reorganize, tournament, plot_curve
from rlcard.agents import RandomAgent

from rlcard.agents import DQNAgent
import torch
import numpy as np
import argparse
import os
from copy import deepcopy


def train(args):
    device = get_device()
    env = rlcard.make('yaniv')
    eval_env = rlcard.make('yaniv')

    agents = [DQNAgent(num_actions=env.num_actions,
                       state_shape=env.state_shape[0],
                       mlp_layers=[64, 64],
                       device=device) for _ in range(env.num_players)]
    
    env.set_agents(agents)

    eval_agents = [agents[0]] + [RandomAgent(num_actions=eval_env.num_actions) for _ in range(eval_env.num_players - 1)]
    eval_env.set_agents(eval_agents)

    with Logger(log_dir='./') as logger:
        for episode in range(args.num_episodes):
            trajectories, payoffs = env.run(is_training=True)
            trajectories = reorganize(trajectories, payoffs)
            for ts in trajectories[0]:
                for agent in agents:
                    agent.feed(ts)
            
            
            if episode % args.evaluate_every == 0:
                # grab best agent 
                payoffs = tournament(env, args.agent_selection_games)
                best = np.argmax(payoffs)
                env.set_agents([agents[best]] + [deepcopy(agents[best]) for _ in range(env.num_players - 1)])
                
                logger.log_performance(
                    env.timestep, tournament(eval_env, args.num_games)[0])
        plot_curve(logger.csv_path, logger.fig_path, 'DQN Performance')

    save_path = os.path.join(args.log_dir, f'model_gen.pth')
    torch.save(agent, save_path)
    print('Model saved in', save_path)


if __name__ == '__main__':

    parser = argparse.ArgumentParser("DQN example in RLCard")
    parser.add_argument('--algorithm', type=str,
                        default='dqn', choices=['dqn'])
    parser.add_argument('--cuda', type=str, default='')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--num_episodes', type=int, default=5000)
    parser.add_argument('--agent_selection_games', type=int, default=100)
    parser.add_argument('--evaluation_games', type=int, default=100)
    parser.add_argument('--evaluate_every', type=int, default=100)
    parser.add_argument('--log_dir', type=str, default='./')
    parser.add_argument('--num_epochs', type=int, default='1')
    register(
        env_id='yaniv',
        entry_point='env:YanivEnv',
    )
    args = parser.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    rlcard.make('yaniv', config={'game_num_players': 4})
    train(args)
