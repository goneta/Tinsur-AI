"use client";

import React from "react";
import { Shield } from "lucide-react";
import { useBranding } from "@/components/branding-provider";

interface TinsurLogoProps {
    className?: string;
    size?: number;
}

export function TinsurLogo({ className = "", size = 40 }: TinsurLogoProps) {
    const { logoUrl, primaryColor } = useBranding();

    if (logoUrl) {
        return (
            <img
                src={logoUrl}
                alt="Company Logo"
                className={`object-contain ${className}`}
                style={{ height: size, width: 'auto' }}
                crossOrigin="anonymous" // Important for html2canvas
            />
        );
    }

    return (
        <div className={`flex items-center gap-2 ${className}`} style={{ color: primaryColor }}>
            <Shield size={size} fill={primaryColor} className="text-white" />
            <span className="font-bold tracking-tight" style={{ fontSize: size * 0.6 }}>
                Tinsur.AI
            </span>
        </div>
    );
}
