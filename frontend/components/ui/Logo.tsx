'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Shield } from 'lucide-react';

export type LogoVariant = 'full' | 'icon-only' | 'text-only';
export type LogoTheme = 'dark' | 'light' | 'auto';

interface LogoProps {
  /**
   * Size in pixels (height reference)
   * @default 40
   */
  size?: number;

  /**
   * Variant: 'full' (icon + text), 'icon-only', 'text-only'
   * @default 'full'
   */
  variant?: LogoVariant;

  /**
   * Theme: 'dark' (black), 'light' (white), 'auto' (system preference)
   * @default 'auto'
   */
  theme?: LogoTheme;

  /**
   * Optional className for additional styling
   */
  className?: string;

  /**
   * Optional link href - wraps logo in Link component
   */
  href?: string;

  /**
   * Whether to use fallback (lucide icon) if SVG fails to load
   * @default true
   */
  useFallback?: boolean;

  /**
   * Custom alt text
   * @default 'Tinsur.AI Logo'
   */
  alt?: string;

  /**
   * Whether to show image or not
   * @default true
   */
  showImage?: boolean;
}

/**
 * Tinsur.AI Logo Component
 * Responsive, accessible logo with multiple variants and themes
 *
 * Usage:
 * <Logo size={40} variant="full" theme="dark" href="/" />
 * <Logo size={32} variant="icon-only" theme="auto" />
 * <Logo size={24} variant="text-only" />
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

  // Detect system dark mode preference
  React.useEffect(() => {
    if (theme === 'auto') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDarkMode(isDark);

      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e: MediaQueryListEvent) => setIsDarkMode(e.matches);

      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      setIsDarkMode(theme === 'dark');
    }
  }, [theme]);

  // Determine which logo file to use
  const getLogoSrc = () => {
    if (variant === 'icon-only') {
      return '/logo-icon.svg';
    }
    return isDarkMode ? '/logo-dark.svg' : '/logo-light.svg';
  };

  // Fallback: Lucide Icon + Text
  const renderFallback = () => {
    const iconColor = isDarkMode ? '#000000' : '#ffffff';
    const textColor = isDarkMode ? 'text-black' : 'text-white';

    if (variant === 'icon-only') {
      return (
        <div
          className="flex items-center justify-center"
          style={{ width: size, height: size }}
          role="img"
          aria-label={alt}
        >
          <Shield
            size={size}
            fill={iconColor}
            color={iconColor}
            strokeWidth={1.5}
          />
        </div>
      );
    }

    if (variant === 'text-only') {
      return (
        <div
          className={`flex items-baseline gap-1 font-bold tracking-tight ${textColor}`}
          style={{ fontSize: size * 0.7 }}
          role="img"
          aria-label={alt}
        >
          <span>Tinsur</span>
          <span style={{ fontSize: size * 0.35 }}>AI</span>
        </div>
      );
    }

    // Full variant
    return (
      <div className={`flex items-center gap-2 ${textColor}`} role="img" aria-label={alt}>
        <div style={{ width: size, height: size, flexShrink: 0 }}>
          <Shield
            size={size}
            fill={iconColor}
            color={iconColor}
            strokeWidth={1.5}
          />
        </div>
        <div
          className="flex items-baseline gap-1 font-bold tracking-tight"
          style={{ fontSize: size * 0.7 }}
        >
          <span>Tinsur</span>
          <span style={{ fontSize: size * 0.35 }}>AI</span>
        </div>
      </div>
    );
  };

  const content = (
    <div className={`inline-flex items-center ${className}`}>
      {showImage && !imageError ? (
        <svg
          viewBox="0 0 200 60"
          width={variant === 'icon-only' ? size : size * 5.5}
          height={size}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          onError={() => useFallback && setImageError(true)}
          role="img"
          aria-label={alt}
        >
          {/* Dynamically load the SVG content */}
          {variant === 'icon-only' ? (
            <g>
              <path
                d="M10 8 L10 24 C10 32 16 38 30 41 C44 38 50 32 50 24 L50 8 Z"
                fill={isDarkMode ? '#000000' : '#ffffff'}
                stroke={isDarkMode ? '#000000' : '#ffffff'}
                strokeWidth="1.5"
                strokeLinejoin="round"
              />
              <path
                d="M22 28 L26 32 L34 22"
                stroke={isDarkMode ? '#ffffff' : '#000000'}
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                fill="none"
              />
            </g>
          ) : (
            <>
              {/* Shield Icon */}
              <g>
                <path
                  d="M20 10 L20 28 C20 38 28 45 38 48 C48 45 56 38 56 28 L56 10 Z"
                  fill={isDarkMode ? '#000000' : '#ffffff'}
                  stroke={isDarkMode ? '#000000' : '#ffffff'}
                  strokeWidth="1.5"
                  strokeLinejoin="round"
                />
                <path
                  d="M32 32 L36 36 L44 26"
                  stroke={isDarkMode ? '#ffffff' : '#000000'}
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  fill="none"
                />
              </g>

              {/* Text */}
              {(variant as LogoVariant) !== 'icon-only' && (
                <>
                  <text
                    x="65"
                    y="37"
                    fontFamily="system-ui, -apple-system, sans-serif"
                    fontSize="24"
                    fontWeight="700"
                    fill={isDarkMode ? '#000000' : '#ffffff'}
                    letterSpacing="-0.5"
                  >
                    Tinsur
                  </text>
                  <text
                    x="65"
                    y="52"
                    fontFamily="system-ui, -apple-system, sans-serif"
                    fontSize="10"
                    fontWeight="600"
                    fill={isDarkMode ? '#000000' : '#ffffff'}
                    letterSpacing="1"
                  >
                    .AI
                  </text>
                </>
              )}
            </>
          )}
        </svg>
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
