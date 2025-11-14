import { Mail, Calendar, Settings, LogOut } from "lucide-react";
import { Avatar, AvatarImage, AvatarFallback } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge/badge";
import { Progress } from "@/shared/ui/progress/progress";
import { useNavigate } from "react-router-dom";
import { useGetProfileQuery } from "@/entities/auth/hooks/useGetProfile";
import {
  getUserInitials,
  getDisplayName,
} from "@/shared/lib/utils/userHelpers";
import { mockData } from "../lib/constants";
import { deleteAccessToken } from "@/entities/token";
import { useQueryClient } from "@tanstack/react-query";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { useChatCollapse } from "@/shared/lib/chatCollapse";
import { Header } from "@/widgets/header";
import { IntegrationCard } from "./components/integrationCard";

const ProfilePage = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { resetChatState } = useChatCollapse();
  const { data: profileData, isLoading: isLoadingProfile } =
    useGetProfileQuery();

  if (isLoadingProfile) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">Загрузка профиля...</p>
      </div>
    );
  }

  const displayName = profileData?.username
    ? getDisplayName(profileData.username)
    : "Пользователь";
  const displayEmail = profileData?.login || "";
  const userInitials = profileData?.username
    ? getUserInitials(profileData.username)
    : "П";

  const progress = (mockData.xp / mockData.xpToNext) * 100;

  const handleLogout = () => {
    deleteAccessToken();
    resetChatState();
    queryClient.clear();
    navigate(`/${ERouteNames.LANDING_ROUTE}`);
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-[#ef3124]/80 to-pink-600/80">
      <Header />
      <div className="overflow-hidden">
        <div className="flex-1 overflow-y-auto bg-zinc-100 rounded-t-2xl h-full">
          <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 md:py-8 space-y-6 md:space-y-8">
            <div className="relative rounded-4xl overflow-hidden border-2 border-gray-200 bg-gradient-to-br from-gray-50 to-white transition-all duration-300">
              <div className="relative z-10 p-6 md:p-8 lg:p-10">
                <div className="flex flex-col md:flex-row items-start gap-6 md:gap-8">
                  <div className="relative">
                    <Avatar className="relative h-32 w-32 md:h-40 md:w-40 ring-4 ring-white shadow-xl">
                      <AvatarImage
                        src="/images/user.webp"
                        alt={displayName}
                        className="object-cover rounded-2xl"
                      />
                      <AvatarFallback className="bg-gradient-to-br from-red-500 to-pink-500 text-white text-4xl md:text-5xl font-bold rounded-2xl">
                        {userInitials}
                      </AvatarFallback>
                    </Avatar>
                  </div>

                  <div className="flex-1 w-full space-y-5">
                    <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
                      <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
                        {displayName}
                      </h2>
                      <Badge className="self-start sm:self-center bg-gradient-to-r from-red-500 to-pink-500 text-white border-0 px-4 py-1.5 rounded-full text-xs font-semibold shadow-md">
                        {mockData.plan}
                      </Badge>
                    </div>

                    <div className="flex flex-col   gap-2">
                      <div className="flex items-center gap-2 text-sm md:text-base text-gray-600">
                        <div className="p-2 rounded-lg bg-gray-100">
                          <Calendar className="h-4 w-4 text-gray-700" />
                        </div>
                        <span>Присоединился {mockData.joinDate}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm md:text-base text-gray-600">
                        <div className="p-2 rounded-lg bg-gray-100">
                          <Mail className="h-4 w-4 text-gray-700" />
                        </div>
                        <span>{displayEmail}</span>
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-semibold text-gray-700">
                          Уровень {mockData.level}
                        </span>
                        <span className="text-sm font-medium text-gray-500">
                          {mockData.xp} / {mockData.xpToNext} XP
                        </span>
                      </div>
                      <Progress
                        value={progress}
                        className="h-3 bg-gray-200 rounded-full overflow-hidden [&>div]:!bg-gradient-to-r [&>div]:!from-red-500 [&>div]:!to-pink-500 [&>div]:!rounded-full [&>div]:!transition-all"
                      />
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3 pt-2">
                      <Button className="flex-1 cursor-pointer h-11 rounded-xl bg-gradient-to-r from-red-500 to-pink-600 text-white text-sm font-medium shadow-md hover:shadow-lg hover:from-red-600 hover:to-pink-700 transition-all">
                        <Settings className="h-4 w-4 mr-2" />
                        Настройки
                      </Button>
                      <Button
                        variant="outline"
                        className="flex-1 cursor-pointer h-11 rounded-xl border-2 border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300 text-gray-700 text-sm font-medium transition-all"
                        onClick={handleLogout}
                      >
                        <LogOut className="h-4 w-4 mr-2" />
                        Выйти
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <div className="mb-6 md:mb-8">
                <h3 className="text-xl md:text-2xl font-bold text-gray-900">
                  Интеграции
                </h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
                {mockData.integrations.map((integration, i) => (
                  <IntegrationCard
                    key={i}
                    name={integration.name}
                    connected={integration.connected}
                    imageSrc={integration.imageSrc}
                    description={integration.description}
                    category={integration.category}
                    onClick={() => {
                      console.log(`Click on ${integration.name}`);
                    }}
                  />
                ))}
              </div>
            </div>

            {mockData.recommendations &&
              mockData.recommendations.length > 0 && (
                <div>
                  <div className="mb-6 md:mb-8">
                    <h3 className="text-xl md:text-2xl font-bold text-gray-900">
                      Рекомендации для вас
                    </h3>
                  </div>

                  <div className="space-y-4 md:space-y-5">
                    {mockData.recommendations.map((rec, i) => (
                      <div
                        key={i}
                        className="group relative overflow-hidden rounded-2xl md:rounded-3xl border-2 border-gray-200/50 bg-white/80 backdrop-blur-sm shadow-md hover:shadow-xl hover:border-red-200 transition-all duration-300"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 via-pink-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-red-500/5 to-pink-500/5 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                        <div className="relative p-5 md:p-6 lg:p-7">
                          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 md:gap-6">
                            <div className="flex-1 space-y-2">
                              <h4 className="text-base md:text-lg font-bold text-gray-900 group-hover:text-gray-950 transition-colors">
                                {rec.title}
                              </h4>
                              <p className="text-sm md:text-base text-gray-600 leading-relaxed">
                                {rec.description}
                              </p>
                            </div>

                            <div className="flex-shrink-0">
                              <Button
                                size="sm"
                                className="h-10 md:h-11 cursor-pointer px-5 md:px-6 text-sm font-medium bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white rounded-xl shadow-md hover:shadow-lg transform hover:scale-105 transition-all duration-200 whitespace-nowrap"
                              >
                                {rec.action}
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
