/**
 * i18n configuration and utilities
 */

export const DEFAULT_LANGUAGE = 'fr' as const;
export const FALLBACK_LANGUAGE = 'fr' as const;

export const LANGUAGES = {
  FR: 'fr',
  EN: 'en',
} as const;

export type Language = typeof LANGUAGES[keyof typeof LANGUAGES];

/**
 * Get the current language from localStorage or default to French
 */
export function getCurrentLanguage(): Language {
  if (typeof window === 'undefined') {
    return DEFAULT_LANGUAGE;
  }

  const stored = localStorage.getItem('i18nextLng');
  if (stored && (stored === 'en' || stored === 'fr')) {
    return stored;
  }

  return DEFAULT_LANGUAGE;
}

/**
 * Set the language in localStorage
 */
export function setLanguage(lang: Language): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('i18nextLng', lang);
  }
}

/**
 * Get language display name
 */
export function getLanguageName(lang: Language): string {
  const names: Record<Language, string> = {
    en: 'English',
    fr: 'Français',
  };
  return names[lang];
}

/**
 * Check if a language is RTL
 */
export function isRTL(lang: Language): boolean {
  return false; // French and English are both LTR
}
