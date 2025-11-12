import { Sidebar } from "@/widgets/sidebar";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useChatCollapse } from "@/shared/lib/chatCollapse";
import { WelcomeContent } from "./welcomeContent";
import { MinimizedChat } from "@/features/chat/ui/minimizedChat";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { cn } from "@/shared/lib/mergeClass";
import { Icon, IconTypes } from "@/shared/ui/icon";
import { useResize } from "@/shared/hooks/useResize";
import { useEffect, useRef } from "react";

const DashboardPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const {
    isCollapsed,
    isMinimizedChatVisible,
    toggleCollapse,
    setCollapsed,
    setMinimizedChatVisible,
  } = useChatCollapse();

  const isChatRoute =
    location.pathname.includes(`/${ERouteNames.CHAT_ROUTE}`) ||
    location.pathname === `/${ERouteNames.DASHBOARD_ROUTE}` ||
    location.pathname === `/${ERouteNames.DASHBOARD_ROUTE}/`;

  const prevIsLgViewRef = useRef<boolean | null>(null);

  const { isLgView } = useResize(() => {
    const wasLgView = prevIsLgViewRef.current;
    const nowIsLgView = window.innerWidth < 1024;

    if (wasLgView === false && nowIsLgView && !isCollapsed && isChatRoute) {
      setCollapsed(true);
      setMinimizedChatVisible(false);
    } else if (
      wasLgView === true &&
      !nowIsLgView &&
      isCollapsed &&
      isChatRoute
    ) {
      setMinimizedChatVisible(true);
    }

    prevIsLgViewRef.current = nowIsLgView;
  }, [isCollapsed, isChatRoute]);

  useEffect(() => {
    if (prevIsLgViewRef.current === null) {
      prevIsLgViewRef.current = isLgView;
    }
  }, [isLgView]);

  const showWelcomeContent = isCollapsed && isChatRoute;

  const showMinimizedChat =
    isCollapsed && isChatRoute && isMinimizedChatVisible && !isLgView;

  const showMobileChatButton =
    isCollapsed &&
    isChatRoute &&
    (isLgView || (!isLgView && !isMinimizedChatVisible));

  const handleMobileChatClick = () => {
    if (!isChatRoute) {
      navigate(`/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}`);
    }

    if (isLgView) {
      if (isCollapsed) {
        toggleCollapse();
      }
    } else {
      setMinimizedChatVisible(true);
    }
  };
  return (
    <div className="flex h-full w-full relative">
      <Sidebar />
      <div
        className={cn(
          "flex-1 flex overflow-hidden relative transition-all duration-300",
          !showWelcomeContent && "border-l border-[#0d0d0d0d]",
          showWelcomeContent && showMinimizedChat && "flex-row"
        )}
      >
        {showWelcomeContent ? (
          <>
            <div className="flex-1 overflow-hidden min-w-0">
              <WelcomeContent />
            </div>
            {showMinimizedChat && (
              <>
                <div className="w-px bg-gray-200 shrink-0" />
                <MinimizedChat />
              </>
            )}
            {showMobileChatButton && (
              <button
                onClick={handleMobileChatClick}
                className={cn(
                  "fixed bottom-6 right-6 z-50",
                  "w-14 h-14 rounded-full",
                  "bg-red-500 hover:bg-red-600",
                  "flex items-center justify-center",
                  "shadow-lg hover:shadow-xl",
                  "transition-all duration-200",
                  "active:scale-95"
                )}
                aria-label="Открыть чат"
              >
                <Icon
                  type={IconTypes.LOGO_OUTLINED_V2}
                  className="text-white w-7 h-7"
                />
              </button>
            )}
          </>
        ) : (
          <div
            className={cn(
              "h-full w-full",
              isCollapsed && isChatRoute && "hidden"
            )}
          >
            <Outlet />
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
