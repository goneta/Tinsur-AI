'use client';

import React, { useState, useCallback } from 'react';
import { useTranslation } from 'next-i18next';
import { formatAmountForInput, parseAmount, getDecimalSeparator } from '@/lib/currency';

interface CurrencyInputProps {
  value: number;
  onChange: (value: number) => void;
  onBlur?: () => void;
  placeholder?: string;
  label?: string;
  error?: string;
  disabled?: boolean;
  className?: string;
}

/**
 * CurrencyInput component
 * Input field for currency amounts with automatic formatting
 * Displays as "1000,00 FCFA" (FR) or "1000.00 FCFA" (EN)
 */
export const CurrencyInput: React.FC<CurrencyInputProps> = ({
  value,
  onChange,
  onBlur,
  placeholder = '0.00',
  label,
  error,
  disabled = false,
  className = '',
}) => {
  const { i18n } = useTranslation();
  const [displayValue, setDisplayValue] = useState<string>(
    value ? formatAmountForInput(value, i18n.language as 'en' | 'fr') : ''
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const inputValue = e.target.value;
      setDisplayValue(inputValue);

      // Try to parse the value
      try {
        // Remove FCFA suffix if it exists and try to parse
        const cleanedValue = inputValue.replace(/\s*FCFA\s*$/i, '').trim();
        
        if (cleanedValue === '') {
          onChange(0);
          return;
        }

        // Parse using locale-aware decimal separator
        const decimalSep = getDecimalSeparator(i18n.language as 'en' | 'fr');
        const parts = cleanedValue.split(decimalSep);
        
        if (parts.length === 1 || parts.length === 2) {
          // Reconstruct with period as decimal for parsing
          const normalized = cleanedValue.replace(/\s/g, '').replace(decimalSep, '.');
          const numericValue = parseFloat(normalized);
          
          if (!isNaN(numericValue)) {
            onChange(numericValue);
          }
        }
      } catch (error) {
        console.error('Error parsing currency input:', error);
      }
    },
    [onChange, i18n.language]
  );

  const handleBlur = useCallback(() => {
    // Format the display value on blur
    try {
      if (displayValue.trim() === '') {
        setDisplayValue('');
        onChange(0);
      } else {
        // Parse and reformat
        const numericValue = parseAmount(displayValue + ' FCFA');
        if (!isNaN(numericValue)) {
          setDisplayValue(formatAmountForInput(numericValue, i18n.language as 'en' | 'fr'));
          onChange(numericValue);
        }
      }
    } catch (error) {
      console.error('Error formatting currency on blur:', error);
    }

    if (onBlur) {
      onBlur();
    }
  }, [displayValue, onChange, onBlur, i18n.language]);

  const handleFocus = useCallback((e: React.FocusEvent<HTMLInputElement>) => {
    // Select all on focus for easier editing
    e.target.select();
  }, []);

  return (
    <div className={`currency-input-wrapper ${className}`}>
      {label && (
        <label className="block text-sm font-semibold mb-2 text-gray-700">
          {label}
        </label>
      )}
      <div className="relative">
        <input
          type="text"
          value={displayValue}
          onChange={handleChange}
          onBlur={handleBlur}
          onFocus={handleFocus}
          placeholder={placeholder}
          disabled={disabled}
          className={`
            w-full px-4 py-2 border rounded-md
            focus:outline-none focus:ring-2 focus:ring-blue-500
            ${error ? 'border-red-500' : 'border-gray-300'}
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
          `}
        />
        <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 pointer-events-none">
          FCFA
        </span>
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}
    </div>
  );
};

export default CurrencyInput;
