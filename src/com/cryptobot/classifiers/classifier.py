import logging
from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.utils.zodb import ZODBRunnable


class Classifier(ZODBRunnable):
    def __init__(self, cls):
        super().__init__()

        self.logger = PrettyLogger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def parse(self, items):
        return items

    def filter(self, items):
        return items

    def classify(self, items):
        items = self.parse(items)
        items = self.filter(items)

        return items
