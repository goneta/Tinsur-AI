/**
 * Currency formatting utilities for FCFA
 * Formats amounts based on locale (French or English)
 */

export type Locale = 'en' | 'fr';

/**
 * Format an amount in FCFA currency
 * @param amount - The amount to format
 * @param locale - The locale ('en' or 'fr')
 * @returns Formatted string like "1,000.00 FCFA" (en) or "1 000,00 FCFA" (fr)
 */
export function formatAmount(amount: number, locale: Locale = 'fr'): string {
  const formatter = new Intl.NumberFormat(locale === 'en' ? 'en-US' : 'fr-FR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const formattedNumber = formatter.format(amount);
  return `${formattedNumber} FCFA`;
}

/**
 * Parse a formatted amount string back to a number
 * @param formattedString - String like "1,000.00 FCFA" or "1 000,00 FCFA"
 * @returns The numeric value
 */
export function parseAmount(formattedString: string): number {
  // Remove FCFA and whitespace
  const cleaned = formattedString.replace(/FCFA/g, '').trim();
  
  // Determine if it uses comma or period as decimal separator
  // If there's a comma, it's French format
  if (cleaned.includes(',')) {
    // French format: "1 000,00" -> replace spaces and convert
    return parseFloat(cleaned.replace(/\s/g, '').replace(',', '.'));
  } else {
    // English format: "1,000.00" -> parse directly
    return parseFloat(cleaned.replace(/,/g, ''));
  }
}

/**
 * Format an amount for display in currency input
 * @param amount - The amount to format
 * @param locale - The locale ('en' or 'fr')
 * @returns Formatted string without FCFA symbol (for input field)
 */
export function formatAmountForInput(amount: number, locale: Locale = 'fr'): string {
  const formatter = new Intl.NumberFormat(locale === 'en' ? 'en-US' : 'fr-FR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return formatter.format(amount);
}

/**
 * Get the decimal separator for a locale
 */
export function getDecimalSeparator(locale: Locale): string {
  return locale === 'en' ? '.' : ',';
}

/**
 * Get the thousands separator for a locale
 */
export function getThousandsSeparator(locale: Locale): string {
  return locale === 'en' ? ',' : ' ';
}
