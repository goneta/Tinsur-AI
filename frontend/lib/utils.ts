import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number, currency?: string, locale: string = 'fr-FR'): string {
  const resolvedCurrency =
    currency ||
    (typeof window !== 'undefined' ? (localStorage.getItem('app_currency') || 'XOF') : 'XOF');

  if (resolvedCurrency === 'XOF' || resolvedCurrency === 'FCFA') {
    return new Intl.NumberFormat(locale, {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount) + ' FCFA';
  }

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: resolvedCurrency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(new Date(date))
}
