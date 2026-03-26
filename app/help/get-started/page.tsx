'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { OnboardingWizard } from '@/components/help/onboarding-wizard';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle } from 'lucide-react';

export default function GetStartedPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [onboardingStatus, setOnboardingStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showWizard, setShowWizard] = useState(false);

  useEffect(() => {
    if (user) {
      loadOnboardingStatus();
    }
  }, [user]);

  const loadOnboardingStatus = async () => {
    try {
      const response = await fetch('/api/v1/help/onboarding/status');
      if (response.ok) {
        const data = await response.json();
        setOnboardingStatus(data);
        // Don't show wizard if already completed
        if (!data.completed && !data.skipped) {
          setShowWizard(true);
        }
      }
    } catch (error) {
      console.error('Failed to load onboarding status:', error);
      setShowWizard(true); // Show wizard if status check fails
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    try {
      const response = await fetch('/api/v1/help/onboarding/complete', {
        method: 'POST',
      });
      if (response.ok) {
        setShowWizard(false);
        setOnboardingStatus((prev: any) => ({
          ...prev,
          completed: true,
        }));
      }
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
    }
  };

  const handleSkip = async () => {
    try {
      const response = await fetch('/api/v1/help/onboarding/skip', {
        method: 'POST',
      });
      if (response.ok) {
        setShowWizard(false);
        setOnboardingStatus((prev: any) => ({
          ...prev,
          skipped: true,
        }));
      }
    } catch (error) {
      console.error('Failed to skip onboarding:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  if (onboardingStatus?.completed) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardContent className="pt-12 pb-12">
            <div className="text-center space-y-6">
              <CheckCircle className="h-16 w-16 text-green-600 mx-auto" />
              <h2 className="text-2xl font-bold">Onboarding Complete!</h2>
              <p className="text-muted-foreground">
                You've completed the Tinsur-AI onboarding. You're ready to get started!
              </p>
              <div className="flex gap-3 justify-center">
                <Button onClick={() => router.push('/dashboard')}>
                  Go to Dashboard
                </Button>
                <Button variant="outline" onClick={() => router.push('/help/guides')}>
                  View All Guides
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <>
      <div className="max-w-2xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold">Get Started with Tinsur-AI</h1>
          <p className="text-lg text-muted-foreground">
            Complete the onboarding wizard or explore our guides to learn about the platform.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Start the Onboarding Wizard</h3>
                <p className="text-sm text-muted-foreground">
                  Follow a guided tour tailored to your role and get tips for getting the most out of Tinsur-AI.
                </p>
                <Button
                  onClick={() => setShowWizard(true)}
                  className="w-full"
                >
                  Start Wizard
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Browse Guides</h3>
                <p className="text-sm text-muted-foreground">
                  Explore our comprehensive documentation and guides for specific features and workflows.
                </p>
                <Button
                  variant="outline"
                  onClick={() => router.push('/help/guides')}
                  className="w-full"
                >
                  View Guides
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Links */}
        <Card>
          <CardContent className="pt-6">
            <h3 className="font-semibold mb-4">Quick Links</h3>
            <div className="grid gap-2">
              <a
                href="/help/faq"
                className="text-primary hover:underline text-sm"
              >
                → Frequently Asked Questions (FAQ)
              </a>
              <a
                href="/dashboard/settings"
                className="text-primary hover:underline text-sm"
              >
                → Go to Settings
              </a>
              <a
                href="mailto:support@tinsur-ai.com"
                className="text-primary hover:underline text-sm"
              >
                → Contact Support
              </a>
            </div>
          </CardContent>
        </Card>
      </div>

      {showWizard && (
        <OnboardingWizard
          userRole={user?.role || 'client'}
          onComplete={handleComplete}
          onSkip={handleSkip}
        />
      )}
    </>
  );
}
