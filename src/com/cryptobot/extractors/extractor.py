import logging

from com.cryptobot.utils.logger import get_logger


class Extractor():
    def __init__(self, cls):
        self.logger = get_logger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def run(self):
        pass
