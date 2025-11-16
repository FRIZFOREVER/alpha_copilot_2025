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
import {
  useTelegramAuthStartMutation,
  useTelegramAuthVerifyMutation,
} from "@/entities/auth/hooks/useTelegramAuth";
import { useState, useEffect } from "react";
import { EModalVariables } from "./constants";
import { Input } from "@/shared/ui/input/input";
import { Label } from "@/shared/ui/label/label";
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/shared/ui/input-otp";
import { Loader2, AlertCircle } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { TELEGRAM_STATUS_QUERY } from "@/entities/auth/hooks/useTelegramStatus";

interface TelegramAuthModalData {
  user_id: string;
}

export const TelegramAuthModal = () => {
  const { isOpen, selectType, data, closeModal } = useModal();
  const queryClient = useQueryClient();
  const {
    mutate: startAuth,
    isPending: isStarting,
    isError: isStartError,
    error: startError,
  } = useTelegramAuthStartMutation();
  const {
    mutate: verifyAuth,
    isPending: isVerifying,
    isError: isVerifyError,
    error: verifyError,
    isSuccess: isVerifySuccess,
  } = useTelegramAuthVerifyMutation();

  const [phoneNumber, setPhoneNumber] = useState("");
  const [phoneCode, setPhoneCode] = useState("");
  const [password, setPassword] = useState("");
  const [step, setStep] = useState<"phone" | "code" | "password">("phone");
  const [error, setError] = useState<string | null>(null);

  const isTelegramModal = selectType === EModalVariables.TELEGRAM_AUTH_MODAL;
  const modalData =
    data && typeof data === "object" && "user_id" in data
      ? (data as unknown as TelegramAuthModalData)
      : null;

  useEffect(() => {
    if (isOpen && isTelegramModal) {
      setPhoneNumber("");
      setPhoneCode("");
      setPassword("");
      setStep("phone");
      setError(null);
    }
  }, [isOpen, isTelegramModal]);

  useEffect(() => {
    if (isVerifySuccess && phoneNumber) {
      try {
        localStorage.setItem("telegram_phone_number", phoneNumber);
      } catch (e) {
        console.warn("Failed to save phone number to localStorage:", e);
      }

      queryClient.invalidateQueries({
        queryKey: [TELEGRAM_STATUS_QUERY, phoneNumber],
      });
      closeModal();
    }
  }, [isVerifySuccess, closeModal, phoneNumber, queryClient]);

  const handlePhoneSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!modalData?.user_id || !phoneNumber.trim()) {
      setError("Введите номер телефона");
      return;
    }

    setError(null);
    startAuth(
      {
        user_id: modalData.user_id,
        phone_number: phoneNumber.trim(),
      },
      {
        onSuccess: (response) => {
          if (response.status === "code_sent") {
            setStep("code");
          } else {
            setError(response.error || "Ошибка при отправке кода");
          }
        },
        onError: (err: Error) => {
          setError(err.message || "Ошибка при отправке кода");
        },
      }
    );
  };

  const handleCodeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!modalData?.user_id || !phoneCode.trim()) {
      setError("Введите код подтверждения");
      return;
    }

    setError(null);
    verifyAuth(
      {
        user_id: modalData.user_id,
        phone_code: phoneCode.trim(),
        password: password.trim() || undefined,
      },
      {
        onSuccess: (response) => {
          if (response.status === "password_required") {
            setStep("password");
          } else if (response.status === "ok") {
            setError(null);
          } else {
            setError(response.error || "Ошибка при проверке кода");
          }
        },
        onError: (err: Error) => {
          setError(err.message || "Ошибка при проверке кода");
        },
      }
    );
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!modalData?.user_id || !password.trim()) {
      setError("Введите пароль двухфакторной аутентификации");
      return;
    }

    setError(null);
    verifyAuth(
      {
        user_id: modalData.user_id,
        phone_code: phoneCode.trim(),
        password: password.trim(),
      },
      {
        onSuccess: (response) => {
          if (response.status === "ok") {
            setError(null);
          } else {
            setError(response.error || "Ошибка при проверке пароля");
          }
        },
        onError: (err: Error) => {
          setError(err.message || "Ошибка при проверке пароля");
        },
      }
    );
  };

  if (!isTelegramModal || !modalData) return null;

  return (
    <Dialog open={isOpen} onOpenChange={closeModal}>
      <DialogContent className="sm:max-w-[425px] p-8">
        <DialogHeader>
          <DialogTitle>Подключение Telegram</DialogTitle>
          <DialogDescription>
            {step === "phone" &&
              "Введите номер телефона в международном формате (например, +79991234567)"}
            {step === "code" &&
              "Введите код подтверждения, который был отправлен в Telegram"}
            {step === "password" &&
              "Введите пароль двухфакторной аутентификации"}
          </DialogDescription>
        </DialogHeader>

        <form
          onSubmit={
            step === "phone"
              ? handlePhoneSubmit
              : step === "code"
              ? handleCodeSubmit
              : handlePasswordSubmit
          }
          className="space-y-4"
        >
          {step === "phone" && (
            <div className="space-y-2">
              <Label htmlFor="phone">Номер телефона</Label>
              <Input
                id="phone"
                type="tel"
                placeholder="+79991234567"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                disabled={isStarting}
                required
              />
            </div>
          )}

          {step === "code" && (
            <div className="space-y-2">
              <Label htmlFor="code">Код подтверждения</Label>
              <InputOTP
                maxLength={5}
                value={phoneCode}
                onChange={(value) => setPhoneCode(value)}
                disabled={isVerifying}
              >
                <InputOTPGroup>
                  <InputOTPSlot index={0} />
                  <InputOTPSlot index={1} />
                  <InputOTPSlot index={2} />
                  <InputOTPSlot index={3} />
                  <InputOTPSlot index={4} />
                </InputOTPGroup>
              </InputOTP>
            </div>
          )}

          {step === "password" && (
            <div className="space-y-2">
              <Label htmlFor="password">Пароль 2FA</Label>
              <Input
                id="password"
                type="password"
                placeholder="Введите пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isVerifying}
                required
              />
            </div>
          )}

          {(error || isStartError || isVerifyError) && (
            <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg">
              <AlertCircle className="h-4 w-4" />
              <span>
                {error ||
                  (startError as Error)?.message ||
                  (verifyError as Error)?.message ||
                  "Произошла ошибка"}
              </span>
            </div>
          )}

          {isVerifySuccess && (
            <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 p-3 rounded-lg">
              <span>✅ Telegram успешно подключен!</span>
            </div>
          )}

          <DialogFooter className="flex-col sm:flex-row gap-2">
            {step !== "phone" && (
              <Button
                className="rounded-3xl cursor-pointer"
                type="button"
                variant="outline"
                onClick={() => {
                  if (step === "code") {
                    setStep("phone");
                  } else if (step === "password") {
                    setStep("code");
                  }
                  setError(null);
                }}
                disabled={isStarting || isVerifying}
              >
                Назад
              </Button>
            )}
            <Button
              type="submit"
              disabled={isStarting || isVerifying}
              className="flex-1 rounded-3xl cursor-pointer"
            >
              {isStarting || isVerifying ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {isStarting ? "Отправка..." : "Проверка..."}
                </>
              ) : step === "phone" ? (
                "Отправить код"
              ) : step === "code" ? (
                "Подтвердить"
              ) : (
                "Войти"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
