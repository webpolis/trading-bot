import json
import re
from typing import List
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.events.consumer import EventsConsumerMixin
from com.cryptobot.events.producer import EventsProducerMixin
from com.cryptobot.schemas.swap_tx import SwapTx
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.ethtx import EthTxWrapper


class SwapClassifier(TXClassifier, EventsConsumerMixin, EventsProducerMixin):
    def __init__(self):
        for base_class in SwapClassifier.__bases__:
            if base_class == EventsConsumerMixin:
                base_class.__init__(self, 'com.cryptobot.extractors.mempool')
            else:
                base_class.__init__(self, __name__)

        self.ethtx = EthTxWrapper()
        self.cached_txs = {}

    def process(self, message=None, id=None, rc=None, ts=None):
        self.logger.info(f"Processing {len(message['item'])} transactions...")

        swap_txs = self.classify(
            list(map(lambda tx: Tx.from_dict(json.loads(tx)), message['item'])))

        self.logger.info(f'Found {len(swap_txs)} swap transaction(s) this time.')

        return True

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
