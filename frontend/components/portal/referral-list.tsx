'use client';

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { formatCurrency } from "@/lib/utils"
import { format } from "date-fns"
import { useLanguage } from "@/contexts/language-context"
import { Referral } from "@/lib/portal-api" // Using the type from portal-api which might re-export or we use shared

export function ReferralList({ referrals }: { referrals: Referral[] }) {
    const { t } = useLanguage();

    return (
        <Card>
            <CardHeader>
                <CardTitle>{t('referrals.history', 'Referral History')}</CardTitle>
                <CardDescription>{t('referrals.history_desc', 'Track the status of your referred friends.')}</CardDescription>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>{t('referrals.code', 'Code Used')}</TableHead>
                            <TableHead>{t('referrals.status', 'Status')}</TableHead>
                            <TableHead>{t('referrals.reward', 'Reward')}</TableHead>
                            <TableHead className="text-right">{t('referrals.date', 'Date')}</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {referrals.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={4} className="h-24 text-center text-muted-foreground">
                                    {t('referrals.no_history', 'No referrals found yet. Invite some friends!')}
                                </TableCell>
                            </TableRow>
                        ) : (
                            referrals.map((referral) => (
                                <TableRow key={referral.id}>
                                    <TableCell className="font-mono text-xs">{referral.referral_code}</TableCell>
                                    <TableCell>
                                        <Badge variant={
                                            referral.status === 'converted' ? 'default' :
                                                referral.status === 'rewarded' ? 'default' :
                                                    referral.status === 'pending' ? 'secondary' : 'outline'
                                        }>
                                            {t(`referrals.status_${referral.status}`, referral.status)}
                                        </Badge>
                                    </TableCell>
                                    <TableCell>
                                        {referral.reward_paid ? (
                                            <span className="text-green-600 font-medium">+{formatCurrency(referral.reward_amount || 0)}</span>
                                        ) : (
                                            <span className="text-muted-foreground">{referral.reward_amount ? formatCurrency(referral.reward_amount) : '-'}</span>
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        {format(new Date(referral.created_at), 'MMM d, yyyy')}
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    )
}
