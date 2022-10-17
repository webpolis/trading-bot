import re
from datetime import datetime

from com.cryptobot.schemas.token import Token, TokenSource
from com.cryptobot.schemas.tx import Tx


def parse_ethereum_address(address_str: str):
    return re.sub(r'^(0x[a-z\d]+).*$', '\\1', address_str, flags=re.IGNORECASE)


def parse_token_symbol(address_str: str):
    return re.sub(r'[^a-z]', '', address_str, flags=re.IGNORECASE)


def tx_parse(tx: dict):
    parsed_tx = {}

    try:
        parsed_tx = {key: tx[key] for key in tx.keys()
                     & {'blockNumber', 'hash', 'from', 'to', 'gas', 'gasPrice', 'value', 'input'}}
    except Exception as error:
        print({'tx_parse_error': error, 'tx': tx})

        return None

    return Tx(
        datetime.utcnow(),
        parsed_tx['blockNumber'],
        parsed_tx['hash'].lower(),
        parsed_tx['from'].lower(
        ) if 'from' in parsed_tx and parsed_tx['from'] != None else None,
        parsed_tx['to'].lower() if 'to' in parsed_tx and parsed_tx['to'] != None else None,
        parsed_tx['gas'],
        parsed_tx['gasPrice'],
        parsed_tx['value'],
        parsed_tx['input']
    )


def token_parse(token, token_source: TokenSource):
    parsed_token = None
    price_usd = None

    if token_source == TokenSource.COINGECKO:
        parsed_token = {key: token[key] for key in token.keys()
                        & {'name', 'symbol', 'market_cap', 'current_price'}}
        price_usd = parsed_token['current_price']

    if token_source == TokenSource.FTX:
        parsed_token = {key: token[key] for key in token.keys()
                        & {'name', 'baseCurrency'}}
        parsed_token['symbol'] = parsed_token['baseCurrency']

    if token_source == TokenSource.FTX_LENDING:
        parsed_token = {key: token[key] for key in token.keys()
                        & {'coin'}}
        parsed_token['symbol'] = parsed_token['coin'].upper()

    if parsed_token.get('symbol') is None:
        return None

    return Token(
        parsed_token['symbol'].upper(),
        parsed_token['name'].upper() if 'name' in parsed_token else None,
        parsed_token.get('market_cap', None),
        float(price_usd) if price_usd is not None else None,
        None
    ) if parsed_token != None else None
