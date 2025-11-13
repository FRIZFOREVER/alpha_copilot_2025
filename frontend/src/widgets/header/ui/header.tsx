import { useNavigate, useLocation } from "react-router-dom";
import { User, ChartArea } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { Icon, IconTypes } from "@/shared/ui/icon";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { Button } from "@/shared/ui";

interface HeaderProps {
  className?: string;
}

export const Header = ({ className }: HeaderProps) => {
  const navigate = useNavigate();
  const location = useLocation();

  const isProfileActive = location.pathname.includes(
    `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.PROFILE_ROUTE}`
  );
  const isAnalyticsActive = location.pathname.includes(
    `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.ANALYTICS_ROUTE}`
  );

  const handleProfileClick = () => {
    navigate(`/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.PROFILE_ROUTE}`);
  };

  const handleAnalyticsClick = () => {
    navigate(`/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.ANALYTICS_ROUTE}`);
  };

  const handleLogoClick = () => {
    navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
  };

  return (
    <header
      className={cn(
        "sticky top-0 z-50 w-full",
        "bg-gradient-to-br from-red-500 to-pink-600",
        "shadow-lg",
        className
      )}
    >
      <div className="mx-auto px-4 md:px-8 md:pr-4">
        <div className="flex items-center justify-between h-14 md:h-16">
          <div
            className="flex items-center gap-1.5 cursor-pointer"
            onClick={handleLogoClick}
          >
            <div className="group rounded-lg transition-all duration-300 hover:bg-white/20 p-2 -ml-2">
              <Icon
                type={IconTypes.LOGO_OUTLINED_V2}
                className="text-2xl md:text-3xl text-white fill-white/90 stroke-white/80 transition-all duration-300 group-hover:scale-110 group-hover:fill-white group-hover:stroke-white group-hover:drop-shadow-lg"
              />
            </div>
            <span className="text-lg md:text-xl font-bold text-white drop-shadow-sm">
              FinAi
            </span>
          </div>

          <nav className="flex items-center space-x-1.5">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleAnalyticsClick}
              className={cn(
                "rounded-lg cursor-pointer h-7 w-7",
                isAnalyticsActive
                  ? "bg-white/30 text-white backdrop-blur-sm"
                  : "text-white/90 hover:bg-white/20 hover:text-white"
              )}
              title="Развернуть чат"
            >
              <ChartArea className="h-3.5 w-3.5" />
            </Button>

            <Button
              variant="ghost"
              size="icon"
              onClick={handleProfileClick}
              className={cn(
                "rounded-lg cursor-pointer h-7 w-7",
                isProfileActive
                  ? "bg-white/30 text-white backdrop-blur-sm"
                  : "text-white/90 hover:bg-white/20 hover:text-white"
              )}
              title="Развернуть чат"
            >
              <User className="h-3.5 w-3.5" />
            </Button>
          </nav>
        </div>
      </div>
    </header>
  );
};
