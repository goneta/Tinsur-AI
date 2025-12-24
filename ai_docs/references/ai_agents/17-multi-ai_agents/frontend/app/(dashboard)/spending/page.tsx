"use client";

import { useState, useCallback, useEffect } from "react";
import { SplitView } from "../../../components/layout/SplitView";
import { useAuth } from "@/components/auth/AuthContext";
import { useRouter } from "next/navigation";
import { SpendingSnapshot } from "@/components/spending/SpendingSnapshot";
import { SpendingChat } from "@/components/spending/SpendingChat";
import { SpendingSnapshotData } from "@/lib/types/spending";
import { Brain, MessageSquare } from "lucide-react";

export default function SpendingPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  // Shared state for snapshot and chat coordination
  const [snapshotLoaded, setSnapshotLoaded] = useState(false);
  const [snapshotData, setSnapshotData] = useState<SpendingSnapshotData | null>(
    null
  );

  // Memoize callback functions to prevent infinite re-renders
  const handleDataLoaded = useCallback((data: SpendingSnapshotData) => {
    setSnapshotData(data);
    setSnapshotLoaded(true);
  }, []);

  const handleLoadingStateChange = useCallback((loading: boolean) => {
    if (!loading) {
      // Additional logic can go here if needed
    }
  }, []);

  // Handle navigation side effect when authentication changes
  useEffect(() => {
    // Only redirect if loading is complete and user is not authenticated
    if (!isLoading && !isAuthenticated) {
      router.push("/");
    }
  }, [isLoading, isAuthenticated, router]);

  // Show loading state while authentication is being restored
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Show loading state while redirecting unauthenticated users
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <SplitView
      leftPanel={
        <div className="h-full flex flex-col">
          {/* Fixed Header */}
          <div className="flex-shrink-0 p-6 border-b border-border/30 bg-gradient-to-r from-background/95 to-background/90 backdrop-blur-sm relative z-10">
            {/* Subtle gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-cyan-500/5 pointer-events-none" />

            <div className="relative flex items-center gap-4 mb-3">
              {/* Mini FI Logo */}
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-br from-primary to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-sm">FI</span>
                </div>
                <div className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-cyan-400 rounded-full animate-pulse" />
              </div>

              {/* Header Text */}
              <div>
                <h2 className="text-2xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
                  Financial Intelligence Dashboard
                </h2>
                <p className="text-muted-foreground text-sm">
                  Welcome back, {user?.username}!
                </p>
              </div>
            </div>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-hidden">
            <SpendingSnapshot
              userId={user?.username || ""}
              onDataLoaded={handleDataLoaded}
              onLoadingStateChange={handleLoadingStateChange}
            />
          </div>
        </div>
      }
      rightPanel={
        <div className="h-full flex flex-col">
          {/* Fixed Header */}
          <div className="flex-shrink-0 p-6 border-b border-border/30 bg-gradient-to-r from-background/95 to-background/90 backdrop-blur-sm relative z-10">
            {/* Subtle gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-cyan-500/5 pointer-events-none" />

            <div className="relative flex items-center gap-4 mb-3">
              {/* AI Chat Icon */}
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-br from-primary to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
                  <Brain className="h-5 w-5 text-white" />
                </div>
                <div className="absolute -bottom-0.5 -right-0.5">
                  <MessageSquare className="h-4 w-4 text-cyan-400" />
                </div>
              </div>

              {/* Header Text */}
              <div>
                <h2 className="text-2xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
                  AI Financial Assistant
                </h2>
                <p className="text-muted-foreground text-sm">
                  Ask questions about your spending patterns
                </p>
              </div>
            </div>
          </div>

          {/* Scrollable Chat Container */}
          <div className="flex-1 overflow-hidden">
            <SpendingChat
              userId={user?.username || ""}
              isEnabled={snapshotLoaded}
              spendingData={snapshotData}
            />
          </div>
        </div>
      }
    />
  );
}
