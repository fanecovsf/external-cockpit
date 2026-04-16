<script setup>
import { computed } from "vue";

const BASE_SIZE = 200;

const props = defineProps({
  label: String,
  value: Number,
  max: {
    type: Number,
    default: 300,
  },
  minAngle: {
    type: Number,
    default: -120,
  },
  maxAngle: {
    type: Number,
    default: 120,
  },
  size: {
    type: Number,
    default: BASE_SIZE,
  },
  minLimit: Number,
  maxLimit: Number,
});

// escala
const scale = computed(() => props.size / BASE_SIZE);

// clamp
const clampedValue = computed(() => {
  return Math.min(props.max, Math.max(0, props.value));
});

// ângulo
const angle = computed(() => {
  const percent = clampedValue.value / props.max;
  return props.minAngle + percent * (props.maxAngle - props.minAngle);
});

// ALERTA 🔥
const isInAlert = computed(() => {
  if (props.minLimit == null || props.maxLimit == null) return false;
  return (
    clampedValue.value >= props.minLimit && clampedValue.value <= props.maxLimit
  );
});

// marcações
const marks = computed(() => {
  const steps = 6;
  const stepValue = props.max / (steps - 1);

  return Array.from({ length: steps }, (_, i) => {
    const value = Math.round(i * stepValue);
    const percent = value / props.max;
    const angle = props.minAngle + percent * (props.maxAngle - props.minAngle);

    return { value, angle };
  });
});
</script>

<template>
  <div class="gauge" :style="{ width: size + 'px', height: size + 'px' }">
    <div class="gauge-face" :style="{ transform: `scale(${scale})` }">
      <!-- TICKS -->
      <div
        v-for="n in 31"
        :key="'tick-' + n"
        class="tick"
        :style="{
          transform: `rotate(${minAngle + (n - 1) * ((maxAngle - minAngle) / 30)}deg)`,
        }"
      />

      <!-- NÚMEROS -->
      <div
        v-for="mark in marks"
        :key="mark.value"
        class="mark"
        :style="{ transform: `rotate(${mark.angle}deg)` }"
      >
        <span class="mark-label">{{ mark.value }}</span>
      </div>

      <!-- PONTEIRO -->
      <div class="needle-wrapper" :style="{ transform: `rotate(${angle}deg)` }">
        <div class="needle"></div>
      </div>

      <!-- CENTRO -->
      <div class="center-display" :class="{ alert: isInAlert }">
        <span class="value" :class="{ alert: isInAlert }">
          {{ Math.round(value) }}
        </span>
        <span class="label" :class="{ alert: isInAlert }">
          {{ label }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.gauge {
  border-radius: 50%;
  background: radial-gradient(circle at center, #222, #000);
  border: 3px solid #444;
  box-shadow:
    inset 0 0 30px rgba(0, 255, 156, 0.1),
    0 0 20px rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.gauge-face {
  position: relative;
  width: 200px;
  height: 200px;
  transform-origin: center;
}

/* ===== TICKS ===== */
.tick {
  position: absolute;
  width: 2px;
  height: 8px;
  background: #00ff9c;
  top: 8px;
  left: 50%;
  transform-origin: center 92px;
  opacity: 0.5;
}

/* ===== NÚMEROS ===== */
.mark {
  position: absolute;
  width: 100%;
  height: 100%;
}

.mark-label {
  position: absolute;
  top: 18px;
  left: 50%;
  transform: translateX(-50%) rotate(180deg);
  color: #00ff9c;
  font-size: 11px;
  font-weight: bold;
}

/* ===== PONTEIRO ===== */
.needle-wrapper {
  position: absolute;
  width: 100%;
  height: 100%;
  transform-origin: center;
  transition: transform 0.1s linear;
}

.needle {
  position: absolute;
  bottom: 50%;
  left: 50%;
  width: 3px;
  height: 80px;
  background: #ff3b3b;
  transform: translateX(-50%);
  transform-origin: bottom center;
  border-radius: 2px;
  box-shadow: 0 0 10px #ff3b3b;
}

/* ===== CENTRO ===== */
.center-display {
  position: absolute;
  width: 75px;
  height: 75px;
  background: black;
  border: 2px solid #00ff9c;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 10px #00ff9c33;
}

/* ===== TEXTO ===== */
.value {
  color: #00ff9c;
  font-size: 20px;
  font-weight: bold;
}

.label {
  font-size: 10px;
  color: #00ff9c;
  opacity: 0.7;
}

/* ===== ALERTA 🔥 ===== */
@keyframes blink {
  0%,
  100% {
    opacity: 1;
    color: #ff3b3b;
    border-color: #ff3b3b;
  }
  50% {
    opacity: 0.2;
  }
}

/* ===== ALERTA 🔥 ===== */
@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.2;
  }
}

/* 🔴 BORDA piscando */
.center-display.alert {
  border-color: #ff3b3b;
  box-shadow: inset 0 0 10px #ff3b3b33;
}

/* 🔴 anima só o que interessa */
.value.alert,
.label.alert {
  animation: blink 0.6s infinite;
  color: #ff3b3b;
}

/* 🔴 borda piscando separado */
.center-display.alert::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid #ff3b3b;
  animation: blink 0.6s infinite;
  pointer-events: none;
}
</style>
