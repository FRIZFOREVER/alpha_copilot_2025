import { z } from "zod";

export const RegisterSchema = z.object({
  login: z
    .string({
      message: "Email обязателен",
    })
    .email({
      message: "Введите корректный email-адрес",
    })
    .max(254, {
      message: "Email не должен превышать 254 символа",
    })
    .trim(),
  username: z
    .string({
      message: "Имя обязательно",
    })
    .max(254, {
      message: "Имя не должно превышать 254 символа",
    })
    .trim(),
  password: z
    .string({
      message: "Пароль обязателен",
    })
    .min(8, {
      message: "Пароль должен содержать минимум 8 символов",
    })
    .max(128, {
      message: "Пароль не должен превышать 128 символов",
    })
    .trim(),
});

export type TypeRegisterSchema = z.infer<typeof RegisterSchema>;
