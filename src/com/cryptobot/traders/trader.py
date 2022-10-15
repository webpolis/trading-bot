import logging
from typing import List

from com.cryptobot.classifiers.swap import SwapClassifier
from com.cryptobot.classifiers.tx import TXClassifier
from com.cryptobot.config import Config
from com.cryptobot.events.consumer import EventsConsumerMixin
from com.cryptobot.schemas.swap_tx import SwapTx
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.strategies.portolio_allocation import \
    PortfolioAllocationStrategy
from com.cryptobot.utils.formatters import tx_parse
from com.cryptobot.utils.logger import PrettyLogger
from jsonpickle import decode, encode


class Trader(EventsConsumerMixin):
    def __init__(self, cls=__name__):
        for base_class in Trader.__bases__:
            if base_class == EventsConsumerMixin:
                base_class.__init__(self, queues=[
                    SwapClassifier.__name__,
                ])
            else:
                base_class.__init__(self, __name__)

        self.strategies = [
            PortfolioAllocationStrategy()
        ]
        self.etherscan_tx_endpoint = Config().get_settings().endpoints.etherscan.tx
        self.logger = PrettyLogger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def process(self, message=None, id=None, rc=None, ts=None):
        txs: List[Tx | SwapTx] = [decode(item) for item in message['item']]

        for tx in txs:
            self.logger.info(
                f'Probing strategies for tx: {self.etherscan_tx_endpoint.format(tx.hash)}')

            for strategy in self.strategies:
                strategy_response: StrategyResponse = strategy.apply(tx)

                self.logger.info(
                    f'We got the strategy\'s verdict: {str(strategy_response)}')

        return True

    def run(self):
        self.consume()
