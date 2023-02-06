
from dataclasses import dataclass
from typing import List
import itertools

HAND_ACTION_IDS = dict()

for i in range(1, 3):
    for play in itertools.combinations(range(5), i):
        if len(play) == 2:
            for j in range(0, 4):
                for combo in itertools.combinations(range(5), j):
                    if set(play).isdisjoint(set(combo)):
                        HAND_ACTION_IDS[''.join([str(c) for c in play + combo])] = len(HAND_ACTION_IDS)
        else:
            HAND_ACTION_IDS[''.join([str(c) for c in play])] = len(HAND_ACTION_IDS)



ID_HAND_ACTION_MAP = {v: k for k, v in HAND_ACTION_IDS.items()}

CALL_ACTION_ID = 3 * len(HAND_ACTION_IDS)


@dataclass
class Action:
    call: bool
    pickup_choice: int  # 0: left, 1: right, 2: deck
    # indices of cards in hand that player wishes to play
    played_cards: List[int]

    def __hash__(self) -> int:
        x = int(self.call)
        y = self.pickup_choice
        z = HAND_ACTION_IDS[''.join([str(c) for c in self.played_cards])]
        action_id = (x * 3 * len(HAND_ACTION_IDS)) + (y * len(HAND_ACTION_IDS)) + z
        return action_id
    
    def __eq__(self, x):
        if type(x) is int:
            return self.__hash__() == x
        return self.__hash__() == x.__hash__()
    
    def __gt__(self, x):
        return self.__hash__() > x.__hash__()


def decode_action(action_id: int) -> Action:
    played_cards_id = action_id % len(HAND_ACTION_IDS)
    action_id = action_id // len(HAND_ACTION_IDS)
    pickup_id = action_id % 3
    action_id = action_id // 3
    call_id = action_id % 2
    return Action(call=bool(call_id), pickup_choice=pickup_id, played_cards=[int(c) for c in ID_HAND_ACTION_MAP[played_cards_id]])
