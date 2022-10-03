import json


class Tx():
    def __init__(self, _blockNumber, _hash, _from, _to, _gas, _gasPrice, _value):
        self.blockNumber = _blockNumber
        self.hash = _hash
        # underscore (reserved keyword)
        self.sender = _from
        self.receiver = _to
        self.gas = _gas
        self.gasPrice = _gasPrice
        self.value = _value

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
