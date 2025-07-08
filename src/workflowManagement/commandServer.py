import asyncio
from metrics.generalLogger import GeneralLogger

class CommandServer:
    def __init__(self, commandQueue: asyncio.Queue, logger: GeneralLogger, host='127.0.0.1', port=8765):
        self.commandQueue = commandQueue
        self.logger = logger
        self.host = host
        self.port = port
        self.server = None
        self.shutting_down = False
        self.writerConnection = None 
        self.active_connections = set() 

    async def start(self):
        self.server = await asyncio.start_server(self._handle_new_client, self.host, self.port)
        if self.logger:
            await self.logger.log(f"Command server running on {self.host}:{self.port}")
        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        if self.logger:
            await self.logger.log("Shutting down CommandServer.")

        self.shutting_down = True

        if self.server:
            self.server.close()
            await self.server.wait_closed()

        for reader, writer, task in list(self.active_connections):
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=2.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
                except Exception as e:
                    await self.logger.log(f"Error cancelling client task: {e}")

        self.active_connections.clear()
        self.writerConnection = None

        if self.logger:
            await self.logger.log("CommandServer has shut down.")

    async def _handle_new_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        task = asyncio.create_task(self._handle_client(reader, writer))
        self.active_connections.add((reader, writer, task))

        def cleanup(_):
            self.active_connections.discard((reader, writer, task))

        task.add_done_callback(cleanup)
        await task  # Important to ensure shutdown can cancel this

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')

        if self.writerConnection:
            writer.write(b"Another client is already connected with write privileges.\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        self.writerConnection = writer
        if self.logger:
            await self.logger.log(f"Client connected: {addr}")

        try:
            while not self.shutting_down:
                try:
                    data = await asyncio.wait_for(reader.readline(), timeout=1)
                except asyncio.TimeoutError:
                    continue

                if not data:
                    break
                command = data.decode().strip()

                if self.logger:
                    await self.logger.log(f"Received server command: {command}")

                await self.commandQueue.put(command)
                writer.write(b"ACK\n")
                await writer.drain()

        except asyncio.CancelledError:
            await self.logger.log("Client handler task was cancelled.")
        except Exception as e:
            await self.logger.log(f"Client handler error: {e}")
        finally:
            self.writerConnection = None
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
            await self.logger.log(f"Client disconnected: {addr}")

    async def sendToClient(self, message: str):
        if self.writerConnection:
            try:
                self.writerConnection.write((message + '\n').encode())
                await self.writerConnection.drain()
            except Exception as e:
                if self.logger:
                    await self.logger.log(f"[CommandServer] Failed to send to client: {e}")
        else:
            if self.logger:
                await self.logger.log("[CommandServer] No active connection to send message to.")
