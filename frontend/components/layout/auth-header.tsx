"use client"

import Link from "next/link"
import { LanguageSwitcher } from "@/components/language-switcher"

export function AuthHeader() {
    return (
        <header className="absolute top-0 w-full z-10 p-6 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
                <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
                    Tinsur.AI
                </span>
            </Link>

            <LanguageSwitcher />
        </header>
    )
}
