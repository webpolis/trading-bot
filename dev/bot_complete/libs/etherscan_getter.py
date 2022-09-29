import pandas as pd


class EtherscanGetter:
    @staticmethod
    def txs_table_to_df(table_html):
        rows = table_html.find_all('tr')
        columns = [element.text for element in rows[0].find_all('th')[1:]]
        # each td is a column
        # we will use the function STRING.replace() in order to clear the data
        txn_hash = [rows[i].find_all('td')[1].a['href'].replace('/tx/', '') for i in range(1, len(rows))]
        method = [rows[i].find_all('td')[2].text for i in range(1, len(rows))]
        block = [rows[i].find_all('td')[3].a['href'].replace('/block/', '') for i in range(1, len(rows))]
        age = [rows[i].find_all('td')[4].text for i in range(1, len(rows))]

        from_address = [rows[i].find_all('td')[6].text for i in range(1, len(rows))]
        to_address = [rows[i].find_all('td')[8].text for i in range(1, len(rows))]
        value = [rows[i].find_all('td')[9].text for i in range(1, len(rows))]

        table = pd.DataFrame(list(zip(
            txn_hash,
            method,
            block,
            age,
            from_address,
            to_address,
            value)),
            columns=[columns[i] for i in [0, 1, 2, 3, 4, 6, 7]])
        return table

    # We define a function to convert the top addresses table into a df
    @staticmethod
    def top_addresses_table_to_df(table_html):
        rows = table_html.find_all('tr')
        columns = [element.text for element in rows[0].find_all('th')]
        # each td is a column
        # we will use the function STRING.replace() in order to clear the data
        addresses = [rows[i].find_all('td')[1].a['href'].replace('/address/', '') for i in range(1, len(rows))]
        balance = [rows[i].find_all('td')[3].text.replace('\n', '').replace(' ', '').replace(',', '') for i in
                   range(1, len(rows))]
        percentage = [rows[i].find_all('td')[4].text for i in range(1, len(rows))]

        table = pd.DataFrame(list(zip(
            addresses,
            balance,
            percentage)),
            columns=[columns[i] for i in [1, 3, 4]])
        return table

