
import { api } from '@/lib/api';
import { User } from '@/types/user';

export interface POSLocation {
    id: string;
    company_id: string;
    name: string;
    address?: string;
    city?: string;
    region?: string;
    manager_id?: string;
    is_active: boolean;
    created_at: string;
}

export interface POSLocationCreate {
    name: string;
    address?: string;
    city?: string;
    region?: string;
    manager_id?: string;
}

export interface POSInventory {
    id: string;
    pos_location_id: string;
    item_name: string;
    quantity: number;
    low_stock_threshold: number;
    sku?: string;
    unit_price?: number;
}

export interface POSStats {
    location_id: string;
    location_name: string;
    active_agents: number;
    total_policies_sold: number;
    total_premium_collected: number;
    total_quotes_generated: number;
}

export const posApi = {
    // Locations
    getLocations: async () => {
        const response = await api.get<POSLocation[]>('/pos/locations');
        return response.data;
    },

    getLocation: async (id: string) => {
        const response = await api.get<POSLocation>(`/pos/locations/${id}`);
        return response.data;
    },

    createLocation: async (data: POSLocationCreate) => {
        const response = await api.post<POSLocation>('/pos/locations', data);
        return response.data;
    },

    updateLocation: async (id: string, data: Partial<POSLocationCreate>) => {
        const response = await api.put<POSLocation>(`/pos/locations/${id}`, data);
        return response.data;
    },

    // Inventory
    getInventory: async (locationId: string) => {
        const response = await api.get<POSInventory[]>(`/pos/inventory/${locationId}`);
        return response.data;
    },

    addInventoryItem: async (data: any) => {
        const response = await api.post<POSInventory>('/pos/inventory', data);
        return response.data;
    },

    updateInventoryItem: async (itemId: string, data: any) => {
        const response = await api.put<POSInventory>(`/pos/inventory/${itemId}`, data);
        return response.data;
    },

    // Management (New)
    getAgents: async (locationId: string) => {
        const response = await api.get<User[]>(`/pos/locations/${locationId}/agents`);
        return response.data;
    },

    getStats: async (locationId: string) => {
        const response = await api.get<POSStats>(`/pos/locations/${locationId}/stats`);
        return response.data;
    }
};
