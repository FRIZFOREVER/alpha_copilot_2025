import { RefObject, useCallback, useEffect, useState } from "react";

type ChatScrollProps = {
  chatRef: RefObject<HTMLDivElement | null>;
  channelId: string;
};

export const useChatScroll = ({ chatRef, channelId }: ChatScrollProps) => {
  const [isAtBottom, setIsAtBottom] = useState(true);

  const findScrollElement = useCallback((): HTMLElement | null => {
    if (!chatRef.current) return null;

    const firstChild = chatRef.current.firstElementChild as HTMLElement;
    if (firstChild) {
      return firstChild;
    }

    return chatRef.current;
  }, [chatRef]);

  const scrollToBottom = useCallback(() => {
    const scrollElement = findScrollElement();
    if (scrollElement) {
      scrollElement.scrollTo({
        top: scrollElement.scrollHeight,
        behavior: "smooth",
      });
      setIsAtBottom(true);
    }
  }, [findScrollElement]);

  useEffect(() => {
    const scrollElement = findScrollElement();
    if (!scrollElement) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = scrollElement;
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
      const isBottom = distanceFromBottom < 10;
      setIsAtBottom(isBottom);
    };

    handleScroll();

    scrollElement.addEventListener("scroll", handleScroll, { passive: true });

    const resizeObserver = new ResizeObserver(() => {
      handleScroll();
    });

    resizeObserver.observe(scrollElement);

    return () => {
      scrollElement.removeEventListener("scroll", handleScroll);
      resizeObserver.disconnect();
    };
  }, [findScrollElement, channelId]);

  return {
    isAtBottom,
    scrollToBottom,
  };
};
