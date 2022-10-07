import pandas as pd
import re
from com.cryptobot.utils.ethereum import is_contract
from com.cryptobot.utils.formatters import format_str_as_number


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
    return re.compile(r'^.*a=([\da-z]+)$').sub('\\1', cell[1])


def parse_number(cell):
    return re.compile(r'[^\d\.\,]').sub('', cell[0])


def holders_table_to_df(table_html):
    table_as_df: pd.DataFrame = pd.read_html(str(table_html), converters={
        0: parse_number,
        1: convert_link_to_address,
        2: parse_number,
        3: parse_number,
        4: parse_number,
    }, extract_links='body')[0]

    table_as_df.drop(table_as_df.columns[5:], axis=1, inplace=True)

    table_as_df.columns = ['rank', 'address', 'qty', 'percentage', 'value']
    table_as_df.reset_index(drop=True, inplace=True)

    return table_as_df


def merge_tokens_dicts_into_df(dict1, dict2, key):
    df = pd.merge(pd.DataFrame(dict1, columns=[
                  'symbol', 'name', 'address', 'market_cap']), pd.DataFrame(dict2, columns=[
                      'symbol', 'name', 'address', 'market_cap']), on=key, how='outer')

    # clean up
    df.dropna(subset=['market_cap_x'], inplace=True)
    df.drop_duplicates(subset=['symbol'], ignore_index=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.drop(['name_y', 'address_y', 'market_cap_y'], axis=1, inplace=True)
    df.rename(columns={'name_x': 'name', 'market_cap_x': 'market_cap',
              'address_x': 'address'}, inplace=True)

    return df
