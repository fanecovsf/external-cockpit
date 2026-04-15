<script setup>
import { computed } from "vue";

const props = defineProps({
  altitude: Number,
  min: Number,
  max: Number,
  isActive: Boolean,
  locked: Boolean,
});

const emit = defineEmits(["update:altitude", "toggle"]);

const onScroll = (e) => {
  if (e.deltaY < 0 && props.altitude < props.max) {
    emit("update:altitude", Math.min(props.max, props.altitude + 10));
  } else if (e.deltaY > 0 && props.altitude > props.min) {
    emit("update:altitude", Math.max(props.min, props.altitude - 10));
  }
};

const indicatorPosition = computed(() => {
  const range = props.max - props.min;
  const value = props.altitude - props.min;
  return 100 - (value / range) * 100;
});
</script>

<template>
  <div class="panel">
    <div class="display">
      <span class="label">ALT</span>
      <span class="value">{{ altitude }}</span>
    </div>

    <div class="scroll" @wheel.prevent="onScroll">
      <div class="indicator" :style="{ top: indicatorPosition + '%' }"></div>

      <div class="tick" v-for="n in 30" :key="n"></div>
    </div>

    <button
      class="toggle mode-btn"
      :class="{ locked }"
      @click="!locked && emit('toggle')"
      :disabled="locked"
    >
      {{ isActive ? "ACTIVE" : "ARM" }}
    </button>
  </div>
</template>

<style scoped>
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
}

.toggle.locked {
  color: #ff4444;
  border-color: #ff4444;
}
</style>
