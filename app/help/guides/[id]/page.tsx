'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { GuideViewer } from '@/components/help/guide-viewer';
import { Skeleton } from '@/components/ui/skeleton';

interface Guide {
  id: string;
  title: string;
  description: string;
  content: string;
  estimated_read_time: number;
}

export default function GuidePage() {
  const params = useParams();
  const guideId = params.id as string;
  const [guide, setGuide] = useState<Guide | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadGuide();
    checkCompletion();
  }, [guideId]);

  const loadGuide = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/api/v1/help/guides/${guideId}`);
      if (!response.ok) {
        throw new Error('Failed to load guide');
      }
      const data = await response.json();
      setGuide(data);

      // Track access
      await fetch(`/api/v1/help/guides/${guideId}/access`, {
        method: 'GET',
      }).catch(() => {
        // Silently fail, don't break the user experience
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load guide');
    } finally {
      setLoading(false);
    }
  };

  const checkCompletion = async () => {
    try {
      const response = await fetch('/api/v1/help/completion-status');
      if (response.ok) {
        const data = await response.json();
        setIsCompleted(data.completed_guides.includes(guideId));
      }
    } catch (err) {
      console.error('Failed to check completion:', err);
    }
  };

  const handleMarkComplete = async (guideId: string) => {
    try {
      const response = await fetch(`/api/v1/help/guides/${guideId}/mark-complete`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to mark complete');
      }
      setIsCompleted(true);
    } catch (err) {
      console.error('Error marking guide complete:', err);
      throw err;
    }
  };

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold">Guide not found</h2>
          <p className="text-muted-foreground">{error}</p>
          <a href="/help/guides" className="text-primary hover:underline">
            Back to guides
          </a>
        </div>
      </div>
    );
  }

  if (loading || !guide) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-full" />
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  return (
    <GuideViewer
      guideId={guide.id}
      title={guide.title}
      description={guide.description}
      content={guide.content}
      estimatedReadTime={guide.estimated_read_time}
      isCompleted={isCompleted}
      onMarkComplete={handleMarkComplete}
    />
  );
}
