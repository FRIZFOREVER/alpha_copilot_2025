import { Sidebar } from "@/widgets/sidebar";
import { Outlet, useLocation } from "react-router-dom";
import { useChatCollapse } from "@/shared/lib/chatCollapse";
import { WelcomeContent } from "./welcomeContent";
import { MinimizedChat } from "@/features/chat/ui/minimizedChat";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { cn } from "@/shared/lib/mergeClass";

const DashboardPage = () => {
  const location = useLocation();
  const { isCollapsed } = useChatCollapse();

  const isChatRoute =
    location.pathname.includes(`/${ERouteNames.CHAT_ROUTE}`) ||
    location.pathname === `/${ERouteNames.DASHBOARD_ROUTE}` ||
    location.pathname === `/${ERouteNames.DASHBOARD_ROUTE}/`;

  const showWelcomeContent = isCollapsed && isChatRoute;
  const showMinimizedChat = isCollapsed && isChatRoute;

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
                <div className="w-px bg-gray-200 shrink-0 hidden lg:block" />
                <MinimizedChat />
              </>
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
