"""
Servidor WebSocket de rastreo GPS.
Recibe posiciones de los carros (clientes) y las reenvía a todos los demás clientes conectados (el mapa).
"""
import asyncio

import websockets

HOST = "0.0.0.0"
PUERTO = 8765

clientes = set()


async def servidor(websocket):
    clientes.add(websocket)
    print("Cliente conectado")

    try:
        async for mensaje in websocket:
            print("GPS:", mensaje)

            # Reenviar la posición a los demás clientes
            for cliente in clientes.copy():
                if cliente != websocket:
                    try:
                        await cliente.send(mensaje)
                    except websockets.ConnectionClosed:
                        clientes.discard(cliente)
    finally:
        clientes.discard(websocket)


async def main():
    async with websockets.serve(servidor, HOST, PUERTO):
        print("Servidor WebSocket iniciado")
        print(f"Puerto: {PUERTO}")
        await asyncio.Future()  # corre indefinidamente


if __name__ == "__main__":
    asyncio.run(main())
