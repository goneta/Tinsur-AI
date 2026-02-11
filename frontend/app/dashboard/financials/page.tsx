'use client';

import { useEffect, useState, Fragment } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { formatDate } from '@/lib/utils';
import {
    BookOpen,
    History,
    BarChart3,
    PlusCircle,
    ArrowUpRight,
    ArrowDownRight,
    Scale,
    RefreshCw,
    AlertCircle,
    PieChart,
    Calendar as CalendarIcon,
    ChevronDown,
    TrendingUp
} from 'lucide-react';
import {
    accountingApi,
    Account,
    JournalEntry,
    TrialBalanceItem,
    ProfitLossData,
    BalanceSheetData
} from '@/lib/accounting-api';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

import { useLanguage } from '@/contexts/language-context';

export default function FinancialsPage() {
    const { t, formatPrice } = useLanguage();
    const [accounts, setAccounts] = useState<Account[]>([]);
    const [ledger, setLedger] = useState<JournalEntry[]>([]);
    const [trialBalance, setTrialBalance] = useState<TrialBalanceItem[]>([]);
    const [profitLoss, setProfitLoss] = useState<ProfitLossData | null>(null);
    const [balanceSheet, setBalanceSheet] = useState<BalanceSheetData | null>(null);
    const [loading, setLoading] = useState(true);
    const [initializing, setInitializing] = useState(false);

    // Date Filters
    const today = new Date().toISOString().split('T')[0];
    const firstDayOfYear = new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0];

    const [startDate, setStartDate] = useState(firstDayOfYear);
    const [endDate, setEndDate] = useState(today);
    const [asOfDate, setAsOfDate] = useState(today);
    const [rangeType, setRangeType] = useState('ytd');

    const fetchData = async () => {
        setLoading(true);
        try {
            const [accRes, ledgerRes, tbRes, plRes, bsRes] = await Promise.all([
                accountingApi.getAccounts(),
                accountingApi.getLedger(100),
                accountingApi.getTrialBalance(),
                accountingApi.getProfitLoss(startDate, endDate),
                accountingApi.getBalanceSheet(asOfDate)
            ]);
            setAccounts(accRes);
            setLedger(ledgerRes);
            setTrialBalance(tbRes);
            setProfitLoss(plRes);
            setBalanceSheet(bsRes);
        } catch (error) {
            console.error("Failed to fetch financial data", error);
        } finally {
            setLoading(false);
        }
    };

    const handleRangeChange = (value: string) => {
        setRangeType(value);
        const now = new Date();
        let start = new Date(now.getFullYear(), 0, 1);
        let end = now;

        if (value === 'month') {
            start = new Date(now.getFullYear(), now.getMonth(), 1);
        } else if (value === 'last_month') {
            start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
            end = new Date(now.getFullYear(), now.getMonth(), 0);
        } else if (value === 'quarter') {
            const quarter = Math.floor(now.getMonth() / 3);
            start = new Date(now.getFullYear(), quarter * 3, 1);
        } else if (value === 'last_quarter') {
            const quarter = Math.floor(now.getMonth() / 3) - 1;
            start = new Date(now.getFullYear(), quarter * 3, 1);
            end = new Date(now.getFullYear(), (quarter + 1) * 3, 0);
        }

        setStartDate(start.toISOString().split('T')[0]);
        setEndDate(end.toISOString().split('T')[0]);
    };

    useEffect(() => {
        fetchData();
    }, [startDate, endDate, asOfDate]);

    const handleInitialize = async () => {
        setInitializing(true);
        try {
            await accountingApi.initializeAccounts();
            await fetchData();
        } catch (error) {
            console.error("Initialization failed", error);
        } finally {
            setInitializing(false);
        }
    };



    const revenueAccounts = trialBalance.filter(i => accounts.find(a => a.code === i.account_code)?.account_type === 'Revenue');
    const expenseAccounts = trialBalance.filter(i => accounts.find(a => a.code === i.account_code)?.account_type === 'Expense');

    const totalRevenue = revenueAccounts.reduce((sum, i) => sum + Math.abs(i.balance), 0);
    const totalExpenses = expenseAccounts.reduce((sum, i) => sum + i.balance, 0);

    if (loading && accounts.length === 0) {
        return (
            <div className="flex h-[400px] items-center justify-center">
                <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
        );
    }

    if (accounts.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-[600px] space-y-6">
                <div className="bg-primary/10 p-6 rounded-full">
                    <BookOpen className="h-12 w-12 text-primary" />
                </div>
                <div className="text-center space-y-2">
                    <h2 className="text-2xl font-bold">{t('financials.no_accounts_title')}</h2>
                    <p className="text-muted-foreground max-w-md">{t('financials.no_accounts_desc')}</p>
                </div>
                <Button size="lg" onClick={handleInitialize} disabled={initializing}>
                    {initializing ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <PlusCircle className="mr-2 h-4 w-4" />}
                    {t('financials.init_ledger')}
                </Button>
            </div>
        );
    }

    return (
        <div className="space-y-6 max-w-7xl mx-auto p-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('financials.title')}</h2>
                    <p className="text-muted-foreground">{t('financials.desc')}</p>
                </div>
                <div className="flex gap-2">
                    <div className="flex items-center gap-2 bg-muted/50 p-1 rounded-md border text-xs text-muted-foreground px-3">
                        <CalendarIcon className="h-3 w-3" />
                        <span>Filter: {formatDate(startDate)} - {formatDate(endDate)}</span>
                    </div>
                    <Button variant="outline" size="sm" onClick={fetchData}>
                        <RefreshCw className="mr-2 h-4 w-4" /> {t('financials.refresh')}
                    </Button>
                </div>
            </div>

            {/* Global Date Filter Bar */}
            <Card className="bg-muted/10">
                <CardContent className="py-4 flex flex-wrap gap-6 items-center">
                    <div className="space-y-1">
                        <label className="text-xs font-medium text-muted-foreground ml-1">{t('financials.reporting_range')}</label>
                        <div className="flex gap-2">
                            <Select value={rangeType} onValueChange={handleRangeChange}>
                                <SelectTrigger className="w-[140px] h-9 bg-background">
                                    <SelectValue placeholder="Range" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="ytd">Year to Date</SelectItem>
                                    <SelectItem value="month">This Month</SelectItem>
                                    <SelectItem value="last_month">Last Month</SelectItem>
                                    <SelectItem value="quarter">This Quarter</SelectItem>
                                    <SelectItem value="last_quarter">Last Quarter</SelectItem>
                                    <SelectItem value="custom">Custom Range</SelectItem>
                                </SelectContent>
                            </Select>
                            <Input
                                type="date"
                                value={startDate}
                                onChange={(e) => { setStartDate(e.target.value); setRangeType('custom'); }}
                                className="w-[140px] h-9 bg-background"
                            />
                            <Input
                                type="date"
                                value={endDate}
                                onChange={(e) => { setEndDate(e.target.value); setRangeType('custom'); }}
                                className="w-[140px] h-9 bg-background"
                            />
                        </div>
                    </div>

                    <div className="space-y-1">
                        <label className="text-xs font-medium text-muted-foreground ml-1">{t('financials.accounting_points')}</label>
                        <div className="flex gap-2">
                            <Input
                                type="date"
                                value={asOfDate}
                                onChange={(e) => setAsOfDate(e.target.value)}
                                className="w-[160px] h-9 bg-background"
                            />
                        </div>
                    </div>

                    <div className="flex-1"></div>

                    <Badge variant="outline" className="h-9 px-4 py-0 flex items-center gap-2 border-primary/20 bg-primary/5 text-primary">
                        <TrendingUp className="h-3.5 w-3.5" />
                        <span className="font-semibold">{t('financials.reporting_standards')}</span>
                    </Badge>
                </CardContent>
            </Card>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-green-600">{t('financials.kpi_revenue')}</CardTitle>
                        <ArrowUpRight className="h-4 w-4 text-green-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{formatPrice(totalRevenue)}</div>
                        <p className="text-xs text-muted-foreground">Premium income across policies</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-red-600">{t('financials.kpi_expenses')}</CardTitle>
                        <ArrowDownRight className="h-4 w-4 text-red-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{formatPrice(totalExpenses)}</div>
                        <p className="text-xs text-muted-foreground">Commission & Salary payouts</p>
                    </CardContent>
                </Card>
                <Card className="bg-primary/5 border-primary/20">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-primary">{t('financials.kpi_net_position')}</CardTitle>
                        <Scale className="h-4 w-4 text-primary" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-primary">{formatPrice(totalRevenue - totalExpenses)}</div>
                        <p className="text-xs text-muted-foreground">Estimated profitability (YTD)</p>
                    </CardContent>
                </Card>
            </div>

            <Tabs defaultValue="ledger" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="ledger" className="flex items-center gap-2">
                        <History className="h-4 w-4" /> {t('financials.context_transactions')}
                    </TabsTrigger>
                    <TabsTrigger value="pl" className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" /> {t('financials.context_pnl')}
                    </TabsTrigger>
                    <TabsTrigger value="bs" className="flex items-center gap-2">
                        <PieChart className="h-4 w-4" /> {t('financials.context_balance_sheet')}
                    </TabsTrigger>
                    <TabsTrigger value="balance" className="flex items-center gap-2">
                        <BarChart3 className="h-4 w-4" /> {t('financials.context_trial_balance')}
                    </TabsTrigger>
                    <TabsTrigger value="accounts" className="flex items-center gap-2">
                        <AlertCircle className="h-4 w-4" /> Chart of Accounts
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="ledger">
                    <Card>
                        <CardHeader>
                            <CardTitle>Journal Entries</CardTitle>
                            <CardDescription>Recent financial transactions recorded in the General Ledger.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="h-[500px] overflow-auto">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead className="w-[100px]">{t('financials.trans_date')}</TableHead>
                                            <TableHead>{t('financials.trans_desc')}</TableHead>
                                            <TableHead>{t('financials.trans_ref')}</TableHead>
                                            <TableHead className="text-right">{t('financials.trans_debit')}</TableHead>
                                            <TableHead className="text-right">{t('financials.trans_credit')}</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {ledger.length === 0 ? (
                                            <TableRow>
                                                <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">No transactions found.</TableCell>
                                            </TableRow>
                                        ) : (
                                            ledger.map((entry) => (
                                                <Fragment key={entry.id}>
                                                    <TableRow className="bg-muted/30 hover:bg-muted/50 transition-colors border-b">
                                                        <TableCell className="font-medium text-xs">
                                                            {formatDate(entry.entry_date)}
                                                        </TableCell>
                                                        <TableCell className="font-semibold">{entry.description}</TableCell>
                                                        <TableCell><Badge variant="outline">{entry.reference}</Badge></TableCell>
                                                        <TableCell colSpan={2}></TableCell>
                                                    </TableRow>
                                                    {entry.entries.map((le) => (
                                                        <TableRow key={le.id} className="hover:bg-transparent border-none">
                                                            <TableCell></TableCell>
                                                            <TableCell className="text-sm text-muted-foreground pl-8">
                                                                {le.account_name || 'Account'} ({le.account_code})
                                                            </TableCell>
                                                            <TableCell></TableCell>
                                                            <TableCell className="text-right text-xs">
                                                                {le.debit > 0 ? formatPrice(le.debit) : '-'}
                                                            </TableCell>
                                                            <TableCell className="text-right text-xs">
                                                                {le.credit > 0 ? formatPrice(le.credit) : '-'}
                                                            </TableCell>
                                                        </TableRow>
                                                    ))}
                                                </Fragment>
                                            ))
                                        )}
                                    </TableBody>
                                </Table>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="pl">
                    <Card>
                        <CardHeader>
                            <CardTitle>Profit & Loss Statement</CardTitle>
                            <CardDescription>Income and expenses over the current period (YTD).</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Revenue</h4>
                                    <Table>
                                        <TableBody>
                                            {(profitLoss?.revenue || []).map(item => (
                                                <TableRow key={item.code} className="border-none">
                                                    <TableCell className="py-2">{item.name} ({item.code})</TableCell>
                                                    <TableCell className="text-right py-2">{formatPrice(item.amount)}</TableCell>
                                                </TableRow>
                                            ))}
                                            <TableRow className="border-t font-bold">
                                                <TableCell className="py-3">Total Revenue</TableCell>
                                                <TableCell className="text-right py-3">{formatPrice(profitLoss?.total_revenue || 0)}</TableCell>
                                            </TableRow>
                                        </TableBody>
                                    </Table>
                                </div>

                                <div>
                                    <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Expenses</h4>
                                    <Table>
                                        <TableBody>
                                            {(profitLoss?.expenses || []).map(item => (
                                                <TableRow key={item.code} className="border-none">
                                                    <TableCell className="py-2">{item.name} ({item.code})</TableCell>
                                                    <TableCell className="text-right py-2">{formatPrice(item.amount)}</TableCell>
                                                </TableRow>
                                            ))}
                                            <TableRow className="border-t font-bold">
                                                <TableCell className="py-3">Total Expenses</TableCell>
                                                <TableCell className="text-right py-3">{formatPrice(profitLoss?.total_expenses || 0)}</TableCell>
                                            </TableRow>
                                        </TableBody>
                                    </Table>
                                </div>

                                <div className="p-4 bg-primary/10 rounded-lg flex justify-between items-center">
                                    <span className="text-lg font-bold">Net Profit</span>
                                    <span className={`text-xl font-black ${(profitLoss?.net_profit || 0) < 0 ? 'text-red-500' : 'text-green-600'}`}>
                                        {formatPrice(profitLoss?.net_profit || 0)}
                                    </span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="bs">
                    <Card>
                        <CardHeader>
                            <CardTitle>Balance Sheet</CardTitle>
                            <CardDescription>Statement of financial position as of today.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid md:grid-cols-2 gap-8">
                                <div className="space-y-6">
                                    <div>
                                        <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Assets</h4>
                                        <Table>
                                            <TableBody>
                                                {(balanceSheet?.assets || []).map(item => (
                                                    <TableRow key={item.code} className="border-none">
                                                        <TableCell className="py-2">{item.name}</TableCell>
                                                        <TableCell className="text-right py-2">{formatPrice(item.amount)}</TableCell>
                                                    </TableRow>
                                                ))}
                                                <TableRow className="border-t font-bold">
                                                    <TableCell className="py-3 text-primary">Total Assets</TableCell>
                                                    <TableCell className="text-right py-3 text-primary">{formatPrice(balanceSheet?.total_assets || 0)}</TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </div>
                                </div>

                                <div className="space-y-6">
                                    <div>
                                        <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Liabilities</h4>
                                        <Table>
                                            <TableBody>
                                                {(balanceSheet?.liabilities || []).map(item => (
                                                    <TableRow key={item.code} className="border-none">
                                                        <TableCell className="py-2">{item.name}</TableCell>
                                                        <TableCell className="text-right py-2">{formatPrice(item.amount)}</TableCell>
                                                    </TableRow>
                                                ))}
                                                <TableRow className="border-t font-bold">
                                                    <TableCell className="py-3">Total Liabilities</TableCell>
                                                    <TableCell className="text-right py-3">{formatPrice(balanceSheet?.total_liabilities || 0)}</TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </div>

                                    <div>
                                        <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Equity</h4>
                                        <Table>
                                            <TableBody>
                                                {(balanceSheet?.equity || []).map(item => (
                                                    <TableRow key={item.code} className="border-none">
                                                        <TableCell className="py-2">{item.name}</TableCell>
                                                        <TableCell className="text-right py-2">{formatPrice(item.amount)}</TableCell>
                                                    </TableRow>
                                                ))}
                                                <TableRow className="border-t font-bold">
                                                    <TableCell className="py-3">Total Equity</TableCell>
                                                    <TableCell className="text-right py-3">{formatPrice(balanceSheet?.total_equity || 0)}</TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </div>

                                    <div className="p-4 border-2 border-dashed rounded-lg flex justify-between items-center bg-muted/30">
                                        <span className="font-bold">Liabilities + Equity</span>
                                        <span className="font-bold">{formatPrice((balanceSheet?.total_liabilities || 0) + (balanceSheet?.total_equity || 0))}</span>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="balance">
                    <Card>
                        <CardHeader>
                            <CardTitle>Trial Balance</CardTitle>
                            <CardDescription>Current balances for all asset, liability, revenue, and expense accounts.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Account Code</TableHead>
                                        <TableHead>Account Name</TableHead>
                                        <TableHead className="text-right">Total Debits</TableHead>
                                        <TableHead className="text-right">Total Credits</TableHead>
                                        <TableHead className="text-right">Net Balance</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {trialBalance.map((item) => (
                                        <TableRow key={item.account_code}>
                                            <TableCell className="font-mono">{item.account_code}</TableCell>
                                            <TableCell className="font-medium">{item.account_name}</TableCell>
                                            <TableCell className="text-right">{formatPrice(item.total_debit)}</TableCell>
                                            <TableCell className="text-right">{formatPrice(item.total_credit)}</TableCell>
                                            <TableCell className={`text-right font-bold ${item.balance < 0 ? 'text-red-500' : item.balance > 0 ? 'text-green-600' : ''}`}>
                                                {formatPrice(item.balance)}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="accounts">
                    <Card>
                        <CardHeader>
                            <CardTitle>Chart of Accounts</CardTitle>
                            <CardDescription>Configuration and hierarchy of your accounting structure.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                                {accounts.map((acc) => (
                                    <Card key={acc.id} className="p-4 flex flex-col justify-between">
                                        <div>
                                            <div className="flex justify-between items-start mb-2">
                                                <Badge variant="secondary" className="font-mono">{acc.code}</Badge>
                                                <Badge variant="outline">{acc.account_type}</Badge>
                                            </div>
                                            <h4 className="font-bold mb-1">{acc.name}</h4>
                                            <p className="text-xs text-muted-foreground">{acc.description || 'No description provided.'}</p>
                                        </div>
                                    </Card>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs >
        </div >
    );
}
