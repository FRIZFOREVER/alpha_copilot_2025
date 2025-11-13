export interface SocketState {
  socket: WebSocket | null;
  isConnected: boolean;
  error: string;
  graphLogSocket: WebSocket | null;
  isGraphLogConnected: boolean;
  graphLogError: string;
}

export interface SocketHandler {
  connectionSocket: (params: { url: string }) => Promise<void>;
  setWebSocket: (socket: WebSocket) => void;
  connectGraphLog: (params: { chatId: number; token: string }) => Promise<void>;
  disconnectGraphLog: () => void;
}
