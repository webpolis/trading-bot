import json
import re

import pandas as pd
from com.cryptobot.schemas.token import Token
from com.cryptobot.utils.path import get_data_path

kucoin_tickers = json.load(open(get_data_path() + 'kucoin_tickers.json'))
ftx_lending_tokens = pd.read_csv(get_data_path() + 'ftx_lending_tokens.csv')


def is_kucoin_listed(token: Token):
    ticker = next(iter([ticker for ticker in kucoin_tickers if re.sub(
        r'^([^\-]+)\-.*$', '\\1', ticker['symbol']) == token.symbol]), None)

    return ticker != None


def is_ftx_listed(token: Token):
    ticker = ftx_lending_tokens[(ftx_lending_tokens['address'] == token.address) | (
        ftx_lending_tokens['symbol'] == token.symbol)]

    return len(ticker) > 0
