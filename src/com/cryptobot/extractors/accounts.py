import time

import pandas as pd
from bs4 import BeautifulSoup as soup
from com.cryptobot.config import Config
from com.cryptobot.extractors.selenium_extractor import SeleniumExtractor
from com.cryptobot.utils.pandas import accounts_table_to_df
from com.cryptobot.utils.path import get_data_path


class AccountsExtractor(SeleniumExtractor):
    def __init__(self):
        super().__init__(__name__)

    def run(self):
        page_number = 1
        addresses_df = pd.DataFrame()

        # collect the top 100 addresses
        while len(addresses_df) < 100:
            url = Config().get_settings().endpoints.etherscan.accounts + '/' + str(
                page_number)

            self.logger.info('Browsing to ' + url)
            time.sleep(3)

            self.driver.get(url)
            time.sleep(3)

            self.logger.info(url + ' loaded')

            soup_data = soup(self.driver.page_source, 'html.parser')
            table_addresses_html = soup_data.findAll(
                'table', {'class': 'table table-hover'})[0]
            addresses_df = pd.concat([addresses_df,
                                     accounts_table_to_df(table_addresses_html)])

            page_number += 1

        # store locally just for reference
        addresses_df.to_csv(get_data_path() + 'etherscan_accounts.csv', index=False)

        self.driver.quit()
        self.driver = None

        self.logger.info('Accounts extraction finished.')
