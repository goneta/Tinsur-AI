/**
 * Simple homepage that redirects to dashboard or login.
 */
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { useLanguage } from '@/contexts/language-context';

export default function HomePage() {
  const router = useRouter();
  const { t } = useLanguage();
  const { isAuthenticated, loading, user } = useAuth();

  useEffect(() => {
    if (!loading) {
      if (isAuthenticated) {
        if (user?.role === 'client') {
          router.push('/portal');
        } else {
          router.push('/dashboard');
        }
      } else {
        router.push('/login');
      }
    }
  }, [isAuthenticated, loading, router, user]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-semibold">{t('Loading...')}</h1>
      </div>
    </div>
  );
}
