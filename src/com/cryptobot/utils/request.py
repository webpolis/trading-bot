import urllib.request
import urllib.parse


class Request():
    def __init__(self) -> None:
        pass

    def get(self, url, params: dict = None):
        out = None
        params = urllib.parse.urlencode(params) if params != None else None

        with urllib.request.urlopen(f'{url}%s' % '?' + params if params != None else '') as req:
            out = req.read().decode('utf-8')

        return out
