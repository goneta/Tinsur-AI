'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ImportWizard } from '@/components/import-export/import-wizard';
import { ExportWizard as ExportWizardComp } from '@/components/import-export/export-wizard';
import { Database, Upload, Download } from 'lucide-react';

import { useLanguage } from '@/contexts/language-context';

export default function ImportExportPage() {
    const { t } = useLanguage();

    return (
        <div className="p-8 max-w-6xl mx-auto space-y-8">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight">{t('import_export.title')}</h1>
                <p className="text-muted-foreground">
                    {t('import_export.desc')}
                </p>
            </div>

            <Tabs defaultValue="import" className="space-y-6">
                <TabsList className="grid w-full grid-cols-2 max-w-[400px]">
                    <TabsTrigger value="import" className="flex items-center gap-2">
                        <Upload className="h-4 w-4" />
                        {t('import_export.tab_import')}
                    </TabsTrigger>
                    <TabsTrigger value="export" className="flex items-center gap-2">
                        <Download className="h-4 w-4" />
                        {t('import_export.tab_export')}
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="import" className="space-y-4">
                    <ImportWizard />
                </TabsContent>

                <TabsContent value="export" className="space-y-4">
                    <ExportWizardComp />
                </TabsContent>
            </Tabs>
        </div>
    );
}
