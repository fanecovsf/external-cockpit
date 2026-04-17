<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { watch } from "vue";
import {
  connectTelemetry,
  disconnectTelemetry,
} from "./services/telemetrySocket";
import ArtificialHorizon from "./components/ArtificialHorizon.vue";
import AltitudeSelector from "./components/AltitudeSelector.vue";
import InstrumentDisplay from "./components/InstrumentDisplay.vue";
import ToggleSwitch from "./components/ToggleSwitch.vue";
import FuelBar from "./components/FuelBar.vue";
import PlaneDisplay from "./components/PlaneDisplay.vue";
import ThrottleLevers from "./components/ThrottleLevers.vue";

// ================= TELEMETRY STATE =================

const lastTelemetryTime = ref(Date.now());
const TIMEOUT = 10000; // 10 segundos

const telemetryAltitude = ref(0);
const telemetrySpeed = ref(0);
const telemetryPitch = ref(0);
const telemetryRoll = ref(0);

// valores exibidos (suavizados)
const displayAltitude = ref(0);
const displaySpeed = ref(0);

const planeName = ref(null);

// ================= UTILS ================
const randomizeTelemetry = () => {
  telemetryAltitude.value = Math.random() * 300;
  telemetrySpeed.value = Math.random() * 200;
};

const zeroTelemetry = () => {
  telemetryAltitude.value = 0;
  telemetrySpeed.value = 0;
};

// ================= FUEL =================

const maxFuel = 88000;
const fuel = ref(maxFuel / 2);

const fuelTransfer = ref(false);

const toggleFuelTransfer = () => {
  fuelTransfer.value = !fuelTransfer.value;
};

// ================= HANDLE TELEMETRY =================

const handleTelemetry = (data) => {
  lastTelemetryTime.value = Date.now();

  if (data.schema === "plane") {
    planeName.value = data.plane_id;
    return;
  }

  if (data.schema === "telemetry") {
    if (data.altitude !== undefined) {
      telemetryAltitude.value = data.altitude;
    }

    if (data.speed !== undefined) {
      telemetrySpeed.value = data.speed;
    }

    if (data.fuel !== undefined) {
      fuel.value = data.fuel;
    }

    if (data.pitch !== undefined) {
      telemetryPitch.value = data.pitch;
    }

    if (data.roll !== undefined) {
      telemetryRoll.value = data.roll;
    }
  }
};

// ================= MAIN LOOP (HIGH PERFORMANCE) =================

let animationFrame = null;

const loop = () => {
  const now = Date.now();

  // 🚨 TIMEOUT
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

// ================= LIFECYCLE =================

onMounted(() => {
  connectTelemetry(handleTelemetry);
  animationFrame = requestAnimationFrame(loop);
});

onUnmounted(() => {
  disconnectTelemetry();

  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
  }
});

// ================= ALTITUDE CONTROL =================

const altitude = ref(140);
const isActive = ref(false);

const min = 140;
const max = 300;

const toggle = () => {
  isActive.value = !isActive.value;
};

const speed = ref(100);
const autoThrottleActive = ref(false);

const toggleSpeed = () => {
  autoThrottleActive.value = !autoThrottleActive.value;
};

const throttleLeft = ref(0);
const throttleRight = ref(0);
const throttleLinked = ref(true);

// ================= MODES =================

// TAKE OFF
const takeOffState = ref("OFF");
// OFF | ARMED | ON | LOCKED

const canTakeOff = computed(() => {
  return telemetryAltitude.value <= 0 && telemetrySpeed.value <= 0;
});

const toggleTakeOffArm = () => {
  if (!canTakeOff.value) return;

  if (takeOffState.value === "OFF") {
    takeOffState.value = "ARMED";
  } else if (takeOffState.value === "ARMED") {
    takeOffState.value = "OFF";
  }
};

const startTakeOff = () => {
  if (takeOffState.value !== "ARMED") return;

  takeOffState.value = "ON";

  setTimeout(() => {
    takeOffState.value = "LOCKED";
  }, 1500);
};

// LANDING MODE
const landingMode = ref(false);
// ================= LOCK STATES =================

const autoPilotLocked = computed(() => {
  return telemetryAltitude.value <= 140;
});

const takeOffLocked = computed(() => {
  return !canTakeOff.value && takeOffState.value === "OFF";
});

const landingLocked = computed(() => {
  return telemetryAltitude.value <= 140;
});

watch(altitude, (newVal, oldVal) => {
  if (isActive.value && newVal !== oldVal) {
    isActive.value = false;
  }
});
</script>
<template>
  <div class="cockpit">
    <PlaneDisplay :plane="planeName" />
    <!--<button class="test-btn" @click="randomizeTelemetry">TEST TELEMETRY</button>-->
    <!--<button class="zero-btn" @click="zeroTelemetry">ZERO TELEMETRY</button>-->
    <div class="left-panel">
      <AltitudeSelector
        v-model="altitude"
        :min="min"
        :max="max"
        :isActive="isActive"
        :locked="autoPilotLocked"
        :buttonLabel="'AP1'"
        @toggle="toggle"
      />

      <AltitudeSelector
        v-model="speed"
        :min="40"
        :max="200"
        label="SPD"
        :isActive="autoThrottleActive"
        :locked="autoPilotLocked"
        :buttonLabel="'A/THR'"
        @toggle="toggleSpeed"
      />
    </div>
    <!-- CENTER INSTRUMENTS (NÃO INTERFERE NO RESTO) -->
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
        :max="200"
        :size="240"
        :minLimit="140"
        :maxLimit="200"
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
      />
    </div>

    <div class="modes-bar">
      <div class="takeoff-group">
        <!-- TOGGLE ARM -->
        <ToggleSwitch
          label="TAKE OFF ARM"
          :modelValue="takeOffState === 'ARMED' || takeOffState === 'ON'"
          :locked="takeOffLocked"
          @click="toggleTakeOffArm"
        />
        <!-- BOTÃO START -->
        <button
          class="start-btn"
          :disabled="takeOffState !== 'ARMED'"
          @click="startTakeOff"
        >
          START
        </button>
      </div>

      <!-- LANDING -->
      <ToggleSwitch
        label="LANDING MODE"
        v-model="landingMode"
        :locked="landingLocked"
      />
    </div>
    <!-- FUEL BAR -->
    <FuelBar
      :fuel="fuel"
      :maxFuel="maxFuel"
      :transferActive="fuelTransfer"
      @toggle-transfer="toggleFuelTransfer"
    />
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
</style>
