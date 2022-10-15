import logging
from typing import List

from com.cryptobot.classifiers.swap import SwapClassifier
from com.cryptobot.classifiers.tx import TXClassifier
from com.cryptobot.config import Config
from com.cryptobot.events.consumer import EventsConsumerMixin
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.formatters import tx_parse
from com.cryptobot.utils.logger import PrettyLogger
from jsonpickle import decode


class Trader(EventsConsumerMixin):
    def __init__(self, cls=__name__):
        for base_class in Trader.__bases__:
            if base_class == EventsConsumerMixin:
                base_class.__init__(self, queues=[
                    SwapClassifier.__name__,
                ])
            else:
                base_class.__init__(self, __name__)

        self.etherscan_tx_endpoint = Config().get_settings().endpoints.etherscan.tx
        self.logger = PrettyLogger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def process(self, message=None, id=None, rc=None, ts=None):
        txs: List[Tx] = [decode(item) for item in message['item']]

        for tx in txs:
            self.logger.info(
                f'A tx is ready for me to trade: {self.etherscan_tx_endpoint.format(tx.hash)}')

        return True

    def run(self):
        self.consume()
