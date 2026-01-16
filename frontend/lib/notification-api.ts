/**
 * API client for notification operations.
 */
import { api } from './api';

export interface Notification {
    id: string;
    type: string;
    channel: string;
    subject: string;
    content: string;
    status: 'pending' | 'sent' | 'delivered' | 'failed' | 'read';
    created_at: string;
    metadata: any;
}

export const notificationApi = {
    /**
     * Get recent notifications.
     */
    getNotifications: async (params?: {
        skip?: number;
        limit?: number;
        unread_only?: boolean;
    }) => {
        const response = await api.get<Notification[]>('/notifications', { params });
        return response.data;
    },

    /**
     * Mark a notification as read.
     */
    markAsRead: async (id: string) => {
        const response = await api.patch<{ message: string }>(`/notifications/${id}/read`);
        return response.data;
    },
};
