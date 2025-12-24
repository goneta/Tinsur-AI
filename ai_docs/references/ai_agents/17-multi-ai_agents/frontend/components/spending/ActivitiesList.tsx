import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Clock, ArrowUpRight, ArrowDownLeft } from "lucide-react";

interface ActivitiesListProps {
  activities: string[];
}

export function ActivitiesList({ activities }: ActivitiesListProps) {
  // Helper function to determine activity type and get appropriate icon
  const getActivityIcon = (activity: string) => {
    const activityLower = activity.toLowerCase();
    if (
      activityLower.includes("paycheck") ||
      activityLower.includes("income") ||
      activityLower.includes("salary")
    ) {
      return <ArrowUpRight className="h-4 w-4 text-green-500" />;
    } else if (
      activityLower.includes("transfer") &&
      activityLower.includes("savings")
    ) {
      return <ArrowDownLeft className="h-4 w-4 text-blue-500" />;
    } else {
      return <ArrowDownLeft className="h-4 w-4 text-red-500" />;
    }
  };

  const getActivityColor = (activity: string) => {
    const activityLower = activity.toLowerCase();
    if (
      activityLower.includes("paycheck") ||
      activityLower.includes("income") ||
      activityLower.includes("salary")
    ) {
      return "text-green-600 dark:text-green-400";
    } else if (
      activityLower.includes("transfer") &&
      activityLower.includes("savings")
    ) {
      return "text-blue-600 dark:text-blue-400";
    } else {
      return "text-red-600 dark:text-red-400";
    }
  };

  return (
    <Card className="bg-card/90 backdrop-blur-md border-border/50 shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden">
      {/* Glass effect overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-white/5 pointer-events-none" />

      <CardHeader className="pb-4 relative">
        <CardTitle className="flex items-center gap-3 text-lg">
          <div className="p-2 rounded-xl bg-gradient-to-br from-primary/20 to-cyan-500/20 backdrop-blur-sm border border-primary/30">
            <Activity className="h-5 w-5 text-primary" />
          </div>
          <div>
            <span className="bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
              Recent Activities
            </span>
            <div className="h-0.5 w-12 bg-gradient-to-r from-primary to-cyan-500 rounded-full mt-1" />
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="pt-0 relative">
        {activities.length > 0 ? (
          <div className="space-y-4">
            {activities.map((activity, index) => {
              // Parse activity to extract date, description, and amount
              const parts = activity.split(" - ");
              const date = parts[0] || "";
              const description = parts.slice(1).join(" - ") || "";

              return (
                <div key={index} className="group relative">
                  {/* Timeline line */}
                  {index < activities.length - 1 && (
                    <div className="absolute left-8 top-12 w-0.5 h-8 bg-gradient-to-b from-primary/50 to-transparent" />
                  )}

                  <div className="flex items-start gap-4 p-3 rounded-xl bg-background/30 backdrop-blur-sm border border-border/30 hover:border-primary/30 transition-all duration-200 group-hover:shadow-lg">
                    {/* Activity Icon */}
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-background/50 backdrop-blur-sm border border-border/50 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                      {getActivityIcon(activity)}
                    </div>

                    {/* Activity Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className="text-sm font-medium text-foreground group-hover:text-primary transition-colors duration-200">
                            {description}
                          </p>
                          <div className="flex items-center gap-2 mt-1">
                            <Clock className="h-3 w-3 text-muted-foreground" />
                            <p className="text-xs text-muted-foreground">
                              {date}
                            </p>
                          </div>
                        </div>

                        {/* Amount extraction and styling */}
                        {(() => {
                          const amountMatch = description.match(/\$[\d,]+/);
                          if (amountMatch) {
                            return (
                              <span
                                className={`text-sm font-semibold ${getActivityColor(
                                  activity
                                )}`}
                              >
                                {amountMatch[0]}
                              </span>
                            );
                          }
                          return null;
                        })()}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 space-y-3">
            <div className="p-3 rounded-full bg-muted/50 backdrop-blur-sm">
              <Activity className="h-6 w-6 text-muted-foreground" />
            </div>
            <p className="text-muted-foreground text-sm">
              No recent activities to display
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
