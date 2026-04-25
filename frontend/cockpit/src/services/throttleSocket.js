import { wsUrl } from "../utils/wsUrl";

let telemetrySocket = null;

export const connectThrottleTelemetry = (onMessage) => {
  telemetrySocket = new WebSocket(wsUrl + "/throttle-telemetry");

  telemetrySocket.onopen = () => {
    console.log("🟢 Throttle Telemetry connected");
  };

  telemetrySocket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage?.(data);
    } catch (e) {
      console.log("telemetrySocket parse error", e);
    }
  };

  telemetrySocket.onclose = () => {
    setTimeout(() => connectThrottleTelemetry(onMessage), 2000);
  };
};

export const disconnectThrottleTelemetry = () => {
  if (telemetrySocket) {
    telemetrySocket.close();
    telemetrySocket = null;
  }
};
