from fastapi import FastAPI, WebSocket
from backend.schemas import CommandSchema, AutoPilotAltitudeSchema, TelemetryDataSchema

app = FastAPI()

command_schema = CommandSchema()
auto_pilot_schema = AutoPilotAltitudeSchema()
telemetry_schema = TelemetryDataSchema()

schemas = ['command', 'auto_pilot', 'telemetry']

@app.websocket("/ws/cockpit")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
        except Exception as e:
            print("Error receiving data:", e)
            continue
        
        if 'schema' not in data:
            continue

        schema_name = data['schema']
        if schema_name not in schemas:
            continue

        if schema_name == 'command':
            try:
                validated_data = command_schema.load(data)
                print("Received Command:", validated_data)
            except Exception as e:
                print("Validation Error:", e)

        elif schema_name == 'auto_pilot':
            try:
                validated_data = auto_pilot_schema.load(data)
                print("Received AutoPilot Altitude:", validated_data)
            except Exception as e:
                print("Validation Error:", e)

        elif schema_name == 'telemetry':
            try:
                validated_data = telemetry_schema.load(data)
                print("Received Telemetry Data:", validated_data)
            except Exception as e:
                print("Validation Error:", e)
        
        