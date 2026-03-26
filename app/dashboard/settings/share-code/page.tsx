"use client";

import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { CreateShareCodeModal } from "@/components/sharecode/CreateShareCodeModal";
import { ShareCodeList } from "@/components/sharecode/ShareCodeList";
import { DisplayShareCode } from "@/components/sharecode/DisplayShareCode";
import { getShareCodes, ShareCode } from "@/lib/sharecode-api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

export default function ShareCodePage() {
    const [openCreate, setOpenCreate] = useState(false);
    const [codes, setCodes] = useState<ShareCode[]>([]);
    const [loading, setLoading] = useState(true);
    const [viewCode, setViewCode] = useState<ShareCode | null>(null);

    const fetchCodes = async () => {
        setLoading(true);
        try {
            const data = await getShareCodes();
            setCodes(data);
        } catch (error) {
            console.error("Failed to fetch codes", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCodes();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Sharecode Management</h2>
                    <p className="text-muted-foreground">
                        Manage your secure document sharing codes.
                    </p>
                </div>
                <Button onClick={() => setOpenCreate(true)}>
                    <Plus className="mr-2 h-4 w-4" /> Create Sharecode
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Active Sharecodes</CardTitle>
                    <CardDescription>
                        List of valid sharecodes you have generated.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {/* Note: In a real app we might want skeleton loading here */}
                    <ShareCodeList
                        codes={codes}
                        onRefresh={fetchCodes}
                        onCodeSelect={(code) => setViewCode(code)}
                    />
                </CardContent>
            </Card>

            <CreateShareCodeModal
                open={openCreate}
                onOpenChange={setOpenCreate}
                onSuccess={(newCode) => {
                    fetchCodes();
                    setViewCode(newCode); // Optionally show the newly created code immediately
                }}
            />

            {/* View Modal for a specific code */}
            <Dialog open={!!viewCode} onOpenChange={(open) => !open && setViewCode(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Sharecode Details</DialogTitle>
                    </DialogHeader>
                    {viewCode && (
                        <div className="flex justify-center">
                            <DisplayShareCode code={viewCode.code} qrCodeBase64={viewCode.qr_code_base64} />
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
}
