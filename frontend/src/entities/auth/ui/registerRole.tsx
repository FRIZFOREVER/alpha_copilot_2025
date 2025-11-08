import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/ui/select/select";
import { motion } from "framer-motion";
import { REGISTER_ROLE } from "../lib/constants";
import { Button } from "@/shared/ui";
import { useActions } from "@/shared/hooks/useActions";
import { useAppSelector } from "@/shared/hooks/useAppSelector";
import { selectAuthRole } from "../model/store/authSlice";
import { EProfileRoles } from "@/entities/profile/types/types";

interface RegisterRoleProps {
  onNextStep: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
}

export const RegisterRole = ({ onNextStep }: RegisterRoleProps) => {
  const selectRole = useAppSelector(selectAuthRole);
  const { setAuthRole } = useActions();

  const handleRoleChange = (value: EProfileRoles) => {
    setAuthRole(value);
  };

  return (
    <div className="space-y-2 flex flex-col w-full justify-center h-full bg-white p-6 md:p-10 rounded-3xl">
      <section className="space-y-1">
        <h2 className="font-medium text-black text-lg text-center">
          Выберите вашу роль
        </h2>
        <p className="text-xs sm:text-sm text-zinc-400 text-center">
          Это необходимо для того, чтобы вы могли получить доступ{" "}
          <br className="hidden sm:block" /> ко всем функциям нашего сервиса.
        </p>
      </section>
      <div className="w-full space-y-4">
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.3 }}
          className="w-full"
        >
          <Select onValueChange={handleRoleChange}>
            <SelectTrigger className="w-full rounded-3xl bg-[#f0f3f7] border-zinc-200 text-black text-[13px] focus:ring-1 focus:ring-zinc-400 py-6 px-3">
              <SelectValue placeholder="Выбрать роль" />
            </SelectTrigger>
            <SelectContent className="bg-[#f0f3f7] border-zinc-200 text-black rounded-3xl">
              {REGISTER_ROLE.map((role) => (
                <SelectItem
                  key={role.id}
                  value={role.role}
                  className="p-3 rounded-3xl"
                >
                  {role.title}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </motion.div>
        <Button
          value={"info"}
          variant={"outline"}
          disabled={!selectRole}
          onClick={onNextStep}
          className="px-6 py-5 rounded-3xl w-full bg-[#D00E46] text-white hover:bg-[#D00E46] hover:text-white"
        >
          Далее
        </Button>
      </div>
    </div>
  );
};
