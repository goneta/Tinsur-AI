"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, Calendar, UserCheck } from "lucide-react";
import { cn } from "@/lib/utils";

// Smart text formatting function for advisor data
function formatAdvisorText(text: string) {
  // Split text by common advisor patterns while preserving delimiters
  const parts = text.split(
    /(\b[A-Z][a-z]+ [A-Z][a-z]+\b|\d{2}:\d{2}-\d{2}:\d{2}|\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b|Investment:|Loans:|Mortgage:|Available:)/g
  );

  return parts.map((part, index) => {
    // Person names (e.g., "Bob Williams", "Alice Johnson")
    if (part.match(/\b[A-Z][a-z]+ [A-Z][a-z]+\b/)) {
      return (
        <span key={index} className="font-bold text-base text-foreground">
          {part}
        </span>
      );
    }

    // Time slots (e.g., "09:00-11:00", "13:00-15:00")
    if (part.match(/\d{2}:\d{2}-\d{2}:\d{2}/)) {
      return (
        <span
          key={index}
          className="font-mono font-semibold text-sm bg-primary/10 text-primary px-2 py-0.5 rounded-md"
        >
          {part}
        </span>
      );
    }

    // Days of the week
    if (
      part.match(
        /\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b/
      )
    ) {
      return (
        <span key={index} className="font-semibold text-sm text-foreground">
          {part}
        </span>
      );
    }

    // Categories (Investment:, Loans:, Mortgage:, Available:)
    if (part.match(/(?:Investment:|Loans:|Mortgage:|Available:)/)) {
      return (
        <span
          key={index}
          className="font-semibold text-sm text-muted-foreground"
        >
          {part}
        </span>
      );
    }

    // Regular text (commas, hyphens, etc.)
    return (
      <span key={index} className="text-sm text-muted-foreground">
        {part}
      </span>
    );
  });
}

interface AdvisorsCardProps {
  title: string;
  items: string[];
  variant?: "advisors" | "meetings" | "default";
}

export function AdvisorsCard({
  title,
  items,
  variant = "default",
}: AdvisorsCardProps): JSX.Element {
  const getIcon = () => {
    switch (variant) {
      case "advisors":
        return <UserCheck className="h-5 w-5" />;
      case "meetings":
        return <Calendar className="h-5 w-5" />;
      default:
        return <Users className="h-5 w-5" />;
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case "advisors":
        return {
          icon: "text-emerald-600 dark:text-emerald-400",
          badge:
            "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800",
          header: "text-emerald-900 dark:text-emerald-100",
        };
      case "meetings":
        return {
          icon: "text-orange-600 dark:text-orange-400",
          badge:
            "bg-orange-50 text-orange-700 dark:bg-orange-950 dark:text-orange-300 border-orange-200 dark:border-orange-800",
          header: "text-orange-900 dark:text-orange-100",
        };
      default:
        return {
          icon: "text-blue-600 dark:text-blue-400",
          badge:
            "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 border-blue-200 dark:border-blue-800",
          header: "text-blue-900 dark:text-blue-100",
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <Card className="hover:shadow-md transition-all duration-200 border-2">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle
            className={cn(
              "text-lg font-semibold flex items-center gap-2",
              styles.header
            )}
          >
            <span className={cn("transition-colors", styles.icon)}>
              {getIcon()}
            </span>
            {title}
          </CardTitle>
          <Badge
            variant="outline"
            className={cn("text-xs px-2 py-1", styles.badge)}
          >
            {items.length} {items.length === 1 ? "item" : "items"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {items.length === 0 ? (
            <div className="text-center py-6">
              {variant === "meetings" ? (
                <div className="bg-gradient-to-br from-orange-50 to-orange-100/50 dark:from-orange-950/50 dark:to-orange-900/30 border-2 border-dashed border-orange-200 dark:border-orange-800/50 rounded-xl p-6 space-y-3">
                  <div className="flex items-center justify-center">
                    <Calendar className="h-8 w-8 text-orange-500 mb-2" />
                  </div>
                  <div className="space-y-2">
                    <p className="text-orange-800 dark:text-orange-200 font-semibold text-sm">
                      No meetings scheduled yet
                    </p>
                    <p className="text-orange-700 dark:text-orange-300 text-xs leading-relaxed">
                      Make sure to schedule one with your upcoming Advisor
                    </p>
                  </div>
                  <div className="pt-1">
                    <div className="inline-flex items-center text-xs text-orange-600 dark:text-orange-400 font-medium">
                      <span className="w-2 h-2 bg-orange-500 rounded-full mr-2 animate-pulse"></span>
                      Ready to get started
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground text-sm italic">
                  No {title.toLowerCase()} found
                </p>
              )}
            </div>
          ) : (
            <div className="max-h-[500px] overflow-y-auto space-y-3">
              {items.map((item, index) => (
                <div
                  key={index}
                  className="group relative bg-card hover:bg-accent/20 rounded-lg p-4 shadow-sm hover:shadow-md border border-border/50 hover:border-border transition-all duration-200 cursor-default"
                >
                  <div className="leading-relaxed space-y-1">
                    {formatAdvisorText(item)}
                  </div>
                  {/* Variant-specific accent line */}
                  <div
                    className={cn(
                      "absolute left-0 top-0 w-1 h-full rounded-l-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200",
                      variant === "advisors"
                        ? "bg-emerald-500"
                        : variant === "meetings"
                        ? "bg-orange-500"
                        : "bg-blue-500"
                    )}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
