import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ClaimData } from "@/types/ai-agent";
import { AlertCircle, Check, Edit2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ClaimPreview({ data, onAction }: { data: ClaimData, onAction?: (action: string, data: any) => void }) {
    if (!data) return null;

    return (
        <Card className="w-full border-l-4 border-l-orange-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-orange-500" />
                    Claim Report
                </CardTitle>
                <Badge variant="secondary">{data.status}</Badge>
            </CardHeader>
            <CardContent>
                <div className="space-y-4 pt-2">
                    <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Claim ID</span>
                        <code className="text-xs bg-muted px-2 py-1 rounded">{data.claim_number}</code>
                    </div>

                    <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Policy Policy</span>
                        <span className="text-sm font-medium">{data.policy_number}</span>
                    </div>

                    <div className="rounded-lg bg-orange-50 dark:bg-orange-950/20 p-3">
                        <p className="text-xs text-muted-foreground mb-1">Estimated Reserve</p>
                        <p className="text-xl font-bold text-orange-700 dark:text-orange-400">
                            ${data.estimated_amount?.toLocaleString()}
                        </p>
                    </div>

                    <div className="text-xs text-muted-foreground">
                        Incident Date: {data.incident_date}
                    </div>
                </div>

                {onAction && (
                    <div className="mt-6 flex gap-2">
                        <Button
                            className="flex-1 bg-orange-600 hover:bg-orange-700"
                            size="sm"
                            onClick={() => onAction('validate', data)}
                        >
                            <Check className="mr-2 h-4 w-4" />
                            Validate Claim
                        </Button>
                        <Button
                            variant="outline"
                            className="flex-1 border-orange-200"
                            size="sm"
                            onClick={() => onAction('modify', data)}
                        >
                            <Edit2 className="mr-2 h-4 w-4" />
                            Modify Claim
                        </Button>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
