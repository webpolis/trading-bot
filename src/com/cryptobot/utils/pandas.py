import pandas as pd


def top_addresses_table_to_df(table_html):
    rows = table_html.find_all('tr')
    columns = [element.text for element in rows[0].find_all('th')]
    # each td is a column
    # we will use the function STRING.replace() in order to clear the data
    addresses = [rows[i].find_all('td')[1].a['href'].replace(
        '/address/', '') for i in range(1, len(rows))]
    balance = [rows[i].find_all('td')[3].text.replace('\n', '').replace(' ', '').replace(',', '') for i in
               range(1, len(rows))]
    percentage = [rows[i].find_all('td')[4].text for i in range(1, len(rows))]

    table = pd.DataFrame(list(zip(
        addresses,
        balance,
        percentage)),
        columns=[columns[i] for i in [1, 3, 4]])
    return table
