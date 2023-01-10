import re
from datetime import datetime

from com.cryptobot.schemas.token import Token, TokenSource
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.schemas.address import Address


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

    _from = parsed_tx['from'].lower(
    ) if 'from' in parsed_tx and parsed_tx['from'] != None else ''
    to = parsed_tx['to'].lower(
    ) if 'to' in parsed_tx and parsed_tx['to'] != None else ''

    return Tx(
        datetime.utcnow(),
        parsed_tx['blockNumber'],
        parsed_tx['hash'].lower() if type(
            parsed_tx['hash']) == str else parsed_tx['hash'].hex(),
        Address(_from),
        Address(to),
        parsed_tx['gas'],
        parsed_tx['gasPrice'],
        parsed_tx['value'],
        parsed_tx['input']
    )


def token_parse(token, token_source: TokenSource):
    parsed_token = None
    price_usd = None
    address = None

    if token_source == TokenSource.COINMARKETCAP:
        parsed_token = {key: token[key] for key in token.keys()
                        & {'name', 'symbol', 'quote', 'platform'}}
        quote = parsed_token.get('quote', {}).get('USD', None)
        platform = parsed_token.get('platform', None)

        if platform != None and platform['slug'] == 'ethereum':
            address = platform.get('token_address', None)

        if quote != None:
            parsed_token['market_cap'] = quote.get('market_cap', None)
            price_usd = quote.get('price', None)

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
        price_usd,
        address,
        no_live_checkup=True
    ) if parsed_token != None else None


def parse_token_qty(token: Token = None, qty=None):
    if token is None or qty is None:
        return float(-1)

    if (type(qty) != int and type(qty) != float) or type(token.decimals) != int:
        return float(-1)

    return float(qty/10**token.decimals)


def convert_dict_values(dictionary, to_array=False):
    for key, value in dictionary.items():
        # Try to convert the value to a float
        try:
            value = float(value)

            # If the value is an integer, convert it to an int
            if value.is_integer():
                value = int(value)
        except ValueError:
            # If the value is not a float, try to convert it to a bool
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif is_valid_timestamp(value):
                value = datetime.strptime(value, '%m/%d/%Y %H:%M:%S')
            # If the value is not a bool, leave it as a str
            else:
                pass
        # Update the dictionary with the converted value
        dictionary[key] = value if to_array is False else [value]
    return dictionary


def is_valid_timestamp(date_string, date_format='%m/%d/%Y %H:%M:%S'):
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False
