<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";

import {
  connectTelemetry,
  disconnectTelemetry,
} from "./services/telemetrySocket";

import {
  connectCommands,
  sendCommand,
  disconnectCommands,
} from "./services/commandSocket";

import {
  connectThrottleTelemetry,
  disconnectThrottleTelemetry,
} from "./services/throttleSocket";

import ArtificialHorizon from "./components/ArtificialHorizon.vue";
import AltitudeSelector from "./components/AltitudeSelector.vue";
import InstrumentDisplay from "./components/InstrumentDisplay.vue";
import ToggleSwitch from "./components/ToggleSwitch.vue";
import FuelBar from "./components/FuelBar.vue";
import PlaneDisplay from "./components/PlaneDisplay.vue";
import ThrottleLevers from "./components/ThrottleLevers.vue";

// ================= TELEMETRY =================

const lastTelemetryTime = ref(Date.now());
const TIMEOUT = 10000;

const telemetryAltitude = ref(0);
const telemetrySpeed = ref(0);
const telemetryPitch = ref(0);
const telemetryRoll = ref(0);

const displayAltitude = ref(0);
const displaySpeed = ref(0);

const planeName = ref(null);

// ================= COMMAND STATE =================

const apAltitude = ref(0);
const apActive = ref(false);

const atSpeed = ref(0);
const atActive = ref(false);

const takeOffState = ref("OFF");
const landingMode = ref(false);

// ================= FUEL =================

const maxFuel = 88000;
const fuel = ref(maxFuel / 2);
const fuelTransfer = ref(false);

// ================= THROTTLE =================

const throttleLeft = ref(0);
const throttleRight = ref(0);
const throttleLinked = ref(true);
const autoThrottleActive = ref(false);

// ================= RESET CONTROL =================

const isResetting = ref(false);

let animationFrame = null;

// ================= TELEMETRY =================

const handleTelemetry = (data) => {
  lastTelemetryTime.value = Date.now();

  if (data.schema === "plane") {
    planeName.value = data.plane_id;
    return;
  }

  if (data.schema === "telemetry") {
    if (data.altitude !== undefined) telemetryAltitude.value = data.altitude;
    if (data.speed !== undefined) telemetrySpeed.value = data.speed;
    if (data.fuel !== undefined) fuel.value = data.fuel;
    if (data.pitch !== undefined) telemetryPitch.value = data.pitch;
    if (data.roll !== undefined) telemetryRoll.value = data.roll;
  }
};

const handleThrottleTelemetry = (data) => {
  if (data.schema !== "telemetry") return;

  throttleLeft.value = data.engine1 ?? throttleLeft.value;
  throttleRight.value = data.engine2 ?? throttleRight.value;
};

const handleCommand = (data) => {
  if (data.schema !== "command") return;

  switch (data.command) {
    case "ap":
      apAltitude.value = data.altitude ?? apAltitude.value;
      apActive.value = data.status === "on";
      break;

    case "at":
      atSpeed.value = data.speed ?? atSpeed.value;
      atActive.value = data.status === "on";
      break;

    case "to":
      takeOffState.value =
        data.status === "arm" ? "ARMED" : data.status === "on" ? "ON" : "OFF";
      break;

    case "ld":
      landingMode.value = data.status === "on";
      break;

    case "ft":
      fuelTransfer.value = data.status === "on";
      break;
  }
};

// ================= LOOP =================

const loop = () => {
  const now = Date.now();

  if (now - lastTelemetryTime.value > TIMEOUT) {
    planeName.value = null;
    telemetryAltitude.value = 0;
    telemetrySpeed.value = 0;
    telemetryPitch.value = 0;
    telemetryRoll.value = 0;
    fuel.value = 0;
  }

  displayAltitude.value +=
    (telemetryAltitude.value - displayAltitude.value) * 0.08;

  displaySpeed.value += (telemetrySpeed.value - displaySpeed.value) * 0.1;

  animationFrame = requestAnimationFrame(loop);
};

// ================= RESET SYSTEM =================

const resetSystem = async () => {
  if (isResetting.value) return;

  isResetting.value = true;

  // 1. limpa UI imediatamente
  planeName.value = null;

  telemetryAltitude.value = 0;
  telemetrySpeed.value = 0;
  telemetryPitch.value = 0;
  telemetryRoll.value = 0;

  displayAltitude.value = 0;
  displaySpeed.value = 0;

  fuel.value = 0;

  apActive.value = false;
  atActive.value = false;
  landingMode.value = false;
  takeOffState.value = "OFF";

  // 2. fecha conexões
  disconnectTelemetry();
  disconnectThrottleTelemetry();
  disconnectCommands();

  // 3. espera 3s
  await new Promise((r) => setTimeout(r, 3000));

  // 4. reconecta tudo
  connectTelemetry(handleTelemetry);
  connectThrottleTelemetry(handleThrottleTelemetry);
  connectCommands(handleCommand);

  isResetting.value = false;
};

// ================= LIFECYCLE =================

onMounted(() => {
  connectTelemetry(handleTelemetry);
  connectThrottleTelemetry(handleThrottleTelemetry);
  connectCommands(handleCommand);

  animationFrame = requestAnimationFrame(loop);
});

onUnmounted(() => {
  disconnectTelemetry();
  disconnectThrottleTelemetry();
  disconnectCommands();

  cancelAnimationFrame(animationFrame);
});
</script>

<template>
  <div class="cockpit">
    <!-- RESET BUTTON -->
    <button class="reset-btn" @click="resetSystem" :disabled="isResetting">
      RESET
    </button>

    <PlaneDisplay :plane="planeName" />

    <div class="left-panel">
      <AltitudeSelector
        :value="apAltitude"
        :min="0"
        :max="300"
        label="ALT"
        buttonLabel="AP1"
        :isActive="apActive"
        :locked="apActive"
      />

      <AltitudeSelector
        :value="atSpeed"
        :min="0"
        :max="160"
        label="SPD"
        buttonLabel="A/THR"
        :isActive="atActive"
        :locked="atActive"
      />
    </div>

    <div class="instruments-wrapper">
      <InstrumentDisplay
        label="ALT"
        :value="displayAltitude"
        :max="300"
        :size="240"
        :minLimit="1"
        :maxLimit="120"
      />

      <InstrumentDisplay
        label="SPD"
        :value="displaySpeed"
        :max="160"
        :size="240"
        :minLimit="120"
        :maxLimit="160"
      />
    </div>

    <div class="horizon-wrapper">
      <ArtificialHorizon :pitch="telemetryPitch" :roll="telemetryRoll" />
    </div>

    <div class="right-panel">
      <ThrottleLevers
        v-model:leftValue="throttleLeft"
        v-model:rightValue="throttleRight"
        v-model:linked="throttleLinked"
        :autothrottleActive="autoThrottleActive"
      />
    </div>

    <div class="modes-bar">
      <div class="takeoff-group">
        <ToggleSwitch
          label="TAKE OFF ARM"
          :modelValue="takeOffState !== 'OFF'"
          :locked="takeOffState === 'ON'"
        />

        <button class="start-btn" :disabled="takeOffState !== 'ARMED'">
          START
        </button>
      </div>

      <ToggleSwitch
        label="LANDING MODE"
        :modelValue="landingMode"
        :locked="false"
      />
    </div>

    <FuelBar :fuel="fuel" :maxFuel="maxFuel" :transferActive="fuelTransfer" />
  </div>
</template>

<style scoped>
.cockpit {
  height: 100vh;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  background: radial-gradient(circle at center, #3a3a3a, #1c1c1c);
  font-family: "Courier New", monospace;
  position: relative;
}

.left-panel {
  margin-left: 40px;
  display: flex;
  align-items: center;
  gap: 20px;
}

/* ===== INSTRUMENTS WRAPPER ===== */
.instruments-wrapper {
  position: absolute;
  left: 50%;
  top: 10%;
  transform: translateX(-50%);
  display: flex;
  gap: 400px;
}

/* ===== MODES BAR ===== */
.modes-bar {
  position: absolute;
  bottom: 110px;
  left: 50%;
  transform: translateX(-50%);
  width: 70%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* grupo takeoff */
.takeoff-group {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* ===== START BUTTON ===== */
.start-btn {
  padding: 14px 18px;
  background: linear-gradient(145deg, #2a2a2a, #111);
  border: 2px solid #444;
  color: #777;
  font-weight: bold;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.1s ease;
  box-shadow:
    0 4px 0 #000,
    0 6px 10px rgba(0, 0, 0, 0.8),
    inset 0 0 5px rgba(255, 255, 255, 0.05);
}

/* habilitado */
.start-btn:not(:disabled) {
  color: #00ff9c;
  border-color: #00ff9c;
  box-shadow:
    0 4px 0 #003a2a,
    0 6px 12px rgba(0, 255, 156, 0.3),
    inset 0 0 8px #00ff9c33;
}

/* pressionado */
.start-btn:active:not(:disabled) {
  transform: translateY(4px);
  box-shadow:
    0 1px 0 #000,
    inset 0 0 10px #00ff9c55;
}

/* desabilitado */
.start-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #ff4444;
  color: #ff4444;
  box-shadow:
    0 2px 0 #300,
    inset 0 0 6px #ff444444;
}

/* ===== TEST BUTTONS ===== */
.test-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 10px 15px;
  background: linear-gradient(145deg, #3a3a3a, #1f1f1f);
  border: 1px solid #555;
  color: #00ff9c;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0, 255, 156, 0.2);
  transition: all 0.2s ease;
}

.test-btn:hover {
  box-shadow: 0 0 15px rgba(0, 255, 156, 0.5);
}

.test-btn:active {
  transform: translateY(2px);
}

.zero-btn {
  position: absolute;
  top: 70px;
  right: 20px;
  padding: 10px 15px;
  background: linear-gradient(145deg, #3a3a3a, #1f1f1f);
  border: 1px solid #555;
  color: #00ff9c;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0, 255, 156, 0.2);
  transition: all 0.2s ease;
}

.zero-btn:hover {
  box-shadow: 0 0 15px rgba(0, 255, 156, 0.5);
}

.zero-btn:active {
  transform: translateY(2px);
}

/* ===== HORIZON POSITION ===== */
.horizon-wrapper {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.right-panel {
  position: absolute;
  right: 40px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
}

/* ===== RESET BUTTON ===== */
.reset-btn {
  position: absolute;
  top: 15px;
  left: 15px;

  padding: 8px 12px;
  font-weight: bold;

  background: linear-gradient(145deg, #2a2a2a, #111);
  border: 1px solid #666;
  color: #ff5555;

  border-radius: 6px;
  cursor: pointer;

  box-shadow: 0 0 10px rgba(255, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.reset-btn:hover {
  box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
}

.reset-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
