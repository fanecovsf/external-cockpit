let socket = null;
let retryTimeout = null;
let latestTelemetry = null;

export const connectTelemetry = (onMessage) => {
  socket = new WebSocket("ws://localhost:8000/ws/telemetry");

  socket.onopen = () => {
    console.log("🟢 Telemetry connected");
  };

  socket.onmessage = (event) => {
    latestTelemetry = JSON.parse(event.data);
  };

  socket.onclose = () => {
    console.warn("🔁 Tentando reconectar...");

    retryTimeout = setTimeout(() => {
      connectTelemetry(onMessage);
    }, 2000);
  };
};

export const disconnectTelemetry = () => {
  if (retryTimeout) clearTimeout(retryTimeout);

  if (socket) {
    socket.close();
    socket = null;
  }
};

export const getLatestTelemetry = () => {
  return latestTelemetry;
};
