from enum import Enum
from com.cryptobot.schemas.schema import Schema
from ethtx.models.objects_model import Transaction


class TxType(Enum):
    UNCLASSIFIED = 0
    SWAP = 1


class Tx(Schema):
    def __init__(self, blockNumber, hash, _from, to, gas, gasPrice, value, input, type=TxType.UNCLASSIFIED, raw: Transaction = None):
        self.blockNumber = blockNumber
        self.hash = hash
        # underscore (reserved keyword)
        self.sender = _from
        self.receiver = to
        self.gas = gas
        self.gasPrice = gasPrice
        self.value = value
        self.type = type
        self.raw = raw
        self.input = input
