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
import { useCreateTodoistTaskMutation } from "@/entities/auth/hooks/useCreateTodoistTask";
import { useState, useEffect } from "react";
import { EModalVariables } from "./constants";
import { Input } from "@/shared/ui/input/input";
import { Textarea } from "@/shared/ui/textarea";
import { Label } from "@/shared/ui/label/label";
import { Loader2, AlertCircle } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";

interface TodoistCreateTaskModalData {
  user_id: string;
  content: string;
  labels?: string[];
}

export const TodoistCreateTaskModal = () => {
  const { isOpen, selectType, data, closeModal } = useModal();
  const {
    mutate: createTask,
    isPending: isCreating,
    isError: isCreateError,
    error: createError,
    isSuccess: isCreateSuccess,
  } = useCreateTodoistTaskMutation();

  const [taskContent, setTaskContent] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  const isTodoistModal =
    selectType === EModalVariables.TODOIST_CREATE_TASK_MODAL;
  const modalData =
    data && typeof data === "object" && "user_id" in data && "content" in data
      ? (data as unknown as TodoistCreateTaskModalData)
      : null;

  useEffect(() => {
    if (isOpen && isTodoistModal) {
      setTaskContent("");
      setDescription(modalData?.content || "");
      setError(null);
    }
  }, [isOpen, isTodoistModal, modalData?.content]);

  useEffect(() => {
    if (isCreateSuccess) {
      closeModal();
    }
  }, [isCreateSuccess, closeModal]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!modalData?.user_id || !taskContent.trim()) {
      setError("Введите название задачи");
      return;
    }

    setError(null);
    createTask(
      {
        user_id: modalData.user_id,
        content: taskContent.trim(),
        description: description.trim() || undefined,
        labels: modalData.labels,
      },
      {
        onSuccess: (response) => {
          if (response.status === "ok") {
            setError(null);
          } else {
            setError(response.error || "Ошибка при создании задачи");
          }
        },
        onError: (err: Error) => {
          setError(err.message || "Ошибка при создании задачи");
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
          "sm:top-[50%] sm:left-[50%] sm:right-auto sm:bottom-auto sm:h-auto sm:w-auto sm:max-w-[500px] sm:rounded-3xl sm:translate-x-[-50%] sm:translate-y-[-50%]",
          "flex flex-col p-4 sm:p-8"
        )}
      >
        <DialogHeader className="flex-shrink-0">
          <DialogTitle>Создать задачу в Todoist</DialogTitle>
          <DialogDescription>
            Заполните название задачи. Сообщение от ассистента автоматически
            добавлено в описание и может быть отредактировано.
          </DialogDescription>
        </DialogHeader>

        <form
          onSubmit={handleSubmit}
          className="flex flex-col flex-1 min-h-0 space-y-4 overflow-y-auto"
        >
          <div className="space-y-2">
            <Label htmlFor="content">Название задачи</Label>
            <Input
              id="content"
              type="text"
              placeholder="Введите название задачи"
              value={taskContent}
              onChange={(e) => setTaskContent(e.target.value)}
              disabled={isCreating}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Описание (необязательно)</Label>
            <Textarea
              id="description"
              placeholder="Введите описание задачи"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isCreating}
              rows={6}
              className="resize-none overflow-y-auto"
            />
          </div>

          {modalData.labels && modalData.labels.length > 0 && (
            <div className="space-y-2">
              <Label>Метки</Label>
              <div className="flex flex-wrap gap-2">
                {modalData.labels.map((label, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 text-xs rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
                  >
                    {label}
                  </span>
                ))}
              </div>
            </div>
          )}

          {(error || isCreateError) && (
            <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg">
              <AlertCircle className="h-4 w-4" />
              <span>
                {error || (createError as Error)?.message || "Произошла ошибка"}
              </span>
            </div>
          )}

          {isCreateSuccess && (
            <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 p-3 rounded-lg">
              <span>✅ Задача успешно создана в Todoist!</span>
            </div>
          )}

          <DialogFooter className="flex-shrink-0 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={closeModal}
              disabled={isCreating}
              className="rounded-3xl cursor-pointer"
            >
              Отмена
            </Button>
            <Button
              type="submit"
              disabled={isCreating}
              className="rounded-3xl cursor-pointer"
            >
              {isCreating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Создание...
                </>
              ) : (
                "Создать задачу"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
