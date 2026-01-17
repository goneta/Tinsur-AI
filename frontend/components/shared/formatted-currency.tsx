import React from 'react';
import { cn } from '@/lib/utils';
import { useLanguage } from '@/contexts/language-context';

interface FormattedCurrencyProps {
    amount: number;
    className?: string; // Class for the amount
    symbolClassName?: string; // Class for the symbol
    contractSymbol?: boolean; // If true, makes symbol smaller by default
}

export function FormattedCurrency({
    amount,
    className,
    symbolClassName,
    contractSymbol = true
}: FormattedCurrencyProps) {
    const { currency, language } = useLanguage();

    const formattedNumber = new Intl.NumberFormat(language === 'fr' ? 'fr-FR' : 'en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);

    const symbol = currency === 'XOF' ? 'FCFA' : currency;

    // Default symbol size reduction if contractSymbol is true
    const defaultSymbolClass = contractSymbol ? "text-[0.6em] ml-1 align-baseline" : "ml-1";

    return (
        <span className={cn("whitespace-nowrap inline-flex items-baseline", className)}>
            <span>{formattedNumber}</span>
            <span className={cn(defaultSymbolClass, symbolClassName)}>{symbol}</span>
        </span>
    );
}
