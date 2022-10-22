import redis
from com.cryptobot.config import Config
from jsonpickle import encode, decode
from rsmq.cmd.utils import encode_message, decode_message

settings = Config().get_settings()
redis_instance = redis.Redis(host=settings.redis.host, port=settings.redis.port, db=0)


class RedisMixin():
    def __init__(self) -> None:
        pass

    def get(self, key):
        print(f'Retrieving key {key}')

        key = f'{self.__hash__()}-{key}'
        value = redis_instance.get(key)
        value = decode(decode_message(value)) if value != None else None

        return value

    def set(self, key, value, ttl=None):
        print(f'Storing key {key}')

        key = f'{self.__hash__()}-{key}'

        value = encode_message(encode(value))

        return redis_instance.set(key, value, ex=ttl)
