
import api from '@/lib/api';
import { CoInsuranceShare, CoInsuranceShareCreateRequest } from '@/types/co-insurance';

export const coInsuranceApi = {
    // Get all participants for a policy
    getShares: async (policyId: string) => {
        const response = await api.get<CoInsuranceShare[]>(`/co-insurance/${policyId}/shares`);
        return response.data;
    },

    // Add a participant
    addShare: async (policyId: string, data: CoInsuranceShareCreateRequest) => {
        // Post expects query params in the endpoint logic or json body? 
        // Our backend endpoint used simple params. FastAPI handles it automatically if they are in the body for POST usually, or query if specified. 
        // Let's check the endpoint again: add_policy_share(policy_id: uuid.UUID, company_id: uuid.UUID, share_percentage: float...
        // These will be expected as query params if not wrapped in a Pydantic model. 
        // To keep it simple, let's pass them as query params.
        const response = await api.post<CoInsuranceShare>(`/co-insurance/${policyId}/shares`, null, {
            params: data
        });
        return response.data;
    },

    // Remove a participant
    removeShare: async (shareId: string) => {
        await api.delete(`/co-insurance/shares/${shareId}`);
    }
};
