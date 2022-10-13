import json
from time import sleep

from com.cryptobot.config import Config
from com.cryptobot.modifiers.df_modifier import DFModifier
from com.cryptobot.utils.path import get_data_path
from pycoingecko import CoinGeckoAPI


class TokensPriceModifier(DFModifier):
    def __init__(self):
        super().__init__(__name__, get_data_path() + 'tokens.csv')

        self.tokens = list(set(list(self.df['symbol'])))
        self.cg = cg = CoinGeckoAPI()

        cg_coins_fp = open(get_data_path() + 'coingecko_coins.json')
        self.cg_coins = json.load(cg_coins_fp)
        self.cg_tokens_coins_map = {}
        self.cg_price_endpoint = Config().get_settings().endpoints.coingecko.price

        for coin in self.cg_coins:
            symbol = coin['symbol'].upper()

            if symbol not in self.tokens:
                continue

            self.cg_tokens_coins_map[symbol] = coin['id']

        cg_coins_fp.close()

    def patch(self):
        super().patch()

        self.logger.info(
            f'Refreshing {len(self.cg_tokens_coins_map)} tokens prices via Coingecko...')

        coins_ids = list(self.cg_tokens_coins_map.values())
        ix = 0

        while True:
            slice_ids = coins_ids[ix:ix+10]

            if len(slice_ids) == 0:
                break

            coingecko_prices = self.cg.get_coins_markets(ids=slice_ids, vs_currency='usd')

            self.logger.info(coingecko_prices)

            ix += 10

            sleep(0.5)

    def run(self):
        while True:
            self.patch()

            sleep(self.settings.tokens_price.refresh_interval_secs)
