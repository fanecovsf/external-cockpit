<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import {
  connectTelemetry,
  disconnectTelemetry,
  getLatestTelemetry,
} from "./services/telemetrySocket";
import ArtificialHorizon from "./components/ArtificialHorizon.vue";
import AltitudeSelector from "./components/AltitudeSelector.vue";
import InstrumentDisplay from "./components/InstrumentDisplay.vue";
import ToggleSwitch from "./components/ToggleSwitch.vue";

// ================= TELEMETRY STATE =================

const telemetryAltitude = ref(0);
const telemetrySpeed = ref(0);
const telemetryPitch = ref(0);
const telemetryRoll = ref(0);

// valores exibidos (suavizados)
const displayAltitude = ref(0);
const displaySpeed = ref(0);

// ================= UTILS ================
const randomizeTelemetry = () => {
  telemetryAltitude.value = Math.random() * 300;
  telemetrySpeed.value = Math.random() * 400;
};

const zeroTelemetry = () => {
  telemetryAltitude.value = 0;
  telemetrySpeed.value = 0;
};

// ================= FUEL =================

const maxFuel = 88000;
const fuel = ref(maxFuel / 2);

const fuelPercent = computed(() => {
  return (fuel.value / maxFuel) * 100;
});

const fuelTransfer = ref(false);

const toggleFuelTransfer = () => {
  fuelTransfer.value = !fuelTransfer.value;
};

// ================= HANDLE TELEMETRY =================

const handleTelemetry = (data) => {
  if (data.schema !== "telemetry") return;

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
};

// ================= MAIN LOOP (HIGH PERFORMANCE) =================

let animationFrame = null;
let lastUpdate = 0;

const loop = (time) => {
  // 🔥 controla frequência de processamento (20 FPS)
  if (time - lastUpdate > 50) {
    const data = getLatestTelemetry();

    if (data) {
      handleTelemetry(data);
    }

    lastUpdate = time;
  }

  displayAltitude.value +=
    (telemetryAltitude.value - displayAltitude.value) * 0.08;

  displaySpeed.value += (telemetrySpeed.value - displaySpeed.value) * 0.1;

  animationFrame = requestAnimationFrame(loop);
};

// ================= LIFECYCLE =================

onMounted(() => {
  connectTelemetry();
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

const toggleLandingMode = () => {
  if (telemetryAltitude.value <= 140) return;
  landingMode.value = !landingMode.value;
};

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
</script>
<template>
  <div class="cockpit">
    <button class="test-btn" @click="randomizeTelemetry">TEST TELEMETRY</button>
    <button class="zero-btn" @click="zeroTelemetry">ZERO TELEMETRY</button>
    <div class="left-panel">
      <AltitudeSelector
        v-model:altitude="altitude"
        :min="min"
        :max="max"
        :isActive="isActive"
        :locked="autoPilotLocked"
        @toggle="toggle"
      />
    </div>
    <!-- CENTER INSTRUMENTS (NÃO INTERFERE NO RESTO) -->
    <div class="instruments-wrapper">
      <InstrumentDisplay label="ALT" :value="displayAltitude" />

      <InstrumentDisplay
        label="SPD"
        :value="displaySpeed"
        :showDecimal="true"
      />

      <div class="horizon-wrapper">
        <ArtificialHorizon :pitch="telemetryPitch" :roll="telemetryRoll" />
      </div>
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
    <!-- BOTTOM BAR -->
    <div class="bottom-bar">
      <div class="fuel-container">
        <span class="fuel-label"
          >FUEL {{ fuel.toLocaleString() }} / {{ maxFuel.toLocaleString() }} -
          {{ Math.round(fuelPercent) }}%</span
        >
        <div class="fuel-bar">
          <div class="fuel-fill" :style="{ width: fuelPercent + '%' }"></div>
        </div>
      </div>
      <button
        class="fuel-transfer"
        :class="{ active: fuelTransfer }"
        @click="toggleFuelTransfer"
      >
        FUEL TRANSFER
      </button>
    </div>
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
}
.panel {
  height: 75vh;
  width: 120px;
  background: linear-gradient(145deg, #2b2b2b, #1a1a1a);
  border: 2px solid #444;
  border-radius: 12px;
  padding: 20px 10px;
  box-shadow:
    inset -4px -4px 10px rgba(0, 0, 0, 0.7),
    inset 4px 4px 10px rgba(255, 255, 255, 0.05),
    0 10px 30px rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
}
.display {
  background: black;
  color: #00ff9c;
  padding: 10px 15px;
  border-radius: 6px;
  border: 2px solid #0a0a0a;
  box-shadow: inset 0 0 10px #00ff9c33;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.label {
  font-size: 10px;
  opacity: 0.7;
}
.value {
  font-size: 26px;
  font-weight: bold;
  letter-spacing: 2px;
}
.scroll {
  position: relative;
  flex: 1;
  width: 50px;
  margin: 20px 0;
  background: linear-gradient(180deg, #111, #222);
  border: 2px solid #555;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px 0;
  cursor: ns-resize;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.8);
}
.tick {
  width: 60%;
  height: 2px;
  background: #777;
  margin: 0 auto;
  opacity: 0.6;
}
.indicator {
  position: absolute;
  left: -5px;
  width: calc(100% + 10px);
  height: 3px;
  background: #00ff9c;
  box-shadow: 0 0 8px #00ff9c;
  transition: top 0.1s linear;
}
.toggle {
  width: 100%;
  padding: 10px;
  background: linear-gradient(145deg, #3a3a3a, #1f1f1f);
  border: 1px solid #555;
  color: #999;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.toggle.active {
  color: #00ff9c;
  border-color: #00ff9c;
  box-shadow: 0 0 10px #00ff9c55;
}
.toggle:active {
  transform: translateY(2px);
} /* BOTTOM BAR */
.bottom-bar {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 70%;
  background: linear-gradient(145deg, #2b2b2b, #1a1a1a);
  border: 2px solid #444;
  border-radius: 10px;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
}
.fuel-container {
  display: flex;
  flex-direction: column;
  width: 70%;
}
.fuel-label {
  color: #aaa;
  font-size: 12px;
  margin-bottom: 5px;
}
.fuel-bar {
  width: 100%;
  height: 20px;
  background: #111;
  border: 1px solid #555;
  border-radius: 4px;
  overflow: hidden;
}
.fuel-fill {
  height: 100%;
  background: linear-gradient(90deg, #00ff9c, #00cc7a);
  box-shadow: 0 0 10px #00ff9c88;
}
.fuel-transfer {
  padding: 10px 15px;
  background: linear-gradient(145deg, #3a3a3a, #1f1f1f);
  border: 1px solid #555;
  color: #999;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.fuel-transfer.active {
  color: #00ff9c;
  border-color: #00ff9c;
  box-shadow: 0 0 10px #00ff9c55;
}
.fuel-transfer:active {
  transform: translateY(2px);
} /* ================= INSTRUMENTS (ISOLADO) ================= */
.instruments-wrapper {
  position: absolute;
  left: 50%;
  top: 17%;
  transform: translate(-50%, -50%);
  display: flex;
  gap: 80px;
} /* caixa */
.inst-box {
  background: radial-gradient(circle at center, #1a1a1a, #0a0a0a);
  border: 2px solid #333;
  border-radius: 12px;
  padding: 20px 25px;
  box-shadow:
    inset 0 0 25px #00ff9c22,
    0 0 15px rgba(0, 0, 0, 0.8);
} /* título */
.inst-title {
  display: block;
  text-align: center;
  font-size: 11px;
  color: #00ff9c;
  letter-spacing: 2px;
  margin-bottom: 10px;
} /* container dos números */
.inst-digits {
  display: flex;
  align-items: center;
  justify-content: center; /* ADICIONE */
  gap: 6px;
}
.inst-digit {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60px;
  width: 28px;
  overflow: hidden;
  position: relative;
} /* número principal */
.inst-active {
  font-size: 30px;
  font-weight: bold;
  color: #00ff9c;
} /* números fantasma */
.inst-faded {
  font-size: 14px;
  opacity: 0.45; /* antes 0.25 */
  color: #00ff9c;
} /* decimal */
.inst-decimal {
  margin-left: 8px;
  font-size: 24px;
  color: #00ff9c;
} /* máscara */
.inst-digit::before,
.inst-digit::after {
  content: "";
  position: absolute;
  width: 100%;
  height: 10px;
  left: 0;
  z-index: 2;
}
.inst-digit::before {
  top: 0;
  background: linear-gradient(to bottom, #0a0a0a, transparent);
}
.inst-digit::after {
  bottom: 0;
  background: linear-gradient(to top, #0a0a0a, transparent);
}
.tape {
  background: linear-gradient(
    180deg,
    rgba(30, 30, 30, 0.85),
    rgba(50, 50, 50, 0.85)
  );
  backdrop-filter: blur(2px);
  width: 100%;
}
.tape-container {
  width: 100px; /* antes menor */
}
.speed-value {
  display: flex;
  align-items: baseline;
  font-weight: bold;
  letter-spacing: 2px;
}
.speed-value .int {
  font-size: 28px;
}
.speed-value .dot {
  font-size: 20px;
  margin: 0 2px;
  color: #00ff9c;
  text-shadow: 0 0 6px #00ff9c;
}
.speed-value .dec {
  font-size: 18px;
  opacity: 0.85;
}
.tape::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0.6),
    transparent 30%,
    transparent 70%,
    rgba(0, 0, 0, 0.6)
  );
  pointer-events: none;
}
.inst-decimal-block {
  display: flex;
  align-items: center;
  margin-left: 4px; /* menor para equilibrar */
}
.inst-dot {
  font-size: 22px;
  margin-right: 4px;
  color: #00ff9c;
  text-shadow: 0 0 8px #00ff9c;
}
.inst-digit.small {
  width: 28px; /* igual aos outros */
  height: 60px; /* igual aos outros */
}

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

.inst-box {
  width: 160px; /* ADICIONE ISSO */
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

/* botão padrão */
.mode-btn {
  padding: 12px 18px;
  background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
  border: 1px solid #555;
  color: #777;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  letter-spacing: 1px;
  transition: all 0.2s ease;
}

/* AUTO PILOT ativo */
.mode-btn.active {
  color: #00ff9c;
  border-color: #00ff9c;
  box-shadow: 0 0 10px #00ff9c55;
}

/* TAKE OFF estados */
.mode-btn.armed {
  color: #00aaff;
  border-color: #00aaff;
  box-shadow: 0 0 10px #00aaff55;
}

.mode-btn.on {
  color: #00ff9c;
  border-color: #00ff9c;
  box-shadow: 0 0 12px #00ff9c88;
}

.mode-btn.locked {
  color: #ff4444;
  border-color: #ff4444;
}

/* grupo takeoff */
.takeoff-group {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* sub botão START */
.sub-btn {
  padding: 10px 14px;
  background: linear-gradient(145deg, #003a2a, #001a12);
  border: 1px solid #00ff9c;
  color: #00ff9c;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 0 10px #00ff9c55;
}

.sub-btn:active {
  transform: translateY(2px);
}

/* container */
.toggle-switch {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

/* base metálica */
.switch-base {
  width: 50px;
  height: 70px;
  background: linear-gradient(145deg, #2a2a2a, #111);
  border: 2px solid #555;
  border-radius: 8px;
  position: relative;
  box-shadow:
    inset 0 0 10px rgba(0, 0, 0, 0.8),
    0 4px 10px rgba(0, 0, 0, 0.8);
}

/* alavanca */
.switch-lever {
  position: absolute;
  left: 50%;
  top: 10px;
  transform: translateX(-50%) rotate(25deg);
  width: 6px;
  height: 40px;
  background: linear-gradient(180deg, #aaa, #555);
  border-radius: 4px;
  transform-origin: bottom center;
  transition: all 0.2s ease;
}

/* estado ON (levanta a chave) */
.switch-lever.on {
  top: 20px;
  transform: translateX(-50%) rotate(-25deg);
  background: linear-gradient(180deg, #00ff9c, #007a55);
  box-shadow: 0 0 8px #00ff9c;
}

/* label */
.switch-label {
  font-size: 11px;
  color: #aaa;
  letter-spacing: 1px;
}

.switch-lever.on + .switch-label,
.toggle-switch:has(.on) .switch-label {
  color: #00ff9c;
}

.switch-base::after {
  content: "";
  position: absolute;
  bottom: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: #222;
  border-radius: 50%;
}

.switch-lever.on ~ .switch-base::after {
  background: #00ff9c;
  box-shadow: 0 0 6px #00ff9c;
}

.switch-lever:active {
  transform: translateX(-50%) scaleY(0.95);
}

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

/* efeito de pressionar */
.start-btn:active:not(:disabled) {
  transform: translateY(4px);
  box-shadow:
    0 1px 0 #000,
    inset 0 0 10px #00ff9c55;
}

/* desabilitado */
.start-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.start-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #ff4444;
  color: #ff4444;
  box-shadow:
    0 2px 0 #300,
    inset 0 0 6px #ff444444;
}

.mode-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #ff4444;
  color: #ff4444;
  box-shadow:
    0 2px 0 #300,
    inset 0 0 6px #ff444444;
}

.horizon-wrapper {
  position: absolute;
  left: 50%;
  top: 400%;
  transform: translate(-50%, -50%);
}
</style>
