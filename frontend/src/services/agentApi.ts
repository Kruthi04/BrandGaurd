/** API client for agent endpoints */
import { api } from "@/lib/api";
import type { AgentTask } from "@/types";

export async function agentChat(data: {
  message: string;
  brand_id?: string;
  session_id?: string;
}) {
  return api.post<{ response: string; actions: unknown[] }>("/agent/chat", data);
}

export async function startTask(data: {
  task_type: string;
  brand_id: string;
  parameters?: Record<string, unknown>;
}) {
  return api.post<AgentTask>("/agent/tasks", data);
}

export async function getTaskStatus(taskId: string) {
  return api.get<AgentTask>(`/agent/tasks/${taskId}`);
}

export async function listTasks(status?: string) {
  const params = status ? `?status=${status}` : "";
  return api.get<AgentTask[]>(`/agent/tasks${params}`);
}
