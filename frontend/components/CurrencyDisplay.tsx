'use client';

import React from 'react';
import { useTranslation } from 'next-i18next';
import { formatAmount } from '@/lib/currency';

interface CurrencyDisplayProps {
  amount: number;
  locale?: 'en' | 'fr';
  size?: 'small' | 'medium' | 'large';
  className?: string;
  showCurrency?: boolean;
}

/**
 * CurrencyDisplay component
 * Displays amounts in FCFA format: "1000,00 FCFA" (FR) or "1000.00 FCFA" (EN)
 */
export const CurrencyDisplay: React.FC<CurrencyDisplayProps> = ({
  amount,
  locale,
  size = 'medium',
  className = '',
  showCurrency = true,
}) => {
  const { i18n } = useTranslation();
  
  // Use provided locale or fall back to i18n language
  const effectiveLocale = (locale || i18n.language) as 'en' | 'fr';
  
  // Format the amount
  const formatted = formatAmount(amount, effectiveLocale);
  
  // Remove FCFA if not showing currency
  const displayText = showCurrency ? formatted : formatted.replace(' FCFA', '');
  
  // Size classes
  const sizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg',
  };
  
  return (
    <span className={`${sizeClasses[size]} font-semibold ${className}`}>
      {displayText}
    </span>
  );
};

export default CurrencyDisplay;
