from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.utils.selenium import get_driver


class SeleniumExtractor(Extractor):
    def __init__(self, cls):
        super().__init__(cls)

        self.driver = get_driver()
