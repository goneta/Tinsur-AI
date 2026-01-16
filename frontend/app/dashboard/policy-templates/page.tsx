"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { useRouter } from "next/navigation"
import { Plus, FileText, Loader2 } from "lucide-react"

import { policyTemplateApi } from "@/lib/policy-template-api"
import { PolicyTemplate } from "@/types/policy-template"

import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { DataTable } from "@/components/ui/data-table"
import { columns } from "./columns"
import { useToast } from "@/components/ui/use-toast"

import { useLanguage } from '@/contexts/language-context';

export default function PolicyTemplatesPage() {
    const { t } = useLanguage()
    const router = useRouter()
    const { toast } = useToast()
    const [templates, setTemplates] = useState<PolicyTemplate[]>([])
    const [loading, setLoading] = useState(true)
    const [isMounted, setIsMounted] = useState(false)

    const loadTemplates = useCallback(async () => {
        setLoading(true)
        try {
            const data = await policyTemplateApi.getPolicyTemplates()
            setTemplates(data)
        } catch (error) {
            console.error("Failed to load policy templates:", error)
            toast({
                title: "Error",
                description: "Failed to load policy templates. Please try again.",
                variant: "destructive",
            })
        } finally {
            setLoading(false)
        }
    }, [toast])

    useEffect(() => {
        setIsMounted(true)
        loadTemplates()
    }, [loadTemplates])

    const handleView = useCallback((id: string) => {
        router.push(`/dashboard/policy-templates/${id}`)
    }, [router])

    const handleEdit = useCallback((template: PolicyTemplate) => {
        router.push(`/dashboard/policy-templates/${template.id}/edit`)
    }, [router])

    const handleDelete = useCallback(async (id: string) => {
        if (confirm("Are you sure you want to delete this template?")) {
            try {
                await policyTemplateApi.deletePolicyTemplate(id)
                toast({
                    title: "Success",
                    description: "Policy template deleted successfully.",
                })
                loadTemplates()
            } catch (error) {
                console.error("Failed to delete template:", error)
                toast({
                    title: "Error",
                    description: "Failed to delete template.",
                    variant: "destructive",
                })
            }
        }
    }, [toast, loadTemplates])

    const handleDuplicate = useCallback(async (id: string) => {
        try {
            await policyTemplateApi.duplicatePolicyTemplate(id)
            toast({
                title: "Success",
                description: "Policy template duplicated successfully.",
            })
            loadTemplates()
        } catch (error) {
            console.error("Failed to duplicate template:", error)
            toast({
                title: "Error",
                description: "Failed to duplicate template.",
                variant: "destructive",
            })
        }
    }, [toast, loadTemplates])

    const tableColumns = useMemo(
        () => columns(handleView, handleEdit, handleDelete, handleDuplicate),
        [handleView, handleEdit, handleDelete, handleDuplicate]
    )

    if (!isMounted) return null

    return (
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('policy_templates.title')}</h2>
                    <p className="text-muted-foreground">
                        {t('policy_templates.desc')}
                    </p>
                </div>
                <Button onClick={() => router.push("/dashboard/policy-templates/new")}>
                    <Plus className="mr-2 h-4 w-4" /> {t('policy_templates.create_template')}
                </Button>
            </div>

            <Card className="transition-all hover:shadow-sm">
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <FileText className="h-5 w-5 text-blue-500" />
                        <CardTitle>{t('policy_templates.available_templates')}</CardTitle>
                    </div>
                    <CardDescription>
                        {t('policy_templates.list_desc', 'A list of all active and inactive policy templates available for issuance.')}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-10 text-muted-foreground">
                            <Loader2 className="h-10 w-10 animate-spin mb-4" />
                            <p>{t('policy_templates.loading', 'Fetching templates...')}</p>
                        </div>
                    ) : templates.length === 0 ? (
                        <div className="text-center py-20 border-2 border-dashed rounded-lg bg-muted/20">
                            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4 opacity-20" />
                            <h3 className="text-lg font-medium">{t('policy_templates.no_templates', 'No templates found')}</h3>
                            <p className="text-sm text-muted-foreground max-w-xs mx-auto mt-1">
                                {t('policy_templates.empty_state_desc', "You haven't created any policy templates yet. Click 'New Template' to get started.")}
                            </p>
                        </div>
                    ) : (
                        <DataTable columns={tableColumns} data={templates} />
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
