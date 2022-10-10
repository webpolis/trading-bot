from enum import Enum
from com.cryptobot.schemas.schema import Schema
from ethtx.models.objects_model import Transaction

from com.cryptobot.utils.ethereum import get_contract


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

    def decode_input(self):
        if self.input is None:
            return None

        try:
            contract = get_contract(self.receiver)

            if contract is None:
                return None

            func_obj, func_params = contract.decode_function_input(self.input)

            return {'func_obj': func_obj, 'func_params': func_params}
        except Exception as error:
            print({'error': error})
