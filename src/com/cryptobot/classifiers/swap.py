import json
import re
from typing import List

from com.cryptobot.classifiers.tx import TXClassifier
from com.cryptobot.events.consumer import EventsConsumerMixin
from com.cryptobot.events.producer import EventsProducerMixin
from com.cryptobot.schemas.swap_tx import SwapTx
from com.cryptobot.schemas.tx import Tx
from jsonpickle import encode, decode


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
        txs = list(map(lambda tx: decode(tx), message['item']))

        self.logger.info(f"Processing {len(txs)} transaction(s)...")

        swap_txs: List[SwapTx] = self.classify(txs)
        swap_count = len(swap_txs)

        if swap_count > 0:
            self.logger.info(f'Found {swap_count} swap transaction(s) this time.')

            encoded_swaps = [encode(swap, max_depth=3) for swap in swap_txs]

            self.logger.info('Publishing swaps...')
            self.publish(encoded_swaps, True)

        return True

    def parse(self, items) -> List[SwapTx]:
        items: List[Tx] = super().parse(items)
        swap_txs = []

        for tx in items:
            # make sure the transaction is processed only once
            if self.cache.has_tx(tx.hash):
                continue
            else:
                self.cache.add_tx(tx.hash)

            decoded_input = tx.decode_input()

            if decoded_input != None:
                func_name = decoded_input['func_obj'].fn_name

                if re.match(r'^swap.*$', func_name, flags=re.IGNORECASE) is not None:
                    # evolve tx
                    tx = SwapTx(tx)
                    swap_txs.append(tx)
                else:
                    self.logger.debug(
                        f'Address {str(tx.sender)} executed {func_name} on {str(tx.receiver)}')

        return swap_txs

    def filter(self, items: List[SwapTx]) -> List[SwapTx]:
        return items
