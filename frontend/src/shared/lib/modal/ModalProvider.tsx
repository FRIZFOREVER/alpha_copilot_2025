import { useModal } from "./context";
import { EModalVariables } from "./constants";
import { SearchChatsModal } from "./searchChatsModal";
import { RatingModal } from "./ratingModal";

export const ModalProvider = () => {
  const { selectType } = useModal();

  if (!selectType) return null;

  switch (selectType) {
    case EModalVariables.RATING_MODAL:
      return <RatingModal />;
    case EModalVariables.SEARCH_CHATS_MODAL:
      return <SearchChatsModal />;
    default:
      return null;
  }
};
