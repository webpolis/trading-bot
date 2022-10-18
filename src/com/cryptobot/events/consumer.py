import atexit
import logging
from typing import List

from com.cryptobot.config import Config
from com.cryptobot.events.producer import EventsProducerMixin
from com.cryptobot.utils.logger import PrettyLogger
from rsmq.consumer import RedisSMQConsumerThread


class EventsConsumerMixin():
    def __init__(self, queues: List[str] | str, *args, **kwargs) -> None:
        self._logger = PrettyLogger(__name__, logging.INFO)
        self.settings = Config().get_settings()
        self.host = self.settings.redis.host
        self.port = self.settings.redis.port
        self.trace = True
        self.vt = 30
        self.delay = 0
        self.ns = EventsProducerMixin.__class__.__name__
        self.queues = [queues] if type(queues) != type([]) else queues
        self.consumers = {}

        for queue in self.queues:
            self.consumers[queue] = RedisSMQConsumerThread(
                qname=queue, processor=self.process, host=self.host, port=self.port,
                ns=self.ns, vt=self.vt, empty_queue_delay=2, trace=self.trace, decode=True)

        atexit.register(self.stop)

    def consume(self):
        for queue in self.queues:
            self.logger.info(f'Listening to {queue} queue')

            self.consumers[queue].start()

    def process(self, message=None, id=None, rc=None, ts=None):
        pass

    def stop(self):
        for queue in self.queues:
            self.logger.info(f'Stopping listener for {queue} queue')

            self.consumers[queue].stop()
