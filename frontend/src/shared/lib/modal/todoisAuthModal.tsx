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
import { useTodoistAuthSaveMutation } from "@/entities/auth/hooks/useTodoistAuth";
import { useState, useEffect } from "react";
import { EModalVariables } from "./constants";
import { Input } from "@/shared/ui/input/input";
import { Label } from "@/shared/ui/label/label";
import { Loader2, AlertCircle } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { TODOIST_STATUS_QUERY } from "@/entities/auth/hooks/useTodoistStatus";
import { cn } from "@/shared/lib/mergeClass";

interface TodoistAuthModalData {
  user_id: string;
}

export const TodoistAuthModal = () => {
  const { isOpen, selectType, data, closeModal } = useModal();
  const queryClient = useQueryClient();
  const {
    mutate: saveToken,
    isPending: isSaving,
    isError: isSaveError,
    error: saveError,
    isSuccess: isSaveSuccess,
  } = useTodoistAuthSaveMutation();

  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState<string | null>(null);

  const isTodoistModal = selectType === EModalVariables.TODOIST_AUTH_MODAL;
  const modalData =
    data && typeof data === "object" && "user_id" in data
      ? (data as unknown as TodoistAuthModalData)
      : null;

  useEffect(() => {
    if (isOpen && isTodoistModal) {
      setApiKey("");
      setError(null);
    }
  }, [isOpen, isTodoistModal]);

  useEffect(() => {
    if (isSaveSuccess && modalData?.user_id) {
      queryClient.invalidateQueries({
        queryKey: [TODOIST_STATUS_QUERY, modalData.user_id],
      });
      closeModal();
    }
  }, [isSaveSuccess, closeModal, modalData?.user_id, queryClient]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!modalData?.user_id || !apiKey.trim()) {
      setError("Введите API ключ Todoist");
      return;
    }

    setError(null);
    saveToken(
      {
        user_id: modalData.user_id,
        token: apiKey.trim(),
      },
      {
        onSuccess: (response) => {
          if (response.status === "ok") {
            setError(null);
          } else {
            setError(response.error || "Ошибка при сохранении токена");
          }
        },
        onError: (err: Error) => {
          setError(err.message || "Ошибка при сохранении токена");
        },
      }
    );
  };

  if (!isTodoistModal || !modalData) return null;

  return (
    <Dialog open={isOpen} onOpenChange={closeModal}>
      <DialogContent
        className={cn(
          "inset-0 h-screen w-screen max-h-screen m-0 rounded-none translate-x-0 translate-y-0",
          "sm:top-[50%] sm:left-[50%] sm:right-auto sm:bottom-auto sm:h-auto sm:w-auto sm:max-w-[425px] sm:rounded-3xl sm:translate-x-[-50%] sm:translate-y-[-50%]",
          "flex flex-col p-4 sm:p-8"
        )}
      >
        <DialogHeader className="flex-shrink-0">
          <DialogTitle className="text-xl sm:text-2xl">Подключение Todoist</DialogTitle>
          <DialogDescription className="text-sm sm:text-base mt-2">
            Введите API ключ Todoist для подключения аккаунта
          </DialogDescription>
        </DialogHeader>

        <form
          onSubmit={handleSubmit}
          className="flex flex-col flex-1 min-h-0 space-y-4 overflow-y-auto"
        >
          <div className="space-y-2">
            <Label htmlFor="apiKey" className="text-base sm:text-sm font-medium">
              API ключ Todoist
            </Label>
            <Input
              id="apiKey"
              type="password"
              placeholder="Введите API ключ"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              disabled={isSaving}
              required
              className="h-11 sm:h-10 text-base sm:text-sm"
            />
          </div>

          {(error || isSaveError) && (
            <div className="flex items-start gap-2 text-sm sm:text-sm text-red-600 bg-red-50 p-3 sm:p-3 rounded-lg">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <span className="break-words">
                {error || (saveError as Error)?.message || "Произошла ошибка"}
              </span>
            </div>
          )}

          {isSaveSuccess && (
            <div className="flex items-center gap-2 text-sm sm:text-sm text-green-600 bg-green-50 p-3 sm:p-3 rounded-lg">
              <span>✅ Todoist успешно подключен!</span>
            </div>
          )}

          <DialogFooter className="flex-shrink-0 pt-4 mt-auto">
            <Button
              type="submit"
              disabled={isSaving}
              className="w-full rounded-3xl cursor-pointer h-11 sm:h-10 text-base sm:text-sm font-medium"
            >
              {isSaving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Сохранение...
                </>
              ) : (
                "Сохранить"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
