/**
 * useDeleteConfirmation Hook
 * Manages delete confirmation modal state and provides easy methods
 */
'use client';

import { useState } from 'react';

interface DeleteState {
  isOpen: boolean;
  itemId?: string | number;
  itemName: string;
  title?: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
  isLoading: boolean;
  isDangerous: boolean;
  onConfirm?: () => void | Promise<void>;
}

export function useDeleteConfirmation() {
  const [deleteState, setDeleteState] = useState<DeleteState>({
    isOpen: false,
    itemName: '',
    isLoading: false,
    isDangerous: false,
  });

  const showDeleteConfirmation = (
    itemName: string,
    onConfirm: () => void | Promise<void>,
    options?: {
      itemId?: string | number;
      title?: string;
      message?: string;
      confirmText?: string;
      cancelText?: string;
      isDangerous?: boolean;
    }
  ) => {
    setDeleteState({
      isOpen: true,
      itemId: options?.itemId,
      itemName,
      title: options?.title || 'Delete Item',
      message: options?.message,
      confirmText: options?.confirmText || 'Delete',
      cancelText: options?.cancelText || 'Cancel',
      isLoading: false,
      isDangerous: options?.isDangerous ?? false,
      onConfirm,
    });
  };

  const handleConfirm = async () => {
    if (!deleteState.onConfirm) return;

    setDeleteState((prev) => ({
      ...prev,
      isLoading: true,
    }));

    try {
      await deleteState.onConfirm();
      // Close modal after successful deletion
      setDeleteState((prev) => ({
        ...prev,
        isOpen: false,
        isLoading: false,
      }));
    } catch (error) {
      console.error('Delete action failed:', error);
      // Keep modal open on error so user can retry
      setDeleteState((prev) => ({
        ...prev,
        isLoading: false,
      }));
      throw error;
    }
  };

  const handleCancel = () => {
    setDeleteState({
      isOpen: false,
      itemName: '',
      isLoading: false,
      isDangerous: false,
    });
  };

  return {
    deleteState,
    showDeleteConfirmation,
    handleConfirm,
    handleCancel,
  };
}
