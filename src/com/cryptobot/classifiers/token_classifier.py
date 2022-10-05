from typing import List

from com.cryptobot.classifiers.classifier import Classifier
from com.cryptobot.schemas.token import Token


class TokenClassifier(Classifier):
    def parse(self, items):
        pass

    def filter(self, items):
        pass

    def classify(self, items) -> List[Token]:
        items = self.filter(items)
        items = self.parse(items)

        return items
