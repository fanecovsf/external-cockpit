<script setup>
import { computed } from "vue";

const props = defineProps({
  plane: {
    type: String,
    default: "",
  },
});

// máximo de 10 chars
const maxChars = 10;

// transforma string em array fixo
const chars = computed(() => {
  const clean = (props.plane || "").toUpperCase().slice(0, maxChars);
  const arr = clean.split("");

  while (arr.length < maxChars) {
    arr.push("-");
  }

  return arr;
});

const isConnected = computed(() => {
  return props.plane && props.plane.trim().length > 0;
});
</script>

<template>
  <div class="plane-display">
    <div class="led" :class="{ on: isConnected }"></div>

    <span class="label">AIRCRAFT</span>

    <div class="slots">
      <div v-for="(char, i) in chars" :key="i" class="slot">
        {{ char }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.plane-display {
  position: absolute;
  top: 20px;
  right: 20px;

  width: 340px;
  height: 90px;

  background: linear-gradient(145deg, #2a2a2a, #0f0f0f);
  border-radius: 12px;

  border: 2px solid #555;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  box-shadow:
    0 4px 10px rgba(0, 0, 0, 0.8),
    inset 0 0 10px rgba(255, 255, 255, 0.05);

  font-family: "Courier New", monospace;
}

.label {
  font-size: 10px;
  color: #00ff9c;
  opacity: 0.6;
  letter-spacing: 2px;
  margin-bottom: 6px;
}

/* container dos caracteres */
.slots {
  display: flex;
  gap: 4px;
  padding: 4px 8px;

  background: #000;
  border-radius: 6px;

  box-shadow: inset 0 0 10px #000;
}

/* cada slot */
.slot {
  width: 22px;
  height: 32px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-left: 1px solid #00ff9c33;
  border-right: 1px solid #00ff9c33;

  color: #00ff9c;
  font-weight: bold;
  font-size: 16px;

  text-shadow: 0 0 6px #00ff9c;

  background: linear-gradient(180deg, #001a12, #000);
  box-shadow: inset 0 0 6px #00ff9c22;
}

/* primeiro e último mais clean */
.slot:first-child {
  border-left: none;
}

.slot:last-child {
  border-right: none;
}

.led {
  width: 10px;
  height: 10px;
  border-radius: 50%;

  margin-bottom: 6px;

  background: #400000;

  box-shadow:
    0 0 6px #ff000055,
    inset 0 0 4px #000;

  transition: all 0.2s ease;
}

.led.on {
  background: #00ff9c;

  box-shadow:
    0 0 8px #00ff9c,
    0 0 16px #00ff9c55,
    inset 0 0 4px #003a2a;
}
</style>
