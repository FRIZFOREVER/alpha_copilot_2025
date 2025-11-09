import { Chat } from "@/features/chat";
import { useParams } from "react-router-dom";
import { useGetHistoryQuery } from "@/entities/chat/hooks/useGetHistory";
import { useSendMessageMutation } from "@/entities/chat/hooks/useSendMessage";

const CopilotChatPage = () => {
  const params = useParams<{ chatId?: string }>();
  const chatId = params.chatId ? parseInt(params.chatId, 10) : undefined;

  const { data: messages = [], isLoading: isLoadingHistory } =
    useGetHistoryQuery(chatId);
  const { mutate: sendMessage, isPending: isSendingMessage } =
    useSendMessageMutation();

  const handleSendMessage = (message: string) => {
    if (!chatId || !message.trim()) return;

    sendMessage({
      chatId,
      sendMessageDto: { question: message.trim() },
    });
  };

  return (
    <Chat
      messages={messages}
      onSendMessage={handleSendMessage}
      isLoading={isLoadingHistory || isSendingMessage}
    />
  );
};

export default CopilotChatPage;
