from typing import List

from com.cryptobot.classifiers.classifier import Classifier
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.formatters import tx_parse


class TXClassifier(Classifier):
    def parse(self, items) -> List[Tx]:
        if (len(items) > 0 and type(items[0]) == Tx):
            return items

        items = super().parse(items)
        txs: List[Tx] = list(map(lambda item: tx_parse(item), items))

        for tx in txs:
            print(tx.decode_input())

        return txs

    def filter(self, items: List[Tx]) -> List[Tx]:
        return super().filter(items)

    def classify(self, items) -> List[Tx]:
        items = self.parse(items)
        items = self.filter(items)

        return items
