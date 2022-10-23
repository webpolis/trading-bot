import socket
import asyncio
import websockets
import logging

from com.cryptobot.utils.logger import PrettyLogger
from websockets.exceptions import InvalidStatusCode


class WSClient():
    def __init__(self, url, **kwargs):
        self.logger = PrettyLogger(__name__, logging.INFO)

        self.logger.info('Initialized.')

        self.url = url
        # set some default values
        self.reply_timeout = kwargs.get('reply_timeout') or 10
        self.ping_timeout = kwargs.get('ping_timeout') or 5
        self.sleep_time = kwargs.get('sleep_time') or 5
        self.callback = kwargs.get('callback')

    async def listen_forever(self, handshake=None):
        while True:
            # outer loop restarted every time the connection fails
            self.logger.info('Creating new connection...')

            try:
                async with websockets.connect(self.url) as ws:
                    if handshake is not None:
                        self.logger.info('Initial handshake...')

                        await handshake(ws)

                        self.logger.info('Initial handshake done.')

                    while True:
                        # listener loop
                        try:
                            reply = await asyncio.wait_for(ws.recv(), timeout=self.reply_timeout)
                        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
                            try:
                                pong = await ws.ping()

                                await asyncio.wait_for(pong, timeout=self.ping_timeout)

                                self.logger.debug(
                                    'Ping OK, keeping connection alive...')

                                continue
                            except:
                                self.logger.error(
                                    'Ping error - retrying connection in {} sec (Ctrl-C to quit)'.format(self.sleep_time))

                                await asyncio.sleep(self.sleep_time)

                                break

                        self.logger.debug('Server said > {}'.format(reply))

                        if self.callback:
                            await self.callback(reply)
            except socket.gaierror:
                self.logger.error(
                    'Socket error - retrying connection in {} sec (Ctrl-C to quit)'.format(self.sleep_time))

                await asyncio.sleep(self.sleep_time)

                continue
            except ConnectionRefusedError:
                self.logger.error(
                    'Nobody seems to listen to this endpoint. Please check the URL.')
                self.logger.error(
                    'Retrying connection in {} sec (Ctrl-C to quit)'.format(self.sleep_time))

                await asyncio.sleep(self.sleep_time)

                continue
            except InvalidStatusCode as error:
                self.logger.error(error)

                await asyncio.sleep(self.sleep_time)
