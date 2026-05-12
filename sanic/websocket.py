import asyncio


class WebSocketConnection:
    def __init__(self, send, receive):
        self._send = send
        self._receive = receive
        self._accepted = False
        self._closed = False

    async def accept(self, subprotocol=None):
        msg = {"type": "websocket.accept"}
        if subprotocol:
            msg["subprotocol"] = subprotocol
        await self._send(msg)
        self._accepted = True

    async def send(self, data):
        if isinstance(data, bytes):
            await self._send({"type": "websocket.send", "bytes": data})
        else:
            await self._send({"type": "websocket.send", "text": str(data)})

    async def recv(self, timeout=None):
        if timeout is not None:
            msg = await asyncio.wait_for(self._receive(), timeout=timeout)
        else:
            msg = await self._receive()

        if msg["type"] == "websocket.disconnect":
            self._closed = True
            return None
        return msg.get("text") or msg.get("bytes")

    receive = recv

    async def close(self, code=1000, reason=""):
        if not self._closed:
            self._closed = True
            await self._send({
                "type": "websocket.close",
                "code": code,
                "reason": reason,
            })

    @property
    def closed(self):
        return self._closed

    def __aiter__(self):
        return self

    async def __anext__(self):
        data = await self.recv()
        if data is None:
            raise StopAsyncIteration
        return data
