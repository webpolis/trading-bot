import os
import time

import pandas as pd
from bs4 import BeautifulSoup as soup
from com.cryptobot.config import Config
from com.cryptobot.extractors.selenium_extractor import SeleniumExtractor
from com.cryptobot.utils.pandas import holders_table_to_df
from com.cryptobot.utils.path import get_data_path


class TokenHoldersExtractor(SeleniumExtractor):
    def __init__(self):
        super().__init__(__name__)

        self.max_token_addresses = Config().get_settings(
        ).runtime.extractors.token_holders.max_token_addresses
        self.max_holders_pages = Config().get_settings(
        ).runtime.extractors.token_holders.max_holders_pages

    def run(self):
        output_path = get_data_path() + 'tokens_holders.csv'
        holders_df = pd.DataFrame()
        tokens: pd.DataFrame = pd.read_csv(get_data_path() + 'tokens.csv')
        tokens_addresses = tokens[tokens['address'].notnull()]
        tokens_addresses.reset_index(inplace=True, drop=True)
        tokens_addresses = tokens_addresses[['symbol', 'address']]
        tokens_addresses = tokens_addresses.loc[0:self.max_token_addresses-1]

        self.logger.info(
            f'Selecting Top #{self.max_token_addresses} tokens\' ERC20 addresses.')

        for ix, token in tokens_addresses.iterrows():
            page_number = 1
            token_symbol = token['symbol']
            token_address = token['address']

            self.logger.info(f'Retrieving holders for {token_symbol} ({token_address})')

            while page_number <= self.max_holders_pages:
                table_df = None
                url = Config().get_settings().endpoints.etherscan.token_holders.format(token_address, page_number)

                self.logger.info('Browsing to ' + url)
                time.sleep(3)

                self.driver.get(url)
                time.sleep(3)

                self.logger.info(url + ' loaded')

                soup_data = soup(self.driver.page_source, 'html.parser')
                table_addresses_html = soup_data.findAll('table')[0]

                try:
                    table_df = holders_table_to_df(table_addresses_html)
                except:
                    break

                table_df['token_address'] = token_address
                table_df['token_symbol'] = token_symbol
                holders_df = pd.concat([holders_df, table_df])

                # store locally just for reference
                table_df.to_csv(output_path, index=False, mode='a',
                                header=not os.path.exists(output_path))

                page_number += 1

        self.driver.quit()
        self.driver = None

        self.logger.info('Tokens Holders extraction finished.')
