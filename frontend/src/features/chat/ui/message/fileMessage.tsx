import { FileText, File, FileSpreadsheet } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";

export type FileType = "pdf" | "txt" | "excel" | "word" | "unknown";

export interface FileMessageProps {
  fileUrl: string;
  className?: string;
}

const getFileTypeFromUrl = (url: string): FileType => {
  const extension = url.substring(url.lastIndexOf(".")).toLowerCase();

  if (extension === ".pdf") return "pdf";
  if (extension === ".txt") return "txt";
  if (extension === ".xlsx" || extension === ".xls") return "excel";
  if (extension === ".doc" || extension === ".docx") return "word";

  return "unknown";
};

const getFileTypeLabel = (fileType: FileType): string => {
  const labels: Record<FileType, string> = {
    pdf: "PDF",
    txt: "Текст",
    excel: "Таблица",
    word: "Документ",
    unknown: "Файл",
  };

  return labels[fileType];
};

const getFileIcon = (fileType: FileType) => {
  switch (fileType) {
    case "pdf":
    case "word":
      return FileText;
    case "excel":
      return FileSpreadsheet;
    case "txt":
    default:
      return File;
  }
};

const getFileNameFromUrl = (url: string): string => {
  const parts = url.split("/");
  const fileName = parts[parts.length - 1];
  return fileName || "Файл";
};

const truncateFileName = (fileName: string, maxLength: number = 25): string => {
  if (fileName.length <= maxLength) {
    return fileName;
  }

  const lastDotIndex = fileName.lastIndexOf(".");
  if (lastDotIndex === -1) {
    return fileName.substring(0, maxLength) + "...";
  }

  const extension = fileName.substring(lastDotIndex);
  const nameWithoutExtension = fileName.substring(0, lastDotIndex);

  const availableLength = maxLength - extension.length - 3;

  if (availableLength <= 0) {
    return fileName;
  }

  return nameWithoutExtension.substring(0, availableLength) + "..." + extension;
};

export const FileMessage = ({ fileUrl, className }: FileMessageProps) => {
  const fileType = getFileTypeFromUrl(fileUrl);
  const fileTypeLabel = getFileTypeLabel(fileType);
  const Icon = getFileIcon(fileType);
  const fileName = getFileNameFromUrl(fileUrl);

  return (
    <button
      className={cn(
        "flex items-center gap-3 rounded-2xl px-3 py-2.5",
        "bg-gray-50 border border-gray-200",
        "hover:bg-gray-100 transition-colors",
        "cursor-pointer text-left w-full",
        className
      )}
    >
      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-red-500 flex items-center justify-center">
        <Icon className="h-5 w-5 text-white" />
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">
          {truncateFileName(fileName, 25)}
        </p>
        <p className="text-xs text-gray-500">{fileTypeLabel}</p>
      </div>
    </button>
  );
};
