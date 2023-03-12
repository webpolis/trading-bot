import logging
import re
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
def get_token_info(address):
    global lock

    with lock:
        response = request.get(
            settings.endpoints.etherscan.token.format(address=address), raw=True)
        soup = BeautifulSoup(response, "html.parser")
        overview = soup.find('div', {'id': 'ContentPlaceHolder1_tr_valuepertoken'})
        overview = re.sub(r'[\r\n]+', '', overview.text,
                          flags=re.MULTILINE | re.IGNORECASE)
        price_usd = re.sub(r'.*Price[\s\t]*\$([\d\.\,]+).*$',
                           '\\1', overview, flags=re.MULTILINE | re.IGNORECASE)
        price_usd = float(price_usd.replace(',', ''))
        market_cap = re.sub(r'.*Market Cap[\s\t\n\r]*\$([\d\.\,]+).*$',
                            '\\1', overview, flags=re.MULTILINE | re.IGNORECASE)
        market_cap = float(market_cap.replace(',', ''))

        return {
            'address': address,
            'name': None,
            'symbol': None,
            'decimals': None,
            'price_usd': price_usd,
            'market_cap': market_cap
        }


explorer_logger = PrettyLogger(HttpRequest.__name__, logging.INFO)
