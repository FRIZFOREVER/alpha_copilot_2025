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
import { useLikeMessageMutation } from "@/entities/chat/hooks/useLikeMessage";
import { useState, useEffect } from "react";
import { Star } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import { EModalVariables } from "./constants";

export const RatingModal = () => {
  const { isOpen, selectType, data, closeModal } = useModal();
  const { mutate: likeMessage, isPending } = useLikeMessageMutation();
  const [selectedRating, setSelectedRating] = useState<number>(0);

  const isRatingModal = selectType === EModalVariables.RATING_MODAL;
  const modalData =
    data && typeof data === "object" && "answerId" in data && "chatId" in data
      ? (data as { answerId: number; chatId: number })
      : null;

  useEffect(() => {
    if (isOpen && isRatingModal) {
      setSelectedRating(0);
    }
  }, [isOpen, isRatingModal]);

  const handleRatingClick = (rating: number) => {
    setSelectedRating(rating);
  };

  const handleSubmit = () => {
    if (!modalData?.answerId || selectedRating === 0 || !modalData?.chatId)
      return;

    likeMessage(
      {
        chatId: modalData.chatId,
        likeDto: {
          answer_id: modalData.answerId,
          rating: selectedRating,
        },
      },
      {
        onSuccess: () => {
          closeModal();
          setSelectedRating(0);
        },
      }
    );
  };

  const handleClose = () => {
    closeModal();
    setSelectedRating(0);
  };

  if (!isRatingModal) return null;

  return (
    <Dialog open={isOpen && isRatingModal} onOpenChange={handleClose}>
      <DialogContent
        className={cn(
          "max-w-[500px] w-[calc(100%-2rem)]",
          "bg-white rounded-3xl p-8",
          "border-0 shadow-none",
          "gap-6"
        )}
        showCloseButton={true}
      >
        <DialogHeader className="gap-4">
          <DialogTitle>Оцените ответ</DialogTitle>
          <DialogDescription>
            Выберите оценку от 1 до 5 звезд для этого ответа
          </DialogDescription>
        </DialogHeader>

        <div className="flex items-center justify-center gap-3 py-4">
          {[1, 2, 3, 4, 5].map((rating) => (
            <button
              key={rating}
              onClick={() => handleRatingClick(rating)}
              disabled={isPending}
              className={cn(
                "transition-all duration-200 hover:scale-110",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "focus:outline-none"
              )}
            >
              <Star
                className={cn(
                  "h-10 w-10 transition-colors",
                  selectedRating >= rating
                    ? "fill-yellow-400 text-yellow-400"
                    : "fill-gray-200 text-gray-300"
                )}
              />
            </button>
          ))}
        </div>

        <DialogFooter className="flex justify-start mt-4">
          <Button
            onClick={handleSubmit}
            disabled={selectedRating === 0 || isPending}
            className={cn(
              "bg-white border border-black text-black",
              "rounded-xl px-6 py-3",
              "hover:bg-gray-50",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "font-normal text-base"
            )}
          >
            {isPending ? "Отправка..." : "Хорошо"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
