import pandas as pd


class CardanoscanGetter:
    @staticmethod
    def txs_table_to_df(table_html):
        rows = table_html.find_all('tr')
        columns = [element.text for element in rows[0].find_all('th')[1:]]
        # each td is a column
        # we will use the function STRING.replace() in order to clear the data
        hash_tx = [rows[i].find_all('td')[1].div.a['href'].replace('/transaction/', '') for i in range(1, len(rows))]
        blocks = [rows[i].find_all('td')[2].div.a['href'].replace('/block/', '') for i in range(1, len(rows))]
        dates_plus_last_txs = [rows[i].find_all('td')[3].text[:(rows[i].find_all('td')[3].text.find('M')) + 1] + ' ' +
                               rows[1].find_all('td')[3].text[(rows[i].find_all('td')[3].text.find('M')) + 1:] for i in
                               range(1, len(rows))]

        entry_addresses = []
        for i in range(1, len(rows)):
            entry_addresses.append(
                [element.a['href'].replace('/address/', '') for element in rows[i].find_all('td')[4].find_all('div') if
                 type(element.a) != type(None)])

        output_addresses = []
        for i in range(1, len(rows)):
            output_addresses.append(
                [element.a['href'].replace('/address/', '') for element in rows[i].find_all('td')[5].find_all('div') if
                 type(element.a) != type(None)])

        # maybe we wont need every single column but let's do it just in case
        commissions = [rows[i].find_all('td')[6].text.replace('\n', '').replace(' ', '')[:-1] for i in
                       range(1, len(rows))]
        total_output = [rows[i].find_all('td')[7].text.replace('\n', '').replace(' ', '')[:-1] for i in
                        range(1, len(rows))]

        table = pd.DataFrame(list(zip(
            hash_tx,
            blocks,
            dates_plus_last_txs,
            entry_addresses,
            output_addresses,
            commissions,
            total_output)),
            columns=columns)
        return table

    # We define a function to convert the top addresses table into a df
    @staticmethod
    def top_addresses_table_to_df(table_html):
        rows = table_html.find_all('tr')
        columns = [element.text for element in rows[0].find_all('th')]
        # each td is a column
        # we will use the function STRING.replace() in order to clear the data
        addresses = [rows[i].find_all('td')[0].a['href'].replace('/address/', '') for i in range(1, len(rows))]
        balance = [float(rows[i].find_all('td')[1].text.replace('\n', '').replace(' ', '').replace(',', '')[:-1]) for i
                   in range(1, len(rows))]
        trx_count = [int(rows[i].find_all('td')[2].text) for i in range(1, len(rows))]

        table = pd.DataFrame(list(zip(
            addresses,
            balance,
            trx_count)),
            columns=columns)
        return table
