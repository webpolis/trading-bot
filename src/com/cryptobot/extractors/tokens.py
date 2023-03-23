import json
from time import sleep
import traceback
from typing import List
from urllib import request

import pandas as pd
from com.cryptobot.classifiers.coingecko_tokens import \
    CoingeckoTokensClassifier
from com.cryptobot.classifiers.coinmarketcap_tokens import CoinmarketcapTokensClassifier
from com.cryptobot.classifiers.portals_tokens import PortalsTokensClassifier
from com.cryptobot.config import Config
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.schemas.token import Token
from com.cryptobot.utils.coingecko import get_markets
from com.cryptobot.utils.path import get_data_path
from com.cryptobot.utils.pandas_utils import fill_diverged_columns, refresh_tokens
from com.cryptobot.utils.coinmarketcap import get_listings
from com.cryptobot.utils.python import combine_lists
from com.cryptobot.utils.request import HttpRequest
from toolz import dissoc

request = HttpRequest()


class TokensExtractor(Extractor):
    def __init__(self):
        super().__init__(__name__)

        self.tokens = {
            'ftx': List[Token],
            'coingecko': List[Token]
        }
        self.coinmarketcap_classifier = CoinmarketcapTokensClassifier()
        self.coingecko_classifier = CoingeckoTokensClassifier()
        self.portals_classifier = PortalsTokensClassifier()

    def run(self):
        while True:
            try:
                runtime_settings = Config().get_settings().runtime
                refresh_interval = runtime_settings.extractors.tokens.refresh_interval_secs
                max_coingecko_pages = runtime_settings.extractors.tokens.max_coingecko_pages
                page_interval = runtime_settings.extractors.tokens.coingecko_page_interval

                # fetch portals.fi tokens
                portals_more = True
                portals_page = 0
                portals_tokens = []

                # preload stored tokens
                portals_tokens_path = get_data_path() + 'portals_tokens.csv'
                portals_tokens_df = pd.read_csv(open(portals_tokens_path))

                while portals_more:
                    try:
                        self.logger.info(
                            f'Collecting listings from Portals.fi (page #{portals_page+1})')

                        portals_response = request.get(
                            Config().get_settings().endpoints.portals.tokens, {
                                'limit': 250,
                                'page': portals_page,
                                'networks': ['arbitrum', 'ethereum', 'polygon']
                            })
                        portals_more = portals_response.get('more', False)
                        parsed_tokens = self.portals_classifier.classify(
                            portals_response.get('tokens'))
                        portals_tokens = combine_lists(portals_tokens, parsed_tokens)
                    except Exception as error:
                        self.logger.error(error)

                        break
                    finally:
                        if portals_more:
                            portals_page += 1

                        sleep(page_interval)

                # refresh portals' tokens
                portals_tokens_last = pd.DataFrame([
                    token.__dict__ for token in portals_tokens if token is not None])
                portals_tokens_df = refresh_tokens(
                    portals_tokens_df, portals_tokens_last)
                portals_tokens_df.to_csv(
                    get_data_path() + 'portals_tokens.csv', index=False)

                # fetch coinmarketcap listings
                self.logger.info('Collecting listings from Coinmarketcap')

                # preload stored tokens
                coinmarketcap_tokens_path = get_data_path() + 'coinmarketcap_tokens.csv'
                cmc_tokens_df = pd.read_csv(open(coinmarketcap_tokens_path))

                try:
                    coinmarketcap_listings = get_listings()
                    coinmarketcap_tokens = self.coinmarketcap_classifier.classify(
                        coinmarketcap_listings)
                    cmc_tokens_df = pd.DataFrame([
                        token.__dict__ for token in coinmarketcap_tokens if token is not None])
                    cmc_tokens_df.to_csv(
                        get_data_path() + 'coinmarketcap_tokens.csv', index=False)
                except Exception as error:
                    self.logger.error(error)

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
                        sleep(page_interval)

                """ coingecko may rate limit us (randomly), hence refresh whatever tokens \
                    we could collect this time """
                coingecko_tokens_last = self.coingecko_classifier.classify(
                    coingecko_markets)
                coingecko_tokens_last = [
                    token.__dict__ for token in coingecko_tokens_last]
                coingecko_tokens_last = pd.DataFrame(coingecko_tokens_last)
                coingecko_tokens = refresh_tokens(
                    coingecko_tokens, coingecko_tokens_last)
                coingecko_tokens.to_csv(coingecko_tokens_path, index=False)

                # convert and merge
                self.logger.info('Produce tokens union list...')
                tokens = coingecko_tokens.merge(cmc_tokens_df, how='outer', on=[
                    'symbol'], suffixes=('', '_cmc'))

                fill_diverged_columns(tokens, '_cmc')

                tokens = tokens.merge(portals_tokens_df, how='outer', on=[
                    'symbol', 'address'], suffixes=('', '_pfi'))

                fill_diverged_columns(tokens, '_pfi')

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

                # sort & sanitize
                tokens.drop_duplicates(
                    subset=['symbol', 'address', 'market_cap'], inplace=True)
                tokens.sort_values(by=['market_cap'], ascending=False, inplace=True)

                # group rows
                tokens = tokens.groupby(by=['symbol', 'address'], as_index=False).aggregate(
                    {'symbol': 'first', 'price_usd': 'first', 'name': 'first', 'market_cap': 'first', 'decimals': 'first', 'address': 'first'})
                tokens.sort_values(by=['market_cap'], ascending=False, inplace=True)

                # export
                tokens.to_csv(get_data_path() + 'tokens.csv', index=False)

                self.logger.info(
                    f'Collected {tokens.symbol.size} tokens from Portals.fi, Coingecko, Coinmarketcap & Tokenslist')

                self.logger.info(f'Sleeping for {refresh_interval} seconds.')
            except Exception as error:
                self.logger.error(error)

                print(traceback.format_exc())
            finally:
                sleep(refresh_interval)
