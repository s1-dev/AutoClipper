import asyncio

from metrics.generalLogger import GeneralLogger

class CommandServer:
    def __init__(self, commandQueue: asyncio.Queue, logger: GeneralLogger, host='127.0.0.1', port=8765):
        self.commandQueue = commandQueue
        self.logger = logger
        self.host = host
        self.port = port
        self.server = None
        self.activeConnection = None

    async def start(self):
        self.server = await asyncio.start_server(self._handle_client, self.host, self.port)
        if self.logger:
            await self.logger.log(f"Command server running on {self.host}:{self.port}")
        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        if self.logger:
            await self.logger.log("Shutting down CommandServer.")

        if self.server:
            self.server.close()
            await self.server.wait_closed()

        if self.activeConnection:
            try:
                self.activeConnection.write(b"Server shutting down.\n")
                await self.activeConnection.drain()
            except Exception:
                pass  # Ignore write errors
            self.activeConnection.close()
            try:
                await self.activeConnection.wait_closed()
            except Exception:
                pass

        self.server = None
        self.activeConnection = None

        if self.logger:
            await self.logger.log("CommandServer has shut down.")

    async def _handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')

        if self.activeConnection:
            writer.write(b"Another client is already connected.\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        self.activeConnection = writer
        if self.logger:
            await self.logger.log(f"Client connected: {addr}")

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                command = data.decode().strip()

                if self.logger:
                    await self.logger.log(f"Received server command: {command}")

                await self.commandQueue.put(command)
                writer.write(b"ACK\n")
                await writer.drain()

        except Exception as e:
            await self.logger.log(f"Error: {e}")
        finally:
            self.activeConnection = None
            writer.close()
            await writer.wait_closed()
            await self.logger.log(f"Client disconnected: {addr}")
    
    async def sendToClient(self, message: str):
        if self.activeConnection:
            try:
                self.activeConnection.write((message + '\n').encode())
                await self.activeConnection.drain()
            except Exception as e:
                if self.logger:
                    await self.logger.log(f"[CommandServer] Failed to send to client: {e}")
        else:
            if self.logger:
                await self.logger.log("[CommandServer] No active connection to send message to.")

# async def main():
#     server = CommandServer()
#     await server.start()

# if __name__ == "__main__":
#     asyncio.run(main())
