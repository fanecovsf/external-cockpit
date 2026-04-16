local http_websocket = require("http.websocket")
local json = require("cjson")
local socket = require("socket")

-- =========================
-- CONFIG
-- =========================
local WS_URL = "ws://localhost:8000/ws/telemetry"
local LOOP_INTERVAL = 0.1 -- 10Hz
local HEARTBEAT_INTERVAL = 5 -- segundos

-- =========================
-- CONNECTION
-- =========================
local function connect()
  local ws, err = http_websocket.new_from_uri(WS_URL)

  if not ws then
    return nil, err
  end

  local ok, conn_err = ws:connect()
  if not ok then
    return nil, conn_err
  end

  ws:send(json.encode({schema = "plane", plane_id = "IC-777x"}))

  return ws
end

local function reconnect()
  local retry = 0

  while true do
    retry = retry + 1
    local delay = math.min(2 ^ retry, 10)

    print("Reconectando em", delay, "segundos...")
    socket.sleep(delay)

    local ws, err = connect()

    if ws then
      print("Reconectado!")
      ws:send(json.encode({schema = "plane", plane_id = "IC-777x"}))
      return ws
    end
  end
end

local ws, err = connect()

if not ws then
  print("Erro ao conectar:", err)
  ws = reconnect()
else
  print("Conectado ao WebSocket")
end

-- =========================
-- HELPERS
-- =========================
local function lerp(current, target, factor)
  return current + (target - current) * factor
end

local function randomRange(min, max)
  return min + math.random() * (max - min)
end

local function round(value, decimals)
  local mult = 10 ^ decimals
  return math.floor(value * mult + 0.5) / mult
end

math.randomseed(os.time())

-- =========================
-- ESTADO
-- =========================
local altitude = 0
local speed = 0
local fuel = 88000

local targetAltitude = 0
local targetSpeed = 0

local pitch = 0
local roll = 0

local targetPitch = 0
local targetRoll = 0

-- =========================
-- PAYLOAD REUTILIZÁVEL
-- =========================
local payload = {
  schema = "telemetry",
  altitude = 0,
  speed = 0,
  fuel = 0,
  pitch = 0,
  roll = 0
}

-- =========================
-- HEARTBEAT
-- =========================
local lastHeartbeat = socket.gettime()

-- =========================
-- LOOP PRINCIPAL
-- =========================
while true do
  -- comortamento aleatório
  if math.random() < 0.1 then
    targetAltitude = randomRange(0, 300)
    targetSpeed = randomRange(0, 200)

    targetPitch = (targetAltitude - altitude) * 0.01
    targetRoll = randomRange(-0.5, 0.5)
  end

  -- suavização
  altitude = lerp(altitude, targetAltitude, 0.08)
  speed = lerp(speed, targetSpeed, 0.1)
  pitch = lerp(pitch, targetPitch, 0.08)
  roll = lerp(roll, targetRoll, 0.08)

  -- consumo combustível
  fuel = fuel - (speed * 0.05)
  if fuel < 0 then fuel = 0 end

  -- atualiza payload (sem recriar tabela)
  payload.altitude = math.floor(altitude)
  payload.speed = round(speed, 1)
  payload.fuel = round(fuel, 2)
  payload.pitch = round(pitch, 2)
  payload.roll = round(roll, 2)

  -- encode JSON
  local message = json.encode(payload)

  -- garante conexão
  if not ws then
    ws = reconnect()
  end

  -- envio protegido
  local ok, send_err = ws:send(message)

  if not ok then
  print("Erro ao enviar:", send_err)
  ws = reconnect()
  else
    while true do
      local msg, opcode, err = ws:receive(0)
      if not msg then break end
    end
  end

  -- heartbeat (mantém conexão viva)
  local now = socket.gettime()
  if now - lastHeartbeat > HEARTBEAT_INTERVAL then
    ws:send('{"type":"ping"}')
    lastHeartbeat = now
  end

  socket.sleep(LOOP_INTERVAL)
end