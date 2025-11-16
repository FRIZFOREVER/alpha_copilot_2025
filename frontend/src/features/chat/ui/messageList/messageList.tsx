import { ScrollArea } from "@/shared/ui/scroll-area";
import { Message } from "../message";
import { ChatEmptyState } from "../chatEmptyState";
import { useScrollBottom } from "@/shared/hooks/useScrollBottom";
import { cn } from "@/shared/lib/mergeClass";
import { useEffect } from "react";
import type { MessageData } from "@/shared/types/message";
import { useChatScroll } from "../../hooks/useChatScroll";

export interface MessageListProps {
  messages: MessageData[];
  isLoading?: boolean;
  isCompact?: boolean;
  onScrollContainerReady?: (ref: React.RefObject<HTMLElement>) => void;
  onScrollStateChange?: (
    isAtBottom: boolean,
    scrollToBottom: () => void
  ) => void;
}

export const MessageList = ({
  messages,
  isLoading = false,
  isCompact = false,
  onScrollContainerReady,
  onScrollStateChange,
}: MessageListProps) => {
  const lastMessage = messages[messages.length - 1];

  const { contentRef } = useScrollBottom([
    messages.length,
    lastMessage?.id,
    lastMessage && !lastMessage.isUser ? lastMessage.content.length : 0,
    isLoading ? "loading" : "loaded",
  ]);

  const { isAtBottom, scrollToBottom } = useChatScroll({
    channelId: "chat",
    chatRef: contentRef,
  });

  useEffect(() => {
    if (onScrollStateChange) {
      onScrollStateChange(isAtBottom, scrollToBottom);
    }
  }, [isAtBottom, scrollToBottom, onScrollStateChange]);

  useEffect(() => {
    if (onScrollContainerReady && contentRef.current) {
      const scrollContainer = contentRef.current
        .firstElementChild as HTMLElement;
      if (scrollContainer) {
        const containerRef = {
          current: scrollContainer,
        } as React.RefObject<HTMLElement>;
        onScrollContainerReady(containerRef);
      }
    }
  }, [onScrollContainerReady, contentRef]);

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
              answerId={message.isUser ? undefined : message.answerId}
              rating={message.isUser ? undefined : message.rating}
              isTyping={message.isUser ? undefined : message.isTyping}
              tag={message.tag}
              file_url={message.isUser ? message.file_url : undefined}
            />
          ))
        )}
      </div>
    </ScrollArea>
  );
};
