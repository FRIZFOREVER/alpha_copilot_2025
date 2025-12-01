import { useMemo } from "react";
import { TimeseriesMessagesResponse } from "../types/types";

interface ActivityChartDataItem {
  month: string;
  value: number;
}

interface FallbackData {
  yearlyActivity: ActivityChartDataItem[];
}

export const useActivityChartData = (
  timeseriesMessages: TimeseriesMessagesResponse | undefined,
  selectedPeriod: "year" | "month",
  fallbackData?: FallbackData
): ActivityChartDataItem[] => {
  return useMemo(() => {
    if (timeseriesMessages && timeseriesMessages.length > 0) {
      if (selectedPeriod === "year") {
        const monthlyData = new Map<string, number>();

        timeseriesMessages.forEach((item) => {
          const date = new Date(item.day);
          const monthKey = `${date.getFullYear()}-${date.getMonth()}`;
          const currentCount = monthlyData.get(monthKey) || 0;
          monthlyData.set(monthKey, currentCount + item.count_messages);
        });

        return Array.from(monthlyData.entries())
          .map(([monthKey, count]) => {
            const [year, monthIndex] = monthKey.split("-").map(Number);
            const date = new Date(year, monthIndex, 1);
            let monthLabel = date.toLocaleDateString("ru-RU", {
              month: "short",
            });
            monthLabel = monthLabel.replace(/\.$/, "");
            monthLabel =
              monthLabel.charAt(0).toUpperCase() + monthLabel.slice(1);

            return {
              month: monthLabel,
              value: count,
              sortKey: monthKey,
            };
          })
          .sort((a, b) => a.sortKey.localeCompare(b.sortKey))
          .map(({ month, value }) => ({ month, value }));
      } else {
        const firstDate = new Date(timeseriesMessages[0].day);
        let monthLabel = firstDate.toLocaleDateString("ru-RU", {
          month: "long",
        });
        monthLabel = monthLabel.charAt(0).toUpperCase() + monthLabel.slice(1);

        const middleIndex = Math.floor(timeseriesMessages.length / 2);
        return timeseriesMessages.map((item, index) => ({
          month: index === middleIndex ? monthLabel : "",
          value: item.count_messages,
        }));
      }
    }

    return fallbackData?.yearlyActivity || [];
  }, [timeseriesMessages, selectedPeriod, fallbackData]);
};

