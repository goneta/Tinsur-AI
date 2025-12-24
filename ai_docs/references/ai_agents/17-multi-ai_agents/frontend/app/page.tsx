"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth/AuthContext";
import { LoginForm } from "@/components/auth/LoginForm";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Brain,
  DollarSign,
  TrendingUp,
  BarChart3,
  PieChart,
  LineChart,
  Shield,
  CheckCircle,
  AlertTriangle,
} from "lucide-react";

export default function Home() {
  const { isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const [showAgentPermissions, setShowAgentPermissions] = useState(false);

  useEffect(() => {
    // Simple effect: authenticated users always see agent permissions
    if (!isLoading) {
      if (isAuthenticated) {
        // Always show agent permission request after login
        setShowAgentPermissions(true);
      } else {
        // Not authenticated - hide permission screen
        setShowAgentPermissions(false);
      }
    }
  }, [isLoading, isAuthenticated]);

  // Handle agent permission granting
  const handleGrantPermissions = () => {
    setShowAgentPermissions(false);
    // Navigate directly to dashboard - no storage needed
    router.push("/spending");
  };

  // Handle agent permission denial
  const handleDenyPermissions = () => {
    setShowAgentPermissions(false);
    // Since the app requires agent permissions to function, sign user out
    logout();
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-primary/5 p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Show agent permissions request if authenticated but permissions not granted
  if (showAgentPermissions) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 relative overflow-hidden flex items-center justify-center p-4">
        {/* Background Elements */}
        <div className="absolute inset-0 opacity-5 dark:opacity-10">
          <div className="absolute top-20 left-10 sm:left-20">
            <Shield className="h-16 w-16 sm:h-24 sm:w-24 text-primary animate-pulse" />
          </div>
          <div className="absolute bottom-20 right-10 sm:right-32">
            <Brain className="h-18 w-18 sm:h-22 sm:w-22 text-primary animate-pulse" />
          </div>
        </div>

        {/* Agent Permission Request */}
        <div className="relative z-10 w-full max-w-2xl mx-auto">
          <Card className="shadow-2xl border-primary/20">
            <CardHeader className="text-center pb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-primary to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <CardTitle className="text-2xl font-bold">
                Enable AI Agents
              </CardTitle>
              <CardDescription className="text-base">
                To use FI, you must allow our AI agents to help manage your
                finances
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Benefits */}
              <div className="space-y-4">
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  What our AI agents will do for you:
                </h3>
                <ul className="space-y-3 text-sm text-muted-foreground">
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                    <span>
                      <strong>Daily Spending Agent:</strong> Analyze your
                      spending patterns, find savings opportunities, and manage
                      subscriptions
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                    <span>
                      <strong>Big Purchases Agent:</strong> Help plan major
                      purchases like homes and cars with personalized advice
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                    <span>
                      <strong>Trip Planning Agent:</strong> Budget and save for
                      vacations, find deals, and track travel expenses
                    </span>
                  </li>
                </ul>
              </div>

              {/* Security Notice */}
              <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
                  <div className="text-sm">
                    <p className="font-medium text-amber-800 dark:text-amber-200 mb-1">
                      Important:
                    </p>
                    <p className="text-amber-700 dark:text-amber-300">
                      Our AI agents will access your transaction history,
                      account balances, and spending patterns to provide
                      personalized financial guidance. Your data is encrypted
                      and never shared with third parties.
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <Button
                  onClick={handleGrantPermissions}
                  className="flex-1 bg-gradient-to-r from-primary to-cyan-500 hover:from-primary/90 hover:to-cyan-500/90"
                  size="lg"
                >
                  <CheckCircle className="mr-2 h-4 w-4" />I Allow Agent Access
                </Button>
                <Button
                  onClick={handleDenyPermissions}
                  variant="outline"
                  size="lg"
                  className="flex-1 border-red-200 text-red-600 hover:bg-red-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-950/20"
                >
                  Cancel
                </Button>
              </div>

              <p className="text-xs text-center text-muted-foreground mt-4">
                You must enable agent access to use FI. You can manage these
                permissions in your account settings later.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Show login form if not authenticated
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 relative overflow-hidden">
      <style jsx>{`
        @keyframes float {
          0%,
          100% {
            transform: translateY(0px) rotate(0deg);
          }
          50% {
            transform: translateY(-10px) rotate(1deg);
          }
        }
        @keyframes breathe {
          0%,
          100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.05);
          }
        }
        @keyframes bounce-slow {
          0%,
          100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-5px);
          }
        }
        @keyframes spin-slow {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        .animate-breathe {
          animation: breathe 4s ease-in-out infinite;
        }
        .animate-bounce-slow {
          animation: bounce-slow 3s ease-in-out infinite;
        }
        .animate-spin-slow {
          animation: spin-slow 20s linear infinite;
        }
        .group:hover .animate-spin-slow {
          animation: spin-slow 2s linear infinite;
        }
      `}</style>
      {/* Background Financial Elements */}
      <div className="absolute inset-0 opacity-5 dark:opacity-10">
        <div className="absolute top-20 left-10 sm:left-20">
          <TrendingUp
            className="h-16 w-16 sm:h-24 sm:w-24 text-primary animate-pulse"
            style={{ animationDelay: "0s", animationDuration: "3s" }}
          />
        </div>
        <div className="absolute top-40 right-10 sm:right-20">
          <BarChart3
            className="h-12 w-12 sm:h-20 sm:w-20 text-primary animate-pulse"
            style={{ animationDelay: "1s", animationDuration: "4s" }}
          />
        </div>
        <div className="absolute bottom-40 left-10 sm:left-32">
          <PieChart
            className="h-14 w-14 sm:h-18 sm:w-18 text-primary animate-pulse"
            style={{ animationDelay: "2s", animationDuration: "3.5s" }}
          />
        </div>
        <div className="absolute bottom-20 right-10 sm:right-32">
          <LineChart
            className="h-18 w-18 sm:h-22 sm:w-22 text-primary animate-pulse"
            style={{ animationDelay: "0.5s", animationDuration: "4.5s" }}
          />
        </div>
        {/* Additional chart elements for larger screens */}
        <div className="hidden lg:block absolute top-60 left-1/4">
          <BarChart3
            className="h-20 w-20 text-primary animate-pulse"
            style={{ animationDelay: "1.5s", animationDuration: "3.8s" }}
          />
        </div>
        <div className="hidden lg:block absolute top-32 right-1/3">
          <TrendingUp
            className="h-16 w-16 text-primary animate-pulse"
            style={{ animationDelay: "2.5s", animationDuration: "3.2s" }}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8">
        {/* Hero Section */}
        <div className="text-center mb-8 sm:mb-12 lg:mb-16 max-w-4xl mx-auto">
          {/* Enhanced Animated Logo + Brand Name (Horizontal Layout) */}
          <div className="mb-6 sm:mb-8 flex items-center justify-center gap-4 sm:gap-6">
            {/* Enhanced Animated Logo */}
            <div className="relative group cursor-pointer">
              {/* Floating backdrop glow */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-cyan-500/20 rounded-3xl blur-xl animate-pulse group-hover:from-primary/30 group-hover:to-cyan-500/30 transition-all duration-1000"></div>

              {/* Main logo container */}
              <div className="relative w-16 h-16 sm:w-20 sm:h-20 lg:w-24 lg:h-24 bg-gradient-to-br from-primary to-cyan-500 rounded-2xl flex items-center justify-center shadow-xl group-hover:shadow-primary/40 transition-all duration-500 transform group-hover:scale-110 group-hover:rotate-2 animate-float">
                <Brain className="h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12 text-white transition-all duration-500 group-hover:scale-110 animate-breathe" />
              </div>

              {/* Enhanced DollarSign with more complex animation */}
              <div className="absolute -top-1 -right-1 sm:-top-2 sm:-right-2 animate-bounce-slow">
                <div className="relative">
                  <div className="absolute inset-0 bg-cyan-400/30 rounded-full blur-sm animate-pulse"></div>
                  <DollarSign className="relative h-6 w-6 sm:h-7 sm:w-7 lg:h-8 lg:w-8 text-cyan-400 animate-pulse group-hover:animate-spin-slow group-hover:text-cyan-300 transition-all duration-500" />
                </div>
              </div>

              {/* Orbiting sparkle elements */}
              <div className="absolute inset-0 animate-spin-slow">
                <div
                  className="absolute top-0 left-1/2 w-1 h-1 bg-primary rounded-full animate-pulse"
                  style={{ animationDelay: "0s" }}
                ></div>
                <div
                  className="absolute top-1/2 right-0 w-1 h-1 bg-cyan-400 rounded-full animate-pulse"
                  style={{ animationDelay: "1s" }}
                ></div>
                <div
                  className="absolute bottom-0 left-1/2 w-1 h-1 bg-primary rounded-full animate-pulse"
                  style={{ animationDelay: "2s" }}
                ></div>
                <div
                  className="absolute top-1/2 left-0 w-1 h-1 bg-cyan-400 rounded-full animate-pulse"
                  style={{ animationDelay: "1.5s" }}
                ></div>
              </div>
            </div>

            {/* Brand Name */}
            <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold bg-gradient-to-r from-primary via-primary to-cyan-500 dark:from-primary dark:via-primary dark:to-cyan-400 bg-clip-text text-transparent">
              FI
            </h1>
          </div>

          {/* Tagline */}
          <div className="mb-6 sm:mb-8">
            <p className="text-xl sm:text-2xl lg:text-3xl font-semibold text-foreground mb-2">
              Your Financial Intelligence Partner
            </p>
            <p className="text-base sm:text-lg lg:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Harness the power of AI to analyze your spending patterns,
              optimize your budget, and make smarter financial decisions.
            </p>
          </div>

          {/* Feature Highlights */}
          <div className="hidden sm:flex justify-center gap-6 lg:gap-8 mb-8 lg:mb-12">
            <div className="text-center">
              <div className="w-12 h-12 lg:w-14 lg:h-14 bg-primary/10 dark:bg-primary/20 rounded-xl flex items-center justify-center mb-2 mx-auto">
                <TrendingUp className="h-6 w-6 lg:h-7 lg:w-7 text-primary" />
              </div>
              <p className="text-sm lg:text-base font-medium text-foreground">
                Smart Analysis
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 lg:w-14 lg:h-14 bg-primary/10 dark:bg-primary/20 rounded-xl flex items-center justify-center mb-2 mx-auto">
                <BarChart3 className="h-6 w-6 lg:h-7 lg:w-7 text-primary" />
              </div>
              <p className="text-sm lg:text-base font-medium text-foreground">
                Visual Insights
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 lg:w-14 lg:h-14 bg-primary/10 dark:bg-primary/20 rounded-xl flex items-center justify-center mb-2 mx-auto">
                <Brain className="h-6 w-6 lg:h-7 lg:w-7 text-primary" />
              </div>
              <p className="text-sm lg:text-base font-medium text-foreground">
                AI Recommendations
              </p>
            </div>
          </div>
        </div>

        {/* Login Form Section */}
        <div className="w-full max-w-md mx-auto relative">
          {/* Subtle glow effect behind login form */}
          <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-cyan-500/5 rounded-3xl blur-xl"></div>
          <div className="relative">
            <LoginForm />
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 sm:mt-12 lg:mt-16 text-center">
          <p className="text-sm text-muted-foreground">
            Secure • Intelligent • Personalized
          </p>
        </div>
      </div>
    </div>
  );
}
