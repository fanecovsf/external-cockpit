import { wsUrl } from "../utils/wsUrl";

let commandSocket = null;

export const connectCommands = (onMessage) => {
  commandSocket = new WebSocket(wsUrl + "/commands");

  commandSocket.onopen = () => {
    console.log("🟢 Commands connected");
  };

  commandSocket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage?.(data);
    } catch (e) {
      console.log("commandSocket parse error", e);
    }
  };

  commandSocket.onclose = () => {
    setTimeout(() => connectCommands(onMessage), 2000);
  };
};

export const sendCommand = (data) => {
  if (commandSocket && commandSocket.readyState === 1) {
    commandSocket.send(JSON.stringify(data));
  }
};

export const disconnectCommands = () => {
  if (commandSocket) {
    commandSocket.close();
    commandSocket = null;
  }
};
