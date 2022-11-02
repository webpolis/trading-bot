import json
from backoff import expo, on_exception
from com.cryptobot.config import Config
from com.cryptobot.utils.path import get_data_path
from com.cryptobot.utils.request import HttpRequest
from ratelimit import RateLimitException, limits

request = HttpRequest()
settings = Config().get_settings()
max_threads = settings.runtime.classifiers.SwapClassifier.max_concurrent_threads
max_calls = int(50/max_threads)
period_per_thread = int(60/max_threads)

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


@on_exception(expo, RateLimitException, max_tries=1, max_time=10)
@limits(calls=max_calls, period=period_per_thread)
def get_markets(coin_id, currency='usd'):
    response = request.get(settings.endpoints.coingecko.markets, {
        'ids': coin_id,
        'vs_currency': currency,
        'order': 'market_cap_desc',
        'sparkline': 'false'
    })

    return response[0] if len(response) > 0 else None
