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
  const [file, setFile] = useState<AttachedFile | null>(null);

  const validateFile = useCallback((file: File): boolean => {
    const fileExtension = file.name
      .substring(file.name.lastIndexOf("."))
      .toLowerCase();

    const isValidType =
      ALLOWED_FILE_TYPES.includes(file.type) ||
      ALLOWED_EXTENSIONS.includes(fileExtension);

    return isValidType;
  }, []);

  const addFile = useCallback(
    (newFile: File) => {
      if (validateFile(newFile)) {
        setFile({
          id: `${newFile.name}-${Date.now()}-${Math.random()}`,
          file: newFile,
          name: newFile.name,
          type: newFile.type,
          size: newFile.size,
        });
        return true;
      }
      return false;
    },
    [validateFile],
  );

  const removeFile = useCallback(() => {
    setFile(null);
  }, []);

  const clearFile = useCallback(() => {
    setFile(null);
  }, []);

  const selectFile = useCallback(() => {
    return new Promise<File | null>((resolve) => {
      const input = document.createElement("input");
      input.type = "file";
      input.multiple = false;
      input.accept = ALLOWED_EXTENSIONS.join(",");

      input.onchange = (e) => {
        const target = e.target as HTMLInputElement;
        resolve(target.files?.[0] || null);
      };

      input.oncancel = () => {
        resolve(null);
      };

      input.click();
    });
  }, []);

  return {
    file,
    addFile,
    removeFile,
    clearFile,
    selectFile,
    hasFile: file !== null,
  };
};
