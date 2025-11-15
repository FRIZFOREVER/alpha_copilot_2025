import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/ui/dialog/dialog";
import { Button } from "@/shared/ui/button";
import { useModal } from "./context";
import { useTelegramContactsQuery } from "@/entities/auth/hooks/useTelegramContacts";
import { useState, useEffect } from "react";
import { EModalVariables } from "./constants";
import { Input } from "@/shared/ui/input/input";
import { Loader2, Search, User } from "lucide-react";
import { TelegramContact } from "@/entities/auth/types/types";
import { cn } from "@/shared/lib/mergeClass";

interface TelegramContactsModalData {
  phone_number?: string;
  tg_user_id?: number;
  onSelect: (contact: TelegramContact) => void;
}

export const TelegramContactsModal = () => {
  const { isOpen, selectType, data, closeModal } = useModal();
  const [searchQuery, setSearchQuery] = useState("");

  const isTelegramContactsModal =
    selectType === EModalVariables.TELEGRAM_CONTACTS_MODAL;
  const modalData =
    data &&
    typeof data === "object" &&
    ("phone_number" in data || "tg_user_id" in data) &&
    "onSelect" in data
      ? (data as unknown as TelegramContactsModalData)
      : null;

  const {
    data: contactsData,
    isLoading,
    isError,
    error,
  } = useTelegramContactsQuery(modalData as TelegramContactsModalData);

  useEffect(() => {
    if (isOpen && isTelegramContactsModal) {
      setSearchQuery("");
    }
  }, [isOpen, isTelegramContactsModal]);

  const contacts = contactsData?.contacts || [];
  const filteredContacts = contacts.filter((contact) => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    const fullName = `${contact.first_name} ${contact.last_name}`.toLowerCase();
    const username = (contact.username || "").toLowerCase();
    const phone = (contact.phone_number || "").toLowerCase();
    return (
      fullName.includes(query) ||
      username.includes(query) ||
      phone.includes(query)
    );
  });

  const handleSelectContact = (contact: TelegramContact) => {
    modalData?.onSelect(contact);
    closeModal();
  };

  if (!isTelegramContactsModal || !modalData) return null;

  return (
    <Dialog open={isOpen} onOpenChange={closeModal}>
      <DialogContent
        className={cn(
          "inset-0 h-screen w-screen max-h-screen m-0 rounded-none translate-x-0 translate-y-0",
          "sm:top-[50%] sm:left-[50%] sm:right-auto sm:bottom-auto sm:h-auto sm:w-auto sm:max-w-[500px] sm:max-h-[60vh] sm:rounded-3xl sm:translate-x-[-50%] sm:translate-y-[-50%]",
          "flex flex-col p-0"
        )}
      >
        <DialogHeader className="flex-shrink-0 p-4 sm:p-6 pb-3 sm:pb-4">
          <DialogTitle className="text-xl sm:text-2xl">Выберите контакт Telegram</DialogTitle>
          <DialogDescription className="text-sm sm:text-base mt-2">
            Выберите контакт, которому хотите отправить сообщение
          </DialogDescription>
        </DialogHeader>

        <div className="flex-shrink-0 px-4 sm:px-6 pb-3 sm:pb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Поиск по имени, username или телефону..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 rounded-3xl h-11 sm:h-10 text-base sm:text-sm"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 sm:px-6 min-h-0">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
            </div>
          )}

          {isError && (
            <div className="flex items-center justify-center py-12 text-red-600">
              <p>
                {error instanceof Error
                  ? error.message
                  : "Ошибка при загрузке контактов"}
              </p>
            </div>
          )}

          {!isLoading && !isError && filteredContacts.length === 0 && (
            <div className="flex items-center justify-center py-12 text-gray-500">
              <p>
                {contacts.length === 0
                  ? "Контакты не найдены"
                  : "Ничего не найдено по запросу"}
              </p>
            </div>
          )}

          {!isLoading && !isError && filteredContacts.length > 0 && (
            <div className="space-y-2 sm:space-y-2 pb-4">
              {filteredContacts.map((contact) => (
                <button
                  key={contact.id}
                  onClick={() => handleSelectContact(contact)}
                  className={cn(
                    "w-full text-left p-3 sm:p-3.5 rounded-2xl sm:rounded-3xl border-2 transition-all duration-200",
                    "active:border-red-200 active:bg-red-50/50",
                    "sm:hover:border-red-200 sm:hover:bg-red-50/50",
                    "border-gray-200 bg-white"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex-shrink-0 w-10 h-10 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center text-white font-semibold text-sm sm:text-base">
                      {contact.first_name?.[0]?.toUpperCase() || (
                        <User className="h-5 w-5" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-base sm:text-base text-gray-900 truncate">
                        {contact.first_name} {contact.last_name}
                      </div>
                      {contact.username && (
                        <div className="text-sm text-gray-500 truncate mt-0.5">
                          @{contact.username}
                        </div>
                      )}
                      {contact.phone_number && (
                        <div className="text-xs text-gray-400 truncate mt-0.5">
                          {contact.phone_number}
                        </div>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <DialogFooter className="flex-shrink-0 p-4 sm:p-6 pt-3 sm:pt-4 border-t border-gray-100">
          <Button
            type="button"
            variant="outline"
            onClick={closeModal}
            className="w-full sm:w-auto rounded-3xl cursor-pointer h-11 sm:h-10 text-base sm:text-sm font-medium"
          >
            Отмена
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
