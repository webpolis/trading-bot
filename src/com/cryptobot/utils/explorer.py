import logging
from threading import RLock
from backoff import expo, on_exception
from bs4 import BeautifulSoup
from com.cryptobot.config import Config
from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.utils.request import HttpRequest
from ratelimit import RateLimitException, limits

lock = RLock()
request = HttpRequest()
settings = Config().get_settings()
max_threads = settings.runtime.classifiers.SwapClassifier.max_concurrent_threads
max_calls = int(300/max_threads)
period_per_thread = int(30/max_threads)


@on_exception(expo, RateLimitException, max_tries=3, max_time=10)
@limits(calls=max_calls, period=period_per_thread)
def get_token_info(token):
    global lock

    with lock:
        response = request.get(
            settings.endpoints.etherscan.token.format(address=token.address), raw=True)
        soup = BeautifulSoup(response, "html.parser")
        value_per_token = soup.find('.ContentPlaceHolder1_tr_valuepertoken')

        return {
            'address': token.address,
            'name': None,
            'symbol': None,
            'decimals': int(0),
            'price_usd': None,
            'market_cap': None
        }


explorer_logger = PrettyLogger(HttpRequest.__name__, logging.INFO)
