

import random
from typing import List, Tuple
from agent import Agent
from misc import Card



class Game:
    def __init__(self) -> None:
        self.num_players = 4
        self.players = [Agent(i) for i in range(self.num_players)]
        self.cur_player = random.randint(0, self.num_players - 1)

        self.deck = [
            Card(suit, value) for suit in range(4) for value in range(13)
        ]
        # Yaniv is played with two jokers (wild cards)
        self.deck.append(Card(4, 0))
        self.deck.append(Card(4, 0))

        random.shuffle(self.deck)
        for player in self.players:
            for _ in range(5):
                player.add_card(self.deck.pop())
            player.id = self.players.index(player)

        self.discarded = []

        self.pickup = self.discarded[0]
    
    def play_game(self) -> None:
        
        while True:
            if len(self.deck) == 0:
                for player in self.players:
                    player.handle_shuffle(self.discarded)
                self.deck = self.discarded
                self.discarded = []
                random.shuffle(self.deck)
            
            called_yaniv, pickup_choice, played_cards = self.players[self.cur_player].make_turn_decisions()

            if called_yaniv:
                scores = self.resolve_game_end(self.cur_player)
                for player_id, score in scores:
                    self.players[player_id].handle_game_result(score)
                break
            else:
                self.play_cards(played_cards, pickup_choice)

    def resolve_game_end(self, caller_id: int) -> List[Tuple[int, int]]:
        scores = [0 for _ in range(self.num_players)]

        lowest_score = (51)
        winning_players = {}
        for player in self.players:
            score = player.get_hand_score()
            if score < lowest_score:
                lowest_score = score
                winning_players = {player.id}
            elif score == lowest_score:
                winning_players.add(player.id)
            scores[player.id] = score
        
        if len(winning_players) == 1 and caller_id in winning_players:
            scores[caller_id] = 0
        else:
            for player in self.players:
                if player.id in winning_players:
                    scores[player.id] = 0
                else:
                    scores[player.id] = lowest_score
            scores[caller_id] = 30
        
        return [(i,s) for i,s in enumerate(scores)]

        
    def play_cards(self, cards: List[Card], pickup_choice = int) -> Card:

        new_card = None
        if pickup_choice == 0:
            new_card = self.pickup[0]
        elif pickup_choice == 1:
            new_card = self.pickup[-1]
        else:
            new_card = self.deck.pop()

        self.discarded.extend(self.pickup)
        self.pickup = cards
        
        for player in range(self.num_players):
            if player != self.cur_player:
                player.update_cards_played(cards, self.cur_player)
            if pickup_choice < 2:
                player.update_cards_picked_up(new_card, self.cur_player)

        self.players[self.cur_player].add_card(new_card)

        self.cur_player = (self.cur_player + 1) % self.num_players

        
        
        

    