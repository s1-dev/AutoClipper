import asyncio
import json

class TargetedContentBridge:
    def __init__(self, process, logger):
        self.process = process
        self.logger = logger
        self.handlers = {}

    def registerHandler(self, message_type, handler):
        self.handlers[message_type] = handler

    async def startListeningForOutput(self):
        await self.logger.log("Starting targeted content message handling.")
        buffer = b""

        try:
            while True:
                chunk = await self.process.stdout.read(16)
                if not chunk:
                    break  # Process exited

                buffer += chunk
                while b"\n" in buffer:
                    line, _, buffer = buffer.partition(b"\n")
                    decoded_line = line.decode().strip()
                    await self._dispatch(decoded_line)

        except asyncio.CancelledError:
            await self.logger.log("Message handler cancelled")
            raise
        except Exception as e:
            await self.logger.log(f"Error in message handler: {e}")
            raise

    async def _dispatch(self, raw_line):
        try:
            msg = json.loads(raw_line)
            msg_type = msg.get("type")
            payload = msg.get("payload", {})

            if msg_type in self.handlers:
                await self.handlers[msg_type](payload)
            else:
                await self.logger.log(f"[TargetedContentBridge] No handler for type: {msg_type}")
        except Exception as e:
            await self.logger.log(f"[TargetedContentBridge] Dispatch error: {e}")

    async def send(self, message_type: str, payload=None):
        if not self.process.stdin:
            await self.logger.log("Cannot send message — stdin is not available.")
            return

        msg = {
            "type": message_type,
            "payload": payload or {}
        }
        try:
            self.process.stdin.write((json.dumps(msg) + "\n").encode())
            await self.process.stdin.drain()
        except Exception as e:
            await self.logger.log(f"[TargetedContentBridge] Failed to send: {e}")
