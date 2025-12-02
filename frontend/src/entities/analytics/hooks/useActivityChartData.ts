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
        const currentYear = new Date().getFullYear();

        const monthlyData = new Map<string, number>();

        timeseriesMessages.forEach((item) => {
          const date = new Date(item.day);
          const year = date.getFullYear();
          const monthIndex = date.getMonth();

          if (year !== currentYear) return;

          const monthKey = `${year}-${monthIndex}`;
          const currentCount = monthlyData.get(monthKey) || 0;
          monthlyData.set(monthKey, currentCount + item.count_messages);
        });

        const result: ActivityChartDataItem[] = [];

        for (let month = 0; month < 12; month++) {
          const key = `${currentYear}-${month}`;
          const count = monthlyData.get(key) || 0;

          const date = new Date(currentYear, month, 1);
          let monthLabel = date.toLocaleDateString("ru-RU", { month: "short" });
          monthLabel = monthLabel.replace(/\.$/, "");
          monthLabel = monthLabel.charAt(0).toUpperCase() + monthLabel.slice(1);

          result.push({
            month: monthLabel,
            value: count,
          });
        }

        return result;
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
