import re
from typing import List
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.schemas.swap_tx import SwapTx
from com.cryptobot.schemas.tx import Tx, TxType
from com.cryptobot.utils.ethtx import EthTxWrapper


class SwapClassifier(TXClassifier):
    def __init__(self):
        super()

        self.ethtx = EthTxWrapper()
        self.cached_txs = {}

    def parse(self, items: List[Tx]) -> List[SwapTx]:
        swap_txs = []

        for tx in items:
            if tx.hash in self.cached_txs:
                continue

            decoded_input = tx.decode_input()

            if decoded_input != None:
                if re.match(r'^swap.*$', decoded_input['func_obj'].fn_name, flags=re.IGNORECASE) is not None:
                    # evolve tx
                    tx = SwapTx(tx)
                    self.cached_txs[tx.hash] = tx

                    swap_txs.append(tx)

        return swap_txs

    def filter(self, items: List[SwapTx]) -> List[SwapTx]:
        return items
