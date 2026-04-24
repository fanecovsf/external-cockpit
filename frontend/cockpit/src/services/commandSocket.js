let commandSocket = null;

export const connectCommands = () => {
  commandSocket = new WebSocket("ws://localhost:8000/ws/commands");
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
