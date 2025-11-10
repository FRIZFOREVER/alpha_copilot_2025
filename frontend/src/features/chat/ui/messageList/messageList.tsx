import { ScrollArea } from "@/shared/ui/scroll-area";
import { Message } from "../message";
import { ChatEmptyState } from "../chatEmptyState";
import { useScrollBottom } from "@/shared/hooks/useScrollBottom";
import { cn } from "@/shared/lib/mergeClass";

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
  isLoading?: boolean;
}

export const MessageList = ({
  messages,
  isLoading = false,
}: MessageListProps) => {
  const { contentRef } = useScrollBottom([
    messages.length,
    messages[messages.length - 1]?.id,
    isLoading ? "loading" : "loaded",
  ]);
  return (
    <ScrollArea className="flex-1 max-w-[832px]" ref={contentRef}>
      <div
        className={cn(
          messages.length === 0 && "h-full flex items-center justify-center"
        )}
      >
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
