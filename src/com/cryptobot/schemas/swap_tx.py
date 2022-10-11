from com.cryptobot.schemas.tx import Tx, TxType


class SwapTx(Tx):
    def __init__(self, tx: Tx):
        super().__init__(tx.blockNumber, tx.hash, tx.sender, tx.receiver,
                         tx.gas, tx.gasPrice, tx.value, tx.input, tx.decoded_input, TxType.SWAP, tx.raw)

        # handle multiple signatures while extracting the swap details
        if 'path' in self.decoded_input['func_params']:
            # Uniswap based contract
            self.token_from = self.decoded_input['func_params']['path'][0]
            self.token_to = self.decoded_input['func_params']['path'][-1]
            self.token_from_qty = self.decoded_input['func_params'][
                'amountIn'] if 'amountIn' in self.decoded_input['func_params'] else self.value

            # output qty's key may vary
            self.token_to_qty = self.decoded_input['func_params'][
                'amountOutMin'] if 'amountOutMin' in self.decoded_input['func_params'] else None
            self.token_to_qty = self.decoded_input['func_params'][
                'amountOut'] if 'amountOut' in self.decoded_input['func_params'] else self.token_to_qty
