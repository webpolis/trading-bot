from itertools import cycle
import logging
from threading import Lock
from urllib.error import HTTPError
from com.cryptobot.config import Config
from com.cryptobot.utils.request import FatalRequestException, HttpRequest
from com.cryptobot.utils.logger import PrettyLogger


request = HttpRequest()
settings = Config().get_settings()
alchemy_api_keys = cycle(settings.web3.providers.alchemy.api_keys)
lock = Lock()
api_key = None


def get_working_key():
    lock.acquire()

    global api_key
    global alchemy_api_keys

    if api_key is None:
        api_key = next(alchemy_api_keys)

    lock.release()

    return api_key


def api_post(payload):
    global api_key

    try:
        response = request.post(settings.endpoints.alchemy.api.format(
            api_key=get_working_key()), payload)

        return response
    except HTTPError as error:
        api_key = None

        alchemy_logger.error(
            f'HTTPError: code {error.code}. Repeating (will try next api_key)...')

        return api_post(payload)
    except FatalRequestException as _error:
        api_key = None

        alchemy_logger.error(
            f'FatalRequestException: tried {_error.num_tries} time(s).')

        return api_post(payload)


alchemy_logger = PrettyLogger(HttpRequest.__name__, logging.INFO)
