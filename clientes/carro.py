"""
Versión 1: un solo carro que avanza en línea recta y manda su posición cada segundo.
"""
import asyncio
import json

import websockets

URI = "ws://localhost:8765"  # servidor local (servidor.py)


async def carro():
    async with websockets.connect(URI) as websocket:
        lat = 29.07403
        lon = -110.98111

        while True:
            lat += 0.0001
            lon += 0.0001

            mensaje = json.dumps({"id": "carro_carla", "lat": lat, "lon": lon})
            await websocket.send(mensaje)
            print("Enviado:", mensaje)

            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(carro())
