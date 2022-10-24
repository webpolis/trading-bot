import json
import logging
from urllib.error import HTTPError
import urllib.parse
from urllib.request import Request, urlopen

from com.cryptobot.config import Config
from com.cryptobot.utils.logger import PrettyLogger


class FatalRequestException(Exception):
    def __init__(self, num_tries=None, *args: object) -> None:
        super().__init__(*args)

        self.num_tries = num_tries


class HttpRequest():
    def get(self, url, params: dict = None):
        out = None
        params_encoded = urllib.parse.urlencode(params) if params != None else None
        url_encoded = f'{url}%s' % (('?' + params_encoded)
                                    if params_encoded != None else '')
        req = Request(url_encoded)

        req.add_header(
            'user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36')

        try:
            out = urlopen(req, timeout=15).read().decode('utf-8')
        except HTTPError as _error:
            raise _error
        except Exception as error:
            raise FatalRequestException(error)

        return json.loads(out) if type(out) == str else out

    def post(self, url, data: dict = None):
        out = None
        data = json.dumps(data).encode('utf-8')
        req = Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.add_header(
            'user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36')

        try:
            out = urlopen(req, data, timeout=15).read().decode('utf-8')
        except HTTPError as _error:
            raise _error
        except Exception as error:
            raise FatalRequestException(error)

        return json.loads(out) if type(out) == str else out


request_logger = PrettyLogger(HttpRequest.__name__, logging.INFO)
