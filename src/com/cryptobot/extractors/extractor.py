import logging

from com.cryptobot.utils.logger import PrettyLogger


class Extractor():
    def __init__(self, cls):
        self.logger = PrettyLogger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def run(self):
        pass
