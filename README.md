# GPS Fleet Tracker — WebSocket + Leaflet

Rastreo en tiempo real de una flotilla de vehículos simulados sobre calles reales de Hermosillo. Cada carro es un cliente WebSocket que manda su posición; un servidor la reenvía al mapa web, que dibuja el marcador y la ruta recorrida de cada vehículo. Práctica de la Maestría en Ingeniería en IoT e Inteligencia Artificial (Universidad de Sonora).

![Demo](docs/demo.gif)

## Arquitectura

```
clientes/flotilla.py  ── 4 carros ──►  servidor.py (WebSocket :8765)  ──►  web/mapa.html (Leaflet)
        │                                     ▲
        └── OSRM: rutas por calles reales      └── reenvía cada posición a los demás clientes
```

| Archivo | Qué hace |
|---|---|
| `servidor.py` | Servidor WebSocket: recibe `{id, lat, lon}` y lo reenvía (broadcast) a los demás clientes |
| `clientes/carro.py` | v1: un carro en línea recta, una posición por segundo |
| `clientes/flotilla.py` | v2: 4 carros con rutas por calles reales (OSRM), ida y vuelta, cada 2 s |
| `web/mapa_un_carro.html` | v1 del mapa: un marcador que sigue al carro |
| `web/mapa.html` | v2 del mapa: un marcador, color y ruta por vehículo, más lista de coordenadas |

## Robustez

- **Reconexión automática:** si se cae el servidor, cada carro reintenta cada 3 s sin detener a los demás.
- **Mensajes incompletos:** el mapa ignora mensajes sin `id`, `lat` o `lon`.
- **Clientes caídos:** el servidor los descarta al fallar el envío, sin interrumpir el broadcast.
- **Límite del servicio de rutas:** la flotilla espera 1 s entre consultas a OSRM (máximo permitido por el servidor público).
- **Estado de conexión visible** en el mapa (conectado / desconectado).

## Cómo ejecutarlo

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt

python servidor.py              # 1. servidor
# 2. abre web/mapa.html en el navegador
python clientes/flotilla.py     # 3. la flotilla (o clientes/carro.py para un solo carro)
```

## Stack

Python · asyncio · websockets · JavaScript · Leaflet · OpenStreetMap / OSRM
