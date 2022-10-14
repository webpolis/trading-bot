import json
import re
from typing import List
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.events.consumer import EventsConsumerMixin
from com.cryptobot.events.producer import EventsProducerMixin
from com.cryptobot.schemas.swap_tx import SwapTx
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.ethtx import EthTxWrapper
from com.cryptobot.utils.tx_queue import TXQueue


class SwapClassifier(TXClassifier, EventsConsumerMixin, EventsProducerMixin):
    def __init__(self, cached_txs: TXQueue):
        for base_class in SwapClassifier.__bases__:
            if base_class == EventsConsumerMixin:
                base_class.__init__(self, 'com.cryptobot.extractors.mempool')
            else:
                base_class.__init__(self, __name__)

        self.ethtx = EthTxWrapper()
        self.cached_txs = cached_txs

    def process(self, message=None, id=None, rc=None, ts=None):
        self.logger.info(f"Processing {len(message['item'])} transactions...")

        txs = list(map(lambda tx: Tx.from_dict(json.loads(tx)), message['item']))
        swap_txs = self.classify(txs)
        swap_count = len(swap_txs)

        self.logger.info(f'Found {swap_count} swap transaction(s) this time.')

        if swap_count > 0:
            self.logger.info([str(swap) for swap in swap_txs])

        return True

    def parse(self, items: List[Tx]) -> List[SwapTx]:
        swap_txs = []

        for tx in items:
            # make sure the transaction is processed only once
            if self.cached_txs.has_tx(tx):
                continue
            else:
                self.cached_txs.add_tx(tx)

            decoded_input = tx.decode_input()

            if decoded_input != None:
                if re.match(r'^swap.*$', decoded_input['func_obj'].fn_name, flags=re.IGNORECASE) is not None:
                    # evolve tx
                    tx = SwapTx(tx)
                    swap_txs.append(tx)

        return swap_txs

    def filter(self, items: List[SwapTx]) -> List[SwapTx]:
        return items
