"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { RefreshCw, Activity, Plus } from "lucide-react"
import { paymentApi } from "@/lib/payment-api"
import { Payment } from "@/types/payment"
import { DataTable } from "@/components/ui/data-table"
import { columns } from "./columns" // Verify this import path is correct relative to page
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

import { useLanguage } from '@/contexts/language-context';

export default function PaymentsPage() {
    const { t, formatPrice } = useLanguage()
    const router = useRouter()
    const [payments, setPayments] = useState<Payment[]>([])
    const [loading, setLoading] = useState(true)

    const loadPayments = async () => {
        setLoading(true)
        try {
            // Fetch all for client-side filtering
            const data = await paymentApi.getPayments({
                // No generic 'limit' param on getPayments? PaymentList used page_size
                page_size: 1000
            })
            setPayments(data.payments)
        } catch (error) {
            console.error('Failed to load payments:', error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        loadPayments()
    }, [])

    const handleView = (id: string) => {
        router.push(`/dashboard/payments/${id}`)
    }

    return (
        <div className="flex-1 space-y-4 p-8 pt-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('payments.title')}</h2>
                    <p className="text-muted-foreground">{t('payments.desc')}</p>
                </div>
                <div className="flex items-center gap-2">
                    <Button onClick={() => router.push("/dashboard/payments/new")}>
                        <Plus className="mr-2 h-4 w-4" /> {t('payments.new_payment')}
                    </Button>
                    <Button variant="outline" size="sm" onClick={loadPayments}>
                        <RefreshCw className="mr-2 h-4 w-4" />
                        {t('payments.refresh')}
                    </Button>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>{t('payments.payment_list')}</CardTitle>
                    <CardDescription>
                        {t('payments.list_desc', 'A list of all payments recorded in the system.')}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="py-8 text-center text-muted-foreground">{t('common.loading', 'Loading payments...')}</div>
                    ) : payments.length === 0 ? (
                        <div className="flex flex-col items-center justify-center p-8 text-center border rounded-md">
                            <Activity className="h-10 w-10 text-muted-foreground mb-4" />
                            <h3 className="text-lg font-medium">{t('payments.no_payments', 'No payments found')}</h3>
                        </div>
                    ) : (
                        <DataTable
                            columns={columns(handleView, t, formatPrice)}
                            data={payments}
                        />
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
