import { wsUrl } from "../utils/wsUrl";

let telemetrySocket = null;
let commandSocket = null;

export const connectThrottleTelemetry = (onMessage) => {
  telemetrySocket = new WebSocket(wsUrl + "/throttle-telemetry");

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
  commandSocket = new WebSocket(wsUrl + "/throttle-commands");
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
