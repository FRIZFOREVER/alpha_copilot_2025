import { Maximize2, X } from "lucide-react";
import { Button } from "@/shared/ui/button";
import { useChatCollapse } from "@/shared/lib/chatCollapse";
import { cn } from "@/shared/lib/mergeClass";
import { Chat } from "../chat";
import { useNavigate, useLocation } from "react-router-dom";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { Icon, IconTypes } from "@/shared/ui/icon";
import { useChatMessages } from "../../hooks/useChatMessages";

export const MinimizedChat = ({
  isCompact = false,
}: {
  isCompact?: boolean;
}) => {
  const { isCollapsed, toggleCollapse, setMinimizedChatVisible } =
    useChatCollapse();
  const navigate = useNavigate();
  const location = useLocation();
  const {
    messages,
    handleSendMessage,
    handleSendVoice,
    isLoading,
    suggestions,
  } = useChatMessages();

  const isChatRoute =
    location.pathname.includes(`/${ERouteNames.CHAT_ROUTE}`) ||
    location.pathname === `/${ERouteNames.DASHBOARD_ROUTE}` ||
    location.pathname === `/${ERouteNames.DASHBOARD_ROUTE}/`;

  const handleExpandChat = () => {
    if (!isChatRoute) {
      navigate(`/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}`);
    }
    setMinimizedChatVisible(true);
    if (isCollapsed) {
      toggleCollapse();
    }
  };

  const handleCollapseChat = () => {
    if (!isChatRoute) {
      navigate(`/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}`);
    }
    if (!isCollapsed) {
      toggleCollapse();
    }
    setMinimizedChatVisible(false);
  };

  if (!isCollapsed) return null;

  return (
    <div
      className={cn(
        "w-[450px] h-full",
        "bg-white rounded-4xl",
        "flex flex-col",
        "transition-all duration-300 ease-in-out",
        "shrink-0",
      )}
    >
      <div className="flex items-center justify-between px-4 py-4 bg-white rounded-4xl">
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 h-auto p-0 border-0 bg-transparent hover:bg-transparent shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 text-lg md:text-xl font-medium text-gray-900 hover:text-gray-700 transition-colors cursor-pointer data-[state=open]:text-gray-700 [&>svg]:opacity-60 [&>svg]:hover:opacity-100 [&_[data-slot=select-value]]:hidden">
            <div className="group cursor-pointer rounded-lg transition-all duration-300 hover:bg-red-50/50">
              <Icon
                type={IconTypes.LOGO_OUTLINED_V2}
                className="text-2xl text-red-400 fill-red-100/80 stroke-red-200 transition-all duration-300 group-hover:scale-110 group-hover:text-red-600 group-hover:fill-red-200 group-hover:stroke-red-300 group-hover:drop-shadow-lg"
              />
            </div>
            <span>FinAi</span>
          </button>
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleExpandChat}
            className="h-7 w-7 rounded-lg hover:bg-gray-100 cursor-pointer"
            title="Развернуть чат"
          >
            <Maximize2 className="h-3.5 w-3.5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleCollapseChat}
            className="h-7 w-7 rounded-lg hover:bg-gray-100 cursor-pointer"
            title="Свернуть чат"
          >
            <X className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
      <div className="flex-1 overflow-hidden rounded-b-4xl">
        <Chat
          messages={messages}
          onSendMessage={handleSendMessage}
          onSendVoice={handleSendVoice}
          isLoading={isLoading}
          hideHeader={true}
          suggestions={suggestions}
          isCompact={isCompact}
        />
      </div>
    </div>
  );
};
