'use client';

import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Clock, Check, Share2, Download, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface GuideViewerProps {
  guideId: string;
  title: string;
  description: string;
  content: string;
  estimatedReadTime: number;
  onMarkComplete?: (guideId: string) => Promise<void>;
  isCompleted?: boolean;
}

export function GuideViewer({
  guideId,
  title,
  description,
  content,
  estimatedReadTime,
  onMarkComplete,
  isCompleted = false,
}: GuideViewerProps) {
  const router = useRouter();
  const [isMarking, setIsMarking] = useState(false);
  const [marked, setMarked] = useState(isCompleted);
  const [error, setError] = useState<string | null>(null);

  const handleMarkComplete = async () => {
    if (!onMarkComplete || marked) return;

    setIsMarking(true);
    setError(null);
    try {
      await onMarkComplete(guideId);
      setMarked(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to mark guide as complete');
    } finally {
      setIsMarking(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPDF = () => {
    // Implement PDF download using a library like jsPDF
    alert('PDF export feature coming soon');
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: title,
          text: description,
          url: window.location.href,
        });
      } catch (err) {
        console.error('Share failed:', err);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard');
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.back()}
              className="gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
          <p className="text-lg text-muted-foreground">{description}</p>
        </div>
      </div>

      {/* Metadata */}
      <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-1">
          <Clock className="h-4 w-4" />
          <span>{estimatedReadTime} min read</span>
        </div>
        {marked && (
          <div className="flex items-center gap-1 text-green-600">
            <Check className="h-4 w-4" />
            <span>Completed</span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2">
        {!marked && onMarkComplete && (
          <Button
            onClick={handleMarkComplete}
            disabled={isMarking}
            className="gap-2"
          >
            <Check className="h-4 w-4" />
            {isMarking ? 'Marking...' : 'Mark as Complete'}
          </Button>
        )}
        <Button variant="outline" onClick={handlePrint} className="gap-2">
          <Download className="h-4 w-4" />
          Print
        </Button>
        <Button variant="outline" onClick={handleShare} className="gap-2">
          <Share2 className="h-4 w-4" />
          Share
        </Button>
      </div>

      {error && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-sm text-red-700">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <Card className="overflow-hidden">
        <CardContent className="pt-6">
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <ReactMarkdown
              components={{
                h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mt-6 mb-4" {...props} />,
                h2: ({ node, ...props }) => <h2 className="text-xl font-bold mt-6 mb-3" {...props} />,
                h3: ({ node, ...props }) => <h3 className="text-lg font-bold mt-4 mb-2" {...props} />,
                p: ({ node, ...props }) => <p className="mb-4 leading-relaxed" {...props} />,
                ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-4 space-y-1" {...props} />,
                ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-4 space-y-1" {...props} />,
                li: ({ node, ...props }) => <li className="ml-4" {...props} />,
                code: ({ node, ...props }) => (
                  <code className="bg-muted px-2 py-1 rounded text-sm font-mono" {...props} />
                ),
                pre: ({ node, ...props }) => (
                  <pre className="bg-muted p-4 rounded-lg overflow-x-auto mb-4" {...props} />
                ),
                blockquote: ({ node, ...props }) => (
                  <blockquote className="border-l-4 border-primary pl-4 py-2 italic my-4" {...props} />
                ),
                a: ({ node, ...props }) => (
                  <a className="text-primary hover:underline" {...props} />
                ),
                table: ({ node, ...props }) => (
                  <table className="w-full border-collapse border border-border my-4" {...props} />
                ),
                th: ({ node, ...props }) => (
                  <th className="border border-border bg-muted p-2 text-left" {...props} />
                ),
                td: ({ node, ...props }) => (
                  <td className="border border-border p-2" {...props} />
                ),
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        </CardContent>
      </Card>

      {/* Completion CTA */}
      {!marked && onMarkComplete && (
        <Card className="border-primary bg-primary/5">
          <CardContent className="pt-6">
            <p className="mb-4 text-sm">Finished reading this guide?</p>
            <Button onClick={handleMarkComplete} disabled={isMarking}>
              <Check className="h-4 w-4 mr-2" />
              Mark as Complete
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
