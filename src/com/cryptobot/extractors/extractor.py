import logging

from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.utils.zodb import ZODBRunnable


class Extractor(ZODBRunnable):
    def __init__(self, cls):
        super().__init__()

        self.logger = PrettyLogger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def run(self):
        pass
