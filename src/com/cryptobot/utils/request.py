import json
import urllib.parse
from urllib.request import Request, urlopen


class HttpRequest():
    def __init__(self) -> None:
        pass

    def get(self, url, params: dict = None):
        out = None
        params = urllib.parse.urlencode(params) if params != None else None
        url = f'{url}%s' % (('?' + params) if params != None else '')

        req = Request(url)

        req.add_header(
            'user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36')
        out = urlopen(req).read().decode('utf-8')

        return json.loads(out) if type(out) == str else out
