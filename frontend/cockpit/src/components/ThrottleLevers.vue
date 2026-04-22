```vue
<script setup>
import {
  connectThrottleTelemetry,
  disconnectThrottleTelemetry,
  connectThrottleCommands,
  disconnectThrottleCommands,
  sendThrottleCommand,
} from "../services/throttleSocket";

import { ref, watch, onMounted } from "vue";

const props = defineProps({
  leftValue: Number,
  rightValue: Number,
  max: {
    type: Number,
    default: 15,
  },
  linked: Boolean,
  autothrottleActive: Boolean,
});

const emit = defineEmits([
  "update:leftValue",
  "update:rightValue",
  "update:linked",
]);

const dragging = ref(null);
const slotRef = ref(null);

const HANDLE_HEIGHT = 46;

// ===== SPRING PHYSICS =====
const smoothValue = ref({
  left: props.leftValue,
  right: props.rightValue,
});

const velocity = ref({
  left: 0,
  right: 0,
});

// ajuste fino (sensação de peso)
const STIFFNESS = 0.08;
const DAMPING = 0.82;

const animate = () => {
  ["left", "right"].forEach((side) => {
    const target = side === "left" ? props.leftValue : props.rightValue;

    const delta = target - smoothValue.value[side];

    velocity.value[side] += delta * STIFFNESS;
    velocity.value[side] *= DAMPING;

    smoothValue.value[side] += velocity.value[side];

    // snap quando chega muito perto
    if (Math.abs(delta) < 0.01) {
      smoothValue.value[side] = target;
      velocity.value[side] = 0;
    }
  });

  requestAnimationFrame(animate);
};

onMounted(() => {
  animate();
});

// ===== POSIÇÃO =====
const getPosition = (val) => {
  const percent = val / props.max;

  const offset = (HANDLE_HEIGHT / (slotRef.value?.clientHeight || 1)) * 50;

  return 100 - percent * (100 - offset * 2) - offset;
};

// ===== DRAG =====
const startDrag = (e, side) => {
  if (props.autothrottleActive) return;

  e.preventDefault();
  dragging.value = side;

  window.addEventListener("mousemove", onMove);
  window.addEventListener("mouseup", stopDrag);
};

const stopDrag = () => {
  dragging.value = null;
  window.removeEventListener("mousemove", onMove);
  window.removeEventListener("mouseup", stopDrag);
};

const onMove = (e) => {
  if (!dragging.value || !slotRef.value) return;

  const rect = slotRef.value.getBoundingClientRect();

  const y = e.clientY - rect.top;

  const minY = HANDLE_HEIGHT / 2;
  const maxY = rect.height - HANDLE_HEIGHT / 2;

  const clampedY = Math.max(minY, Math.min(maxY, y));

  const percent = (clampedY - minY) / (maxY - minY);

  const value = Math.round((1 - percent) * props.max);

  if (props.linked) {
    emit("update:leftValue", value);
    emit("update:rightValue", value);
  } else {
    if (dragging.value === "left") {
      emit("update:leftValue", value);
    } else {
      emit("update:rightValue", value);
    }
  }
};

// ===== LOCK =====
const toggleLink = () => {
  emit("update:linked", !props.linked);
};

// ===== STATUS =====
const getEngineStatus = (value) => {
  if (value === 0) return { label: "OFF", class: "off" };
  if (value <= 9) return { label: "IDLE", class: "idle" };
  if (value <= 14) return { label: "CRUISE", class: "cruise" };
  return { label: "TAKEOFF", class: "takeoff" };
};

// ===== PERCENT =====
const getPercent = (value) => {
  const num = Number(value);

  if (isNaN(num) || props.max === 0) return "0%";

  if (num === 0) return "0%";
  if (num === props.max) return "100%";

  return Math.round((num / props.max) * 100) + "%";
};

watch(
  () => props.autothrottleActive,
  (active) => {
    if (active) {
      disconnectThrottleCommands();

      connectThrottleTelemetry((data) => {
        if (data.schema === "telemetry") {
          emit("update:leftValue", Number(data.engine1) || 0);
          emit("update:rightValue", Number(data.engine2) || 0);
        }
      });
    } else {
      disconnectThrottleTelemetry();
      connectThrottleCommands();
    }
  },
);

watch(
  () => [props.leftValue, props.rightValue],
  ([left, right]) => {
    if (!props.autothrottleActive) {
      sendThrottleCommand({
        schema: "command",
        engine1: left,
        engine2: right,
      });
    }
  },
);
</script>

<template>
  <div class="throttle">
    <!-- DISPLAY -->
    <div class="display">
      <div class="engine">
        <span class="label">E1</span>
        <span class="value">{{ getPercent(leftValue) }}</span>
        <span class="status" :class="getEngineStatus(leftValue).class">
          {{ getEngineStatus(leftValue).label }}
        </span>
      </div>

      <div class="engine">
        <span class="label">E2</span>
        <span class="value">{{ getPercent(rightValue) }}</span>
        <span class="status" :class="getEngineStatus(rightValue).class">
          {{ getEngineStatus(rightValue).label }}
        </span>
      </div>
    </div>

    <!-- SLOT -->
    <div class="slot" ref="slotRef">
      <div class="rail left-rail"></div>
      <div class="rail right-rail"></div>

      <div
        class="lever left"
        :style="{ top: getPosition(smoothValue.left, 'left') + '%' }"
        @mousedown="(e) => startDrag(e, 'left')"
      >
        <div class="handle"></div>
      </div>

      <div
        class="lever right"
        :style="{ top: getPosition(smoothValue.right, 'right') + '%' }"
        @mousedown="(e) => startDrag(e, 'right')"
      >
        <div class="handle"></div>
      </div>
    </div>

    <!-- LOCK -->
    <button class="link-btn" :class="{ active: linked }" @click="toggleLink">
      LOCK
    </button>
  </div>
</template>

<style scoped>
.throttle {
  width: 160px;
  height: 415px;
  background: linear-gradient(145deg, #2a2a2a, #0f0f0f);
  border: 2px solid #444;
  border-radius: 16px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow:
    inset -6px -6px 14px rgba(0, 0, 0, 0.8),
    inset 6px 6px 14px rgba(255, 255, 255, 0.05);
}

/* DISPLAY */
.display {
  display: flex;
  justify-content: space-around;
  background: black;
  border: 2px solid #222;
  border-radius: 8px;
  padding: 8px;
  box-shadow: inset 0 0 12px #00ff9c22;
}

.engine {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #00ff9c;
}

.label {
  font-size: 10px;
  opacity: 0.6;
}

.value {
  font-size: 16px;
  font-weight: bold;
}

/* SLOT */
.slot {
  position: relative;
  height: 300px;
  background: linear-gradient(180deg, #111, #222);
  border-radius: 12px;
  border: 2px solid #555;
}

/* RAILS */
.rail {
  position: absolute;
  width: 5px;
  height: 100%;
  background: #444;
}

.left-rail {
  left: 30%;
}
.right-rail {
  left: 70%;
}

/* LEVERS */
.lever {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: grab;
}

.lever:active {
  cursor: grabbing;
}

.lever.left {
  left: 30%;
}
.lever.right {
  left: 70%;
}

/* HANDLE */
.handle {
  width: 26px;
  height: 46px;
  background: linear-gradient(145deg, #3a3a3a, #111);
  border-radius: 8px;
  border: 2px solid #00ff9c;
  box-shadow:
    0 4px 8px rgba(0, 0, 0, 0.9),
    inset 0 0 10px #00ff9c44;
  position: relative;
}

.handle::before {
  content: "";
  position: absolute;
  top: -7px;
  left: 50%;
  width: 20px;
  height: 12px;
  background: #2a2a2a;
  border-radius: 8px 8px 0 0;
  transform: translateX(-50%);
}

.handle::after {
  content: "";
  position: absolute;
  top: 7px;
  left: 50%;
  width: 2px;
  height: 12px;
  background: #00ff9c;
  transform: translateX(-50%);
}

/* LOCK */
.link-btn {
  background: #111;
  border: 1px solid #555;
  color: #777;
  padding: 8px;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
}

.link-btn.active {
  color: #00ff9c;
  border-color: #00ff9c;
  box-shadow: 0 0 10px #00ff9c55;
}

/* STATUS */
.status {
  font-size: 10px;
  margin-top: 2px;
  font-weight: bold;
  letter-spacing: 0.5px;
}

.status.off {
  color: #ff3b3b;
}
.status.idle {
  color: #ff9f1a;
}
.status.cruise {
  color: #3aa0ff;
}
.status.takeoff {
  color: #00ff9c;
}
</style>
```
