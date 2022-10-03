import decimal
from typing import List

import pandas as pd
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.formatters import tx_parse
from com.cryptobot.utils.path import get_data_path


class MempoolWhaleTXClassifier(TXClassifier):
    def parse(self, items):
        items: List[Tx] = [tx_parse(tx) for tx in items]

        return items

    def filter(self, items):
        # retrieve a list of big wallets (collected by com.cryptobot.extractors.AccountsExtractor)
        whales_df = pd.read_csv(get_data_path() + 'whales.csv',
                                converters={'balance_in_ether': decimal.Decimal})

        # filter out contracts
        whales_df = whales_df[(whales_df['is_contract'] == 0)]

        addresses = [str(address).lower() for address in list(whales_df.address)]

        return list(item for item in items if (
            str(item.sender).lower() in addresses
            or str(item.receiver).lower() in addresses
        ))
