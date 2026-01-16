"use client"

import { useState, useEffect } from "react"
import { Plus, Trash2, Key, Copy, Check } from "lucide-react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"

import { Button } from "@/components/ui/button"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useToast } from "@/components/ui/use-toast"
import { apiKeyApi, ApiKey } from "@/lib/api-keys-api"
import { Badge } from "@/components/ui/badge"
import { useLanguage } from "@/contexts/language-context"

const formSchema = z.object({
    name: z.string().min(2, "Name must be at least 2 characters."),
    agent_id: z.string().optional(),
})

export default function ApiKeysPage() {
    const { t } = useLanguage()
    const [keys, setKeys] = useState<ApiKey[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [isOpen, setIsOpen] = useState(false)
    const [newKey, setNewKey] = useState<string | null>(null)
    const { toast } = useToast()

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            name: "",
            agent_id: "",
        },
    })

    useEffect(() => {
        fetchKeys()
    }, [])

    const fetchKeys = async () => {
        try {
            const data = await apiKeyApi.getAll()
            setKeys(data)
        } catch (error) {
            toast({
                title: "Error fetching keys",
                description: "Could not load API keys.",
                variant: "destructive",
            })
        } finally {
            setIsLoading(false)
        }
    }

    const onSubmit = async (values: z.infer<typeof formSchema>) => {
        try {
            const created = await apiKeyApi.create(values)
            setKeys([...keys, created])
            setNewKey(created.plain_text_key || null)
            toast({
                title: "API Key Created",
                description: "Make sure to copy your key now. You won't see it again!",
            })
            form.reset()
        } catch (error) {
            toast({
                title: "Error creating key",
                description: "Could not create API key.",
                variant: "destructive",
            })
        }
    }

    const handleRevoke = async (id: string) => {
        if (!confirm("Are you sure you want to revoke this key? It will stop working immediately.")) return

        try {
            await apiKeyApi.revoke(id)
            setKeys(keys.filter((k) => k.id !== id))
            toast({
                title: "Key Revoked",
                description: "The API key has been revoked.",
            })
        } catch (error) {
            toast({
                title: "Error revoking key",
                description: "Could not revoke API key.",
                variant: "destructive",
            })
        }
    }

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text)
        toast({ title: "Copied to clipboard" })
    }

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('settings.keys.title', 'API Keys')}</h2>
                    <p className="text-muted-foreground">
                        {t('settings.keys.desc', 'Manage API keys for your AI Agents.')}
                    </p>
                </div>
                <Dialog open={isOpen} onOpenChange={(open) => {
                    setIsOpen(open)
                    if (!open) setNewKey(null) // Reset new key view when closing
                }}>
                    <DialogTrigger asChild>
                        <Button><Plus className="mr-2 h-4 w-4" /> {t('settings.keys.create_new', 'Create New Key')}</Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[425px]">
                        <DialogHeader>
                            <DialogTitle>{t('settings.keys.create_title', 'Create API Key')}</DialogTitle>
                            <DialogDescription>
                                {t('settings.keys.create_desc', 'Generate a new key for an agent.')}
                            </DialogDescription>
                        </DialogHeader>

                        {newKey ? (
                            <div className="space-y-4 py-4">
                                <div className="rounded-md bg-muted p-4">
                                    <p className="text-sm font-medium mb-2 text-destructive">{t('settings.keys.copy_warning', 'Make sure to copy this key now!')}</p>
                                    <div className="flex items-center gap-2">
                                        <code className="relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm font-semibold break-all">
                                            {newKey}
                                        </code>
                                        <Button variant="ghost" size="icon" onClick={() => copyToClipboard(newKey)}>
                                            <Copy className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </div>
                                <DialogFooter>
                                    <Button onClick={() => setIsOpen(false)}>{t('common.done', 'Done')}</Button>
                                </DialogFooter>
                            </div>
                        ) : (
                            <Form {...form}>
                                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                                    <FormField
                                        control={form.control}
                                        name="name"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>{t('settings.keys.name_label', 'Name')}</FormLabel>
                                                <FormControl>
                                                    <Input placeholder="e.g. OCR Agent Key" {...field} />
                                                </FormControl>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                    <FormField
                                        control={form.control}
                                        name="agent_id"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Agent ID (Optional)</FormLabel>
                                                <FormControl>
                                                    <Input placeholder="e.g. ocr_agent_v1" {...field} />
                                                </FormControl>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                    <DialogFooter>
                                        <Button type="submit">{t('settings.keys.generate_btn', 'Generate Key')}</Button>
                                    </DialogFooter>
                                </form>
                            </Form>
                        )}
                    </DialogContent>
                </Dialog>
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>{t('settings.keys.table.name', 'Name')}</TableHead>
                            <TableHead>{t('settings.keys.table.prefix', 'Prefix')}</TableHead>
                            <TableHead>{t('settings.keys.table.agent_id', 'Agent ID')}</TableHead>
                            <TableHead>{t('settings.keys.table.created', 'Created')}</TableHead>
                            <TableHead>{t('settings.keys.table.status', 'Status')}</TableHead>
                            <TableHead className="text-right">{t('common.actions', 'Actions')}</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {isLoading ? (
                            <TableRow>
                                <TableCell colSpan={6} className="text-center h-24">Loading...</TableCell>
                            </TableRow>
                        ) : keys.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={6} className="text-center h-24">{t('settings.keys.empty', 'No API keys found.')}</TableCell>
                            </TableRow>
                        ) : (
                            keys.map((key) => (
                                <TableRow key={key.id}>
                                    <TableCell className="font-medium">
                                        <div className="flex items-center gap-2">
                                            <Key className="h-4 w-4 text-muted-foreground" />
                                            {key.name}
                                        </div>
                                    </TableCell>
                                    <TableCell className="font-mono text-xs">{key.key_prefix}...</TableCell>
                                    <TableCell>{key.agent_id || "-"}</TableCell>
                                    <TableCell>{new Date(key.created_at).toLocaleDateString()}</TableCell>
                                    <TableCell>
                                        {key.is_active ? (
                                            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Active</Badge>
                                        ) : (
                                            <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">Revoked</Badge>
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            onClick={() => handleRevoke(key.id)}
                                            className="text-destructive hover:text-destructive hover:bg-destructive/10"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    )
}
