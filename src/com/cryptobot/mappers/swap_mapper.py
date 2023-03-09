from com.cryptobot.mappers.mapper import Mapper
from typing import TypedDict


class SwapMapOutput(TypedDict):
    token_from: str
    token_from_qty: int
    token_to: str
    token_to_qty: int


# Balancer Swap


class BalancerSwapArgs(TypedDict):
    singleSwap: tuple
    funds: tuple
    limit: int
    deadline: int

# 1Inch Swap


class OneInchSwapArgs(TypedDict):
    caller: str
    desc: tuple
    executorData: bytes
    clientData: bytes


class OneInchV5RouterSwapArgs(TypedDict):
    executor: str
    desc: tuple
    permit: bytes
    data: bytes

# TransitSwap


class TransitSwapArgs(TypedDict):
    desc: tuple
    callbytesDesc: tuple


"""
This maps the actual parameters used during a swap call execution with the fields we want to extract.

'destination field' : 'parameter name holding the value or a tuple indicating the field & index position 
                      if parameter itself is a tuple'
"""
BalancerSwapMap = {
    'token_from': ('singleSwap', 2),
    'token_to': ('singleSwap', 3),
    'token_from_qty': ('singleSwap', 4),
    'token_to_qty': 'limit'
}

OneInchSwapMap = {
    'token_from': ('desc', 0),
    'token_to': ('desc', 1),
    'token_from_qty': ('desc', -4),
    'token_to_qty': ('desc', -3)
}

OneInchV5RouterSwapMap = {
    'token_from': ('desc', 0),
    'token_to': ('desc', 1),
    'token_from_qty': ('desc', -3),
    'token_to_qty': ('desc', -2)
}

TransitSwapMap = {
    'token_from': ('desc', 1),
    'token_to': ('desc', 2),
    'token_from_qty': ('desc', 5),
    'token_to_qty': ('desc', 6)
}


class SwapMapper(Mapper):
    def __init__(self):
        super().__init__(__name__)

    def map(self, input, map_def) -> SwapMapOutput:
        output = super().map(input, map_def)

        return output
