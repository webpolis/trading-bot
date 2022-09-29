import time

import pandas as pd
import json
from datetime import datetime, timedelta
import pandas as pd
import pygsheets
import pytz


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

    def get_txs_until_last_date(self, last_date):
        self.metrics_calculator.get_txs_until_last_date(self.scrappers, last_date)

    def get_whales(self, number_of_whales):
        return self.scrappers.get_whales(number_of_whales)

    # def get_txs(self,token, page_number):
    #     self.scrappers.get_txs(token, page_number)

    def get_whale_txs(self, whale_address, df_txs):
        return self.metrics_calculator.get_whale_vol_in_df(whale['Address'], df_txs)

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
    btc_current_price = app.historical_data[-1]
    btc_last_price = app.historical_data[-2]
    btc_change = btc_current_price / btc_last_price
    symbol = "ETHUSDC"
    app.get_historical_data(symbol=symbol, initial_date=initial_date, freq=freq, save=True)
    eth_current_price = app.historical_data[-1]
    eth_last_price = app.historical_data[-2]
    eth_change = eth_current_price / eth_last_price
    # #####################################
    # get last hour txs
    last_date = datetime.strftime(datetime.today() - timedelta(hours=0, minutes=1), format='%d/%m/%y %H:%M:%S')
    last_date = datetime.strptime(last_date, '%d/%m/%y %H:%M:%S')
    df_txs = app.metrics_calculator.get_txs_until_last_date(app.scrappers, last_date)
    # #####################################
    # get 10 whales for eth
    number_of_whales = 25
    # whales_df = app.scrappers.get_whales(number_of_whales)
    # whales_df.to_csv("/home/agustin/Git-Repos/Short-bot/files/whales_df_%s.csv" % number_of_whales)
    whales_df = pd.read_csv("/home/agustin/Git-Repos/Short-bot/files/whales_df_%s.csv" % number_of_whales)
    # #####################################
    # get txs made by whales
    for i in range(len(whales_df)):
        whale = whales_df.iloc[i]
        # print(whale['Address'])
        globals()['whale_'+str(i)+'_txs'] = app.metrics_calculator.get_whale_vol_in_df(whale['Address'], df_txs)
    # ######################################
    # writte data
    dtobj1 = datetime.utcnow()  # utcnow class method
    dtobj3 = dtobj1.replace(tzinfo=pytz.UTC)  # replace method
    dtobj_ba = dtobj3.astimezone(pytz.timezone("America/Buenos_Aires")).strftime(
        "%Y-%m-%d %H:%M:%S")  # astimezone method
    date = dtobj_ba

    datos_tab = [date,
                 btc_current_price, btc_change,
                 eth_current_price, eth_change]

    for i in range(len(whales_df)):
        datos_tab.append(globals()['whale_' + str(i) + '_txs'])
        datos_tab.append(globals()['whale_' + str(i) + '_txs']*eth_current_price)

    datos_tab_str = [str(x) for x in datos_tab]

    # print(datos_tab_str)

    # ESCRIBIMOS EL SHEET
    gc = pygsheets.authorize(service_file='/home/agustin/Git-Repos/Short-bot_simple/files/sminteractor-23ab016c70ea.json')
    sh = gc.open('ETH Short Bot')
    sh[0].append_table(datos_tab_str, end=None, dimension='ROWS', overwrite=False)

    # # metrics
    # for token in tokens:
    #     globals()[token]['Returns'] = np.around(globals()[token]['close'].pct_change().dropna(), 3)
    #     globals()[token]['std21'] = globals()[token]['Returns'].rolling(14).std() * np.sqrt(365)
    #     globals()[token] = globals()[token].dropna()
    # for token in tokens:
    #     for hour in [2, 4, 6]:
    #         globals()[token]['pcg_change_' + str(hour) + '_hours'] = globals()[token]['close'].pct_change(hour)
    #     globals()[token] = globals()[token].dropna()

    #########################################
    import requests
    TIMESTAMP_NOW = time.time()
    YourApiKeyToken = "API_KEY"
    block_number = requests.get(f"https://api.etherscan.io/api?module = block&"
                               f" action = getblocknobytime&"
                               f" timestamp = {TIMESTAMP_NOW}&"
                               f" closest = before& apikey = {YourApiKeyToken}")
    last_txs = []
    for address in addres_df:
        url_request_txs = f"https://api.etherscan.io/api?module = account&" \
                          f"action = tokenbalancehistory&" \
                          f" contractaddress = {token_address}&" \
                          f" address = {address}&" \
                          f" blockno = {last_block}&" \
                          f" apikey = {YourApiKeyToken}"
        last_txs.append(request.get(url_request_txs)['result'])
    data_dumper.write_data(last_txs)