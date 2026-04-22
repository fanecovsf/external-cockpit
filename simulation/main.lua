local http_websocket = require("http.websocket")
local json = require("cjson")
local socket = require("socket")

-- =========================
-- CONFIG
-- =========================
local WS_URL = "ws://localhost:8000/ws/telemetry"
local THROTTLE_WS_URL = "ws://localhost:8000/ws/throttle-telemetry"

local LOOP_INTERVAL = 0.1 -- 10Hz
local HEARTBEAT_INTERVAL = 5 -- segundos
local THROTTLE_SEND_INTERVAL = 3 -- 🔥 envia throttle a cada 3s

-- =========================
-- CONNECTION
-- =========================
local function connect()
  local ws, err = http_websocket.new_from_uri(WS_URL)
  if not ws then return nil, err end

  local ok, conn_err = ws:connect()
  if not ok then return nil, conn_err end

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

    local ws = connect()
    if ws then
      print("Reconectado!")
      ws:send(json.encode({schema = "plane", plane_id = "IC-777x"}))
      return ws
    end
  end
end

local ws = connect()
if not ws then
  ws = reconnect()
else
  print("Conectado ao WebSocket")
end

-- =========================
-- THROTTLE CONNECTION
-- =========================
local function connectThrottle()
  local ws, err = http_websocket.new_from_uri(THROTTLE_WS_URL)
  if not ws then return nil, err end

  local ok, conn_err = ws:connect()
  if not ok then return nil, conn_err end

  return ws
end

local function reconnectThrottle()
  while true do
    print("Reconectando throttle...")
    socket.sleep(2)

    local ws = connectThrottle()
    if ws then
      print("Throttle conectado!")
      return ws
    end
  end
end

local throttleWs = connectThrottle()
if not throttleWs then
  throttleWs = reconnectThrottle()
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

local function stepTowards(current, target)
  if current < target then
    return current + 1
  elseif current > target then
    return current - 1
  end
  return current
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
-- THROTTLE STATE
-- =========================
local throttle1 = 0
local throttle2 = 0

local targetThrottle1 = 0
local targetThrottle2 = 0

local lastThrottleSend = socket.gettime()

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
  -- =====================
  -- THROTTLE SIMULATION
  -- =====================
  if math.random() < 0.05 then
    targetThrottle1 = math.random(0, 15)
    targetThrottle2 = math.random(0, 15)
  end

  -- 70% chance de manter sincronizado
  if math.random() < 0.7 then
    targetThrottle2 = targetThrottle1
  end

  throttle1 = stepTowards(throttle1, targetThrottle1)
  throttle2 = stepTowards(throttle2, targetThrottle2)

  -- 🔥 ENVIO CONTROLADO (a cada 3s)
  local now = socket.gettime()
  if now - lastThrottleSend >= THROTTLE_SEND_INTERVAL then
    local throttlePayload = {
      schema = "telemetry",
      engine1 = throttle1,
      engine2 = throttle2
    }

    local throttleMessage = json.encode(throttlePayload)

    if not throttleWs then
      throttleWs = reconnectThrottle()
    end

    local ok, err = throttleWs:send(throttleMessage)

    if not ok then
      print("Erro throttle:", err)
      throttleWs = reconnectThrottle()
    else
      print("Throttle enviado:", throttle1, throttle2)
    end

    lastThrottleSend = now
  end

  -- =====================
  -- TELEMETRY NORMAL
  -- =====================
  if math.random() < 0.1 then
    targetAltitude = randomRange(0, 300)
    targetSpeed = randomRange(0, 160)

    targetPitch = (targetAltitude - altitude) * 0.01
    targetRoll = randomRange(-0.5, 0.5)
  end

  altitude = lerp(altitude, targetAltitude, 0.08)
  speed = lerp(speed, targetSpeed, 0.1)
  pitch = lerp(pitch, targetPitch, 0.08)
  roll = lerp(roll, targetRoll, 0.08)

  fuel = fuel - (speed * 0.05)
  if fuel < 0 then fuel = 0 end

  payload.altitude = math.floor(altitude)
  payload.speed = round(speed, 1)
  payload.fuel = round(fuel, 2)
  payload.pitch = round(pitch, 2)
  payload.roll = round(roll, 2)

  local message = json.encode(payload)

  if not ws then
    ws = reconnect()
  end

  local ok, send_err = ws:send(message)

  if not ok then
    print("Erro ao enviar:", send_err)
    ws = reconnect()
  else
    while true do
      local msg = ws:receive(0)
      if not msg then break end
    end
  end

  -- =====================
  -- HEARTBEAT
  -- =====================
  if now - lastHeartbeat > HEARTBEAT_INTERVAL then
    ws:send('{"type":"ping"}')
    lastHeartbeat = now
  end

  socket.sleep(LOOP_INTERVAL)
end