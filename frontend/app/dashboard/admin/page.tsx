'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PermissionMatrix } from '@/components/admin/permission-matrix';
import { UserManagement } from '@/components/admin/user-management';
import { SuperAdminAISettings } from '@/components/admin/super-admin-ai-settings';
import { Users, Shield, FileText, Bot, Crown } from 'lucide-react';
import PremiumPolicies from './premium-policies/page';
import PolicyServices from './services/page';
import TranslationsPage from './translations/page';
import { ShieldCheck, Percent, Globe } from 'lucide-react';
import { FinancialSettings } from '@/components/admin/financial-settings';

import { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/language-context';

export default function AdminPage() {
    const { t } = useLanguage();
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    if (!isMounted) return null;
    return (
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('admin.console', 'Administration Console')}</h2>
                    <p className="text-muted-foreground">{t('admin.desc', 'System-wide settings and access control.')}</p>
                </div>
            </div>

            <Tabs defaultValue="users" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="users">
                        <Users className="mr-2 h-4 w-4" />
                        {t('admin.tabs.users', 'Users & Teams')}
                    </TabsTrigger>
                    <TabsTrigger value="permissions">
                        <Shield className="mr-2 h-4 w-4" />
                        {t('admin.tabs.permissions', 'Permissions & Roles')}
                    </TabsTrigger>
                    <TabsTrigger value="audit">
                        <FileText className="mr-2 h-4 w-4" />
                        {t('admin.tabs.audit', 'Audit Logs')}
                    </TabsTrigger>
                    <TabsTrigger value="ai-config">
                        <Bot className="mr-2 h-4 w-4" />
                        {t('admin.tabs.ai', 'Global AI Configuration')}
                    </TabsTrigger>
                    <TabsTrigger value="premium-policies">
                        <Crown className="mr-2 h-4 w-4" />
                        {t('admin.tabs.policies', 'Premium Policies')}
                    </TabsTrigger>
                    <TabsTrigger value="policy-services">
                        <ShieldCheck className="mr-2 h-4 w-4" />
                        {t('admin.tabs.services', 'Policy Services')}
                    </TabsTrigger>
                    <TabsTrigger value="financials">
                        <Percent className="mr-2 h-4 w-4" />
                        {t('admin.tabs.financials', 'Interest & Fees / Tax')}
                    </TabsTrigger>
                    <TabsTrigger value="translations">
                        <Globe className="mr-2 h-4 w-4" />
                        {t('admin.tabs.translations', 'Translations')}
                    </TabsTrigger>
                </TabsList>

                {/* Users Tab */}
                <TabsContent value="users" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>{t('admin.users.title', 'User Management')}</CardTitle>
                            <CardDescription>{t('admin.users.desc', 'Manage users, invite team members, and assign roles.')}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <UserManagement />
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Permissions Tab */}
                <TabsContent value="permissions" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>{t('admin.permissions.title', 'Access Control')}</CardTitle>
                            <CardDescription>{t('admin.permissions.desc', 'Configure Role-Based Access Control (RBAC) user Permissions.')}</CardDescription>
                        </CardHeader>
                        <CardContent className="p-0 md:p-6 md:pt-2">
                            <PermissionMatrix />
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Audit Tab Placeholder */}
                <TabsContent value="audit" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>{t('admin.audit.title', 'System Audit Logs')}</CardTitle>
                            <CardDescription>{t('admin.audit.desc', 'View system-wide activity and security events.')}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-muted-foreground py-8 text-center">{t('admin.audit.coming_soon', 'Audit logging module coming soon.')}</p>
                        </CardContent>
                    </Card>
                </TabsContent>
                {/* AI Configuration Tab */}
                <TabsContent value="ai-config" className="space-y-4">
                    <SuperAdminAISettings />
                </TabsContent>

                {/* Premium Policies Tab */}
                <TabsContent value="premium-policies" className="space-y-4">
                    <PremiumPolicies />
                </TabsContent>

                {/* Policy Services Tab */}
                <TabsContent value="policy-services" className="space-y-4">
                    <PolicyServices />
                </TabsContent>

                {/* Interest & Fees Tab */}
                <TabsContent value="financials" className="space-y-4">
                    <FinancialSettings />
                </TabsContent>

                {/* Translations Tab */}
                <TabsContent value="translations" className="space-y-4">
                    <TranslationsPage />
                </TabsContent>
            </Tabs>
        </div>
    );
}
