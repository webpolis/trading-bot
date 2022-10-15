from typing import List

from com.cryptobot.classifiers.classifier import Classifier
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.formatters import tx_parse
from com.cryptobot.utils.tx_queue import TXQueue


class TXClassifier(Classifier):
    def __init__(self, cls=__name__, cache: TXQueue = None):
        super().__init__(cls)

        self.cache = cache

    def parse(self, items) -> List[Tx]:
        if (len(items) > 0 and type(items[0]) == Tx):
            return items

        items = super().parse(items)
        txs: List[Tx] = list(map(lambda item: tx_parse(item), items))

        return txs

    def filter(self, items: List[Tx]) -> List[Tx]:
        return super().filter(items)

    def classify(self, items) -> List[Tx]:
        items = self.parse(items)
        items = self.filter(items)

        return items