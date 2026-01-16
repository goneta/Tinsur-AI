'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, Circle } from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';

interface QuoteProgressPreviewProps {
    data: {
        current_step: string;
        missing_count: number;
        total_fields: number;
        extracted_data: any;
        next_question: string;
    };
}

export function QuoteProgressPreview({ data }: QuoteProgressPreviewProps) {
    const { t } = useLanguage();
    const progress = Math.round(((data.total_fields - data.missing_count) / data.total_fields) * 100);

    // Define the steps logically
    const steps = [
        { label: t('quote.step_basic', "Basic Info"), key: ["client_name", "policy_type"] },
        { label: t('quote.step_coverage', "Coverage"), key: ["coverage_amount", "duration_months", "payment_frequency"] },
        { label: t('quote.step_vehicle', "Vehicle/Risk"), key: ["vehicle_value", "vehicle_age", "vehicle_mileage", "vehicle_registration"] },
        { label: t('quote.step_driver', "Driver/Legal"), key: ["license_number", "driver_dob"] }
    ];

    const isStepComplete = (keys: string[]) => {
        return keys.every(k => data.extracted_data[k] !== null && data.extracted_data[k] !== undefined);
    };

    return (
        <Card className="border-none shadow-none bg-transparent">
            <CardHeader className="px-0 pt-0">
                <div className="flex items-center justify-between mb-2">
                    <CardTitle className="text-xl font-bold">{t('quote.progress_title', 'Quote Progress')}</CardTitle>
                    <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
                        {progress}% {t('quote.complete', 'Complete')}
                    </Badge>
                </div>
                <Progress value={progress} className="h-2" />
            </CardHeader>
            <CardContent className="px-0 space-y-6">
                <div className="grid gap-4">
                    {steps.map((step, i) => {
                        const complete = isStepComplete(step.key);
                        const isCurrent = step.key.includes(data.current_step.toLowerCase().replace(' ', '_'));

                        return (
                            <div key={i} className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${isCurrent ? 'bg-primary/5 border-primary/20 shadow-sm' : 'bg-muted/30 border-transparent text-muted-foreground'}`}>
                                {complete ? (
                                    <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                                ) : (
                                    <Circle className={`h-5 w-5 shrink-0 mt-0.5 ${isCurrent ? 'text-primary' : 'text-muted-foreground/30'}`} />
                                )}
                                <div className="space-y-1">
                                    <p className={`text-sm font-semibold ${isCurrent ? 'text-foreground' : ''}`}>{step.label}</p>
                                    <div className="flex flex-wrap gap-2">
                                        {step.key.map(k => (
                                            <span key={k} className={`text-[10px] uppercase tracking-wider font-bold ${data.extracted_data[k] ? 'text-green-600' : (isCurrent && data.current_step.toLowerCase().replace(' ', '_') === k ? 'text-primary animate-pulse' : 'text-muted-foreground/50')}`}>
                                                {t(`field.${k}`, k.replace('_', ' '))}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                <div className="p-4 rounded-xl bg-muted/40 border-l-4 border-primary">
                    <p className="text-xs font-bold text-primary uppercase tracking-widest mb-1">{t('quote.next_step', 'Next Step')}</p>
                    <p className="text-sm font-medium">{data.next_question}</p>
                </div>

                {Object.keys(data.extracted_data).some(k => data.extracted_data[k]) && (
                    <div className="space-y-3">
                        <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">{t('quote.extracted_info', 'Extracted Information')}</h4>
                        <div className="grid grid-cols-2 gap-2">
                            {Object.entries(data.extracted_data || {}).map(([key, value]) => (
                                (value && key !== 'manual_discount') ? (
                                    <div key={key} className="p-2 rounded border bg-background flex flex-col">
                                        <span className="text-[10px] text-muted-foreground uppercase">{t(`field.${key}`, key.replace('_', ' '))}</span>
                                        <span className="text-xs font-medium truncate">{String(value)}</span>
                                    </div>
                                ) : null
                            ))}
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
