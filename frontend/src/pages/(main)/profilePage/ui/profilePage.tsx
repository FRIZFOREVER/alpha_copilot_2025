import {
  Mail,
  Calendar,
  Settings,
  LogOut,
  ArrowLeft,
  MessageSquare,
  BarChart3,
  Clock,
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
      <div className="max-w-5xl mx-auto px-4 py-8 space-y-4">
        <div className="flex items-center gap-3 mb-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="h-10 w-10 rounded-xl bg-white hover:bg-gray-50 shadow-sm transition cursor-pointer"
          >
            <ArrowLeft className="h-5 w-5 text-gray-700" />
          </Button>
          <h1 className="text-xl font-semibold text-gray-900">Профиль</h1>
        </div>

        <div className="rounded-2xl bg-white/80 backdrop-blur-sm border border-gray-200 shadow-sm p-6">
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
                <Button className="flex-1 cursor-pointer h-10 rounded-xl bg-gradient-to-r from-red-500 to-pink-600 hover:opacity-90 text-white text-sm font-medium">
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

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            {
              icon: MessageSquare,
              value: mockData.usage.chats,
              label: "Диалогов",
            },
            {
              icon: BarChart3,
              value: mockData.usage.messages,
              label: "Сообщений",
            },
            {
              icon: Clock,
              value: mockData.usage.daysActive,
              label: "Дней активен",
            },
          ].map((stat, i) => (
            <div
              key={i}
              className="rounded-xl cursor-pointer p-4 bg-white/60 backdrop-blur-sm border border-gray-200 hover:shadow-sm transition-all text-center"
            >
              <stat.icon className="h-6 w-6 text-gray-700 mx-auto mb-2" />
              <p className="text-xl font-medium text-gray-900">{stat.value}</p>
              <p className="text-xs text-gray-500">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
