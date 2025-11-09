import { EModalVariables } from "./constants";

export type ModalData =
  | Date
  | string
  | number
  | null
  | undefined
  | Record<string, unknown>
  | unknown[];

export interface ModalPayload {
  type: EModalVariables;
  isOpen: boolean;
  data?: ModalData;
}

export interface IModalState {
  isOpen: boolean;
  selectType: EModalVariables | null;
  data: ModalData;
}

export interface IModalContext {
  isOpen: boolean;
  selectType: EModalVariables | null;
  data: ModalData;
  openModal: (type: EModalVariables, data?: ModalData) => void;
  closeModal: () => void;
}

