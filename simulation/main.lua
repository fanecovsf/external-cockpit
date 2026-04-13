local http_websocket = require("http.websocket")
local json = require("cjson")
local socket = require("socket")

local function connect()
  local ws, err = http_websocket.new_from_uri("ws://localhost:8000/ws/cockpit")

  if not ws then
    return nil, err
  end

  local ok, conn_err = ws:connect()
  if not ok then
    return nil, conn_err
  end

  return ws
end

local ws, err = connect()

if not ws then
  print("Erro ao conectar:", err)
  return
end

print("Conectado ao WebSocket")

-- =========================
-- ESTADO
-- =========================
local altitude = 0
local speed = 0
local fuel = 88000

local targetAltitude = 0
local targetSpeed = 0

-- =========================
-- HELPERS
-- =========================
local function lerp(current, target, factor)
  return current + (target - current) * factor
end

local function randomRange(min, max)
  return min + math.random() * (max - min)
end

math.randomseed(os.time())

-- =========================
-- LOOP PRINCIPAL
-- =========================
while true do
  -- muda comportamento aleatório
  if math.random() < 0.1 then
    targetAltitude = randomRange(0, 300)
    targetSpeed = randomRange(0, 200)
  end

  -- suavização
  altitude = lerp(altitude, targetAltitude, 0.08)
  speed = lerp(speed, targetSpeed, 0.1)

  -- consumo combustível
  fuel = fuel - (speed * 0.05)
  if fuel < 0 then fuel = 0 end

  -- payload
  local payload = {
    schema = "telemetry",
    altitude = math.floor(altitude),
    speed = tonumber(string.format("%.1f", speed)),
    fuel = tonumber(string.format("%.2f", fuel))
  }

  local message = json.encode(payload)

  -- envio
  local ok, send_err = ws:send(message)

  if not ok then
    print("Erro ao enviar:", send_err)

    -- 🔁 reconectar automaticamente
    print("Tentando reconectar...")
    ws, err = connect()

    if not ws then
      print("Falha ao reconectar:", err)
      socket.sleep(2)
    else
      print("Reconectado!")
    end
  else
    print("Enviado:", message)
  end

  socket.sleep(0.5)
end