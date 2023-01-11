import rlcard
from rlcard.envs.registration import register
from rlcard.utils import get_device, Logger, reorganize, tournament, plot_curve
from rlcard.agents import RandomAgent

from rlcard.agents import DQNAgent
import torch
import argparse
import os

def train(args):
    device = get_device()
    env = rlcard.make('yaniv', config={'game_num_players': 4})

    agents = [DQNAgent(num_actions=env.num_actions,
                        state_shape=env.state_shape[0],
                        mlp_layers=[64,64],
                        device=device)]
    agent = agents[0]
    for _ in range(1, env.num_players):
        agents.append(RandomAgent(num_actions=env.num_actions))
    env.set_agents(agents)
    with Logger(log_dir='./') as logger:
        for episode in range(args.num_episodes):
            trajectories, payoffs = env.run(is_training=True)
            trajectories = reorganize(trajectories, payoffs)
            for ts in trajectories[0]:
                agent.feed(ts)
            if episode % args.evaluate_every == 0:
                logger.log_performance(env.timestep, tournament(env, args.num_games)[0])
        plot_curve(logger.csv_path, logger.fig_path, 'DQN Performance')
    
    
    save_path = os.path.join(args.log_dir, 'model.pth')
    torch.save(agent, save_path)
    print('Model saved in', save_path)

if __name__ == '__main__':

    parser = argparse.ArgumentParser("DQN example in RLCard")
    parser.add_argument('--algorithm', type=str, default='dqn', choices=['dqn'])
    parser.add_argument('--cuda', type=str, default='')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--num_episodes', type=int, default=5000)
    parser.add_argument('--num_games', type=int, default=2000)
    parser.add_argument('--evaluate_every', type=int, default=100)
    parser.add_argument('--log_dir', type=str, default='./')
    register(
        env_id='yaniv',
        entry_point='env:YanivEnv',
    )
    args = parser.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    rlcard.make('yaniv', config={'game_num_players': 4})
    train(args)

