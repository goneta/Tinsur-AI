import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PolicyData } from "@/types/ai-agent";
import { Calendar, Shield, Check, Edit2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export function PolicyPreview({ data, onAction }: { data: PolicyData, onAction?: (action: string, data: any) => void }) {
    if (!data) return null;

    return (
        <Card className="w-full border-green-200 dark:border-green-900 bg-green-50/50 dark:bg-green-900/10">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Shield className="h-4 w-4 text-green-600" />
                    Policy Generated
                </CardTitle>
                <Badge className="bg-green-600 hover:bg-green-700">{data.status || 'Active'}</Badge>
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{data.policy_number}</div>
                <p className="text-xs text-muted-foreground">
                    Policy Number
                </p>

                <div className="mt-6 space-y-4">
                    <div className="flex items-center justify-between border-b pb-2">
                        <span className="text-sm text-muted-foreground">Premium</span>
                        <span className="font-bold">${data.premium}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="flex flex-col gap-1">
                            <span className="text-muted-foreground flex items-center gap-1">
                                <Calendar className="h-3 w-3" /> Effective
                            </span>
                            <span>{data.effective_date}</span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-muted-foreground flex items-center gap-1">
                                <Calendar className="h-3 w-3" /> Expires
                            </span>
                            <span>{data.expiry_date}</span>
                        </div>
                    </div>
                </div>

                {onAction && (
                    <div className="mt-6 flex gap-2">
                        <Button
                            className="flex-1 bg-green-600 hover:bg-green-700"
                            size="sm"
                            onClick={() => onAction('validate', data)}
                        >
                            <Check className="mr-2 h-4 w-4" />
                            Validate Policy
                        </Button>
                        <Button
                            variant="outline"
                            className="flex-1 border-green-200"
                            size="sm"
                            onClick={() => onAction('modify', data)}
                        >
                            <Edit2 className="mr-2 h-4 w-4" />
                            Modify Policy
                        </Button>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
