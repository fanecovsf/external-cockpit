<script setup>
import { ref, computed, onMounted } from "vue";

const props = defineProps({
  pitch: { type: Number, default: 0 },
  roll: { type: Number, default: 0 },
});

const displayPitch = ref(0);
const displayRoll = ref(0);

const SMOOTH = 0.05;

function lerp(current, target, factor) {
  return current + (target - current) * factor;
}

function animate() {
  displayPitch.value = lerp(displayPitch.value, props.pitch, SMOOTH);
  displayRoll.value = lerp(displayRoll.value, props.roll, SMOOTH);
  requestAnimationFrame(animate);
}

onMounted(() => animate());

// escala visual
const pitchOffset = computed(() => displayPitch.value * 140);
const rollRotation = computed(() => displayRoll.value * 180);

// linhas de pitch (de -90 até +90)
const pitchLines = Array.from({ length: 19 }, (_, i) => (i - 9) * 10);
</script>

<template>
  <div class="horizon">
    <!-- ROLL SCALE -->
    <div class="roll-scale">
      <div
        v-for="r in [-60, -45, -30, -20, -10, 0, 10, 20, 30, 45, 60]"
        :key="r"
        class="roll-tick"
        :style="{ transform: `rotate(${r}deg)` }"
      >
        <div class="tick-line"></div>
      </div>
    </div>

    <!-- MUNDO -->
    <div
      class="horizon-inner"
      :style="{
        transform: `rotate(${rollRotation}deg) translateY(${pitchOffset}px)`,
      }"
    >
      <div class="sky"></div>
      <div class="ground"></div>

      <!-- LINHAS DE PITCH -->
      <div
        v-for="p in pitchLines"
        :key="p"
        class="pitch-line"
        :style="{ top: `${100 - p * 1}%` }"
      >
        <div class="line-mark"></div>
        <span v-if="p % 20 === 0 && p !== 0" class="pitch-text">
          {{ Math.abs(p) }}
        </span>
      </div>

      <!-- HORIZONTE -->
      <div class="main-line"></div>
    </div>

    <!-- AVIÃO -->
    <div class="aircraft">
      <div class="wing"></div>
      <div class="center"></div>
      <div class="wing"></div>
    </div>
  </div>
</template>

<style scoped>
.horizon {
  width: 350px;
  height: 350px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #222;
  position: relative;
  background: black;
  box-shadow: inset 0 0 30px #000;
}

/* escala de roll */
.roll-scale {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.roll-tick {
  position: absolute;
  width: 100%;
  height: 100%;
}

.tick-line {
  position: absolute;
  top: 5px;
  left: 50%;
  width: 2px;
  height: 12px;
  background: white;
}

/* mundo */
.horizon-inner {
  position: absolute;
  width: 300%;
  height: 300%;
  top: -100%;
  left: -100%;
}

/* céu infinito */
.sky {
  position: absolute;
  width: 100%;
  height: 50%;
  background: linear-gradient(#6ec6ff, #1e90ff);
}

/* chão infinito */
.ground {
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 50%;
  background: linear-gradient(#9b6b3f, #5a3a1a);
}

/* linha principal */
.main-line {
  position: absolute;
  top: 50%;
  width: 100%;
  height: 3px;
  background: white;
  box-shadow: 0 0 8px white;
}

/* linhas de pitch */
.pitch-line {
  position: absolute;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.line-mark {
  width: 80px;
  height: 2px;
  background: white;
}

.pitch-text {
  position: absolute;
  right: 10px;
  font-size: 12px;
  color: white;
}

/* avião */
.aircraft {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
}

.wing {
  width: 70px;
  height: 3px;
  background: #00ff9c;
}

.center {
  width: 12px;
  height: 12px;
  border: 2px solid #00ff9c;
  border-radius: 50%;
  margin: 0 6px;
}
</style>
