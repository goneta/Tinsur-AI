'use client';

import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { LayoutTemplate } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { PreviewState } from '@/types/ai-agent';
import { QuotePreview } from './previews/quote-preview';
import { QuoteSelectionPreview } from './previews/quote-selection-preview';
import { PolicyPreview } from './previews/policy-preview';
import { ClaimPreview } from './previews/claim-preview';
import { QuoteProgressPreview } from './previews/quote-progress-preview';
import { useLanguage } from '@/contexts/language-context';

interface RightPanelProps {
    previewState: PreviewState;
    onAction?: (action: string, data: any) => void;
}

export function RightPanel({ previewState, onAction }: RightPanelProps) {
    const { t } = useLanguage();

    const renderContent = () => {
        switch (previewState.type) {
            case 'quote':
                return <QuotePreview data={previewState.data} onAction={onAction} />;
            case 'quote_selection':
                return <QuoteSelectionPreview data={previewState.data} onAction={onAction} />;
            case 'policy':
                return <PolicyPreview data={previewState.data} onAction={onAction} />;
            case 'claim':
                return <ClaimPreview data={previewState.data} onAction={onAction} />;
            case 'quote_progress':
                return <QuoteProgressPreview data={previewState.data} />;
            case 'empty':
            default:
                return (
                    <div className="flex flex-col items-center justify-center h-[500px] text-muted-foreground p-8 text-center">
                        <div className="h-16 w-16 bg-muted/50 rounded-full flex items-center justify-center mb-4">
                            <LayoutTemplate className="h-8 w-8" />
                        </div>
                        <h3 className="text-lg font-semibold text-foreground mb-2">{t('ai_manager.preview_area')}</h3>
                        <p className="max-w-xs text-sm">
                            {t('ai_manager.preview_hint')}
                        </p>
                    </div>
                );
        }
    };

    return (
        <div className="flex h-full flex-col bg-background">
            {/* Header */}
            <div className="flex h-14 items-center justify-between border-b px-4">
                <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-sm">{t('ai_manager.preview_area')}</h3>
                    {previewState.type !== 'empty' && (
                        <Badge variant="outline" className="text-[10px] h-5 capitalize">
                            {previewState.type.replace('_', ' ')}
                        </Badge>
                    )}
                </div>
                <div className="flex items-center gap-1">
                    {/* Toolbar actions could go here */}
                </div>
            </div>

            {/* Document Content */}
            <ScrollArea className="flex-1 p-6">
                <div className="max-w-3xl mx-auto pb-10">
                    {renderContent()}
                </div>
            </ScrollArea>
        </div>
    );
}
