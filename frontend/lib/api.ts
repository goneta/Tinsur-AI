/**
 * API client configuration with axios.
 */
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh and enhanced error logging
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Log detailed network error info
    if (error.message === 'Network Error') {
      console.error('Axios Network Error detected!', {
        url: error.config?.url,
        baseURL: error.config?.baseURL,
        method: error.config?.method,
        headers: error.config?.headers,
        error: error
      });
    }

    // If error is 401, we haven't retried yet, AND it's not the login endpoint itself
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/login')) {
      originalRequest._retry = true;

      try {
        if (typeof window !== 'undefined') {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            const response = await axios.post(`${API_URL}/auth/refresh`, {
              refresh_token: refreshToken,
            });

            const { access_token, refresh_token } = response.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);

            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Safely formats API error details into a string for React rendering.
 * Handes strings, arrays of Pydantic errors, and generic objects.
 */
export function formatApiError(detail: any): string {
  if (!detail) return '';

  // If already a string
  if (typeof detail === 'string') return detail;

  // If array of Pydantic/Standard errors: [{msg: "..."}, ...]
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item;
        return item?.msg || item?.message || JSON.stringify(item);
      })
      .join(', ');
  }

  // If single object: {message: "..."} or {detail: "..."}
  if (typeof detail === 'object') {
    return detail.msg || detail.message || detail.detail || JSON.stringify(detail);
  }

  return String(detail);
}


/**
 * Helper to construct full image URL from a relative path stored in the DB.
 */
export const getProfileImageUrl = (path?: string) => {
  if (!path) return undefined;
  if (path.startsWith('http')) return path;
  const baseUrl = api.defaults.baseURL?.replace('/api/v1', '') || 'http://localhost:8000';
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${cleanPath}`;
};

export default api;

