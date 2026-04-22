// services/throttleSocket.js
let telemetrySocket = null;
let commandSocket = null;

export const connectThrottleTelemetry = (onMessage) => {
  telemetrySocket = new WebSocket("ws://localhost:8000/ws/throttle-telemetry");

  telemetrySocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
};

export const disconnectThrottleTelemetry = () => {
  if (telemetrySocket) {
    telemetrySocket.close();
    telemetrySocket = null;
  }
};

export const connectThrottleCommands = () => {
  commandSocket = new WebSocket("ws://localhost:8000/ws/throttle-commands");
};

export const sendThrottleCommand = (data) => {
  if (commandSocket && commandSocket.readyState === 1) {
    commandSocket.send(JSON.stringify(data));
  }
};

export const disconnectThrottleCommands = () => {
  if (commandSocket) {
    commandSocket.close();
    commandSocket = null;
  }
};
