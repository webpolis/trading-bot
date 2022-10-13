import logging
from com.cryptobot.utils.logger import PrettyLogger


class Classifier():
    def __init__(self, cls):
        self.logger = PrettyLogger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def parse(self, items):
        return items

    def filter(self, items):
        return items

    def classify(self, items):
        return items
