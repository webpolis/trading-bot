from typing import List

from com.cryptobot.classifiers.token_classifier import TokenClassifier
from com.cryptobot.schemas.token import Token, TokenSource
from com.cryptobot.utils.formatters import token_parse


class CoingeckoTokensClassifier(TokenClassifier):
    def __init__(self):
        super()

    def filter(self, items):
        return items

    def parse(self, items):
        items.sort(key=lambda item: item['market_cap'], reverse=True)

        tokens: List[Token] = [token_parse(
            token, TokenSource.COINGECKO) for token in items]

        return tokens
