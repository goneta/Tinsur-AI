"use client";

import { useState, useEffect, useCallback } from "react";
import { SpendingSnapshotData } from "@/lib/types/spending";
import { Loader2, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { SpendingCard } from "./SpendingCard";
import { ActivitiesList } from "./ActivitiesList";
import { InsightsCard } from "./InsightsCard";

interface SpendingSnapshotProps {
  userId: string;
  onDataLoaded?: (data: SpendingSnapshotData) => void;
  onLoadingStateChange?: (isLoading: boolean) => void;
}

export function SpendingSnapshot({
  userId,
  onDataLoaded,
  onLoadingStateChange,
}: SpendingSnapshotProps) {
  const [data, setData] = useState<SpendingSnapshotData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSpendingData = useCallback(async () => {
    let successfulResult: SpendingSnapshotData | null = null;

    try {
      setIsLoading(true);
      onLoadingStateChange?.(true);
      setError(null);

      console.log("[FRONTEND] 🚀 Fetching spending data for userId:", userId);

      const response = await fetch("/api/cymbal/spending-snapshot", {
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
      setError(`Failed to load spending data: ${errorMessage}`);
      console.error("[FRONTEND] ❌ Spending data fetch error:", err);
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
      fetchSpendingData();
    }
  }, [userId, fetchSpendingData]);

  // Loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-b from-transparent via-primary/[0.02] to-transparent relative">
        {/* Glass loading card */}
        <div className="bg-card/90 backdrop-blur-md border border-border/50 rounded-2xl p-8 shadow-lg relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-white/5 pointer-events-none" />

          <div className="relative flex flex-col items-center space-y-6">
            {/* Animated FI logo */}
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-primary to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg animate-pulse">
                <span className="text-white font-bold text-lg">FI</span>
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-cyan-400 rounded-full animate-pulse" />
            </div>

            {/* Loading spinner */}
            <Loader2 className="h-8 w-8 animate-spin text-primary" />

            <div className="text-center space-y-2">
              <p className="text-foreground font-semibold">
                Analyzing Financial Data
              </p>
              <p className="text-muted-foreground text-sm">
                AI is processing your spending patterns...
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
      <div className="h-full p-6 flex items-center justify-center bg-gradient-to-b from-transparent via-primary/[0.02] to-transparent">
        <div className="w-full max-w-md">
          <Alert
            variant="destructive"
            className="bg-card/90 backdrop-blur-md border-destructive/20 shadow-lg relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-white/5 pointer-events-none" />
            <div className="relative">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="flex flex-col space-y-4 pt-2">
                <div className="space-y-2">
                  <p className="font-semibold text-destructive">
                    Unable to load financial data
                  </p>
                  <p className="text-sm text-muted-foreground">{error}</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={fetchSpendingData}
                  className="self-start bg-background/50 hover:bg-background border-destructive/30 hover:border-destructive/50 text-destructive hover:text-destructive"
                >
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4" />
                    Retry Analysis
                  </div>
                </Button>
              </AlertDescription>
            </div>
          </Alert>
        </div>
      </div>
    );
  }

  // Success state - render the dashboard
  console.log("[FRONTEND] 🎨 Rendering dashboard with data:");
  console.log("[FRONTEND] 🎨 Income:", data?.income);
  console.log("[FRONTEND] 🎨 Expenses:", data?.expenses);
  console.log("[FRONTEND] 🎨 Activities count:", data?.activities?.length);
  console.log("[FRONTEND] 🎨 Activities:", data?.activities);
  console.log("[FRONTEND] 🎨 Insights length:", data?.insights?.length);
  console.log(
    "[FRONTEND] 🎨 Insights preview:",
    data?.insights?.substring(0, 100)
  );

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-transparent via-primary/[0.02] to-transparent relative">
      {/* Subtle background pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.05),transparent_50%)] pointer-events-none" />

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6 space-y-8">
          <div className="relative space-y-8">
            {/* Income and Expenses Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <SpendingCard
                title="Income"
                amount={data?.income || 0}
                variant="success"
              />
              <SpendingCard
                title="Expenses"
                amount={data?.expenses || 0}
                variant="destructive"
              />
            </div>

            {/* Activities List */}
            <div className="transform hover:scale-[1.01] transition-transform duration-300">
              <ActivitiesList activities={data?.activities || []} />
            </div>

            {/* Financial Insights */}
            <div className="transform hover:scale-[1.01] transition-transform duration-300">
              <InsightsCard insights={data?.insights || ""} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
