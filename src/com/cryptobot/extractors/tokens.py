from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.utils.request import Request
from com.cryptobot.config import Config


class TokensExtractor(Extractor):
    def __init__(self):
        super().__init__(__name__)

        self.tokens = {
            'ftx': [],
            'coingecko': []
        }

    def run(self):
        # fetch markets from coingecko
        coingecko_markets = Request().get(Config().get_settings().endpoints.coingecko.markets, {
            'vs_currency': 'usd',
            'order': 'market_cap_desc,volume_desc',
            'per_page': 1000,
            'sparkline': 'false'
        })

        self.logger.info(coingecko_markets)
