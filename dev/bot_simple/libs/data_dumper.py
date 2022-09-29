from datetime import datetime
import pygsheets
import pytz


class DataDamper:
    @staticmethod
    def write_data(pool):
        dtobj1 = datetime.utcnow()  # utcnow class method
        dtobj3 = dtobj1.replace(tzinfo=pytz.UTC)  # replace method
        dtobj_ba = dtobj3.astimezone(pytz.timezone("America/Buenos_Aires")).strftime(
            "%Y-%m-%d %H:%M:%S")  # astimezone method

        date = dtobj_ba

        datos_tab = [date,
                     pool.tvl, pool.daily_volume, pool.daily_fees,
                     pool.pool_token_supply, pool.pool_token_price]
        for balance in pool.tokens_balances:
            datos_tab.append(balance)
        for price in pool.tokens_prices:
            datos_tab.append(price)

        datos_tab_str = [str(x) for x in datos_tab]

        # ESCRIBIMOS EL SHEET
        gc = pygsheets.authorize(service_file='/home/agustin/Git-Repos/algo-trading-crypto/sm-interactor'
                                              '/sm_interactor/files/sminteractor-23ab016c70ea.json')
        sh = gc.open('Pool data')
        sh.worksheet(pool.identifier).append_table(datos_tab_str, end=None, dimension='ROWS', overwrite=False)

