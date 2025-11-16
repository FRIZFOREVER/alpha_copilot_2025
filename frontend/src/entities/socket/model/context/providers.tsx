import {
  createContext,
  FC,
  PropsWithChildren,
  useContext,
  useState,
  useCallback,
} from "react";
import { SocketContext as SocketContextType } from "./types";

const SocketContext = createContext<SocketContextType>({
  socket: null,
  isConnected: false,
  error: "",
  graphLogSocket: null,
  isGraphLogConnected: false,
  graphLogError: "",
  connectionSocket: async () => {},
  setWebSocket: () => {},
  connectGraphLog: async () => {},
  disconnectGraphLog: () => {},
});

export const useSocket = () => {
  return useContext(SocketContext);
};

const WS_BASE_URL = "ws://localhost:8080";

export const SocketProvider: FC<PropsWithChildren> = ({ children }) => {
  const [state, setState] = useState<SocketState>({
    socket: null,
    isConnected: false,
    error: "",
    graphLogSocket: null,
    isGraphLogConnected: false,
    graphLogError: "",
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

  const connectGraphLog = useCallback(
    async ({ chatId, token }: { chatId: number; token: string }) => {
      try {
        setState((prev: SocketState) => {
          if (prev.graphLogSocket) {
            prev.graphLogSocket.close();
          }

          return {
            ...prev,
            isGraphLogConnected: false,
            graphLogError: "",
          };
        });

        const socket = new WebSocket(
          `${WS_BASE_URL}/graph_log/${chatId}?jwt=${encodeURIComponent(token)}`
        );

        socket.onopen = () => {
          setState((prev: SocketState) => ({
            ...prev,
            graphLogSocket: socket,
            isGraphLogConnected: true,
            graphLogError: "",
          }));
        };

        socket.onerror = () => {
          setState((prev: SocketState) => ({
            ...prev,
            graphLogError: "Ошибка подключения к graph_log",
            isGraphLogConnected: false,
          }));
        };

        socket.onclose = () => {
          setState((prev: SocketState) => ({
            ...prev,
            graphLogSocket: null,
            isGraphLogConnected: false,
          }));
        };
      } catch (err) {
        setState((prev: SocketState) => ({
          ...prev,
          graphLogError: `${err}`,
          isGraphLogConnected: false,
        }));
      }
    },
    []
  );

  const disconnectGraphLog = useCallback(() => {
    setState((prev: SocketState) => {
      if (prev.graphLogSocket) {
        prev.graphLogSocket.close();
      }
      return {
        ...prev,
        graphLogSocket: null,
        isGraphLogConnected: false,
        graphLogError: "",
      };
    });
  }, []);

  return (
    <SocketContext.Provider
      value={{
        ...state,
        connectionSocket,
        setWebSocket,
        connectGraphLog,
        disconnectGraphLog,
      }}
    >
      {children}
    </SocketContext.Provider>
  );
};
