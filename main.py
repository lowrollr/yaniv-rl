import rlcard
from rlcard.envs.registration import register

if __name__ == '__main__':
    register(
        env_id='yaniv',
        entry_point='env:YanivEnv',
    )
    rlcard.make('yaniv', config={'game_num_players': 4})