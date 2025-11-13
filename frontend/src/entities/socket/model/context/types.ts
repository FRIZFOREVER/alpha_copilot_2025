export interface SocketState {
  socket: WebSocket | null;
  isConnected: boolean;
  error: string;
}

export interface SocketHandler {
  connectionSocket: (params: { url: string }) => Promise<void>;
  setWebSocket: (socket: WebSocket) => void;
}

