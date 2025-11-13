import { Sidebar } from "@/widgets/sidebar";
import { Header } from "@/widgets/header";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useChatCollapse } from "@/shared/lib/chatCollapse";
import { WelcomeContent } from "./welcomeContent";
import { MinimizedChat } from "@/features/chat/ui/minimizedChat";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { cn } from "@/shared/lib/mergeClass";
import { Icon, IconTypes } from "@/shared/ui/icon";
import { useResize } from "@/shared/hooks/useResize";
import { useEffect, useRef } from "react";
import { Onboarding } from "@/widgets/onboarding";
import { useOnboarding } from "@/shared/lib/onboarding";

const DashboardPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const {
    isCollapsed,
    isMinimizedChatVisible,
    toggleCollapse,
    setMinimizedChatVisible,
  } = useChatCollapse();
  const { isOnboardingCompleted, startOnboarding, skipOnboarding } =
    useOnboarding();

  const isChatRoute =
    location.pathname.includes(`/${ERouteNames.CHAT_ROUTE}`) ||
    location.pathname === `/${ERouteNames.DASHBOARD_ROUTE}` ||
    location.pathname === `/${ERouteNames.DASHBOARD_ROUTE}/`;

  const prevIsLgViewRef = useRef<boolean | null>(null);
  const chatButtonRef = useRef<HTMLButtonElement>(null);

  const { isLgView } = useResize();

  const showWelcomeContent = isCollapsed && isChatRoute;

  const showMinimizedChat =
    isCollapsed && isChatRoute && isMinimizedChatVisible && !isLgView;

  const showMobileChatButton =
    isCollapsed &&
    isChatRoute &&
    (isLgView || (!isLgView && !isMinimizedChatVisible));

  useEffect(() => {
    if (prevIsLgViewRef.current === null) {
      prevIsLgViewRef.current = isLgView;
    }
  }, [isLgView]);

  useEffect(() => {
    if (isChatRoute && showWelcomeContent && !isOnboardingCompleted) {
      const timer = setTimeout(() => {
        if (showMobileChatButton || chatButtonRef.current) {
          startOnboarding();
        }
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [
    isChatRoute,
    showWelcomeContent,
    isOnboardingCompleted,
    startOnboarding,
    showMobileChatButton,
  ]);

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
  const shouldShowHeader = isCollapsed;

  return (
    <div className="flex h-full w-full relative flex-col">
      {shouldShowHeader && <Header />}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <div
          className={cn(
            "flex-1 flex overflow-hidden relative transition-all duration-300 bg-gradient-to-br from-[#ef3124]/80 to-pink-600/80",
            !showWelcomeContent && "border-l border-zinc-100",
            showWelcomeContent && showMinimizedChat && "flex-row"
          )}
        >
          {showWelcomeContent ? (
            <>
              <div
                className={cn(
                  "flex-1 overflow-hidden min-w-0 border bg-zinc-50 rounded-2xl",
                  showMinimizedChat && "md:mr-2 "
                )}
              >
                <WelcomeContent />
              </div>
              {showMinimizedChat && (
                <div>
                  <div className="w-px bg-gray-200 shrink-0" />
                  <MinimizedChat isCompact={true} />
                </div>
              )}
              {showMobileChatButton && (
                <button
                  ref={chatButtonRef}
                  onClick={() => {
                    if (!isOnboardingCompleted) {
                      skipOnboarding();
                    }
                    handleMobileChatClick();
                  }}
                  className={cn(
                    "fixed bottom-6 right-6 z-[105] cursor-pointer",
                    "w-14 h-14 rounded-full",
                    "bg-red-500 hover:bg-red-600",
                    "flex items-center justify-center",
                    "shadow-lg hover:shadow-xl",
                    "transition-all duration-200",
                    "active:scale-95"
                  )}
                  aria-label="Открыть чат"
                  style={{ pointerEvents: "auto" }}
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
      <Onboarding />
    </div>
  );
};

export default DashboardPage;
