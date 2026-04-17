<script setup>
import { computed } from "vue";
import ApButton from "./ApButton.vue";

const props = defineProps({
  modelValue: Number, // <- mais padrão pra reutilização
  min: {
    type: Number,
    default: 0,
  },
  max: {
    type: Number,
    default: 300,
  },
  label: {
    type: String,
    default: "ALT",
  },
  isActive: Boolean,
  locked: Boolean,
  buttonLabel: {
    type: String,
    default: "AP",
  },
});

const emit = defineEmits(["update:modelValue", "toggle"]);

// SCROLL
const onScroll = (e) => {
  e.preventDefault();

  const step = 10;

  if (e.deltaY < 0) {
    emit("update:modelValue", Math.min(props.max, props.modelValue + step));
  } else {
    emit("update:modelValue", Math.max(props.min, props.modelValue - step));
  }
};

// POSIÇÃO DO INDICADOR
const indicatorPosition = computed(() => {
  const range = props.max - props.min;
  const value = props.modelValue - props.min;
  return 100 - (value / range) * 100;
});

const handleClick = () => {
  if (props.locked && !props.isActive) return;

  emit("toggle");
};
</script>

<template>
  <div class="panel">
    <!-- DISPLAY -->
    <div class="display">
      <span class="label">{{ label }}</span>
      <span class="value">{{ modelValue }}</span>
    </div>

    <!-- SCROLL -->
    <div
      class="scroll"
      @wheel="onScroll"
      @mouseenter="(e) => e.currentTarget.focus()"
      tabindex="0"
    >
      <!-- INDICADOR (AGORA BOTÃO REAL) -->
      <div class="indicator" :style="{ top: indicatorPosition + '%' }">
        <div class="knob"></div>
      </div>

      <!-- TICKS -->
      <div class="tick" v-for="n in 20" :key="n"></div>
    </div>

    <!-- BOTÃO -->
    <ApButton
      :label="buttonLabel"
      :active="isActive"
      :locked="locked"
      @toggle="handleClick"
    />
  </div>
</template>

<style scoped>
.panel {
  height: 70vh;
  width: 90px; /* 👈 mais fino */
  background: linear-gradient(145deg, #2b2b2b, #1a1a1a);
  border: 2px solid #444;
  border-radius: 10px;
  padding: 15px 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  box-shadow:
    inset -3px -3px 8px rgba(0, 0, 0, 0.7),
    inset 3px 3px 8px rgba(255, 255, 255, 0.05);
}

/* DISPLAY */
.display {
  width: 60px; /* 👈 largura fixa */
  background: black;
  color: #00ff9c;
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #0a0a0a;
  box-shadow: inset 0 0 8px #00ff9c33;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.label {
  font-size: 9px;
  opacity: 0.7;
}

.value {
  font-size: 20px;
  font-weight: bold;
}

/* SCROLL */
.scroll {
  position: relative;
  flex: 1;
  width: 36px; /* 👈 mais fino */
  margin: 15px 0;
  background: linear-gradient(180deg, #111, #222);
  border: 1px solid #555;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 8px 0;
  cursor: ns-resize;
  outline: none;
}

/* TICKS */
.tick {
  width: 50%;
  height: 2px;
  background: #666;
  margin: 0 auto;
}

/* INDICADOR */
.indicator {
  position: absolute;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* KNOB REAL 🔥 */
.knob {
  width: 28px;
  height: 14px;
  background: linear-gradient(145deg, #3a3a3a, #111);
  border: 1px solid #00ff9c;
  border-radius: 4px;
  box-shadow:
    0 2px 4px rgba(0, 0, 0, 0.8),
    inset 0 0 4px #00ff9c55;
}

/* BOTÃO */
.toggle {
  width: 100%;
  padding: 8px;
  font-size: 11px;
  background: linear-gradient(145deg, #3a3a3a, #1f1f1f);
  border: 1px solid #555;
  color: #999;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
}

.toggle.locked {
  color: #ff4444;
  border-color: #ff4444;
}

.toggle.active {
  color: #00ff9c;
  border-color: #00ff9c;
  box-shadow: 0 0 8px #00ff9c55;
}
</style>
