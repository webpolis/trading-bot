from typing import List

from com.cryptobot.classifiers.token import TokenClassifier
from com.cryptobot.schemas.token import Token, TokenSource
from com.cryptobot.utils.formatters import token_parse


class FTXTokensClassifier(TokenClassifier):
    def __init__(self):
        super().__init__(__name__)

    def parse(self, items, token_source: TokenSource):
        tokens: List[Token] = [token_parse(
            token, token_source) for token in items]

        return tokens

    def classify(self, items, token_source: TokenSource):
        items = self.parse(items, token_source)
        items = self.filter(items)

        return items
