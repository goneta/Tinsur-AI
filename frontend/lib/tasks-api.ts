import { api } from "./api";

export interface Task {
    id: string;
    company_id: string;
    created_by: string;
    assigned_to?: string;
    title: string;
    description?: string;
    priority: "low" | "medium" | "high" | "urgent";
    status: "pending" | "in_progress" | "completed" | "cancelled";
    due_date?: string;
    related_resource?: string;
    related_resource_id?: string;
    created_at: string;
    updated_at: string;
}

export interface CreateTaskPayload {
    title: string;
    description?: string;
    priority: Task["priority"];
    status: Task["status"];
    due_date?: string;
    related_resource?: string;
    related_resource_id?: string;
    assigned_to?: string;
}

export const tasksApi = {
    listTasks: async (params?: { status?: string; assigned_to?: string }) => {
        const response = await api.get<Task[]>("/tasks", { params });
        return response.data;
    },
    listEmployees: async () => {
        const response = await api.get<any[]>("/employees/");
        return response.data;
    },
    createTask: async (payload: CreateTaskPayload) => {
        const response = await api.post<Task>("/tasks", payload);
        return response.data;
    },
    updateTask: async (id: string, payload: Partial<CreateTaskPayload>) => {
        const response = await api.put<Task>(`/tasks/${id}`, payload);
        return response.data;
    },
};
