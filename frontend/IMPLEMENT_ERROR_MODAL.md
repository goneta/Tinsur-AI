# How to Implement Error Modal in Your Auth Component

## Current Issue

Your login error message displays like this:
```
Error
Email and Phone are required for clients.
```

This will be replaced with a professional modal.

---

## Implementation for lib/auth.tsx

### Step 1: Add Import at Top

```typescript
import { useErrorModal } from '@/hooks/useErrorModal';
import { ErrorModal } from '@/components/ErrorModal';
```

### Step 2: Add Error Hook in AuthProvider

```typescript
export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [aiCredits, setAiCredits] = useState<number>(0);
    const router = useRouter();
    
    // ← ADD THIS LINE
    const { error, showError, showAuthError, closeError } = useErrorModal();

    // ... rest of your code
}
```

### Step 3: Update Login Function

**BEFORE:**
```typescript
const login = async (data: LoginRequest, redirectTo?: string) => {
    try {
        const response = await api.post<LoginResponse>('/auth/login', data);
        const { access_token, refresh_token, user: userData } = response.data;
        // ... success handling
    } catch (error: any) {
        console.error('Login failed:', error);
        // ← Error was shown as console only
    }
};
```

**AFTER:**
```typescript
const login = async (data: LoginRequest, redirectTo?: string) => {
    try {
        const response = await api.post<LoginResponse>('/auth/login', data);
        const { access_token, refresh_token, user: userData } = response.data;
        
        if (typeof window !== 'undefined') {
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
        }
        setUser(userData);
        refreshCredits();
        
        if (redirectTo && typeof window !== 'undefined') {
            router.push(redirectTo);
        }
        
    } catch (error: any) {
        // Handle different error types
        if (error.response?.status === 401) {
            showAuthError('Invalid email or password. Please try again.');
        } 
        else if (error.response?.status === 422) {
            // Validation error
            const detail = error.response.data?.detail;
            showError(
                'Validation Error',
                typeof detail === 'string' ? detail : 'Please check your input',
                error.response.data?.detail
            );
        } 
        else if (error.message === 'Network Error') {
            showError(
                'Network Error',
                'Unable to connect to the server. Please check your internet connection.'
            );
        } 
        else {
            const message = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          'Login failed. Please try again.';
            showError(message, 'Error');
        }
    }
};
```

### Step 4: Update Register Function (Same Pattern)

```typescript
const register = async (data: RegisterRequest) => {
    try {
        const response = await api.post<LoginResponse>('/auth/register', data);
        // ... handle success
    } catch (error: any) {
        if (error.response?.status === 409) {
            showError(
                'Email already registered',
                'Registration Failed',
                'Please use a different email or login instead'
            );
        } 
        else if (error.response?.status === 422) {
            showError(
                'Validation Error',
                'Please fill in all required fields'
            );
        } 
        else {
            showError('Registration failed', 'Error');
        }
    }
};
```

### Step 5: Add Modal Component to Return

In your AuthProvider's return statement, add the ErrorModal **before the closing tag**:

```typescript
return (
    <AuthContext.Provider value={{
        user,
        loading,
        login,
        register,
        logout,
        // ... other values
    }}>
        {children}
        
        {/* Add this line */}
        <ErrorModal
            isOpen={error.isOpen}
            title={error.title}
            message={error.message}
            details={error.details}
            onClose={closeError}
        />
    </AuthContext.Provider>
);
```

---

## Full Example (lib/auth.tsx)

```typescript
'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { useErrorModal } from '@/hooks/useErrorModal'; // ← ADD
import { ErrorModal } from '@/components/ErrorModal'; // ← ADD
import { User, LoginRequest, RegisterRequest, LoginResponse } from '@/types/user';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (data: LoginRequest, redirectTo?: string) => Promise<void>;
    register: (data: RegisterRequest) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();
    const { error, showError, showAuthError, closeError } = useErrorModal(); // ← ADD

    const login = async (data: LoginRequest, redirectTo?: string) => {
        try {
            const response = await api.post<LoginResponse>('/auth/login', data);
            const { access_token, refresh_token, user: userData } = response.data;

            if (typeof window !== 'undefined') {
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', refresh_token);
            }
            setUser(userData);

            if (redirectTo && typeof window !== 'undefined') {
                router.push(redirectTo);
            }

        } catch (error: any) {
            // Handle different error types
            if (error.response?.status === 401) {
                showAuthError('Invalid email or password. Please try again.');
            } 
            else if (error.response?.status === 422) {
                showError(
                    'Please fill in all required fields',
                    'Validation Error'
                );
            } 
            else if (error.message === 'Network Error') {
                showError(
                    'Unable to connect to the server. Check your internet connection.',
                    'Network Error'
                );
            } 
            else {
                showError(
                    error.response?.data?.detail || 'Login failed. Please try again.',
                    'Error'
                );
            }
        }
    };

    const register = async (data: RegisterRequest) => {
        try {
            const response = await api.post<LoginResponse>('/auth/register', data);
            const { access_token, refresh_token, user: userData } = response.data;

            if (typeof window !== 'undefined') {
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', refresh_token);
            }
            setUser(userData);

        } catch (error: any) {
            if (error.response?.status === 409) {
                showError(
                    'Email already registered',
                    'Registration Failed'
                );
            } 
            else {
                showError(
                    error.response?.data?.detail || 'Registration failed',
                    'Error'
                );
            }
        }
    };

    const logout = () => {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        }
        setUser(null);
        router.push('/login');
    };

    return (
        <AuthContext.Provider value={{
            user,
            loading,
            login,
            register,
            logout,
            isAuthenticated: !!user,
        }}>
            {children}
            
            {/* Error Modal */}
            <ErrorModal
                isOpen={error.isOpen}
                title={error.title}
                message={error.message}
                details={error.details}
                onClose={closeError}
            />
        </AuthContext.Provider>
    );
}

// ... rest of your code
```

---

## Testing After Implementation

### Test 1: Invalid Login
1. Go to http://localhost:3000/login
2. Enter wrong email/password
3. Click Login
4. **Expected:** Modal appears with "Authentication Failed" and message

### Test 2: Empty Fields
1. Click Login without entering credentials
2. **Expected:** Modal appears with "Validation Error"

### Test 3: Dismiss Button
1. Trigger any error
2. Click "Dismiss" button
3. **Expected:** Modal closes and clears

### Test 4: Keyboard
1. Trigger an error
2. Press Tab (focuses Dismiss button)
3. Press Enter
4. **Expected:** Modal closes

---

## Checklist

- [ ] Import ErrorModal hook in auth.tsx
- [ ] Import ErrorModal component
- [ ] Add error hook to AuthProvider
- [ ] Update login() to use showError/showAuthError
- [ ] Update register() to use showError/showAuthError
- [ ] Add <ErrorModal /> component to return
- [ ] Clear .next cache: `rm -r .next`
- [ ] Restart dev server: `npm run dev`
- [ ] Test login with invalid credentials
- [ ] Test error modal appears
- [ ] Test dismiss button works
- [ ] Verify in browser at http://localhost:3000

---

## Result

Instead of this:
```
Error
Email and Phone are required for clients.
```

You'll get a professional modal like this:
```
┌──────────────────────────────────────┐
│  ⚠️  Authentication Failed           │
├──────────────────────────────────────┤
│                                      │
│  Invalid email or password.          │
│  Please try again.                   │
│                                      │
└──────────────────────────────────────┘
           [Dismiss]
```

**Much better user experience!** ✨
