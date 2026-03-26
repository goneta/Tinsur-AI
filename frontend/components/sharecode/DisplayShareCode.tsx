import React from 'react';
import Image from 'next/image';

interface DisplayShareCodeProps {
    code: string;
    qrCodeBase64?: string;
}

export const DisplayShareCode: React.FC<DisplayShareCodeProps> = ({ code, qrCodeBase64 }) => {
    return (
        <div className="flex flex-col items-center justify-center p-6 border rounded-lg bg-white shadow-sm space-y-4">
            {qrCodeBase64 && (
                <div className="relative w-48 h-48">
                    <Image
                        src={qrCodeBase64}
                        alt={`QR Code for ${code}`}
                        fill
                        className="object-contain"
                    />
                </div>
            )}
            <div className="text-center">
                <p className="text-sm text-gray-500 uppercase tracking-wider mb-1">Share Code</p>
                <p className="text-3xl font-mono font-bold tracking-widest text-primary">{code}</p>
            </div>
            <p className="text-xs text-center text-muted-foreground w-64">
                Users can scan this QR code or enter the code above to authorize document sharing.
            </p>
        </div>
    );
};
