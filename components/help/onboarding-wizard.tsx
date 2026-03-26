'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { X, ChevronRight, ChevronLeft, CheckCircle } from 'lucide-react';
import Link from 'next/link';

interface OnboardingStep {
  id: number;
  title: string;
  description: string;
  content: string;
  guideName?: string;
  guideLink?: string;
  icon?: React.ReactNode;
}

interface OnboardingWizardProps {
  steps: OnboardingStep[];
  onComplete?: () => Promise<void>;
  onSkip?: () => Promise<void>;
  initialStep?: number;
  userRole?: string;
}

const defaultSteps: Record<string, OnboardingStep[]> = {
  client: [
    {
      id: 1,
      title: 'Welcome to Tinsur-AI',
      description: 'Your complete insurance management solution',
      content: 'Get started with creating your first client profile and generating insurance quotes.',
      guideName: 'Client Onboarding Guide',
      guideLink: '/help/guides/client-guide',
    },
    {
      id: 2,
      title: 'Create Your First Client',
      description: 'Build your client database',
      content: 'Learn how to add and manage client information, contact details, and communication history.',
      guideName: 'Client Management Tutorial',
    },
    {
      id: 3,
      title: 'Generate Your First Quote',
      description: 'Create an insurance quote with AI assistance',
      content: 'Discover how to create accurate quotes, customize coverage, and send to clients.',
      guideName: 'Quote Creation Guide',
    },
    {
      id: 4,
      title: 'Manage Policies',
      description: 'Track and manage insurance policies',
      content: 'Learn policy management, renewal tracking, and claims processing.',
      guideName: 'Policy Management Guide',
    },
  ],
  admin: [
    {
      id: 1,
      title: 'Welcome, Administrator',
      description: 'System setup and configuration',
      content: 'Set up your Tinsur-AI instance with proper configuration and security settings.',
      guideName: 'Admin Setup Guide',
      guideLink: '/help/guides/admin-guide',
    },
    {
      id: 2,
      title: 'User Management',
      description: 'Create and manage team members',
      content: 'Add users, assign roles, and configure permissions for your team.',
    },
    {
      id: 3,
      title: 'Security Configuration',
      description: 'Secure your system',
      content: 'Set up 2FA, password policies, and access control settings.',
    },
    {
      id: 4,
      title: 'System Monitoring',
      description: 'Monitor system health and usage',
      content: 'View analytics, audit logs, and system performance metrics.',
    },
  ],
  insurance_company: [
    {
      id: 1,
      title: 'Welcome to Tinsur-AI Enterprise',
      description: 'Insurance company management platform',
      content: 'Set up your insurance company profile and start receiving quotes.',
      guideName: 'Insurance Company Guide',
      guideLink: '/help/guides/insurance-guide',
    },
    {
      id: 2,
      title: 'Team Setup',
      description: 'Configure your underwriting team',
      content: 'Add underwriters, operations staff, and configure roles.',
    },
    {
      id: 3,
      title: 'Quote Management',
      description: 'Process incoming quotes',
      content: 'Review, underwrite, approve, or decline quotes from agents.',
    },
    {
      id: 4,
      title: 'Integration',
      description: 'Connect with your systems',
      content: 'Set up integrations with your existing business systems.',
    },
  ],
  default: [
    {
      id: 1,
      title: 'Welcome to Tinsur-AI',
      description: 'Your complete insurance management solution',
      content: 'Let\'s get you started with a quick orientation of the platform.',
    },
    {
      id: 2,
      title: 'Dashboard Overview',
      description: 'Navigate the main dashboard',
      content: 'Explore the key features and navigation options available to you.',
    },
    {
      id: 3,
      title: 'Set Up Your Profile',
      description: 'Customize your account',
      content: 'Complete your user profile and preferences.',
    },
    {
      id: 4,
      title: 'You\'re All Set!',
      description: 'Ready to go',
      content: 'You\'re ready to start using Tinsur-AI. Let\'s begin!',
    },
  ],
};

export function OnboardingWizard({
  steps: customSteps,
  onComplete,
  onSkip,
  initialStep = 0,
  userRole = 'client',
}: OnboardingWizardProps) {
  const [currentStep, setCurrentStep] = useState(initialStep);
  const [isCompleting, setIsCompleting] = useState(false);
  const [isSkipping, setIsSkipping] = useState(false);

  const steps = customSteps.length > 0 ? customSteps : (defaultSteps[userRole] || defaultSteps.default);
  const step = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    setIsCompleting(true);
    try {
      if (onComplete) {
        await onComplete();
      }
    } finally {
      setIsCompleting(false);
    }
  };

  const handleSkip = async () => {
    setIsSkipping(true);
    try {
      if (onSkip) {
        await onSkip();
      }
    } finally {
      setIsSkipping(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <Card className="w-full max-w-2xl mx-4">
        {/* Header */}
        <CardHeader className="flex flex-row items-start justify-between space-y-0">
          <div className="space-y-2">
            <CardTitle className="text-2xl">{step.title}</CardTitle>
            <CardDescription className="text-base">{step.description}</CardDescription>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleSkip}
            className="h-8 w-8"
          >
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>

        {/* Progress Bar */}
        <div className="px-6 space-y-2">
          <div className="flex justify-between items-center text-sm text-muted-foreground">
            <span>Step {currentStep + 1} of {steps.length}</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Content */}
        <CardContent className="space-y-6 pt-6">
          <div className="prose prose-sm max-w-none">
            <p className="text-foreground leading-relaxed">{step.content}</p>
          </div>

          {/* Guide Link */}
          {step.guideLink && (
            <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
              <p className="text-sm font-medium mb-2">📖 Learn More</p>
              <p className="text-sm text-muted-foreground mb-3">
                {step.guideName && `Check out our ${step.guideName}`}
              </p>
              <Link href={step.guideLink}>
                <Button variant="outline" size="sm" className="gap-2">
                  Read Guide
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          )}
        </CardContent>

        {/* Footer with Actions */}
        <div className="flex items-center justify-between border-t p-6 space-x-4">
          <Button
            variant="outline"
            onClick={handleSkip}
            disabled={isSkipping}
          >
            {currentStep === steps.length - 1 ? 'Close' : 'Skip for Now'}
          </Button>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className="gap-2"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>

            {currentStep === steps.length - 1 ? (
              <Button
                onClick={handleComplete}
                disabled={isCompleting}
                className="gap-2 bg-green-600 hover:bg-green-700"
              >
                <CheckCircle className="h-4 w-4" />
                {isCompleting ? 'Completing...' : 'Complete Onboarding'}
              </Button>
            ) : (
              <Button onClick={handleNext} className="gap-2">
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>

        {/* Text Info */}
        <div className="px-6 pb-4 text-center text-xs text-muted-foreground">
          You can access this guide anytime from Help → Get Started
        </div>
      </Card>
    </div>
  );
}
