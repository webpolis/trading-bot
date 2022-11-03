import json
from time import sleep
import traceback
from typing import List

import pandas as pd
from com.cryptobot.classifiers.coingecko_tokens import \
    CoingeckoTokensClassifier
from com.cryptobot.classifiers.coinmarketcap_tokens import CoinmarketcapTokensClassifier
from com.cryptobot.config import Config
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.schemas.token import Token
from com.cryptobot.utils.coingecko import get_markets
from com.cryptobot.utils.path import get_data_path
from com.cryptobot.utils.pandas_utils import fill_diverged_columns
from com.cryptobot.utils.request import HttpRequest
from com.cryptobot.utils.coinmarketcap import get_listings
from toolz import dissoc


class TokensExtractor(Extractor):
    def __init__(self):
        super().__init__(__name__)

        self.tokens = {
            'ftx': List[Token],
            'coingecko': List[Token]
        }
        self.coinmarketcap_classifier = CoinmarketcapTokensClassifier()
        self.coingecko_classifier = CoingeckoTokensClassifier()

    def run(self):
        while True:
            try:
                runtime_settings = Config().get_settings().runtime
                refresh_interval = runtime_settings.extractors.tokens.refresh_interval_secs
                max_coingecko_pages = runtime_settings.extractors.tokens.max_coingecko_pages
                coingecko_page_interval = runtime_settings.extractors.tokens.coingecko_page_interval

                # fetch coinmarketcap listings
                self.logger.info('Collecting listings from Coinmarketcap')

                coinmarketcap_listings = get_listings()
                coinmarketcap_tokens = self.coinmarketcap_classifier.classify(
                    coinmarketcap_listings)
                cmc_tokens_df = pd.DataFrame([
                    token.__dict__ for token in coinmarketcap_tokens if token is not None])
                cmc_tokens_df.to_csv(
                    get_data_path() + 'coinmarketcap_tokens.csv', index=False)

                # fetch markets from coingecko
                coingecko_markets = []
                page = 1

                # preload stored tokens
                coingecko_tokens_path = get_data_path() + 'coingecko_tokens.csv'
                coingecko_tokens = pd.read_csv(open(coingecko_tokens_path))

                while page <= max_coingecko_pages:
                    try:
                        self.logger.info(
                            f'Collecting markets from Coingecko (page #{page})')
                        markets = get_markets(page)
                        coingecko_markets += markets if markets != None else []

                        self.logger.info(
                            f'{len(coingecko_markets)} markets collected so far')

                        page += 1
                    except Exception as error:
                        self.logger.error(error)

                        break
                    finally:
                        sleep(coingecko_page_interval)

                """ coingecko may rate limit us (randomly), hence refresh whatever tokens \
                    we could collect this time """
                coingecko_tokens_last = self.coingecko_classifier.classify(
                    coingecko_markets)
                coingecko_tokens_last = [
                    token.__dict__ for token in coingecko_tokens_last]
                coingecko_tokens_last = pd.DataFrame(coingecko_tokens_last)
                coingecko_tokens = tokens.merge(coingecko_tokens_last, how='left', on=[
                                                'symbol', 'name'], suffixes=('', '_last'))

                # preserve latest price & market cap
                coingecko_tokens['price_usd_last'].fillna(
                    tokens['price_usd'], inplace=True)
                coingecko_tokens['market_cap_last'].fillna(
                    tokens['market_cap'], inplace=True)
                coingecko_tokens['price_usd'] = coingecko_tokens['price_usd_last']
                coingecko_tokens['market_cap'] = coingecko_tokens['market_cap_last']

                del coingecko_tokens['price_usd_last']
                del coingecko_tokens['market_cap_last']
                del coingecko_tokens['address_last']
                del coingecko_tokens['decimals_last']

                coingecko_tokens.to_csv(coingecko_tokens_path, index=False)

                # convert and merge
                self.logger.info('Produce tokens union list...')
                tokens = coingecko_tokens.merge(cmc_tokens_df, how='outer', on=[
                    'symbol'], suffixes=('', '_cmc'))

                fill_diverged_columns(tokens, '_cmc')

                # combine with tokenslist
                self.logger.info('Combine with tokenslist...')
                tokenslist_cg_tokens = json.load(
                    open(get_data_path() + 'tokenslist_coingecko.json'))['tokens']
                tokenslist_uniswap_tokens = json.load(
                    open(get_data_path() + 'tokenslist_uniswap.json'))['tokens']
                tokenslist_1inch_tokens = json.load(
                    open(get_data_path() + 'tokenslist_1inch.json'))['tokens']
                tokenslist_all_tokens = list(map(lambda token: dissoc(
                    token, 'extensions', 'logoURI', 'name'), tokenslist_cg_tokens + tokenslist_uniswap_tokens + tokenslist_1inch_tokens))
                tokenslist_df = pd.DataFrame(tokenslist_all_tokens)
                tokenslist_df['address'] = tokenslist_df['address'].str.lower()
                tokenslist_df.drop_duplicates(inplace=True)
                tokens = tokens.merge(tokenslist_df, how='outer', on=[
                    'symbol', 'address'], suffixes=('', '_tl'))

                fill_diverged_columns(tokens, '_tl')

                # store locally for future reference
                tokens.to_csv(get_data_path() + 'tokens.csv', index=False)

                self.logger.info(
                    f'Collected {tokens.symbol.size} tokens from Coingecko, Coinmarketcap & Tokenslist')

                self.logger.info(f'Sleeping for {refresh_interval} seconds.')
            except Exception as error:
                self.logger.error(error)

                print(traceback.format_exc())
            finally:
                sleep(refresh_interval)
