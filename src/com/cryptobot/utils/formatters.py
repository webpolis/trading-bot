import re

from com.cryptobot.schemas.token import Token, TokenSource
from com.cryptobot.schemas.tx import Tx


def format_str_as_number(number):
    return float(re.sub(r'[^\d\.]+', '', str(number)))


def tx_parse(tx):
    parsed_tx = {key: tx[key] for key in tx.keys()
                 & {'blockNumber', 'hash', 'from', 'to', 'gas', 'gasPrice', 'value'}}

    return Tx(
        parsed_tx['blockNumber'],
        parsed_tx['hash'],
        parsed_tx['from'],
        parsed_tx['to'],
        parsed_tx['gas'],
        parsed_tx['gasPrice'],
        parsed_tx['value']
    )


def token_parse(token, token_source: TokenSource):
    parsed_token = None

    if token_source == TokenSource.COINGECKO:
        parsed_token = {key: token[key] for key in token.keys()
                        & {'name', 'symbol', 'market_cap'}}

    if token_source == TokenSource.FTX:
        parsed_token = {key: token[key] for key in token.keys()
                        & {'name', 'baseCurrency'}}
        parsed_token['symbol'] = parsed_token['baseCurrency']

    return Token(
        parsed_token['symbol'].upper(),
        parsed_token['name'].upper(),
        None,
        parsed_token['market_cap'] if 'market_cap' in parsed_token.keys() else None
    ) if parsed_token != None else None
