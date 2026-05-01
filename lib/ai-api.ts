import axios from 'axios';
import { api } from '@/lib/api';

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp?: string;
}

export interface ChatResponse {
    response: string;
    meta?: {
        model?: string;
        durationMs?: number;
        retries?: number;
    };
}

const CHAT_TIMEOUT_MS = 25000;
const MAX_RETRIES = 1;

function wait(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function toUserSafeError(error: unknown): string {
    if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNABORTED') return 'timeout';
        if (!error.response) return 'network';
        if (error.response.status === 429) return 'rate_limit';
        if (error.response.status >= 500) return 'server';
    }
    return 'unknown';
}

export const AiAPI = {
    chat: async (
        message: string,
        history?: ChatMessage[],
        policy_id?: string,
        image_path?: string,
    ): Promise<ChatResponse> => {
        const startedAt = Date.now();
        let lastError: unknown;

        for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
            try {
                const response = await api.post<ChatResponse>(
                    '/chat/',
                    { message, history, policy_id, image_path },
                    { timeout: CHAT_TIMEOUT_MS },
                );

                const durationMs = Date.now() - startedAt;
                const model = (response.data as any)?.model || (response.data as any)?.meta?.model || 'unknown-model';

                console.info('[AI_CHAT_OK]', {
                    model,
                    durationMs,
                    retries: attempt,
                    historyLength: history?.length || 0,
                });

                return {
                    response: response.data?.response || '',
                    meta: { model, durationMs, retries: attempt },
                };
            } catch (error) {
                lastError = error;
                const kind = toUserSafeError(error);
                const durationMs = Date.now() - startedAt;

                console.error('[AI_CHAT_ERROR]', {
                    kind,
                    durationMs,
                    attempt,
                    messagePreview: message?.slice(0, 120),
                    status: axios.isAxiosError(error) ? error.response?.status : undefined,
                });

                const canRetry = attempt < MAX_RETRIES && (kind === 'timeout' || kind === 'network' || kind === 'server' || kind === 'rate_limit');
                if (canRetry) {
                    await wait(500 + attempt * 400);
                    continue;
                }
                break;
            }
        }

        throw lastError;
    },

    validateEntity: async (type: string, data: any): Promise<any> => {
        try {
            const response = await api.post('/validation/validate', { type, data });
            return response.data;
        } catch (error) {
            console.error('Validation Error:', error);
            throw error;
        }
    },

    /**
     * Stream a chat response via WebSocket for real-time token-by-token output.
     * Calls onToken for each streamed chunk, then onDone when complete.
     * Falls back to HTTP POST on any WebSocket error.
     *
     * @param message      User message to send
     * @param onToken      Called with each text chunk as it arrives
     * @param onDone       Called once with the full accumulated text
     * @param onError      Called with error code string on failure
     * @param policy_id    Optional policy context
     */
    streamChat: (
        message: string,
        onToken: (chunk: string) => void,
        onDone: (fullText: string) => void,
        onError: (code: string) => void,
        policy_id?: string,
    ): (() => void) => {
        const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
        if (!token) {
            onError('unauthenticated');
            return () => {};
        }

        const baseUrl = (api.defaults.baseURL || 'http://localhost:8000/api/v1')
            .replace(/^http/, 'ws')
            .replace('/api/v1', '');

        const wsUrl = `${baseUrl}/api/v1/chat/ws?token=${encodeURIComponent(token)}`;
        let ws: WebSocket | null = null;
        let accumulated = '';
        let done = false;

        try {
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                ws!.send(JSON.stringify({ message, policy_id: policy_id ?? null }));
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'token' && data.text) {
                        accumulated += data.text;
                        onToken(data.text);
                    } else if (data.type === 'done') {
                        done = true;
                        onDone(accumulated);
                        ws?.close();
                    } else if (data.type === 'error') {
                        onError(data.detail || 'server_error');
                        ws?.close();
                    }
                } catch {
                    // Ignore JSON parse errors
                }
            };

            ws.onerror = () => {
                if (!done) onError('websocket_error');
            };

            ws.onclose = (ev) => {
                if (!done && ev.code !== 1000) {
                    // Unexpected close — treat accumulated text as done if we have any
                    if (accumulated) {
                        onDone(accumulated);
                    } else {
                        onError('connection_closed');
                    }
                }
            };
        } catch (err) {
            console.error('[AI_WS] WebSocket init error:', err);
            onError('init_error');
        }

        // Return cleanup function
        return () => {
            if (ws && ws.readyState < WebSocket.CLOSING) {
                ws.close(1000, 'component unmounted');
            }
        };
    },
};
