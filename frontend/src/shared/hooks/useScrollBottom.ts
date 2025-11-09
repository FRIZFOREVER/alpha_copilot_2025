import { useLayoutEffect, useRef, useEffect } from "react";

export const useScrollBottom = <T>(deps: Array<T>) => {
  const contentRef = useRef<HTMLDivElement>(null);

  const findScrollContainer = (): HTMLElement | null => {
    if (!contentRef.current) return null;

    const firstChild = contentRef.current.firstElementChild as HTMLElement;

    if (firstChild) {
      return firstChild;
    }

    const style = window.getComputedStyle(contentRef.current);
    if (
      style.overflow === "auto" ||
      style.overflowY === "auto" ||
      style.overflow === "scroll" ||
      style.overflowY === "scroll"
    ) {
      return contentRef.current;
    }

    return contentRef.current;
  };

  const scrollToBottom = (retryCount = 0) => {
    const scrollContainer = findScrollContainer();
    if (!scrollContainer) {
      if (retryCount < 15) {
        setTimeout(() => scrollToBottom(retryCount + 1), 50);
      }
      return;
    }

    const scrollHeight = scrollContainer.scrollHeight;

    if (scrollHeight > 0) {
      scrollContainer.scrollTo({
        top: scrollHeight,
        behavior: "smooth",
      });
    }

    if (retryCount < 10) {
      const delay = retryCount < 3 ? 100 : retryCount < 6 ? 200 : 300;
      setTimeout(() => {
        const newScrollHeight = scrollContainer.scrollHeight;
        if (newScrollHeight !== scrollHeight || retryCount < 3) {
          scrollToBottom(retryCount + 1);
        }
      }, delay);
    }
  };

  useLayoutEffect(() => {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        scrollToBottom(0);
      });
    });

    const timeoutId1 = setTimeout(() => scrollToBottom(2), 100);
    const timeoutId2 = setTimeout(() => scrollToBottom(4), 300);
    const timeoutId3 = setTimeout(() => scrollToBottom(6), 500);
    const timeoutId4 = setTimeout(() => scrollToBottom(8), 800);

    return () => {
      clearTimeout(timeoutId1);
      clearTimeout(timeoutId2);
      clearTimeout(timeoutId3);
      clearTimeout(timeoutId4);
    };
  }, deps);

  useEffect(() => {
    const timeoutId1 = setTimeout(() => {
      scrollToBottom(0);
    }, 200);

    const timeoutId2 = setTimeout(() => {
      scrollToBottom(3);
    }, 600);

    return () => {
      clearTimeout(timeoutId1);
      clearTimeout(timeoutId2);
    };
  }, deps);

  return {
    contentRef,
  };
};
