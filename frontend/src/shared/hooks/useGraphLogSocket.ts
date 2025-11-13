import { useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { useSocket } from "@/entities/socket/model/context";
import { getAccessToken } from "@/entities/token/lib/tokenService";

export const useGraphLogSocket = () => {
  const params = useParams<{ chatId?: string }>();
  const chatId = params.chatId ? Number(params.chatId) : null;
  const {
    connectGraphLog,
    disconnectGraphLog,
    graphLogSocket,
    isGraphLogConnected,
  } = useSocket();
  const prevChatIdRef = useRef<number | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const accessToken = getAccessToken();
    if (!accessToken) {
      console.warn("Токен доступа не найден для подключения к graph_log");
      return;
    }

    if (prevChatIdRef.current !== null && prevChatIdRef.current !== chatId) {
      disconnectGraphLog();
    }

    if (chatId && chatId !== prevChatIdRef.current) {
      connectGraphLog({ chatId, token: accessToken });
      prevChatIdRef.current = chatId;
    }

    return () => {
      if (chatId) {
        disconnectGraphLog();
        prevChatIdRef.current = null;
      }
    };
  }, [chatId, connectGraphLog, disconnectGraphLog]);

  return {
    graphLogSocket,
    isGraphLogConnected,
    chatId,
  };
};
