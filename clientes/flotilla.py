"""
Versión 2: flotilla de 4 carros que recorren rutas sobre calles reales de Hermosillo (OSRM / OpenStreetMap),
ida y vuelta, mandando su posición cada 2 segundos. Cada carro reintenta si se cae la conexión.
"""
import asyncio
import json
import math
import urllib.request

import websockets

# ── Configuración ──────────────────────────────────────────────
URI = "ws://127.0.0.1:8765"      # servidor local (servidor.py)
INTERVALO = 2                    # segundos entre envíos (requisito de la tarea)
PASO_METROS = 30                 # distancia que avanza cada carro por envío (~54 km/h)

# Servicio público de rutas sobre calles reales (OpenStreetMap)
OSRM = ("https://router.project-osrm.org/route/v1/driving/"
        "{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson")

# Cada carro: (origen, destino) en (lat, lon), dentro de Hermosillo.
# No tienen que caer exacto en una calle: OSRM los "pega" a la calle más cercana.
CARROS = {
    "carro_carla":  ((29.0729, -110.9559), (29.0980, -110.9480)),
    "carro_luis":   ((29.0800, -110.9664), (29.0600, -110.9900)),
    "carro_maria":  ((29.0662, -110.9476), (29.0900, -110.9700)),
    "carro_daniel": ((29.0790, -110.9384), (29.0550, -110.9600)),
}


def obtener_ruta(origen, destino):
    """Pide a OSRM la ruta por calles entre dos puntos. Regresa lista de (lat, lon)."""
    url = OSRM.format(lat1=origen[0], lon1=origen[1], lat2=destino[0], lon2=destino[1])
    req = urllib.request.Request(url, headers={"User-Agent": "tarea-iot-unison"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        datos = json.load(resp)
    if datos.get("code") != "Ok":
        raise RuntimeError(f"OSRM respondió: {datos.get('code')}")
    # OSRM entrega [lon, lat]; Leaflet usa [lat, lon]
    return [(lat, lon) for lon, lat in datos["routes"][0]["geometry"]["coordinates"]]


def distancia_m(a, b):
    """Distancia aproximada en metros entre dos puntos cercanos."""
    dlat = (b[0] - a[0]) * 111_320
    dlon = (b[1] - a[1]) * 111_320 * math.cos(math.radians(a[0]))
    return math.hypot(dlat, dlon)


def interpolar(puntos, paso):
    """Rellena la ruta con puntos cada `paso` metros, para que el carro avance parejo."""
    resultado = [puntos[0]]
    for a, b in zip(puntos, puntos[1:]):
        n = max(1, int(distancia_m(a, b) // paso))
        for i in range(1, n + 1):
            t = i / n
            resultado.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return resultado


async def carro(nombre, ruta, retraso):
    """Cliente WebSocket que recorre su ruta de ida y vuelta. Reintenta si se cae la conexión."""
    await asyncio.sleep(retraso)
    recorrido = ruta + ruta[::-1]        # ida y vuelta
    i = 0

    while True:
        try:
            async with websockets.connect(URI, open_timeout=20) as websocket:
                print(f"{nombre} conectado ({len(ruta)} puntos de ruta)")
                while True:
                    lat, lon = recorrido[i % len(recorrido)]
                    datos = {"id": nombre, "lat": lat, "lon": lon}
                    await websocket.send(json.dumps(datos))
                    print("Enviado:", datos)
                    i += 1
                    await asyncio.sleep(INTERVALO)

        except (OSError, asyncio.TimeoutError, websockets.ConnectionClosed) as e:
            print(f"⚠️ {nombre}: problema de conexión ({type(e).__name__}). Reintentando en 3 s...")
            await asyncio.sleep(3)


async def main():
    rutas = {}
    for nombre, (origen, destino) in CARROS.items():
        print(f"Calculando ruta por calles para {nombre}...")
        rutas[nombre] = interpolar(obtener_ruta(origen, destino), PASO_METROS)
        await asyncio.sleep(1)           # el servidor público pide máx. 1 consulta por segundo

    await asyncio.gather(*(
        carro(nombre, ruta, i * 0.5)
        for i, (nombre, ruta) in enumerate(rutas.items())
    ))


if __name__ == "__main__":
    asyncio.run(main())