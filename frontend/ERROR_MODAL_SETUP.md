# Error Modal Setup Guide

## Overview

This guide shows how to replace basic error messages with a professional modal dialog component.

## Files Created

1. **`components/ErrorModal.tsx`** - Reusable error modal component
2. **`hooks/useErrorModal.ts`** - Hook for managing error state
3. **`components/ErrorModalExample.tsx`** - Usage examples

## Quick Start

### Step 1: Import the Hook

```typescript
import { useErrorModal } from '@/hooks/useErrorModal';
```

### Step 2: Use in Your Component

```typescript
export function LoginPage() {
  const { error, showError, showAuthError, closeError } = useErrorModal();

  const handleLogin = async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      // Success
    } catch (err: any) {
      if (err.response?.status === 401) {
        showAuthError('Invalid email or password');
      } else {
        showError('An error occurred', 'Error');
      }
    }
  };

  return (
    <div>
      {/* Your form */}
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
```

## API Reference

### useErrorModal Hook

#### Methods

```typescript
// Show generic error
showError(message: string, title?: string, details?: string)

// Show validation error (highlights required fields)
showValidationError(message: string, fields?: string[])

// Show network error
showNetworkError(details?: string)

// Show authentication error
showAuthError(message?: string)

// Show server error (with status code messages)
showServerError(statusCode?: number)

// Close modal
closeError()
```

#### Example Usage

```typescript
const { showError, showAuthError, showValidationError, closeError } = useErrorModal();

// Generic error
showError('Something went wrong', 'Error', 'Please try again later');

// Auth error
showAuthError('Invalid credentials');

// Validation error
showValidationError('Please fill all fields', ['Email', 'Password']);

// Network error
showNetworkError('Unable to reach server');

// Server error
showServerError(500); // Shows "Server error. Please try again later."
```

## Error Types & Messages

### Validation Error
```typescript
showValidationError('Please fill in all required fields', ['Email', 'Password'])
```
**Display:** Modal with title "Validation Error" and list of missing fields

### Network Error
```typescript
showNetworkError()
```
**Display:** "Unable to connect to the server" with connection details

### Authentication Error
```typescript
showAuthError('Invalid email or password')
```
**Display:** "Authentication Failed" with custom message

### Server Error
```typescript
showServerError(500)
```
**Display:** "Server Error" with appropriate message based on status code:
- 400: Bad request
- 401: Unauthorized
- 403: Access denied
- 404: Resource not found
- 500: Server error
- 503: Service unavailable

## Modal Features

✅ **Professional Design**
- Clean, modern appearance
- Red alert icon
- Clear hierarchy

✅ **Responsive**
- Works on all screen sizes
- Touch-friendly on mobile
- Keyboard accessible

✅ **Flexible**
- Customizable title
- Main message
- Optional details (shown in gray box)
- Single action button (Dismiss)

✅ **Accessible**
- WCAG compliant
- Keyboard navigation
- Screen reader friendly

## Integration Steps

### 1. Update Your Auth Component

In your `lib/auth.tsx` or login page:

```typescript
import { useErrorModal } from '@/hooks/useErrorModal';

export function AuthProvider({ children }: { children: ReactNode }) {
  const { error, showError, showAuthError, closeError } = useErrorModal();

  const login = async (data: LoginRequest) => {
    try {
      const response = await api.post('/auth/login', data);
      // Success handling
    } catch (err: any) {
      if (err.response?.status === 401) {
        showAuthError();
      } else if (err.message === 'Network Error') {
        showError('Network connection failed', 'Network Error');
      } else {
        showError(err.response?.data?.detail || 'Login failed', 'Error');
      }
    }
  };

  return (
    <>
      {/* Your auth UI */}
      <ErrorModal
        isOpen={error.isOpen}
        title={error.title}
        message={error.message}
        details={error.details}
        onClose={closeError}
      />
    </>
  );
}
```

### 2. Add to All Error-Prone Components

Use in:
- Login/Register forms
- API calls
- Form submissions
- Data fetching

### 3. Test Different Error Scenarios

```typescript
// Click button to test
<button onClick={() => showAuthError('Test error')}>
  Test Error
</button>
```

## Styling

The ErrorModal uses shadcn/ui components. To ensure proper styling:

1. Make sure you have `@/components/ui/alert-dialog` installed
2. Tailwind CSS is configured in your project
3. The component automatically uses the configured theme colors

To customize colors, edit `ErrorModal.tsx`:

```typescript
// Change error color from red
<AlertCircle className="h-6 w-6 text-red-600" /> {/* Change this */}
<AlertDialogContent className="border-red-200"> {/* And this */}
```

## Common Patterns

### Pattern 1: Login Form
```typescript
try {
  await login(email, password);
} catch (err) {
  showAuthError(err.response?.data?.message);
}
```

### Pattern 2: Form Submission
```typescript
try {
  await submitForm(data);
} catch (err) {
  if (err.response?.status === 422) {
    showValidationError('Form validation failed', Object.keys(err.response.data.errors));
  }
}
```

### Pattern 3: Data Fetching
```typescript
try {
  const data = await fetchData();
} catch (err) {
  if (err.message === 'Network Error') {
    showNetworkError();
  } else {
    showServerError(err.response?.status);
  }
}
```

## Troubleshooting

### Modal doesn't appear
- Check that `<ErrorModal>` component is rendered in your component
- Verify `error.isOpen` is being set to `true`
- Check browser console for errors

### Error message is truncated
- Messages are automatically wrapped
- For long messages, use the `details` prop for secondary info
- Max width is 448px

### Styling doesn't match
- Ensure Tailwind CSS is running
- Check that shadcn/ui is properly installed
- Clear `.next` cache and rebuild

## Next Steps

1. Copy the three files to your project
2. Update your auth flow to use the hook
3. Test with different error scenarios
4. Deploy and monitor error messages

---

**Result:** Professional error handling that matches modern UI standards! 🎉
