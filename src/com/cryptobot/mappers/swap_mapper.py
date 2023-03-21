from com.cryptobot.mappers.mapper import Mapper
from typing import TypedDict


class SwapMapOutput(TypedDict):
    token_from: str
    token_from_qty: int
    token_to: str
    token_to_qty: int

# Swap function signatures


class BalancerSwapArgs(TypedDict):
    singleSwap: tuple
    funds: tuple
    limit: int
    deadline: int


class OneInchSwapArgs(TypedDict):
    caller: str
    desc: tuple
    executorData: bytes
    clientData: bytes


class OneInchV5RouterArgs(TypedDict):
    executor: str
    desc: tuple
    permit: bytes
    data: bytes


class TransitSwapArgs(TypedDict):
    desc: tuple
    callbytesDesc: tuple


class UniswapRouterArgs(TypedDict):
    amountOut: int
    amountInMax: int
    path: list
    to: str
    deadline: int


class UniswapV2RouterArgs(TypedDict):
    amountIn: int
    amountOutMin: int
    path: list
    to: str
    deadline: int


class KyberSwapArgs(TypedDict):
    execution: tuple


class KyberElasticRouterArgs(TypedDict):
    params: tuple


class SushiSwapRouterArgs(TypedDict):
    amountOutMin: int
    path: list
    to: str
    deadline: int

class CamelotRouterArgs(TypedDict):
    amountOutMin: int
    path: list
    to: str
    referrer: str
    deadline: int

class FirebirdAggregatorArgs(TypedDict):
    caller: str
    desc: tuple
    data: bytes


"""
The following maps the actual parameters used during a swap call execution with the fields we want to extract.

'destination field' : 'parameter name holding the value or a tuple indicating the field & index position 
                      if parameter itself is a tuple or list'
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

OneInchV5RouterMap = {
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

UniswapRouterMap = {
    'token_from': ('path', 0),
    'token_to': ('path', 1),
    'token_from_qty': 'amountInMax',
    'token_to_qty': 'amountOut'
}

UniswapV2RouterMap = {
    'token_from': ('path', 0),
    'token_to': ('path', 1),
    'token_from_qty': 'amountIn',
    'token_to_qty': 'amountOutMin'
}

KyberSwapMap = {
    """
    The execution field is a tuple which contains a desc field (similar to 1inch's desc), located at index 
    defined by 2nd number; the 3rd number on these tuples is the index location of the value we want to 
    extract from desc.
    """
    'token_from': ('execution', 3, 0),
    'token_to': ('execution', 3, 1),
    'token_from_qty': ('execution', 3, -4),
    'token_to_qty': ('execution', 3, -3)
}

KyberElasticRouterMap = {
    'token_from': ('params', 1),
    'token_to': ('params', 0),
    'token_from_qty': ('params', -3),
    'token_to_qty': ('params', -2)
}

SushiSwapRouterMap = {
    'token_from': ('path', 0),
    'token_to': ('path', 1),
    'token_from_qty': None,
    'token_to_qty': 'amountOutMin'
}

CamelotRouterMap = {
    'token_from': ('path', 0),
    'token_to': ('path', 1),
    'token_from_qty': None,
    'token_to_qty': 'amountOutMin'
}

FirebirdAggregatorMap = {
    'token_from': ('desc', 0),
    'token_to': ('desc', 1),
    'token_from_qty': ('desc', 4),
    'token_to_qty': ('desc', 5)
}


class SwapMapper(Mapper):
    def __init__(self):
        super().__init__(__name__)

    def map(self, input, map_def) -> SwapMapOutput:
        output = super().map(input, map_def)

        return output
