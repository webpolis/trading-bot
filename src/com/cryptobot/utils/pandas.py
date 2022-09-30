import pandas as pd
import re
from com.cryptobot.utils.ethereum import is_contract


def top_addresses_table_to_df(table_html):
    rows = table_html.find_all('tr')
    # each td is a column
    # we will use the function STRING.replace() in order to clear the data
    addresses = [rows[i].find_all('td')[1].a['href'].replace(
        '/address/', '') for i in range(1, len(rows))]
    is_contracts = map(lambda address: is_contract(address), addresses)

    balance = [rows[i].find_all('td')[3].text.replace('\n', '').replace(' ', '').replace(',', '') for i in
               range(1, len(rows))]
    percentage = [rows[i].find_all('td')[4].text for i in range(1, len(rows))]

    table = pd.DataFrame(list(zip(
        addresses,
        balance,
        percentage,
        is_contracts)),
        columns=["address", "balance_in_ether", "ether_share_percent", "is_contract"])

    return table
