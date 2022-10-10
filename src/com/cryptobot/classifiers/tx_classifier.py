from typing import List

from com.cryptobot.classifiers.classifier import Classifier
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.formatters import tx_parse


class TXClassifier(Classifier):
    def parse(self, items: List[Tx]) -> List[Tx]:
        items = super().parse(items)
        txs: List[Tx] = [tx_parse(tx) for tx in items]

        return txs

    def filter(self, items: List[Tx]) -> List[Tx]:
        return super().filter(items)

    def classify(self, items) -> List[Tx]:
        items = self.parse(items)
        items = self.filter(items)

        return items
