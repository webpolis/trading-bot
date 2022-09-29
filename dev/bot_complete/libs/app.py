import schedule
import time
import pandas as pd
import json
from datetime import datetime, timedelta


import data_dumper as dd
import scrappers
import metrics_calculator
import binance_client_
import token_
import whale

class Scheduler:
    def __init__(self, config):
        self.binance_client_ = binance_client_.BinanceClient(config["BinanceInteractor"])
        self.scrappers = scrappers.Scrappers(config)
        self.metrics_calculator = metrics_calculator.MetricsCalculator()
        self.data_dumper = dd.DataDamper()
        self._call_at_hour = config["Scheduler"]["at_hour"]
        self._call_every_x_minutes = config["Scheduler"]["every_x_minutes"]


    def get_historical_data(self, symbol, initial_date, freq, save=False):
        historical_data = self.binance_client_.get_all_binance(symbol, initial_date, freq, save=save)
        self.historical_data = historical_data["close"]
        for i in range(len(self.historical_data)):
            self.historical_data[i] = float(self.historical_data[i])
        # self.load_intervals()

    def get_txs(self, token, last_date, freq, page_number, number_of_whales):
        # we track (most relevant) number_of_whales whales and update token
        # with whale info address
        self.get_whales(token, number_of_whales)
        # for every whale we track their txs made until last_date in block of freq
        self.call_metrics_calculator(token, freq, last_date)
        self.call_data_dumper(token)

    def get_whales(self, token, number_of_whales):
        return self.scrappers.get_whales(token, number_of_whales)

    # def get_txs(self,token, page_number):
    #     self.scrappers.get_txs(token, page_number)

    def get_whale_txs(self, token, freq, df_txs):
        for element in token.whales:
            whale_ = token.whales[element]
            whale_.movements = self.metrics_calculator.get_whale_txs(whale_, freq, df_txs)

    def write_data(self, token):
        self.data_dumper.write_data(token)


if __name__ == '__main__':
    with open('/home/agustin/Git-Repos/Short-bot/config/config.json') as json_file:
        config = json.load(json_file)
    app = Scheduler(config)

    #####################################
    # get btc, eth price
    initial_date = datetime.strftime(datetime.today(), format="%d %b %Y")
    freq = "1h"
    symbol = "BTCUSDC"
    app.get_historical_data(symbol=symbol, initial_date=initial_date, freq=freq, save=True)
    btc_price = app.historical_data['close'][-1]

    symbol = "ETHUSDC"
    app.get_historical_data(symbol=symbol, initial_date=initial_date, freq=freq, save=True)
    eth_price = app.historical_data['close'][-1]
    # #####################################
    # get last hour txs
    last_date = datetime.strftime(datetime.today()- timedelta(hours=1), format='%d/%m/%y %H:%M:%S')
    last_date = datetime.strptime(last_date, '%d/%m/%y %H:%M:%S')
    df_txs = app.get_txs_until_last_date(app.tokens["ether"], last_date)
    df_txs.to_csv("/home/agustin/Git-Repos/Short-bot/files/txs_df_%s.csv" % last_date)
    # df_txs = pd.read_csv("/home/agustin/Git-Repos/Short-bot/files/txs_df_%s.csv" % last_date)
    # #####################################
    # get 10 whales for eth
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
    # #####################################
    # get txs made by whales
    freq = 2*60*60 # window of 2hs in seconds
    app.get_whale_txs(app.tokens["ether"], freq, df_txs)
    print([app.tokens["ether"].whales[str(i)].movements for i in range(len(whales_df))])
    # ######################################
    # # metrics
    # for token in tokens:
    #     globals()[token]['Returns'] = np.around(globals()[token]['close'].pct_change().dropna(), 3)
    #     globals()[token]['std21'] = globals()[token]['Returns'].rolling(14).std() * np.sqrt(365)
    #     globals()[token] = globals()[token].dropna()
    # for token in tokens:
    #     for hour in [2, 4, 6]:
    #         globals()[token]['pcg_change_' + str(hour) + '_hours'] = globals()[token]['close'].pct_change(hour)
    #     globals()[token] = globals()[token].dropna()