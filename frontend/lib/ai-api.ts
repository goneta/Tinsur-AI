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

    /**
     * Stream a chat response over WebSocket.
     * Falls back to HTTP POST if WebSocket fails.
     *
     * @returns cleanup function to close the connection
     */
    streamChat: (
        message: string,
        history: ChatMessage[] = [],
        onToken: (chunk: string) => void,
        onDone: (fullText: string) => void,
        onError: (code: number) => void,
        policy_id?: string,
    ): (() => void) => {
        const baseUrl = (api.defaults.baseURL || 'http://localhost:8000/api/v1')
            .replace(/\/api\/v1\/?$/, '');
        const token = localStorage.getItem('access_token') || '';
        const wsUrl = `${baseUrl.replace(/^http/, 'ws')}/api/v1/chat/ws?token=${encodeURIComponent(token)}`;

        let ws: WebSocket | null = null;
        let fullText = '';
        let connected = false;

        const fallbackToHttp = () => {
            AiAPI.chat(message, history, policy_id)
                .then((res) => {
                    onToken(res.response);
                    onDone(res.response);
                })
                .catch(() => onError(0));
        };

        try {
            ws = new WebSocket(wsUrl);

            const timeout = setTimeout(() => {
                if (!connected) {
                    ws?.close();
                    fallbackToHttp();
                }
            }, 5000);

            ws.onopen = () => {
                connected = true;
                clearTimeout(timeout);
                ws!.send(JSON.stringify({ message, history, policy_id }));
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'token' && data.text) {
                        fullText += data.text;
                        onToken(data.text);
                    } else if (data.type === 'done') {
                        onDone(fullText || data.response || '');
                        ws?.close();
                    } else if (data.type === 'error') {
                        onError(1011);
                        ws?.close();
                    }
                } catch {
                    // ignore parse errors
                }
            };

            ws.onerror = () => {
                if (!connected) fallbackToHttp();
                else onError(1006);
            };

            ws.onclose = (e) => {
                if (!connected) fallbackToHttp();
            };
        } catch {
            fallbackToHttp();
        }

        return () => ws?.close();
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
