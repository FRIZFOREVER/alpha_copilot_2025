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
        console.log("useGraphLogEvents: Распарсенные данные:", parsedData);

        if (parsedData.type === "connection_established" && parsedData.uuid) {
          console.log(
            "useGraphLogEvents: Подключение установлено, UUID:",
            parsedData.uuid
          );
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
          console.log(
            "useGraphLogEvents: Сообщение в старом формате:",
            parsedData
          );
          onMessage?.(parsedData as unknown as GraphLogWebSocketMessage);
        } else {
          console.log(
            "useGraphLogEvents: Неизвестный формат сообщения:",
            parsedData
          );
        }
      } catch (error) {
        console.error(
          "Ошибка при парсинге сообщения graph_log:",
          error,
          event.data
        );
      }
    };

    graphLogSocket.addEventListener("message", handleMessage);

    return () => {
      graphLogSocket.removeEventListener("message", handleMessage);
    };
  }, [graphLogSocket, onMessage, onConnectionEstablished]);
};
