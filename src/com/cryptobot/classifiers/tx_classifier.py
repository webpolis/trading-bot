from typing import List

from com.cryptobot.classifiers.classifier import Classifier
from com.cryptobot.schemas.tx import Tx


class TXClassifier(Classifier):
    def parse(self, items):
        pass

    def filter(self, items):
        pass

    def classify(self, items) -> List[Tx]:
        items = self.parse(items)
        items = self.filter(items)

        return items
