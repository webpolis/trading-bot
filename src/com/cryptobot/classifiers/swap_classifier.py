import re
from typing import List
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.schemas.tx import Tx, TxType
from com.cryptobot.utils.ethtx import EthTxWrapper


class SwapClassifier(TXClassifier):
    def __init__(self):
        super()

        self.ethtx = EthTxWrapper()
        self.cached_txs = {}

    def parse(self, items: List[Tx]) -> List[Tx]:
        swap_txs = []

        for tx in items:
            if tx.hash in self.cached_txs:
                swap_txs.append(tx)
                continue

            decoded_input = tx.decode_input()

            if decoded_input != None:
                if re.match(r'^<Function swap.*$', str(decoded_input['func_obj']), flags=re.IGNORECASE) is not None:
                    tx.type = TxType.SWAP

                    self.cached_txs[tx.hash] = tx
                    swap_txs.append(tx)

        return super().parse(swap_txs)

    def filter(self, items: List[Tx]) -> List[Tx]:
        return items
