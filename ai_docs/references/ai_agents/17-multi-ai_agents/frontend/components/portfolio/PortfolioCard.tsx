"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, DollarSign, Wallet } from "lucide-react";
import { cn } from "@/lib/utils";

// Smart text formatting function
function formatFinancialText(text: string) {
  // Split text by common financial patterns while preserving the delimiters
  const parts = text.split(
    /([$]\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+(?:\.\d+)?%|\d{1,3}(?:,\d{3})*(?:\.\d{2})?)/g
  );

  return parts.map((part, index) => {
    // Currency amounts (e.g., $60,000, $2,500.50)
    if (part.match(/[$]\d{1,3}(?:,\d{3})*(?:\.\d{2})?/)) {
      return (
        <span key={index} className="font-bold text-lg text-foreground">
          {part}
        </span>
      );
    }

    // Percentages (e.g., 5.8%, 12.5%)
    if (part.match(/\d+(?:\.\d+)?%/)) {
      return (
        <span
          key={index}
          className="font-semibold text-base bg-primary/10 text-primary px-2 py-0.5 rounded-md"
        >
          {part}
        </span>
      );
    }

    // Large numbers without $ (e.g., 60,000, 1,234)
    if (part.match(/\d{1,3}(?:,\d{3})+/)) {
      return (
        <span key={index} className="font-semibold text-base text-foreground">
          {part}
        </span>
      );
    }

    // Regular text
    return (
      <span key={index} className="text-sm text-muted-foreground">
        {part}
      </span>
    );
  });
}

interface PortfolioCardProps {
  title: string;
  items: string[];
  variant?: "success" | "destructive" | "default";
}

export function PortfolioCard({
  title,
  items,
  variant = "default",
}: PortfolioCardProps) {
  const getIcon = () => {
    switch (variant) {
      case "success":
        return <TrendingUp className="h-5 w-5" />;
      case "destructive":
        return <TrendingDown className="h-5 w-5" />;
      default:
        return <Wallet className="h-5 w-5" />;
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case "success":
        return {
          icon: "text-green-600 dark:text-green-400",
          badge:
            "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300 border-green-200 dark:border-green-800",
          header: "text-green-900 dark:text-green-100",
        };
      case "destructive":
        return {
          icon: "text-red-600 dark:text-red-400",
          badge:
            "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300 border-red-200 dark:border-red-800",
          header: "text-red-900 dark:text-red-100",
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
            <p className="text-muted-foreground text-sm italic">
              No {title.toLowerCase()} found
            </p>
          ) : (
            <div className="max-h-[500px] overflow-y-auto space-y-3">
              {items.map((item, index) => (
                <div
                  key={index}
                  className="group relative bg-card hover:bg-accent/20 rounded-lg p-4 shadow-sm hover:shadow-md border border-border/50 hover:border-border transition-all duration-200 cursor-default"
                >
                  <div className="leading-relaxed space-y-1">
                    {formatFinancialText(item)}
                  </div>
                  {/* Subtle accent line */}
                  <div
                    className={cn(
                      "absolute left-0 top-0 w-1 h-full rounded-l-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200",
                      variant === "success"
                        ? "bg-green-500"
                        : variant === "destructive"
                        ? "bg-red-500"
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
