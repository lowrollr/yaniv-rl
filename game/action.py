
from dataclasses import dataclass
from typing import List
import itertools

PERM_ID_MAP = {''.join([str(c) for c in p]): i for i, p in enumerate(
    itertools.chain.from_iterable(itertools.permutations(range(5), r) for r in range(1, 6)))}
ID_PERM_MAP = {v: k for k, v in PERM_ID_MAP.items()}


CALL_ACTION_ID = 3 * 325


@dataclass
class Action:
    call: bool
    pickup_choice: int  # 0: left, 1: right, 2: deck
    # indices of cards in hand that player wishes to play
    played_cards: List[int]

    def __hash__(self) -> int:
        if self.call:
            return CALL_ACTION_ID
        else:
            y = self.pickup_choice
            z = PERM_ID_MAP[''.join([str(c) for c in self.played_cards])]
            action_id = (y * 325) + z
            return action_id


def decode_action(action_id: int) -> Action:
    played_cards_id = action_id % 325
    action_id = action_id // 325
    pickup_id = action_id % 3
    action_id = action_id // 3
    call_id = action_id
    if call_id:
        return Action(call=True, pickup_choice=None, played_cards=None)
    return Action(call=bool(call_id), pickup_choice=pickup_id, played_cards=[int(c) for c in ID_PERM_MAP[played_cards_id]])
