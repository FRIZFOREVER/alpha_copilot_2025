import { Globe, Brain, Mic } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import type { GraphLog } from "@/entities/chat/types/types";

interface GraphLogCardProps {
  log: GraphLog;
  index: number;
}

const getTagConfig = (tag: string) => {
  const normalizedTag = tag.toLowerCase();

  if (normalizedTag === "web") {
    return {
      icon: Globe,
      bgColor: "bg-blue-50",
      hoverBgColor: "hover:bg-blue-100",
      textColor: "text-blue-700",
      borderColor: "border-blue-200",
      iconColor: "text-blue-600",
      badgeBg: "bg-blue-500",
    };
  }

  if (normalizedTag === "think") {
    return {
      icon: Brain,
      bgColor: "bg-purple-50",
      hoverBgColor: "hover:bg-purple-100",
      textColor: "text-purple-700",
      borderColor: "border-purple-200",
      iconColor: "text-purple-600",
      badgeBg: "bg-purple-500",
    };
  }

  if (normalizedTag === "mic") {
    return {
      icon: Mic,
      bgColor: "bg-pink-50",
      hoverBgColor: "hover:bg-pink-100",
      textColor: "text-pink-700",
      borderColor: "border-pink-200",
      iconColor: "text-pink-600",
      badgeBg: "bg-pink-500",
    };
  }

  return {
    icon: null,
    bgColor: "bg-gray-50",
    hoverBgColor: "hover:bg-gray-100",
    textColor: "text-gray-700",
    borderColor: "border-gray-200",
    iconColor: "text-gray-600",
    badgeBg: "bg-gray-500",
  };
};

const formatTime = (timeString: string) => {
  try {
    const date = new Date(timeString);
    const hours = date.getHours().toString().padStart(2, "0");
    const minutes = date.getMinutes().toString().padStart(2, "0");
    const seconds = date.getSeconds().toString().padStart(2, "0");
    return `${hours}:${minutes}:${seconds}`;
  } catch {
    return timeString;
  }
};

export const GraphLogCard = ({ log }: GraphLogCardProps) => {
  const tagConfig = getTagConfig(log.tag);
  const IconComponent = tagConfig.icon;

  return (
    <div
      className={cn(
        "p-4 rounded-xl border transition-all duration-200",
        tagConfig.bgColor,
        tagConfig.hoverBgColor,
        tagConfig.borderColor
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          {IconComponent && (
            <IconComponent
              className={cn("h-4 w-4", tagConfig.iconColor)}
              aria-hidden="true"
            />
          )}
          <span
            className={cn(
              "text-xs font-semibold px-3 py-1.5 rounded-full text-white",
              tagConfig.badgeBg
            )}
          >
            {log.tag}
          </span>
        </div>
        <span className="text-xs text-gray-500 font-medium">
          {formatTime(log.log_time)}
        </span>
      </div>
      <p className={cn("text-sm leading-relaxed", tagConfig.textColor)}>
        {log.message}
      </p>
    </div>
  );
};
