import { useState } from "react";
import { X } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { type TagId, getTagConfig } from "../tagSelector/tagSelector";

export interface TagBadgeProps {
  tagId: TagId;
  onRemove: () => void;
  disabled?: boolean;
  className?: string;
}

export const TagBadge = ({
  tagId,
  onRemove,
  disabled = false,
  className,
}: TagBadgeProps) => {
  const [isHovered, setIsHovered] = useState(false);
  const tagConfig = getTagConfig(tagId);

  if (!tagConfig) return null;

  const handleRemove = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    if (!disabled) {
      onRemove();
    }
  };

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md px-2.5 py-1",
        "text-xs font-medium transition-all duration-200",
        "border cursor-default",
        className
      )}
      style={{
        backgroundColor: `${tagConfig.color}15`,
        borderColor: `${tagConfig.color}40`,
        color: tagConfig.color,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <span className="select-none">{tagConfig.label}</span>
      {isHovered && (
        <button
          type="button"
          onClick={handleRemove}
          disabled={disabled}
          className={cn(
            "flex-shrink-0 w-4 h-4 rounded-full cursor-pointer",
            "flex items-center justify-center",
            "hover:bg-black/10 active:bg-black/20",
            "transition-all duration-150",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "ml-0.5"
          )}
          aria-label="Удалить тег"
        >
          <X className="h-3 w-3" style={{ color: tagConfig.color }} />
        </button>
      )}
    </div>
  );
};
