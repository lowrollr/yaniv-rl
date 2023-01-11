from typing import List
from rlcard.utils.utils import init_54_deck
from .card import YanivCard
import numpy as np

def make_yaniv_deck():
    return [YanivCard(card) for card in init_54_deck()]

def cards_to_bin_array(cards: List[YanivCard]):
    
    array = np.zeros(54)
    for card in cards:
        if card is not None:
            array[card.id] = 1
    return array