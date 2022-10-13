from time import sleep
from typing import List

from com.cryptobot.classifiers.coingecko_tokens import \
    CoingeckoTokensClassifier
from com.cryptobot.classifiers.ftx_tokens import FTXTokensClassifier
from com.cryptobot.config import Config
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.schemas.token import Token
from com.cryptobot.utils.pandas import merge_tokens_dicts_into_df
from com.cryptobot.utils.path import get_data_path
from com.cryptobot.utils.request import HttpRequest


class TokensExtractor(Extractor):
    def __init__(self):
        super().__init__(__name__)

        self.tokens = {
            'ftx': List[Token],
            'coingecko': List[Token]
        }
        self.coingecko_classifier = CoingeckoTokensClassifier()
        self.ftx_classifier = FTXTokensClassifier()
        self.settings = Config().get_settings().runtime.extractors.tokens

    def run(self):
        refresh_interval = self.settings.refresh_interval_secs

        while True:
            # fetch markets from coingecko
            coingecko_markets = []
            page = 1

            while page < 10:
                self.logger.info(f'Collecting markets from Coingecko (page #{page})')

                coingecko_markets = HttpRequest().get(Config().get_settings().endpoints.coingecko.markets, {
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc,volume_desc',
                    'per_page': 250,
                    'page': page,
                    'sparkline': 'false',
                }) + coingecko_markets
                page += 1

                self.logger.info(f'{len(coingecko_markets)} markets collected so far')

                sleep(1)

            coingecko_tokens = self.coingecko_classifier.classify(coingecko_markets)

            # fetch markets from FTX
            self.logger.info(f'Collecting markets from FTX')
            ftx_markets = HttpRequest().get(Config().get_settings().endpoints.ftx.markets)
            ftx_markets = ftx_markets['result']

            self.logger.info(f'{len(ftx_markets)} markets collected so far')
            ftx_tokens = self.ftx_classifier.classify(ftx_markets)

            # convert and merge
            self.logger.info('Produce tokens union list...')
            tokens = merge_tokens_dicts_into_df([token.__dict__
                                                 for token in coingecko_tokens], [token.__dict__
                                                                                  for token in ftx_tokens], 'symbol')

            # store locally just for reference
            tokens.to_csv(get_data_path() + 'tokens.csv', index=False)

            self.logger.info(
                f'Collected {tokens.symbol.size} tokens from Coingecko & FTX')
            
            self.logger.info(f'Sleeping for {refresh_interval} seconds.')

            sleep(refresh_interval)
