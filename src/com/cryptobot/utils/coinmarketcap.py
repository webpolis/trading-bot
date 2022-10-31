from datetime import datetime
import json
from backoff import expo, on_exception
from com.cryptobot.config import Config
from com.cryptobot.utils.python import modification_date
from com.cryptobot.utils.request import HttpRequest
from com.cryptobot.utils.path import get_data_path
from ratelimit import RateLimitException, limits

request = HttpRequest()
settings = Config().get_settings()
max_threads = settings.runtime.classifiers.SwapClassifier.max_concurrent_threads
max_calls = int(50/max_threads)
period_per_thread = int(60/max_threads)


@on_exception(expo, RateLimitException, max_tries=1, max_time=10)
@limits(calls=max_calls, period=period_per_thread)
def get_listings():
    filepath = get_data_path() + 'coinmarketcap_listings.json'
    last_updated = modification_date(filepath)
    diff = datetime.now() - last_updated

    if diff.total_seconds() <= settings.runtime.extractors.tokens.coinmarketcap_listings_interval:
        with open(filepath) as fp:
            return json.load(fp)

    url = settings.endpoints.coinmarketcap.listings_latest.format(
        api_key=settings.endpoints.coinmarketcap.api_key
    )
    listings = []
    pages = 2
    limit = 5000

    for ix in range(1, pages + 1):
        response = request.get(url, {
            'start': ix if ix == 1 else limit + 1,
            'limit': limit
        })

        listings += response.get('data', None)

    return response.get('data', None)
