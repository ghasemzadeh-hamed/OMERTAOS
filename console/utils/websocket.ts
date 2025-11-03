let socket: WebSocket | null = null;

export const createWebSocket = () => {
  if (typeof window === "undefined") {
    throw new Error("websocket unavailable during server-side rendering");
  }
  if (socket && socket.readyState === WebSocket.OPEN) {
    return socket;
  }
  socket = new WebSocket(process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8080/ws");
  socket.onopen = () => {
    console.info("websocket connected");
  };
  socket.onerror = (event) => {
    console.error("websocket error", event);
  };
  return socket;
};
