from com.cryptobot.schemas.token import Token
from com.cryptobot.schemas.tx import Tx, TxType
from com.cryptobot.utils.pandas_utils import get_token_by_address


class SwapTx(Tx):
    def __init__(self, tx: Tx):
        super().__init__(tx.timestamp, tx.block_number, tx.hash, tx.sender, tx.receiver,
                         tx.gas, tx.gas_price, tx.value, tx.input, tx.decoded_input, TxType.SWAP, tx.raw)

        # handle multiple signatures while extracting the swap details
        params = self.decoded_input['func_params']

        self.token_from = None
        self.token_from_qty = -1
        self.token_to = None
        self.token_to_qty = -1

        if 'path' in params:
            # Uniswap based contract
            self.token_from = Token.from_dict(
                get_token_by_address(params['path'][0].lower()), params['path'][0].lower())
            self.token_to = Token.from_dict(
                get_token_by_address(params['path'][-1].lower()), params['path'][-1].lower())
            self.token_from_qty = params['amountIn'] if 'amountIn' in params else self.value

            # output qty's key may vary
            self.token_to_qty = params['amountOutMin'] if 'amountOutMin' in params else None
            self.token_to_qty = params['amountOut'] if 'amountOut' in params else self.token_to_qty
        elif 'desc' in params:
            desc = params['desc']

            if type(desc[0]) == int:
                # see 0x9865eebdd1ce65f45b6247aeed2fa2252eca7a08
                self.token_from = Token.from_dict(
                    get_token_by_address(desc[1].lower()), desc[1].lower())
                self.token_to = Token.from_dict(
                    get_token_by_address(desc[2].lower()), desc[2].lower())
                self.token_from_qty = float(desc[5])
                self.token_to_qty = float(desc[6])
            else:
                # 1inch based contract
                self.token_from = Token.from_dict(
                    get_token_by_address(desc[0].lower()), desc[0].lower())
                self.token_to = Token.from_dict(
                    get_token_by_address(desc[1].lower()), desc[1].lower())
                self.token_from_qty = desc[-4]
                self.token_to_qty = desc[-3]
        elif 'singleSwap' in params:
            # Balancer vault based contract
            self.token_from = Token.from_dict(
                get_token_by_address(params['singleSwap'][2].lower()), params['singleSwap'][2].lower())
            self.token_to = Token.from_dict(
                get_token_by_address(params['singleSwap'][3].lower()), params['singleSwap'][3].lower())
            self.token_from_qty = params['singleSwap'][4]
            self.token_to_qty = params['limit']  # a minimum amount to receive

        if hasattr(self, 'token_from_qty') and type(self.token_from_qty) == str:
            self.token_from_qty = int(self.token_from_qty, 0)

        if hasattr(self, 'token_to_qty') and type(self.token_to_qty) == str:
            self.token_to_qty = int(self.token_to_qty, 0)

    def __str__(self):
        return str({'timestamp': str(self.timestamp), 'sender': self.sender.address, 'receiver': self.receiver.address,
                    'token_from': str(self.token_from) if self.token_from is not None else None, 'token_from_qty': self.token_from_qty,
                    'token_to': str(self.token_to) if self.token_to is not None else None, 'token_to_qty': self.token_to_qty,
                    'hash': self.hash, 'block_number': self.block_number, 'value': self.value})
