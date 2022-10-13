import json
import socket
import urllib.parse
from urllib.request import Request, urlopen
from com.cryptobot.config import Config


class HttpRequest():
    def __init__(self) -> None:
        self.max_tries = Config().get_settings().runtime.utils.request.max_tries

    def get(self, url, params: dict = None, try_num=1):
        if try_num > self.max_tries:
            return None

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
