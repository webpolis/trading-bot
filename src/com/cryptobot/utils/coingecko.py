from importlib.metadata import metadata
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


def get_coin_by_address(address):
    address = address.lower()

    for coin in cg_coins:
        if ('ethereum' in coin['platforms'] and coin['platforms']['ethereum'].lower() == address) \
                or ('polygon-pos' in coin['platforms'] and coin['platforms']['polygon-pos'].lower() == address) \
                or ('arbitrum-one' in coin['platforms'] and coin['platforms']['arbitrum-one'].lower() == address):
            platforms = coin['platforms']
            metadata = {
                'symbol': coin['symbol'],
                'name': coin['name'],
                'address_ethereum': platforms['ethereum'].lower() if 'ethereum' in platforms else None,
                'address_arbitrum': platforms['arbitrum-one'].lower() if 'arbitrum-one' in platforms else None,
                'address_polygon': platforms['polygon-pos'].lower() if 'polygon-pos' in platforms else None
            }

            return metadata

    return {}


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
