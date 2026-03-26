/**
 * useErrorModal Hook
 * Manages error modal state and provides easy methods to show/hide errors
 */
'use client';

import { useState } from 'react';

interface ErrorState {
  isOpen: boolean;
  title: string;
  message: string;
  details?: string;
}

export function useErrorModal() {
  const [error, setError] = useState<ErrorState>({
    isOpen: false,
    title: 'Error',
    message: '',
    details: undefined,
  });

  const showError = (message: string, title?: string, details?: string) => {
    setError({
      isOpen: true,
      title: title || 'Error',
      message,
      details,
    });
  };

  const closeError = () => {
    setError((prev) => ({
      ...prev,
      isOpen: false,
    }));
  };

  const showValidationError = (message: string, fields?: string[]) => {
    showError(
      message,
      'Validation Error',
      fields ? `Required fields: ${fields.join(', ')}` : undefined
    );
  };

  const showNetworkError = (details?: string) => {
    showError(
      'Unable to connect to the server. Please check your internet connection and try again.',
      'Network Error',
      details
    );
  };

  const showAuthError = (message?: string) => {
    showError(
      message || 'Invalid email or password. Please try again.',
      'Authentication Failed'
    );
  };

  const showServerError = (statusCode?: number) => {
    const messages: { [key: number]: string } = {
      400: 'Bad request. Please check your input.',
      401: 'Unauthorized. Please login again.',
      403: 'Access denied.',
      404: 'Resource not found.',
      500: 'Server error. Please try again later.',
      503: 'Service unavailable. Please try again later.',
    };

    showError(
      messages[statusCode || 500] || 'An unexpected error occurred.',
      'Server Error',
      statusCode ? `Status code: ${statusCode}` : undefined
    );
  };

  return {
    error,
    showError,
    closeError,
    showValidationError,
    showNetworkError,
    showAuthError,
    showServerError,
  };
}
