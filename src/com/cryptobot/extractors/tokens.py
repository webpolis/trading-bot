from time import sleep
from typing import List
import pandas as pd
from com.cryptobot.classifiers.coingecko_tokens import \
    CoingeckoTokensClassifier
from com.cryptobot.classifiers.ftx_tokens import FTXTokensClassifier
from com.cryptobot.config import Config
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.schemas.token import Token, TokenSource
from com.cryptobot.utils.pandas_utils import merge_tokens_dicts_into_df
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

    def run(self):
        settings = Config().get_settings()
        cg_markets_endpoint = settings.endpoints.coingecko.markets
        ftx_markets_endpoint = settings.endpoints.ftx.markets
        ftx_lending_endpoint = settings.endpoints.ftx.lending

        while True:
            runtime_settings = Config().get_settings().runtime
            refresh_interval = runtime_settings.extractors.tokens.refresh_interval_secs
            max_pages = runtime_settings.extractors.tokens.max_pages

            # fetch markets from coingecko
            coingecko_markets = []
            page = 1

            while page < max_pages:
                self.logger.info(f'Collecting markets from Coingecko (page #{page})')

                coingecko_markets = HttpRequest().get(cg_markets_endpoint, {
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
            coingecko_tokens = [token.__dict__ for token in coingecko_tokens]
            pd.DataFrame(coingecko_tokens).to_csv(
                get_data_path() + 'coingecko_tokens.csv', index=False)

            # fetch tokens for lend in FTX
            self.logger.info(f'Collecting tokens from FTX')

            ftx_lending = HttpRequest().get(ftx_lending_endpoint)
            ftx_lending = ftx_lending['result']
            ftx_lending_tokens = self.ftx_classifier.classify(
                ftx_lending, TokenSource.FTX_LENDING)
            ftx_lending_tokens = pd.DataFrame([
                token.__dict__ for token in ftx_lending_tokens if token is not None])

            # fetch markets from FTX
            ftx_markets = HttpRequest().get(ftx_markets_endpoint)
            ftx_markets = ftx_markets['result']
            ftx_markets_tokens = self.ftx_classifier.classify(
                ftx_markets, TokenSource.FTX)
            ftx_markets_tokens = pd.DataFrame([
                token.__dict__ for token in ftx_markets_tokens if token is not None])

            ftx_tokens = ftx_lending_tokens.merge(
                ftx_markets_tokens, how='left', on='symbol')
            ftx_tokens.drop_duplicates(inplace=True, subset=['symbol'])

            self.logger.info(
                f'{len(ftx_tokens)} tokens collected for lending in FTX')

            pd.DataFrame(ftx_lending_tokens).to_csv(
                get_data_path() + 'ftx_lending_tokens.csv', index=False)
            pd.DataFrame(ftx_markets_tokens).to_csv(
                get_data_path() + 'ftx_markets_tokens.csv', index=False)

            # convert and merge
            self.logger.info('Produce tokens union list...')
            tokens = merge_tokens_dicts_into_df(coingecko_tokens, ftx_tokens, 'symbol')

            # store locally just for reference
            tokens.to_csv(get_data_path() + 'tokens.csv', index=False)

            self.logger.info(
                f'Collected {tokens.symbol.size} tokens from Coingecko & FTX')

            self.logger.info(f'Sleeping for {refresh_interval} seconds.')

            sleep(refresh_interval)
