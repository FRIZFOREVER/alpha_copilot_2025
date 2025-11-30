import { ArrowLeft, ArrowUp, ChevronRight } from "lucide-react";
import { Button } from "@/shared/ui/button";
import { useNavigate } from "react-router-dom";
import { analyticsData } from "../lib/constants";
import { Header } from "@/widgets/header";
import { Suspense, useMemo, useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/ui/select/select";
import {
  PieChartComponent,
  ActivityChart,
  EfficiencyMiniChart,
} from "@/features/analytics/ui";

const AnalyticsPage = () => {
  const navigate = useNavigate();
  const [selectedMonth, setSelectedMonth] = useState("year");
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
        <div className="flex-1 overflow-y-auto scrollbar-hide bg-white rounded-t-3xl md:rounded-4xl h-full">
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

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1 space-y-4">
                <div className="bg-white border border-gray-200 rounded-3xl p-5">
                  <div className="text-sm text-gray-600 mb-2">Сообщений</div>
                  <div className="text-4xl font-semibold text-gray-900">
                    {analyticsData.usage.messages.toLocaleString()}
                  </div>
                </div>
                <div className="bg-white border border-gray-200 rounded-3xl p-5">
                  <div className="text-sm text-gray-600 mb-2">Диалогов</div>
                  <div className="text-4xl font-semibold text-gray-900">
                    {analyticsData.usage.chats}
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-3xl p-5">
                  <div className="text-sm text-gray-600 mb-2">
                    Эффективность
                  </div>
                  <div className="text-4xl font-semibold text-gray-900 mb-2">
                    {analyticsData.efficiency}%
                  </div>
                  <Suspense fallback={<div className="h-8" />}>
                    <EfficiencyMiniChart />
                  </Suspense>
                </div>
              </div>

              <div className="lg:col-span-2 bg-white border border-gray-200 rounded-3xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    Активность запросов
                  </h2>
                  <Select
                    value={selectedMonth}
                    onValueChange={setSelectedMonth}
                  >
                    <SelectTrigger className="w-[120px] border-gray-300">
                      <SelectValue placeholder="Месяц" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="year">Год</SelectItem>
                      <SelectItem value="month">Месяц</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Suspense fallback={<div className="h-[250px]" />}>
                  <ActivityChart data={analyticsData.yearlyActivity} />
                </Suspense>
              </div>
            </div>
            <div className="relative rounded-4xl overflow-hidden border shadow-sm">
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

            <div className="space-y-3">
              {analyticsData.topFeatures.map((feature, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-4 rounded-4xl border transition-all cursor-pointer shadow-sm hover:shadow-md"
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
