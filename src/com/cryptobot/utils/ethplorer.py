import logging
from backoff import expo, on_exception
from operator import itemgetter
from com.cryptobot.config import Config
from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.utils.request import HttpRequest
from ratelimit import RateLimitException, limits

request = HttpRequest()
settings = Config().get_settings()
max_threads = settings.runtime.classifiers.SwapClassifier.max_concurrent_threads
max_calls = int(300/max_threads)
period_per_thread = int(30/max_threads)


@on_exception(expo, RateLimitException, max_tries=1, max_time=10)
@limits(calls=max_calls, period=period_per_thread)
def get_token_info(token):
    response = request.get(settings.endpoints.ethplorer.token_info.format(
        address=token.address, api_key=settings.endpoints.ethplorer.api_key))
    address = response.get('address', None)
    name = response.get('name', None)
    symbol = response.get('symbol', None)
    decimals = response.get('decimals', None)
    price = response.get('price', {})

    return {
        'address': address.lower(),
        'name': name,
        'symbol': symbol.upper(),
        'decimals': int(decimals),
        'price_usd': price.get('rate') if type(price) == dict else None,
        'market_cap': price.get('marketCapUsd') if type(price) == dict else None
    }


@on_exception(expo, RateLimitException, max_tries=1, max_time=10)
@limits(calls=max_calls, period=period_per_thread)
def get_address_info(address):
    response = request.get(settings.endpoints.ethplorer.address_info.format(
        address=address, api_key=settings.endpoints.ethplorer.api_key))
    eth = response.get('ETH', None)
    tokens = response.get('tokens', [])

    if type(eth) == dict:
        tokens.append({
            'tokenInfo': {
                'symbol': 'ETH',
                'name': 'Ethereum',
                'price': eth.get('price', None),
                'decimals': 18,
                'address': '0x0000000000000000000000000000000000000000'
            },
            'balance': eth.get('balance', None)
        })

    return tokens


ethplorer_logger = PrettyLogger(HttpRequest.__name__, logging.INFO)
