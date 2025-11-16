/**
 * Режимы работы модели, соответствующие ModelMode в ML сервисе
 */
export enum ModelMode {
  Fast = "fast",
  Thinking = "thinking",
  Research = "research",
  Auto = "auto",
}

/**
 * UI модели для выбора пользователем (соответствуют режимам ML сервиса)
 */
export type UIModelValue = "fast" | "thinking" | "research" | "auto";

/**
 * Маппинг UI модели в режим ML сервиса
 */
export const mapUIModelToMode = (uiModel: UIModelValue): ModelMode => {
  switch (uiModel) {
    case "fast":
      return ModelMode.Fast;
    case "thinking":
      return ModelMode.Thinking;
    case "research":
      return ModelMode.Research;
    case "auto":
      return ModelMode.Auto;
    default:
      return ModelMode.Auto;
  }
};

/**
 * Ключ для localStorage
 */
export const SELECTED_MODEL_STORAGE_KEY = "selected_model";

/**
 * Значение по умолчанию
 */
export const DEFAULT_MODEL: UIModelValue = "auto";

