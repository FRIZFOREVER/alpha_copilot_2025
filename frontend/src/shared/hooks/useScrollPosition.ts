import { useState, useEffect, useCallback } from "react";

interface UseScrollPositionOptions {
  threshold?: number;
}

export const useScrollPosition = (
  scrollContainerRef: React.RefObject<HTMLElement | null>,
  options: UseScrollPositionOptions = {}
) => {
  const { threshold = 100 } = options;
  const [isNearBottom, setIsNearBottom] = useState(true);
  const [showScrollButton, setShowScrollButton] = useState(false);

  const findScrollElement = useCallback((): HTMLElement | null => {
    if (!scrollContainerRef.current) return null;

    const firstChild = scrollContainerRef.current
      .firstElementChild as HTMLElement;
    if (firstChild) {
      return firstChild;
    }

    return scrollContainerRef.current;
  }, [scrollContainerRef]);

  const checkScrollPosition = useCallback(() => {
    const scrollElement = findScrollElement();
    if (!scrollElement) return;

    const { scrollTop, scrollHeight, clientHeight } = scrollElement;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
    const nearBottom = distanceFromBottom <= threshold;
    const shouldShowButton = distanceFromBottom > threshold;

    setIsNearBottom(nearBottom);
    setShowScrollButton(shouldShowButton);
  }, [findScrollElement, threshold]);

  useEffect(() => {
    const scrollElement = findScrollElement();
    if (!scrollElement) return;

    checkScrollPosition();

    scrollElement.addEventListener("scroll", checkScrollPosition, {
      passive: true,
    });

    const resizeObserver = new ResizeObserver(() => {
      checkScrollPosition();
    });

    resizeObserver.observe(scrollElement);

    return () => {
      scrollElement.removeEventListener("scroll", checkScrollPosition);
      resizeObserver.disconnect();
    };
  }, [findScrollElement, checkScrollPosition]);

  const scrollToBottom = useCallback(() => {
    const scrollElement = findScrollElement();
    if (!scrollElement) return;

    scrollElement.scrollTo({
      top: scrollElement.scrollHeight,
      behavior: "smooth",
    });
  }, [findScrollElement]);

  return {
    isNearBottom,
    showScrollButton,
    scrollToBottom,
  };
};
