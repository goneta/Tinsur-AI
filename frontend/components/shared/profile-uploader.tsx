'use client';

import { useState } from 'react';
import { api, getProfileImageUrl } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import { UserAvatar } from './user-avatar';
import { PermissionDeniedModal } from './permission-denied-modal';

interface ProfileUploaderProps {
    /** The ID of the user or client */
    entityId: string;
    /** 'user' for employees/admins, 'client' for clients */
    entityType: 'user' | 'client';
    /** Current profile picture URL/path */
    currentImageUrl?: string | null;
    /** Name to display for alt text */
    name: string;
    /** Size of the avatar */
    size?: 'sm' | 'md' | 'lg' | 'xl';
    /** Callback when upload succeeds */
    onUploadSuccess: () => void;
    /** Class name for styling */
    className?: string;
    /** Custom endpoint URL if standard ones don't apply */
    customEndpoint?: string;
}

export function ProfileUploader({
    entityId,
    entityType,
    currentImageUrl,
    name,
    size = 'md',
    onUploadSuccess,
    className,
    customEndpoint
}: ProfileUploaderProps) {
    const [uploading, setUploading] = useState(false);
    const [showPermissionModal, setShowPermissionModal] = useState(false);
    const { toast } = useToast();

    const handleUpload = async (file: File) => {
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            toast({
                title: "Invalid file",
                description: "Please upload an image file.",
                variant: 'destructive'
            });
            return;
        }

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Determine endpoint
            let endpoint = customEndpoint;
            if (!endpoint) {
                endpoint = entityType === 'client'
                    ? `/clients/${entityId}/profile-picture`
                    : `/users/${entityId}/profile-picture`;
            }

            console.log('ProfileUploader handling upload for:', entityId, name);
            console.log(`Uploading to ${endpoint}...`);

            await api.post(endpoint, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            toast({
                title: "Success",
                description: "Profile picture updated.",
            });
            onUploadSuccess();

        } catch (error: any) {
            console.error("Upload failed", error);

            if (error.response?.status === 403) {
                setShowPermissionModal(true);
            } else {
                const msg = error.response?.data?.detail || "Could not upload profile picture.";
                toast({
                    title: "Upload failed",
                    description: msg,
                    variant: 'destructive'
                });
            }
        } finally {
            setUploading(false);
        }
    };

    return (
        <>
            <UserAvatar
                src={getProfileImageUrl(currentImageUrl || undefined)}
                alt={name}
                className={className}
                size={size}
                editable={true}
                uploading={uploading}
                onUpload={handleUpload}
                fallback={undefined} // Let UserAvatar handle fallback logic
                uid={entityId}
            />

            <PermissionDeniedModal
                isOpen={showPermissionModal}
                onClose={() => setShowPermissionModal(false)}
            />
        </>
    );
}
