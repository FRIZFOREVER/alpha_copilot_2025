import { useNavigate, useLocation } from "react-router-dom";
import { ChartArea } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { Icon, IconTypes } from "@/shared/ui/icon";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { Button } from "@/shared/ui";
import { Avatar, AvatarImage, AvatarFallback } from "@/shared/ui/avatar";
import { useGetProfileQuery } from "@/entities/auth/hooks/useGetProfile";
import {
  getUserInitials,
  getDisplayName,
} from "@/shared/lib/utils/userHelpers";

interface HeaderProps {
  className?: string;
}

export const Header = ({ className }: HeaderProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { data: profileData } = useGetProfileQuery();

  const isProfileActive = location.pathname.includes(
    `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.PROFILE_ROUTE}`
  );

  const displayName = profileData?.username
    ? getDisplayName(profileData.username)
    : "Пользователь";

  const userInitials = profileData?.username
    ? getUserInitials(profileData.username)
    : "П";

  const handleProfileClick = () => {
    navigate(`/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.PROFILE_ROUTE}`);
  };

  const handleLogoClick = () => {
    navigate(`/${ERouteNames.DASHBOARD_ROUTE}`);
  };

  return (
    <header
      className={cn(
        "sticky top-0 z-50 w-full",
        "bg-gradient-to-br from-[#ef3124]/80 to-pink-600/80",
        "backdrop-blur-md",
        "shadow-lg shadow-red-500/20",
        className
      )}
    >
      <div className="mx-auto px-4 md:px-8 md:pr-6">
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
            <button
              onClick={handleProfileClick}
              className={cn(
                "flex items-center gap-2 px-3 py-1 m rounded-xl cursor-pointer transition-all duration-200",
                "md:bg-white/95 md:backdrop-blur-sm md:shadow-sm md:hover:shadow",
                "md:border border-white/50",
                "md:hover:bg-white",
                isProfileActive && "md:ring-1 ring-white/50"
              )}
              title="Профиль"
            >
              <Avatar className="h-8 w-8 md:border border-gray-200 rounded-full shrink-0">
                <AvatarImage
                  src="/images/user.webp"
                  alt={displayName}
                  className="object-cover rounded-full"
                />
                <AvatarFallback className="bg-gradient-to-br from-red-500 to-pink-500 text-white rounded-full text-xs font-medium">
                  {userInitials}
                </AvatarFallback>
              </Avatar>
              <div className="hidden md:flex flex-col items-start min-w-0">
                <span className="text-xs font-medium text-gray-900 truncate max-w-[100px] leading-tight">
                  {displayName}
                </span>
                <span className="text-[10px] text-gray-500 truncate max-w-[100px] leading-tight">
                  Бизнесмен
                </span>
              </div>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
