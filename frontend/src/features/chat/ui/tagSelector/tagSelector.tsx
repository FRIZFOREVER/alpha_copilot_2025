import { useEffect, useRef } from "react";
import { cn } from "@/shared/lib/mergeClass";

export interface TagConfig {
  id: string;
  label: string;
  color: string;
}

export const AVAILABLE_TAGS: TagConfig[] = [
  { id: "general", label: "#general", color: "#6366f1" },
  { id: "finance", label: "#finance", color: "#10b981" },
  { id: "law", label: "#law", color: "#f59e0b" },
  { id: "marketing", label: "#marketing", color: "#ef4444" },
  { id: "managment", label: "#managment", color: "#8b5cf6" },
] as const;

export const TAG_COLORS = {
  general: "#6366f1",
  finance: "#10b981",
  law: "#f59e0b",
  marketing: "#ef4444",
  managment: "#8b5cf6",
};

export type TagId = (typeof AVAILABLE_TAGS)[number]["id"];

export const getTagConfig = (tagId: TagId): TagConfig | undefined => {
  return AVAILABLE_TAGS.find((tag) => tag.id === tagId);
};

interface TagSelectorProps {
  onSelect: (tag: TagId) => void;
  onClose: () => void;
  position: { top?: number; bottom?: number; left: number };
  className?: string;
}

export const TagSelector = ({
  onSelect,
  onClose,
  position,
  className,
}: TagSelectorProps) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        onClose();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [onClose]);

  return (
    <div
      ref={containerRef}
      className={cn(
        "absolute z-50 border border-gray-200 shadow-sm",
        "bg-white/90 backdrop-blur-xl",
        "rounded-4xl",
        "p-1 min-w-[240px] max-h-[320px] overflow-y-auto",
        className
      )}
      style={{
        ...(position.top !== undefined && { top: `${position.top}px` }),
        ...(position.bottom !== undefined && {
          bottom: `${position.bottom}px`,
        }),
        left: `${position.left}px`,
      }}
    >
      {AVAILABLE_TAGS.map((tag) => (
        <button
          key={tag.id}
          type="button"
          onClick={() => onSelect(tag.id)}
          className={cn(
            "w-full px-4 py-3 cursor-pointer text-left text-sm font-medium",
            "rounded-3xl transition-all duration-200",
            "hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100",
            "hover:shadow-sm hover:scale-[0.99]",
            "active:scale-95",
            "focus:outline-none focus:ring-2 focus:ring-blue-200",
            "flex items-center gap-3 group"
          )}
        >
          <span
            className="group-hover:translate-x-0.5 transition-transform"
            style={{ color: tag.color }}
          >
            {tag.label}
          </span>
        </button>
      ))}
    </div>
  );
};
