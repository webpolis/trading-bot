import json


class Token():
    def __init__(self, symbol, name, address):
        self.symbol = symbol
        self.name = name
        self.address = address

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
