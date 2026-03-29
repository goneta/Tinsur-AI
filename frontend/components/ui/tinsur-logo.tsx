"use client";

import React from "react";
import { Shield } from "lucide-react";
import { useBranding } from "@/components/branding-provider";
import Image from "next/image";

interface TinsurLogoProps {
    className?: string;
    size?: number;
    href?: string;
    responsive?: boolean;
}

export function TinsurLogo({ className = "", size = 40, href = "/", responsive = false }: TinsurLogoProps) {
    const { logoUrl, primaryColor } = useBranding();
    const [imageError, setImageError] = React.useState(false);

    const responsiveClass = responsive ? 'w-12 h-12 sm:w-16 md:w-20' : '';
    const sizeStyle = responsive ? {} : { height: size, width: 'auto' };

    // Try to use custom logo URL first
    if (logoUrl) {
        return (
            <a href={href} className={`inline-block hover:opacity-80 transition-opacity ${className}`}>
                <img
                    src={logoUrl}
                    alt="Company Logo"
                    className={`object-contain ${className}`}
                    style={sizeStyle}
                    crossOrigin="anonymous"
                    onError={() => setImageError(true)}
                />
            </a>
        );
    }

    // Fallback to PNG logo from public assets if available
    if (!imageError) {
        return (
            <a href={href} className={`inline-block hover:opacity-80 transition-opacity ${className}`}>
                <Image
                    src="/images/tinsurAI_logo.png"
                    alt="Tinsur.AI Logo"
                    width={96}
                    height={96}
                    priority
                    className={`object-contain ${responsiveClass} ${className}`}
                    style={responsiveClass ? {} : sizeStyle}
                    onError={() => setImageError(true)}
                />
            </a>
        );
    }

    // Fallback to SVG icon + text
    return (
        <a href={href} className={`inline-flex items-center gap-2 hover:opacity-80 transition-opacity ${className}`} style={{ color: primaryColor }}>
            <Shield size={size} fill={primaryColor} className="text-white" />
            <span className="font-bold tracking-tight" style={{ fontSize: size * 0.6 }}>
                Tinsur.AI
            </span>
        </a>
    );
}
