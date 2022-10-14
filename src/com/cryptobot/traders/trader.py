import logging
from com.cryptobot.classifiers.swap_classifier import SwapClassifier

from com.cryptobot.events.consumer import EventsConsumerMixin
from com.cryptobot.utils.logger import PrettyLogger


class Trader(EventsConsumerMixin):
    def __init__(self, cls=__name__):
        for base_class in Trader.__bases__:
            if base_class == EventsConsumerMixin:
                base_class.__init__(self, SwapClassifier.__name__)
            else:
                base_class.__init__(self, __name__)

        self.logger = PrettyLogger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def process(self, message=None, id=None, rc=None, ts=None):
        self.logger.info(message)

        return True

    def run(self):
        self.consume()
