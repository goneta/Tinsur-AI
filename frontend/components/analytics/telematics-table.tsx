'use client';

import { TelematicsData } from '@/services/analyticsService';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils';

interface TelematicsTableProps {
    data: TelematicsData[];
}

export function TelematicsTable({ data }: TelematicsTableProps) {
    if (data.length === 0) {
        return <div className="text-center py-4 text-muted-foreground">No trip data available.</div>;
    }

    return (
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Distance (km)</TableHead>
                    <TableHead>Avg Speed</TableHead>
                    <TableHead>Safety Score</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {data.map((trip) => (
                    <TableRow key={trip.id}>
                        <TableCell>{formatDate(trip.trip_date)}</TableCell>
                        <TableCell>{trip.distance_km.toFixed(1)}</TableCell>
                        <TableCell>{trip.avg_speed.toFixed(1)} km/h</TableCell>
                        <TableCell>
                            <Badge variant={trip.safety_score > 90 ? 'secondary' : 'destructive'}>
                                {trip.safety_score}
                            </Badge>
                        </TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    );
}
