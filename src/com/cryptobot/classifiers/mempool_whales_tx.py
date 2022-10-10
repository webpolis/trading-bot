import decimal
from typing import List

import pandas as pd
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.formatters import tx_parse
from com.cryptobot.utils.path import get_data_path


class MempoolWhaleTXClassifier(TXClassifier):
    def __init__(self):
        super()

        # load up the list of big wallets collected by com.cryptobot.extractors.AccountsExtractor
        self.tokens_holders_df = pd.read_csv(get_data_path() + 'tokens_holders.csv',
                                converters={'balance_in_ether': decimal.Decimal})

        # filter out contracts
        self.tokens_holders_df = self.tokens_holders_df[(self.tokens_holders_df['is_contract'] == 0)]

    def parse(self, items):
        items: List[Tx] = [tx_parse(tx) for tx in items]

        return items

    def filter(self, items):
        addresses = [str(address).lower() for address in list(self.tokens_holders_df.address)]

        return list(item for item in items if (
            str(item.sender).lower() in addresses
            or str(item.receiver).lower() in addresses
        ))
