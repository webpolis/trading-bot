from typing import List
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.schemas.tx import Tx


class SwapClassifier(TXClassifier):
    def __init__(self):
        super()

    def parse(self, items: List[Tx]) -> List[Tx]:
        return items

    def filter(self, items: List[Tx]) -> List[Tx]:
        print(items)

        return items
