import { useMutation } from "@tanstack/react-query";
import { saveTodoistToken } from "../api/authService";
import {
  TodoistAuthSaveRequest,
  TodoistAuthSaveResponse,
} from "../types/types";

export const TODOIST_AUTH_SAVE_QUERY = "todoist-auth-save-query";

export const useTodoistAuthSaveMutation = () => {
  return useMutation({
    mutationKey: [TODOIST_AUTH_SAVE_QUERY],
    mutationFn: async (
      request: TodoistAuthSaveRequest
    ): Promise<TodoistAuthSaveResponse> => {
      const response = await saveTodoistToken(request);
      return response;
    },
  });
};

