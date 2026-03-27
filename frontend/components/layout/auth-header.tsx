"use client"

import { Logo } from "@/components/ui/Logo"
import { LanguageSwitcher } from "@/components/language-switcher"

export function AuthHeader() {
    return (
        <header className="absolute top-0 w-full z-10 p-6 flex items-center justify-between">
            <Logo 
                size={40} 
                variant="full" 
                theme="dark" 
                href="/" 
                className="hover:opacity-80 transition-opacity"
            />

            <LanguageSwitcher />
        </header>
    )
}
