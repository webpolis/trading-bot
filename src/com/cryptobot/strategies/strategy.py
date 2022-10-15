import logging
import json

from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.schemas.token import Token
from enum import Enum


class StrategyAction(Enum):
    NONE = 0
    BUY = 1
    SELL = 2


class StrategyResponse:
    action: StrategyAction
    token: Token | None

    def __init__(self, action: StrategyAction = StrategyAction.NONE, token: Token = None):
        self.action = action
        self.token = token

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else (
            o._asdict() if hasattr(o, '_asdict') else None
        ),
            sort_keys=True)


class Strategy:
    def __init__(self, cls):
        self.logger = PrettyLogger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def apply(self, tx: Tx) -> StrategyResponse:
        return StrategyResponse()
