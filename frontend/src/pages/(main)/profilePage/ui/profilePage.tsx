import {
  Mail,
  Calendar,
  Settings,
  LogOut,
  ArrowLeft,
  MessageSquare,
  Zap,
  BarChart3,
  Target,
  Clock,
  Star,
  Crown,
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge/badge";
import { Progress } from "@/shared/ui/progress/progress";
import { useNavigate } from "react-router-dom";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { cn } from "@/shared/lib/mergeClass";
import { useGetProfileQuery } from "@/entities/auth/hooks/useGetProfile";

const ProfilePage = () => {
  const navigate = useNavigate();
  const { data: profileData, isLoading: isLoadingProfile } = useGetProfileQuery();

  // Мок данные для статистики и достижений (пока нет API)
  const mockData = {
    joinDate: "15 января 2024",
    plan: "Pro",
    level: 5,
    xp: 1247,
    xpToNext: 1500,
    usage: {
      messages: 1247,
      chats: 24,
      daysActive: 12,
    },
    achievements: [
      { icon: Zap, label: "Молния", unlocked: true },
      { icon: Star, label: "Звезда", unlocked: true },
      { icon: Crown, label: "Корона", unlocked: false },
      { icon: Target, label: "Цель", unlocked: true },
    ],
  };

  const getUserInitials = (username: string) => {
    const parts = username.trim().split(" ").filter(Boolean);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return username.charAt(0).toUpperCase();
  };

  const getDisplayName = (username: string) => {
    const parts = username.trim().split(" ").filter(Boolean);
    if (parts.length >= 3) {
      // Если 3+ слова (например, "Маслов Денис Романович"), берем второе и первое (Имя Фамилия)
      return `${parts[1]} ${parts[0]}`;
    } else if (parts.length === 2) {
      // Если 2 слова, берем оба
      return `${parts[0]} ${parts[1]}`;
    }
    // Если одно слово, возвращаем как есть
    return username;
  };

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
  const userInitials = profileData?.username ? getUserInitials(profileData.username) : "П";

  const progress = (mockData.xp / mockData.xpToNext) * 100;

  return (
    <div>
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center gap-4 mb-8">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(`/${ERouteNames.DASHBOARD_ROUTE}`)}
            className="h-12 w-12 rounded-2xl bg-white cursor-pointer hover:shadow-lg hover:bg-gray-50 transition-all"
          >
            <ArrowLeft className="h-6 w-6 text-gray-700" />
          </Button>
          <h1 className="text-2xl font-medium bg-clip-text text-black">
            Профиль
          </h1>
        </div>

        <div>
          <div className="lg:col-span-8 space-y-6">
            <div className="relative rounded-3xl overflow-hidden bg-white border border-gray-100">
              <div className="absolute inset-0 bg-gradient-to-t from-red-50/50 via-transparent to-transparent" />

              <div className="relative p-8">
                <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
                  <div className="relative group">
                    <Avatar className="relative h-32 w-32 md:h-40 md:w-40 border-4 border-white">
                      <AvatarFallback className="bg-gradient-to-br from-red-500 to-pink-600 text-white text-4xl font-bold rounded-3xl">
                        {userInitials}
                      </AvatarFallback>
                    </Avatar>
                  </div>

                  <div className="flex-1 text-center md:text-left">
                    <div className="flex items-center justify-center md:justify-start gap-3 mb-3">
                      <h2 className="text-2xl font-medium text-gray-900">
                        {displayName}
                      </h2>
                      <Badge className="bg-gradient-to-r from-red-500 to-pink-600 text-white border-0 px-4 py-1 text-sm font-bold">
                        {mockData.plan}
                      </Badge>
                    </div>

                    <p className="text-gray-600 flex items-center justify-center md:justify-start gap-2 mb-1">
                      <Calendar className="h-4 w-4" />
                      Присоединился {mockData.joinDate}
                    </p>

                    <div className="flex items-center justify-center md:justify-start gap-2 text-sm text-gray-600 mb-6">
                      <Mail className="h-4 w-4" />
                      {displayEmail}
                    </div>

                    <div className="mb-6">
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="font-medium text-gray-700">
                          Уровень {mockData.level}
                        </span>
                        <span className="text-gray-500">
                          {mockData.xp} / {mockData.xpToNext} XP
                        </span>
                      </div>
                      <Progress
                        value={progress}
                        className="h-3 bg-gray-200 [&>div]:!bg-gradient-to-r [&>div]:!from-red-500 [&>div]:!to-pink-600 [&>div]:!rounded-full [&>div]:!transition-all [&>div]:!duration-500 [&>div]:!shadow-sm"
                      />
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3">
                      <Button className="flex-1 h-12 rounded-2xl bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white font-semibold cursor-pointer">
                        <Settings className="h-5 w-5" />
                        Настройки
                      </Button>
                      <Button
                        variant="outline"
                        className="flex-1 h-12 rounded-2xl border-gray-300 bg-white hover:bg-gray-50 text-gray-700 border-0 cursor-pointer"
                      >
                        <LogOut className="h-5 w-5" />
                        Выйти
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {[
                {
                  icon: MessageSquare,
                  value: mockData.usage.chats,
                  label: "Диалогов",
                  color: "bg-red-50 border-red-200",
                },
                {
                  icon: BarChart3,
                  value: mockData.usage.messages,
                  label: "Сообщений",
                  color: "bg-purple-50 border-purple-200",
                },
                {
                  icon: Clock,
                  value: mockData.usage.daysActive,
                  label: "Дней активен",
                  color: "bg-emerald-50 border-emerald-200",
                },
              ].map((stat, i) => (
                <div
                  key={i}
                  className={cn(
                    "rounded-2xl p-5 bg-white border transition-all",
                    stat.color
                  )}
                >
                  <stat.icon className="h-8 w-8 text-gray-700 mx-auto mb-3" />
                  <p className="text-3xl font-medium text-center text-gray-900">
                    {stat.value}
                  </p>
                  <p className="text-sm text-gray-600 text-center mt-1">
                    {stat.label}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
