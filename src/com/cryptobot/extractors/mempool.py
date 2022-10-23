import asyncio
import json
from typing import List

from com.cryptobot.classifiers.tx import TXClassifier
from com.cryptobot.config import Config
from com.cryptobot.events.consumer import EventsConsumerMixin
from com.cryptobot.events.producer import EventsProducerMixin
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.python import get_class_by_fullname
from com.cryptobot.utils.tx_queue import TXQueue
from com.cryptobot.utils.websocket import FatalWebsocketException, WSClient
from com.cryptobot.utils.ethereum import fetch_mempool_txs

from jsonpickle import encode


class MempoolExtractor(Extractor, EventsProducerMixin):
    def __init__(self, classifiers_paths=None):
        for base_class in MempoolExtractor.__bases__:
            if base_class == EventsProducerMixin:
                base_class.__init__(self, queue=TXClassifier.__name__)
            else:
                base_class.__init__(self, __name__)

        self.cached_txs = TXQueue()
        self.classifiers = []
        self.ws = WSClient(Config().get_settings(
        ).web3.providers.alchemy.wss, callback=self.ws_callback)

        classifiers_paths = ['com.cryptobot.classifiers.tx.TXClassifier'] + \
            (
                Config().get_settings().runtime.extractors.mempool.classifiers if classifiers_paths is None
            else classifiers_paths
        )

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

    async def ws_callback(self, data, *args, **kwargs):
        response = json.loads(data)
        mempool_txs = [response['params']['result']]

        self.process_txs(mempool_txs)

    async def ws_handshake(self, ws):
        initial_payload = '{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["alchemy_pendingTransactions"]}'

        await ws.send(initial_payload)
        await ws.recv()

    async def get_pending_txs(self):
        try:
            await self.ws.listen_forever(handshake=self.ws_handshake)
        except FatalWebsocketException as error:
            # @TODO: fallback to http polling (utils.ethereum.fetch_mempool_txs)
            self.logger.error(error)
            self.logger.info('Trying fallback to http polling...')

            while True:
                try:
                    mempool_txs = fetch_mempool_txs()

                    self.process_txs(mempool_txs)
                except Exception as error:
                    self.logger.error(error)
                finally:
                    await asyncio.sleep(1)

    def process_txs(self, txs):
        # initialize on demand classifiers
        for ondemand in self.ondemand_classifiers:
            mempool_txs: List[Tx] = ondemand.classify(txs)

        if len(mempool_txs) > 0:
            self.publish(
                list(map(lambda tx: encode(tx, max_depth=3), mempool_txs)))

    def run(self):
        self.listen()
