'use client';

import { useState, useEffect, useId } from 'react';
import { cn } from '@/lib/utils';
import { Loader2, Camera, User } from 'lucide-react';

interface UserAvatarProps {
    src?: string | null;
    alt: string;
    fallback?: React.ReactNode;
    className?: string;
    onUpload?: (file: File) => void;
    editable?: boolean;
    uploading?: boolean;
    size?: 'sm' | 'md' | 'lg' | 'xl';
    uid?: string;
}

const sizeClasses = {
    sm: 'h-10 w-10',
    md: 'h-16 w-16',
    lg: 'h-20 w-20',
    xl: 'h-24 w-24',
};

const iconSizes = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-10 w-10',
};

export function UserAvatar({
    src,
    alt,
    fallback,
    className,
    onUpload,
    editable = false,
    uploading = false,
    size = 'md',
    uid,
}: UserAvatarProps) {
    const [imgError, setImgError] = useState(false);
    const uniqueId = useId();
    const inputId = uid ? `avatar-upload-${uid}` : `avatar-upload-${uniqueId}`;

    // Reset error state if src changes
    useEffect(() => {
        setImgError(false);
    }, [src]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file && onUpload) {
            onUpload(file);
            e.target.value = ''; // Reset input
        }
    };

    return (
        <div className={cn("relative group shrink-0 rounded-full", editable && "cursor-pointer", className)}>
            <div className={cn(
                "overflow-hidden rounded-full border shadow-sm ring-1 ring-muted flex items-center justify-center bg-muted",
                sizeClasses[size],
                editable && "transition-opacity group-hover:opacity-90",
            )}>
                {!imgError && src ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                        src={src}
                        alt={alt}
                        className="h-full w-full object-cover"
                        onError={() => setImgError(true)}
                    />
                ) : (
                    <div className="flex h-full w-full items-center justify-center bg-muted text-muted-foreground">
                        {uploading ? (
                            <Loader2 className={cn("animate-spin", iconSizes[size])} />
                        ) : fallback ? (
                            fallback
                        ) : (
                            <User className={cn(iconSizes[size])} />
                        )}
                    </div>
                )}
            </div>

            {editable && (
                <>
                    <label
                        htmlFor={inputId}
                        className="absolute inset-0 flex items-center justify-center cursor-pointer bg-black/40 rounded-full opacity-0 group-hover:opacity-100 transition-opacity z-10"
                        title="Change picture"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <Camera className={cn("text-white drop-shadow-md", iconSizes[size])} />
                    </label>
                    <input
                        type="file"
                        id={inputId}
                        className="hidden"
                        accept="image/*"
                        onChange={handleFileChange}
                        disabled={uploading}
                        onClick={(e) => e.stopPropagation()}
                    />
                </>
            )}
        </div>
    );
}
