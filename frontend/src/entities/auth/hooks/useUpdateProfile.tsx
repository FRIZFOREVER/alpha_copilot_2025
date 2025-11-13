import { useMutation } from "@tanstack/react-query";
import { updateProfile } from "../api/authService";

export const useUpdateProfile = () => {
  return useMutation({
    mutationFn: updateProfile,
  });
};
