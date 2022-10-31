from typing import List

from com.cryptobot.classifiers.token import TokenClassifier
from com.cryptobot.schemas.token import Token, TokenSource
from com.cryptobot.utils.formatters import token_parse


class CoinmarketcapTokensClassifier(TokenClassifier):
    def __init__(self):
        super().__init__(__name__)

    def filter(self, items):
        return items

    def parse(self, items):
        tokens: List[Token] = [token_parse(
            token, TokenSource.COINMARKETCAP) for token in items]

        return tokens
