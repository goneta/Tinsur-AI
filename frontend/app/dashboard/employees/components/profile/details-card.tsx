'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { User, Phone, MapPin } from 'lucide-react';
import { Employee } from '../../columns';

interface DetailsCardProps {
    employee: Employee;
}

export function DetailsCard({ employee }: DetailsCardProps) {
    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-medium flex items-center gap-2">
                    <User className="h-4 w-4 text-primary" />
                    Employee Details
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="space-y-1">
                    <div className="text-sm text-muted-foreground">Full Name</div>
                    <div className="font-medium text-lg">{employee.first_name} {employee.last_name}</div>
                </div>

                <div className="flex items-start gap-3">
                    <Phone className="h-4 w-4 mt-1 text-muted-foreground" />
                    <div className="space-y-1">
                        <div className="text-sm text-muted-foreground">Phone Number</div>
                        <div className="font-medium">{employee.phone || 'Not provided'}</div>
                    </div>
                </div>

                <div className="flex items-start gap-3">
                    <MapPin className="h-4 w-4 mt-1 text-muted-foreground" />
                    <div className="space-y-1">
                        <div className="text-sm text-muted-foreground">Address / City</div>
                        <div className="font-medium">{employee.pos_location?.city || 'Not provided'}</div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
