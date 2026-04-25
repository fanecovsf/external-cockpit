export const wsUrl =
  process.env.NODE_ENV === "production"
    ? "ws://192.168.15.9:1337/ws"
    : "ws://localhost:1337/ws";
