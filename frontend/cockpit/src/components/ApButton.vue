```vue
<script setup>
const props = defineProps({
  label: String,
  active: Boolean,
  locked: Boolean,
});

const emit = defineEmits(["update:modelValue", "toggle"]);

const handleClick = () => {
  // bloqueia apenas se locked e OFF
  if (props.locked && !props.active) return;

  emit("toggle");
};
</script>

<template>
  <button
    class="ap-button"
    :class="{ active: active, locked: locked }"
    @click="handleClick"
    :disabled="locked && !active"
  >
    <div class="top-bar"></div>
    <span class="text">{{ label }}</span>
  </button>
</template>

<style scoped>
.ap-button {
  width: 60px;
  height: 60px;
  background: #0a0a0a;
  border: 1px solid #5a5a5a;
  border-radius: 6px;

  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  box-shadow:
    inset -2px -2px 5px rgba(0, 0, 0, 0.9),
    inset 2px 2px 3px rgba(255, 255, 255, 0.04),
    0 0 0 1px rgba(0, 0, 0, 0.6);

  transition: filter 0.15s ease;
}

/* TEXTO */
.text {
  color: #ddd;
  font-size: 13px;
  font-weight: bold;
  letter-spacing: 1px;
}

/* BARRA BASE */
.top-bar {
  position: absolute;
  top: 6px;
  left: 8px;
  right: 8px;
  height: 4px;
  border-radius: 2px;
  background: #222;
  transition: all 0.2s ease;
}

/* ATIVO */
.ap-button.active .top-bar {
  background: #00ff9c;
  box-shadow: 0 0 4px rgba(0, 255, 156, 0.5);
}

/* LOCKED (somente se OFF) */
.ap-button.locked:not(.active) .top-bar {
  background: #aa3333;
  box-shadow: 0 0 4px rgba(255, 0, 0, 0.4);
}

/* HOVER */
.ap-button:hover:not(:disabled) {
  filter: brightness(1.08);
}

/* CURSOR CORRETO */
.ap-button:disabled {
  cursor: not-allowed;
}

/* MICRO HIGHLIGHT */
.ap-button::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 6px;
  box-shadow: inset 0 0 2px rgba(255, 255, 255, 0.03);
}
</style>
```
