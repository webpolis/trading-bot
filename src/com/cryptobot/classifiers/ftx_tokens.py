from typing import List

from com.cryptobot.classifiers.token_classifier import TokenClassifier
from com.cryptobot.schemas.token import Token, TokenSource
from com.cryptobot.utils.formatters import token_parse


class FTXTokensClassifier(TokenClassifier):
    def __init__(self):
        super()

    def filter(self, items):
        return [token for token in items if token['baseCurrency'] != None and token['type'] == 'spot']

    def parse(self, items):
        tokens: List[Token] = [token_parse(
            token, TokenSource.FTX) for token in items]

        return tokens