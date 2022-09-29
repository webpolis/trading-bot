import pandas as pd
from collections import namedtuple


class MetricsCalculator:
    def __init__(self):
        Whale = namedtuple('Whale', ['address'])
        self.whales_data = {}
        # last_date = '2022-07-10 12:00:00'
        # last_date = pd.to_datetime(last_date, format="%Y-%m-%d %H:%M:%S")

    def divide_df_in_freq_blocks(self, freq, df_txs):
        index = 0
        number_of_blocks = 0
        txs_blocks_of_freq = []
        df_txs_age_as_datetime = pd.to_datetime(df_txs['\n\nAge\n\n'], format="%Y-%m-%d %H:%M:%S")
        while index < len(df_txs):
            # We define the initial_datetime as the datetime for the i-th index
            initial_datetime = pd.to_datetime(df_txs['\n\nAge\n\n'][index], format="%Y-%m-%d %H:%M:%S")
            # We define final_datetime as initial_datetime + freq
            final_datetime = initial_datetime + pd.Timedelta(seconds=freq)
            # We calculate the index at which final_datetime is reached
            # as the Age field has repeated values (several txs in the last X seconds) we have to use [index:] for
            # df_txs and df_txs_age_as_datetime
            index_to_check = [initial_datetime <= i < final_datetime for i in df_txs_age_as_datetime[index:]]
            # indexes_between_dates = df_txs.loc[index_to_check]
            # We filter txs between initial_datetime and end_datetime
            txs_between_dates = df_txs[index:].iloc[index_to_check]
            txs_blocks_of_freq.append(txs_between_dates)
            # We update i summing up the indexes in between_indexes
            index += sum(index_to_check)
            number_of_blocks += 1
        return txs_blocks_of_freq

    def get_whale_txs(self, whale, freq, df_txs):
        # Now we define a time window and we track the txs made by whales for all the txs between today and last_date
        txs_blocks_of_freq = self.divide_df_in_freq_blocks(freq, df_txs)
        # self.whales_data['whale_number_'+str(whale.number)] = {}
        # self.whales_data['whale_number_'+str(whale.number)]['address'] = whale.address
        movements = {}
        for block_number in range(len(txs_blocks_of_freq)):
            # self.whales_data['whale_number_'+str(whale.number)]['vol_block_n_' + str(block_number)
            #                                                     + '_of_freq_' + str(freq)] = \
            #     self.get_whale_vol_in_df(whale.address, txs_blocks_of_freq[block_number])
            aux_df = txs_blocks_of_freq[block_number]
            aux_df.index = range(len(txs_blocks_of_freq[block_number]))
            movements['vol_block_n_' + str(block_number) + '_of_freq_' + str(freq)] = \
                self.get_whale_vol_in_df(whale.address, aux_df)
        return movements
    
    # First we find the page number that contains the oldest txs with respect to our last_date
    def get_txs_until_last_date(self, scrappers_instance, token, last_date):
        """
        call_driver has to be a method that returns i-th page txs table as df
        urt_to_txs_page_i has to be a method that
        """
        # We will walk through different txs pages until we reach
        # a row_number with a datetime older or equal to last_date
        page_number = 1
        txs_df = scrappers_instance.get_txs(token, page_number)
        frames = [txs_df]
        row_number = 0
        date_row_number = pd.to_datetime(txs_df['\n\nAge\n\n'][row_number], format="%Y-%m-%d %H:%M:%S")
        # We will read all txs in all pages until we reach the page which contains a txs as oldest as our last_date
        while (date_row_number - last_date).total_seconds() > 0:
            # If we walked through all the txs in page i, then i <-- i+1 and update everything
            while(row_number < len(txs_df)):
                print(row_number, len(txs_df))
                date_row_number = pd.to_datetime(txs_df['\n\nAge\n\n'][row_number], format="%Y-%m-%d %H:%M:%S")
                row_number += 1
            page_number += 1
            # url_to_txs_page_i = 'https://etherscan.io/txs?p=' + str(page_number)
            txs_df = scrappers_instance.get_txs(token, page_number)
            frames.append(txs_df)
            row_number = 0
            date_row_number = pd.to_datetime(txs_df['\n\nAge\n\n'][row_number], format="%Y-%m-%d %H:%M:%S")
            # Else we go to the next tx

        # MODIFICAR CÓMO APPENDEO EN FRAMES XQ EL ULTIMO DF SE LO METO COMPLETO PERO PUEDE PASAR QUE last_date LLEGUE
        # HASTA CIERTO ROW Y NO HASTA EL FINAL
        return pd.concat(frames)


    # We define a function that returns a dict with the address of each whale and the vol of txs
    # for every whale in a given whale_list and for all txs in a given df_txs
    def get_whale_vol_in_df(self, whale_address, df_txs):
        """
        :param whale_address
        :param df_txs: a df with txs. CUANDO DIVIDO LAS TXS EN PEDAZOS THE LONGITUD freq LLAMO A ESTA FUNCIÓN PERO PASO df_txs COMO LISTA MEPA
        :return:
        """
        # For every txs associated with address_whale we sum the volume and save it into the dict whale_data
        vol = 0
        for i in range(len(df_txs.index)):
            address = df_txs['\n\nFrom\n\n'][i]
            if whale_address == address:
                vol += float(df_txs.loc[i]['\nValue'].replace('Ether', ''))
        return vol

if __name__ == '__main__':
    from datetime import datetime
    import json
    import scheduler
    import token_
    import whale
    with open('/home/agustin/Git-Repos/Short-bot/config/config.json') as json_file:
        config = json.load(json_file)
    app = scheduler.Scheduler(config)
    metrics = MetricsCalculator()
    app.tokens = {}
    for item in config["tokens"]:
        # print(config["tokens"][item])
        app.tokens[item] = token_.Token(name=item,
                                        symbol=config["tokens"][item]["symbol"],
                                        network=config["tokens"][item]["network"])
    number_of_whales = 10
    # whales_df = app.get_whales(app.tokens["ether"], number_of_whales)
    # whales_df.to_csv("/home/agustin/Git-Repos/Short-bot/files/whales_df_%s.csv" % number_of_whales)
    whales_df = pd.read_csv("/home/agustin/Git-Repos/Short-bot/files/whales_df_%s.csv" % number_of_whales)
    for i in range(len(whales_df)):
        element = whales_df.iloc[i]
        app.tokens["ether"].whales[str(i)] = whale.Whale()
        app.tokens["ether"].whales[str(i)].address = element['Address']
        app.tokens["ether"].whales[str(i)].balance = element['\n Balance']
        app.tokens["ether"].whales[str(i)].mkt_share = element['Percentage']

    last_date = '07/01/22 12:00:00'
    last_date = datetime.strptime(last_date, '%m/%d/%y %H:%M:%S')
    # df_txs = app.get_txs_until_last_date(app.tokens["ether"], last_date)
    # df_txs.to_csv("/home/agustin/Git-Repos/Short-bot/files/txs_df_%s.csv" % last_date)
    df_txs = pd.read_csv("/home/agustin/Git-Repos/Short-bot/files/txs_df_%s.csv" % last_date)
    freq = 2 * 60 * 60  # window of 2hs in seconds
    whale_ = app.tokens["ether"].whales["0"]
    print(metrics.get_whale_txs(whale_, freq, df_txs))