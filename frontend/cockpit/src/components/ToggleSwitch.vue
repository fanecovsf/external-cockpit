<script setup>
const props = defineProps({
  label: String,
  modelValue: Boolean, // estado ON/OFF
  locked: Boolean,
});

const emit = defineEmits(["update:modelValue", "click"]);

const handleClick = () => {
  console.log(
    "ToggleSwitch clicked. Locked:",
    props.locked,
    "Current Value:",
    props.modelValue,
  );
  if (props.locked) return;

  emit("update:modelValue", !props.modelValue);
  emit("click");
};
</script>

<template>
  <div class="toggle-switch" @click="handleClick" :class="{ locked: locked }">
    <div class="switch-base">
      <div class="switch-lever" :class="{ on: modelValue }"></div>
    </div>

    <span class="switch-label">{{ label }}</span>
  </div>
</template>

<style scoped>
.toggle-switch {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

.switch-base {
  width: 50px;
  height: 70px;
  background: linear-gradient(145deg, #2a2a2a, #111);
  border: 2px solid #555;
  border-radius: 8px;
  position: relative;
}

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

.switch-lever.on {
  top: 20px;
  transform: translateX(-50%) rotate(-25deg);
  background: linear-gradient(180deg, #00ff9c, #007a55);
  box-shadow: 0 0 8px #00ff9c;
}

.switch-label {
  font-size: 11px;
  color: #aaa;
  letter-spacing: 1px;
}

.toggle-switch.locked .switch-base {
  border-color: #ff4444;
  box-shadow: 0 0 10px rgba(255, 68, 68, 0.4);
}

.toggle-switch.locked .switch-lever {
  background: linear-gradient(180deg, #ff8888, #aa2222);
}

.toggle-switch.locked .switch-label {
  color: #ff4444;
}
</style>
