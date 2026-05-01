"use client";

import { useState, useEffect } from "react";
import { format, subDays, startOfMonth, startOfYear } from "date-fns";
import { Calendar as CalendarIcon, Filter, Download } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { AnalyticsFilter } from "@/lib/types/analytics";
import { useLanguage } from "@/contexts/language-context";

interface UnifiedFilterProps {
    initialFilter: AnalyticsFilter;
    onFilterChange: (filter: AnalyticsFilter) => void;
    onExport: (format: "csv" | "pdf") => void;
}

export function UnifiedFilter({
    initialFilter,
    onFilterChange,
    onExport,
}: UnifiedFilterProps) {
    const { t } = useLanguage();
    const [filter, setFilter] = useState<AnalyticsFilter>(initialFilter);
    const [dateRange, setDateRange] = useState<{
        from: Date | undefined;
        to: Date | undefined;
    }>({
        from: initialFilter.start_date ? new Date(initialFilter.start_date) : undefined,
        to: initialFilter.end_date ? new Date(initialFilter.end_date) : undefined,
    });

    const handlePeriodChange = (value: string) => {
        let newStart = new Date();
        const newEnd = new Date();
        const type = value as AnalyticsFilter["period_type"];

        switch (type) {
            case "day":
                newStart = newEnd; // Today
                break;
            case "week":
                newStart = subDays(newEnd, 7);
                break;
            case "month":
                newStart = startOfMonth(newEnd);
                break;
            case "year":
                newStart = startOfYear(newEnd);
                break;
            default:
                // Custom keeps current range or defaults to month
                if (dateRange.from) newStart = dateRange.from;
                break;
        }

        const newFilter = {
            ...filter,
            period_type: type,
            start_date: format(newStart, "yyyy-MM-dd"),
            end_date: format(newEnd, "yyyy-MM-dd"),
        };

        setFilter(newFilter);
        setDateRange({ from: newStart, to: newEnd });
        onFilterChange(newFilter);
    };

    const handleScopeChange = (value: string) => {
        const newFilter = { ...filter, scope: value as AnalyticsFilter["scope"] };
        setFilter(newFilter);
        onFilterChange(newFilter);
    };

    return (
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 border rounded-lg bg-card shadow-sm">
            <div className="flex flex-wrap items-center gap-2">
                <Filter className="w-5 h-5 text-muted-foreground mr-2" />

                {/* Period Selector */}
                <Select value={filter.period_type} onValueChange={handlePeriodChange}>
                    <SelectTrigger className="w-[140px]">
                        <SelectValue placeholder={t('analytics.select_period', 'Select Period')} />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="day">{t('analytics.period.today', 'Today')}</SelectItem>
                        <SelectItem value="week">{t('analytics.period.last_7_days', 'Last 7 Days')}</SelectItem>
                        <SelectItem value="month">{t('analytics.period.this_month', 'This Month')}</SelectItem>
                        <SelectItem value="year">{t('analytics.period.this_year', 'This Year')}</SelectItem>
                        <SelectItem value="custom">{t('analytics.period.custom_range', 'Custom Range')}</SelectItem>
                    </SelectContent>
                </Select>

                {/* Date Range Picker (Visible if Custom or just always visible for info?) */}
                <Popover>
                    <PopoverTrigger asChild>
                        <Button
                            variant={"outline"}
                            className={cn(
                                "w-[240px] justify-start text-left font-normal",
                                !dateRange.from && "text-muted-foreground"
                            )}
                        >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {dateRange.from ? (
                                dateRange.to ? (
                                    <>
                                        {format(dateRange.from, "PPP")} -{" "}
                                        {format(dateRange.to, "PPP")}
                                    </>
                                ) : (
                                    format(dateRange.from, "PPP")
                                )
                            ) : (
                                <span>{t('analytics.pick_date', 'Pick a date')}</span>
                            )}
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                        {/* Note: Simplified Calendar for now, ideally range picker */}
                        <div className="p-4">
                            <p className="text-sm text-muted-foreground mb-2">{t('analytics.start_date', 'Start Date')}</p>
                            <Calendar
                                mode="single"
                                selected={dateRange.from}
                                onSelect={(d) => {
                                    const newRange = { ...dateRange, from: d };
                                    setDateRange(newRange);
                                    if (d && dateRange.to) {
                                        const newFilter: AnalyticsFilter = {
                                            ...filter,
                                            start_date: format(d, "yyyy-MM-dd"),
                                            end_date: format(dateRange.to, "yyyy-MM-dd"),
                                            period_type: 'custom'
                                        };
                                        setFilter(newFilter);
                                        onFilterChange(newFilter);
                                    }
                                }}
                                initialFocus
                            />
                        </div>
                    </PopoverContent>
                </Popover>

                {/* Scope Selector */}
                <Select value={filter.scope} onValueChange={handleScopeChange}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder={t('analytics.select_scope', 'Select Scope')} />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="me">{t('analytics.scope.my_performance', 'My Performance')}</SelectItem>
                        <SelectItem value="team">{t('analytics.scope.my_team', 'My Team')}</SelectItem>
                        <SelectItem value="company">{t('analytics.scope.company_wide', 'Company Wide')}</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <div className="flex items-center gap-2">
                <Select onValueChange={(v) => onExport(v as "csv" | "pdf")}>
                    <SelectTrigger className="w-[130px]">
                        <Download className="mr-2 h-4 w-4" />
                        <SelectValue placeholder={t('analytics.export', 'Export')} />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="csv">{t('analytics.export_csv', 'Export CSV')}</SelectItem>
                        <SelectItem value="pdf" disabled>{t('analytics.export_pdf', 'Export PDF (Pro)')}</SelectItem>
                    </SelectContent>
                </Select>
            </div>
        </div>
    );
}
