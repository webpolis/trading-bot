import logging

import pandas as pd
from com.cryptobot.config import Config
from com.cryptobot.utils.logger import PrettyLogger


class DFModifier():
    def __init__(self, cls, filepath):
        self.settings = Config().get_settings().runtime.modifiers
        self.logger = PrettyLogger(cls, logging.INFO)
        self.df = pd.read_csv(filepath)

        self.logger.info('Initialized.')

    def patch(self):
        pass
