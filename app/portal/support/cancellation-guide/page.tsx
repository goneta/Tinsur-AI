'use client';

import { CancellationGuide } from '@/components/support/cancellation-guide';
import { Button } from '@/components/ui/button';
import { ChevronLeft, Printer } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function CancellationGuidePage() {
    const router = useRouter();

    return (
        <div className="max-w-[1700px] mx-auto flex-1 space-y-8 pt-6 pb-20">
            <div className="flex items-center justify-between">
                <Button
                    variant="ghost"
                    onClick={() => router.back()}
                    className="flex items-center gap-2 text-slate-600 hover:text-slate-900"
                >
                    <ChevronLeft className="h-4 w-4" /> Retour
                </Button>

                <Button
                    variant="outline"
                    onClick={() => window.print()}
                    className="flex items-center gap-2"
                >
                    <Printer className="h-4 w-4" /> Imprimer
                </Button>
            </div>

            <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-100">
                <CancellationGuide />
            </div>
        </div>
    );
}
