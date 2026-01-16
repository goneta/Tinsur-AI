"use client"

import React, { createContext, useContext, useEffect, useState } from "react"
import { useAuth } from "@/lib/auth"

interface BrandingContextType {
    logoUrl: string | null
    primaryColor: string
    secondaryColor: string
}

const BrandingContext = createContext<BrandingContextType>({
    logoUrl: null,
    primaryColor: "#000000",
    secondaryColor: "#e6e8eb",
})

export const useBranding = () => useContext(BrandingContext)

export function BrandingProvider({ children }: { children: React.ReactNode }) {
    const { user } = useAuth()
    const [branding, setBranding] = useState<BrandingContextType>({
        logoUrl: null,
        primaryColor: "#000000",
        secondaryColor: "#e6e8eb",
    })

    useEffect(() => {
        if (user) {
            const newBranding = {
                logoUrl: user.company_logo_url || null,
                primaryColor: user.primary_color || "#000000",
                secondaryColor: user.secondary_color || "#e6e8eb",
            }
            setBranding(newBranding)

            // Inject CSS variables into :root
            const root = document.documentElement
            root.style.setProperty("--primary", newBranding.primaryColor)
            root.style.setProperty("--secondary", newBranding.secondaryColor)

            // Optionally set sidebar-primary to match
            root.style.setProperty("--sidebar-primary", newBranding.primaryColor)

            // Log for debugging (can be removed later)
            console.log("Applied branding:", newBranding)
        } else {
            // Reset to defaults on logout
            const root = document.documentElement
            root.style.removeProperty("--primary")
            root.style.removeProperty("--secondary")
            root.style.removeProperty("--sidebar-primary")

            setBranding({
                logoUrl: null,
                primaryColor: "#000000",
                secondaryColor: "#e6e8eb",
            })
        }
    }, [user])

    return (
        <BrandingContext.Provider value={branding}>
            {children}
        </BrandingContext.Provider>
    )
}
