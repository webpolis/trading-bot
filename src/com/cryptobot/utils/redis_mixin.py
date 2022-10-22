import redis
from com.cryptobot.config import Config
from jsonpickle import encode, decode
from threading import Lock
from rsmq.cmd.utils import encode_message, decode_message

settings = Config().get_settings()
redis_instance = redis.Redis(host=settings.redis.host, port=settings.redis.port, db=0)


class RedisMixin():
    lock = Lock()

    def get(self, key):
        self.lock.acquire()

        key = f'{self.__hash__()}-{key}'
        value = redis_instance.get(key)
        value = decode(decode_message(value)) if value != None else None

        self.lock.release()

        return value

    def set(self, key, value, ttl=None):
        self.lock.acquire()

        key = f'{self.__hash__()}-{key}'
        value = encode_message(encode(value))

        self.lock.release()

        return redis_instance.set(key, value, ex=ttl)
