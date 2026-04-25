<script setup>
const props = defineProps({
  label: String,
  modelValue: Boolean,
  locked: Boolean,
});

const emit = defineEmits(["click"]);

const handleClick = () => {
  if (props.locked) return;
  emit("click");
};

const getStatus = () => {
  if (props.locked) return { text: "LOCK", class: "locked" };
  if (props.modelValue) return { text: "ON", class: "on" };
  return { text: "OFF", class: "off" };
};
</script>

<template>
  <div class="toggle-switch" @click="handleClick" :class="{ locked }">
    <div class="status-display" :class="getStatus().class">
      {{ getStatus().text }}
    </div>

    <div class="switch-base">
      <div class="screw tl"></div>
      <div class="screw tr"></div>
      <div class="screw bl"></div>
      <div class="screw br"></div>

      <div class="switch-track">
        <div class="switch-knob" :class="{ on: modelValue }"></div>
      </div>
    </div>

    <span class="switch-label">{{ label }}</span>
  </div>
</template>

<style scoped>
.toggle-switch {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.status-display {
  width: 50px;
  height: 18px;
  font-size: 10px;
  font-weight: bold;
  text-align: center;
  line-height: 18px;
  border-radius: 4px;
  background: #111;
  border: 1px solid #333;
  letter-spacing: 1px;
}

.status-display.on {
  color: #00ff9c;
  box-shadow: 0 0 6px rgba(0, 255, 156, 0.5);
}

.status-display.off {
  color: #aaa;
}

.status-display.locked {
  color: #ff4444;
  box-shadow: 0 0 6px rgba(255, 0, 0, 0.5);
}

.switch-base {
  width: 60px;
  height: 90px;
  background: linear-gradient(145deg, #3a3a3a, #111);
  border: 2px solid #666;
  border-radius: 10px;
  position: relative;
  box-shadow:
    inset -5px -5px 10px rgba(0, 0, 0, 0.9),
    inset 5px 5px 10px rgba(255, 255, 255, 0.05);
}

.screw {
  width: 6px;
  height: 6px;
  background: #999;
  border-radius: 50%;
  position: absolute;
}

.tl {
  top: 5px;
  left: 5px;
}
.tr {
  top: 5px;
  right: 5px;
}
.bl {
  bottom: 5px;
  left: 5px;
}
.br {
  bottom: 5px;
  right: 5px;
}

.switch-track {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 30px;
  height: 60px;
  background: linear-gradient(180deg, #0a0a0a, #000);
  border-radius: 6px;
  box-shadow: inset 0 0 8px #000;
}

.switch-knob {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 14px;
  background: linear-gradient(145deg, #bbb, #555);
  border-radius: 4px;
  border: 1px solid #222;
  box-shadow:
    0 2px 4px rgba(0, 0, 0, 0.8),
    inset 0 0 4px rgba(255, 255, 255, 0.2);

  top: 36px;
  transition: top 0.2s ease;
}

.switch-knob.on {
  top: 10px;
}

.switch-label {
  font-size: 11px;
  color: #bbb;
  letter-spacing: 1px;
}

.toggle-switch.locked {
  cursor: not-allowed;
}
</style>
