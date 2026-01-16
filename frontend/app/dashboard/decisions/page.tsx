'use client';

import React from 'react';
import {
    Tabs,
    TabsContent,
    TabsList,
    TabsTrigger
} from '@/components/ui/tabs';
import {
    Gavel,
    ShieldCheck,
    RotateCcw
} from 'lucide-react';
import UnderwritingApprovals from './components/underwriting-approvals';
import RecoveryPipeline from './components/recovery-pipeline';

import { useLanguage } from '@/contexts/language-context';

export default function DecisionHubPage() {
    const { t } = useLanguage();
    return (
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
                        <Gavel className="h-8 w-8 text-blue-600" />
                        {t('decisions.title', 'Expert Decision Hub')}
                    </h2>
                    <p className="text-muted-foreground">
                        {t('decisions.desc', 'Centralized command center for risk approvals and financial recoveries.')}
                    </p>
                </div>
            </div>

            <Tabs defaultValue="underwriting" className="space-y-4">
                <TabsList className="grid w-full grid-cols-2 max-w-[400px]">
                    <TabsTrigger value="underwriting" className="flex items-center gap-2">
                        <ShieldCheck className="h-4 w-4" />
                        {t('decisions.tab_underwriting', 'Underwriting')}
                    </TabsTrigger>
                    <TabsTrigger value="recovery" className="flex items-center gap-2">
                        <RotateCcw className="h-4 w-4" />
                        {t('decisions.tab_recovery', 'Recovery')}
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="underwriting" className="space-y-4">
                    <UnderwritingApprovals />
                </TabsContent>

                <TabsContent value="recovery" className="space-y-4">
                    <RecoveryPipeline />
                </TabsContent>
            </Tabs>
        </div>
    );
}
