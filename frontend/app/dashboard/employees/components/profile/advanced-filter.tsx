'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar as CalendarIcon, Filter as FilterIcon } from 'lucide-react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import { useEffect } from 'react';

export type FilterPeriod = 'day' | 'week' | 'month' | 'year';

interface AdvancedFilterProps {
    onFilterChange: (period: FilterPeriod, value: any) => void;
}

export function AdvancedFilter({ onFilterChange }: AdvancedFilterProps) {
    const [period, setPeriod] = useState<FilterPeriod>('month');
    const [date, setDate] = useState<Date>(new Date());
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const handlePeriodChange = (val: string) => {
        const p = val as FilterPeriod;
        setPeriod(p);
        onFilterChange(p, date);
    };

    const handleDateChange = (newDate: Date | undefined) => {
        if (newDate) {
            setDate(newDate);
            onFilterChange(period, newDate);
        }
    };

    if (!mounted) return (
        <Card className="bg-muted/30 border-dashed">
            <CardContent className="p-4 flex h-16 animate-pulse bg-muted/20" />
        </Card>
    );

    return (
        <Card className="bg-muted/30 border-dashed">
            <CardContent className="p-4 flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-2">
                    <FilterIcon className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Filter by Period:</span>
                </div>

                <Select value={period} onValueChange={handlePeriodChange}>
                    <SelectTrigger className="w-[140px] bg-white">
                        <SelectValue placeholder="Period" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="day">Day</SelectItem>
                        <SelectItem value="week">Week</SelectItem>
                        <SelectItem value="month">Month</SelectItem>
                        <SelectItem value="year">Year</SelectItem>
                    </SelectContent>
                </Select>

                <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">Select:</span>
                    <Popover>
                        <PopoverTrigger asChild>
                            <Button
                                variant={"outline"}
                                className={cn(
                                    "w-[240px] justify-start text-left font-normal bg-white",
                                    !date && "text-muted-foreground"
                                )}
                            >
                                <CalendarIcon className="mr-2 h-4 w-4" />
                                {date ? (
                                    period === 'month' ? format(date, 'MMMM yyyy') :
                                        period === 'year' ? format(date, 'yyyy') :
                                            format(date, 'PPP')
                                ) : <span>Pick a date</span>}
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                                mode="single"
                                selected={date}
                                onSelect={handleDateChange}
                                initialFocus
                            />
                        </PopoverContent>
                    </Popover>
                </div>

                <div className="ml-auto text-xs text-muted-foreground italic">
                    Filtering all performance data by {period} selection
                </div>
            </CardContent>
        </Card>
    );
}
