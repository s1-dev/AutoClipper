# persistent_command_client.py

import asyncio

async def persistentClient(host='127.0.0.1', port=8765):
    try:
        reader, writer = await asyncio.open_connection(host, port)
        print(f"[Client] Connected to server at {host}:{port}")

        while True:
            cmd = input("Enter command (or 'exit' to quit): ")
            if cmd.lower() == 'exit':
                print("[Client] Closing connection.")
                break

            writer.write((cmd + '\n').encode())
            await writer.drain()

            response = await reader.readline()
            if not response:
                print("[Client] Server disconnected.")
                break

            print(f"[Client] Server response: {response.decode().strip()}")

        writer.close()
        await writer.wait_closed()

    except ConnectionRefusedError:
        print("[Client] Could not connect to server.")
    except Exception as e:
        print(f"[Client] Error: {e}")

if __name__ == "__main__":
    asyncio.run(persistentClient())
