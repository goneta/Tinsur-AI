"use client";

import { useState, useEffect, useCallback } from "react";
import { AdvisorsSnapshotData } from "@/lib/types/advisors";
import { Loader2, AlertCircle, UserCheck } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { AdvisorsCard } from "./AdvisorsCard";

interface AdvisorsSnapshotProps {
  userId: string;
  onDataLoaded?: (data: AdvisorsSnapshotData) => void;
  onLoadingStateChange?: (isLoading: boolean) => void;
}

export function AdvisorsSnapshot({
  userId,
  onDataLoaded,
  onLoadingStateChange,
}: AdvisorsSnapshotProps): JSX.Element {
  const [data, setData] = useState<AdvisorsSnapshotData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAdvisorsData = useCallback(async (): Promise<void> => {
    let successfulResult: AdvisorsSnapshotData | null = null;

    try {
      setIsLoading(true);
      onLoadingStateChange?.(true);
      setError(null);

      console.log("[FRONTEND] 🚀 Fetching advisors data for userId:", userId);

      const response = await fetch("/api/cymbal/advisors-snapshot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId }),
      });

      console.log("[FRONTEND] 📡 API response status:", response.status);
      console.log(
        "[FRONTEND] 📡 API response headers:",
        Object.fromEntries(response.headers.entries())
      );

      if (!response.ok) {
        console.log(
          "[FRONTEND] ❌ API request failed with status:",
          response.status
        );
        const errorData = await response.json().catch(() => ({}));
        console.log("[FRONTEND] ❌ Error response data:", errorData);
        throw new Error(
          errorData.message || `Request failed: ${response.status}`
        );
      }

      const result = await response.json();
      console.log("[FRONTEND] ✅ API response received:");
      console.log("[FRONTEND] ✅ Response data type:", typeof result);
      console.log(
        "[FRONTEND] ✅ Response data keys:",
        result ? Object.keys(result) : "no keys"
      );
      console.log(
        "[FRONTEND] ✅ Full response data:",
        JSON.stringify(result, null, 2)
      );

      setData(result);
      successfulResult = result;
      console.log("[FRONTEND] ✅ Data set in component state");
      console.log("[FRONTEND] ✅ Component will re-render with new data");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      setError(`Failed to load advisors data: ${errorMessage}`);
      console.error("[FRONTEND] ❌ Advisors data fetch error:", err);
    } finally {
      setIsLoading(false);
      onLoadingStateChange?.(false);

      // Only call onDataLoaded if we successfully loaded data
      if (successfulResult) {
        onDataLoaded?.(successfulResult);
      }
    }
  }, [userId, onLoadingStateChange, onDataLoaded]);

  useEffect(() => {
    if (userId) {
      fetchAdvisorsData();
    }
  }, [userId, fetchAdvisorsData]);

  // Loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-b from-transparent via-primary/[0.02] to-transparent relative">
        {/* Glass loading card */}
        <div className="bg-card/90 backdrop-blur-md border border-border/50 rounded-2xl p-8 shadow-lg relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-white/5 pointer-events-none" />

          <div className="relative flex flex-col items-center space-y-6">
            {/* Animated Advisors logo */}
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-primary to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg animate-pulse">
                <UserCheck className="h-8 w-8 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-cyan-400 rounded-full animate-pulse" />
            </div>

            {/* Loading spinner */}
            <Loader2 className="h-8 w-8 animate-spin text-primary" />

            <div className="text-center space-y-2">
              <p className="text-foreground font-semibold">
                Analyzing Advisors Data
              </p>
              <p className="text-muted-foreground text-sm">
                AI is processing your advisors and meetings...
              </p>
            </div>

            {/* Progress dots */}
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
              <div
                className="w-2 h-2 bg-primary rounded-full animate-pulse"
                style={{ animationDelay: "0.3s" }}
              />
              <div
                className="w-2 h-2 bg-primary rounded-full animate-pulse"
                style={{ animationDelay: "0.6s" }}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex-1 p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>{error}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchAdvisorsData}
              className="ml-4"
            >
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Success state - render the dashboard
  console.log("[FRONTEND] 🎨 Rendering advisors dashboard with data:");
  console.log("[FRONTEND] 🎨 Advisors:", data?.advisors);
  console.log("[FRONTEND] 🎨 Meetings:", data?.meetings);

  return (
    <div className="flex-1 p-6 space-y-4 overflow-y-auto">
      {/* Advisors Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <AdvisorsCard
          title="Available Advisors"
          items={data?.advisors || []}
          variant="advisors"
        />
        <AdvisorsCard
          title="Your Meetings"
          items={data?.meetings || []}
          variant="meetings"
        />
      </div>
    </div>
  );
}
