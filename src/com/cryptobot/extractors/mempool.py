from time import sleep
from typing import List
from com.cryptobot.classifiers.mempool_whales_tx import MempoolWhaleTXClassifier
from com.cryptobot.classifiers.swap_classifier import SwapClassifier
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.schemas.swap_tx import SwapTx
from com.cryptobot.utils.ethereum import fetch_mempool_txs


class MempoolExtractor(Extractor):
    def __init__(self):
        super().__init__(__name__)

        self.whales_classifier = MempoolWhaleTXClassifier()
        self.swap_classifier = SwapClassifier()

    def listen(self):
        self.logger.info('Monitoring the mempool...')

        while (True):
            mempool_txs_orig = fetch_mempool_txs()
            mempool_txs = self.whales_classifier.classify(mempool_txs_orig)

            if len(mempool_txs) > 0:
                self.logger.info(
                    f'{len(mempool_txs)} transactions coming from whales caught our attention at block #{mempool_txs[0].blockNumber} and we\'ll start classifying them.')

                # classify swap transactions
                swap_txs: List[SwapTx] = self.swap_classifier.classify(mempool_txs)

                if len(swap_txs) > 0:
                    for swap in swap_txs:
                        print(swap.__dict__)

                    # @TODO: feed event system

            sleep(1)

    def run(self):
        self.listen()
