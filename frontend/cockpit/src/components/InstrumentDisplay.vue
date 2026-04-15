<script setup>
import { computed } from "vue";

const props = defineProps({
  label: String,
  value: Number,
  showDecimal: {
    type: Boolean,
    default: false,
  },
});

// ===== helpers =====
const getDigits = (value) => {
  const str = Math.floor(value).toString().padStart(3, "0");
  return str.split("").map((n) => parseInt(n));
};

const getDecimal = (value) => {
  return Math.floor((value % 1) * 10);
};

const digits = computed(() => getDigits(props.value));
const decimal = computed(() => getDecimal(props.value));
</script>

<template>
  <div class="inst-box">
    <span class="inst-title">{{ label }}</span>

    <div class="inst-digits">
      <!-- parte inteira -->
      <div class="inst-digit" v-for="(d, i) in digits" :key="i">
        <span class="inst-faded">{{ (d + 1) % 10 }}</span>
        <span class="inst-active">{{ d }}</span>
        <span class="inst-faded">{{ (d + 9) % 10 }}</span>
      </div>

      <!-- decimal opcional -->
      <div v-if="showDecimal" class="inst-decimal-block">
        <span class="inst-dot">.</span>

        <div class="inst-digit small">
          <span class="inst-faded">{{ (decimal + 1) % 10 }}</span>
          <span class="inst-active">{{ decimal }}</span>
          <span class="inst-faded">{{ (decimal + 9) % 10 }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.inst-box {
  width: 160px;
  background: radial-gradient(circle at center, #1a1a1a, #0a0a0a);
  border: 2px solid #333;
  border-radius: 12px;
  padding: 20px 25px;
  box-shadow:
    inset 0 0 25px #00ff9c22,
    0 0 15px rgba(0, 0, 0, 0.8);
}

.inst-title {
  display: block;
  text-align: center;
  font-size: 11px;
  color: #00ff9c;
  letter-spacing: 2px;
  margin-bottom: 10px;
}

.inst-digits {
  display: flex;
  align-items: center;
  justify-content: center;
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
}

.inst-active {
  font-size: 30px;
  font-weight: bold;
  color: #00ff9c;
}

.inst-faded {
  font-size: 14px;
  opacity: 0.45;
  color: #00ff9c;
}

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

.inst-decimal-block {
  display: flex;
  align-items: center;
  margin-left: 4px;
}

.inst-dot {
  font-size: 22px;
  margin-right: 4px;
  color: #00ff9c;
  text-shadow: 0 0 8px #00ff9c;
}

.inst-digit.small {
  width: 28px;
  height: 60px;
}
</style>
