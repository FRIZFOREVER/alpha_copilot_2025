import { useState, useEffect, useCallback } from "react";
import {
  UIModelValue,
  SELECTED_MODEL_STORAGE_KEY,
  DEFAULT_MODEL,
} from "@/shared/types/modelMode";

/**
 * Хук для работы с выбранной моделью из localStorage
 */
export const useSelectedModel = () => {
  const [selectedModel, setSelectedModelState] = useState<UIModelValue>(() => {
    if (typeof window === "undefined") return DEFAULT_MODEL;
    const stored = localStorage.getItem(SELECTED_MODEL_STORAGE_KEY);
    if (stored && ["fast", "thinking", "research", "auto"].includes(stored)) {
      return stored as UIModelValue;
    }
    return DEFAULT_MODEL;
  });

  useEffect(() => {
    // Сохраняем значение по умолчанию в localStorage, если его там нет
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem(SELECTED_MODEL_STORAGE_KEY);
      if (!stored || !["fast", "thinking", "research", "auto"].includes(stored)) {
        localStorage.setItem(SELECTED_MODEL_STORAGE_KEY, DEFAULT_MODEL);
      }
    }
  }, []);

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === SELECTED_MODEL_STORAGE_KEY && e.newValue) {
        if (["fast", "thinking", "research", "auto"].includes(e.newValue)) {
          setSelectedModelState(e.newValue as UIModelValue);
        }
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  const setSelectedModel = useCallback((model: UIModelValue) => {
    setSelectedModelState(model);
    localStorage.setItem(SELECTED_MODEL_STORAGE_KEY, model);
  }, []);

  return { selectedModel, setSelectedModel };
};
