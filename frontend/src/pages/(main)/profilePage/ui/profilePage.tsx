import {
  Mail,
  Calendar,
  Settings,
  LogOut,
  Sparkles,
  ArrowLeft,
  MessageSquare,
  Zap,
  TrendingUp,
  Award,
  BarChart3,
  Target,
  Clock,
  Star,
  Crown,
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useNavigate } from "react-router-dom";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { cn } from "@/shared/lib/mergeClass";

const ProfilePage = () => {
  const navigate = useNavigate();

  const userData = {
    name: "Иван Иванов",
    email: "ivan@example.com",
    joinDate: "15 января 2024",
    avatar: null,
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

  const stats = [
    {
      icon: Zap,
      value: "1.2 сек",
      label: "Среднее время ответа",
      color: "from-amber-400 to-orange-500",
    },
    {
      icon: TrendingUp,
      value: "+45%",
      label: "Рост продуктивности",
      color: "from-emerald-400 to-teal-500",
    },
    {
      icon: Award,
      value: "4.8/5",
      label: "Качество ответов",
      color: "from-blue-400 to-indigo-500",
    },
    {
      icon: Clock,
      value: "12 дн.",
      label: "Активность подряд",
      color: "from-purple-400 to-pink-500",
    },
  ];

  const progress = (userData.xp / userData.xpToNext) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Header */}
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-4 mb-8">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(`/${ERouteNames.DASHBOARD_ROUTE}`)}
            className="h-12 w-12 rounded-2xl bg-white shadow-md hover:shadow-lg hover:bg-gray-50 transition-all"
          >
            <ArrowLeft className="h-6 w-6 text-gray-700" />
          </Button>
          <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-gray-900 to-red-600 bg-clip-text text-transparent">
            Профиль
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Main Card */}
          <div className="lg:col-span-8 space-y-6">
            {/* Profile Card */}
            <div className="relative rounded-3xl overflow-hidden bg-white shadow-xl border border-gray-100">
              <div className="absolute inset-0 bg-gradient-to-t from-red-50/50 via-transparent to-transparent" />

              <div className="relative p-8">
                <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
                  {/* Avatar */}
                  <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-red-400 to-pink-400 rounded-3xl blur-lg opacity-70 group-hover:opacity-100 transition duration-300" />
                    <Avatar className="relative h-32 w-32 md:h-40 md:w-40 border-4 border-white shadow-lg">
                      <AvatarFallback className="bg-gradient-to-br from-red-500 to-pink-600 text-white text-4xl font-bold rounded-3xl">
                        {userData.name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")}
                      </AvatarFallback>
                    </Avatar>
                    <div className="absolute bottom-0 right-0 h-12 w-12 rounded-2xl bg-gradient-to-br from-red-500 to-pink-600 flex items-center justify-center shadow-xl">
                      <Sparkles className="h-6 w-6 text-white" />
                    </div>
                  </div>

                  {/* User Info */}
                  <div className="flex-1 text-center md:text-left">
                    <div className="flex items-center justify-center md:justify-start gap-3 mb-3">
                      <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
                        {userData.name}
                      </h2>
                      <Badge className="bg-gradient-to-r from-red-500 to-pink-600 text-white border-0 px-4 py-1 text-sm font-bold">
                        {userData.plan}
                      </Badge>
                    </div>

                    <p className="text-gray-600 flex items-center justify-center md:justify-start gap-2 mb-4">
                      <Calendar className="h-4 w-4" />
                      Присоединился {userData.joinDate}
                    </p>

                    <div className="flex items-center justify-center md:justify-start gap-2 text-sm text-gray-600 mb-6">
                      <Mail className="h-4 w-4" />
                      {userData.email}
                    </div>

                    {/* Level Progress */}
                    <div className="mb-6">
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="font-medium text-gray-700">
                          Уровень {userData.level}
                        </span>
                        <span className="text-gray-500">
                          {userData.xp} / {userData.xpToNext} XP
                        </span>
                      </div>
                      <Progress
                        value={progress}
                        className="h-3 bg-gray-200 [&>div]:!bg-gradient-to-r [&>div]:!from-red-500 [&>div]:!to-pink-600 [&>div]:!rounded-full [&>div]:!transition-all [&>div]:!duration-500 [&>div]:!shadow-sm"
                      />
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row gap-3">
                      <Button className="flex-1 h-12 rounded-2xl bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white font-semibold shadow-lg">
                        <Settings className="h-5 w-5 mr-2" />
                        Настройки
                      </Button>
                      <Button
                        variant="outline"
                        className="flex-1 h-12 rounded-2xl border-gray-300 bg-white hover:bg-gray-50 text-gray-700"
                      >
                        <LogOut className="h-5 w-5 mr-2" />
                        Выйти
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {[
                {
                  icon: MessageSquare,
                  value: userData.usage.chats,
                  label: "Диалогов",
                  color: "bg-red-50 border-red-200",
                },
                {
                  icon: BarChart3,
                  value: userData.usage.messages,
                  label: "Сообщений",
                  color: "bg-purple-50 border-purple-200",
                },
                {
                  icon: Clock,
                  value: userData.usage.daysActive,
                  label: "Дней активен",
                  color: "bg-emerald-50 border-emerald-200",
                },
              ].map((stat, i) => (
                <div
                  key={i}
                  className={cn(
                    "rounded-2xl p-5 bg-white border shadow-sm hover:shadow-md transition-all",
                    stat.color
                  )}
                >
                  <stat.icon className="h-8 w-8 text-gray-700 mx-auto mb-3" />
                  <p className="text-3xl font-bold text-center text-gray-900">
                    {stat.value}
                  </p>
                  <p className="text-sm text-gray-600 text-center mt-1">
                    {stat.label}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Stats & Achievements */}
          <div className="lg:col-span-4 space-y-6">
            {/* KPI Cards */}
            <div className="rounded-3xl bg-white shadow-xl border border-gray-100 p-6">
              <h3 className="text-xl font-bold mb-5 bg-gradient-to-r from-gray-900 to-red-600 bg-clip-text text-transparent">
                Ваши достижения
              </h3>
              <div className="space-y-4">
                {stats.map((stat, i) => (
                  <div key={i} className="group">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div
                          className={cn(
                            "p-2 rounded-xl bg-gradient-to-br shadow-sm",
                            stat.color
                          )}
                        >
                          <stat.icon className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-sm font-medium text-gray-700">
                          {stat.label}
                        </span>
                      </div>
                      <span className="text-lg font-bold bg-gradient-to-r from-gray-900 to-red-600 bg-clip-text text-transparent">
                        {stat.value}
                      </span>
                    </div>
                    {i < stats.length - 1 && (
                      <div className="h-px bg-gray-200 mt-3" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Achievements */}
            <div className="rounded-3xl bg-white shadow-xl border border-gray-100 p-6">
              <h3 className="text-xl font-bold mb-5 bg-gradient-to-r from-gray-900 to-red-600 bg-clip-text text-transparent">
                Награды
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {userData.achievements.map((ach, i) => (
                  <div
                    key={i}
                    className={cn(
                      "aspect-square rounded-2xl flex flex-col items-center justify-center p-3 transition-all border",
                      ach.unlocked
                        ? "bg-gradient-to-br from-red-50 to-pink-50 border-red-200 shadow-sm"
                        : "bg-gray-50 border-gray-200 opacity-60"
                    )}
                  >
                    <ach.icon
                      className={cn(
                        "h-8 w-8 mb-2",
                        ach.unlocked ? "text-red-600" : "text-gray-400"
                      )}
                    />
                    <span className="text-xs font-medium text-center text-gray-700">
                      {ach.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
