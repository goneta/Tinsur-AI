import api from '@/lib/api';
import { Payment, PaymentListResponse, PaymentProcessRequest, PaymentRefundRequest } from '@/types/payment';

export const paymentApi = {
    getPayments: async (params?: {
        page?: number;
        page_size?: number;
        status?: string;
        payment_method?: string;
        client_id?: string;
    }): Promise<PaymentListResponse> => {
        const queryParams = new URLSearchParams();
        if (params?.page) queryParams.append('page', params.page.toString());
        if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
        if (params?.status && params.status !== 'all') queryParams.append('status', params.status);
        if (params?.payment_method && params.payment_method !== 'all') queryParams.append('payment_method', params.payment_method);
        if (params?.client_id) queryParams.append('client_id', params.client_id);

        const response = await api.get(`/payments/?${queryParams.toString()}`);
        return response.data;
    },

    getPayment: async (id: string): Promise<Payment> => {
        const response = await api.get(`/payments/${id}`);
        return response.data;
    },

    processPayment: async (data: PaymentProcessRequest): Promise<Payment> => {
        const response = await api.post('/payments/process', data);
        return response.data;
    },

    refundPayment: async (id: string, data: PaymentRefundRequest): Promise<Payment> => {
        const response = await api.post(`/payments/${id}/refund`, data);
        return response.data;
    },

    getPaymentsByPolicy: async (policyId: string): Promise<Payment[]> => {
        const response = await api.get<Payment[]>(`/payments/policy/${policyId}`);
        return response.data;
    },
};
