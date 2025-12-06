import { FileText, File, FileSpreadsheet } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { axiosAuth } from "@/shared/api/baseQueryInstance";
import { useState } from "react";

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

const downloadFile = async (fileUrl: string, fileName: string) => {
  try {
    // Извлекаем имя файла из URL (последняя часть после /)
    const fileNameFromUrl = fileUrl.split("/").pop() || fileName;
    
    // Получаем базовый экземпляр axios для прямого доступа
    const axiosInstance = (axiosAuth as any).baseQueryV1Instance;
    
    // Делаем запрос с responseType: 'blob' для скачивания файла
    const response = await axiosInstance.get(fileUrl, {
      responseType: "blob",
    });

    // Создаем blob из ответа
    const blob = response.data as Blob;
    const url = window.URL.createObjectURL(blob);
    
    // Создаем временную ссылку и кликаем по ней для скачивания
    const link = document.createElement("a");
    link.href = url;
    link.download = fileNameFromUrl;
    document.body.appendChild(link);
    link.click();
    
    // Очищаем
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Ошибка при скачивании файла:", error);
    throw error;
  }
};

export const FileMessage = ({ fileUrl, className }: FileMessageProps) => {
  const fileType = getFileTypeFromUrl(fileUrl);
  const fileTypeLabel = getFileTypeLabel(fileType);
  const Icon = getFileIcon(fileType);
  const fileName = getFileNameFromUrl(fileUrl);
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    if (isDownloading) return;

    setIsDownloading(true);
    try {
      // Извлекаем путь к файлу из URL (убираем базовый URL если есть)
      const filePath = fileUrl.startsWith("http")
        ? `/files/${getFileNameFromUrl(fileUrl)}`
        : fileUrl.startsWith("/files/")
        ? fileUrl
        : `/files/${fileUrl}`;

      await downloadFile(filePath, fileName);
    } catch (error) {
      console.error("Не удалось скачать файл:", error);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <button
      onClick={handleDownload}
      disabled={isDownloading}
      className={cn(
        "flex items-center gap-3 rounded-2xl px-3 py-2.5",
        "bg-gray-50 border border-gray-200",
        "hover:bg-gray-100 transition-colors",
        "cursor-pointer text-left w-full",
        isDownloading && "opacity-50 cursor-wait",
        className
      )}
      aria-label={`Скачать файл ${fileName}`}
      title={`Скачать файл ${fileName}`}
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
