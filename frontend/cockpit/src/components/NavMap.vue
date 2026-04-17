<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const emit = defineEmits(["close"]);

const canvasRef = ref(null);
const containerRef = ref(null);

// posição avião (fallback)
const position = ref({ x: 0, z: 0 });

// rota
const inputX = ref(0);
const inputZ = ref(0);
const route = ref(null);

const scale = ref(1);

const close = () => emit("close");

// ================= ROUTE =================
const defineRoute = () => {
  route.value = {
    x: Number(inputX.value),
    z: Number(inputZ.value),
  };
};

const cleanRoute = () => {
  route.value = null;
};

// ================= KEY =================
const onKey = (e) => {
  if (e.key === "Escape") close();
};

// ================= CANVAS SETUP (FIX DPI + PROPORTION) =================
const resizeCanvas = () => {
  const canvas = canvasRef.value;
  const container = containerRef.value;

  if (!canvas || !container) return;

  const rect = container.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;

  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;

  canvas.style.width = rect.width + "px";
  canvas.style.height = rect.height + "px";

  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
};

// ================= DRAW =================
const draw = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  const w = canvas.clientWidth;
  const h = canvas.clientHeight;

  ctx.clearRect(0, 0, w, h);

  // background
  ctx.fillStyle = "#050505";
  ctx.fillRect(0, 0, w, h);

  const cx = w / 2;
  const cy = h / 2;

  // GRID (leve e proporcional)
  ctx.strokeStyle = "rgba(0,255,156,0.06)";
  ctx.lineWidth = 1;

  const gridSize = 60 * scale.value;

  const offsetX = cx % gridSize;
  const offsetY = cy % gridSize;

  for (let x = offsetX; x < w; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }

  for (let y = offsetY; y < h; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  // AVIÃO (centro)
  ctx.fillStyle = "#00ff9c";
  ctx.beginPath();
  ctx.arc(cx, cy, 5, 0, Math.PI * 2);
  ctx.fill();

  ctx.strokeStyle = "#00ff9c55";
  ctx.beginPath();
  ctx.arc(cx, cy, 14, 0, Math.PI * 2);
  ctx.stroke();

  // ROUTE LINE (preview simples)
  if (route.value) {
    ctx.strokeStyle = "#00ff9c";
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(cx, cy);

    // escala fake (visual only por enquanto)
    const dx = (route.value.x - position.value.x) * 2;
    const dz = (route.value.z - position.value.z) * 2;

    ctx.lineTo(cx + dx, cy + dz);
    ctx.stroke();

    // target
    ctx.fillStyle = "#ff4444";
    ctx.beginPath();
    ctx.arc(cx + dx, cy + dz, 6, 0, Math.PI * 2);
    ctx.fill();
  }

  // TEXT
  ctx.fillStyle = "#00ff9c";
  ctx.font = "12px monospace";
  ctx.fillText(`X: ${position.value.x}`, 16, 22);
  ctx.fillText(`Z: ${position.value.z}`, 16, 40);
};

// ================= LOOP =================
let animation;

const loop = () => {
  draw();
  animation = requestAnimationFrame(loop);
};

// ================= LIFECYCLE =================
onMounted(() => {
  window.addEventListener("keydown", onKey);
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  loop();
});

onUnmounted(() => {
  window.removeEventListener("keydown", onKey);
  window.removeEventListener("resize", resizeCanvas);
  cancelAnimationFrame(animation);
});
</script>

<template>
  <div class="overlay" @click.self="close">
    <div class="tablet">
      <div class="topbar">
        <div class="title">NAVIGATION SYSTEM</div>
        <button class="close" @click="close">✕</button>
      </div>

      <div class="content">
        <!-- SIDEBAR -->
        <div class="sidebar">
          <div class="route-display">
            <div class="title-small">ACTIVE ROUTE</div>

            <div v-if="route" class="coords">
              X: {{ route.x }}<br />
              Z: {{ route.z }}
            </div>

            <div v-else class="coords off">NO ROUTE</div>
          </div>

          <div class="inputs">
            <label>X</label>
            <input v-model="inputX" type="number" />

            <label>Z</label>
            <input v-model="inputZ" type="number" />
          </div>

          <button class="btn define" @click="defineRoute">DEFINE ROUTE</button>

          <button class="btn clean" @click="cleanRoute">CLEAN ROUTE</button>
        </div>

        <!-- MAP -->
        <div class="map-area" ref="containerRef">
          <canvas ref="canvasRef"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.tablet {
  width: 70vw;
  height: 75vh;
  background: #0a0a0a;
  border: 1px solid #2a2a2a;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
}

.topbar {
  height: 44px;
  background: #0b0b0b;
  border-bottom: 1px solid #1f1f1f;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 12px;
  color: #00ff9c;
  font-family: monospace;
}

.content {
  flex: 1;
  display: flex;
}

.sidebar {
  width: 200px;
  background: #0a0a0a;
  border-right: 1px solid #1f1f1f;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-family: monospace;
}

.route-display {
  border: 1px solid #1f1f1f;
  padding: 8px;
  color: #00ff9c;
}

.title-small {
  font-size: 10px;
  opacity: 0.6;
  margin-bottom: 6px;
}

.coords {
  font-size: 12px;
}

.coords.off {
  color: #555;
}

.inputs {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.inputs label {
  font-size: 10px;
  color: #888;
}

.inputs input {
  background: #111;
  border: 1px solid #333;
  color: #00ff9c;
  padding: 6px;
  font-family: monospace;
}

.btn {
  padding: 8px;
  font-size: 11px;
  font-family: monospace;
  cursor: pointer;
}

.define {
  background: #0f1f1a;
  border: 1px solid #00ff9c;
  color: #00ff9c;
}

.clean {
  background: #1a0f0f;
  border: 1px solid #ff4444;
  color: #ff4444;
}

.map-area {
  flex: 1;
  background: #050505;
}

canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
