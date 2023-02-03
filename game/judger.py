
class YanivJudger:


    @staticmethod
    def get_points(players, caller_id):
        scores = [0 for _ in range(len(players))]

        lowest_score = 51
        winning_players = {}
        for player in players:
            score = player.get_hand_score()
            if score < lowest_score:
                lowest_score = score
                winning_players = {player.player_id}
            elif score == lowest_score:
                winning_players.add(player.player_id)
            scores[player.player_id] = score

        if len(winning_players) == 1 and caller_id in winning_players:
            scores[caller_id] = 0
        else:
            for p in winning_players:
                scores[p] = 0
            scores[caller_id] = 30

        return scores
