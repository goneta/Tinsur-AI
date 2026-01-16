import { api } from '@/lib/api';

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp?: string;
}

export interface ChatResponse {
    response: string;
}

export const AiAPI = {
    chat: async (message: string, history?: ChatMessage[], policy_id?: string, image_path?: string): Promise<ChatResponse> => {
        try {
            const response = await api.post<ChatResponse>('/chat/', {
                message,
                history,
                policy_id,
                image_path
            });
            return response.data;
        } catch (error) {
            console.error('AI Chat Error:', error);
            throw error;
        }
    },
    validateEntity: async (type: string, data: any): Promise<any> => {
        try {
            const response = await api.post('/validation/validate', {
                type,
                data,
            });
            return response.data;
        } catch (error) {
            console.error('Validation Error:', error);
            throw error;
        }
    }
};
