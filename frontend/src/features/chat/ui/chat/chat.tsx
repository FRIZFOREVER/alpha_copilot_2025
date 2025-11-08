import { ChatHeader } from "../chatHeader";
import { MessageList, type MessageData } from "../messageList";
import { ChatInput } from "../chatInput";

export interface ChatProps {
  messages?: MessageData[];
  onSendMessage?: (message: string) => void;
  isLoading?: boolean;
}

export const Chat = ({
  messages = [],
  onSendMessage,
  isLoading = false,
}: ChatProps) => {
  return (
    <div className="flex h-full flex-col bg-white overflow-hidden">
      <ChatHeader />
      <div className="flex-1 overflow-hidden flex justify-center">
        <MessageList messages={messages} />
      </div>
      <ChatInput onSend={onSendMessage} disabled={isLoading} />
    </div>
  );
};
