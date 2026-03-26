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
};
