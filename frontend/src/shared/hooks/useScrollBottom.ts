import { useLayoutEffect, useRef, useEffect } from "react";

export const useScrollBottom = <T>(deps: Array<T>) => {
  const contentRef = useRef<HTMLDivElement>(null);

  // Функция для поиска элемента со скроллом
  const findScrollContainer = (): HTMLElement | null => {
    if (!contentRef.current) return null;

    // Для ScrollArea: структура div > div (внутренний div имеет overflow-auto)
    // Берем первый дочерний элемент - это скроллируемый контейнер
    const firstChild = contentRef.current.firstElementChild as HTMLElement;

    if (firstChild) {
      return firstChild;
    }

    // Fallback: если контейнер сам имеет скролл
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

  // Функция скролла вниз с плавной анимацией
  const scrollToBottom = (retryCount = 0) => {
    const scrollContainer = findScrollContainer();
    if (!scrollContainer) {
      // Если контейнер еще не найден, пробуем еще раз
      if (retryCount < 15) {
        setTimeout(() => scrollToBottom(retryCount + 1), 50);
      }
      return;
    }

    const scrollHeight = scrollContainer.scrollHeight;

    // Скроллим вниз до максимальной позиции с плавной анимацией
    if (scrollHeight > 0) {
      scrollContainer.scrollTo({
        top: scrollHeight,
        behavior: "smooth",
      });
    }

    // Дополнительная проверка через небольшую задержку на случай, если контент еще загружается
    if (retryCount < 10) {
      const delay = retryCount < 3 ? 100 : retryCount < 6 ? 200 : 300;
      setTimeout(() => {
        const newScrollHeight = scrollContainer.scrollHeight;
        // Если высота контента изменилась, продолжаем скроллить
        if (newScrollHeight !== scrollHeight || retryCount < 3) {
          scrollToBottom(retryCount + 1);
        }
      }, delay);
    }
  };

  // Используем useLayoutEffect для синхронного скролла перед отрисовкой
  useLayoutEffect(() => {
    // Используем requestAnimationFrame для гарантии, что DOM обновлен
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        scrollToBottom(0);
      });
    });

    // Дополнительные попытки для асинхронно загружаемого контента
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

  // Дополнительный эффект для обработки случаев, когда контент загружается после первого рендера
  useEffect(() => {
    // Небольшая задержка для обработки асинхронно загружаемого контента
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
