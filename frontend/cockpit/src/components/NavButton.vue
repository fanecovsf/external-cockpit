<script setup>
const props = defineProps({
  active: Boolean,
  disabled: Boolean,
});

const emit = defineEmits(["toggle"]);

const handleClick = () => {
  if (props.disabled) return;
  emit("toggle");
};
</script>

<template>
  <button class="nav-btn" :class="{ active, disabled }" @click="handleClick">
    <div class="label">NAVIGATION</div>
    <div class="sub">MAP SYSTEM</div>

    <div class="indicator"></div>
  </button>
</template>

<style scoped>
.nav-btn {
  width: 100%;
  height: 70px;

  position: relative;
  overflow: hidden;

  background: linear-gradient(145deg, #1a1a1a, #0e0e0e);
  border: 1px solid #333;
  border-radius: 10px;

  cursor: pointer;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  transition: all 0.15s ease;
  box-shadow:
    inset 0 0 10px rgba(0, 0, 0, 0.8),
    0 2px 6px rgba(0, 0, 0, 0.6);
}

/* TEXT */
.label {
  font-size: 12px;
  font-weight: bold;
  color: #aaa;
  letter-spacing: 1px;
}

.sub {
  font-size: 9px;
  color: #555;
  margin-top: 2px;
}

/* INDICATOR LIGHT */
.indicator {
  position: absolute;
  right: 10px;
  top: 10px;

  width: 8px;
  height: 8px;
  border-radius: 50%;

  background: #333;
  box-shadow: inset 0 0 4px rgba(0, 0, 0, 0.8);
  transition: all 0.2s ease;
}

/* ACTIVE STATE */
.nav-btn.active {
  border-color: #00ff9c;
  box-shadow:
    inset 0 0 12px rgba(0, 255, 156, 0.15),
    0 0 10px rgba(0, 255, 156, 0.2);
}

.nav-btn.active .label {
  color: #00ff9c;
}

.nav-btn.active .sub {
  color: #00ff9c;
  opacity: 0.6;
}

.nav-btn.active .indicator {
  background: #00ff9c;
  box-shadow: 0 0 8px #00ff9c;
}

/* PRESS EFFECT */
.nav-btn:active {
  transform: scale(0.98);
}

/* DISABLED */
.nav-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
