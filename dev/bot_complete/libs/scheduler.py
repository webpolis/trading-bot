import schedule
import time
import pandas as pd
import json


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

    def run(self, token, last_date, freq, page_number, number_of_whales):
        # schedule.every(self.call_every_x_minutes).minutes.do(self.job)
        schedule.every().hour.at(self._call_at_hour).do(self.job,
                                                        token=token,
                                                        last_date=last_date,
                                                        freq=freq,
                                                        page_number=page_number,
                                                        number_of_whales=number_of_whales)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def job(self, token, last_date, freq, page_number, number_of_whales):
        self.get_data(token, last_date, freq, page_number, number_of_whales)

    def get_txs_until_last_date(self, token, last_date):
        txs_df = self.metrics_calculator.get_txs_until_last_date(self.scrappers, token, last_date)
        return txs_df

    def get_historical_data(self, symbol, initial_date, freq, save):
        historical_data = self.binance_client_.get_all_binance(symbol, initial_date, freq, save=save)
        self.historical_data = historical_data["close"]
        for i in range(len(self.historical_data)):
            self.historical_data[i] = float(self.historical_data[i])
        # self.load_intervals()

    def get_data(self, token, last_date, freq, page_number, number_of_whales):
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

    def call_data_dumper(self, token):
        self.data_dumper.write_data(token)


if __name__ == '__main__':
    with open('/home/agustin/Git-Repos/Short-bot/config/config.json') as json_file:
        config = json.load(json_file)
    app = Scheduler(config)

    #####################################
    # get btc, eth price
    # initial_date = "1 Jan 2022"
    # symbol = "BTCUSDC"
    # freq = "5m"
    # app.get_historical_data(symbol=symbol, initial_date=initial_date, freq=freq, save=True)
    # app.historical_btc = pd.DataFrame(app.historical_data, columns=["close"])
    # symbol = "ETHUSDC"
    # app.get_historical_data(symbol=symbol, initial_date=initial_date, freq=freq, save=True)
    # app.historical_btc = pd.DataFrame(app.historical_data, columns=["close"])

    # Load historical data if previously tracked and saved
    historical_5m_btc = pd.read_csv("/home/agustin/Git-Repos/Short-bot/files/BTCUSDC-5m-data.csv")
    historical_5m_eth = pd.read_csv("/home/agustin/Git-Repos/Short-bot/files/ETHUSDC-5m-data.csv")
    # assign data to stgy instance + define index as dates
    app.historical_5m_btc = pd.DataFrame(historical_5m_btc["close"], columns=['close'])
    app.historical_5m_eth = pd.DataFrame(historical_5m_eth["close"], columns=['close'])
    # timestamp = pd.to_datetime(historical_data['timestamp'])
    # stgy.historical_data.index = timestamp

    # #####################################
    # add tokens as classes
    app.tokens = {}
    for item in config["tokens"]:
        # print(config["tokens"][item])
        app.tokens[item] = token_.Token(name=item,
                                        symbol=config["tokens"][item]["symbol"],
                                        network=config["tokens"][item]["network"])
    # #####################################
    # get txs until last_date = "1 Jul 2022"
    from datetime import datetime
    last_date = '20/08/22 12:00:00'
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