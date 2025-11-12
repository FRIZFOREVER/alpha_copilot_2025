import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

interface ChatCollapseContextType {
  isCollapsed: boolean;
  isMinimizedChatVisible: boolean;
  toggleCollapse: () => void;
  setCollapsed: (collapsed: boolean) => void;
  setMinimizedChatVisible: (visible: boolean) => void;
  resetChatState: () => void;
}

const ChatCollapseContext = createContext<ChatCollapseContextType | undefined>(
  undefined
);

export const STORAGE_KEY = "chat-collapsed";
export const MINIMIZED_CHAT_VISIBLE_KEY = "minimized-chat-visible";

export const ChatCollapseProvider = ({ children }: { children: ReactNode }) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored !== null ? stored === "true" : true;
    }
    return true;
  });

  const [isMinimizedChatVisible, setIsMinimizedChatVisible] = useState<boolean>(
    () => {
      if (typeof window !== "undefined") {
        const stored = localStorage.getItem(MINIMIZED_CHAT_VISIBLE_KEY);
        return stored !== null ? stored === "true" : false;
      }
      return false;
    }
  );

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(isCollapsed));
  }, [isCollapsed]);

  useEffect(() => {
    localStorage.setItem(
      MINIMIZED_CHAT_VISIBLE_KEY,
      String(isMinimizedChatVisible)
    );
  }, [isMinimizedChatVisible]);

  const toggleCollapse = () => {
    setIsCollapsed((prev) => !prev);
  };

  const setCollapsed = (collapsed: boolean) => {
    setIsCollapsed(collapsed);
  };

  const setMinimizedChatVisible = (visible: boolean) => {
    setIsMinimizedChatVisible(visible);
  };

  const resetChatState = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(MINIMIZED_CHAT_VISIBLE_KEY);
    }
    setIsCollapsed(true);
    setIsMinimizedChatVisible(false);
  };

  // Синхронизация с localStorage при монтировании
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedCollapsed = localStorage.getItem(STORAGE_KEY);
      const storedMinimized = localStorage.getItem(MINIMIZED_CHAT_VISIBLE_KEY);

      // Если ключей нет в localStorage, сбрасываем состояние к значениям по умолчанию
      if (storedCollapsed === null) {
        setIsCollapsed(true);
      }
      if (storedMinimized === null) {
        setIsMinimizedChatVisible(false);
      }
    }
  }, []);

  return (
    <ChatCollapseContext.Provider
      value={{
        isCollapsed,
        isMinimizedChatVisible,
        toggleCollapse,
        setCollapsed,
        setMinimizedChatVisible,
        resetChatState,
      }}
    >
      {children}
    </ChatCollapseContext.Provider>
  );
};

export const useChatCollapse = () => {
  const context = useContext(ChatCollapseContext);
  if (context === undefined) {
    throw new Error("useChatCollapse must be used within ChatCollapseProvider");
  }
  return context;
};
