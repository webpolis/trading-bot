from collections import Counter
from enum import Enum
import logging
from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.utils.python import get_class_attributes

logger = PrettyLogger(__name__, logging.INFO)


class MapType(Enum):
    SWAP = 0


class Mapper():
    def __init__(self, cls=__name__):
        self.logger = PrettyLogger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def is_mappable(self, input, map_def) -> bool:
        map_keys = map_def.keys()
        input_keys = input.keys()
        same_keys = Counter(map_keys) == Counter(input_keys)
        same_types = True

        if not same_keys:
            return False

        for key in input_keys:
            same_types = same_types and (type(input[key]) == map_def[key])

        return same_keys and same_types

    def map(self, input, map_def) -> dict:
        output = {}

        for key in map_def:
            if type(map_def[key]) == tuple:
                output[key] = input[map_def[key][0]][map_def[key][1]]
            elif type(map_def[key]) == str:
                output[key] = input[map_def[key]]

        return output


def map_runner(input, map_type: MapType):
    attrs = mapper = map_def = module = None

    if map_type == MapType.SWAP:
        import com.cryptobot.mappers.swap_mapper as swap_mapper

        module = swap_mapper
        attrs = get_class_attributes(swap_mapper)
        mapper = module.SwapMapper()

    if mapper != None:
        for cls in attrs.keys():
            is_mappable = mapper.is_mappable(input, attrs[cls])

            logger.info(f'{cls} mappable result: {is_mappable}')

            if is_mappable:
                map_def = getattr(module, cls.replace('Args', 'Map'))

                return mapper.map(input, map_def)

    return None
