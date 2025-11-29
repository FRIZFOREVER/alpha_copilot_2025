import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useCallback,
  useMemo,
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

const getInitialCollapsed = (): boolean => {
  if (typeof window === "undefined") return true;
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored !== null ? stored === "true" : true;
};

const getInitialMinimized = (): boolean => {
  if (typeof window === "undefined") return false;
  const stored = localStorage.getItem(MINIMIZED_CHAT_VISIBLE_KEY);
  return stored !== null ? stored === "true" : true;
};

export const ChatCollapseProvider = ({ children }: { children: ReactNode }) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(getInitialCollapsed);
  const [isMinimizedChatVisible, setIsMinimizedChatVisible] =
    useState<boolean>(getInitialMinimized);

  const toggleCollapse = useCallback(() => {
    setIsCollapsed((prev) => !prev);
  }, []);

  const setCollapsed = useCallback((collapsed: boolean) => {
    setIsCollapsed(collapsed);
  }, []);

  const setMinimizedChatVisible = useCallback((visible: boolean) => {
    setIsMinimizedChatVisible(visible);
  }, []);

  const resetChatState = useCallback(() => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(MINIMIZED_CHAT_VISIBLE_KEY);
    }
    setIsCollapsed(true);
    setIsMinimizedChatVisible(false);
  }, []);

  const value = useMemo<ChatCollapseContextType>(
    () => ({
      isCollapsed,
      isMinimizedChatVisible,
      toggleCollapse,
      setCollapsed,
      setMinimizedChatVisible,
      resetChatState,
    }),
    [
      isCollapsed,
      isMinimizedChatVisible,
      toggleCollapse,
      setCollapsed,
      setMinimizedChatVisible,
      resetChatState,
    ]
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

  useEffect(() => {
    if (typeof window === "undefined") return;

    const storedCollapsed = localStorage.getItem(STORAGE_KEY);

    if (storedCollapsed === null) {
      setIsCollapsed(true);
    }
    // Убрана логика для minimized, так как getInitialMinimized уже устанавливает правильное значение
  }, []);

  return (
    <ChatCollapseContext.Provider value={value}>
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
