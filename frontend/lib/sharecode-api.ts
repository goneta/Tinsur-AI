import { api } from './api';

export interface ShareCode {
    id: string;
    code: string;
    share_type: string; // 'B2B', 'B2C', 'B2E', 'E2C', 'E2E', 'C2C'
    recipient_ids: string[];
    status: string; // 'active', 'revoked', 'used'
    created_at: string;
    expires_at?: string;
    qr_code_base64?: string;
}

export interface ShareCodeCreate {
    share_type: string;
    recipient_ids: string[];
}

export const createShareCode = async (data: ShareCodeCreate): Promise<ShareCode> => {
    const response = await api.post('/share-codes/', data);
    return response.data;
};

export const getShareCodes = async (): Promise<ShareCode[]> => {
    const response = await api.get('/share-codes/');
    return response.data;
};

export const revokeShareCode = async (id: string): Promise<ShareCode> => {
    const response = await api.delete(`/share-codes/${id}`);
    return response.data;
};
