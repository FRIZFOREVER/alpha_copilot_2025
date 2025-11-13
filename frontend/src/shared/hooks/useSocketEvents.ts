import { useEffect } from "react";
import { useSocket } from "@/entities/socket/model/context";

export const useWebSocketEvents = <T>(
  eventType: string,
  callback: (data: T) => void
) => {
  const { socket } = useSocket();

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const parsedData = JSON.parse(event.data);
        if (parsedData.event === eventType) {
          callback(parsedData);
        }
      } catch (error) {
        console.error("Ошибка при парсинге сообщения:", error);
      }
    };

    socket.addEventListener("message", handleMessage);

    return () => {
      socket.removeEventListener("message", handleMessage);
    };
  }, [socket, eventType, callback]);
};
