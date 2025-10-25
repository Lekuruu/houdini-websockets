
from websockets.exceptions import ConnectionClosed, WebSocketException
from websockets.asyncio.server import ServerConnection
from contextlib import suppress
from .utils import resolve_ip_address

import asyncio

class WebsocketWriter:
    """Replacement for the `StreamWriter` class in asyncio"""
    info_handlers = {'peername': resolve_ip_address}

    def __init__(self, websocket: ServerConnection):
        self.websocket = websocket
        self.stack = b''
        self.closing = False
        self.close_task = None
        self.drain_task = None

    def write(self, data: bytes) -> None:
        if self.closing:
            return

        self.stack += data

        if self.drain_task is None or self.drain_task.done():
            # Only create a new drain task if one isn't already running
            self.drain_task = asyncio.create_task(self.drain())

    async def drain(self) -> None:
        if not self.stack:
            return

        # Check if connection is closed or closing
        if self.closing or self.websocket.close_code is not None:
            self.stack = b''
            return

        try:
            await self.websocket.send(self.stack)
            self.stack = b''
        except (ConnectionClosed, WebSocketException):
            # Connection is closed, clear the stack but don't raise
            self.stack = b''
            self.closing = True

    def close(self) -> None:
        if self.closing:
            return

        self.closing = True

        if self.close_task is None or self.close_task.done():
            # Only create a close task if one doesn't exist
            self.close_task = asyncio.create_task(self.perform_close())

    def is_closing(self) -> bool:
        return self.closing or self.websocket.close_code is not None

    def get_extra_info(self, name: str, default=None):
        return self.info_handlers.get(name, lambda _: default)(self.websocket)

    async def perform_close(self) -> None:
        if self.drain_task and not self.drain_task.done():
            # Cancel any pending drain task
            self.drain_task.cancel()

            with suppress(asyncio.CancelledError):
                await self.drain_task

        with suppress(ConnectionClosed, WebSocketException):
            if self.websocket.close_code is None:
                # Close the websocket, if not already closed
                await self.websocket.close()

class WebsocketReader:
    """Replacement for the `StreamReader` class in asyncio"""
    def __init__(self, websocket: ServerConnection, writer: "WebsocketWriter" = None) -> None:
        self.websocket = websocket
        self.writer = writer
        self.stack = b''

    async def readuntil(self, separator: bytes) -> bytes:
        while True:
            # Check if connection is closed first
            is_closing = (
                (self.writer.closing if self.writer else False) or
                self.websocket.close_code is not None
            )

            if is_closing:
                raise ConnectionResetError()

            if separator in self.stack:
                index = self.stack.index(separator)
                data = self.stack[:index + len(separator)]
                self.stack = self.stack[index + len(separator):]
                return data

            try:
                chunk = await self.websocket.recv()

                # Ensure chunk is in bytes
                if isinstance(chunk, str):
                    chunk = chunk.encode('utf-8')

                self.stack += chunk
            except (ConnectionClosed, WebSocketException):
                if self.writer:
                    # Mark writer as closing so it knows the connection is dead
                    self.writer.closing = True
                raise ConnectionResetError()
