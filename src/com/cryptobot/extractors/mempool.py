from time import sleep
from typing import List
from com.cryptobot.classifiers.mempool_whales_tx import MempoolWhaleTXClassifier
from com.cryptobot.classifiers.swap_classifier import SwapClassifier
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.events.producer import EventsProducerMixin
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.schemas.swap_tx import SwapTx
from com.cryptobot.utils.ethereum import fetch_mempool_txs


class MempoolExtractor(Extractor, EventsProducerMixin):
    def __init__(self):
        for base_class in MempoolExtractor.__bases__:
            base_class.__init__(self, __name__)

        self.whales_classifier = MempoolWhaleTXClassifier()
        self.swap_classifier = SwapClassifier()

    def listen(self):
        self.logger.info('Monitoring the mempool...')

        while (True):
            mempool_txs_orig = fetch_mempool_txs()
            mempool_txs = self.whales_classifier.classify(mempool_txs_orig)
            # mempool_txs = TXClassifier().classify(mempool_txs_orig)  # for devs only

            if len(mempool_txs) > 0:
                self.logger.info(
                    f'{len(mempool_txs)} transactions coming from whales have caught our attention at block #{mempool_txs[0].block_number} and we\'ll start classifying them.')

                # classify swap transactions
                swap_txs: List[SwapTx] = self.swap_classifier.classify(mempool_txs)
                swaps_count = len(swap_txs)

                if swaps_count > 0:
                    self.logger.info(f'Detected {swaps_count} swap transactions.')

                    for swap in swap_txs:
                        try:
                            self.logger.info(str(swap))

                            # feed event system
                            self.publish(str(swap))
                        except Exception as error:
                            print({'error': error, 'tx': str(swap)})
                else:
                    self.logger.info('No swaps detected this time.')

            sleep(1)

    def run(self):
        self.listen()
