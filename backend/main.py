from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.schemas import CommandSchema, AutoPilotAltitudeSchema, TelemetryDataSchema
import orjson
import uvloop
import asyncio

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI()

command_schema = CommandSchema()
auto_pilot_schema = AutoPilotAltitudeSchema()
telemetry_schema = TelemetryDataSchema()

schemas = ['command', 'auto_pilot', 'telemetry']

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

            if data.get("schema") != "telemetry":
                continue

            await broadcast(raw)

    except WebSocketDisconnect as e:
        print("Disconnect:", e)
    finally:
        connections.discard(websocket)
        