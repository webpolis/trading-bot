from enum import Enum

from com.cryptobot.schemas.schema import Schema


class TokenSource(Enum):
    COINGECKO = 1
    FTX = 2


class Token(Schema):
    def __init__(self, symbol, name, address, market_cap):
        self.symbol = symbol
        self.name = name
        self.address = address
        self.market_cap = market_cap
