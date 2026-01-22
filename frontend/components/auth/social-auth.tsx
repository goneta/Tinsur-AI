"use client";

import React from 'react';
import { Button } from "@/components/ui/button";
import { Mail, Facebook, Apple } from "lucide-react";
import { useLanguage } from '@/contexts/language-context';

interface SocialAuthProps {
    onEmailClick: () => void;
    isLoading?: boolean;
}

export function SocialAuth({ onEmailClick, isLoading }: SocialAuthProps) {
    const { t } = useLanguage();

    return (
        <div className="w-full space-y-4">
            {/* Primary: Google */}
            <Button
                variant="default"
                className="w-full h-14 rounded-full bg-[#1A1A1A] hover:bg-[#2A2A2A] text-white flex items-center justify-center gap-3 text-lg font-semibold transition-all"
                disabled={isLoading}
                onClick={() => console.log("Google Login")}
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
                <span>{t("auth.social.google", "Continue with Google")}</span>
            </Button>

            {/* Secondary: Facebook & Apple */}
            <div className="grid grid-cols-2 gap-4">
                <Button
                    variant="secondary"
                    className="h-14 rounded-[28px] bg-[#F1F3F5] hover:bg-[#E9ECEF] text-black flex items-center justify-center p-0 transition-all border-none"
                    disabled={isLoading}
                    onClick={() => console.log("Facebook Login")}
                >
                    <Facebook className="w-7 h-7 text-[#1877F2] fill-[#1877F2]" />
                </Button>
                <Button
                    variant="secondary"
                    className="h-14 rounded-[28px] bg-[#F1F3F5] hover:bg-[#E9ECEF] text-black flex items-center justify-center p-0 transition-all border-none"
                    disabled={isLoading}
                    onClick={() => console.log("Apple Login")}
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
                <span>{t("auth.social.email", "Continue with Email")}</span>
            </Button>
        </div>
    );
}
