
from websockets.exceptions import ConnectionClosed
from websockets import WebSocketClientProtocol
from websockets.protocol import State
from .utils import resolve_ip_address

import asyncio

class WebsocketWriter:
    """Replacement for the `StreamWriter` class in asyncio"""
    info_handlers = {'peername': resolve_ip_address}

    def __init__(self, websocket: WebSocketClientProtocol):
        self.websocket = websocket
        self.stack = b''

    def write(self, data: bytes) -> None:
        self.stack += data

    async def drain(self) -> None:
        if not self.stack:
            return

        await self.websocket.send(self.stack)
        self.stack = b''

    def close(self) -> None:
        asyncio.create_task(self.websocket.close())

    def is_closing(self) -> bool:
        return self.websocket.state == State.CLOSING

    def get_extra_info(self, name: str, default=None):
        return self.info_handlers.get(name, lambda _: default)(self.websocket)

class WebsocketReader:
    """Replacement for the `StreamReader` class in asyncio"""
    def __init__(self, websocket: WebSocketClientProtocol):
        self.websocket = websocket
        self.stack = b''

    async def readuntil(self, separator: bytes) -> bytes:
        if separator in self.stack:
            index = self.stack.index(separator)
            data = self.stack[:index + len(separator)]
            self.stack = self.stack[index + len(separator):]
            return data

        try:
            self.stack += await self.websocket.recv()
            return await self.readuntil(separator)
        except ConnectionClosed:
            raise ConnectionResetError()
