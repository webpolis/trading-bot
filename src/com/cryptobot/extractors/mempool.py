from time import sleep

from com.cryptobot.classifiers.mempool_whale_tx import \
    MempoolWhaleTXClassifier
from com.cryptobot.classifiers.swap import SwapClassifier
from com.cryptobot.classifiers.tx import TXClassifier
from com.cryptobot.config import Config
from com.cryptobot.events.consumer import EventsConsumerMixin
from com.cryptobot.events.producer import EventsProducerMixin
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.utils.ethereum import fetch_mempool_txs
from com.cryptobot.utils.python import get_class_by_fullname
from com.cryptobot.utils.tx_queue import TXQueue


class MempoolExtractor(Extractor, EventsProducerMixin):
    def __init__(self):
        for base_class in MempoolExtractor.__bases__:
            if base_class == EventsProducerMixin:
                base_class.__init__(self, queue=TXClassifier.__name__)
            else:
                base_class.__init__(self, __name__)

        self.cached_txs = TXQueue()
        self.classifiers = []

        for clf in Config().get_settings().runtime.extractors.mempool.classifiers:
            cls = get_class_by_fullname(clf)

            self.classifiers.append(cls)

    def listen(self):
        self.logger.info('Monitoring the mempool...')

        ondemand_classifiers = [
            cls(cache=self.cached_txs) for cls in self.classifiers if not issubclass(cls, EventsConsumerMixin)]
        consumers_classifiers = [
            cls for cls in self.classifiers if issubclass(cls, EventsConsumerMixin)]

        for consumer in consumers_classifiers:
            settings = getattr(Config().get_settings(
            ).runtime.classifiers, consumer.__name__)
            max_concurrent_threads = getattr(
                settings, 'max_concurrent_threads') if settings is not None else 1

            for i in range(0, max_concurrent_threads):
                consumer(cache=self.cached_txs).consume()

        while (True):
            try:
                mempool_txs_orig = fetch_mempool_txs()
                mempool_txs = mempool_txs_orig

                # initialize on demand classifiers
                for ondemand in ondemand_classifiers:
                    mempool_txs = ondemand.classify(mempool_txs)

                if len(mempool_txs) > 0:
                    current_block = mempool_txs[0].block_number

                    self.logger.info(
                        f'{len(mempool_txs)} transactions coming from whales have caught our attention at block #{current_block} and we\'ll start classifying them.')

                    self.publish(list(map(lambda tx: str(tx), mempool_txs)))
            except Exception as error:
                self.logger.error(error)
            finally:
                sleep(1)

    def run(self):
        self.listen()
