from typing import List

from com.cryptobot.classifiers.classifier import Classifier
from com.cryptobot.schemas.token import Token


class TokenClassifier(Classifier):
    def parse(self, items) -> List[Token]:
        return super().parse(items)

    def classify(self, items) -> List[Token]:
        return super().classify(items)
