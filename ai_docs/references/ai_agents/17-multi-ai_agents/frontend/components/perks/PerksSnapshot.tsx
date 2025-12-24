"use client";

import { useState, useEffect, useCallback } from "react";
import { PerksSnapshotData } from "@/lib/types/perks";
import { Loader2, AlertCircle, Gift } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { PerksCard } from "./PerksCard";
import { InsightsCard } from "../spending/InsightsCard";

interface PerksSnapshotProps {
  userId: string;
  onDataLoaded?: (data: PerksSnapshotData) => void;
  onLoadingStateChange?: (isLoading: boolean) => void;
}

export function PerksSnapshot({
  userId,
  onDataLoaded,
  onLoadingStateChange,
}: PerksSnapshotProps) {
  const [data, setData] = useState<PerksSnapshotData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPerksData = useCallback(async (): Promise<void> => {
    let successfulResult: PerksSnapshotData | null = null;

    try {
      setIsLoading(true);
      onLoadingStateChange?.(true);
      setError(null);

      console.log("[FRONTEND] 🚀 Fetching perks data for userId:", userId);

      const response = await fetch("/api/cymbal/perks-snapshot", {
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
      setError(`Failed to load perks data: ${errorMessage}`);
      console.error("[FRONTEND] ❌ Perks data fetch error:", err);
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
      fetchPerksData();
    }
  }, [userId, fetchPerksData]);

  // Loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-b from-transparent via-primary/[0.02] to-transparent relative">
        {/* Glass loading card */}
        <div className="bg-card/90 backdrop-blur-md border border-border/50 rounded-2xl p-8 shadow-lg relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-white/5 pointer-events-none" />

          <div className="relative flex flex-col items-center space-y-6">
            {/* Animated Perks logo */}
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-primary to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg animate-pulse">
                <Gift className="h-8 w-8 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-cyan-400 rounded-full animate-pulse" />
            </div>

            {/* Loading spinner */}
            <Loader2 className="h-8 w-8 animate-spin text-primary" />

            <div className="text-center space-y-2">
              <p className="text-foreground font-semibold">
                Analyzing Perks Data
              </p>
              <p className="text-muted-foreground text-sm">
                AI is processing your benefits and financial perks...
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
              onClick={fetchPerksData}
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
  console.log("[FRONTEND] 🎨 Rendering perks dashboard with data:");
  console.log("[FRONTEND] 🎨 Activities:", data?.activities);
  console.log("[FRONTEND] 🎨 Partners:", data?.partners);
  console.log("[FRONTEND] 🎨 Insights length:", data?.insights?.length);
  console.log(
    "[FRONTEND] 🎨 Insights preview:",
    data?.insights?.substring(0, 100)
  );

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="p-6 space-y-4 pb-8">
          {/* Perks Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <PerksCard
              title="Your Benefits"
              items={data?.activities || []}
              variant="activities"
            />
            <PerksCard
              title="Bank Partners"
              items={data?.partners || []}
              variant="partners"
            />
          </div>

          {/* Financial Insights */}
          <InsightsCard insights={data?.insights || ""} />
        </div>
      </div>
    </div>
  );
}
