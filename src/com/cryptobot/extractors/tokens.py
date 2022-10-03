from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.utils.request import HttpRequest
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
        coingecko_markets = HttpRequest().get(Config().get_settings().endpoints.coingecko.markets, {
            'vs_currency': 'usd',
            'order': 'market_cap_desc,volume_desc',
            'per_page': 1000,
            'sparkline': 'false'
        })

        # fetch markets from FTX
        ftx_markets = HttpRequest().get(Config().get_settings().endpoints.ftx.markets)

        self.logger.info(coingecko_markets)
        self.logger.info(ftx_markets)
