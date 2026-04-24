export const wsUrl =
  process.env.NODE_ENV === "production"
    ? "ws://localhost:1337/ws"
    : "ws://localhost:1337/ws";
