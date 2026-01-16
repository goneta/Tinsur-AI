'use client';

import { MLModel } from '@/services/analyticsService';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

interface MLStatusBoardProps {
    models: MLModel[];
}

export function MLStatusBoard({ models }: MLStatusBoardProps) {
    return (
        <Card className="col-span-3">
            <CardHeader>
                <CardTitle>ML Model Status</CardTitle>
                <CardDescription>
                    Real-time performance of deployed models.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-8">
                    {models.length === 0 ? (
                        <p className="text-sm text-muted-foreground">No active models.</p>
                    ) : models.map((model) => (
                        <div key={model.id} className="flex items-center">
                            <span className="relative flex h-2 w-2 mr-2">
                                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${model.is_active ? 'bg-green-400' : 'bg-red-400'} opacity-75`}></span>
                                <span className={`relative inline-flex rounded-full h-2 w-2 ${model.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                            </span>
                            <div className="ml-4 space-y-1">
                                <p className="text-sm font-medium leading-none">{model.model_name} v{model.version}</p>
                                <p className="text-sm text-muted-foreground">Accuracy: {(model.accuracy * 100).toFixed(1)}%</p>
                            </div>
                            <div className={`ml-auto font-medium ${model.is_active ? 'text-green-500' : 'text-red-500'}`}>
                                {model.is_active ? 'Active' : 'Offline'}
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
