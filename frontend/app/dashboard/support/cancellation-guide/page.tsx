'use client';

import { CancellationGuide } from '@/components/support/cancellation-guide';
import { Button } from '@/components/ui/button';
import { ChevronLeft, Printer } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function AdminCancellationGuidePage() {
    const router = useRouter();

    return (
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
            <div className="flex items-center justify-between">
                <Button
                    variant="ghost"
                    onClick={() => router.back()}
                    className="flex items-center gap-2"
                >
                    <ChevronLeft className="h-4 w-4" /> Retour au Support
                </Button>

                <Button
                    variant="outline"
                    onClick={() => window.print()}
                    className="flex items-center gap-2"
                >
                    <Printer className="h-4 w-4" /> Imprimer
                </Button>
            </div>

            <div className="bg-white p-8 rounded-xl shadow border">
                <CancellationGuide />
            </div>
        </div>
    );
}
