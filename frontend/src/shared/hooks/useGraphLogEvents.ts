import { useEffect } from "react";
import { useSocket } from "@/entities/socket/model/context";
import { GraphLogWebSocketMessage } from "@/entities/chat/types/types";

export interface GraphLogMessage {
  message?: string;
  type?: string;
  uuid?: string;
}

export const useGraphLogEvents = (
  onMessage?: (data: GraphLogWebSocketMessage) => void,
  onConnectionEstablished?: (uuid: string) => void
) => {
  const { graphLogSocket } = useSocket();

  useEffect(() => {
    if (!graphLogSocket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const parsedData = JSON.parse(event.data);

        if (parsedData.type === "connection_established" && parsedData.uuid) {
          onConnectionEstablished?.(parsedData.uuid);
          return;
        }

        if (
          parsedData.tag &&
          parsedData.answer_id !== undefined &&
          parsedData.message
        ) {
          const graphLogMessage = parsedData as GraphLogWebSocketMessage;
          onMessage?.(graphLogMessage);
          return;
        }

        if (parsedData.message) {
          onMessage?.(parsedData as unknown as GraphLogWebSocketMessage);
        }
      } catch (error) {
        console.error("Ошибка при парсинге сообщения graph_log:", error);
      }
    };

    graphLogSocket.addEventListener("message", handleMessage);

    return () => {
      graphLogSocket.removeEventListener("message", handleMessage);
    };
  }, [graphLogSocket, onMessage, onConnectionEstablished]);
};
