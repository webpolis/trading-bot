import json
from com.cryptobot.config import Config
from com.cryptobot.utils.path import get_data_path
from com.cryptobot.utils.request import HttpRequest

request = HttpRequest()
settings = Config().get_settings()

with open(get_data_path() + 'coingecko_coins.json') as f:
    cg_coins = json.load(f)

    f.close()

with open(get_data_path() + 'coingecko_stablecoins.json') as f:
    cg_stablecoins = json.load(f)

    f.close()


def get_coin(symbol):
    return next(iter([coin for coin in cg_coins if
                      coin['symbol'].upper() == symbol]), None)


def is_stablecoin(symbol):
    stablecoin = next(iter([coin for coin in cg_stablecoins if
                            coin['symbol'].upper() == symbol]), None)

    return stablecoin != None


def get_markets(page, currency='usd'):
    response = request.get(settings.endpoints.coingecko.markets, {
        'vs_currency': currency,
        'order': 'market_cap_desc,volume_desc',
        'sparkline': 'false',
        'per_page': 250,
        'page': page,
    })

    return response if response != None and len(response) > 0 else None
