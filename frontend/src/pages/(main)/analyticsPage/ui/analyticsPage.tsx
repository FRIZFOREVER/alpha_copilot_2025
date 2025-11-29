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
import { Image } from "@/shared/ui/image/image";
import { Suspense, lazy, useMemo } from "react";

// Динамический импорт recharts для code splitting
const PieChartComponent = lazy(async () => {
  const recharts = await import("recharts");
  return {
    default: ({
      categoryChartData,
    }: {
      categoryChartData: Array<{
        name: string;
        value: number;
        color: string;
      }>;
    }) => {
      const { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } = recharts;
      return (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={categoryChartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) =>
                `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`
              }
              outerRadius={90}
              fill="#8884d8"
              dataKey="value"
            >
              {categoryChartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={
                    entry.color === "purple-500"
                      ? "#8b5cf6"
                      : entry.color === "blue-500"
                      ? "#3b82f6"
                      : entry.color === "pink-500"
                      ? "#ec4899"
                      : entry.color === "green-500"
                      ? "#10b981"
                      : "#6b7280"
                  }
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e5e7eb",
                borderRadius: "12px",
                padding: "8px",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      );
    },
  };
});

const AnalyticsPage = () => {
  const navigate = useNavigate();

  const categoryChartData = useMemo(
    () =>
      analyticsData.categoryDistribution.map((cat) => ({
        name: cat.category,
        value: cat.percentage,
        color: cat.color.replace("bg-", ""),
      })),
    []
  );

  return (
    <div className="flex flex-col h-full bg-[#1D1D1B]">
      <Header />
      <div className="overflow-hidden md:px-6 md:pb-6">
        <div className="flex-1 overflow-y-auto scrollbar-hide bg-zinc-100 rounded-t-3xl md:rounded-4xl h-full">
          <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 md:py-8 space-y-6 md:space-y-8">
            <div className="flex items-center gap-3 sm:gap-4 mb-6">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate(-1)}
                className="h-10 w-10 rounded-4xl bg-white hover:bg-gray-50 shadow-sm transition cursor-pointer"
              >
                <ArrowLeft className="h-5 w-5 text-gray-700" />
              </Button>
              <div>
                <h1 className="text-xl sm:text-2xl font-semibold text-gray-900">
                  Аналитика
                </h1>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {analyticsData.businessMetrics.map((metric, i) => (
                <div
                  key={i}
                  className="rounded-4xl p-4 sm:p-5 bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 shadow-sm hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div
                      className={cn(
                        "h-10 w-10 rounded-4xl flex items-center justify-center",
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

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {[
                {
                  icon: MessageSquare,
                  value: analyticsData.usage.chats,
                  label: "Диалогов",
                  color: "text-blue-600",
                  bgColor: "bg-blue-100",
                },
                {
                  icon: BarChart3,
                  value: analyticsData.usage.messages,
                  label: "Сообщений",
                  color: "text-purple-600",
                  bgColor: "bg-purple-100",
                },
                {
                  icon: Clock,
                  value: analyticsData.usage.daysActive,
                  label: "Дней активен",
                  color: "text-pink-600",
                  bgColor: "bg-pink-100",
                },
              ].map((stat, i) => (
                <div
                  key={i}
                  className="rounded-4xl cursor-pointer p-5 bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 hover:border-gray-300 transition-all text-center shadow-sm hover:shadow-md"
                >
                  <div
                    className={cn(
                      "h-12 w-12 rounded-4xl flex items-center justify-center mx-auto mb-3",
                      stat.bgColor
                    )}
                  >
                    <stat.icon className={cn("h-6 w-6", stat.color)} />
                  </div>
                  <p className="text-2xl font-bold text-gray-900 mb-1">
                    {stat.value}
                  </p>
                  <p className="text-xs text-gray-500">{stat.label}</p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                {
                  icon: CheckCircle2,
                  value: analyticsData.overview.totalTasks,
                  label: "Задач выполнено",
                  color: "text-green-600",
                  bgColor: "bg-green-100",
                },
                {
                  icon: Clock,
                  value: analyticsData.overview.timeSaved,
                  label: "Сэкономлено времени",
                  color: "text-blue-600",
                  bgColor: "bg-blue-100",
                },
                {
                  icon: FileText,
                  value: analyticsData.overview.documentsCreated,
                  label: "Документов создано",
                  color: "text-purple-600",
                  bgColor: "bg-purple-100",
                },
                {
                  icon: Sparkles,
                  value: analyticsData.overview.templatesUsed,
                  label: "Шаблонов использовано",
                  color: "text-pink-600",
                  bgColor: "bg-pink-100",
                },
              ].map((stat, i) => (
                <div
                  key={i}
                  className="rounded-4xl p-4 bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 text-center shadow-sm hover:shadow-md transition-all"
                >
                  <div
                    className={cn(
                      "h-10 w-10 rounded-4xl flex items-center justify-center mx-auto mb-2",
                      stat.bgColor
                    )}
                  >
                    <stat.icon className={cn("h-5 w-5", stat.color)} />
                  </div>
                  <p className="text-xl font-bold text-gray-900 mb-1">
                    {stat.value}
                  </p>
                  <p className="text-xs text-gray-500">{stat.label}</p>
                </div>
              ))}
            </div>

            <div className="relative rounded-4xl overflow-hidden border-2 border-gray-200 bg-gradient-to-br from-gray-50 to-white shadow-sm">
              <div className="absolute inset-0 opacity-5">
                <Image
                  src="/images/D03_CardPromo1_210325.webp"
                  alt=""
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="relative z-10 p-4 sm:p-6">
                <Suspense
                  fallback={
                    <div className="flex items-center justify-center h-[300px]">
                      <div className="text-gray-500">Загрузка графика...</div>
                    </div>
                  }
                >
                  <PieChartComponent categoryChartData={categoryChartData} />
                </Suspense>
              </div>
            </div>

            {/* Популярные функции */}
            <div className="space-y-3">
              {analyticsData.topFeatures.map((feature, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-4 rounded-4xl bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 hover:border-gray-300 transition-all cursor-pointer shadow-sm hover:shadow-md"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-4xl bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center flex-shrink-0 shadow-md">
                      <feature.icon className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-900">
                        {feature.name}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <p className="text-xs text-gray-500">
                          Использовано {feature.count} раз
                        </p>
                        <div className="flex items-center gap-0.5 text-xs font-medium text-green-600">
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
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
