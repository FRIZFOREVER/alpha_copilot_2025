import { useState } from "react";
import { useForm } from "react-hook-form";
import { LoginSchema, TypeLoginSchema } from "../lib/schemes/loginSchema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form, FormField, FormItem } from "@/shared/ui/form/form";
import { CircleAlert, X, Eye, EyeOff } from "lucide-react";
import { Button } from "@/shared/ui";
import { Link } from "react-router-dom";
import { FloatingLabelInput } from "@/shared/ui/input/floatingInputLabel";
import { cn } from "@/shared/lib/mergeClass";
import { ERouteNames } from "@/shared/lib/routeVariables";
import { useLoginMutation } from "../hooks/useLogin";

export const LoginForm = () => {
  const [showPassword, setShowPassword] = useState(false);

  const form = useForm<TypeLoginSchema>({
    resolver: zodResolver(LoginSchema),
    defaultValues: {
      login: "",
      password: "",
    },
  });

  const { mutate } = useLoginMutation();

  const {
    handleSubmit,
    reset,
    formState: { errors },
  } = form;

  const onSubmit = (data: TypeLoginSchema) => {
    mutate(data);
    reset();
  };

  return (
    <div className="space-y-2 flex flex-col w-full justify-center h-full bg-white p-6 md:p-10 rounded-4xl">
      <Form {...form}>
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-3 flex flex-col w-full h-full justify-between"
        >
          <section className="space-y-3">
            <h2 className="font-medium text-black text-lg text-center">
              C возвращением!
            </h2>
            <FormField
              control={form.control}
              name="login"
              render={({ field }) => (
                <FormItem className="relative gap-1">
                  <FloatingLabelInput
                    {...field}
                    label="Почта"
                    className={cn(
                      "py-1.5 text-black bg-[#f0f3f7] rounded-3xl shadow-sm border-[#f0f3f7]",
                      errors.login && "border-red-700",
                    )}
                  />
                  {errors.login && (
                    <span className="text-red-800 text-xs px-3">
                      {errors.login.message}
                    </span>
                  )}
                  {field.value && !errors.login && (
                    <button
                      className="absolute right-4 top-4.5 text-blue-800 cursor-pointer"
                      onClick={() => field.onChange("")}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                  {errors.login && (
                    <button className="absolute right-4 top-4.5 text-red-800 cursor-pointer">
                      <CircleAlert className="w-4 h-4" />
                    </button>
                  )}
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem className="relative gap-1">
                  <FloatingLabelInput
                    {...field}
                    label="Пароль"
                    type={showPassword ? "text" : "password"}
                    className={cn(
                      "py-1.5 text-black bg-[#f0f3f7] rounded-3xl shadow-sm border-[#f0f3f7] pr-12",
                      errors.password && "border-red-700",
                    )}
                  />
                  {errors.password && (
                    <span className="text-red-800 text-xs px-3">
                      {errors.password.message}
                    </span>
                  )}
                  <div className="absolute right-4 top-4.5 flex items-center gap-2">
                    {field.value && !errors.password && (
                      <>
                        <button
                          type="button"
                          className="text-blue-800 cursor-pointer hover:text-blue-900"
                          onClick={() => setShowPassword(!showPassword)}
                        >
                          {showPassword ? (
                            <EyeOff className="w-4 h-4" />
                          ) : (
                            <Eye className="w-4 h-4" />
                          )}
                        </button>
                        <button
                          type="button"
                          className="text-blue-800 cursor-pointer hover:text-blue-900"
                          onClick={() => field.onChange("")}
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </>
                    )}
                    {errors.password && (
                      <button
                        type="button"
                        className="text-red-800 cursor-pointer"
                      >
                        <CircleAlert className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </FormItem>
              )}
            />

            <Button
              type="submit"
              variant={"outline"}
              className="px-6 py-5 w-full rounded-3xl bg-gradient-to-br from-red-500 to-pink-600 text-white hover:bg-[#D00E46] hover:text-white"
            >
              Войти
            </Button>
          </section>
          <p className="text-black text-center text-sm">
            У меня нет аккаунта,{" "}
            <Link
              to={`/${ERouteNames.AUTH_ROUTE}/${ERouteNames.REGISTER_ROUTE}`}
              className="text-blue-600 cursor-pointer"
            >
              зарегестрироваться
            </Link>
          </p>
        </form>
      </Form>
    </div>
  );
};
