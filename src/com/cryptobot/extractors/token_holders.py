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
        page_number = 1
        addresses_df = pd.DataFrame()
        tokens: pd.DataFrame = pd.read_csv(get_data_path() + 'tokens.csv')
        tokens_addresses = tokens[tokens['address'].notnull()].address
        tokens_addresses.reset_index(inplace=True, drop=True)
        tokens_addresses = tokens_addresses.loc[0:self.max_token_addresses-1]

        self.logger.info(
            f'Selecting Top #{self.max_token_addresses} tokens\' ERC20 addresses.')

        for ix, token_address in tokens_addresses.items():
            while page_number <= self.max_holders_pages:
                url = Config().get_settings().endpoints.etherscan.token_holders.format(token_address, page_number)

                self.logger.info('Browsing to ' + url)
                time.sleep(3)

                self.driver.get(url)
                time.sleep(3)

                self.logger.info(url + ' loaded')

                soup_data = soup(self.driver.page_source, 'html.parser')
                table_addresses_html = soup_data.findAll('table')[0]
                addresses_df = pd.concat([addresses_df,
                                          holders_table_to_df(table_addresses_html)])

                page_number += 1

        # store locally just for reference
        addresses_df.to_csv(get_data_path() + 'tokens_holders.csv', index=False)

        self.driver.quit()
        self.driver = None

        self.logger.info('Accounts extraction finished.')
