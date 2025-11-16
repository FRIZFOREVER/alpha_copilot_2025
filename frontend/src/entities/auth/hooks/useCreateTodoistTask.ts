import { useMutation } from "@tanstack/react-query";
import { createTodoistTask } from "../api/authService";
import {
  TodoistCreateTaskRequest,
  TodoistCreateTaskResponse,
} from "../types/types";

export const TODOIST_CREATE_TASK_QUERY = "todoist-create-task-query";

export const useCreateTodoistTaskMutation = () => {
  return useMutation({
    mutationKey: [TODOIST_CREATE_TASK_QUERY],
    mutationFn: async (
      request: TodoistCreateTaskRequest
    ): Promise<TodoistCreateTaskResponse> => {
      const response = await createTodoistTask(request);
      return response;
    },
  });
};

