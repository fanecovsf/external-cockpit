from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.schemas import CommandSchema, AutoPilotAltitudeSchema, TelemetryDataSchema

app = FastAPI()

command_schema = CommandSchema()
auto_pilot_schema = AutoPilotAltitudeSchema()
telemetry_schema = TelemetryDataSchema()

schemas = ['command', 'auto_pilot', 'telemetry']

connections = []

async def broadcast(message):
    disconnected = []

    for conn in connections:
        try:
            await conn.send_json(message)
        except:
            disconnected.append(conn)

    for conn in disconnected:
        connections.remove(conn)

@app.websocket("/ws/cockpit")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if 'schema' not in data:
                continue

            schema_name = data['schema']
            if schema_name not in schemas:
                continue

            if schema_name == 'command':
                try:
                    validated_data = command_schema.load(data)
                    await broadcast(validated_data)
                except Exception as e:
                    print("Validation Error:", e)

            elif schema_name == 'auto_pilot':
                try:
                    validated_data = auto_pilot_schema.load(data)
                    await broadcast(validated_data)
                except Exception as e:
                    print("Validation Error:", e)

            elif schema_name == 'telemetry':
                try:
                    validated_data = telemetry_schema.load(data)
                    await broadcast(validated_data)
                except Exception as e:
                    print("Validation Error:", e)

    except WebSocketDisconnect:
        connections.remove(websocket)
        