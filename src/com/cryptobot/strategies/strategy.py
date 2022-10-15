import logging
from com.cryptobot.utils.logger import PrettyLogger


class StrategyAction(Enum):
    NONE = 0
    BUY = 1
    SELL = 2


class StrategyResponse:
    action: StrategyAction = StrategyAction.NONE
    token: Token


class Strategy:
    def __init__(self, cls):
        self.logger = PrettyLogger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def apply(self, tx: Tx) -> StrategyResponse:
        return StrategyResponse()
