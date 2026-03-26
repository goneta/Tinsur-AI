
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CheckCircle2, XCircle, ShieldCheck, Calendar, Building2, UserCircle } from "lucide-react";
import { formatDate } from "@/lib/utils";

interface VerificationData {
    status: string;
    policy_number?: string;
    policy_type?: string;
    company_name?: string;
    client_initials?: string;
    expiry_date?: string;
    is_active?: boolean;
    verified_at?: string;
    message?: string;
}

export default function VerificationPage() {
    const params = useParams();
    const token = params.token as string;
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<VerificationData | null>(null);

    useEffect(() => {
        const verify = async () => {
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/public/verify/verify/${token}`);
                const result = await response.json();
                setData(result);
            } catch (error) {
                console.error("Verification error:", error);
                setData({ status: "ERROR", message: "Unable to connect to verification server." });
            } finally {
                setLoading(false);
            }
        };

        if (token) {
            verify();
        }
    }, [token]);

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center p-4 bg-gray-50">
                <Card className="w-full max-w-md">
                    <CardHeader className="space-y-2">
                        <Skeleton className="h-6 w-1/2" />
                        <Skeleton className="h-4 w-3/4" />
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <Skeleton className="h-20 w-full" />
                        <Skeleton className="h-10 w-full" />
                    </CardContent>
                </Card>
            </div>
        );
    }

    const isVerified = data?.status === "VERIFIED";
    const isInactive = data?.status === "INACTIVE";
    const isInvalid = data?.status === "INVALID" || data?.status === "ERROR";

    return (
        <div className="flex min-h-screen flex-col items-center justify-center p-4 bg-gray-50">
            <div className="mb-8 text-center">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-black text-white mb-4">
                    <span className="text-2xl font-bold tracking-tighter">I</span>
                </div>
                <h1 className="text-xl font-semibold text-gray-900">Tinsur.AI Verification</h1>
            </div>

            <Card className="w-full max-w-md overflow-hidden border-2 shadow-xl">
                <div className={`h-2 w-full ${isVerified ? 'bg-green-500' : isInactive ? 'bg-yellow-500' : 'bg-red-500'}`} />

                <CardHeader className="text-center pb-2">
                    <div className="flex justify-center mb-2">
                        {isVerified ? (
                            <CheckCircle2 className="h-16 w-16 text-green-500" />
                        ) : isInactive ? (
                            <XCircle className="h-16 w-16 text-yellow-500" />
                        ) : (
                            <XCircle className="h-16 w-16 text-red-500" />
                        )}
                    </div>
                    <CardTitle className={`text-2xl ${isVerified ? 'text-green-700' : isInactive ? 'text-yellow-700' : 'text-red-700'}`}>
                        {isVerified ? "POLICY VERIFIED" : isInactive ? "POLICY EXPIRED" : "VERIFICATION FAILED"}
                    </CardTitle>
                    <CardDescription>
                        Official verification results for insurance policy authenticity.
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-6 pt-4">
                    {isVerified || isInactive ? (
                        <div className="grid gap-4 bg-gray-50 p-4 rounded-lg border border-gray-100">
                            <div className="flex items-center gap-3">
                                <ShieldCheck className="h-5 w-5 text-gray-500" />
                                <div>
                                    <p className="text-xs text-gray-500 uppercase font-semibold">Policy Number</p>
                                    <p className="text-sm font-bold text-gray-900">{data?.policy_number}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <Building2 className="h-5 w-5 text-gray-500" />
                                <div>
                                    <p className="text-xs text-gray-500 uppercase font-semibold">Insurance Provider</p>
                                    <p className="text-sm font-medium text-gray-900">{data?.company_name}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <UserCircle className="h-5 w-5 text-gray-500" />
                                <div>
                                    <p className="text-xs text-gray-500 uppercase font-semibold">Holder Initials</p>
                                    <p className="text-sm font-medium text-gray-900">{data?.client_initials}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <Calendar className="h-5 w-5 text-gray-500" />
                                <div>
                                    <p className="text-xs text-gray-500 uppercase font-semibold">Expiry Date</p>
                                    <p className={`text-sm font-medium ${isInactive ? 'text-red-600' : 'text-gray-900'}`}>
                                        {data?.expiry_date ? formatDate(data.expiry_date) : 'N/A'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-4">
                            <p className="text-sm text-gray-600 font-medium">{data?.message || "The provided token is invalid or has been revoked."}</p>
                        </div>
                    )}

                    <div className="text-center border-t pt-4">
                        <p className="text-[10px] text-gray-400 uppercase tracking-widest mb-1">Verification Timestamp</p>
                        <p className="text-xs text-gray-500 tabular-nums">
                            {data?.verified_at ? formatDate(data.verified_at) : formatDate(new Date())}
                        </p>
                    </div>
                </CardContent>
            </Card>

            <p className="mt-8 text-xs text-gray-400 max-w-xs text-center">
                This verification portal is provided by Tinsur.AI. Unauthorized use or spoofing of this data is subject to legal action.
            </p>
        </div>
    );
}
