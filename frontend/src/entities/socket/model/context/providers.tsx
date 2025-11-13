import {
  createContext,
  FC,
  PropsWithChildren,
  useContext,
  useState,
  useCallback,
} from "react";
import { SocketState, SocketHandler } from "./types";

const SocketContext = createContext<SocketState & SocketHandler>({
  socket: null,
  isConnected: false,
  error: "",
  connectionSocket: async () => {},
  setWebSocket: () => {},
});

export const useSocket = () => {
  return useContext(SocketContext);
};

const WS_BASE_URL = "ws://89.104.68.181/api/v1/";

export const SocketProvider: FC<PropsWithChildren> = ({ children }) => {
  const [state, setState] = useState<SocketState>({
    socket: null,
    isConnected: false,
    error: "",
  });

  const connectionSocket = useCallback(async ({ url }: { url: string }) => {
    try {
      setState((prev: SocketState) => ({
        ...prev,
        isConnected: false,
        error: "",
      }));

      const socket = new WebSocket(`${WS_BASE_URL}${url}`);

      socket.onopen = () => {
        setState((prev: SocketState) => ({
          ...prev,
          socket,
          isConnected: true,
          error: "",
        }));
      };

      socket.onerror = () => {
        setState((prev: SocketState) => ({
          ...prev,
          error: "No connection",
          isConnected: false,
        }));
      };

      socket.onclose = () => {
        setState((prev: SocketState) => ({
          ...prev,
          socket: null,
          isConnected: false,
        }));
      };
    } catch (err) {
      setState((prev: SocketState) => ({
        ...prev,
        error: `${err}`,
        isConnected: false,
      }));
    }
  }, []);

  const setWebSocket = useCallback((socket: WebSocket) => {
    setState((prev: SocketState) => ({
      ...prev,
      socket,
    }));
  }, []);

  return (
    <SocketContext.Provider
      value={{
        ...state,
        connectionSocket,
        setWebSocket,
      }}
    >
      {children}
    </SocketContext.Provider>
  );
};

