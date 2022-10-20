from backoff import expo, on_exception
from com.cryptobot.config import Config
from com.cryptobot.utils.request import HttpRequest
from ratelimit import RateLimitException, limits

request = HttpRequest()


@on_exception(expo, RateLimitException, max_tries=3)
@limits(calls=49, period=60)
def get_price(coin_id, currency='usd'):
    response = request.get(Config().get_settings().endpoints.coingecko.price, {
        'ids': coin_id,
        'vs_currencies': currency
    })
    price = response.get(coin_id, {}).get(
        currency, None) if response is not None else None

    return price
