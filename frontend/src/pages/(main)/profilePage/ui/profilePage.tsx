import {
  Mail,
  Calendar,
  Settings,
  LogOut,
  CheckCircle2,
  ChevronLeft,
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge/badge";
import { Progress } from "@/shared/ui/progress/progress";
import { useNavigate } from "react-router-dom";
import { useGetProfileQuery } from "@/entities/auth/hooks/useGetProfile";
import {
  getUserInitials,
  getDisplayName,
} from "@/shared/lib/utils/userHelpers";
import { cn } from "@/shared/lib/mergeClass";
import { mockData } from "../lib/constants";

const ProfilePage = () => {
  const navigate = useNavigate();
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

  return (
    <div>
      <div className="max-w-5xl mx-auto px-4 py-4 space-y-4">
        <div className="flex items-center gap-3 mb-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="h-11 w-11 rounded-3xl bg-white hover:bg-gray-50 shadow-sm transition cursor-pointer"
          >
            <ChevronLeft className="h-5 w-5 text-gray-700" />
          </Button>
          <h1 className="text-xl font-semibold text-gray-900">Профиль</h1>
        </div>

        <div className="rounded-3xl bg-white/80 backdrop-blur-sm border border-gray-200 shadow-sm p-6">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
            <Avatar className="h-28 w-28 md:h-32 md:w-32">
              <AvatarFallback className="bg-gradient-to-br from-red-500 to-pink-500 text-white text-3xl font-bold rounded-2xl">
                {userInitials}
              </AvatarFallback>
            </Avatar>

            <div className="flex-1 text-center md:text-left space-y-3 w-full">
              <div className="flex flex-col sm:flex-row items-center justify-center md:justify-start gap-3">
                <h2 className="text-xl font-medium text-gray-900">
                  {displayName}
                </h2>
                <Badge className="bg-gradient-to-r from-red-500 to-pink-500 text-white border-0 px-3 py-1 rounded-full text-xs font-semibold">
                  {mockData.plan}
                </Badge>
              </div>
              <div className="w-full flex justify-center flex-col items-center md:items-start">
                <p className="text-sm text-gray-600 flex items-center justify-center md:justify-start gap-2">
                  <Calendar className="h-4 w-4" />
                  Присоединился {mockData.joinDate}
                </p>
                <p className="text-sm text-gray-600 flex items-center justify-center md:justify-start gap-2">
                  <Mail className="h-4 w-4" />
                  {displayEmail}
                </p>
              </div>

              <div className="mt-4 space-y-1">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Уровень {mockData.level}</span>
                  <span>
                    {mockData.xp} / {mockData.xpToNext} XP
                  </span>
                </div>
                <Progress
                  value={progress}
                  className="h-2 bg-gray-200 [&>div]:!bg-gradient-to-r [&>div]:!from-red-500 [&>div]:!to-pink-500 [&>div]:!rounded-full"
                />
              </div>

              <div className="flex flex-col sm:flex-row gap-2 mt-4">
                <Button className="flex-1 cursor-pointer h-10 rounded-xl bg-gradient-to-r from-red-500 to-pink-600 text-white text-sm font-medium">
                  <Settings className="h-4 w-4" />
                  Настройки
                </Button>
                <Button
                  variant="outline"
                  className="flex-1 cursor-pointer h-10 rounded-xl border-gray-200 bg-white hover:bg-gray-50 text-gray-700 text-sm font-medium"
                >
                  <LogOut className="h-4 w-4" />
                  Выйти
                </Button>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-3xl bg-white/80 backdrop-blur-sm border border-gray-200 shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Продуктивность
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              {
                icon: "✅",
                value: mockData.productivity.tasksCompleted,
                label: "Задач выполнено",
                color: "text-green-600",
              },
              {
                icon: "⏰",
                value: mockData.productivity.timeSaved,
                label: "Сэкономлено времени",
                color: "text-blue-600",
              },
              {
                icon: "💻",
                value: mockData.productivity.documentsCreated,
                label: "Документов создано",
                color: "text-purple-600",
              },
              {
                icon: "⭐️",
                value: mockData.productivity.templatesUsed,
                label: "Шаблонов использовано",
                color: "text-pink-600",
              },
            ].map((stat, i) => (
              <div
                key={i}
                className="rounded-xl p-4 bg-gradient-to-br from-gray-50 to-white border border-gray-200 text-center"
              >
                <div className="text-2xl mb-2 text-center">{stat.icon}</div>
                <p className="text-xl font-medium text-gray-900">
                  {stat.value}
                </p>
                <p className="text-xs text-gray-500 mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl bg-white/80 backdrop-blur-sm border border-gray-200 shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Интеграции</h3>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {mockData.integrations.map((integration, i) => (
              <div
                key={i}
                className={cn(
                  "rounded-xl p-4 border-2 transition-all cursor-pointer",
                  integration.connected
                    ? "border-green-200 bg-green-50/50"
                    : "border-gray-200 bg-gray-50/50 hover:border-gray-300"
                )}
              >
                <div className="text-2xl mb-2 text-center">
                  {integration.icon}
                </div>
                <p className="text-sm font-medium text-gray-900 text-center">
                  {integration.name}
                </p>
                <div className="flex items-center justify-center mt-2">
                  {integration.connected ? (
                    <span className="text-xs text-green-600 font-medium flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3" />
                      Подключено
                    </span>
                  ) : (
                    <span className="text-xs text-gray-400">Не подключено</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {mockData.recommendations && mockData.recommendations.length > 0 && (
          <div className="rounded-3xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Рекомендации для вас
              </h3>
            </div>
            <div className="space-y-3">
              {mockData.recommendations.map((rec, i) => (
                <div
                  key={i}
                  className="flex items-start justify-between p-4 rounded-xl bg-white/80 border border-blue-100"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 mb-1">
                      {rec.title}
                    </p>
                    <p className="text-xs text-gray-600">{rec.description}</p>
                  </div>
                  <Button
                    size="sm"
                    className="ml-4 h-8 px-4 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
                  >
                    {rec.action}
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfilePage;
