/**
 * Settings API client for managing user preferences and company settings.
 */
import api from './api';
import {
    UserSettings,
    UserSettingsUpdateRequest,
    CompanySettings,
    CompanyUpdateRequest,
} from '@/types/settings';

/**
 * Get current user's settings
 */
export const getUserSettings = async (): Promise<UserSettings> => {
    const response = await api.get('/settings');
    return response.data;
};

/**
 * Update current user's settings
 */
export const updateUserSettings = async (
    data: UserSettingsUpdateRequest
): Promise<UserSettings> => {
    const response = await api.put('/settings', data);
    return response.data;
};

/**
 * Get company settings (admin only)
 */
export const getCompanySettings = async (): Promise<CompanySettings> => {
    const response = await api.get('/settings/company');
    return response.data;
};

/**
 * Update company settings (admin only)
 */
export const updateCompanySettings = async (
    data: CompanyUpdateRequest
): Promise<CompanySettings> => {
    const response = await api.put('/settings/company', data);
    return response.data;
};

/**
 * Upload company logo (admin only)
 */
export const uploadCompanyLogo = async (
    file: File
): Promise<{ message: string; logo_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/settings/company/logo', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};
