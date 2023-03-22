from typing import List

import pandas as pd
from com.cryptobot.classifiers.tx import TXClassifier
from com.cryptobot.config import Config
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.pandas_utils import get_tokens_holders_df


class MempoolWhaleTXClassifier(TXClassifier):
    def __init__(self, **args):
        super().__init__(__name__, **args)

        settings = Config().get_settings().runtime.classifiers
        settings = settings.MempoolWhaleTXClassifier if hasattr(
            settings, 'MempoolWhaleTXClassifier') else None

        # load up the list of big wallets collected by com.cryptobot.extractors.TokenHoldersExtractor
        self.tokens_holders_df = get_tokens_holders_df(settings.min_wallet_alloc_usd)
        self.whales_addresses = list(
            map(lambda address: address.lower(), list(self.tokens_holders_df.address.unique())))

        self.logger.info(f'Loaded {len(self.whales_addresses)} addresses.')

    def filter(self, items: List[Tx]) -> List[Tx]:
        return list(item for item in items if (
            str(item.sender).lower() in self.whales_addresses
            or str(item.receiver).lower() in self.whales_addresses
        ))
