import { useState, useCallback } from "react";

export interface AttachedFile {
  id: string;
  file: File;
  name: string;
  type: string;
  size: number;
}

const ALLOWED_FILE_TYPES = [
  "application/pdf",
  "text/plain",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", // .xlsx
  "application/vnd.ms-excel", // .xls
  "application/msword", // .doc
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // .docx
];

const ALLOWED_EXTENSIONS = [".pdf", ".txt", ".xlsx", ".xls", ".doc", ".docx"];

export const useFileAttachments = () => {
  const [files, setFiles] = useState<AttachedFile[]>([]);

  const validateFile = useCallback((file: File): boolean => {
    const fileExtension = file.name
      .substring(file.name.lastIndexOf("."))
      .toLowerCase();

    const isValidType =
      ALLOWED_FILE_TYPES.includes(file.type) ||
      ALLOWED_EXTENSIONS.includes(fileExtension);

    return isValidType;
  }, []);

  const addFiles = useCallback(
    (newFiles: FileList | File[]) => {
      const fileArray = Array.from(newFiles);
      const validFiles: AttachedFile[] = [];

      fileArray.forEach((file) => {
        if (validateFile(file)) {
          validFiles.push({
            id: `${file.name}-${Date.now()}-${Math.random()}`,
            file,
            name: file.name,
            type: file.type,
            size: file.size,
          });
        }
      });

      setFiles((prev) => [...prev, ...validFiles]);
    },
    [validateFile],
  );

  const removeFile = useCallback((fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
  }, []);

  const selectFiles = useCallback(() => {
    return new Promise<FileList | null>((resolve) => {
      const input = document.createElement("input");
      input.type = "file";
      input.multiple = true;
      input.accept = ALLOWED_EXTENSIONS.join(",");

      input.onchange = (e) => {
        const target = e.target as HTMLInputElement;
        resolve(target.files);
      };

      input.oncancel = () => {
        resolve(null);
      };

      input.click();
    });
  }, []);

  return {
    files,
    addFiles,
    removeFile,
    clearFiles,
    selectFiles,
    hasFiles: files.length > 0,
  };
};
