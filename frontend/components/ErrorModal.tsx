/**
 * Error Modal Component
 * Displays error messages in a professional modal dialog
 */
'use client';

import React from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { AlertCircle } from 'lucide-react';

interface ErrorModalProps {
  isOpen: boolean;
  title?: string;
  message: string;
  onClose: () => void;
  details?: string;
}

export function ErrorModal({
  isOpen,
  title = 'Error',
  message,
  onClose,
  details,
}: ErrorModalProps) {
  return (
    <AlertDialog open={isOpen} onOpenChange={onClose}>
      <AlertDialogContent className="max-w-md border-red-200 bg-white">
        {/* Header with Icon */}
        <AlertDialogHeader className="flex items-start gap-3">
          <div className="mt-1 flex-shrink-0">
            <AlertCircle className="h-6 w-6 text-red-600" />
          </div>
          <div className="flex-1">
            <AlertDialogTitle className="text-left text-lg font-semibold text-gray-900">
              {title}
            </AlertDialogTitle>
          </div>
        </AlertDialogHeader>

        {/* Message */}
        <AlertDialogDescription className="text-left">
          <p className="text-base text-gray-700">{message}</p>
          
          {/* Optional Details */}
          {details && (
            <div className="mt-3 rounded-md bg-red-50 p-3">
              <p className="text-sm text-red-700">{details}</p>
            </div>
          )}
        </AlertDialogDescription>

        {/* Action Button */}
        <div className="mt-6 flex justify-end">
          <AlertDialogAction
            onClick={onClose}
            className="bg-red-600 px-6 py-2 font-medium text-white hover:bg-red-700"
          >
            Dismiss
          </AlertDialogAction>
        </div>
      </AlertDialogContent>
    </AlertDialog>
  );
}

export default ErrorModal;
