import { ScrollArea } from "@/shared/ui/scroll-area";
import { Message } from "../message";
import { ChatEmptyState } from "../chatEmptyState";
import { useScrollBottom } from "@/shared/hooks/useScrollBottom";
import { cn } from "@/shared/lib/mergeClass";
import { useEffect } from "react";

export interface MessageData {
  id: string;
  content: string;
  isUser: boolean;
  timestamp?: string;
  answerId?: number;
  rating?: number | null;
  isTyping?: boolean;
  file_url?: string;
  tag: string;
}

export interface MessageListProps {
  messages: MessageData[];
  isLoading?: boolean;
  isCompact?: boolean;
}

export const MessageList = ({
  messages,
  isLoading = false,
  isCompact = false,
}: MessageListProps) => {
  const lastMessage = messages[messages.length - 1];

  const { contentRef } = useScrollBottom([
    messages.length,
    lastMessage?.id,
    lastMessage && !lastMessage.isUser ? lastMessage.content.length : 0,
    isLoading ? "loading" : "loaded",
  ]);

  useEffect(() => {
    if (!lastMessage || lastMessage.isUser) return;

    const scrollArea = contentRef.current;
    if (!scrollArea) return;

    const scrollContainer = scrollArea.firstElementChild as HTMLElement;
    if (!scrollContainer) return;

    const scrollToBottom = () => {
      scrollContainer.scrollTo({
        top: scrollContainer.scrollHeight,
        behavior: "smooth",
      });
    };

    const rafId = requestAnimationFrame(() => {
      requestAnimationFrame(scrollToBottom);
    });

    return () => cancelAnimationFrame(rafId);
  }, [lastMessage?.content, lastMessage?.isUser, contentRef]);

  return (
    <ScrollArea className="flex-1 max-w-[832px]" ref={contentRef}>
      <div
        className={cn(
          messages.length === 0 && "h-full flex items-center justify-center"
        )}
      >
        {messages.length === 0 ? (
          <ChatEmptyState isCompact={isCompact} />
        ) : (
          messages.map((message) => (
            <Message
              key={message.id}
              isCompact={isCompact}
              content={message.content}
              isUser={message.isUser}
              answerId={message.answerId}
              rating={message.rating}
              isTyping={message.isTyping}
              tag={message.tag}
              file_url={message.file_url}
            />
          ))
        )}
      </div>
    </ScrollArea>
  );
};
