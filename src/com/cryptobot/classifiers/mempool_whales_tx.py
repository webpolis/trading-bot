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
        self.etherscan_accounts_df = pd.read_csv(get_data_path() + 'etherscan_accounts.csv',
                                converters={'balance_in_ether': decimal.Decimal})

        # filter out contracts
        self.etherscan_accounts_df = self.etherscan_accounts_df[(self.etherscan_accounts_df['is_contract'] == 0)]

    def parse(self, items):
        items: List[Tx] = [tx_parse(tx) for tx in items]

        return items

    def filter(self, items):
        addresses = [str(address).lower() for address in list(self.etherscan_accounts_df.address)]

        return list(item for item in items if (
            str(item.sender).lower() in addresses
            or str(item.receiver).lower() in addresses
        ))
