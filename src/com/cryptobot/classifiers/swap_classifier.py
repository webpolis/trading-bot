from typing import List
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.ethtx import EthTxWrapper


class SwapClassifier(TXClassifier):
    def __init__(self):
        super()

        self.ethtx = EthTxWrapper()

    def filter(self, items: List[Tx]) -> List[Tx]:
        return items
