'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { GraduationCap, Award, ScrollText } from 'lucide-react';

interface EducationCardProps {
    employeeId: string;
}

export function EducationCard({ employeeId }: EducationCardProps) {
    // Mock education data as requested
    const educationItems = [
        { type: 'Degree', title: 'Master in Management', institution: 'ESSEC Business School', year: '2018', icon: <GraduationCap className="h-4 w-4" /> },
        { type: 'Diploma', title: 'Insurance Professional', institution: 'Insurance Institute', year: '2016', icon: <ScrollText className="h-4 w-4" /> },
        { type: 'Certificate', title: 'Risk Analysis Expert', institution: 'Global Risk Org', year: '2020', icon: <Award className="h-4 w-4" /> },
    ];

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-medium flex items-center gap-2">
                    <GraduationCap className="h-4 w-4 text-primary" />
                    Employee Education
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {educationItems.map((item, idx) => (
                        <div key={idx} className="flex gap-4 items-start pb-4 last:pb-0 border-b last:border-0 border-muted/50">
                            <div className="mt-1 p-2 rounded-full bg-primary/10 text-primary">
                                {item.icon}
                            </div>
                            <div className="flex-1 space-y-1">
                                <div className="flex justify-between items-center">
                                    <span className="font-semibold text-sm">{item.title}</span>
                                    <span className="text-xs text-muted-foreground">{item.year}</span>
                                </div>
                                <div className="text-xs text-muted-foreground">{item.institution}</div>
                                <div className="text-[10px] uppercase tracking-wider text-primary font-medium">{item.type}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
