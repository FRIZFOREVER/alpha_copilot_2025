import { useQuery } from "@tanstack/react-query";
import { getTodoistStatus } from "../api/authService";
import { TodoistStatusResponse } from "../types/types";

export const TODOIST_STATUS_QUERY = "todoist-status-query";

export const useTodoistStatusQuery = (user_id: string | undefined) => {
  return useQuery({
    queryKey: [TODOIST_STATUS_QUERY, user_id],
    queryFn: async (): Promise<TodoistStatusResponse> => {
      if (!user_id) {
        throw new Error("user_id is required");
      }
      const response = await getTodoistStatus({ user_id });
      return response;
    },
    enabled: !!user_id,
    retry: false,
  });
};

