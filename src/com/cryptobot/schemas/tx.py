from com.cryptobot.schemas.schema import Schema


class Tx(Schema):
    def __init__(self, _blockNumber, _hash, _from, _to, _gas, _gasPrice, _value):
        self.blockNumber = _blockNumber
        self.hash = _hash
        # underscore (reserved keyword)
        self.sender = _from
        self.receiver = _to
        self.gas = _gas
        self.gasPrice = _gasPrice
        self.value = _value
