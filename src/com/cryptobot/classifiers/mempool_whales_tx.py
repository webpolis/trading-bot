import pandas as pd
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.utils.formatters import tx_parse
from com.cryptobot.utils.path import get_data_path
import decimal


class MempoolWhaleTXClassifier(TXClassifier):
    def parse(self, items):
        items = [tx_parse(tx) for tx in items]

        return items

    def filter(self, items):
        # retrieve a list of big wallets (collected by com.cryptobot.extractors.AccountsExtractor)
        whales_df = pd.read_csv(get_data_path() + 'whales.csv',
                                converters={'balance_in_ether': decimal.Decimal})
        addresses = [str(address).lower() for address in list(whales_df.address)]

        return list(item for item in items if (
            str(item['from']).lower() in addresses
            or str(item['to']).lower() in addresses
        ))
