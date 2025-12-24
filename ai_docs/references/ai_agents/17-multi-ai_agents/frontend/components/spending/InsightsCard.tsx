import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, Lightbulb, Sparkles, TrendingUp } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface InsightsCardProps {
  insights: string;
}

export function InsightsCard({ insights }: InsightsCardProps) {
  return (
    <Card className="bg-card/90 backdrop-blur-md border-border/50 shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden">
      {/* Glass effect overlay with subtle AI-inspired pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-white/5 pointer-events-none" />
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-primary/10 via-cyan-500/5 to-transparent rounded-full blur-3xl" />

      <CardHeader className="pb-4 relative">
        <CardTitle className="flex items-center gap-3 text-lg">
          <div className="relative">
            {/* Main brain icon with animated glow */}
            <div className="p-2 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 backdrop-blur-sm border border-amber-500/30 relative">
              <Brain className="h-5 w-5 text-amber-500" />
              {/* Pulsing glow effect */}
              <div className="absolute inset-0 rounded-xl bg-amber-500/20 animate-pulse" />
            </div>
            {/* Small sparkles around the brain */}
            <Sparkles className="absolute -top-1 -right-1 h-3 w-3 text-amber-400 animate-pulse" />
          </div>

          <div>
            <span className="bg-gradient-to-r from-amber-600 via-amber-500 to-orange-500 bg-clip-text text-transparent font-semibold">
              AI Financial Insights
            </span>
            <div className="h-0.5 w-16 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full mt-1" />
          </div>

          {/* Floating trend indicator */}
          <div className="ml-auto">
            <div className="p-1.5 rounded-lg bg-gradient-to-br from-primary/10 to-cyan-500/10 backdrop-blur-sm border border-primary/20">
              <TrendingUp className="h-4 w-4 text-primary" />
            </div>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="pt-0 relative">
        {insights && insights.trim() ? (
          <div className="relative">
            {/* AI processing indicator */}
            <div className="absolute top-0 right-0 flex items-center gap-1 text-xs text-muted-foreground bg-background/50 backdrop-blur-sm px-2 py-1 rounded-full border border-border/50">
              <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse" />
              AI Analysis
            </div>

            <div className="prose prose-sm dark:prose-invert max-w-none pt-6">
              <ReactMarkdown
                components={{
                  p: ({ children }) => (
                    <p className="text-sm text-muted-foreground leading-relaxed mb-4 last:mb-0 pl-4 border-l-2 border-amber-500/20">
                      {children}
                    </p>
                  ),
                  strong: ({ children }) => (
                    <strong className="font-semibold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                      {children}
                    </strong>
                  ),
                  em: ({ children }) => (
                    <em className="italic text-amber-600 dark:text-amber-400 font-medium">
                      {children}
                    </em>
                  ),
                  ul: ({ children }) => (
                    <ul className="space-y-2 text-sm text-muted-foreground ml-4 mt-3">
                      {children}
                    </ul>
                  ),
                  li: ({ children }) => (
                    <li className="flex items-start gap-3 p-2 rounded-lg bg-background/30 backdrop-blur-sm border border-border/30 hover:border-amber-500/30 transition-colors duration-200">
                      <div className="flex-shrink-0 w-2 h-2 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full mt-2" />
                      <span className="flex-1">{children}</span>
                    </li>
                  ),
                  code: ({ children }) => (
                    <code className="bg-amber-500/10 text-amber-700 dark:text-amber-300 px-2 py-1 rounded-md text-xs font-mono border border-amber-500/20">
                      {children}
                    </code>
                  ),
                }}
              >
                {insights}
              </ReactMarkdown>
            </div>

            {/* AI signature at bottom */}
            <div className="mt-6 flex items-center justify-between text-xs text-muted-foreground bg-gradient-to-r from-amber-500/5 to-orange-500/5 backdrop-blur-sm p-3 rounded-lg border border-amber-500/10">
              <div className="flex items-center gap-2">
                <Brain className="h-3 w-3 text-amber-500" />
                <span>Powered by Financial Intelligence AI</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-1 h-1 bg-green-500 rounded-full animate-pulse" />
                <span>Live Analysis</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 space-y-4">
            <div className="relative">
              <div className="p-4 rounded-2xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 backdrop-blur-sm border border-amber-500/20">
                <Brain className="h-8 w-8 text-amber-500" />
              </div>
              <Sparkles className="absolute -top-1 -right-1 h-4 w-4 text-amber-400 animate-pulse" />
            </div>
            <div className="text-center space-y-2">
              <p className="text-muted-foreground text-sm font-medium">
                AI is analyzing your financial data
              </p>
              <p className="text-muted-foreground text-xs">
                Insights will appear once analysis is complete
              </p>
            </div>
            <div className="flex items-center gap-1 text-xs text-amber-500">
              <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse" />
              <div
                className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse"
                style={{ animationDelay: "0.3s" }}
              />
              <div
                className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse"
                style={{ animationDelay: "0.6s" }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
