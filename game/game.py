
import numpy as np
from game.dealer import YanivDealer
from game.round import YanivRound
from game.player import YanivPlayer
from game.judger import YanivJudger


class YanivGame:
    def __init__(self, num_players=4):
        self.np_random = np.random.RandomState()



        self.num_players = num_players
        self.judger = YanivJudger()
    

    def configure(self, game_config):
        self.num_players = game_config["game_num_players"]

    def init_game(self):

        self.dealer = YanivDealer(self.np_random)

        self.players = [YanivPlayer(i, self.np_random) for i in range(self.num_players)]

        for player in self.players:
            self.dealer.deal_cards(player, 5)

        self.round = YanivRound(self.dealer, self.num_players, self.np_random)

        self.round.flip_top_card()


        player_id = self.round.cur_player

        state = self.get_state(player_id)

        return state, player_id
    
    def step(self, action):
        self.round.proceed_round(self.players, action)
        player_id = self.round.cur_player
        state = self.get_state(player_id)
        return state, player_id
    
    def get_state(self, player_id):
        state = self.round.get_state(self.players, player_id)
        state['num_players'] = self.get_num_players()
        state['current_player'] = self.round.cur_player

        return state

    def get_payoffs(self):
        return self.judger.get_points(self.players, self.round.caller_id)

    def get_legal_actions(self):
        return self.round.get_legal_actions(self.players, self.round.cur_player)

    def get_num_players(self):
        return self.num_players

    def is_over(self):
        return self.round.is_over
    
    def get_num_actions(self):
        return 2 * 3 * 325

    def get_player_id(self):
        return self.round.cur_player