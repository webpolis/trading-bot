import pandas as pd
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from com.cryptobot.utils.pandas import top_addresses_table_to_df


class AccountsExtractor():
    def run(this):
        page_number = 1
        addresses_df = pd.DataFrame()
        self.driver = webdriver.Chrome('/home/nico/dev/chromedriver')

        while len(addresses_df) < number_of_whales:
            url_to_top_addresses_page_number = self.tokens[token.name].url_whales + str(
                page_number)
            time.sleep(3)
            self.driver.get(url_to_top_addresses_page_number)
            time.sleep(3)
            soup_data = soup(self.driver.page_source, 'html.parser')
            # self.driver.close()
            if token.network == 'ethereum':
                table_addresses_html = soup_data.findAll(
                    "table", {"class": "table table-hover"})[0]
                addresses_df = addresses_df.append(
                    self.ethereum_getter.top_addresses_table_to_df(table_addresses_html))
            elif token.network == 'cardano':
                table_addresses_html = soup_data.findAll(
                    "table", {"class": "table table-hover"})[0]
                addresses_df = addresses_df.append(
                    self.ethereum_getter.top_addresses_table_to_df(table_addresses_html))
            page_number += 1
        self.driver.close()

        # MODIFICARLO PARA QUE TAMBIÉN TRACKEE EL MKT SHARE DE LA WHALE
        return addresses_df
