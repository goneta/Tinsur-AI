import React from 'react';
import { useLanguage } from "@/contexts/language-context";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

/**
 * Example component demonstrating the use of the translation system.
 * 
 * To use this in your component:
 * 1. Import `useLanguage` from the language context.
 * 2. Destructure the `t` function.
 * 3. Call `t(key, defaultText)`.
 */
export function TranslationExample() {
    const { t, language } = useLanguage();

    return (
        <Card>
            <CardHeader>
                <CardTitle>
                    {t("example.title", "Translation Example")}
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <p>
                    {t("example.current_language", "Current language is: ")}
                    <span className="font-bold uppercase">{language}</span>
                </p>

                <div className="p-4 bg-slate-100 rounded">
                    <p className="text-sm text-slate-600 mb-2">
                        {t("example.demo_text_label", "Translated Content:")}
                    </p>
                    <p className="text-lg">
                        {t("example.demo_content", "This text can be overridden by the backend or found in local JSON files.")}
                    </p>
                </div>

                <div className="flex gap-2">
                    <button className="px-4 py-2 bg-primary text-white rounded">
                        {t("common.save", "Save")}
                    </button>
                    <button className="px-4 py-2 border rounded">
                        {t("common.cancel", "Cancel")}
                    </button>
                </div>
            </CardContent>
        </Card>
    );
}
