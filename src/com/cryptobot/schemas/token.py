from enum import Enum
import json

from com.cryptobot.schemas.schema import Schema
from com.cryptobot.utils.path import get_data_path

# initialize data
with open(get_data_path() + 'coingecko_coins.json') as f:
    cg_coins = json.load(f)

    f.close()

with open(get_data_path() + 'ftx_coins.json') as f:
    ftx_coins = json.load(f)

    f.close()


class TokenSource(Enum):
    COINGECKO = 1
    FTX = 2
    FTX_LENDING = 3


class Token(Schema):
    def __init__(self, symbol, name, market_cap, price_usd, address=None):
        self.symbol = symbol
        self.name = name
        self.market_cap = market_cap
        self.address = address
        self.price_usd = price_usd

        if self.address is None:
            # populate ERC20 address
            token = next((coin for coin in cg_coins if
                          coin['symbol'].upper() == symbol
                          and coin.get('platforms', None) != None
                          and coin['platforms'].get('ethereum', None) != None), None)

            # 1st try
            if token != None:
                self.address = token['platforms']['ethereum'].lower() if \
                    token['platforms'].get(
                    'ethereum', None) != None else None

            # 2nd try
            if self.address is None:
                token = next((coin for coin in cg_coins if coin['id'].upper() == symbol
                              and coin.get('erc20Contract', None) != None), None)

                if token != None:
                    self.address = token['erc20Contract'].lower()
