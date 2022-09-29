import time
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from collections import namedtuple
import pandas as pd

import etherscan_getter
import cardanoscan_getter


class Scrappers:
    def __init__(self, config):
        self.ethereum_getter = etherscan_getter.EtherscanGetter()
        self.cardano_getter = cardanoscan_getter.CardanoscanGetter()
        self.driver = None
        Token_info = namedtuple('Token_info', ['url_token', 'url_txs', 'url_whales'])
        self.scanner_url = config["Scrapper"]["scanners"]["ethereum"]
        ether_urls = list(config["Scrapper"]["tokens_urls"]["ether"].values())
        self.tokens = {
            "ether": Token_info(ether_urls[0], ether_urls[1], ether_urls[2])
        }
        option = webdriver.ChromeOptions()
        option.add_argument("headless")
        self.driver_option = option

    def get_txs(self, page_number):
        url_to_txs_page_number = "https://etherscan.io/txs?ps=100&p=" + str(page_number)
        self.driver = webdriver.Chrome('/home/agustin/Git-Repos/algo-trading-crypto/sm-interactor/'
                                       'sm_interactor/app/chromedriver')#, options=self.driver_option)
        time.sleep(3)
        self.driver.get(url_to_txs_page_number)
        time.sleep(3)
        soup_data = soup(self.driver.page_source, 'html.parser')
        self.driver.close()
        # print(soup_data.findAll("table", {"class": "table table-hover"}))
        table_txs_html = soup_data.findAll("table", {"class": "table table-hover"})[0]
        txs_df = self.ethereum_getter.txs_table_to_df(table_txs_html)
        return txs_df

    def get_whales(self, number_of_whales):
        page_number = 1
        addresses_df = pd.DataFrame()
        self.driver = webdriver.Chrome('/home/agustin/Git-Repos/algo-trading-crypto/sm-interactor/'
                                       'sm_interactor/app/chromedriver')

        while len(addresses_df) < number_of_whales:
            url_to_top_addresses_page_number = "https://etherscan.io/accounts/" + str(page_number)
            time.sleep(3)
            self.driver.get(url_to_top_addresses_page_number)
            time.sleep(3)
            soup_data = soup(self.driver.page_source, 'html.parser')
            # self.driver.close()
            table_addresses_html = soup_data.findAll("table", {"class": "table table-hover"})[0]
            addresses_df = addresses_df.append(self.ethereum_getter.top_addresses_table_to_df(table_addresses_html))
            page_number += 1
        self.driver.close()

            # MODIFICARLO PARA QUE TAMBIÉN TRACKEE EL MKT SHARE DE LA WHALE
        return addresses_df

if __name__ == '__main__':
    import json
    with open('/home/agustin/Git-Repos/Short-bot/config/config.json') as json_file:
        config = json.load(json_file)
    scrapper = Scrappers(config)
    Token_info = namedtuple('Token_info', ['url_token', 'url_txs', 'url_whales'])
    scrapper.scanner_url = config["Scrapper"]["scanners"]["ethereum"]
    urls = list(config["Scrapper"]["tokens_urls"]["ether"].values())
   #  scrapper.tokens = {
   #      "ether": Token_info([i for i in urls])
   # }
    print(Token_info(urls[0],urls[1],urls[2]))