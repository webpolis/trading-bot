from com.cryptobot.schemas.tx import Tx, TxType
from com.cryptobot.utils.pandas import get_token_by_address


class SwapTx(Tx):
    def __init__(self, tx: Tx):
        super().__init__(tx.block_number, tx.hash, tx.sender, tx.receiver,
                         tx.gas, tx.gas_price, tx.value, tx.input, tx.decoded_input, TxType.SWAP, tx.raw)

        # handle multiple signatures while extracting the swap details
        params = self.decoded_input['func_params']

        if 'path' in params:
            # Uniswap based contract
            self.token_from = params['path'][0].lower()
            self.token_to = params['path'][-1].lower()
            self.token_from_qty = params['amountIn'] if 'amountIn' in params else self.value

            # output qty's key may vary
            self.token_to_qty = params['amountOutMin'] if 'amountOutMin' in params else None
            self.token_to_qty = params['amountOut'] if 'amountOut' in params else self.token_to_qty
        elif 'desc' in params:
            # 1inch based contract
            self.token_from = params['desc'][0].lower()
            self.token_to = params['desc'][1].lower()
            self.token_from_qty = params['desc'][-4]
            self.token_to_qty = params['desc'][-3]
        elif 'singleSwap' in params:
            # Balancer vault based contract
            self.token_from = params['singleSwap'][2].lower()
            self.token_to = params['singleSwap'][3].lower()
            self.token_from_qty = params['singleSwap'][4]
            self.token_to_qty = params['limit']  # a minimum amount to receive

        if hasattr(self, 'token_from_qty') and type(self.token_from_qty) == str:
            self.token_from_qty = int(self.token_from_qty, 0)

        if hasattr(self, 'token_to_qty') and type(self.token_to_qty) == str:
            self.token_to_qty = int(self.token_to_qty, 0)

    def __str__(self):
        return str({'sender': self.sender, 'receiver': self.receiver,
                    'token_from': self.token_from, 'token_from_qty': self.token_from_qty,
                    'token_to': self.token_to, 'token_to_qty': self.token_to_qty,
                    'hash': self.hash, 'block_number': self.block_number})

    def metadata(self) -> dict:
        metadata = super().metadata()
        token_from_df = get_token_by_address(self.token_from)
        token_to_df = get_token_by_address(self.token_to)

        return {**metadata, 'token_from': token_from_df, 'token_to': token_to_df}
