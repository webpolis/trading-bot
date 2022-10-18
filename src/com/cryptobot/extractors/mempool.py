import asyncio
import json
from typing import List

from com.cryptobot.classifiers.mempool_whale_tx import MempoolWhaleTXClassifier
from com.cryptobot.classifiers.swap import SwapClassifier
from com.cryptobot.classifiers.tx import TXClassifier
from com.cryptobot.config import Config
from com.cryptobot.events.consumer import EventsConsumerMixin
from com.cryptobot.events.producer import EventsProducerMixin
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.ethereum import fetch_mempool_txs
from com.cryptobot.utils.python import get_class_by_fullname
from com.cryptobot.utils.tx_queue import TXQueue
from jsonpickle import encode
from websockets import connect
from websockets.connection import ConnectionClosed


class MempoolExtractor(Extractor, EventsProducerMixin):
    def __init__(self):
        for base_class in MempoolExtractor.__bases__:
            if base_class == EventsProducerMixin:
                base_class.__init__(self, queue=TXClassifier.__name__)
            else:
                base_class.__init__(self, __name__)

        self.cached_txs = TXQueue()
        self.classifiers = []

        classifiers_paths = ['com.cryptobot.classifiers.tx.TXClassifier'] + \
            Config().get_settings().runtime.extractors.mempool.classifiers

        for clf in classifiers_paths:
            cls = get_class_by_fullname(clf)

            self.classifiers.append(cls)

    def listen(self):
        self.logger.info('Monitoring the mempool...')

        # setup classifiers
        self.ondemand_classifiers = [
            cls(cache=self.cached_txs) for cls in self.classifiers if not issubclass(cls, EventsConsumerMixin)]
        self.consumers_classifiers = [
            cls for cls in self.classifiers if issubclass(cls, EventsConsumerMixin)]

        for consumer in self.consumers_classifiers:
            settings = getattr(Config().get_settings(
            ).runtime.classifiers, consumer.__name__)
            max_concurrent_threads = getattr(
                settings, 'max_concurrent_threads') if settings is not None else 1

            for i in range(0, max_concurrent_threads):
                consumer(cache=self.cached_txs).consume()

        # start listening
        asyncio.run(self.get_pending_txs())

    async def get_pending_txs(self):
        async with connect(Config().get_settings().web3.providers.alchemy.wss) as wss:
            await wss.send('{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["alchemy_pendingTransactions"]}')
            await wss.recv()

            while True:
                try:
                    response = json.loads(await asyncio.wait_for(wss.recv(), timeout=15))
                    mempool_txs = [response['params']['result']]

                    # initialize on demand classifiers
                    for ondemand in self.ondemand_classifiers:
                        mempool_txs: List[Tx] = ondemand.classify(mempool_txs)

                    if len(mempool_txs) > 0:
                        self.publish(
                            list(map(lambda tx: encode(tx, max_depth=3), mempool_txs)))
                except ConnectionClosed:
                    continue
                except Exception as error:
                    self.logger.error(error)

                    await self.restart_ws(wss)
                    await asyncio.sleep(1)

                    continue

    async def restart_ws(self, wss):
        await wss.close()
        await wss.wait_closed()

        await wss.send('{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["alchemy_pendingTransactions"]}')
        await wss.recv()

    def run(self):
        self.listen()
