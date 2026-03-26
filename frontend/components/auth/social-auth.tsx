"use client";

import React from 'react';
import { Button } from "@/components/ui/button";
import { Mail, Facebook, Apple } from "lucide-react";
import { useLanguage } from '@/contexts/language-context';
import { useGoogleLogin } from '@react-oauth/google';
import { useAuth } from '@/lib/auth';
import { toast } from 'sonner';

interface SocialAuthProps {
    onEmailClick: () => void;
    isLoading?: boolean;
    userType?: 'client' | 'company' | 'login';
}

export function SocialAuth({ onEmailClick, isLoading, userType = 'login' }: SocialAuthProps) {
    const { t } = useLanguage();
    const { loginWithGoogle, loginWithFacebook, loginWithApple } = useAuth();

    const googleLogin = useGoogleLogin({
        onSuccess: async (tokenResponse) => {
            try {
                // In mock mode, we just pass the access_token as the 'token'
                await loginWithGoogle(tokenResponse.access_token, userType);
                toast.success(t('Successfully authenticated with Google'));
            } catch (error) {
                console.error('Google login failed:', error);
                toast.error(t('Failed to authenticate with Google'));
            }
        },
        onError: () => {
            toast.error(t('Google Login Failed'));
        },
    });

    const handleFacebookLogin = async () => {
        try {
            // Check if we should use mock or real
            const appId = process.env.NEXT_PUBLIC_FACEBOOK_APP_ID;

            if (!appId || appId === "mock-fb-id") {
                const mockEmail = `mock-fb-${userType}-${Math.floor(Math.random() * 1000)}@social.tinsur.ai`;
                toast.promise(loginWithFacebook(mockEmail, userType), {
                    loading: 'Testing with Mock Facebook...',
                    success: 'Mock Facebook Signup/Login Successful!',
                    error: 'Mock Facebook Login Failed'
                });
                return;
            }

            // Real Facebook Login using global FB object (needs to be loaded in layout.tsx)
            // @ts-ignore
            if (window.FB) {
                // @ts-ignore
                window.FB.login((response: any) => {
                    if (response.authResponse) {
                        const token = response.authResponse.accessToken;
                        toast.promise(loginWithFacebook(token, userType), {
                            loading: t('Authenticating with Facebook...'),
                            success: t('Successfully authenticated with Facebook'),
                            error: t('Facebook authentication failed')
                        });
                    } else {
                        toast.error(t('Facebook login cancelled or failed'));
                    }
                }, { scope: 'public_profile' });
            } else {
                toast.error(t('Facebook SDK not loaded. Check your connection or configuration.'));
            }
        } catch (error) {
            console.error('Facebook login handler error:', error);
            toast.error(t('An error occurred during Facebook login'));
        }
    };

    const loadAppleSdk = React.useCallback(async () => {
        // @ts-ignore
        if (window.AppleID) return;

        await new Promise<void>((resolve, reject) => {
            const existing = document.getElementById('apple-sdk-manual') as HTMLScriptElement | null;
            if (existing) {
                existing.addEventListener('load', () => resolve(), { once: true });
                existing.addEventListener('error', () => reject(new Error('Failed to load Apple SDK')), { once: true });
                return;
            }

            const script = document.createElement('script');
            script.id = 'apple-sdk-manual';
            script.src = 'https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/auth/v1/appleid.auth.js';
            script.async = true;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Failed to load Apple SDK'));
            document.head.appendChild(script);
        });
    }, []);

    const initApple = React.useCallback(async () => {
        const clientId = process.env.NEXT_PUBLIC_APPLE_CLIENT_ID;
        if (!clientId || clientId === 'mock-apple-id') return;

        await loadAppleSdk();

        // @ts-ignore
        if (!window.AppleID) throw new Error('Apple SDK not available after load');

        // @ts-ignore
        window.AppleID.auth.init({
            clientId,
            scope: 'name email',
            redirectURI: window.location.origin + '/login',
            usePopup: true
        });
    }, [loadAppleSdk]);

    // Prime SDK in background, but we also hard-retry on click.
    React.useEffect(() => {
        initApple().catch((err) => console.warn('Apple SDK init deferred:', err));
    }, [initApple]);

    const handleAppleLogin = async () => {
        try {
            const clientId = process.env.NEXT_PUBLIC_APPLE_CLIENT_ID;

            if (!clientId || clientId === "mock-apple-id") {
                const mockEmail = `mock-apple-${userType}-${Math.floor(Math.random() * 1000)}@social.tinsur.ai`;
                toast.promise(loginWithApple(mockEmail, userType, "Apple", "User"), {
                    loading: 'Testing with Mock Apple...',
                    success: 'Mock Apple Signup/Login Successful!',
                    error: 'Mock Apple Login Failed'
                });
                return;
            }

            // Real Apple Login logic using Apple JS SDK
            await initApple();

            // @ts-ignore
            if (!window.AppleID) {
                toast.error(t('auth.social.sdk_loading', 'Apple SDK not loaded yet. Please wait or refresh the page.'));
                return;
            }

            try {
                // @ts-ignore
                const response = await window.AppleID.auth.signIn();
                if (response && response.authorization) {
                    const token = response.authorization.id_token || response.authorization.code;
                    if (!token) {
                        toast.error(t('auth.social.failed_generic', 'Apple login failed. Please try again.'));
                        return;
                    }

                    const firstName = response.user?.name?.firstName;
                    const lastName = response.user?.name?.lastName;

                    toast.promise(loginWithApple(token, userType, firstName, lastName), {
                        loading: t('auth.social.authenticating', 'Authenticating with Apple...'),
                        success: t('auth.social.success', 'Successfully authenticated with Apple'),
                        error: t('auth.social.failed', 'Apple authentication failed')
                    });
                }
            } catch (error: any) {
                console.error('Apple login error:', error);
                // Detail standard Apple error codes
                const errorMsg = error?.error;
                if (errorMsg === 'popup_closed_by_user') {
                    toast.error(t('auth.social.closed', 'Apple login window was closed'));
                } else if (errorMsg === 'access_denied') {
                    toast.error(t('auth.social.denied', 'Access denied for Apple login'));
                } else {
                    toast.error(t('auth.social.failed_generic', 'Apple login failed. Please try again.'));
                }
            }
        } catch (error) {
            console.error('Apple login handler exception:', error);
            toast.error(t('auth.social.error', 'An error occurred during Apple login'));
        }
    };

    const labelPrefix = userType === 'login' ? 'auth.social.google' : 'auth.social.register_google';
    const defaultLabel = userType === 'login' ? 'Continue with Google' : t('register.social_google', 'Sign up with Google');

    return (
        <div className="w-full space-y-4">
            {/* Primary: Google */}
            <Button
                variant="default"
                className="w-full h-14 rounded-full bg-[#1A1A1A] hover:bg-[#2A2A2A] text-white flex items-center justify-center gap-3 text-lg font-semibold transition-all"
                disabled={isLoading}
                onClick={() => googleLogin()}
            >
                <svg viewBox="0 0 24 24" className="w-6 h-6 shrink-0" role="presentation">
                    <path
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                        fill="#4285F4"
                    />
                    <path
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-1 .67-2.28 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                        fill="#34A853"
                    />
                    <path
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.16H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.84l3.66-2.75z"
                        fill="#FBBC05"
                    />
                    <path
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.16l3.66 2.84c.87-2.6 3.3-4.53 12-4.53z"
                        fill="#EA4335"
                    />
                </svg>
                <span>{t(labelPrefix, defaultLabel)}</span>
            </Button>

            {/* Secondary: Facebook & Apple */}
            <div className="grid grid-cols-2 gap-4">
                <Button
                    variant="secondary"
                    className="h-14 rounded-[28px] bg-[#F1F3F5] hover:bg-[#E9ECEF] text-black flex items-center justify-center p-0 transition-all border-none"
                    disabled={isLoading}
                    onClick={handleFacebookLogin}
                >
                    <Facebook className="w-7 h-7 text-[#1877F2] fill-[#1877F2]" />
                </Button>
                <Button
                    variant="secondary"
                    className="h-14 rounded-[28px] bg-[#F1F3F5] hover:bg-[#E9ECEF] text-black flex items-center justify-center p-0 transition-all border-none"
                    disabled={isLoading}
                    onClick={handleAppleLogin}
                >
                    <Apple className="w-7 h-7 fill-black" />
                </Button>
            </div>

            {/* Divider */}
            <div className="flex items-center gap-4 py-2">
                <div className="flex-1 border-t border-dashed border-gray-300"></div>
                <span className="text-gray-400 font-medium text-sm">{t("auth.social.or", "OR")}</span>
                <div className="flex-1 border-t border-dashed border-gray-300"></div>
            </div>

            {/* Email Toggle */}
            <Button
                variant="secondary"
                className="w-full h-14 rounded-full bg-[#F1F3F5] hover:bg-[#E9ECEF] text-black flex items-center justify-center gap-3 text-lg font-semibold transition-all border-none"
                disabled={isLoading}
                onClick={onEmailClick}
            >
                <div className="bg-gray-300 p-1.5 rounded-lg">
                    <Mail className="w-5 h-5 text-gray-600 fill-gray-600" />
                </div>
                <span>{userType === 'login' ? t("auth.social.email", "Continue with Email") : t('register.social_email', 'Sign up with Email')}</span>
            </Button>

            {/* MOCK LOGIN (Only if client_id is missing or for rapid testing) */}
            {(process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID === undefined ||
                process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID === "" ||
                process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID === "mock-client-id") && (
                    <Button
                        variant="outline"
                        className="w-full h-12 rounded-full border-dashed border-2 border-orange-200 text-orange-600 hover:bg-orange-50 transition-all text-sm font-medium"
                        onClick={async () => {
                            const mockEmail = `mock-${userType}-${Math.floor(Math.random() * 1000)}@example.com`;
                            toast.promise(loginWithGoogle(mockEmail, userType), {
                                loading: 'Testing with Mock Google...',
                                success: 'Mock Signup/Login Successful!',
                                error: 'Mock Login Failed'
                            });
                        }}
                    >
                        <div className="bg-orange-100 p-1 rounded-full">
                            <svg viewBox="0 0 24 24" className="w-4 h-4 fill-orange-500">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" />
                            </svg>
                        </div>
                        <span>{t('auth.social.mock', 'DEMO: Test registration workflow (Mock)')}</span>
                    </Button>
                )}
        </div>
    );
}
