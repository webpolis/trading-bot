import locale
import re
import time

from com.cryptobot.config import Config
from com.cryptobot.utils.ethereum import is_contract, is_eth_address
from com.cryptobot.utils.path import get_data_path

import pandas as pd

settings = Config().get_settings()
tokens_df = None
tokens_df_last_update = None
tokens_holders_df = None
tokens_holders_df_last_update = None


def format_str_as_number(number):
    return float(re.sub(r'[^\d\.]+', '', str(number)))


def get_tokens_df():
    global tokens_df
    global tokens_df_last_update

    elapsed_time = time.time() - tokens_df_last_update if tokens_df_last_update is not None else None

    if tokens_df is None or elapsed_time is None or elapsed_time > settings.runtime.utils.pandas.tokens_df_refresh_interval:
        tokens_df = pd.read_csv(get_data_path() + 'tokens.csv')
        tokens_df_last_update = time.time()

    return tokens_df


def get_tokens_holders_df():
    global tokens_holders_df
    global tokens_holders_df_last_update

    elapsed_time = time.time() - \
        tokens_holders_df_last_update if tokens_holders_df_last_update is not None else None

    if tokens_holders_df is None or elapsed_time is None or elapsed_time > settings.runtime.utils.pandas.tokens_holders_df_refresh_interval:
        tokens_holders_df = pd.read_csv(get_data_path() + 'tokens_holders.csv')
        tokens_holders_df_last_update = time.time()

    return tokens_holders_df


def accounts_table_to_df(table_html):
    rows = table_html.find_all('tr')
    # each td is a column
    # we will use the function STRING.replace() in order to clear the data
    addresses = [rows[i].find_all('td')[1].a['href'].replace(
        '/address/', '') for i in range(1, len(rows))]
    is_contracts = map(lambda address: 1 if is_contract(address) else 0, addresses)
    balances = [rows[i].find_all('td')[3].text.replace('\n', '').replace(' ', '').replace(',', '') for i in
                range(1, len(rows))]
    percentages = [rows[i].find_all('td')[4].text for i in range(1, len(rows))]

    # format
    balances = map(format_str_as_number, balances)
    percentages = map(format_str_as_number, percentages)

    table = pd.DataFrame(list(zip(
        addresses,
        balances,
        percentages,
        is_contracts)),
        columns=['address', 'balance_in_ether', 'ether_share_percent', 'is_contract'])

    return table


def convert_link_to_address(cell):
    return re.compile(r'^.*a=([\da-z]+)$', flags=re.IGNORECASE).sub('\\1', cell[1]).lower()


def parse_number(cell):
    return locale.atof(re.compile(r'[^\d\.]').sub('', cell[0]))


def holders_table_to_df(table_html):
    table_as_df: pd.DataFrame = pd.read_html(str(table_html), converters={
        0: parse_number,
        1: convert_link_to_address,
        2: parse_number,
        3: parse_number,
    }, extract_links='body')[0]

    table_as_df.drop(table_as_df.columns[4:], axis=1, inplace=True)

    table_as_df.columns = ['rank', 'address', 'qty', 'percentage']
    table_as_df.reset_index(drop=True, inplace=True)

    return table_as_df


def merge_tokens_dicts_into_df(dict1, dict2, key):
    df = pd.merge(pd.DataFrame(dict1, columns=[
                  'symbol', 'name', 'address', 'market_cap', 'price_usd']), pd.DataFrame(dict2, columns=[
                      'symbol', 'name', 'address', 'market_cap', 'price_usd']), on=key, how='outer')

    # clean up
    df.dropna(subset=['market_cap_x'], inplace=True)
    df.drop_duplicates(subset=['symbol'], ignore_index=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.drop(['name_y', 'address_y', 'market_cap_y', 'price_usd_y'], axis=1, inplace=True)
    df.rename(columns={'name_x': 'name', 'market_cap_x': 'market_cap',
              'address_x': 'address', 'price_usd_x': 'price_usd'}, inplace=True)

    return df


def get_address_details(address: str) -> dict:
    tokens = (get_tokens_df()).copy()
    tokens_holders_df = (get_tokens_holders_df()).copy()

    # sort them by symbol
    tokens.sort_values(by=['symbol'], inplace=True)
    tokens_holders_df.sort_values(by=['token_symbol'], inplace=True)
    wallet = tokens_holders_df.copy()[tokens_holders_df['address'] == address]

    del wallet['percentage']
    del tokens['address']

    wallet_tokens = tokens.copy()[tokens['symbol'].isin(list(wallet['token_symbol']))]
    wallet.reset_index(drop=True, inplace=True)
    wallet_tokens.reset_index(drop=True, inplace=True)

    wallet.loc[:, ('wallet_holdings_usd')] = wallet.qty.mul(wallet_tokens.price_usd)
    total_usd = wallet.wallet_holdings_usd.sum()
    wallet.loc[:, ('wallet_portfolio_alloc')] = (
        wallet.wallet_holdings_usd.mul(100))/total_usd

    wallet = wallet.merge(tokens, left_on='token_symbol', right_on='symbol')
    wallet.loc[:, ('wallet_market_percent')] = (
        wallet.wallet_holdings_usd.mul(100))/wallet.market_cap
    wallet.rename(columns={'address_x': 'wallet_address', 'address_y': 'token_address',
                           'name': 'token_name', 'price_usd': 'token_price_usd',
                           'qty': 'wallet_holdings_qty', 'market_cap': 'token_market_cap'}, inplace=True)
    wallet.sort_values(by=['wallet_portfolio_alloc', 'wallet_market_percent'],
                       ascending=False, inplace=True)

    del wallet['symbol']

    return wallet.copy().to_dict(orient='records')


def get_token_by_symbol(symbol: str) -> dict:
    tokens = get_tokens_df().copy()
    result = tokens[tokens['symbol'] == symbol.upper()]
    result = result.dropna(axis='columns')
    result = result.to_dict(orient='records')
    result = result[0] if len(result) > 0 else None

    return result


def get_token_by_address(address) -> dict:
    if address == None:
        return None

    if address != None and is_eth_address(str(address)):
        return {
            'symbol': 'ETH',
            'name': 'Ethereum',
            'decimals': 18,
            'address': '0x0000000000000000000000000000000000000000'
        }

    tokens = get_tokens_df().copy()
    result = tokens[tokens['address'] == address.lower()]
    result = result.dropna(axis='columns')
    result = result.to_dict(orient='records')
    result = result[0] if len(result) > 0 else None

    return result


def fill_diverged_columns(df, suffix):
    for col in df:
        try:
            df[col].fillna(df[col+suffix], inplace=True)
            df.drop([col + suffix], axis=1, inplace=True)
        except:
            pass
