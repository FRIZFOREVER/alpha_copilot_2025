import { useModal } from "./context";
import { EModalVariables } from "./constants";
import { RatingModal } from "./ratingModal";
import { SearchChatsModal } from "./searchChatsModal";
import { TelegramAuthModal } from "./telegramAuthModal";
import { TelegramContactsModal } from "./telegramContactsModal";
import { TodoistAuthModal } from "./todoisAuthModal";
import { TodoistCreateTaskModal } from "./todoistCreateTaskModal";

export const ModalProvider = () => {
  const { selectType } = useModal();

  if (!selectType) return null;

  switch (selectType) {
    case EModalVariables.RATING_MODAL:
      return <RatingModal />;
    case EModalVariables.SEARCH_CHATS_MODAL:
      return <SearchChatsModal />;
    case EModalVariables.TELEGRAM_AUTH_MODAL:
      return <TelegramAuthModal />;
    case EModalVariables.TELEGRAM_CONTACTS_MODAL:
      return <TelegramContactsModal />;
    case EModalVariables.TODOIST_AUTH_MODAL:
      return <TodoistAuthModal />;
    case EModalVariables.TODOIST_CREATE_TASK_MODAL:
      return <TodoistCreateTaskModal />;
    default:
      return null;
  }
};
