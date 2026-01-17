"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { translationApi } from '@/lib/translation-api';
import enTranslations from '@/messages/en.json';
import frTranslations from '@/messages/fr.json';

type Language = 'en' | 'fr';

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string, defaultText?: string) => string;
    translations: Record<string, string>;
    loading: boolean;
    currency: string;
    setCurrency: (currency: string) => void;
    formatPrice: (amount: number) => string;
}

// Flatten nested objects logic (helper)
function flattenMessages(nestedMessages: Record<string, any>, prefix = ''): Record<string, string> {
    return Object.keys(nestedMessages).reduce((messages: Record<string, string>, key) => {
        let value = nestedMessages[key];
        let prefixedKey = prefix ? `${prefix}.${key}` : key;

        if (typeof value === 'string') {
            messages[prefixedKey] = value;
        } else {
            Object.assign(messages, flattenMessages(value, prefixedKey));
        }

        return messages;
    }, {});
}

const LOCAL_TRANSLATIONS: Record<Language, Record<string, string>> = {
    'en': flattenMessages(enTranslations),
    'fr': flattenMessages(frTranslations),
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
    const [language, setLanguageState] = useState<Language>('fr'); // Default to server-match
    // Initialize with local files to prevent flicker
    const [translations, setTranslations] = useState<Record<string, string>>(LOCAL_TRANSLATIONS['fr']);
    const [loading, setLoading] = useState(false); // No need to load if we have local

    // Hydrate from localStorage only on client mount
    useEffect(() => {
        const savedLang = localStorage.getItem('app_language') as Language;
        if (savedLang && (savedLang === 'en' || savedLang === 'fr') && savedLang !== language) {
            setLanguageState(savedLang);
            setTranslations(LOCAL_TRANSLATIONS[savedLang]);
        }
    }, []);

    // Fetch translations when language changes (backend overrides)
    useEffect(() => {
        // Reset to local immediately when language changes
        setTranslations(prev => ({
            ...LOCAL_TRANSLATIONS[language],
            ...prev
        }));

        async function loadTranslations() {
            try {
                const map = await translationApi.getMap(language);
                // Merge backend keys over local keys
                setTranslations(prev => ({
                    ...LOCAL_TRANSLATIONS[language],
                    ...map
                }));
            } catch (e) {
                console.error("Failed to load backend translations, using local fallback", e);
            }
        }
        loadTranslations();
    }, [language]);

    const setLanguage = (lang: Language) => {
        setLanguageState(lang);
        localStorage.setItem('app_language', lang);
    };

    const [currency, setCurrencyState] = useState<string>('XOF');

    useEffect(() => {
        const savedCurrency = localStorage.getItem('app_currency');
        if (savedCurrency) {
            setCurrencyState(savedCurrency);
        }
    }, []);

    const setCurrency = (curr: string) => {
        setCurrencyState(curr);
        localStorage.setItem('app_currency', curr);
    };

    const t = (key: string, defaultText?: string): string => {
        return translations[key] || defaultText || key;
    };

    const formatPrice = (amount: number): string => {
        if (currency === 'XOF' || currency === 'FCFA') {
            return new Intl.NumberFormat(language === 'fr' ? 'fr-FR' : 'en-US', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(amount) + ' FCFA';
        }

        return new Intl.NumberFormat(language === 'fr' ? 'fr-FR' : 'en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage, t, translations, loading, currency, setCurrency, formatPrice }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
}
