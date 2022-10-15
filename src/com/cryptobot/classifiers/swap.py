import json
import re
from typing import List
from com.cryptobot.classifiers.tx import TXClassifier
from com.cryptobot.events.consumer import EventsConsumerMixin
from com.cryptobot.events.producer import EventsProducerMixin
from com.cryptobot.schemas.swap_tx import SwapTx
from com.cryptobot.schemas.tx import Tx


class SwapClassifier(TXClassifier, EventsConsumerMixin, EventsProducerMixin):
    def __init__(self, **args):
        for base_class in SwapClassifier.__bases__:
            if base_class == EventsConsumerMixin:
                base_class.__init__(self, queues=[TXClassifier.__name__])
            elif base_class == EventsProducerMixin:
                base_class.__init__(self, queue=SwapClassifier.__name__)
            else:
                base_class.__init__(self, __name__, **args)

    def process(self, message=None, id=None, rc=None, ts=None):
        txs = list(map(lambda tx: Tx.from_dict(json.loads(tx)), message['item']))

        self.logger.info(f"Processing {len(txs)} transactions...")

        swap_txs = self.classify(txs)
        swap_count = len(swap_txs)

        self.logger.info(f'Found {swap_count} swap transaction(s) this time.')

        if swap_count > 0:
            encoded_swaps = [str(swap) for swap in swap_txs]

            self.publish(encoded_swaps)

        return True

    def parse(self, items) -> List[SwapTx]:
        items: List[Tx] = super().parse(items)
        swap_txs = []

        for tx in items:
            # make sure the transaction is processed only once
            if self.cache.has_tx(tx):
                continue
            else:
                self.cache.add_tx(tx)

            decoded_input = tx.decode_input()

            if decoded_input != None:
                if re.match(r'^swap.*$', decoded_input['func_obj'].fn_name, flags=re.IGNORECASE) is not None:
                    # evolve tx
                    tx = SwapTx(tx)
                    swap_txs.append(tx)

        return swap_txs

    def filter(self, items: List[SwapTx]) -> List[SwapTx]:
        return super().filter(items)
