import json
import logging
import urllib.parse
from urllib.request import Request, urlopen

from com.cryptobot.config import Config
from com.cryptobot.utils.logger import PrettyLogger


class FatalRequestException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class HttpRequest():
    def get(self, url, params: dict = None, try_num=1):
        max_tries = Config().get_settings().runtime.utils.request.max_tries

        if try_num > max_tries:
            raise FatalRequestException(f'Tried {try_num} time(s)')

        out = None
        params_encoded = urllib.parse.urlencode(params) if params != None else None
        url_encoded = f'{url}%s' % (('?' + params_encoded)
                                    if params_encoded != None else '')
        req = Request(url_encoded)

        req.add_header(
            'user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36')

        try:
            out = urlopen(req, timeout=15).read().decode('utf-8')
        except Exception as error:
            return self.get(url, params, try_num+1)

        return json.loads(out) if type(out) == str else out

    def post(self, url, data: dict = None, try_num=1):
        max_tries = Config().get_settings().runtime.utils.request.max_tries

        if try_num > max_tries:
            raise FatalRequestException(f'Tried {try_num} time(s)')

        out = None
        data = json.dumps(data).encode('utf-8')
        req = Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.add_header(
            'user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36')

        try:
            out = urlopen(req, data, timeout=15).read().decode('utf-8')
        except Exception as error:
            request_logger.error({'error': error, 'data': data, 'url': url})

            return self.post(url, data, try_num+1)

        return json.loads(out) if type(out) == str else out


request_logger = PrettyLogger(HttpRequest.__name__, logging.INFO)
