import { Chat } from "@/features/chat";
import { useChatMessages } from "@/features/chat/hooks/useChatMessages";

const CopilotChatPage = () => {
  const {
    messages,
    handleSendMessage,
    handleSendVoice,
    isLoading,
    suggestions,
  } = useChatMessages();

  // Подключение к graph_log WebSocket происходит на уровне DashboardPage
  // Это обеспечивает единое подключение для всех компонентов чата

  return (
    <Chat
      messages={messages}
      onSendMessage={handleSendMessage}
      onSendVoice={handleSendVoice}
      isLoading={isLoading}
      suggestions={suggestions}
    />
  );
};
export default CopilotChatPage;
