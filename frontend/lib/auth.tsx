/**
 * Authentication context for managing user state.
 */
'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { User, LoginRequest, RegisterRequest, LoginResponse } from '@/types/user';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (data: LoginRequest, redirectTo?: string) => Promise<void>;
    loginWithGoogle: (token: string, userType: string) => Promise<void>;
    loginWithFacebook: (token: string, userType: string) => Promise<void>;
    register: (data: RegisterRequest) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
    ai_credits_balance: number;
    refreshCredits: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [aiCredits, setAiCredits] = useState<number>(0);
    const router = useRouter();

    const refreshCredits = async () => {
        try {
            const { subscriptionApi } = await import('@/lib/subscription-api');
            const status = await subscriptionApi.getStatus();
            setAiCredits(status.credits);
        } catch (error) {
            console.error('Failed to refresh AI credits:', error);
        }
    };

    // Load user from localStorage on mount (client-side only)
    useEffect(() => {
        const loadUser = async () => {
            if (typeof window === 'undefined') {
                setLoading(false);
                return;
            }

            const token = localStorage.getItem('access_token');
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                // key fix: race against a timeout so we never hang
                // Increased to 45s to accommodate cold starts/slow local SQLite
                const timeoutPromise = new Promise((_, reject) =>
                    setTimeout(() => reject(new Error('Auth check timed out')), 45000)
                );

                const response: any = await Promise.race([
                    api.get('/auth/me'),
                    timeoutPromise
                ]);

                setUser(response.data);
                // After loading user, fetch initial credits
                refreshCredits();
            } catch (error: any) {
                console.error('Failed to load user:', error);

                // Only clear tokens if it is NOT a timeout (server might just be slow)
                // This prevents forced logout loops during development/cold starts
                if (error.message !== 'Auth check timed out') {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                }
            } finally {
                setLoading(false);
            }
        };

        loadUser();
    }, []);

    const login = async (data: LoginRequest, redirectTo?: string) => {
        try {
            const response = await api.post<LoginResponse>('/auth/login', data);
            const { access_token, refresh_token, user: userData } = response.data;

            if (typeof window !== 'undefined') {
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', refresh_token);
            }
            setUser(userData);
            refreshCredits();

            if (redirectTo) {
                router.push(redirectTo);
            } else if (userData.role === 'client') {
                router.push('/portal/insurance-details');
            } else {
                router.push('/dashboard');
            }
        } catch (error: any) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    const loginWithGoogle = async (token: string, userType: string) => {
        try {
            setLoading(true);
            const response = await api.post<LoginResponse>('/auth/social/google', {
                token: token,
                user_type: userType
            });
            const { access_token, refresh_token, user: userData } = response.data;

            if (typeof window !== 'undefined') {
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', refresh_token);
            }
            setUser(userData);
            refreshCredits();

            if (userData.role === 'client') {
                router.push('/portal/insurance-details');
            } else {
                router.push('/dashboard');
            }
        } catch (error: any) {
            console.error('Google login failed:', error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const loginWithFacebook = async (token: string, userType: string) => {
        try {
            setLoading(true);
            const response = await api.post<LoginResponse>('/auth/social/facebook', {
                token: token,
                user_type: userType
            });
            const { access_token, refresh_token, user: userData } = response.data;

            if (typeof window !== 'undefined') {
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', refresh_token);
            }
            setUser(userData);
            refreshCredits();

            if (userData.role === 'client') {
                router.push('/portal/insurance-details');
            } else {
                router.push('/dashboard');
            }
        } catch (error: any) {
            console.error('Facebook login failed:', error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const register = async (data: RegisterRequest) => {
        try {
            await api.post('/auth/register', data);
            // After successful registration, log the user in
            await login({ email: data.email, password: data.password });
        } catch (error: any) {
            console.error('Registration failed:', error);
            throw new Error(error.response?.data?.detail || 'Registration failed');
        }
    };

    const logout = () => {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        }
        setUser(null);
        setAiCredits(0);
        router.push('/login');
    };

    const value = {
        user,
        loading,
        login,
        loginWithGoogle,
        loginWithFacebook,
        register,
        logout,
        isAuthenticated: !!user,
        ai_credits_balance: aiCredits,
        refreshCredits,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
