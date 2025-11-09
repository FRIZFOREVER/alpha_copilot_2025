import { RatingModal } from "./RatingModal";
import { useModal } from "./context";
import { EModalVariables } from "./constants";

export const ModalProvider = () => {
  const { selectType } = useModal();

  if (!selectType) return null;

  switch (selectType) {
    case EModalVariables.RATING_MODAL:
      return <RatingModal />;
    default:
      return null;
  }
};
