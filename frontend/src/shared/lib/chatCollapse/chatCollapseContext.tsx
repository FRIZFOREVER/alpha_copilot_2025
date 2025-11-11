import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface ChatCollapseContextType {
  isCollapsed: boolean;
  toggleCollapse: () => void;
  setCollapsed: (collapsed: boolean) => void;
}

const ChatCollapseContext = createContext<ChatCollapseContextType | undefined>(
  undefined
);

const STORAGE_KEY = "chat-collapsed";

export const ChatCollapseProvider = ({ children }: { children: ReactNode }) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored === "true";
    }
    return false;
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(isCollapsed));
  }, [isCollapsed]);

  const toggleCollapse = () => {
    setIsCollapsed((prev) => !prev);
  };

  const setCollapsed = (collapsed: boolean) => {
    setIsCollapsed(collapsed);
  };

  return (
    <ChatCollapseContext.Provider
      value={{ isCollapsed, toggleCollapse, setCollapsed }}
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

