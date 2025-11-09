import { ScrollArea } from "@/shared/ui/scroll-area";
import { Message } from "../message";
import { ChatEmptyState } from "../chatEmptyState";

export interface MessageData {
  id: string;
  content: string;
  isUser: boolean;
  timestamp?: string;
  answerId?: number;
  rating?: number | null;
  isTyping?: boolean;
}

export interface MessageListProps {
  messages: MessageData[];
}

export const MessageList = ({ messages }: MessageListProps) => {
  return (
    <ScrollArea className="flex-1 max-w-[832px]">
      <div>
        {messages.length === 0 ? (
          <ChatEmptyState />
        ) : (
          messages.map((message) => (
            <Message
              key={message.id}
              content={message.content}
              isUser={message.isUser}
              answerId={message.answerId}
              rating={message.rating}
              isTyping={message.isTyping}
            />
          ))
        )}
      </div>
    </ScrollArea>
  );
};
