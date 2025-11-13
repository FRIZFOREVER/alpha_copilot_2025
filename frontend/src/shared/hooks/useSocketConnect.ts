import { useEffect } from "react";
import { useSocket } from "@/entities/socket/model/context";
import { getAccessToken } from "@/entities/token/lib/tokenService";

export const useSocketConnect = () => {
  const { connectionSocket, isConnected, socket } = useSocket();

  useEffect(() => {
    if (typeof window === "undefined") return;

    const accessToken = getAccessToken();

    if (!isConnected) {
      connectionSocket({
        url: `/${crypto.randomUUID()}?access_token=${accessToken}`,
      });
    }

    if (socket instanceof WebSocket) {
      socket.onclose = () => {
        connectionSocket({
          url: `/${crypto.randomUUID()}?access_token=${accessToken}`,
        });
      };
    }

    return () => {
      if (socket instanceof WebSocket) {
        socket.onclose = null;
      }
    };
  }, [isConnected, socket, connectionSocket]);
};