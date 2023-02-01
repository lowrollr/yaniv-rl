import unittest
import numpy as np
from game.dealer import YanivDealer

from game.game import YanivGame
from game.action import decode_action
from game.card import YanivCard, Card, rank_id_values, suit_id_values, rank_point_values

from game.player import YanivPlayer
from game.round import YanivRound

class TestYanivMethods(unittest.TestCase):
    # GAME:
    def test_get_number_of_players(self):
        game = YanivGame()
        game_players = game.get_num_players()
        self.assertEqual(game_players, 4)

    def test_get_num_actions(self):
        game = YanivGame()
        num_actions = game.get_num_actions()
        self.assertEqual(num_actions, (325 * 3) + 1)

    def test_init_game(self):
        game = YanivGame()
        state, player_id = game.init_game()
        self.assertEqual(player_id, 0)
        self.assertEqual(state['num_players'], 4)
        self.assertEqual(state['current_player'], 0)
        self.assertEqual(state['num_cards'][0], 5)
        self.assertEqual(state['num_cards'][1], 5)
        self.assertEqual(state['num_cards'][2], 5)
        self.assertEqual(state['num_cards'][3], 5)
        self.assertEqual(state['my_id'], 0)
        self.assertEqual(len(state['hand']), 54)
        self.assertEqual(len(state['pickups']), 54)
        self.assertEqual(len(state['discard_pile']), 54)
        self.assertEqual(len(state['known_in_hand']), state['num_players'])
        self.assertEqual(len(state['played_cards']), state['num_players'])
        self.assertEqual(len(state['known_in_hand'][0]), 54)
        self.assertEqual(len(state['played_cards'][0]), 54)

    def test_get_player_id(self):
        game = YanivGame()
        _, player_id = game.init_game()
        self.assertEqual(game.get_player_id(), player_id)

    def test_get_legal_actions(self):
        game = YanivGame()
        game.init_game()
        legal_actions = game.get_legal_actions()
        self.assertGreater(len(legal_actions), 0)
        self.assertLess(len(legal_actions), game.get_num_actions())

    def test_step(self):
        game = YanivGame()
        game.init_game()
        legal_actions = game.get_legal_actions()
        action = legal_actions[0]
        state, player_id = game.step(action)
        current = game.round.cur_player
        self.assertEqual(player_id, current)
        self.assertGreater(len(state['discard_pile']), 0)
        self.assertGreater(len(state['pickups']), 0)

    def test_get_payoffs(self):
        game = YanivGame()
        game.init_game()
        while not game.is_over():
            legal_actions = game.get_legal_actions()
            action = np.random.choice(legal_actions)
            game.step(action)
        payoffs = game.get_payoffs()
        seen_zero = False
        for payoff in payoffs:
            if payoff == 0:
                assert not seen_zero, "Two players have 0 points"
                seen_zero = True
        assert seen_zero, "No player has 0 points"

    def test_step_back(self):
        # not implemented
        pass

    def test_is_over(self):
        game = YanivGame()
        game.init_game()
        self.assertFalse(game.is_over())

    # ACTION:
    def test_action_eq_hash(self):
        game = YanivGame()
        game.init_game()
        legal_actions = game.get_legal_actions()
        action = legal_actions[0]
        encoded_action = action.__hash__()
        equal = action == encoded_action
        self.assertTrue(equal)
    
    def test_action_decode_encode(self):
        game = YanivGame()
        game.init_game()
        legal_actions = game.get_legal_actions()
        action = legal_actions[0]
        encode_action = action.__hash__()
        decoded_action = decode_action(encode_action)
        self.assertTrue(encode_action == decoded_action == action)

    # CARD:
    def test_card(self):
        card = YanivCard(Card('S', 'A'))
        self.assertTrue(card.rank_value == card.value == rank_point_values['A'])
        self.assertEqual(card.id, 0)

        card = YanivCard(Card('BJ', ''))
        self.assertTrue(card.rank_value == card.value == 0)
        self.assertEqual(card.id, 52)

    # DEALER:
    def test_dealer_init(self):
        game = YanivGame()
        dealer = game.dealer
        self.assertEqual(len(dealer.deck), 54)
        game.init_game()
        self.assertEqual(len(dealer.deck), 54 - (5 * game.num_players) - 1)

    def test_dealer_deal(self):
        cards_to_deal = 5
        game = YanivGame()
        game.init_game()
        dealer = game.dealer
        dealer.deal_cards(game.players[0], cards_to_deal)
        self.assertEqual(len(dealer.deck), 54 - (5 * game.num_players) - 1 -  cards_to_deal)
        self.assertEqual(len(game.players[0].hand), 5 + cards_to_deal)

    def test_dealer_flip_top(self):
        game = YanivGame()
        dealer = game.dealer
        dealer.flip_top_card()
        self.assertEqual(len(dealer.deck), 54 - 1)

    # JUDGER:
    def test_get_points(self):
        game = YanivGame()
        game.init_game()
        judger = game.judger
        points = judger.get_points(game.players, 0)
        self.assertIn(0, points)
        self.assertEqual(len(points), game.num_players)
    
    # PLAYER:
    def test_init(self):
        player = YanivPlayer(0, None)
        self.assertEqual(player.player_id, 0)
        self.assertEqual(player.hand, [])
    
    def test_hand_value(self):
        player = YanivPlayer(0, None)
        player.hand = [YanivCard(Card('S', 'A')), YanivCard(Card('S', '2'))]
        self.assertEqual(player.get_hand_score(), 3)

        player.hand = []
        self.assertEqual(player.get_hand_score(), 0)
    
    def test_get_hand_state(self):
        player = YanivPlayer(0, None)
        hand = [YanivCard(Card('S', '2')), YanivCard(Card('S', 'A'))]
        player.hand = [YanivCard(Card('S', '2')), YanivCard(Card('S', 'A'))]
        hand_state = player.get_hand_state()
        self.assertEqual(hand_state, hand[::-1])

    def get_play_actions(self):
        player = YanivPlayer(0, None)
        player.hand = [YanivCard(Card('S', '2')), YanivCard(Card('S', 'A'))]
        actions = player.get_play_actions()
        self.assertEqual(len(actions), 2)

        # Test straights
        player.hand = [YanivCard(Card('S', '2')), YanivCard(Card('S', 'A')), YanivCard(Card('BJ', ''))]

        actions = player.get_play_actions()
        self.assertEqual(len(actions), 4)

        player.hand = [YanivCard(Card('S', '2')), YanivCard(Card('S', '4')), YanivCard(Card('BJ', ''))]
        actions = player.get_play_actions()
        self.assertEqual(len(actions), 4)

        player.hand = [YanivCard(Card('S', '2')), YanivCard(Card('S', '4')), YanivCard(Card('S', '3'))]
        actions = player.get_play_actions()
        self.assertEqual(len(actions), 4)

        player.hand = [YanivCard(Card('S', '2')), YanivCard(Card('S', '5')), YanivCard(Card('RJ', '')), YanivCard(Card('BJ', ''))]
        actions = player.get_play_actions()
        self.assertEqual(len(actions), 7)

        # Test pairs
        player.hand = [YanivCard(Card('S', '2')), YanivCard(Card('H', '2'))]
        actions = player.get_play_actions()
        self.assertEqual(len(actions), 3)

        player.hand = [YanivCard(Card('S', '2')), YanivCard(Card('H', '2')), YanivCard(Card('BJ', ''))]
        actions = player.get_play_actions()
        self.assertEqual(len(actions), 4)

        player.hand = [YanivCard(Card('S', '2')), YanivCard(Card('H', '2')), YanivCard(Card('D', '2'))]
        actions = player.get_play_actions()
        self.assertEqual(len(actions), 6)

        player.hand = [YanivCard(Card('S', '2')), YanivCard(Card('H', '2')), YanivCard(Card('D', '2')), YanivCard(Card('C', '2'))]
        actions = player.get_play_actions()
        self.assertEqual(len(actions), 14)

        player.hand = [YanivCard(Card('BJ', '')), YanivCard(Card('RJ', ''))]
        actions = player.get_play_actions()
        self.assertEqual(len(actions), 3)

    # ROUND:
    def test_round_init(self):
        rando = np.random.RandomState()
        round = YanivRound(YanivDealer(rando), 4, rando)
        self.assertEqual(round.num_players, 4)
        self.assertEqual(round.discard_pile, [])
        self.assertEqual(round.cur_player, 0)
        self.assertEqual(round.num_players, 4)
        self.assertEqual(round.is_over, False)
        self.assertEqual(len(round.played_cards), 4)
        self.assertEqual(round.played_cards[0].shape, (54,))
        self.assertEqual(len(round.played_cards), 4)
        self.assertEqual(round.known_cards[0].shape, (54,))
    
    def test_flip_top(self):
        rando = np.random.RandomState()
        round = YanivRound(YanivDealer(rando), 4, rando)
        top = round.flip_top_card()
        self.assertEqual(len(round.dealer.deck), 54 - 1)
        self.assertEqual(round.pickup_left, top)

    def test_proceed_round(self):
        rando = np.random.RandomState()
        round = YanivRound(YanivDealer(rando), 4, rando)
        round.flip_top_card()
        player0 = YanivPlayer(0, rando)
        player0.hand = [YanivCard(Card('S', '2')), YanivCard(Card('S', 'A'))]
        player1 = YanivPlayer(1, rando)
        round.proceed_round([player0, player1], decode_action(0))
        self.assertEqual(round.cur_player, 1)
        self.assertEqual(round.is_over, False)
        self.assertEqual(round.played_cards[0].shape, (54,))
        self.assertGreater(round.played_cards[0].sum(), 0)
        self.assertEqual(round.known_cards[0].shape, (54,))

    def test_get_legal_actions(self):
        player = YanivPlayer(0, None)
        player.hand = [YanivCard(Card('S', '2')), YanivCard(Card('S', 'A'))]
        actions = player.get_play_actions()

        rando = np.random.RandomState()
        round = YanivRound(YanivDealer(rando), 4, rando)
        round.flip_top_card()


        round_actions = round.get_legal_actions([player], 0)
        self.assertEqual(len(round_actions), len(actions) * 2 + 1)

        player = YanivPlayer(0, None)
        player.hand = [YanivCard(Card('S', 'T')), YanivCard(Card('S', 'A'))]
        actions = player.get_play_actions()

        rando = np.random.RandomState()
        round = YanivRound(YanivDealer(rando), 4, rando)
        round.flip_top_card()


        round_actions = round.get_legal_actions([player], 0)
        self.assertEqual(len(round_actions), len(actions) * 2)


        

        rando = np.random.RandomState()
        round = YanivRound(YanivDealer(rando), 4, rando)
        round.pickup_left = YanivCard(Card('S', '2'))
        round.pickup_right = YanivCard(Card('S', '3'))

        round_actions = round.get_legal_actions([player], 0)
        self.assertEqual(len(round_actions), len(actions) * 3)

    def test_get_state(self):
        rando = np.random.RandomState()
        round = YanivRound(YanivDealer(rando), 4, rando)
        round.flip_top_card()
        player0 = YanivPlayer(0, rando)
        player0.hand = [YanivCard(Card('S', '2')), YanivCard(Card('S', 'A'))]
        player1 = YanivPlayer(1, rando)
        player1.hand = [YanivCard(Card('H', '2')), YanivCard(Card('H', 'A'))]

        state = round.get_state([player0, player1], 0)
        self.assertEqual(len(state['hand']), 54)
        self.assertEqual(state['hand'].sum(), 2)
        self.assertEqual(len(state['num_cards']), 2)
        self.assertEqual(state['pickups'].sum(), 1)
        self.assertEqual(sum(state['num_cards']), 4)

    def test_replace_deck(self):
        rando = np.random.RandomState()
        round = YanivRound(YanivDealer(rando), 4, rando)
        top = round.flip_top_card()

        round.discard_pile = [YanivCard(Card('S', '2')), YanivCard(Card('S', 'A'))]
        round.replace_deck()
        self.assertEqual(len(round.dealer.deck), 55)
        self.assertEqual(round.pickup_left, top)


        
if __name__ == '__main__':
    unittest.main()