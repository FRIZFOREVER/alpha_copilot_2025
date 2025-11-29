import { useNavigate, useLocation } from "react-router-dom";
import { cn } from "@/shared/lib/mergeClass";
import { Icon, IconTypes } from "@/shared/ui/icon";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { Avatar, AvatarImage } from "@/shared/ui/avatar";
import { useGetProfileQuery } from "@/entities/auth/hooks/useGetProfile";
import { getDisplayName } from "@/shared/lib/utils/userHelpers";

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

  const isDashboardActive = location.pathname.includes(
    `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.CHAT_ROUTE}`
  );

  const displayName = profileData?.username
    ? getDisplayName(profileData.username)
    : "Пользователь";

  const handleProfileClick = () => {
    navigate(`/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.PROFILE_ROUTE}`);
  };

  const handleLogoClick = () => {
    if (!isDashboardActive) {
      navigate(-1);
    }
  };

  return (
    <header className={cn("sticky top-0 z-50 w-full", className)}>
      <div className="mx-auto px-2 md:px-5 md:pr-6">
        <div className="flex items-center justify-between h-14 md:h-16">
          <button
            onClick={handleLogoClick}
            className={cn(
              "flex items-center gap-2 px-3 py-2 md:py-2.5 rounded-3xl cursor-pointer transition-all duration-200",
              "bg-white/10 backdrop-blur-sm shadow-sm hover:shadow",
              "border border-white/20",
              "hover:bg-white/20"
            )}
            title="Alfa Core"
          >
            <div className="group rounded-lg transition-all duration-300">
              <Icon
                type={IconTypes.ALPHA_OUTLINED}
                className="text-2xl md:text-2xl text-white fill-white/90 stroke-white/80 transition-all duration-300 group-hover:fill-white group-hover:stroke-white group-hover:drop-shadow-lg shrink-0"
              />
            </div>
            <div className="flex flex-col items-start min-w-0">
              <span className="text-xs font-medium text-white/90 truncate max-w-[100px] leading-tight">
                Alfa Core
              </span>
            </div>
          </button>

          <nav className="flex items-center space-x-1.5">
            <button
              onClick={handleProfileClick}
              className={cn(
                "flex items-center gap-2 px-3 py-1.5 m rounded-3xl cursor-pointer transition-all duration-200",
                "md:bg-white/95 md:backdrop-blur-sm md:shadow-sm md:hover:shadow",
                "md:border border-white/50",
                "md:hover:bg-white",
                isProfileActive && "md:ring-1 ring-white/50"
              )}
              title="Профиль"
            >
              <Avatar className="h-8 w-8 md:border border-gray-200 rounded-full shrink-0">
                <AvatarImage
                  src="/images/alpha-user.png"
                  alt={displayName}
                  className="object-cover rounded-full"
                />
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
