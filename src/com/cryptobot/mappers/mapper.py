from collections import Counter
import logging
import com.cryptobot.mappers.swap_maps as swap_maps
from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.utils.python import get_class_attributes

logger = PrettyLogger(__name__, logging.INFO)


class Mapper():
    def __init__(self):
        self.logger = logger

        self.logger.info('Initialized.')

    def is_mappable(self, input, map) -> bool:
        map_keys = map.keys()
        input_keys = input.keys()
        same_keys = Counter(map_keys) == Counter(input_keys)
        same_types = True

        if not same_keys:
            return False

        for key in input_keys:
            same_types = same_types and (type(input[key]) == map[key])

        return same_keys and same_types

    def map(self, input) -> dict:
        if not self.is_mappable(input):
            return None

        return {}


def map_runner(input):
    attrs = get_class_attributes(swap_maps)
    mapper = Mapper()

    for cls in attrs.keys():
        is_mappable = mapper.is_mappable(input, attrs[cls])

        logger.info(f'{cls} mappable result: {is_mappable}')

    return None
