import {
  createContext,
  FC,
  PropsWithChildren,
  useContext,
  useState,
} from "react";
import { EModalVariables } from "./constants";
import { IModalContext, ModalData } from "./types";

const ModalContext = createContext<IModalContext>({
  isOpen: false,
  selectType: null,
  data: null,
  openModal: () => {},
  closeModal: () => {},
});

export const useModal = () => {
  return useContext(ModalContext);
};

export const ModalProvider: FC<PropsWithChildren> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectType, setSelectType] = useState<EModalVariables | null>(null);
  const [data, setData] = useState<ModalData>(null);

  const openModal = (type: EModalVariables, modalData?: ModalData) => {
    setSelectType(type);
    setData(modalData || null);
    setIsOpen(true);
  };

  const closeModal = () => {
    setIsOpen(false);
    setSelectType(null);
    setData(null);
  };

  return (
    <ModalContext.Provider
      value={{
        isOpen,
        selectType,
        data,
        openModal,
        closeModal,
      }}
    >
      {children}
    </ModalContext.Provider>
  );
};

