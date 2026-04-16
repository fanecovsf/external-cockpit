let socket = null;
let retryTimeout = null;

export const connectTelemetry = (onMessage) => {
  socket = new WebSocket("ws://localhost:8000/ws/telemetry");

  socket.onopen = () => {
    console.log("🟢 Telemetry connected");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (onMessage) {
      onMessage(data); // 🔥 ENTREGA NA HORA
    }
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
