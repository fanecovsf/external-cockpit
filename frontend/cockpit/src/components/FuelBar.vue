<script setup>
import { computed } from "vue";

const props = defineProps({
  fuel: Number,
  maxFuel: Number,
  transferActive: Boolean,
});

const fuelPercent = computed(() => {
  if (!props.maxFuel) return 0;
  return (props.fuel / props.maxFuel) * 100;
});
</script>

<template>
  <div class="bottom-bar">
    <div class="fuel-container">
      <span class="fuel-label">
        FUEL {{ fuel.toLocaleString() }} / {{ maxFuel.toLocaleString() }} -
        {{ Math.round(fuelPercent) }}%
      </span>

      <div class="fuel-bar">
        <div class="fuel-fill" :style="{ width: fuelPercent + '%' }"></div>
      </div>
    </div>

    <button class="fuel-transfer" :class="{ active: transferActive }">
      FUEL TRANSFER
    </button>
  </div>
</template>

<style scoped>
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
  transition: all 0.2s ease;
}

.fuel-transfer.active {
  color: #00ff9c;
  border-color: #00ff9c;
  box-shadow: 0 0 10px #00ff9c55;
}
</style>
