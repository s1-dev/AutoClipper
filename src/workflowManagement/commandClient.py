import asyncio
import sys

async def handle_input(writer: asyncio.StreamWriter):
    loop = asyncio.get_event_loop()

    while True:
        try:
            # Run input() in a thread so it doesn't block the event loop
            cmd = await loop.run_in_executor(None, input, "Enter command (or 'exit' to quit): ")
            if cmd.lower() == 'exit':
                print("[Client] Closing connection.")
                writer.close()
                await writer.wait_closed()
                break

            writer.write((cmd + '\n').encode())
            await writer.drain()
        except (EOFError, KeyboardInterrupt):
            print("\n[Client] Exiting.")
            writer.close()
            await writer.wait_closed()
            break


async def handle_server(reader: asyncio.StreamReader):
    try:
        while True:
            response = await reader.readline()
            if not response:
                print("[Client] Server disconnected.")
                break
            print(f"\n[Client] Server response: {response.decode().strip()}")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"[Client] Error reading from server: {e}")


async def persistentClient(host='127.0.0.1', port=8765):
    try:
        reader, writer = await asyncio.open_connection(host, port)
        print(f"[Client] Connected to server at {host}:{port}")

        # Run input and server handler concurrently
        input_task = asyncio.create_task(handle_input(writer))
        server_task = asyncio.create_task(handle_server(reader))

        done, pending = await asyncio.wait(
            [input_task, server_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel the remaining task
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except ConnectionRefusedError:
        print("[Client] Could not connect to server.")
    except Exception as e:
        print(f"[Client] Error: {e}")


if __name__ == "__main__":
    asyncio.run(persistentClient())
