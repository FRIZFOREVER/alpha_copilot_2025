import { useMemo } from "react";
import { TagCountsResponse } from "../types/types";

interface CategoryChartDataItem {
  name: string;
  value: number;
  color: string;
}

interface FallbackData {
  categoryDistribution: Array<{
    category: string;
    percentage: number;
    color: string;
  }>;
}

export const useCategoryChartData = (
  tagCounts: TagCountsResponse | undefined,
  fallbackData?: FallbackData
): CategoryChartDataItem[] => {
  return useMemo(() => {
    if (tagCounts && tagCounts.length > 0) {
      const totalCount = tagCounts.reduce(
        (sum, item) => sum + item.tag_count,
        0
      );

      const tagColorMap: Record<string, string> = {
        general: "purple-500",
        finance: "green-500",
        law: "orange-500",
        marketing: "pink-500",
        managment: "purple-500",
      };

      return tagCounts
        .map((item) => {
          const tagName = item.tag || "general";
          const percentage =
            totalCount > 0 ? (item.tag_count / totalCount) * 100 : 0;

          return {
            name: tagName,
            value: Number(percentage.toFixed(0)),
            color: tagColorMap[tagName] || "gray-500",
          };
        })
        .sort((a, b) => b.value - a.value);
    }

    if (fallbackData?.categoryDistribution) {
      return fallbackData.categoryDistribution.map((cat) => ({
        name: cat.category,
        value: cat.percentage,
        color: cat.color.replace("bg-", ""),
      }));
    }

    return [];
  }, [tagCounts, fallbackData]);
};

