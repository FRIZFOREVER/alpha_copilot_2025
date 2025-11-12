import { X } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import type { AttachedFile } from "../../hooks/useFileAttachments";
import {
  getFileType,
  getFileTypeLabel,
  getFileIcon,
} from "../../lib/fileHelpers";

export interface FileBadgeProps {
  file: AttachedFile;
  onRemove: (fileId: string) => void;
  disabled?: boolean;
  className?: string;
}

export const FileBadge = ({
  file,
  onRemove,
  disabled = false,
  className,
}: FileBadgeProps) => {
  const fileType = getFileType(file);
  const fileTypeLabel = getFileTypeLabel(fileType);
  const Icon = getFileIcon(fileType);

  const handleRemove = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    if (!disabled) {
      onRemove(file.id);
    }
  };

  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-[16px] px-2",
        "bg-white border border-gray-200",
        "max-w-full md:max-w-1/2",
        className
      )}
    >
      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center">
        <Icon className="h-5 w-5 text-white" />
      </div>

      <div className="flex-1 min-w-0 py-2">
        <p className="text-sm font-medium text-gray-900 truncate">
          {file.name}
        </p>
        <p className="text-xs text-gray-500">{fileTypeLabel}</p>
      </div>

      <button
        type="button"
        onClick={handleRemove}
        disabled={disabled}
        className={cn(
          "flex-shrink-0 w-6 h-6 rounded-full",
          "flex items-center justify-center",
          "text-gray-700 hover:text-gray-900 hover:bg-gray-100",
          "transition-all duration-200",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          "mr-1"
        )}
        aria-label="Удалить файл"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};
