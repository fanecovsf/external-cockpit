from marshmallow import Schema, fields

class CommandSchema(Schema):
    schema = fields.Str(required=True)
    command = fields.Str(required=True, validate=lambda x: x in ["AP", "TO", "LD", "FT"])
    status = fields.Str(required=True, validate=lambda x: x in ["ON", "OFF"])

class AutoPilotAltitudeSchema(Schema):
    schema = fields.Str(required=True)
    altitude = fields.Integer(required=True, validate=lambda x: 140 <= x <= 240)

class TelemetryDataSchema(Schema):
    schema = fields.Str(required=True)
    altitude = fields.Integer(required=True)
    speed = fields.Float(required=True)
    pitch = fields.Float(required=True)
    roll = fields.Float(required=True)
