import api from '@/lib/api';

export interface DocumentData {
    id: string;
    name: string;
    label: string;
    fileType: string;
    size: string;
    visibility: 'PUBLIC' | 'PRIVATE';
    scope?: string;
    isShareable?: boolean;
    reshareRule?: 'A' | 'B' | 'C';
    owner: string;
    date: string;
}

export interface DocumentsResponse {
    my_docs: DocumentData[];
    public_docs: DocumentData[];
    shared_with_me: DocumentData[];
}

export interface InterCompanyShare {
    id: string;
    resource_type: string;
    resource_id: string;
    shared_with_company_id: string;
    permissions: string;
    status: string;
    created_at: string;
}

export interface Referral {
    id: string;
    referral_code: string;
    referrer_client_id: string;
    referred_client_email: string;
    status: string;
    reward_amount: number;
    created_at: string;
}

export const collaborationService = {
    // Documents
    async getDocuments() {
        const response = await api.get<DocumentsResponse>('/documents/list');
        return response.data;
    },

    async uploadDocument(file: File, label: string) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('label', label);

        const response = await api.post<{ status: string; document: DocumentData; url: string }>('/documents/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    // Inter-Company Shares
    async getShares() {
        const response = await api.get<InterCompanyShare[]>('/inter-company/');
        return response.data;
    },

    async createShare(data: { resource_type: string; resource_id: string; shared_with_company_id: string; permissions: string }) {
        const response = await api.post<InterCompanyShare>('/inter-company/', data);
        return response.data;
    },

    // Referrals
    async getReferrals() {
        const response = await api.get<Referral[]>('/referrals/');
        return response.data;
    },

    async createReferral(data: { referred_client_email: string }) {
        const response = await api.post<Referral>('/referrals/', data);
        return response.data;
    }
};
