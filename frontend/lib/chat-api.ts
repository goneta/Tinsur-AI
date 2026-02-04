import { api } from "./api";

export interface ChatChannel {
    id: string;
    company_id: string;
    name: string;
    is_private: boolean;
    created_by: string;
    created_at: string;
}

export interface ChatMessage {
    id: string;
    company_id: string;
    channel_id: string;
    sender_id: string;
    message: string;
    attachments?: any[];
    read_by: any[];
    reactions?: Array<{ emoji: string; user_id: string }>;
    created_at: string;
}

export interface ChatChannelMember {
    id: string;
    channel_id: string;
    user_id: string;
    added_by?: string;
    created_at: string;
}

export const chatApi = {
    listChannels: async () => {
        const response = await api.get<ChatChannel[]>("/chat/channels");
        return response.data;
    },
    createChannel: async (name: string, isPrivate: boolean, memberIds?: string[]) => {
        const response = await api.post<ChatChannel>("/chat/channels", {
            name,
            is_private: isPrivate,
            member_ids: memberIds && memberIds.length > 0 ? memberIds : undefined,
        });
        return response.data;
    },
    listChannelMembers: async (channelId: string) => {
        const response = await api.get<ChatChannelMember[]>(`/chat/channels/${channelId}/members`);
        return response.data;
    },
    inviteChannelMembers: async (channelId: string, userIds: string[]) => {
        const response = await api.post<ChatChannelMember[]>(`/chat/channels/${channelId}/members`, {
            user_ids: userIds,
        });
        return response.data;
    },
    listMessages: async (channelId: string) => {
        const response = await api.get<ChatMessage[]>("/chat/messages", {
            params: { channel_id: channelId },
        });
        return response.data;
    },
    sendMessage: async (channelId: string, message: string) => {
        const response = await api.post<ChatMessage>("/chat/messages", {
            channel_id: channelId,
            message,
        });
        return response.data;
    },
    markMessageRead: async (messageId: string) => {
        const response = await api.post<ChatMessage>(`/chat/messages/${messageId}/read`);
        return response.data;
    },
    reactToMessage: async (messageId: string, emoji: string, action: "add" | "remove") => {
        const response = await api.post<ChatMessage>(`/chat/messages/${messageId}/react`, {
            emoji,
            action,
        });
        return response.data;
    },
};
