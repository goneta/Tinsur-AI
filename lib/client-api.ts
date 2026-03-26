import { api } from './api';
import { Client, ClientAutomobile, ClientHousing, ClientHealth, ClientLife, ClientDriver } from '@/types/client';

export const clientApi = {
    // Core Client Operations
    getClients: async (params?: any) => {
        const response = await api.get<Client[]>('/clients/', { params });
        return response.data;
    },

    getClient: async (id: string) => {
        const response = await api.get<Client>(`/clients/${id}/`);
        return response.data;
    },

    getMyClient: async () => {
        const response = await api.get<Client>('/clients/me/');
        return response.data;
    },

    createClient: async (data: any) => {
        const response = await api.post<Client>('/clients/', data);
        return response.data;
    },

    updateClient: async (id: string, data: any) => {
        const response = await api.put<Client>(`/clients/${id}/`, data);
        return response.data;
    },

    deleteClient: async (id: string) => {
        await api.delete(`/clients/${id}/`);
    },

    // Details Operations
    updateAutomobileDetails: async (clientId: string, data: Partial<ClientAutomobile>) => {
        const response = await api.put(`/clients/${clientId}/automobile/`, data);
        return response.data;
    },

    updateVehicle: async (clientId: string, vehicleId: string, data: Partial<ClientAutomobile>) => {
        const response = await api.put<ClientAutomobile>(`/clients/${clientId}/vehicles/${vehicleId}`, data);
        return response.data;
    },

    updateHousingDetails: async (clientId: string, data: Partial<ClientHousing>) => {
        const response = await api.put(`/clients/${clientId}/housing/`, data);
        return response.data;
    },

    updateHealthDetails: async (clientId: string, data: Partial<ClientHealth>) => {
        const response = await api.put(`/clients/${clientId}/health/`, data);
        return response.data;
    },

    updateLifeDetails: async (clientId: string, data: Partial<ClientLife>) => {
        const response = await api.put(`/clients/${clientId}/life/`, data);
        return response.data;
    },

    uploadProfilePicture: async (clientId: string, file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post<Client>(`/clients/${clientId}/profile-picture/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    // KYC & Verification
    parseKycDocument: async (imageUrl: string, docType: string = "identity_document") => {
        const response = await api.post('/kyc/parse-document/', {
            image_url: imageUrl,
            doc_type: docType
        });
        return response.data;
    },

    uploadAndParseKycDocument: async (file: File, docType: string = "identity_document", clientId?: string) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('doc_type', docType);
        if (clientId) formData.append('client_id', clientId);

        const response = await api.post('/kyc/upload-and-parse', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    updateKycStatus: async (clientId: string, status: string, notes?: string, results: any = {}) => {
        const response = await api.post(`/kyc/verify/${clientId}`, {
            status,
            notes,
            results
        });
        return response.data;
    },

    getKycStatus: async (clientId: string) => {
        const response = await api.get(`/kyc/status/${clientId}`);
        return response.data;
    },

    // Vehicle & Driver Operations
    createVehicle: async (clientId: string, data: any) => {
        const response = await api.post<ClientAutomobile>(`/clients/${clientId}/vehicles`, data);
        return response.data;
    },

    createDriver: async (clientId: string, data: any) => {
        const response = await api.post<ClientDriver>(`/clients/${clientId}/drivers`, data);
        return response.data;
    },

    updateDriver: async (clientId: string, driverId: string, data: any) => {
        const response = await api.put<ClientDriver>(`/clients/${clientId}/drivers/${driverId}`, data);
        return response.data;
    },

    uploadDriverLicense: async (clientId: string, driverId: string, file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post<ClientDriver>(`/clients/${clientId}/drivers/${driverId}/license`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },
    uploadVehicleImage: async (clientId: string, vehicleId: string, file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post(`/clients/${clientId}/vehicles/${vehicleId}/image`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    }
};

