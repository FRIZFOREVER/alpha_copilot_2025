import { FileText, File, FileSpreadsheet } from "lucide-react";
import type { AttachedFile } from "../hooks/useFileAttachments";

export type FileType = "pdf" | "txt" | "excel" | "word" | "unknown";

export const getFileType = (file: AttachedFile): FileType => {
  const extension = file.name
    .substring(file.name.lastIndexOf("."))
    .toLowerCase();

  if (extension === ".pdf") return "pdf";
  if (extension === ".txt") return "txt";
  if (extension === ".xlsx" || extension === ".xls") return "excel";
  if (extension === ".doc" || extension === ".docx") return "word";

  return "unknown";
};

export const getFileTypeLabel = (fileType: FileType): string => {
  const labels: Record<FileType, string> = {
    pdf: "PDF",
    txt: "Текст",
    excel: "Таблица",
    word: "Документ",
    unknown: "Файл",
  };

  return labels[fileType];
};

export const getFileIcon = (fileType: FileType) => {
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

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
};
