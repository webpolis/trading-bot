import logging
from backoff import expo, on_exception
from com.cryptobot.config import Config
from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.utils.request import HttpRequest
from ratelimit import RateLimitException, limits

request = HttpRequest()
settings = Config().get_settings()
max_threads = settings.runtime.classifiers.SwapClassifier.max_concurrent_threads
max_calls = int(600/max_threads)
period_per_thread = int(60/max_threads)


@on_exception(expo, RateLimitException, max_tries=1, max_time=10)
@limits(calls=max_calls, period=period_per_thread)
def get_price(token):
    price = None

    response = request.get(settings.endpoints.ethplorer.token_info.format(
        address=token.address, api_key=settings.endpoints.ethplorer.api_key))
    price = response.get('price', False)
    price = response.get('price', {}).get(
        'rate', None) if response is not None and price != False else None

    return price


ethplorer_logger = PrettyLogger(HttpRequest.__name__, logging.INFO)
