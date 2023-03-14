import logging
from com.cryptobot.mappers.mapper import MapType, map_runner
from com.cryptobot.schemas.token import Token
from com.cryptobot.schemas.tx import Tx, TxType
from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.utils.pandas_utils import get_token_by_address

logger = PrettyLogger(__name__, logging.INFO)


class SwapTx(Tx):
    def __init__(self, tx: Tx):
        super().__init__(tx.timestamp, tx.block_number, tx.hash, tx.sender, tx.receiver,
                         tx.gas, tx.gas_price, tx.value, tx.input, tx.decoded_input, TxType.SWAP, tx.raw)

        # handle multiple signatures while extracting the swap details
        params = self.decoded_input['func_params']
        map_output = map_runner(params, MapType.SWAP)

        if map_output != None:
            token_from = map_output['token_from'].lower()
            token_to = map_output['token_to'].lower()
            token_from_info = get_token_by_address(token_from)
            self.token_from = Token.from_dict(token_from_info, address=token_from)
            self.token_from_qty = map_output['token_from_qty'] if 'token_from_qty' in map_output else tx.value
            token_to_info = get_token_by_address(token_to)
            self.token_to = Token.from_dict(token_to_info, address=token_to)
            self.token_to_qty = map_output['token_to_qty']
        else:
            self.token_from = None
            self.token_to = None
            self.token_from_qty = -1
            self.token_to_qty = -1

            logger.info(f'No mapping output for Swap transaction {self.hash}')

        if hasattr(self, 'token_from_qty') and type(self.token_from_qty) == str:
            self.token_from_qty = int(self.token_from_qty, 0)

        if hasattr(self, 'token_to_qty') and type(self.token_to_qty) == str:
            self.token_to_qty = int(self.token_to_qty, 0)

    def __str__(self):
        return str({'timestamp': str(self.timestamp), 'sender': self.sender.address, 'receiver': self.receiver.address,
                    'token_from': str(self.token_from) if self.token_from is not None else None, 'token_from_qty': self.token_from_qty,
                    'token_to': str(self.token_to) if self.token_to is not None else None, 'token_to_qty': self.token_to_qty,
                    'hash': self.hash, 'block_number': self.block_number, 'value': self.value})
