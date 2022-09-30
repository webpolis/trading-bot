import time

import pandas as pd
from bs4 import BeautifulSoup as soup
from com.cryptobot.utils.pandas import top_addresses_table_to_df
from com.cryptobot.utils.selenium import get_driver
from selenium import webdriver


class AccountsExtractor():
    def __init__(self, _logger):
        self._logger = _logger
        self.driver = get_driver()

        _logger.info("Initialized AccountsExtractor.")

    def run(self):
        page_number = 1
        addresses_df = pd.DataFrame()

        while len(addresses_df) < 100:
            url_to_top_addresses_page_number = "https://etherscan.io/accounts/" + str(
                page_number)

            self._logger.info("Browsing to " + url_to_top_addresses_page_number)
            time.sleep(3)

            self.driver.get(url_to_top_addresses_page_number)
            time.sleep(3)

            self._logger.info(url_to_top_addresses_page_number + ' loaded')

            soup_data = soup(self.driver.page_source, 'html.parser')
            table_addresses_html = soup_data.findAll(
                "table", {"class": "table table-hover"})[0]
            addresses_df = pd.concat([addresses_df,
                                     top_addresses_table_to_df(table_addresses_html)])

            page_number += 1

        addresses_df.to_csv("whales.csv", index=False)

        self.driver.quit()
        self.driver = None

        self._logger.info("Accounts extraction finished.")

        return addresses_df
