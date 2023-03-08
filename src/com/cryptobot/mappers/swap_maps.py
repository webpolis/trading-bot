from typing import TypedDict


class SwapMapOutput(TypedDict):
    token_from: str
    token_from_qty: int
    token_to: str
    token_to_qty: int


class BalancerSwapArgs(TypedDict):
    singleSwap: tuple
    funds: tuple
    limit: int
    deadline: int
