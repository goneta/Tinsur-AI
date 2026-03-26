/**
 * Example: How to Use ErrorModal in Your Components
 * 
 * This shows how to integrate the error modal into your auth flow
 */

'use client';

import { useState } from 'react';
import { ErrorModal } from '@/components/ErrorModal';
import { useErrorModal } from '@/hooks/useErrorModal';
import api from '@/lib/api';

// EXAMPLE 1: Simple component with error handling
export function LoginFormExample() {
  const { error, showError, showAuthError, closeError } = useErrorModal();
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      
      // API call
      const response = await api.post('/auth/login', {
        email,
        password,
      });
      
      // Success
      console.log('Login successful:', response.data);
      
    } catch (err: any) {
      // Handle different error types
      if (err.response?.status === 401) {
        showAuthError('Invalid email or password');
      } else if (err.response?.status === 422) {
        const details = err.response.data?.detail || 'Please check your input';
        showError(
          'Validation Error',
          'Please ensure all fields are filled correctly',
          details
        );
      } else if (err.message === 'Network Error') {
        showError(
          'Unable to connect to the server',
          'Network Error',
          'Please check your internet connection'
        );
      } else {
        showError(
          err.response?.data?.detail || 'An unexpected error occurred',
          'Error'
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {/* Your login form here */}
      
      {/* Error Modal */}
      <ErrorModal
        isOpen={error.isOpen}
        title={error.title}
        message={error.message}
        details={error.details}
        onClose={closeError}
      />
    </div>
  );
}

// EXAMPLE 2: Using with AuthContext
export function UpdateAuthComponent() {
  const { error, showAuthError, closeError } = useErrorModal();

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login', {
        email,
        password,
      });

      // Store token
      localStorage.setItem('access_token', response.data.access_token);
      
    } catch (err: any) {
      if (err.response?.status === 401) {
        showAuthError();
      } else if (err.response?.status === 404) {
        showAuthError('User not found');
      } else {
        showAuthError(err.response?.data?.message);
      }
    }
  };

  return (
    <ErrorModal
      isOpen={error.isOpen}
      title={error.title}
      message={error.message}
      details={error.details}
      onClose={closeError}
    />
  );
}

// EXAMPLE 3: Complex error handling with multiple scenarios
export function RegistrationFormExample() {
  const {
    error,
    showError,
    showValidationError,
    showServerError,
    closeError,
  } = useErrorModal();

  const handleRegister = async (formData: any) => {
    try {
      // Validate form
      const missingFields = [];
      if (!formData.email) missingFields.push('Email');
      if (!formData.password) missingFields.push('Password');
      if (!formData.name) missingFields.push('Name');

      if (missingFields.length > 0) {
        showValidationError(
          'Please fill in all required fields',
          missingFields
        );
        return;
      }

      // API call
      const response = await api.post('/auth/register', formData);
      
      console.log('Registration successful');
      
    } catch (err: any) {
      const status = err.response?.status;

      if (status === 400) {
        showServerError(400);
      } else if (status === 409) {
        showError(
          'Email already registered',
          'Registration Failed',
          'Please use a different email or login instead'
        );
      } else if (status >= 500) {
        showServerError(status);
      } else {
        showError(
          'Registration failed. Please try again.',
          'Error'
        );
      }
    }
  };

  return (
    <ErrorModal
      isOpen={error.isOpen}
      title={error.title}
      message={error.message}
      details={error.details}
      onClose={closeError}
    />
  );
}
