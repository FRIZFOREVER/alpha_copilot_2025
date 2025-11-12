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
}

const ChatCollapseContext = createContext<ChatCollapseContextType | undefined>(
  undefined
);

const STORAGE_KEY = "chat-collapsed";
const MINIMIZED_CHAT_VISIBLE_KEY = "minimized-chat-visible";

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

  return (
    <ChatCollapseContext.Provider
      value={{
        isCollapsed,
        isMinimizedChatVisible,
        toggleCollapse,
        setCollapsed,
        setMinimizedChatVisible,
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
