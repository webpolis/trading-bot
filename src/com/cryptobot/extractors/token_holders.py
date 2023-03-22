import os
import time
import traceback
import shutil

import pandas as pd
from bs4 import BeautifulSoup as soup
from com.cryptobot.config import Config
from com.cryptobot.extractors.selenium_extractor import SeleniumExtractor
from com.cryptobot.utils.explorer import get_tokens_by_page
from com.cryptobot.utils.network import get_network_suffix
from com.cryptobot.utils.pandas_utils import get_tokens_df, holders_table_to_df
from com.cryptobot.utils.path import get_data_path


class TokenHoldersExtractor(SeleniumExtractor):
    def __init__(self):
        super().__init__(__name__)

    def run(self):
        while True:
            try:
                suffix = get_network_suffix()
                runtime_settings = Config().get_settings().runtime
                refresh_interval = runtime_settings.extractors.token_holders.refresh_interval_secs
                max_token_addresses = runtime_settings.extractors.token_holders.max_token_addresses
                max_holders_pages = runtime_settings.extractors.token_holders.max_holders_pages
                tmp_output_path = get_data_path(
                ) + 'tokens_holders{0}tmp.csv'.format(suffix)
                output_path = get_data_path(
                ) + 'tokens_holders{0}.csv'.format(suffix[:-1])

                # truncate
                initial = True
                f = open(tmp_output_path, 'a')
                f.truncate(0)
                f.close()

                # an empty suffix means it's ProviderNetwork.ETHEREUM
                if suffix == '':
                    tokens: pd.DataFrame = get_tokens_df()
                else:
                    # secondary networks have better data in their explorers' websites
                    tokens = []

                    for p in [1, 2]:
                        tokens = tokens + get_tokens_by_page(p, self.driver)

                    tokens = pd.DataFrame.from_dict(tokens)

                tokens.drop_duplicates(
                    subset=['symbol', 'address', 'market_cap'], inplace=True)
                tokens.sort_values(by=['market_cap'], ascending=False, inplace=True)
                tokens_addresses = tokens[tokens['address'].notnull()]
                tokens_addresses.reset_index(inplace=True, drop=True)
                tokens_addresses = tokens_addresses[['symbol', 'address']]
                tokens_addresses = tokens_addresses.loc[0:max_token_addresses-1]
                token_holders_endpoint = Config().get_settings().endpoints.etherscan.token_holders

                self.logger.info(
                    f'Selecting Top #{max_token_addresses} tokens\' ERC20 addresses.')

                for ix, token in tokens_addresses.iterrows():
                    page_number = 1
                    num_try_table_extract = 1
                    token_symbol = token['symbol']
                    token_address = token['address']

                    self.logger.info(
                        f'Retrieving holders for {token_symbol} ({token_address})')

                    while page_number <= max_holders_pages:
                        holders_table_df = None
                        url = token_holders_endpoint.format(token_address, page_number)

                        self.logger.info('Browsing to ' + url)
                        time.sleep(3)

                        num_try = 1

                        while num_try <= Config().get_settings().runtime.utils.selenium.max_tries:
                            try:
                                self.driver.get(url)
                                break
                            except Exception as error:
                                self.logger.error(error)

                                num_try += 1
                            finally:
                                time.sleep(3)

                        self.logger.info(url + ' loaded')

                        try:
                            soup_data = soup(self.driver.page_source, 'html.parser')
                            table_addresses_html = soup_data.findAll('table')[0]
                        except Exception as error:
                            self.logger.error(error)

                            if num_try_table_extract <= Config().get_settings().runtime.utils.selenium.max_tries:
                                num_try_table_extract += 1
                                continue

                        try:
                            holders_table_df = holders_table_to_df(table_addresses_html)
                        except:
                            break

                        holders_table_df['token_address'] = token_address
                        holders_table_df['token_symbol'] = token_symbol

                        # store locally just for reference
                        holders_table_df.to_csv(tmp_output_path, index=False, mode='a',
                                                header=initial)
                        initial = False

                        page_number += 1

                self.driver.quit()
                self.driver = None

                shutil.copy(tmp_output_path, output_path)

                self.logger.info('Tokens Holders extraction finished.')
            except Exception as error:
                self.logger.error(error)

                print(traceback.format_exc())
            finally:
                self.logger.info(f'Sleeping for {refresh_interval} seconds.')

                time.sleep(refresh_interval)
