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

telemetry_connections = set()
throttle_telemetry_connections = set()
throttle_command_connections = set()
command_connections = set()

import asyncio

async def broadcast(message: str, pool: set):
    tasks = [conn.send_text(message) for conn in pool]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for conn, result in zip(list(pool), results):
        if isinstance(result, Exception):
            pool.remove(conn)

@app.websocket("/ws/commands", name="commands")
async def commands_websocket(websocket: WebSocket):
    '''
    This websocket is used to receive commands from the frontend and broadcast them to all connected clients. The expected command format is as follows:
    Available commands:
    - Autopilot: { command: "ap", status: "on"/"off", altitude: number }
    - Autothrottle: { command: "at", status: "on"/"off", speed: number }
    - Takeoff: { command: "to", status: "arm"/"on"/"off" }
    - Landing: { command: "ld", status: "on"/"off" }
    - Fuel Transfer: { command: "ft", status: "on"/"off" }
    '''
    await websocket.accept()
    command_connections.add(websocket)

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

            if data.get("schema") != "command":
                continue

            await broadcast(raw, command_connections)

    except WebSocketDisconnect as e:
        print("Disconnect:", e)
    finally:
        command_connections.discard(websocket)

@app.websocket("/ws/telemetry", name="telemetry")
async def websocket_endpoint(websocket: WebSocket):
    '''
    This websocket is used to receive telemetry from the plane and broadcast it to frontend. The expected telemetry format is as follows:
    {
        schema: "telemetry",
        altitude: number,
        speed: number,
        fuel: number,
        pitch: number,
        roll: number
    }
    '''
    await websocket.accept()
    telemetry_connections.add(websocket)

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

            await broadcast(raw, telemetry_connections)

    except WebSocketDisconnect as e:
        print("Disconnect:", e)
    finally:
        telemetry_connections.discard(websocket)

@app.websocket("/ws/throttle-telemetry", name="throttle-telemetry")
async def throttle_websocket(websocket: WebSocket):
    '''
    This websocket is used to receive throttle telemetry from the plane and broadcast it to frontend. The expected telemetry format is as follows:
    {
        schema: "telemetry",
        engine1: number (0-15),
        engine2: number (0-15)
    }
    '''
    await websocket.accept()
    throttle_telemetry_connections.add(websocket)

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

            if data.get("schema") != "telemetry":
                continue

            await broadcast(raw, throttle_telemetry_connections)

    except WebSocketDisconnect as e:
        print("Disconnect:", e)
    finally:
        throttle_telemetry_connections.discard(websocket)

@app.websocket("/ws/throttle-commands")
async def throttle_commands_websocket(websocket: WebSocket):
    '''
    This websocket is used to receive throttle commands from the frontend and broadcast them to all connected clients. The expected command format is as follows:
    {
        schema: "command",
        engine1: number (0-15),
        engine2: number (0-15)
    }
    '''
    await websocket.accept()
    throttle_command_connections.add(websocket)

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

            if data.get("schema") != "command":
                continue

            await broadcast(raw, throttle_command_connections)

    except WebSocketDisconnect as e:
        print("Disconnect:", e)
    finally:
        throttle_command_connections.discard(websocket)

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
        