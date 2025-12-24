"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Gift, Users, Star } from "lucide-react";
import { cn } from "@/lib/utils";

// Smart text formatting function for perks
function formatPerksText(text: string) {
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

    // Percentages (e.g., 10%, 15%, 20%)
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

interface PerksCardProps {
  title: string;
  items: string[];
  variant?: "activities" | "partners" | "default";
}

export function PerksCard({
  title,
  items,
  variant = "default",
}: PerksCardProps): JSX.Element {
  const getIcon = () => {
    switch (variant) {
      case "activities":
        return <Gift className="h-5 w-5" />;
      case "partners":
        return <Users className="h-5 w-5" />;
      default:
        return <Star className="h-5 w-5" />;
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case "activities":
        return {
          icon: "text-purple-600 dark:text-purple-400",
          badge:
            "bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300 border-purple-200 dark:border-purple-800",
          header: "text-purple-900 dark:text-purple-100",
        };
      case "partners":
        return {
          icon: "text-blue-600 dark:text-blue-400",
          badge:
            "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 border-blue-200 dark:border-blue-800",
          header: "text-blue-900 dark:text-blue-100",
        };
      default:
        return {
          icon: "text-green-600 dark:text-green-400",
          badge:
            "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300 border-green-200 dark:border-green-800",
          header: "text-green-900 dark:text-green-100",
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
                    {formatPerksText(item)}
                  </div>
                  {/* Variant-specific accent line */}
                  <div
                    className={cn(
                      "absolute left-0 top-0 w-1 h-full rounded-l-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200",
                      variant === "activities"
                        ? "bg-purple-500"
                        : variant === "partners"
                        ? "bg-blue-500"
                        : "bg-green-500"
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
