from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.schemas import CommandSchema, AutoPilotAltitudeSchema, TelemetryDataSchema
import orjson
import uvloop
import asyncio
from .utils.parse_world import parse_world
from fastapi.middleware.cors import CORSMiddleware

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
WORLD_CACHE = None

command_schema = CommandSchema()
auto_pilot_schema = AutoPilotAltitudeSchema()
telemetry_schema = TelemetryDataSchema()

schemas = ['command', 'auto_pilot', 'telemetry', 'plane']

connections = set()

import asyncio

async def broadcast(message: str):
    tasks = [conn.send_text(message) for conn in connections]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for conn, result in zip(list(connections), results):
        if isinstance(result, Exception):
            connections.remove(conn)

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)

    try:
        while True:
            try:
                raw = await websocket.receive_text()
            except Exception as e:
                print("Erro receive:", type(e), repr(e))
                break

            try:
                data = orjson.loads(raw)
            except Exception as e:
                print("Erro JSON:", repr(e))
                continue

            if data.get("schema") != "telemetry" and data.get("schema") != "plane":
                continue

            await broadcast(raw)

    except WebSocketDisconnect as e:
        print("Disconnect:", e)
    finally:
        connections.discard(websocket)

@app.post("/map/load")
def load_map(payload: dict):
    global WORLD_CACHE

    path = payload["path"]
    WORLD_CACHE = parse_world(path)

    return {
        "chunks": len(WORLD_CACHE)
    }


@app.get("/map")
def get_map():
    return WORLD_CACHE or []
        