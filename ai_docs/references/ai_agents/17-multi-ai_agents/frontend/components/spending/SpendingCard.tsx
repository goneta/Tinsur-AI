import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown, DollarSign } from "lucide-react";
import { cn } from "@/lib/utils";

interface SpendingCardProps {
  title: string;
  amount: number;
  variant: "success" | "destructive";
}

export function SpendingCard({ title, amount, variant }: SpendingCardProps) {
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const getIcon = () => {
    if (variant === "success") {
      return (
        <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
      );
    } else if (variant === "destructive") {
      return (
        <TrendingDown className="h-5 w-5 text-red-600 dark:text-red-400" />
      );
    }
    return <DollarSign className="h-5 w-5 text-gray-600 dark:text-gray-400" />;
  };

  const getIconBackground = () => {
    if (variant === "success") {
      return "bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-sm border border-green-500/30";
    } else if (variant === "destructive") {
      return "bg-gradient-to-br from-red-500/20 to-rose-500/20 backdrop-blur-sm border border-red-500/30";
    }
    return "bg-gradient-to-br from-primary/20 to-cyan-500/20 backdrop-blur-sm border border-primary/30";
  };

  const getAmountColor = () => {
    if (variant === "success") {
      return "text-green-600 dark:text-green-400";
    } else if (variant === "destructive") {
      return "text-red-600 dark:text-red-400";
    }
    return "text-primary";
  };

  const getCardBackground = () => {
    if (variant === "success") {
      return "bg-card/90 backdrop-blur-md border-green-500/20 hover:border-green-500/30 shadow-lg hover:shadow-green-500/10";
    } else if (variant === "destructive") {
      return "bg-card/90 backdrop-blur-md border-red-500/20 hover:border-red-500/30 shadow-lg hover:shadow-red-500/10";
    }
    return "bg-card/90 backdrop-blur-md border-primary/20 hover:border-primary/30 shadow-lg hover:shadow-primary/10";
  };

  return (
    <Card
      className={cn(
        "transition-all duration-300 hover:scale-105 group relative overflow-hidden",
        getCardBackground()
      )}
    >
      {/* Glass effect overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-white/5 pointer-events-none" />

      <CardContent className="p-6 relative">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-sm font-semibold text-muted-foreground/90 uppercase tracking-wide">
              {title}
            </p>
            <p
              className={cn(
                "text-3xl font-bold tracking-tight transition-colors duration-200",
                getAmountColor()
              )}
            >
              {formatCurrency(amount)}
            </p>
            {/* Subtle indicator line */}
            <div
              className={cn(
                "h-1 w-16 rounded-full transition-all duration-300 group-hover:w-20",
                variant === "success"
                  ? "bg-gradient-to-r from-green-500 to-emerald-500"
                  : variant === "destructive"
                  ? "bg-gradient-to-r from-red-500 to-rose-500"
                  : "bg-gradient-to-r from-primary to-cyan-500"
              )}
            />
          </div>

          <div className="relative">
            {/* Glow effect behind icon */}
            <div
              className={cn(
                "absolute inset-0 rounded-2xl blur-xl transition-opacity duration-300 opacity-0 group-hover:opacity-100",
                variant === "success"
                  ? "bg-green-500/30"
                  : variant === "destructive"
                  ? "bg-red-500/30"
                  : "bg-primary/30"
              )}
            />

            {/* Icon container */}
            <div
              className={cn(
                "relative p-4 rounded-2xl transition-all duration-300 group-hover:scale-110",
                getIconBackground()
              )}
            >
              {getIcon()}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
