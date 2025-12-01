import { useMemo } from "react";
import { FileText, TrendingUp, Sparkles, CheckCircle2 } from "lucide-react";
import { TagCountsResponse, FileCountsResponse } from "../types/types";

export interface TopFeature {
  name: string;
  count: number;
  icon: any;
  trend: number;
}

export const useTopFeatures = (
  tagCounts: TagCountsResponse | undefined,
  fileCounts: FileCountsResponse | undefined
): TopFeature[] => {
  return useMemo(() => {
    const features: TopFeature[] = [];

    const tagFeatureMap: Record<string, { name: string; icon: any }> = {
      finance: {
        name: "Финансовые вопросы",
        icon: TrendingUp,
      },
      law: {
        name: "Юридические вопросы",
        icon: CheckCircle2,
      },
      marketing: {
        name: "Маркетинг",
        icon: Sparkles,
      },
      managment: {
        name: "Управление",
        icon: TrendingUp,
      },
    };

    if (tagCounts && tagCounts.length > 0) {
      tagCounts.forEach((item) => {
        const tagName = item.tag || "general";
        if (tagName !== "general" && tagFeatureMap[tagName]) {
          const feature = tagFeatureMap[tagName];
          const trend = item.tag_count - item.tag_count_yesterday || 0;
          features.push({
            name: feature.name,
            count: item.tag_count,
            icon: feature.icon,
            trend: trend,
          });
        }
      });
    }

    if (fileCounts && fileCounts.count_messages > 0) {
      const trend =
        fileCounts.count_messages - fileCounts.count_messages_yesterday;
      features.push({
        name: "Создание документов",
        count: fileCounts.count_messages,
        icon: FileText,
        trend: trend,
      });
    }

    return features.sort((a, b) => b.count - a.count);
  }, [tagCounts, fileCounts]);
};

