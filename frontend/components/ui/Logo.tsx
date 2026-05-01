'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Shield } from 'lucide-react';

export type LogoVariant = 'full' | 'icon-only' | 'text-only';
export type LogoTheme = 'dark' | 'light' | 'auto';

interface LogoProps {
  /** Size in pixels (height reference) @default 40 */
  size?: number;
  /** Variant: 'full' (icon + text), 'icon-only', 'text-only' @default 'full' */
  variant?: LogoVariant;
  /** Theme: 'dark' (black), 'light' (white), 'auto' (system preference) @default 'auto' */
  theme?: LogoTheme;
  /** Optional className for additional styling */
  className?: string;
  /** Optional link href - wraps logo in Link component */
  href?: string;
  /** Whether to use fallback (lucide icon) if image fails to load @default true */
  useFallback?: boolean;
  /** Custom alt text @default 'Tinsur.AI Logo' */
  alt?: string;
  /** Whether to show image or not @default true */
  showImage?: boolean;
}

/**
 * Tinsur.AI Logo Component
 * Uses the actual tinsurAI_logo.png from public/images with responsive sizing.
 * Falls back to SVG shield + text if the image fails to load.
 *
 * Usage:
 *   <Logo size={40} variant="full" theme="dark" href="/" />
 *   <Logo size={32} variant="icon-only" theme="auto" />
 */
export function Logo({
  size = 40,
  variant = 'full',
  theme = 'auto',
  className = '',
  href,
  useFallback = true,
  alt = 'Tinsur.AI Logo',
  showImage = true,
}: LogoProps) {
  const [isDarkMode, setIsDarkMode] = React.useState(theme === 'dark');
  const [imageError, setImageError] = React.useState(false);

  React.useEffect(() => {
    if (theme === 'auto') {
      const isDark = document.documentElement.classList.contains('dark') ||
        window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDarkMode(isDark);

      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e: MediaQueryListEvent) => setIsDarkMode(e.matches);
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      setIsDarkMode(theme === 'dark');
    }
  }, [theme]);

  // Responsive width: logo image is roughly 3:1 aspect ratio
  const imgHeight = size;
  const imgWidth = variant === 'icon-only' ? size : Math.round(size * 3);

  // Fallback: Lucide Shield Icon + Text
  const renderFallback = () => {
    const iconColor = isDarkMode ? '#000000' : '#ffffff';
    const textColor = isDarkMode ? 'text-black' : 'text-white';

    if (variant === 'icon-only') {
      return (
        <div className="flex items-center justify-center" style={{ width: size, height: size }} role="img" aria-label={alt}>
          <Shield size={size} fill={iconColor} color={iconColor} strokeWidth={1.5} />
        </div>
      );
    }

    if (variant === 'text-only') {
      return (
        <div className={`flex items-baseline gap-1 font-bold tracking-tight ${textColor}`} style={{ fontSize: size * 0.7 }} role="img" aria-label={alt}>
          <span>Tinsur</span>
          <span style={{ fontSize: size * 0.35 }}>.AI</span>
        </div>
      );
    }

    return (
      <div className={`flex items-center gap-2 ${textColor}`} role="img" aria-label={alt}>
        <Shield size={size} fill={iconColor} color={iconColor} strokeWidth={1.5} />
        <div className="flex items-baseline gap-1 font-bold tracking-tight" style={{ fontSize: size * 0.7 }}>
          <span>Tinsur</span>
          <span style={{ fontSize: size * 0.35 }}>.AI</span>
        </div>
      </div>
    );
  };

  const content = (
    <div className={`inline-flex items-center ${className}`}>
      {showImage && !imageError ? (
        <Image
          src="/images/tinsurAI_logo.png"
          alt={alt}
          width={imgWidth}
          height={imgHeight}
          priority
          className="object-contain"
          style={{ height: imgHeight, width: 'auto', maxWidth: imgWidth }}
          onError={() => {
            if (useFallback) setImageError(true);
          }}
        />
      ) : (
        renderFallback()
      )}
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="inline-flex items-center hover:opacity-80 transition-opacity">
        {content}
      </Link>
    );
  }

  return content;
}

export default Logo;
