'use client';

import React from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { DashboardStats } from '@/lib/portal-api';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface PortalExcessDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    stats: DashboardStats | null;
}

export function PortalExcessDialog({ open, onOpenChange, stats }: PortalExcessDialogProps) {
    const policy = stats?.primary_policy;
    const clientName = stats?.client_name || 'Client';

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-3xl p-0 overflow-hidden border-none rounded-none bg-white">
                <div className="p-8 space-y-8">
                    <div className="flex justify-between items-start">
                        <DialogHeader className="p-0">
                            <DialogTitle className="text-3xl font-bold text-gray-900">Excesses</DialogTitle>
                        </DialogHeader>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => onOpenChange(false)}
                            className="text-gray-400 hover:text-gray-600"
                        >
                            <X className="h-6 w-6" />
                        </Button>
                    </div>

                    <div className="space-y-6 text-[17px] text-gray-700 leading-relaxed">
                        <p>
                            An excess is the amount you pay towards any claim. Your policy includes a compulsory excess and any voluntary excess chosen by you.
                        </p>
                        <p>
                            We&apos;ve outlined below the total voluntary and compulsory excesses that you&apos;ll pay depending on the type of claim you make.
                        </p>
                        <p className="font-bold text-black">
                            Your voluntary excess is £{policy?.voluntary_excess ?? 250}
                        </p>
                    </div>

                    <div className="border border-gray-200 overflow-hidden">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-gray-50 border-b border-gray-200">
                                    <th className="p-6 text-lg font-bold text-gray-900 w-2/3 border-r border-gray-200">
                                        {clientName}
                                    </th>
                                    <th className="p-6 text-lg font-bold text-gray-900 text-center">
                                        Total voluntary and compulsory excess
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200 bg-white">
                                <tr>
                                    <td className="p-6 text-[17px] text-gray-700 border-r border-gray-200">
                                        Compulsory Accidental Damage Excess for Proposer
                                    </td>
                                    <td className="p-6 text-lg font-medium text-gray-900 text-center">
                                        £{policy?.compulsory_excess ?? 200}
                                    </td>
                                </tr>
                                <tr>
                                    <td className="p-6 text-[17px] text-gray-700 border-r border-gray-200">
                                        Compulsory Fire & Theft Excess
                                    </td>
                                    <td className="p-6 text-lg font-medium text-gray-900 text-center">
                                        £{policy?.compulsory_excess ?? 200}
                                    </td>
                                </tr>
                                <tr>
                                    <td className="p-6 text-[17px] text-gray-700 border-r border-gray-200">
                                        Windscreen Replacement Excess
                                    </td>
                                    <td className="p-6 text-lg font-medium text-gray-900 text-center">
                                        £75*
                                    </td>
                                </tr>
                                <tr className="bg-gray-50/30">
                                    <td colSpan={2} className="p-6 text-[15px] text-gray-500 italic flex items-start gap-4">
                                        <div className="flex flex-col">
                                            <span>There was an error retrieving the excess details. Additional excesses may apply, please call for details.</span>
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td className="p-6 text-[17px] text-gray-700 border-r border-gray-200">
                                        Theft of keys excess.
                                    </td>
                                    <td className="p-6 text-lg font-medium text-gray-900 text-center">
                                        £75
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div className="flex justify-end pt-4">
                        <Button
                            onClick={() => onOpenChange(false)}
                            className="bg-[#00539F] hover:bg-blue-800 text-white font-bold px-10 py-6 text-lg rounded-full"
                        >
                            Close
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
