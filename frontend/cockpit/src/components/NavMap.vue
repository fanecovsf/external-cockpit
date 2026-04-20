<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const emit = defineEmits(["close"]);

const canvasRef = ref(null);
const containerRef = ref(null);

const camera = ref({
  x: 0,
  z: 0,
});

const isDragging = ref(false);
const lastMouse = ref({ x: 0, y: 0 });

// ================= STATE =================
const position = ref({ x: 0, z: 0 });

const route = ref(null);
const inputX = ref(0);
const inputZ = ref(0);

const scale = ref(0.5);

// ================= MAP DATA =================
const chunks = ref([]); // vindo do backend

const worldPath = ref("");

// ================= BACKEND URL =================
const API = "http://localhost:8000";

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

const getChunkColor = (chunk) => {
  const type = chunk.type || "";

  switch (type) {
    case "water":
      return "#2b6fff";

    case "sand":
      return "#d9c58a";

    case "snow":
      return "#ffffff";

    case "rock":
    case "stone":
      return "#7a7a7a";

    case "land":
      return "#2ecc71";

    case "mountain":
      return "#9b7b5b";

    default:
      // fallback baseado no bloco
      if (chunk.topBlock?.includes("water")) return "#2b6fff";
      if (chunk.topBlock?.includes("sand")) return "#d9c58a";
      if (chunk.topBlock?.includes("stone")) return "#7a7a7a";
      if (chunk.topBlock?.includes("grass") || chunk.topBlock?.includes("dirt"))
        return "#2ecc71";

      return "#1f1f1f";
  }
};

// ================= IMPORT MAP (CALL BACKEND) =================
const importMap = async () => {
  try {
    const res = await fetch(`${API}/map/load`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        path: worldPath.value || "/minecraft/saves/world",
      }),
    });

    const data = await res.json();
    console.log("Map loaded:", data);
  } catch (err) {
    console.error("Error loading map:", err);
  }
};

// ================= LOAD MAP (GET CHUNKS) =================
const loadMap = async () => {
  try {
    const res = await fetch(`${API}/map`);
    const data = await res.json();

    chunks.value = data || [];
  } catch (err) {
    console.error("Error fetching map:", err);
  }
};

// ================= CLEAR MAP =================
const clearMap = () => {
  chunks.value = [];
};

// ================= CLOSE =================
const close = () => emit("close");

const onKey = (e) => {
  if (e.key === "Escape") close();
};

// ================= RESIZE =================
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

  const w = canvas.width / (window.devicePixelRatio || 1);
  const h = canvas.height / (window.devicePixelRatio || 1);

  ctx.clearRect(0, 0, w, h);

  // background
  ctx.fillStyle = "#050505";
  ctx.fillRect(0, 0, w, h);

  const cx = w / 2 - camera.value.x;
  const cy = h / 2 - camera.value.z;

  // GRID
  ctx.strokeStyle = "rgba(0,255,156,0.06)";
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

  // ================= CHUNKS (FROM BACKEND) =================
  const baseChunkSize = 8;
  for (const chunk of chunks.value) {
    const color = getChunkColor(chunk);

    const size = baseChunkSize * scale.value;

    const x = cx + chunk.chunkX * size;
    const z = cy + chunk.chunkZ * size;

    ctx.fillStyle = color;
    ctx.fillRect(x, z, size, size);

    ctx.strokeStyle = "rgba(0,0,0,0.25)";
    ctx.strokeRect(x, z, size, size);
  }

  // AIRCRAFT
  ctx.fillStyle = "#00ff9c";
  ctx.beginPath();
  ctx.arc(cx, cy, 5, 0, Math.PI * 2);
  ctx.fill();

  // ROUTE
  const size = baseChunkSize * scale.value;
  if (route.value) {
    const dx = (route.value.x - position.value.x) * size;
    const dz = (route.value.z - position.value.z) * size;

    ctx.strokeStyle = "#00ff9c";
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + dx, cy + dz);
    ctx.stroke();

    ctx.fillStyle = "#ff4444";
    ctx.beginPath();
    ctx.arc(cx + dx, cy + dz, 6, 0, Math.PI * 2);
    ctx.fill();
  }
};

// ================= LOOP =================
let animation;

const loop = () => {
  draw();
  animation = requestAnimationFrame(loop);
};

// ================= LIFE =================
onMounted(() => {
  window.addEventListener("keydown", onKey);
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  const canvas = canvasRef.value;

  canvas.addEventListener("mousedown", onMouseDown);
  window.addEventListener("mousemove", onMouseMove);
  window.addEventListener("mouseup", onMouseUp);
  canvas.addEventListener("wheel", onWheel, { passive: true });

  loop();
});

onUnmounted(() => {
  window.removeEventListener("keydown", onKey);
  window.removeEventListener("resize", resizeCanvas);
  cancelAnimationFrame(animation);

  const canvas = canvasRef.value;

  if (canvas) {
    canvas.removeEventListener("mousedown", onMouseDown);
    canvas.removeEventListener("wheel", onWheel);
  }

  window.removeEventListener("mousemove", onMouseMove);
  window.removeEventListener("mouseup", onMouseUp);
});

const onWheel = (e) => {
  const zoomIntensity = 0.001;

  const newScale = scale.value * (1 - e.deltaY * zoomIntensity);

  scale.value = Math.min(5, Math.max(0.05, newScale));
};

const onMouseDown = (e) => {
  isDragging.value = true;
  lastMouse.value = { x: e.clientX, y: e.clientY };
};

const onMouseMove = (e) => {
  if (!isDragging.value) return;

  const dx = e.clientX - lastMouse.value.x;
  const dy = e.clientY - lastMouse.value.y;

  camera.value.x -= dx;
  camera.value.z -= dy;

  lastMouse.value = { x: e.clientX, y: e.clientY };
};

const onMouseUp = () => {
  isDragging.value = false;
};
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
          <input v-model="worldPath" placeholder="world path..." />

          <button class="btn import" @click="importMap">IMPORT MAP</button>

          <button class="btn" @click="loadMap">LOAD MAP</button>

          <button class="btn clean" @click="clearMap">CLEAR MAP</button>

          <div class="route-display">
            <div v-if="route">ROUTE: {{ route.x }} / {{ route.z }}</div>
            <div v-else>NO ROUTE</div>
          </div>

          <input v-model="inputX" placeholder="X" />
          <input v-model="inputZ" placeholder="Z" />

          <button class="btn define" @click="defineRoute">SET ROUTE</button>

          <button class="btn clean" @click="cleanRoute">REMOVE ROUTE</button>
        </div>

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
