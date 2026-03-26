
import React from 'react';
import { LucideIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
    title: string;
    description: string;
    icon: LucideIcon;
    action?: {
        label: string;
        onClick: () => void;
        icon?: LucideIcon;
    };
    className?: string;
}

export function EmptyState({
    title,
    description,
    icon: Icon,
    action,
    className
}: EmptyStateProps) {
    return (
        <div className={cn(
            "flex flex-col items-center justify-center p-12 text-center",
            "rounded-xl border border-dashed bg-card/50 backdrop-blur-sm",
            "animate-in fade-in zoom-in duration-500",
            className
        )}>
            <div className="relative mb-6">
                <div className="absolute -inset-4 rounded-full bg-primary/5 blur-2xl animate-pulse" />
                <div className="relative flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 via-primary/5 to-transparent border border-primary/10 shadow-inner">
                    <Icon className="h-10 w-10 text-primary animate-in slide-in-from-bottom-2 duration-700" />
                </div>
            </div>

            <h3 className="text-2xl font-semibold tracking-tight mb-2">
                {title}
            </h3>
            <p className="text-muted-foreground max-w-[400px] mb-8 leading-relaxed">
                {description}
            </p>

            {action && (
                <Button
                    onClick={action.onClick}
                    size="lg"
                    className="shadow-lg hover:shadow-primary/20 transition-all duration-300 transform hover:-translate-y-1"
                >
                    {action.icon && <action.icon className="mr-2 h-5 w-5" />}
                    {action.label}
                </Button>
            )}
        </div>
    );
}
