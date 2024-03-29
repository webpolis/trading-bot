import json
import re

import numpy as np
import pandas as pd
from com.cryptobot.config import Config
from com.cryptobot.schemas.token import Token
from com.cryptobot.utils.path import get_data_path
from com.cryptobot.utils.request import HttpRequest

request = HttpRequest()
settings = Config().get_settings()

kucoin_tickers = json.load(open(get_data_path() + 'kucoin_tickers.json'))
ftx_lending_tokens = pd.read_csv(get_data_path() + 'ftx_lending_tokens.csv')


def slope(data, order=1):
    coeffs = np.polyfit(data.index.values, list(data), order)
    slope = coeffs[-2]

    return float(slope)


def is_kucoin_listed(token: Token):
    ticker = next(iter([ticker for ticker in kucoin_tickers if re.sub(
        r'^([^\-]+)\-.*$', '\\1', ticker['symbol']) == token.symbol]), None)

    return ticker != None


def is_ftx_listed(token: Token):
    ticker = ftx_lending_tokens[(ftx_lending_tokens['address'] == token.address) | (
        ftx_lending_tokens['symbol'] == token.symbol)]

    return len(ticker) > 0


def get_btc_trend(days=1):
    try:
        response = request.get(settings.endpoints.coingecko.ohlc.format(
            coin_id='bitcoin',
            days=days))

        btc_df = pd.DataFrame(response, columns=[
                              'time', 'open', 'high', 'low', 'close'])
        diff = btc_df['close'].pct_change()
        diff = diff[diff.notna()]
        norm = np.linalg.norm(diff.values)
        trend = round(slope(diff), 8)
        vel = (norm/btc_df.time).mean()

        return trend
    except Exception as error:
        return float(0)
