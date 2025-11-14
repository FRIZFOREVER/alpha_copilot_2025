import {
  ArrowLeft,
  MessageSquare,
  BarChart3,
  Clock,
  FileText,
  CheckCircle2,
  Sparkles,
  ArrowUp,
  ArrowDown,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/shared/ui/button";
import { useNavigate } from "react-router-dom";
import { cn } from "@/shared/lib/mergeClass";
import { analyticsData } from "../lib/constants";
import { Header } from "@/widgets/header";

const AnalyticsPage = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-[#ef3124]/80 to-pink-600/80">
      <Header />
      <div className="overflow-hidden">
        <div className="flex-1 overflow-y-auto bg-zinc-100 rounded-t-2xl h-full">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-4 sm:space-y-6">
            <div className="flex items-center gap-3 sm:gap-4 mb-6">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate(-1)}
                className="h-10 w-10 rounded-xl bg-white hover:bg-gray-50 shadow-sm transition cursor-pointer"
              >
                <ArrowLeft className="h-5 w-5 text-gray-700" />
              </Button>
              <div>
                <h1 className="text-xl sm:text-2xl font-semibold text-gray-900">
                  Аналитика
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                  Обзор эффективности использования AI Copilot
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {analyticsData.businessMetrics.map((metric, i) => (
                <div
                  key={i}
                  className="rounded-xl p-4 sm:p-5 bg-white border border-gray-200 shadow-sm hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div
                      className={cn(
                        "h-10 w-10 rounded-lg flex items-center justify-center",
                        metric.color
                          .replace("text-", "bg-")
                          .replace("-600", "-100")
                      )}
                    >
                      <metric.icon className={cn("h-5 w-5", metric.color)} />
                    </div>
                    <div
                      className={cn(
                        "flex items-center gap-1 text-xs font-medium",
                        metric.isPositive ? "text-green-600" : "text-red-600"
                      )}
                    >
                      {metric.isPositive ? (
                        <ArrowUp className="h-3 w-3" />
                      ) : (
                        <ArrowDown className="h-3 w-3" />
                      )}
                      {metric.change}%
                    </div>
                  </div>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900 mb-1">
                    {metric.value}
                  </p>
                  <p className="text-xs sm:text-sm text-gray-500">
                    {metric.label}
                  </p>
                </div>
              ))}
            </div>

            <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Статистика использования
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {[
                  {
                    icon: MessageSquare,
                    value: analyticsData.usage.chats,
                    label: "Диалогов",
                  },
                  {
                    icon: BarChart3,
                    value: analyticsData.usage.messages,
                    label: "Сообщений",
                  },
                  {
                    icon: Clock,
                    value: analyticsData.usage.daysActive,
                    label: "Дней активен",
                  },
                ].map((stat, i) => (
                  <div
                    key={i}
                    className="rounded-xl cursor-pointer p-4 bg-gray-50/50 hover:bg-gray-100/50 transition-all text-center border border-gray-100"
                  >
                    <stat.icon className="h-6 w-6 text-gray-700 mx-auto mb-2" />
                    <p className="text-xl font-medium text-gray-900">
                      {stat.value}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{stat.label}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Продуктивность
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
                  {
                    icon: CheckCircle2,
                    value: analyticsData.overview.totalTasks,
                    label: "Задач выполнено",
                    color: "text-green-600",
                  },
                  {
                    icon: Clock,
                    value: analyticsData.overview.timeSaved,
                    label: "Сэкономлено времени",
                    color: "text-blue-600",
                  },
                  {
                    icon: FileText,
                    value: analyticsData.overview.documentsCreated,
                    label: "Документов создано",
                    color: "text-purple-600",
                  },
                  {
                    icon: Sparkles,
                    value: analyticsData.overview.templatesUsed,
                    label: "Шаблонов использовано",
                    color: "text-pink-600",
                  },
                ].map((stat, i) => (
                  <div
                    key={i}
                    className="rounded-xl p-4 bg-gradient-to-br from-gray-50 to-white border border-gray-200 text-center"
                  >
                    <stat.icon
                      className={`h-6 w-6 ${stat.color} mx-auto mb-2`}
                    />
                    <p className="text-xl font-medium text-gray-900">
                      {stat.value}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{stat.label}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Динамика по периодам
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {analyticsData.trends.map((trend, i) => (
                  <div
                    key={i}
                    className="rounded-xl p-4 bg-gradient-to-br from-gray-50 to-white border border-gray-200"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium text-gray-600">
                        {trend.period}
                      </p>
                      <div
                        className={cn(
                          "flex items-center gap-1 text-xs font-medium",
                          trend.isPositive ? "text-green-600" : "text-red-600"
                        )}
                      >
                        {trend.isPositive ? (
                          <ArrowUp className="h-3 w-3" />
                        ) : (
                          <ArrowDown className="h-3 w-3" />
                        )}
                        {Math.abs(trend.change)}%
                      </div>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">
                      {trend.tasks}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      задач выполнено
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Популярные функции
              </h3>
              <div className="space-y-2">
                {analyticsData.topFeatures.map((feature, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-3 rounded-xl bg-gray-50/50 hover:bg-gray-100/50 transition-all cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                        <feature.icon className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {feature.name}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <p className="text-xs text-gray-500">
                            Использовано {feature.count} раз
                          </p>
                          <div
                            className={cn(
                              "flex items-center gap-0.5 text-xs font-medium",
                              "text-green-600"
                            )}
                          >
                            <ArrowUp className="h-3 w-3" />+{feature.trend}
                          </div>
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="h-5 w-5 text-gray-400 flex-shrink-0" />
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Активность по дням недели
              </h3>
              <div className="space-y-3">
                {analyticsData.weeklyActivity.map((day, i) => {
                  const maxTasks = Math.max(
                    ...analyticsData.weeklyActivity.map((d) => d.tasks)
                  );
                  const taskPercentage = (day.tasks / maxTasks) * 100;

                  return (
                    <div key={i} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium text-gray-700">
                          {day.day}
                        </span>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>{day.tasks} задач</span>
                          <span>{day.documents} документов</span>
                        </div>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-red-500 to-pink-500 rounded-full transition-all"
                          style={{ width: `${taskPercentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Распределение по категориям
              </h3>
              <div className="space-y-3">
                {analyticsData.categoryDistribution.map((category, i) => (
                  <div key={i} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-gray-700">
                        {category.category}
                      </span>
                      <span className="text-xs text-gray-500">
                        {category.percentage}%
                      </span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all",
                          category.color
                        )}
                        style={{ width: `${category.percentage}%` }}
                      />
                    </div>
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

export default AnalyticsPage;
