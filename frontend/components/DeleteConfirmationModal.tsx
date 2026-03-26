/**
 * Delete Confirmation Modal Component
 * Displays confirmation dialog before deleting items
 */
'use client';

import React from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Trash2 } from 'lucide-react';

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  title?: string;
  itemName: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void | Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
  isDangerous?: boolean;
}

export function DeleteConfirmationModal({
  isOpen,
  title = 'Delete Item',
  itemName,
  message,
  confirmText = 'Delete',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
  isLoading = false,
  isDangerous = false,
}: DeleteConfirmationModalProps) {
  return (
    <AlertDialog open={isOpen} onOpenChange={onCancel}>
      <AlertDialogContent className="max-w-md border-red-200 bg-white">
        {/* Header with Icon */}
        <AlertDialogHeader className="flex items-start gap-3">
          <div className="mt-1 flex-shrink-0">
            <Trash2 className={`h-6 w-6 ${isDangerous ? 'text-red-600' : 'text-orange-600'}`} />
          </div>
          <div className="flex-1">
            <AlertDialogTitle className="text-left text-lg font-semibold text-gray-900">
              {title}
            </AlertDialogTitle>
          </div>
        </AlertDialogHeader>

        {/* Message */}
        <AlertDialogDescription className="text-left">
          <p className="text-base text-gray-700">
            {message || `Are you sure you want to delete "${itemName}"?`}
          </p>
          {isDangerous && (
            <div className="mt-3 rounded-md bg-red-50 p-3">
              <p className="text-sm font-medium text-red-800">
                ⚠️ This action cannot be undone.
              </p>
            </div>
          )}
        </AlertDialogDescription>

        {/* Action Buttons */}
        <div className="mt-6 flex justify-end gap-3">
          <AlertDialogCancel
            onClick={onCancel}
            disabled={isLoading}
            className="px-6 py-2 font-medium text-gray-700 hover:bg-gray-100"
          >
            {cancelText}
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            disabled={isLoading}
            className={`px-6 py-2 font-medium text-white ${
              isDangerous
                ? 'bg-red-600 hover:bg-red-700 disabled:bg-red-400'
                : 'bg-orange-600 hover:bg-orange-700 disabled:bg-orange-400'
            }`}
          >
            {isLoading ? 'Deleting...' : confirmText}
          </AlertDialogAction>
        </div>
      </AlertDialogContent>
    </AlertDialog>
  );
}

export default DeleteConfirmationModal;
